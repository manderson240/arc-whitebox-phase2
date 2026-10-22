"""G-RB151 cache generator: rb130/lc_src130.py (the generator of the shipped head's caches lc/cache/tf_sscf_*, free-SSC env) with
the chain module swapped from rebuild/srcchain_aug.py to rb142/s117.py (a srcchain_aug copy whose default path is bit-identical,
plus the G-RB142 SHARED=fixed old tier). env ARM = A0 (own bases, SW empty) | A2 (shared fixed, aged 6:384/8:224) | A2r (A2 + refresh224).
Output rb151/cache/tf_<CHAIN>_<mid>.npz, CHAIN = env CHAIN. usage: lc_src151.py tf <mid> ...   (FIT/VALID/full nets only; never TEST)"""
import sys, os, time, json
from pathlib import Path
import numpy as np
HERE = Path("~/cohezion-labs/arc-whitebox/research/rebuild")
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(HERE.parent)); sys.path.append(str(HERE.parent / "lc"))
sys.path.insert(0, str(HERE.parent / "rb142"))
import s117 as S  # noqa: E402  (rb142 copy; reads AUG/LAMBDA/QCOEF/FREE/SSC env at import like srcchain_aug)
import k3chain as K, proto_sectcost as SC  # noqa: E402
import lcfeat as F  # noqa: E402
OUT = Path(__file__).resolve().parent / "cache"; OUT.mkdir(exist_ok=True)
FULLD = HERE.parent / "full" / "data"

def load_net(mid):
    if mid < 1000: return K.load_net(mid)
    ws = np.load(FULLD / f"w_{mid:05d}.npy", mmap_mode="r"); t = np.load(FULLD / f"truth_{mid:05d}.npz", allow_pickle=True)
    return [np.asarray(ws[l]) for l in range(16)], t["all_layer_means"].astype(np.float64)

S.RF["on"], S.RF["power"] = True, 1
ARM = os.environ.get("ARM", "A0")
RANK = int(os.environ.get("RANK", "16"))
GS = float(os.environ.get("GSCALE", "1.0"))
CHAIN = os.environ.get("CHAIN", ARM.lower())
AGE = int(os.environ.get("AGE", "5"))
if ARM == "A0":
    AGED = [("own", AGE, 384)] + ([(8, 224)] if os.environ.get("NESTED") else [])
    S.SW.clear()
else:
    AGED = [(AGE, 384), (8, 224)]
    S.SW.clear(); S.SW["shared"] = "fixed"
    if ARM == "A2r":
        S.SW["refresh224"] = 1
SPLIT = json.load(open(HERE.parent / "lc" / "split.json"))
def run(kind, mid):
    assert mid not in SPLIT["TEST"], "TEST nets are never touched here"
    assert mid >= 1000 or mid in SPLIT["FIT"] + SPLIT["VALID"]
    f = OUT / f"{kind}_{CHAIN}_{mid:05d}.npz"
    if f.exists():
        return
    ws, truth = load_net(mid); g = SC.load_g() * GS; kappa = np.load(HERE / "kappa_table.npz")["kappa"]
    fe, pre = [None] * 16, [None] * 16
    def hook(l, ctx):
        fe[l] = F.feats(l, ctx); pre[l] = ctx["mu"].copy()
        return truth[l].copy() if kind == "tf" else ctx["mu"]
    t0 = time.time()
    est = S.src_closure(ws, g, kappa, rank=RANK, aged=AGED, lc_hook=hook)
    np.savez(f, feats=np.stack(fe), mu_pre=np.stack(pre), truth=truth.astype(np.float32), est=est, secs=time.time() - t0,
             final=float(np.mean((est[-1] - truth[-1]) ** 2)))
    print(kind, ARM, mid, "final", float(np.mean((est[-1] - truth[-1]) ** 2)), f"{time.time() - t0:.0f}s", flush=True)
if __name__ == "__main__":
    for m in sys.argv[2:]:
        run(sys.argv[1], int(m))
