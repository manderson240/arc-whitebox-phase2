"""G-RB140 phase 2: trust-region repair with the iteration-0 Jacobian. Boxes 0.04/0.02/0.01, lambda=1; 3 verification sweeps; best verified theta -> final2.json."""
import json, math, sys
import numpy as np
sys.argv = ["x"]
src = open("gn.py").read().replace("\nmain()\n", "\n")
exec(compile(src, "gn.py", "exec"))
S = json.load(open(R / "lc" / "split.json")); nets = sorted(S["FIT"])
th = dict(SHIPPED)
base = sweep(th, "base_it0")
G = np.load(HERE / "res" / "G_it0.npy")
l0 = np.log(np.array([base[n] for n in nets]))
w = np.exp(l0 - l0.max()); w /= w.sum()
g = (w[:, None] * G).sum(0); Gc = G - g; H = (Gc * w[:, None]).T @ Gc
best = None
for box in (0.04, 0.02, 0.01):
    A = H + 1.0 * np.diag(np.diag(H)) + 1e-6 * np.eye(6)
    delta = np.clip(-np.linalg.solve(A, g), -box, box)
    t2 = {k: th[k] * math.exp(delta[j]) for j, k in enumerate(KEYS)}
    ver = sweep(t2, f"p2_box{box}")
    act = math.log(pooled(ver, nets)) - math.log(pooled(base, nets))
    pred = math.log(np.exp(l0 + G @ delta).sum()) - math.log(np.exp(l0).sum())
    log(f"p2 box {box} delta {np.round(delta,4)} pred {pred:.5f} actual {act:.5f} theta {spec_of(t2)}")
    if act < 0 and (best is None or act < best[0]): best = (act, spec_of(t2))
json.dump(dict(best=best, shipped=spec_of(th)), open(HERE / "final2.json", "w"), indent=1)
log("P2 FINAL", best)
