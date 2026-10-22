"""G-RB144 table: python tab144.py res_144_heldout.jsonl -> A0 reproduction of rb130 res_heldout_SHIPPED (1e-10 rel), A2/A0 pooled, bar."""
import json, collections, os, sys
R = collections.defaultdict(dict)
for ln in open(sys.argv[1]):
    r = json.loads(ln); R[r["arm"]][r["net"]] = r["final"]
ship = {}
for ln in open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "rb130", "res_heldout_SHIPPED.jsonl")):
    r = json.loads(ln); ship[r["net"]] = r["final"]
A0, A2 = R.get("A0", {}), R.get("A2", {})
if A0:
    dev = max(abs(A0[n] / ship[n] - 1) for n in A0)
    print(f"A0 vs rb130 SHIPPED: n={len(A0)} max|rel| {dev:.3e} -> {'VALID' if dev <= 1e-10 else 'VOID'}; bit-identical {all(A0[n] == ship[n] for n in A0)}")
ns = sorted(n for n in A2 if n in A0)
if ns:
    per = [A2[n] / A0[n] for n in ns]; pooled = sum(A2[n] for n in ns) / sum(A0[n] for n in ns)
    ok = pooled <= 1.038 and sum(p <= 1.10 for p in per) >= 24
    print(f"A2/A0 HELD-OUT: n={len(ns)} pooled {pooled:.4f} nets<=1.10 {sum(p <= 1.10 for p in per)}/{len(ns)} improve {sum(p < 1 for p in per)}/{len(ns)} worst {max(per):.3f} -> {'PASS' if (ok and len(ns) == 40) else 'FAIL/incomplete'} (bar <= 1.038, >= 24/40)")
    print(" ".join(f"{n}:{p:.3f}" for n, p in zip(ns, per)))
