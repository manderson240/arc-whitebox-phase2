#!/usr/bin/env python3
"""Generate the four write-up figures F1-F4 (PNG, 200 dpi) from existing data files.

Run from the arc-whitebox root:
    ulimit -v 4000000; ~/dev/cohezion/.venv/bin/python3 writeup/figs/make_figs.py
Light numpy/matplotlib only; nothing is re-run on the heavy slot.
"""
from __future__ import annotations

import json
from datetime import datetime as dt
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.dates as mdates  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent

# Okabe-Ito colour-blind-safe palette
C = {
    "blue": "#0072B2", "orange": "#E69F00", "green": "#009E73", "red": "#D55E00",
    "purple": "#CC79A7", "sky": "#56B4E9", "yellow": "#F0E442", "black": "#000000",
    "grey": "#7F7F7F",
}
plt.rcParams.update({
    "font.size": 8, "axes.titlesize": 9, "axes.labelsize": 8, "legend.fontsize": 7,
    "xtick.labelsize": 7, "ytick.labelsize": 7, "axes.spines.top": False,
    "axes.spines.right": False, "figure.dpi": 100, "savefig.dpi": 200,
})
W1 = 3.4  # single-column width, inches


# --------------------------------------------------------------------------- F1
def fig1() -> Path:
    # Values transcribed from PROGRESS.md "GRADED" lines / submissions table (verified 2026-10-12).
    ladder = [  # labelled rungs (the brief's list)
        ("v0", "2026-09-27", 3.93e-7), ("v1", "2026-09-27", 1.27e-7),
        ("v3", "2026-09-28", 9.47e-8), ("v5b", "2026-09-28", 6.69e-8),
        ("v6b", "2026-09-28", 1.88e-8), ("v10", "2026-10-01", 1.1845e-8),
        ("v21", "2026-10-06", 9.22e-9), ("v26", "2026-10-06", 8.19e-9),
        ("v31", "2026-10-07", 7.51e-9), ("v43", "2026-10-07", 6.47e-9),
        ("v47", "2026-10-07", 5.74e-9), ("v51", "2026-10-08", 5.46e-9),
        ("v55", "2026-10-08", 5.23e-9), ("v58_ne", "2026-10-10", 4.98e-9),
        ("v59_p05", "2026-10-12", 4.92e-9),
    ]
    others = [  # other graded submissions in PROGRESS.md (unlabelled markers)
        ("2026-09-29", 1.546e-8), ("2026-10-04", 1.0934e-8), ("2026-10-06", 1.0841e-8),
        ("2026-10-06", 9.16e-9), ("2026-10-07", 7.87e-9), ("2026-10-07", 7.28e-9),
        ("2026-10-07", 7.20e-9), ("2026-10-07", 7.06e-9), ("2026-10-07", 6.26e-9),
        ("2026-10-07", 5.93e-9), ("2026-10-07", 5.67e-9), ("2026-10-08", 5.59e-9),
        ("2026-10-08", 5.44e-9), ("2026-10-08", 5.31e-9), ("2026-10-09", 5.23e-9),
    ]
    leader = 1.40e-9          # public board read 2026-10-12 (V11 §1; two figures printed)
    cluster = (3.9e-9, 4.4e-9)  # band per the brief; PROGRESS.md 2026-10-07 read 4.06-4.09e-9

    d = lambda s: dt.strptime(s, "%Y-%m-%d")  # noqa: E731
    x = [d(t) for _, t, _ in ladder]
    y = [v for _, _, v in ladder]

    fig, ax = plt.subplots(figsize=(W1, 2.9))
    ax.set_yscale("log")
    ax.axhspan(*cluster, color=C["sky"], alpha=0.35, lw=0, label="3.9–4.4e-9 cluster")
    ax.axhline(leader, color=C["red"], lw=1.2, ls="--", label=f"leader {leader:.2e}")
    ax.scatter([d(t) for t, _ in others], [v for _, v in others], s=9, color=C["grey"],
               zorder=2, label="other graded")
    ax.plot(x, y, "-o", color=C["blue"], ms=3.5, lw=1.2, zorder=3, label="graded best (ours)")
    for (n, _, v), xi in zip(ladder, x):
        if n in {"v0", "v1", "v3", "v5b", "v6b", "v10", "v21", "v31", "v47", "v55", "v59_p05"}:
            ax.annotate(n, (xi, v), textcoords="offset points", xytext=(4, 3), fontsize=6,
                        color=C["blue"])
    # phase bands
    for (a, b, lab) in [("2026-09-26", "2026-10-02", "method"),
                        ("2026-10-05", "2026-10-08", "cost ladder"),
                        ("2026-10-09", "2026-10-13", "floor")]:
        ax.axvspan(d(a), d(b), color=C["yellow"], alpha=0.18, lw=0)
        ax.text(d(a) + (d(b) - d(a)) / 2, 6e-7, lab, ha="center", va="top", fontsize=7,
                style="italic", color="#444444")
    ax.set_ylim(1e-9, 8e-7)
    ax.set_xlim(d("2026-09-26"), d("2026-10-13"))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %d"))
    ax.xaxis.set_major_locator(mdates.DayLocator(interval=3))
    ax.set_ylabel("graded adjusted score (log)")
    ax.set_title("F1  Graded ladder vs the public leader")
    ax.legend(loc="upper right", frameon=False, ncol=1, bbox_to_anchor=(1.0, 0.92))
    ax.grid(axis="y", which="major", lw=0.4, alpha=0.4)
    fig.tight_layout()
    p = OUT / "F1_graded_ladder.png"
    fig.savefig(p)
    plt.close(fig)
    return p


# --------------------------------------------------------------------------- F2
def fig2() -> Path:
    # Digitised from research/review/LENS_B_math.md §1 table (net 0): MSE(fresh_l) x1e-9 and gain_l.
    # The scratch script that produced it (/tmp/claude/p2_k2_adjoint.py) saved only m2/Phi/a
    # (p2_state.npz), not fresh/gains, so the prose table is the only record.
    layers = np.arange(1, 16)
    fresh = np.array([0.25, 0.57, 1.0, 1.2, 1.7, 2.2, 2.9, 3.0, 3.1, 3.7, 4.5, 3.8, 4.2, 5.9, 5.1])
    gain = np.array([.047, .068, .097, .134, .175, .221, .307, .381, .435, .510, .627, .710, .774,
                     .902, 1.0])
    contrib = fresh * gain
    share = 100 * contrib / contrib.sum()  # sum = 25.5e-9 vs final 2.58e-8 (Lens B)
    last5 = share[-5:].sum()

    fig, ax = plt.subplots(figsize=(W1, 2.6))
    cols = [C["blue"] if l < 11 else C["orange"] for l in layers]
    ax.bar(layers, share, color=cols, width=0.75)
    ax.set_xticks(layers)
    ax.set_xlabel("layer of origin  l")
    ax.set_ylabel("share of final MSE (%)")
    ax.set_title("F2  Where the final error is born (adjoint, net 0)")
    ax.annotate(f"last 5 layers = {last5:.0f} %\n(75–79 % on nets 0/2/4)",
                xy=(13, share[12]), xytext=(4.5, 17), fontsize=7,
                arrowprops=dict(arrowstyle="->", color=C["orange"], lw=0.8), color=C["orange"])
    ax.text(1, share[:8].sum() + 1.5, f"l ≤ 8: {share[:8].sum():.0f} %", fontsize=7,
            color=C["blue"])
    ax.set_ylim(0, 24)
    ax.grid(axis="y", lw=0.4, alpha=0.4)
    fig.tight_layout()
    p = OUT / "F2_error_origin_by_layer.png"
    fig.savefig(p)
    plt.close(fig)
    return p


# --------------------------------------------------------------------------- F3
def fig3() -> Path:
    src = ROOT / "research/rebuild/ladder/v58_ne_noclose_vs_v58_ne_screen_valid.json"
    d = json.loads(src.read_text())
    v = d["rung_data"]["valid"]
    base = {r["net"]: r for r in v["base"]}
    cand = {r["net"]: r for r in v["cand"]}
    nets = sorted(base)
    ratio = np.array([cand[n]["raw"] / base[n]["raw"] for n in nets])  # OFF / ON, raw MSE
    pooled = sum(cand[n]["raw"] for n in nets) / sum(base[n]["raw"] for n in nets)
    worse = int((ratio > 1).sum())
    order = np.argsort(ratio)
    labels = [f"net {nets[i]}" for i in order]

    fig, ax = plt.subplots(figsize=(W1, 3.2))
    cols = [C["red"] if r > 1 else C["green"] for r in ratio[order]]
    ax.barh(np.arange(len(nets)), ratio[order] - 1, left=1, color=cols, height=0.7)
    ax.axvline(1.0, color=C["black"], lw=0.8)
    ax.axvline(pooled, color=C["purple"], lw=1.0, ls="--")
    ax.text(pooled, len(nets) - 0.3, f"pooled {pooled:.4f}", color=C["purple"], fontsize=7,
            ha="left", va="bottom")
    ax.set_yticks(np.arange(len(nets)))
    ax.set_yticklabels(labels, fontsize=6)
    ax.set_xlabel("raw MSE, closure OFF / closure ON (VALID-20, v58_ne)")
    ax.set_title(f"F3  κ4 closure OFF/ON: worse on {worse} of {len(nets)} nets")
    ax.set_xlim(0.95, 1.11)
    ax.grid(axis="x", lw=0.4, alpha=0.4)
    fig.tight_layout()
    p = OUT / "F3_closure_on_off_v58ne.png"
    fig.savefig(p)
    plt.close(fig)
    return p, pooled, worse, len(nets)


# --------------------------------------------------------------------------- F4
def fig4() -> Path:
    src = ROOT / "research/rb67/rb67_slice.jsonl"
    rows = [json.loads(l) for l in src.read_text().splitlines() if l.strip()]
    nets = sorted({r["net"] for r in rows})
    layers = sorted({r["layer"] for r in rows})
    share = {n: [next(r["share_off"] for r in rows if r["net"] == n and r["layer"] == l)
                 for l in layers] for n in nets}
    top32 = {n: [next(r["delta_top32_energy"] for r in rows if r["net"] == n and r["layer"] == l)
                 for l in layers] for n in nets}
    mk = {0: "o", 2: "s", 4: "^"}
    fig, (a1, a2) = plt.subplots(2, 1, figsize=(W1, 3.9), sharex=True)
    for n in nets:
        a1.plot(layers, share[n], marker=mk.get(n, "o"), ms=3, lw=1, color=C["blue"],
                alpha=0.55 + 0.15 * nets.index(n), label=f"net {n}")
        a2.plot(layers, top32[n], marker=mk.get(n, "o"), ms=3, lw=1, color=C["orange"],
                alpha=0.55 + 0.15 * nets.index(n), label=f"net {n}")
    a1.axhspan(0.40, 0.49, color=C["sky"], alpha=0.3, lw=0)
    a1.set_ylabel("‖off Δ‖ / ‖off Tz‖")
    a1.text(2, 0.515, "(1,1,1)-induced share of next-layer D21 norm:\n0.40–0.49, no depth trend", fontsize=6.5,
            color="#333333", va="bottom")
    a1.set_ylim(0.3, 0.58)
    a1.legend(frameon=False, ncol=3, loc="lower left", handlelength=1.5, columnspacing=0.8)
    a2.set_ylabel("Δ energy in top-32\nsingular directions")
    a2.set_ylim(0, 1)
    a2.axhline(0.15, color=C["grey"], lw=0.8, ls=":")
    a2.text(2, 0.17, "pre-registered prediction ≤ 0.15", fontsize=6.5, color=C["grey"])
    a2.set_xlabel("layer")
    a2.set_xticks(layers[::2])
    for a in (a1, a2):
        a.grid(axis="y", lw=0.4, alpha=0.4)
    a1.set_title("F4  G-RB68: Δ sector by layer (FIT 0/2/4)")
    fig.tight_layout()
    p = OUT / "F4_rb68_delta_structure.png"
    fig.savefig(p)
    plt.close(fig)
    return p


if __name__ == "__main__":
    print(fig1())
    print(fig2())
    p3, pooled, worse, n = fig3()
    print(p3, f"pooled {pooled:.4f}, {worse}/{n} worse")
    print(fig4())
