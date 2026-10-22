#!/usr/bin/env python3
"""F6 (V23 key figure): the oracle / ceiling ladder.

Run from the arc-whitebox root:
    ~/dev/cohezion/.venv/bin/python writeup/figs/make_f6_ladder.py
Reads research/rb117/results_*.jsonl directly (G-RB117, v95 twin) and asserts the orchestrator's
re-tabulation (0.8151 / 0.7762 / 0.5452 / 0.5121 / 0.8684). The G-RB85 rows (v59_p05 twin) are the
pooled M0 ratios printed in research/rb85/ERROR_MAP.md §2 (rows 1-5, 7); they are typed in, not recomputed.
V23 adds: the G-RB119 noise-corrected v95-twin group (research/rb119/ci119.json: split-half extrapolated
r_inf = 2*full - mean(A,B), 90% bootstrap CI over 6 nets, whiskers) and the G-RB120 head-refit bar
(research/rb120/results_fit12_{ctl,refit60}.jsonl, recomputed and asserted = 0.8071). The uncorrected
G-RB117 oracle group is kept, labelled superseded.
Writes writeup/figs/F6_oracle_ceiling_ladder.png (overwritten by V23).
"""

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

import matplotlib


matplotlib.use("Agg")
import matplotlib.pyplot as plt


ROOT = Path(__file__).resolve().parents[2]
RB = ROOT / "research" / "rb117"
RB119 = ROOT / "research" / "rb119"
RB120 = ROOT / "research" / "rb120"
OUT = Path(__file__).resolve().parent / "F6_oracle_ceiling_ladder_v27.png"  # V27: no leader reference line


def pooled() -> dict[str, float]:
    base = {}
    for line in open(RB / "results_ctl.jsonl"):
        r = json.loads(line)
        base[r["net"]] = r["final"]
    arms: dict[str, dict[int, float]] = defaultdict(dict)
    for f in (
        "results_seat.jsonl",
        "results_r1024.jsonl",
        "results_r64.jsonl",
        "results_build.jsonl",
    ):
        for line in open(RB / f):
            r = json.loads(line)
            arms[r["arm"]][r["net"]] = r["final"]
    out = {}
    for a, d in arms.items():
        out[a] = (sum(d.values()) / sum(base[n] for n in d), len(d))
    return out


P = pooled()
for arm, want in (
    ("u_all_r1024", 0.8151),
    ("var", 0.7762),
    ("var_k3", 0.5452),
    ("var_k3_k4", 0.5121),
    ("k4", 0.8684),
):
    got = P[arm][0]
    assert abs(got - want) < 5e-5, (arm, got, want)

CI = json.load(open(RB119 / "ci119.json"))
for k, want in (("var", 0.511), ("k4", 0.852), ("var_k3", 0.253), ("var_k3_k4", 0.209), ("varL1115", 0.635)):
    assert abs(CI[k]["pooled"] - want) < 5e-4, (k, CI[k]["pooled"], want)


def _rd(f):
    return {json.loads(l)["net"]: json.loads(l)["final"] for l in open(f)}


_c, _r = _rd(RB120 / "results_fit12_ctl.jsonl"), _rd(RB120 / "results_fit12_refit60.jsonl")
REFIT = sum(_r[n] for n in _r) / sum(_c[n] for n in _r)
assert abs(REFIT - 0.8071) < 5e-5, REFIT

# (label, ratio, colour group[, (lo, hi) 90% CI])
ROWS = [
    ("G-RB117/120 uncosted constructions (v95 twin, 12 nets, no MC)", None, None),
    ("second-order κ3×κ3 Gram-Charlier", P["second"][0], "build"),
    ("no ageing (all sources young)", P["u_noage"][0], "build"),
    ("untruncated, rank 64", P["u_all_r64"][0], "build"),
    ("untruncated, rank 1024", P["u_all_r1024"][0], "build"),
    ("untruncated, rank 1024, head REFIT (G-RB120)\nv95 twin · 12 nets · refit on 60 FIT nets (0.810 FIT12 held out)", REFIT, "build"),
    ("G-RB119 noise-corrected (v95 twin, 6 nets, split-half extrapolated, 90% CI)", None, None),
    ("exact κ4 diagonal", CI["k4"]["pooled"], "or119", tuple(CI["k4"]["ci90"])),
    ("exact σ²", CI["var"]["pooled"], "or119", tuple(CI["var"]["ci90"])),
    ("exact σ² at z-layers 11–15 only", CI["varL1115"]["pooled"], "or119", tuple(CI["varL1115"]["ci90"])),
    ("exact σ² + κ3 diagonal", CI["var_k3"]["pooled"], "or119", tuple(CI["var_k3"]["ci90"])),
    ("exact σ² + κ3 + κ4", CI["var_k3_k4"]["pooled"], "or119", tuple(CI["var_k3_k4"]["ci90"])),
    ("G-RB117 oracles, SUPERSEDED (uncorrected upper bounds)", None, None),
    ("exact κ4 diagonal", P["k4"][0], "or95"),
    ("exact σ²", P["var"][0], "or95"),
    ("exact σ² + κ3 diagonal", P["var_k3"][0], "or95"),
    ("exact σ² + κ3 + κ4", P["var_k3_k4"][0], "or95"),
    ("G-RB85 noise-corrected (v59_p05 twin, 3 nets, two-half M0)", None, None),
    ("exact κ3 diagonal", 0.79, "or59"),
    ("exact κ4 diagonal", 0.78, "or59"),
    ("exact σ²", 0.57, "or59"),
    ("exact κ3 + κ4", 0.57, "or59"),
    ("exact σ² + κ3", 0.33, "or59"),
    ("whole marginal (noise-flagged)", 0.32, "or59"),
]
COL = {"build": "#0072B2", "or95": "#F2D7A0", "or119": "#E69F00", "or59": "#CC79A7"}
TAG = {"build": "v95 twin · 12 nets · construction, no MC", "or95": "v95 twin · 6 nets · halves averaged", "or119": "v95 twin · 6 nets · MC, split-half extrapolated", "or59": "v59_p05 twin · 3 nets · MC, two-half M0"}
LEADER = 1.09 / 2.11  # live 2026-10-18 leader raw / our graded raw (graded MLPs; cross-instrument)

plt.rcParams.update({"font.size": 7.5, "axes.spines.top": False, "axes.spines.right": False})
fig, ax = plt.subplots(figsize=(9.2, 9.4))
y = 0
yt, yl = [], []
for row in ROWS:
    label, val, grp = row[:3]
    ci = row[3] if len(row) > 3 else None
    if val is None:
        ax.text(0.0, y, label, fontsize=7.5, fontweight="bold", va="center", ha="left")
        y -= 1
        continue
    ax.barh(y, val, color=COL[grp], height=0.7)
    if ci:
        ax.errorbar(val, y, xerr=[[val - ci[0]], [ci[1] - val]], color="black", capsize=2.5, lw=1)
    ax.text((ci[1] if ci else val) + 0.01, y, f"{val:.3f}" if grp != "or59" else f"{val:.2f}", va="center", fontsize=7)
    yt.append(y)
    yl.append(label if "\n" in label else f"{label}\n{TAG[grp]}")
    y -= 1
ax.axvline(1.0, color="#7F7F7F", lw=0.8)
ax.set_yticks(yt)
ax.set_yticklabels(yl)
ax.set_xlim(0, 1.12)
ax.set_ylim(y + 0.3, 1.6)
ax.set_xlabel("final raw MSE, pooled Σ candidate / Σ base (head ON); 1 = the twin as shipped")
fig.tight_layout()
fig.subplots_adjust(left=0.38)
fig.savefig(OUT, dpi=200)
print("wrote", OUT)
