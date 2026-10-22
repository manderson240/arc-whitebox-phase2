"""G-RB119 step 2 table: pooled-sum ratios from results_seat (AB, rb117), results_half (A,B), results_dose (T2,T-2) vs BASE."""
import json, collections, sys
from pathlib import Path
H = Path(__file__).resolve().parent
R = collections.defaultdict(dict)
def load(p, sub=None):
    p = Path(p)
    if not p.exists(): return
    for l in open(p):
        r = json.loads(l); a = r["arm"]
        a, _, h = a.partition("__"); R[(a, h or "AB")][r["net"]] = r["final"]
load(H.parent / "rb117/results_seat.jsonl"); load(H / "results_half_on.jsonl"); load(H / "results_half_off.jsonl"); load(H / "results_dose.jsonl")
NETS = [0, 2, 4, 5, 6, 7]
base = {n: R[("BASE", "AB")][n] for n in NETS}
def ratio(arm, h, nets=NETS):
    d = R.get((arm, h), {})
    if not all(n in d for n in nets): return None
    return sum(d[n] for n in nets) / sum(base[n] for n in nets)
out = {}
print(f"{'arm':14s} {'full':>6s} {'A':>6s} {'B':>6s} {'|A-B|':>6s} {'r_inf':>6s} {'d':>7s} {'inf(A)':>7s} {'inf(B)':>7s}  T2   T-2   quad_inf")
for arm in ("var", "k4", "var_k3", "var_k3_k4", "var_h0", "k4_h0", "var_k3_h0", "var_k3_k4_h0"):
    f, a, b = ratio(arm, "AB"), ratio(arm, "A"), ratio(arm, "B")
    if None in (f, a, b): print(arm, "incomplete", f, a, b); continue
    half = 0.5 * (a + b); inf = 2 * f - half
    t2, tm2 = ratio(arm, "T2"), ratio(arm, "T-2")
    q0 = None
    if t2 is not None and tm2 is not None:  # exact quadratic through noise units 1 (AB), 2 (A/B mean), 5 (T+-2 mean): r = r0 + c v + d v^2
        import numpy as np
        t5 = 0.5 * (t2 + tm2); M = np.array([[1, v, v * v] for v in (1, 2, 5)], float)
        q0 = float(np.linalg.solve(M, np.array([f, half, t5]))[0])
    out[arm] = dict(quad_inf=q0, full=f, A=a, B=b, inf=inf, delta=inf - f, infA=2 * f - a, infB=2 * f - b, T2=t2, Tm2=tm2)
    print(f"{arm:14s} {f:6.3f} {a:6.3f} {b:6.3f} {abs(a-b):6.3f} {inf:6.3f} {inf-f:+7.3f} {2*f-a:7.3f} {2*f-b:7.3f}  {t2 and round(t2,3)} {tm2 and round(tm2,3)} {q0 and round(q0,3)}")
json.dump(out, open(H / "table119.json", "w"), indent=1)
