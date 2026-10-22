"""G-RB139 table: ratio of sums vs v105 (same run), predicted grader max = 89.4 x ratio, E = util saved per predicted s."""
import collections, json, sys
UTIL = {"v105_sw": 20.3224, "v110_t2": 20.2237, "v110_f0": 20.2560, "v110_k0": 20.2715, "v110_fk": 20.2051}
UTIL.update(json.loads(sys.argv[2]) if len(sys.argv) > 2 else {})
rows = [json.loads(l) for l in open(sys.argv[1]) if l.startswith('{"build"') and '"net"' in l]
S = collections.defaultdict(float); N = collections.Counter(); per = collections.defaultdict(list)
for r in rows:
    b = r["build"].split("/")[-1]; S[b] += r["wall_s"]; N[b] += 1; per[b].append(f"{r['tag']}/n{r['net']}={r['wall_s']:.1f}")
base = S["v105_sw"]
print("| build | walls (s) | sum | ratio vs v105 | pred grader max (s) | util | dutil pt | E pt/s |")
print("|---|---|---|---|---|---|---|---|")
for b in S:
    ratio = S[b] / base; pm = 89.4 * ratio; du = UTIL.get(b, float("nan")) - UTIL["v105_sw"]
    E = (-du / (pm - 89.4)) if pm > 89.4 + 1e-9 else float("nan")
    print(f"| {b} | {', '.join(per[b])} | {S[b]:.1f} (n={N[b]}) | {ratio:.4f} | {pm:.1f} | {UTIL.get(b, float('nan')):.4f} | {du:+.4f} | {E:.4f} |")
