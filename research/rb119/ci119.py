"""G-RB119 follow-up 1: per-net extrapolation, bootstrap-over-nets 90% CI and leave-one-out for the pooled extrapolated ratios.
usage: ci119.py [results files...]; arms with suffix _L1115 are read from results_L1115_*.jsonl when present (same table)."""
import json, collections, sys, numpy as np
from pathlib import Path
H = Path(__file__).resolve().parent
R = collections.defaultdict(dict)
files = [H.parent/"rb117/results_seat.jsonl"] + sorted(H.glob("results_half_*.jsonl")) + sorted(H.glob("results_L1115*.jsonl"))
for p in files:
    for l in open(p):
        r = json.loads(l); a, _, h = r["arm"].partition("__"); R[(a, h or "AB")][r["net"]] = r["final"]
NETS = [0, 2, 4, 5, 6, 7]; base = np.array([R[("BASE", "AB")][n] for n in NETS])
rng = np.random.default_rng(119); out = {}
arms = sorted({a for a, h in R if a != "BASE" and h == "A"}, key=lambda a: (a.endswith("h0"), a))
for a in arms:
    f, A, B = (np.array([R[(a, h)][n] for n in NETS]) for h in ("AB", "A", "B"))
    ex = 2 * f - 0.5 * (A + B)
    pooled = ex.sum() / base.sum()
    idx = rng.integers(0, 6, (20000, 6)); bs = ex[idx].sum(1) / base[idx].sum(1)
    lo, hi = np.percentile(bs, [5, 95])
    loo = [np.delete(ex, i).sum() / np.delete(base, i).sum() for i in range(6)]
    out[a] = dict(pooled=pooled, ci90=[lo, hi], loo=[min(loo), max(loo)], per_net=(ex / base).round(3).tolist(), full=f.sum() / base.sum())
    print(f"{a:18s} full {f.sum()/base.sum():.3f} extrap {pooled:.3f} CI90 [{lo:.3f},{hi:.3f}] LOO [{min(loo):.3f},{max(loo):.3f}] per-net {np.round(ex/base,3).tolist()}")
json.dump(out, open(H / "ci119.json", "w"), indent=1)
