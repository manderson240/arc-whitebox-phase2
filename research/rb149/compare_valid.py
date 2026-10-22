"""rb149 paired comparison table: ours (submissions/v112_sb, shipped, via eval_port.py) vs ARC SIMPLE K=3 on VALID nets. Final-layer MSE vs the 1e9-sample truth,
noise-corrected analytically (truth stored as a single mean, no A/B halves exist): MSE_true = MSE_obs - avg_variance/1e9 (identical for both arms, so paired diffs are unaffected)."""
import json, sys
from pathlib import Path
import numpy as np
HERE = Path(__file__).resolve().parent; LC = HERE.parent / "lc"; RB = HERE.parent / "rebuild"
meta = {m["mlp_id"]: m["avg_variance"] for m in json.load(open(LC / "data" / "meta.json"))}
arcrows = {json.loads(l)["net"]: json.loads(l) for l in open(HERE / "arc_valid.jsonl")}
ours_rows = {}
for l in open(RB / "port_results.jsonl"):
    r = json.loads(l)
    if r["sub"] == "v112_sb": ours_rows[r["net"]] = r
nets = sorted(set(arcrows) & set(ours_rows)); rng = np.random.default_rng(149)
rows = []; D = []
for m in nets:
    t = np.load(LC / "data" / f"truth_{m:05d}.npz")["all_layer_means"][-1]
    o = np.load(RB / f"port_v112_sb_{m:05d}.npy")[-1]; a = np.load(HERE / f"arc_valid_{m:05d}.npy")[-1]
    floor = meta[m] / 1e9
    eo, ea = (o - t) ** 2, (a - t) ** 2
    d = eo - ea; bs = [rng.choice(d, d.size).mean() for _ in range(2000)]
    rows.append(dict(net=m, ours=eo.mean() - floor, arc=ea.mean() - floor, diff=d.mean(), ci=(np.percentile(bs, 2.5), np.percentile(bs, 97.5)),
                     ours_pct=ours_rows[m]["budget_pct"], arc_flops=1520.08*2*1024**3))
    D.append(d.mean())
O = np.array([r["ours"] for r in rows]); A = np.array([r["arc"] for r in rows]); Dd = O - A
idx = [rng.integers(0, len(nets), len(nets)) for _ in range(20000)]
cd = np.percentile([Dd[i].mean() for i in idx], [2.5, 97.5]); cr = np.percentile([O[i].mean() / A[i].mean() for i in idx], [2.5, 97.5])
lines = ["| net | ours (v112_sb) | ARC simple K=3 | ours - ARC | 95% CI (neuron bootstrap) | ours budget % | ARC torch FLOPs (n^3 MAC units) |", "|---|---|---|---|---|---|---|"]
for r in rows:
    lines.append(f"| {r['net']} | {r['ours']:.3e} | {r['arc']:.3e} | {r['diff']:+.2e} | [{r['ci'][0]:+.1e}, {r['ci'][1]:+.1e}] | {r['ours_pct']:.2f} | {r['arc_flops']/2/1024**3:.0f} |")
lines.append(f"| **mean** | **{O.mean():.3e}** | **{A.mean():.3e}** | **{Dd.mean():+.2e}** | net-bootstrap [{cd[0]:+.1e}, {cd[1]:+.1e}] | {np.mean([r['ours_pct'] for r in rows]):.2f} | {np.mean([r['arc_flops'] for r in rows])/2/1024**3:.0f} |")
txt = "\n".join(lines) + f"\n\nratio of means ours/ARC = {O.mean()/A.mean():.3f}, net-bootstrap 95% CI [{cr[0]:.3f}, {cr[1]:.3f}]; n nets = {len(nets)}; wins for ours {int((Dd<0).sum())}/{len(nets)}"
print(txt); open(HERE / "compare_valid_table.md", "w").write(txt + "\n")
print(f"SUMMARY: ours {O.mean():.2e} vs ARC {A.mean():.2e} final-layer MSE (noise-corrected), paired diff CI [{cd[0]:+.1e}, {cd[1]:+.1e}], FLOPs {np.mean([r['ours_pct'] for r in rows])*2048/100:.0f} vs {np.mean([r['arc_flops'] for r in rows])/2/1024**3:.0f} n^3 units, {len(nets)} nets")
