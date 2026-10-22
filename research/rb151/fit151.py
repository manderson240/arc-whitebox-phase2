"""G-RB151: the shipped MIX2 recipe (rb130/fit130.py with N = 0: lc/fit_all.py M2/L0=4/U + lc/fit_head15.py shared8, seed 0, 30 ep,
VALID-20 TF early stop) on FIT60 TF caches of chain <tag> from rb151/cache (tf_<tag>_*), early stop on that chain's VALID-20 caches.
usage: fit151.py <tag>   (tag a0 = control, must give max|dW| = 0 vs shipped corr_sscf_*)"""
import sys, time, numpy as np
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "lc"))
import lctrain as T, lcfeat as F  # noqa: E402
tag = sys.argv[1]
fit_ids = T.SPLIT["FIT"]
assert not set(fit_ids) & set(T.SPLIT["TEST"]) and not set(T.SPLIT["VALID"]) & set(fit_ids)
T.CACHE = HERE / "cache"
Dtr = T.load_tf(tag, fit_ids); Dva = T.load_tf(tag, T.SPLIT["VALID"])
print(tag, "fit nets", len(Dtr), flush=True)
cs = list(range(len(F.NAMES)))
X, y, ls = T.stack(Dtr, cs, 4); Xv, yv, lv = T.stack(Dva, cs, 4)
mu, sd = X.mean(0), X.std(0) + 1e-9
t0 = time.time()
net, bl, hist = T.train((X - mu) / sd, y, np.ones(len(y)), (Xv - mu) / sd, yv, np.ones(len(yv)), [len(cs), 32, 32, 1], seed=0, epochs=30)
pv = net.fwd((Xv - mu) / sd)
print(f"{tag} M2_U_L4 VALID TF R2 {1 - ((yv - pv) ** 2).sum() / (yv ** 2).sum():.4f} (ep {int(np.argmin(hist))}, {time.time() - t0:.0f}s, rows {len(y)})", flush=True)
pa = HERE / "cache" / f"corr_{tag}_M2_U_L4.npz"; T.save_corrector(pa, net, cs, mu, sd, 4, 15)
hc = [F.NAMES.index(n) for n in F.LITE]
Xh, yh, _ = T.stack(Dtr, hc, 8); Xhv, yhv, _ = T.stack(Dva, hc, 8)
mh, sh = Xh.mean(0), Xh.std(0) + 1e-9
net2, bl2, hist2 = T.train((Xh - mh) / sh, yh, np.ones(len(yh)), (Xhv - mh) / sh, yhv, np.ones(len(yhv)), [len(hc), 16, 1], seed=0, epochs=30)
X15, y15, _ = T.stack(Dva, hc, 15, layers=[15])
p15 = net2.fwd((X15 - mh) / sh)
print(f"{tag} head shared8 TF R2 at l=15 on VALID {1 - ((y15 - p15) ** 2).sum() / (y15 ** 2).sum():.4f}", flush=True)
pb = HERE / "cache" / f"corr_{tag}_M1h15.npz"; T.save_corrector(pb, net2, hc, mh, sh, 15, 15)
np.savez(HERE / "cache" / f"corr_{tag}_MIX2.npz", mix_a=str(pa), mix_b=str(pb))
for new, old in ((pa, "corr_sscf_M2_U_L4.npz"), (pb, "corr_sscf_M1h15.npz")):
    a, b = np.load(new, allow_pickle=True), np.load(HERE.parent / "lc" / "cache" / old, allow_pickle=True)
    d = max(float(np.abs(a[k] - b[k]).max()) for k in a.files if a[k].dtype.kind == "f")
    print("max|dW| vs shipped", old, d, flush=True)
