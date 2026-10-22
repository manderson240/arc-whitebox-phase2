import json, os
def rd(f):
    return {json.loads(l)["net"]: json.loads(l)["final"] for l in open(f)} if os.path.exists(f) else {}
def rep(split, ctl, arms):
    c = rd(ctl)
    for a, f in arms:
        d = rd(f); ns = [n for n in d if n in c]
        if not ns: continue
        s = sum(d[n] for n in ns) / sum(c[n] for n in ns)
        print(f"{split:8s} {a:10s} n={len(ns):2d} pooled {s:.4f} improve {sum(d[n] < c[n] for n in ns)}/{len(ns)} per-net", " ".join(f"{d[n]/c[n]:.3f}" for n in sorted(ns)))
r117 = "../rb117/results_ctl.jsonl"
c, c0 = rd("results_fit12_ctl.jsonl"), rd(r117)
if c: print("control repro vs rb117: max |rel diff|", max(abs(c[n] / c0[n] - 1) for n in c if n in c0), "n", len(c), "pooled mean %.5e" % (sum(c.values()) / len(c)))
f0 = rd("../rb117/results_r1024.jsonl"); f1 = rd("results_fit12_frozen.jsonl")
if f1: print("frozen repro vs rb117 r1024: max |rel diff|", max(abs(f1[n] / f0[n] - 1) for n in f1 if n in f0))
rep("FIT12", "results_fit12_ctl.jsonl", [("frozen", "results_fit12_frozen.jsonl"), ("refit60", "results_fit12_refit60.jsonl"), ("refit48", "results_fit12_refit48.jsonl")])
rep("VALID20", "results_valid_ctl.jsonl", [("frozen", "results_valid_frozen.jsonl"), ("refit60", "results_valid_refit60.jsonl")])
