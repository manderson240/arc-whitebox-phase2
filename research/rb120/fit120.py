"""G-RB120: the corr_sscf_MIX2 recipe (lc/fit_all.py M2/L0=4/loss U + lc/fit_head15.py FORCE_HEAD=shared8) on rb120/cache/tf_u1024_*.
usage: fit120.py <out_tag> <fit60|fit48>   fit48 = FIT[12:60] (FIT12 excluded). Early stop on VALID TF loss exactly as the original (TEST never read)."""
import sys, time, numpy as np
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "lc"))
import lctrain as T, lcfeat as F  # noqa: E402
T.CACHE = HERE / "cache"
tag, which = sys.argv[1], sys.argv[2]
ids = T.SPLIT["FIT"] if which == "fit60" else T.SPLIT["FIT"][12:]
assert not set(ids) & set(T.SPLIT["TEST"]) and not set(T.SPLIT["VALID"]) & set(ids)
Dtr, Dva = T.load_tf("u1024", ids), T.load_tf("u1024", T.SPLIT["VALID"])
print(tag, "fit nets", len(ids), flush=True)
# --- M2 / L0=4 / U
cs = list(range(len(F.NAMES)))
X, y, ls = T.stack(Dtr, cs, 4); Xv, yv, lv = T.stack(Dva, cs, 4)
mu, sd = X.mean(0), X.std(0) + 1e-9
t0 = time.time()
net, bl, hist = T.train((X - mu) / sd, y, np.ones(len(y)), (Xv - mu) / sd, yv, np.ones(len(yv)), [len(cs), 32, 32, 1], seed=0, epochs=30)
pv = net.fwd((Xv - mu) / sd)
print(f"{tag} M2_U_L4 VALID TF R2 {1 - ((yv - pv) ** 2).sum() / (yv ** 2).sum():.4f} (ep {int(np.argmin(hist))}, {time.time() - t0:.0f}s)", flush=True)
pa = HERE / "cache" / f"corr_{tag}_M2_U_L4.npz"; T.save_corrector(pa, net, cs, mu, sd, 4, 15)
# --- head shared8 (LITE cols, layers 8..15, applied at 15)
hc = [F.NAMES.index(n) for n in F.LITE]
Xh, yh, _ = T.stack(Dtr, hc, 8); Xhv, yhv, _ = T.stack(Dva, hc, 8)
mh, sh = Xh.mean(0), Xh.std(0) + 1e-9
net2, bl2, hist2 = T.train((Xh - mh) / sh, yh, np.ones(len(yh)), (Xhv - mh) / sh, yhv, np.ones(len(yhv)), [len(hc), 16, 1], epochs=30)
X15, y15, _ = T.stack(Dva, hc, 15, layers=[15])
p15 = net2.fwd((X15 - mh) / sh)
print(f"{tag} head shared8 TF R2 at l=15 on VALID {1 - ((y15 - p15) ** 2).sum() / (y15 ** 2).sum():.4f}", flush=True)
pb = HERE / "cache" / f"corr_{tag}_M1h15.npz"; T.save_corrector(pb, net2, hc, mh, sh, 15, 15)
np.savez(HERE / "cache" / f"corr_{tag}_MIX2.npz", mix_a=str(pa), mix_b=str(pb))
print("saved", HERE / "cache" / f"corr_{tag}_MIX2.npz")
