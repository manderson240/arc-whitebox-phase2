import json,collections,sys
R=collections.defaultdict(dict)
for f in sys.argv[1:]:
    for l in open(f):
        r=json.loads(l);R[r["arm"]][r["net"]]=r["final"]
base={}
for l in open("results_ctl.jsonl"):
    r=json.loads(l);base[r["net"]]=r["final"]
for a,d in R.items():
    ns=[n for n in d]
    s=sum(d[n] for n in ns)/sum(base[n] for n in ns)
    print(f"{a:20s} n={len(ns):2d} pooled {s:.4f} impr {sum(d[n]<base[n] for n in ns)}/{len(ns)}", " ".join(f"{d[n]/base[n]:.3f}" for n in sorted(ns)))
