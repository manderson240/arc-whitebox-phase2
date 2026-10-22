"""G-RB137 step 2 table: ratio of sums over all predicts per build (pre-registered) + remote per-class attribution v106-v105."""
import collections, json, sys
rows = [json.loads(l) for l in open(sys.argv[1] if len(sys.argv) > 1 else "research/rb137/wall.jsonl") if l.startswith('{"build"') and '"net"' in l]
S = collections.defaultdict(float); N = collections.Counter(); BK = collections.defaultdict(float)
cls = collections.defaultdict(lambda: collections.defaultdict(float)); calls = collections.defaultdict(lambda: collections.defaultdict(int))
for r in rows:
    b = r["build"].split("/")[-1]; S[b] += r["wall_s"]; N[b] += 1; BK[b] += r["backend_s"]
    for op, v in r["ops"].items():
        if isinstance(v, dict):
            cls[b][op] += v["backend_s"] + v["overhead_s"]; calls[b][op] += v["calls"]
for b in S: print(f"{b:10s} n={N[b]} sum_wall={S[b]:.1f} mean={S[b]/N[b]:.2f} sum_backend={BK[b]:.1f}  per-run: " + ", ".join(f"{r['tag']}/n{r['net']}={r['wall_s']:.1f}" for r in rows if r['build'].endswith(b)))
v99, v105, v106, v102 = (S.get(k) for k in ("v99r_rm", "v105_sw", "v106_1x", "v102_sz"))
if all((v99, v105, v106, v102)):
    a, b_, c = v105 / v99, v106 / v105, v102 / v105
    print(f"v105/v99r={a:.4f} (|.-1|<=0.05: {abs(a-1)<=0.05})  v106/v105={b_:.4f} ([1.12,1.28]: {1.12<=b_<=1.28})  v102/v105={c:.4f} ([1.18,1.36]: {1.18<=c<=1.36})  order v105<v106<v102: {v105<v106<v102}")
    print("CALIBRATION", "PASS" if abs(a-1)<=0.05 and 1.12<=b_<=1.28 and 1.18<=c<=1.36 and v105<v106<v102 else "FAIL")
    tot = sum(cls["v106_1x"].values()) - sum(cls["v105_sw"].values())
    print(f"remote v106-v105 backend+overhead delta (sum over 4 predicts) {tot:.2f} s; per class:")
    for op in sorted(set(cls["v106_1x"]) | set(cls["v105_sw"]), key=lambda o: -(cls["v106_1x"][o] - cls["v105_sw"][o])):
        dd = cls["v106_1x"][op] - cls["v105_sw"][op]
        if abs(dd) > 0.05: print(f"  {op:12s} {dd:+8.2f} s ({100*dd/tot:5.1f} %)  calls {calls['v106_1x'][op]-calls['v105_sw'][op]:+d}")
