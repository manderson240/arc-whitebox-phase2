"""G-RB86: arm runner + energy decomposition on the rb85 twin. FIT nets 0/2/4 only. usage: run_rb86.py <mid> {ctrl|varmu|decomp}"""
import json, sys, time
from pathlib import Path
import numpy as np
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "k4pred"))
import k4lib as L  # noqa: E402
L.set_twin_env()
sys.path.insert(0, str(HERE))
import k3chain as K  # noqa: E402
import lctrain as T  # noqa: E402
import proto_sectcost as SC  # noqa: E402
import srcchain_rb86 as S  # noqa: E402

S.RF["on"], S.RF["power"] = True, 1
AGED = [("own", 6, 384), (8, 224)]
g = SC.load_g() * 0.92
kappa = np.load(L.RB / "kappa_table.npz")["kappa"]
HEAD = T.load_any(str(L.HERE.parent / "lc" / "cache" / "corr_sscf_MIX2.npz"), sign=1.2, Lmax=15)
mid = int(sys.argv[1]); mode = sys.argv[2]
SPLIT = json.load(open(HERE.parent / "lc" / "split.json"))
assert mid in SPLIT["FIT"] and mid not in L.SPLIT["TEST"]
ws, truth = K.load_net(mid)
mc = L.load_mc(mid)
# truth mu_z[l] = W_l^T E[h_{l-1}] (layer 0: input mean 0)
mz_t = []
for l, w in enumerate(ws):
    prev = np.zeros(w.shape[0]) if l == 0 else truth[l - 1].astype(np.float64)
    mz_t.append(w.astype(np.float64).T @ prev)
mz_t = np.stack(mz_t)
rec = {}
def k4hook(l, ctx):
    rec[l] = dict(var=ctx["var_z"].copy(), mu_z=ctx["mu_z"].copy(), mu=None)
    return ctx["k4z"]
S.K4HOOK = k4hook
RAW = {}
def hook(l, ctx):
    RAW[l] = np.array(ctx["mu"], dtype=np.float64).copy()
    return HEAD.hook(l, ctx)
if mode == "varmu":
    S.INJECT = {"mu_z_truth": mz_t, "lam": 1.0}; S.INJ_LAYERS = set(range(1, 16)); S.INJ_KEYS = {"varmu"}
elif mode == "varmuraw":
    S.INJECT = {"mu_z_truth": mz_t, "RAW": RAW}; S.INJ_LAYERS = set(range(1, 16)); S.INJ_KEYS = {"varmuraw"}
else:
    S.INJECT = None
t0 = time.time()
est = S.src_closure(ws, g, kappa, rank=4, aged=AGED, lc_hook=hook)
final = float(np.mean((est[-1] - truth[-1]) ** 2))
row = dict(net=mid, mode=mode, final=final, secs=round(time.time() - t0, 1))
print(json.dumps(row), flush=True)
open(HERE / "arms.jsonl", "a").write(json.dumps(row) + "\n")
if mode == "decomp":
    out = []
    for l in sorted(rec):
        c = rec[l]["var"]; A = mc["var_A"][l]; B = mc["var_B"][l]
        mzc = rec[l]["mu_z"]
        ea = -(mzc**2) + mz_t[l] ** 2          # (a): chain minus exact-mean variant of var
        mzr = ws[l].astype(np.float64).T @ (RAW[l - 1] if l > 0 else np.zeros(ws[l].shape[0]))
        ear = -(mzr**2) + mz_t[l] ** 2
        # sanity: truth mu_z vs MC mu_z
        mA = mc["mu_A"][l]; mB = mc["mu_B"][l]
        ee_ab = float(np.mean((c - A) * (c - B)))            # debiased <e,e>
        e_ab = c - 0.5 * (A + B)
        cross = float(np.mean(ea * e_ab))                    # <e_a, e> (MC noise independent of ea)
        aa = float(np.mean(ea * ea))
        sc = float(np.mean(0.25 * (A + B) ** 2))
        out.append(dict(net=mid, l=l, ee=ee_ab, ea_e=cross, ea_ea=aa, scale2=sc,
                        ear_e=float(np.mean(ear * e_ab)), ear_ear=float(np.mean(ear * ear)), mu_sanity=float(np.mean((mz_t[l] - 0.5*(mA+mB))**2)), mu_chain_err=float(np.mean((mzc - mz_t[l])**2)),
                        mu_chain_vs_mc=float(np.mean((mzc - mA)*(mzc-mB)))))
    open(HERE / "decomp.jsonl", "a").write("".join(json.dumps(r) + "\n" for r in out))
