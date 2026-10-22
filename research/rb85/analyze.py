"""G-RB85: M0-debiased ratios from map.jsonl. M0 = 2 M(AB) - (M(A) + M(B))/2 (linear noise-penalty law, K4_FEED_ORACLE / G-RB73).
Ratio = M0 / control(same head) per net; pooled = sum M0 / sum control over the nets present. Mean rows (1e9 truth) are noise-free: AB only."""

import json
from collections import defaultdict
from pathlib import Path


HERE = Path(__file__).resolve().parent
rows = [json.loads(l) for l in open(HERE / "map.jsonl")]
last = {}
for r in rows:  # last row wins per (net, spec)
    last[(r["net"], r["spec"])] = r
ctrl = {
    (n, h): last[(n, f"ctrl:AB:{h}")]["final"]
    for n in (0, 2, 4)
    for h in ("full", "none")
    if (n, f"ctrl:AB:{h}") in last
}
arms = defaultdict(dict)
for (n, spec), r in last.items():
    p = spec.split(":")
    key = (p[0], p[2], p[3] if len(p) > 3 else "1-15")
    arms[key].setdefault(n, {})[p[1]] = r["final"]
out = []
for (keys, head, lay), per in sorted(arms.items()):
    if keys == "ctrl":
        continue
    m0s, cs, flags = {}, {}, []
    for n, h in per.items():
        if (n, head) not in ctrl:
            continue
        if keys.startswith("mean") and "+" not in keys:
            if "AB" in h:
                m0s[n] = h["AB"]
        elif all(k in h for k in ("A", "B", "AB")):
            m0s[n] = 2 * h["AB"] - 0.5 * (h["A"] + h["B"])
            pen = 0.5 * (h["A"] + h["B"]) - h["AB"]  # = half the A-arm penalty
            if pen > m0s[n]:
                flags.append(f"net{n}: noise penalty {pen:.2e} > M0 {m0s[n]:.2e}")
        else:
            continue
        cs[n] = ctrl[(n, head)]
    if not m0s:
        continue
    per_ratio = {n: m0s[n] / cs[n] for n in sorted(m0s)}
    pooled = sum(m0s.values()) / sum(cs[n] for n in m0s)
    pooled_raw = sum(m0s.values()) / len(m0s)
    out.append(
        dict(
            keys=keys,
            head=head,
            layers=lay,
            per_net=per_ratio,
            pooled=pooled,
            pooled_raw=pooled_raw,
            flags=flags,
        )
    )
    print(
        f"{keys:22s} {head:4s} {lay:6s} pooled {pooled:.3f} (raw {pooled_raw:.3e}) per-net "
        + " ".join(f"{n}:{v:.3f}" for n, v in per_ratio.items())
        + ("  !! " + "; ".join(flags) if flags else "")
    )
for h in ("full", "none"):
    cc = [ctrl[(n, h)] for n in (0, 2, 4) if (n, h) in ctrl]
    if cc:
        print(
            f"control head={h}: "
            + " ".join(f"{c:.4e}" for c in cc)
            + f"  mean {sum(cc) / len(cc):.4e}"
        )

# noise-dose law check: M(v) over noise multipliers v (AB = 1, A/B = 2, T<t> = 1 + t^2); linear and quadratic intercepts
import numpy as np  # noqa: E402

print("\nnoise-dose fits (intercept at v = 0 as a ratio to control; lin / quad):")
for (keys, head, lay), per in sorted(arms.items()):
    for n, h in sorted(per.items()):
        pts = []
        for half, v in h.items():
            if half in ("A", "B"):
                pts.append((2.0, v))
            elif half == "AB":
                pts.append((1.0, v))
            elif half.startswith("T"):
                pts.append((1.0 + float(half[1:]) ** 2, v))
        vs = sorted({p[0] for p in pts})
        if len(vs) < 3 or (n, head) not in ctrl:
            continue
        x = np.array([p[0] for p in pts])
        y = np.array([p[1] for p in pts])
        lin = np.polyfit(x, y, 1)
        quad = np.polyfit(x, y, 2)
        c = ctrl[(n, head)]
        print(f"  {keys:14s} net {n}: points {len(pts)} v={vs}  lin {lin[1] / c:.3f}  quad {quad[2] / c:.3f}  slope/ctrl {lin[0] / c:.3f}")
json.dump(out, open(HERE / "map_summary.json", "w"), indent=1)
