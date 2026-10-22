"""G-RB155 control compare: cmplam.py <a.npz> <b.npz> -> per-layer max|dLam|/max|Lam| and verdict (<= 1e-9, zero layers stay zero)."""

import sys

import numpy as np


a = np.load(sys.argv[1])["lam"]
b = np.load(sys.argv[2])["lam"]
assert a.shape == b.shape, (a.shape, b.shape)
worst = 0.0
ok = True
for l in range(a.shape[0]):
    s = np.abs(b[l]).max()
    if s == 0:
        z = np.abs(a[l]).max()
        ok &= z == 0
        print(f"l={l:2d} zero layer, |a| max {z:.3e}")
        continue
    r = np.abs(a[l] - b[l]).max() / s
    worst = max(worst, r)
    print(f"l={l:2d} rel {r:.3e}")
ok &= worst <= 1e-9
print(f"WORST rel {worst:.3e} -> {'PASS' if ok else 'FAIL'}")
