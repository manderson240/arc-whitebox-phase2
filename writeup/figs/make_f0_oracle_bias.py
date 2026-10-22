#!/usr/bin/env python3
"""F0 (headline): Monte-Carlo noise biases oracle-injection readings; split-half correction.

Run from the arc-whitebox root:
    ~/dev/cohezion/.venv/bin/python writeup/figs/make_f0_oracle_bias.py
Every plotted value is read from research/rb119 (and research/rb117/results_seat.jsonl for the
full-noise 'AB' arms, exactly as ci119.py does). Per-noise-level pooled ratios are recomputed from
the raw results_*.jsonl and asserted equal to ci119.json / table119.json; CIs are read from ci119.json.
Noise units (as in tab119.py): full (AB-mean) = 1, a single half (A or B) = 2, the +/-2 dose = 5.
No constant from the write-up is typed here. The dose (noise 5) points exist only for the arms in
results_dose.jsonl (sigma^2 yes, known-answer control no)."""
import json, collections, sys
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[2]
RB = ROOT / "research" / "rb119"
NETS = [0, 2, 4, 5, 6, 7]
R = collections.defaultdict(dict)
files = ([ROOT / "research/rb117/results_seat.jsonl"] + sorted(RB.glob("results_half_*.jsonl"))
         + sorted(RB.glob("results_L1115*.jsonl")) + [RB / "results_dose.jsonl"])
for p in files:
    for l in open(p):
        r = json.loads(l); a, _, h = r["arm"].partition("__"); R[(a, h or "AB")][r["net"]] = r["final"]
base = sum(R[("BASE", "AB")][n] for n in NETS)
def ratio(arm, h):
    d = R.get((arm, h), {})
    return sum(d[n] for n in NETS) / base if all(n in d for n in NETS) else None

CI = json.load(open(RB / "ci119.json")); TAB = json.load(open(RB / "table119.json"))
ci_lines = (RB / "ci119.json").read_text().splitlines()
def jline(arm, key):  # line number of "key" inside arm's block of ci119.json
    s = next(i for i, t in enumerate(ci_lines) if t.startswith(f' "{arm}"'))
    return next(i for i in range(s, len(ci_lines)) if f'"{key}"' in ci_lines[i]) + 1
tab_lines = (RB / "tab119.out").read_text().splitlines()
ci_out = (RB / "ci119.out").read_text().splitlines()
def outline(lines, arm): return next(i for i, t in enumerate(lines) if t.split()[:1] == [arm]) + 1

ARMS = {"sig": ("var", "per-neuron $\\sigma^2$ oracle (all layers)"),
        "ctl": ("var_k3_k4_h0", "known-answer control (should be 0)")}
pts, extrap = {}, {}
for k, (arm, _) in ARMS.items():
    f, A, B = ratio(arm, "AB"), ratio(arm, "A"), ratio(arm, "B")
    xs, ys = [1, 2], [f, 0.5 * (A + B)]
    T2, Tm2 = ratio(arm, "T2"), ratio(arm, "T-2")
    if T2 is not None and Tm2 is not None:
        xs.append(5); ys.append(0.5 * (T2 + Tm2))
    pts[k] = (xs, ys)
    extrap[k] = 2 * f - 0.5 * (A + B)
    assert abs(extrap[k] - CI[arm]["pooled"]) < 1e-9 and abs(f - CI[arm]["full"]) < 1e-9, arm
for arm in ("var", "var_k3_k4_h0", "varL1115"):
    assert abs(ratio(arm, "AB") - CI[arm]["full"]) < 1e-9
assert abs(ratio("var", "T2") - TAB["var"]["T2"]) < 1e-9

OI = dict(blue="#0072B2", verm="#D55E00", green="#009E73", grey="#7f7f7f")
plt.rcParams.update({"font.size": 7.5, "axes.linewidth": 0.7, "font.family": "DejaVu Sans"})
fig, (a1, a2) = plt.subplots(1, 2, figsize=(7.0, 3.0), gridspec_kw=dict(width_ratios=[1.15, 1]))

# (a) ratio vs injected-truth noise level
for k, col, mk in (("sig", OI["blue"], "o"), ("ctl", OI["verm"], "s")):
    arm, lab = ARMS[k]; xs, ys = pts[k]
    a1.plot([0, 2], [extrap[k], ys[1]], ls="--", color=col, lw=1, zorder=1)  # 2-pt line through 1,2 -> 0
    a1.plot(xs, ys, mk, color=col, ms=5, label=lab, zorder=3)
    lo, hi = CI[arm]["ci90"]
    a1.errorbar([0], [extrap[k]], yerr=[[extrap[k] - lo], [hi - extrap[k]]], fmt="*", ms=9, color=col,
                mec="k", mew=0.5, capsize=2.5, lw=1, zorder=4)
    a1.annotate(f"raw {ys[0]:.3f}", (1, ys[0]), ((0.3, 1.0) if k == "sig" else (1.2, 0.08)), fontsize=7, color=col,
                arrowprops=dict(arrowstyle="-", color=col, lw=0.5))
    a1.annotate(f"{extrap[k]:.3f}", (0, extrap[k]), (0.15, extrap[k] - (0.14 if k == "sig" else 0.1)),
                fontsize=7, color=col, fontweight="bold")
a1.axhline(0, color=OI["grey"], lw=0.6)
a1.set_xlabel("noise level of the sampled truth (1 = full mean, 2 = one half, 5 = dose)")
a1.set_ylabel("MSE ratio vs baseline (pooled, 6 nets)")
a1.set_xticks([0, 1, 2, 3, 4, 5]); a1.set_xlim(-0.35, 5.4); a1.set_ylim(-0.15, 2.0)
a1.legend(loc="upper left", frameon=False, fontsize=6.8)
a1.text(0.97, 0.45, "stars: zero-noise extrapolation, 90% CI\n(between-net bootstrap)", transform=a1.transAxes,
        ha="right", va="bottom", fontsize=6.3, color=OI["grey"])
a1.set_title("(a) extrapolating to zero noise", fontsize=8, loc="left")

# (b) uncorrected vs corrected with CIs
GROUPS = [("var", "$\\sigma^2$\nall layers"), ("varL1115", "$\\sigma^2$\nlayers 11-15"),
          ("var_k3_k4_h0", "known-answer\ncontrol")]
w = 0.36
for i, (arm, lab) in enumerate(GROUPS):
    raw, cor = CI[arm]["full"], CI[arm]["pooled"]; lo, hi = CI[arm]["ci90"]
    a2.bar(i - w / 2, raw, w, color=OI["grey"], label="uncorrected (full noise)" if i == 0 else None)
    a2.bar(i + w / 2, cor, w, color=OI["green"], label="split-half corrected" if i == 0 else None)
    a2.errorbar(i + w / 2, cor, yerr=[[cor - lo], [hi - cor]], color="k", capsize=3, lw=0.9)
    a2.text(i - w / 2, raw + 0.02, f"{raw:.3f}", ha="center", va="bottom", fontsize=7)
    a2.text(i + w / 2 + 0.02, hi + 0.02, f"{cor:.3f}", ha="center", va="bottom", fontsize=7, fontweight="bold")
a2.axhline(0, color="k", lw=0.6)
a2.set_xticks(range(3)); a2.set_xticklabels([g[1] for g in GROUPS], fontsize=7)
a2.set_ylabel("MSE ratio vs baseline"); a2.set_ylim(-0.08, 0.95)
a2.legend(loc="upper right", frameon=False, fontsize=6.8)
a2.set_title("(b) uncorrected vs corrected, 90% CI", fontsize=8, loc="left")
for a in (a1, a2):
    a.spines[["top", "right"]].set_visible(False)
fig.tight_layout()
out = ROOT / "writeup/figs/F0_oracle_noise_bias.png"
fig.savefig(out, dpi=300); print("wrote", out)

# ---- plotted-number table with sources ------------------------------------------------------
rel = lambda p: str(Path(p).relative_to(ROOT))
print("\nPLOTTED NUMBERS (value | source file:line)")
for k, (arm, _) in ARMS.items():
    xs, ys = pts[k]
    for x, y in zip(xs, ys):
        print(f"(a) {arm:14s} noise={x}: {y:.4f} | recomputed from results_*.jsonl "
              f"({', '.join(sorted({rel(p) for p in files if any(arm == q.partition('__')[0] for q in [json.loads(l)['arm'] for l in open(p)])}))})")
    lo, hi = CI[arm]["ci90"]
    print(f"(a) {arm:14s} noise=0 extrap: {extrap[k]:.4f}  CI90[{lo:.4f},{hi:.4f}] | research/rb119/ci119.json:{jline(arm,'pooled')}-{jline(arm,'ci90')+2}; ci119.out:{outline(ci_out,arm)}")
for arm, _ in GROUPS:
    print(f"(b) {arm:14s} uncorrected {CI[arm]['full']:.4f} | ci119.json:{jline(arm,'full')}, ci119.out:{outline(ci_out,arm)}"
          f"; corrected {CI[arm]['pooled']:.4f} CI90[{CI[arm]['ci90'][0]:.4f},{CI[arm]['ci90'][1]:.4f}] | ci119.json:{jline(arm,'pooled')}")
for arm in ("var", "var_k3_k4_h0"):
    print(f"cross-check tab119.out:{outline(tab_lines,arm)}  {tab_lines[outline(tab_lines,arm)-1]}")
