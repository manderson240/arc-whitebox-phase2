"""G-RB142 table: python tab142.py res_142.jsonl [more.jsonl]  -> per-arm pooled raw vs A0 (same file), validity checks, PASS bar.
A0 must be bit-identical to ../rb117/results_ctl.jsonl (BASE). u_saved = hand-ledger util fraction (0.128) unless U_SAVED env is set."""
import json, collections, os, sys
R = collections.defaultdict(dict)
for f in sys.argv[1:]:
    for ln in open(f):
        r = json.loads(ln); R[r["arm"]][r["net"]] = r["final"]
ctl = {}
for ln in open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "rb117", "results_ctl.jsonl")):
    r = json.loads(ln); ctl[r["net"]] = r["final"]
A0 = R.get("A0", {})
ident = all(A0[n] == ctl[n] for n in A0) if A0 else None
print(f"A0 vs rb117 ctl: n={len(A0)} bit-identical={ident}" + ("" if ident else f" maxrel={max(abs(A0[n]/ctl[n]-1) for n in A0) if A0 else 'NA'}"))
base = A0 if A0 else ctl
u = float(os.environ.get("U_SAVED", "0.128")); bar = 1 + 0.5 * u
pooled = {}
for a in sorted(R):
    d = R[a]; ns = sorted(n for n in d if n in base)
    if not ns: continue
    s = sum(d[n] for n in ns) / sum(base[n] for n in ns); pooled[a] = s
    per = [d[n] / base[n] for n in ns]
    print(f"{a:5s} n={len(ns):2d} pooled {s:.4f} nets<=1.10 {sum(p <= 1.10 for p in per)}/{len(ns)} impr {sum(p < 1 for p in per)}/{len(ns)} | " + " ".join(f"{p:.3f}" for p in per))
chk = []
if "A3" in pooled: chk.append(("A3 within 0.01 of 0.975", abs(pooled["A3"] - 0.975) <= 0.01, round(pooled["A3"], 4)))
if "P1" in pooled: chk.append(("P1 >= 1.3", pooled["P1"] >= 1.3, round(pooled["P1"], 4)))
if "M2" in pooled and "A2" in pooled: chk.append(("M2 worse than A2", pooled["M2"] > pooled["A2"], round(pooled["M2"] - pooled["A2"], 4)))
if "M1" in pooled and "A2" in pooled: chk.append(("M1 >= A2 + 0.05", pooled["M1"] >= pooled["A2"] + 0.05, round(pooled["M1"] - pooled["A2"], 4)))
for name, ok, v in chk: print(f"VALIDITY {name}: {'OK' if ok else 'FAIL'} ({v})")
if "A2" in pooled:
    d = R["A2"]; ns = sorted(n for n in d if n in base); per = [d[n] / base[n] for n in ns]
    ok = pooled["A2"] <= bar and sum(p <= 1.10 for p in per) >= 7
    print(f"BAR A2: pooled {pooled['A2']:.4f} <= {bar:.4f} (u_saved {u}) and >=7/12 nets <= 1.10 ({sum(p <= 1.10 for p in per)}/{len(ns)}) -> {'PASS' if ok else 'FAIL'}")
