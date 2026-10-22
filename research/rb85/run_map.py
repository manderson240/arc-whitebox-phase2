"""G-RB85 stage A: oracle-injection error map on the v59_p05 f64 twin (= v77_fuse output-identical), FIT nets only, 1024x16.
usage: run_map.py <mid> <spec> [<spec> ...]   -> research/rb85/map.jsonl
spec = keys:half:head[:lmin-lmax]
  keys  '+'-joined subset of {var, k3, k4, mean<k>, lam<x>, ctrl}  (lam<x>: chain + x (MC - chain), default 1); var/k3/k4 come from research/k4pred/mc_<mid>.npz (two 2^22 halves);
        mean<k> = the 1e9-sample truth E[h_l] (research/lc/data/truth_*) replaces the carried mean AFTER the head at h-layers 0..k
  half  A | B | AB | T<t>  (which MC half feeds var/k3/k4; AB = average; T<t> = AB + t(A-B)/2, noise var (1+t^2) x AB's)  -- M0 = 2 M(AB) - (M(A)+M(B))/2 is formed in analyze.py
  head  full (shipped MIX2 corrector, as in G-RB73) | none
  lmin-lmax  z-layers that receive var/k3/k4 (default 1-15)"""

import json
import sys
import time
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
import srcchain_rb85 as S  # noqa: E402


S.RF["on"], S.RF["power"] = True, 1
AGED = [("own", 6, 384), (8, 224)]
g = SC.load_g() * 0.92
kappa = np.load(L.RB / "kappa_table.npz")["kappa"]
HEAD = T.load_any(str(L.HERE.parent / "lc" / "cache" / "corr_sscf_MIX2.npz"), sign=1.2, Lmax=15)

mid = int(sys.argv[1])
assert mid not in L.SPLIT["TEST"], "TEST nets are never touched here"
SPLIT = json.load(open(HERE.parent / "lc" / "split.json"))
assert mid in SPLIT["FIT"], "G-RB85 runs on FIT nets only"
ws, truth = K.load_net(mid)
mc = L.load_mc(mid)


def pick(key, half, l):
    if half.startswith("T"):  # AB + t (A - B)/2: same truth, noise variance (1 + t^2) x the AB noise ((A-B) is independent of (A+B))
        t = float(half[1:])
        return 0.5 * (mc[f"{key}_A"][l] + mc[f"{key}_B"][l]) + t * 0.5 * (mc[f"{key}_A"][l] - mc[f"{key}_B"][l])
    if half == "AB":
        return 0.5 * (mc[f"{key}_A"][l] + mc[f"{key}_B"][l])
    return mc[f"{key}_{half}"][l]


for spec in sys.argv[2:]:
    parts = spec.split(":")
    keys, half, headv = set(parts[0].split("+")), parts[1], parts[2]
    lmin, lmax = (int(x) for x in (parts[3] if len(parts) > 3 else "1-15").split("-"))
    lays = range(lmin, lmax + 1)
    meank = max([int(k[4:]) for k in keys if k.startswith("mean")] or [-1])
    lam = float(([k[3:] for k in keys if k.startswith("lam")] or ["1"])[0])  # chain + lam (MC - chain) for var/k3/k4
    inj_keys = [k for k in ("var", "k3") if k in keys]
    if inj_keys:
        S.INJECT = {
            "var_z": np.stack([pick("var", half, l) for l in range(16)]),
            "k3_z": np.stack([pick("k3", half, l) for l in range(16)]),
            "lam": lam,
        }
        S.INJ_LAYERS = set(lays)
        S.INJ_KEYS = set(inj_keys)
    else:
        S.INJECT = None
    if "k4" in keys:
        S.K4HOOK = lambda l, ctx: ctx["k4z"] + lam * (pick("k4", half, l) - ctx["k4z"]) if l in lays else ctx["k4z"]
    else:
        S.K4HOOK = None
    base_hook = HEAD.hook if headv == "full" else None

    def hook(l, ctx):
        m = base_hook(l, ctx) if base_hook is not None else ctx["mu"]
        if l <= meank and l < 15:
            return truth[l].astype(np.float64).copy()
        return m

    use_hook = hook if (base_hook is not None or meank >= 0) else None
    t0 = time.time()
    est = S.src_closure(ws, g, kappa, rank=4, aged=AGED, lc_hook=use_hook)
    row = dict(
        spec=spec,
        keys=sorted(keys),
        half=half,
        head=headv,
        lmin=lmin,
        lmax=lmax,
        meank=meank,
        net=mid,
        final=float(np.mean((est[-1] - truth[-1]) ** 2)),
        layer_mse=[float(np.mean((est[i] - truth[i]) ** 2)) for i in range(16)],
        secs=round(time.time() - t0, 1),
        utc=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    )
    print(json.dumps({k: v for k, v in row.items() if k != "layer_mse"}), flush=True)
    with open(HERE / "map.jsonl", "a") as f:
        f.write(json.dumps(row) + "\n")
