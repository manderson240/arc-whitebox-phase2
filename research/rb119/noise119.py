"""G-RB119 step 1: per-layer MC standard error vs the v95 twin's own (debiased) chain error. Needs chain_<net>.npz (cap119.py)."""
import sys, numpy as np
from pathlib import Path
HERE = Path(__file__).resolve().parent
NETS = [0, 2, 4, 5, 6, 7]
rows = {q: [] for q in ("var", "k3", "k4")}
for q in rows:
    for l in range(16):
        se2 = er2 = ms = 0.0; neg = 0
        for n in NETS:
            mc = np.load(HERE.parent / "k4pred" / f"mc_{n:05d}.npz"); ch = np.load(HERE / f"chain_{n:05d}.npz")[q][l]
            A, B = mc[f"{q}_A"][l], mc[f"{q}_B"][l]
            se2 += np.mean((A - B) ** 2) / 4.0          # variance of the AB mean
            er2 += np.mean((ch - A) * (ch - B))          # debiased chain error^2
            ms += np.mean((0.5 * (A + B)) ** 2)
        k = len(NETS)
        rows[q].append((l, np.sqrt(se2 / k), np.sqrt(max(er2 / k, 0)), er2 / k < 0, np.sqrt(ms / k)))
for q, r in rows.items():
    print(f"\n{q}: z-layer | rms SE(AB) rel | rms chain err rel (debiased) | SE/err | err^2<0 (below noise)")
    for l, se, er, neg, rms in r:
        print(f"  {l:2d}  {se/rms:.2e}  {er/rms:.2e}  {se/max(er,1e-300):7.2f}  {'BELOW-NOISE' if neg else ''}")
