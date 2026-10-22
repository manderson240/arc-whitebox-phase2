"""G-RB96 worker: f64 twin (s96 = s94 switches + fixed call-counter sketch seed + K31L). run(net, spec) -> (final raw MSE, secs).
spec = dict of switches as in board5/screen/run94.py (ks, k31s, k31sE/D, q22sE/D, k31S, sm, deg, hs/hsE/hsD, ksE/ksD, qcs...) plus
  k31l: {layer: mult} (per chain layer K31 multiplier), kapl: {layer: mult}. BASE (applied underneath, overridable): ks=0.8, k31s=0.9, fixseed=1."""
import json, sys, time, os
from pathlib import Path
import numpy as np
HERE = Path(__file__).resolve().parent
R2 = HERE.parent
sys.path.insert(0, str(R2 / "k4pred"))
import k4lib as L  # noqa: E402
L.set_twin_env()
sys.path.insert(0, str(R2 / "rb85"))
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / 'rb97'))
import k3chain as K  # noqa: E402
import lctrain as T  # noqa: E402
import proto_sectcost as SC  # noqa: E402
import s117 as S  # noqa: E402

S.RF["on"], S.RF["power"] = True, 1
AGED = [("own", 6, 384), (8, 224)]
g0 = SC.load_g() * 0.92
kappa0 = np.load(L.RB / "kappa_table.npz")["kappa"]
LAM0 = np.array(S.LAMBDA).copy()
QC0 = np.array(S.QC).copy()
HEADP = str(L.HERE.parent / "lc" / "cache" / "corr_sscf_MIX2.npz")
SPLIT = json.load(open(R2 / "lc" / "split.json"))
BASE = dict(ks=0.8, k31s=0.9, fixseed=1.0)
_NETS = {}
STR_KEYS = ("sm", "lamf", "qcf")


def smooth(a, layers, deg=3):
    out = a.copy()
    flat = a.reshape(a.shape[0], -1)
    of = out.reshape(a.shape[0], -1)
    x = np.array(layers, float)
    for c in range(flat.shape[1]):
        y = flat[list(layers), c]
        if np.allclose(y, 0):
            continue
        of[list(layers), c] = np.polyval(np.polyfit(x, y, deg), x)
    return out


def run(mid, spec):
    assert mid in SPLIT["FIT"] + SPLIT["VALID"] and mid not in SPLIT["TEST"]
    if mid not in _NETS:
        _NETS.clear()
        _NETS[mid] = K.load_net(mid)
    ws, truth = _NETS[mid]
    sw = dict(BASE); sw.update({k: v for k, v in spec.items() if k not in ("k31l", "kapl", "q22l", "aged", "rank", "inj", "kh")})
    S.SW.clear(); S.PR_LOG.clear(); S.RCNT[0] = 0
    S.SW.update(sw)
    inj = spec.get("inj")
    S.INJECT = None; S.K4HOOK = None
    if inj:  # {"keys":["var","k3","k4"], "layers":[1,15], "lam":1.0, "half":"AB"}  (FIT nets with k4pred MC only; per-net load)
        mc = L.load_mc(mid)
        def pick(key, l, half=inj.get("half", "AB")):
            if half.startswith("T"):  # G-RB119 dose arm: AB + t (A-B)/2, noise variance (1+t^2) x AB (as rb85/run_map.py)
                return 0.5 * (mc[f"{key}_A"][l] + mc[f"{key}_B"][l]) + float(half[1:]) * 0.5 * (mc[f"{key}_A"][l] - mc[f"{key}_B"][l])
            return 0.5 * (mc[f"{key}_A"][l] + mc[f"{key}_B"][l]) if half == "AB" else mc[f"{key}_{half}"][l]
        lam = float(inj.get("lam", 1.0)); lo, hi = inj.get("layers", [1, 15]); lays = set(range(lo, hi + 1))
        ik = [k for k in ("var", "k3") if k in inj["keys"]]
        if ik:
            S.INJECT = {"var_z": np.stack([pick("var", l) for l in range(16)]), "k3_z": np.stack([pick("k3", l) for l in range(16)]), "lam": lam}
            S.INJ_LAYERS = lays; S.INJ_KEYS = set(ik)
        if "k4" in inj["keys"]:
            S.K4HOOK = lambda l, ctx: ctx["k4z"] + lam * (pick("k4", l) - ctx["k4z"]) if l in lays else ctx["k4z"]
    S.C4.KH = int(spec.get('kh', 8)); S.C4.KMAX = S.C4.KH + 8
    S.K31L = np.ones(16)
    for l, m in spec.get("k31l", {}).items(): S.K31L[int(l)] = m
    S.Q22L = np.ones(16)
    for l, m in spec.get("q22l", {}).items(): S.Q22L[int(l)] = m
    g, kappa = g0.copy(), kappa0.copy()
    for l, m in spec.get("kapl", {}).items(): kappa[int(l)] *= m
    S.LAMBDA, S.QC = LAM0.copy(), QC0.copy()
    sm, deg = sw.get("sm"), int(sw.get("deg", 3))
    if sm == "qc":
        S.QC = smooth(QC0, range(0, 14), deg)
    elif sm == "qc0":
        tmp = QC0.copy(); tmp[:, 0] = smooth(QC0[:, :1], range(0, 14), deg)[:, 0]; S.QC = tmp
    ER = np.array([1.0 if r <= 7 else 0.0 for r in range(16)])
    def split(e, d, qc=False):
        ind = ER if not qc else np.array([1.0 if r <= 6 else 0.0 for r in range(16)])
        return ind * e + (1 - ind) * d
    kappa = kappa * sw["ks"] * split(sw.get("ksE", 1.0), sw.get("ksD", 1.0))
    qf = sw.get("qcs", 1.0) * split(sw.get("qcsE", 1.0), sw.get("qcsD", 1.0), qc=True)
    S.QC = S.QC * qf[:, None]
    HEAD = T.load_any(HEADP, sign=1.2 * sw.get("hs", 1.0), Lmax=15)
    hsE, hsD, hsL = sw.get("hsE", 1.0), sw.get("hsD", 1.0), sw.get("hsL", 1.0)
    def hook(l, ctx, _H=HEAD):
        out = _H.hook(l, ctx)
        f = hsL if l == 15 else (hsE if l <= 7 else hsD)
        return ctx["mu"] + f * (out - ctx["mu"])
    t0 = time.time()
    aged = [tuple(x) for x in spec["aged"]] if "aged" in spec else AGED
    est = S.src_closure(ws, g, kappa, rank=int(spec.get("rank", 4)), aged=aged, lc_hook=hook)
    return float(np.mean((est[-1] - truth[-1]) ** 2)), round(time.time() - t0, 1)


if __name__ == "__main__":
    mid = int(sys.argv[1]); spec = json.loads(sys.argv[2]) if len(sys.argv) > 2 else {}
    print(mid, run(mid, spec))
