"""G-RB153 table: tab153.py <res.jsonl> [more] -> per-arm pooled raw vs the in-session CTL, fitted (0,2,4,5,6,7) vs unfitted split,
nets improving, adjusted (util ratio from UTIL env json {arm: ratio}, default 1.0), and the CTL check vs rb142 A2 (res_143_*)."""

import collections
import json
import os
import sys
from pathlib import Path


HERE = Path(__file__).resolve().parent
FITTED = {0, 2, 4, 5, 6, 7}
R = collections.defaultdict(dict)
for f in sys.argv[1:]:
    for ln in open(f):
        r = json.loads(ln)
        R[r["arm"]][r["net"]] = r["final"]
ref = {}
for f in ("res_143_fit12.jsonl", "res_143_valid20.jsonl"):
    for ln in open(HERE.parent / "rb142" / f):
        r = json.loads(ln)
        if r["arm"] == "A2":
            ref[r["net"]] = r["final"]
ctl = R.get("CTL", {})
if ctl:
    rel = [abs(ctl[n] / ref[n] - 1) for n in ctl if n in ref]
    print(
        f"CTL vs rb142 A2: n={len(rel)} max rel {max(rel) if rel else float('nan'):.2e} ({'OK <= 1e-9' if rel and max(rel) <= 1e-9 else 'MISMATCH (in-session CTL is the base)'})"
    )
U = json.loads(os.environ.get("UTIL", "{}"))
for a in sorted(R):
    if a == "CTL":
        continue
    d = R[a]
    ns = sorted(n for n in d if n in ctl)
    if not ns:
        continue
    s = sum(d[n] for n in ns) / sum(ctl[n] for n in ns)
    u = U.get(a, 1.0)
    per = [d[n] / ctl[n] for n in ns]
    fi = [n for n in ns if n in FITTED]
    un = [n for n in ns if n not in FITTED]
    sf = sum(d[n] for n in fi) / sum(ctl[n] for n in fi) if fi else float("nan")
    su = sum(d[n] for n in un) / sum(ctl[n] for n in un) if un else float("nan")
    print(
        f"{a:16s} n={len(ns):2d} raw {s:.5f} adj {s * u:.5f} (u {u:.4f}) impr {sum(p < 1 for p in per)}/{len(ns)} adj-impr {sum(p * u < 1 for p in per)}/{len(ns)} | fitted {sf:.5f} unfitted {su:.5f} | worst {max(per):.4f}"
    )
