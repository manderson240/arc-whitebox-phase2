"""G-RB151 control: bit-compare rb151/cache/tf_<tag>_<mid> to lc/cache/tf_sscf_<mid>. usage: cmp.py <tag> <mid> ..."""
import sys, numpy as np
from pathlib import Path
H = Path(__file__).resolve().parent
tag = sys.argv[1]; bad = 0
for m in map(int, sys.argv[2:]):
    a = np.load(H / "cache" / f"tf_{tag}_{m:05d}.npz"); b = np.load(H.parent / "lc" / "cache" / f"tf_sscf_{m:05d}.npz")
    d = {k: (a[k].shape == b[k].shape) and float(np.abs(a[k].astype(np.float64) - b[k].astype(np.float64)).max()) for k in ("feats", "mu_pre", "truth", "est")}
    ok = all(v is not False and v == 0.0 for v in d.values()); bad += not ok
    print(m, "OK" if ok else "DIFF", d, "final", float(a["final"]), float(b["final"]) if "final" in b.files else None)
print("ALL BIT-IDENTICAL" if bad == 0 else f"{bad} nets differ")
