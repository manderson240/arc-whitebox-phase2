"""G-RB151 head export: fold (lc/export_port.py fold) + lc/export_v42.py layout, in one step, for corr_<tag>_M2_U_L4 + corr_<tag>_M1h15.
usage (from research/): PYTHONPATH=.. ../whest-starterkit/.venv/bin/python rb151/export151.py <corr_dir> <tag> <target_folder> [--check <ref lc_weights.npz>]
Writes <target>/lc_weights.npz (target's weights.npz g must equal 0.92 x table). --check: compare every array to a reference npz (export control)."""
import importlib.util, sys
from pathlib import Path
import numpy as np
R = Path(__file__).resolve().parents[1]
sys.path.append(str(R / "lc"))
import lcchain as L  # noqa: E402
cdir, tag, tgt = Path(sys.argv[1]), sys.argv[2], R.parent / sys.argv[3]
GS = 0.92

def fold(cpath):
    z = np.load(cpath)
    n = int(z["n_layers"]); W = [z[f"W{i}"] for i in range(n)]; b = [z[f"b{i}"] for i in range(n)]
    mean, std, cols, sc = z["mean"], z["std"], z["cols"], float(z["scale"])
    W0 = W[0] / std[:, None]; b0 = b[0] - (mean / std) @ W[0]
    Ws, bs = [W0] + W[1:], [b0] + b[1:]
    Ws[-1] = Ws[-1] * sc; bs[-1] = bs[-1] * sc
    import lcfeat as F
    return [F.NAMES2[i] for i in cols], [w.astype(np.float32).astype(np.float64) for w in Ws], [x.astype(np.float32).astype(np.float64) for x in bs]

g_ship = np.load(tgt / "weights.npz")["g"].astype(np.float64)
g_proto = np.asarray(L.g_table(), dtype=np.float64) * GS
assert np.max(np.abs(g_proto - g_ship)) <= 1e-6 * np.max(np.abs(g_proto))
cols, (W0, W1, W2), (b0, b1, b2) = fold(cdir / f"corr_{tag}_M2_U_L4.npz")
RAW = ["mu_z", "sz", "alpha", "pdf", "cdf", "sz_pdf", "mu_pre", "corr_marg", "skew", "rs_z", "rq_z", "trs_z", "trq_z",
       "var_h", "rs_h", "ts_h", "k3_h", "alpha2", "pdf_over_sz", "k3", "absskew"]
MEANS = {"m_alpha": "alpha", "m_sz": "sz", "m_absskew": "absskew", "m_rs_z": "rs_z", "m_mu_pre": "mu_pre"}
wr = np.zeros((21, 32)); wm = np.zeros((21, 32)); used = set()
for r, name in enumerate(RAW):
    if name in cols: wr[r] = W0[cols.index(name)]; used.add(name)
for mname, raw in MEANS.items():
    wm[RAW.index(raw)] = W0[cols.index(mname)]; used.add(mname)
gi, li = cols.index("g"), cols.index("layer"); used |= {"g", "layer"}
assert used == set(cols) and len(cols) == 27, set(cols) - used
bias = np.zeros((16, 32))
for l in range(4, 15):
    bias[l] = b0 + g_ship[l] * W0[gi] + (l / 15.0) * W0[li]
hc, (hW0, hW1), (hb0, hb1) = fold(cdir / f"corr_{tag}_M1h15.npz")
HRAW = ["mu_z", "sz", "alpha", "pdf", "cdf", "mu_pre", "k3"]
hw = np.stack([hW0[hc.index(c)] for c in HRAW])
hbias15 = hb0 + g_ship[15] * hW0[hc.index("g")] + 1.0 * hW0[hc.index("layer")]
assert set(hc) == set(HRAW) | {"g", "layer"}
spec = importlib.util.spec_from_file_location("tgtest", tgt / "estimator.py"); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
import flopscope.numpy as fnp  # noqa: E402
w = m.LCWeights(); f32 = lambda x: fnp.asarray(np.asarray(x, dtype=np.float32))
w.wr, w.wm, w.bias, w.w1, w.b1, w.w2, w.b2 = f32(wr), f32(wm), f32(bias), f32(W1), f32(b1), f32(W2[:, 0]), f32(b2)
w.hw, w.hbias, w.hw1, w.hb1 = f32(hw), f32(hbias15), f32(hW1[:, 0]), f32(hb1)
w.save(str(tgt / "lc_weights.npz"))
d = np.load(tgt / "lc_weights.npz", allow_pickle=False)
print({k: d[k].shape for k in d.files})
if "--check" in sys.argv:
    ref = np.load(R.parent / sys.argv[sys.argv.index("--check") + 1], allow_pickle=False)
    dev = {k: float(np.abs(d[k].astype(np.float64) - ref[k].astype(np.float64)).max()) if d[k].dtype.kind in "fi" else bool((d[k] == ref[k]).all()) for k in ref.files}
    print("EXPORT CONTROL max|d| per array vs", sys.argv[sys.argv.index("--check") + 1], dev)
