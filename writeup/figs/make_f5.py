#!/usr/bin/env python3
"""F5 (rival raw-vs-util trajectories) and the V16 refresh of F1 (graded ladder to v80_kk).

Run from the arc-whitebox root:
    ~/dev/cohezion/.venv/bin/python3 writeup/figs/make_f5.py
Sources: research/leaderboard/insights/p2_rows.json (fields t, sid, adj, raw, u, f, who; filter f == 0
and raw < 1e-6); F1 values from PROGRESS.md "GRADED" lines and research/rebuild/calibration.jsonl.
Style follows writeup/figs/make_figs.py. F1 is written to a NEW file (F1_graded_ladder_v16.png) so that
the V15 figure is left untouched.
"""

from __future__ import annotations

import json
from datetime import datetime as dt
from pathlib import Path

import matplotlib


matplotlib.use("Agg")
import matplotlib.dates as mdates
import matplotlib.pyplot as plt


ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
C = {
    "blue": "#0072B2",
    "orange": "#E69F00",
    "green": "#009E73",
    "red": "#D55E00",
    "purple": "#CC79A7",
    "sky": "#56B4E9",
    "yellow": "#F0E442",
    "black": "#000000",
    "grey": "#7F7F7F",
}
plt.rcParams.update(
    {
        "font.size": 8,
        "axes.titlesize": 9,
        "axes.labelsize": 8,
        "legend.fontsize": 7,
        "xtick.labelsize": 7,
        "ytick.labelsize": 7,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "figure.dpi": 100,
        "savefig.dpi": 200,
    }
)

TEAMS = [  # (name in p2_rows.json, colour, marker)
    ("AndreasHad04", C["blue"], "o"),
    ("J2W", C["red"], "s"),
    ("huang_chung_yi", C["green"], "^"),
    ("Puffi", C["orange"], "D"),
    ("marius_binner", C["purple"], "v"),
    ("michael_anderson7", C["black"], "*"),
]


def record_steps(rows):
    best, out = 9.0, []
    for r in rows:
        if r["raw"] < best:
            best = r["raw"]
            out.append(r)
    return out


def fig5() -> Path:
    # frozen snapshot (git bbe858d, 2026-10-16): the live p2_rows.json is overwritten by every insights.py run
    rows = json.loads((ROOT / "research/leaderboard/insights/p2_rows_20261016.json").read_text())
    rows = [r for r in rows if r["f"] == 0 and r["raw"] < 1e-6]
    fig, ax = plt.subplots(figsize=(6.2, 4.3))
    for name, col, mk in TEAMS:
        mine = sorted((r for r in rows if r["who"] == name), key=lambda r: r["sid"])
        ax.scatter(
            [r["u"] for r in mine], [r["raw"] for r in mine], s=5, color=col, alpha=0.15, lw=0
        )
        rec = record_steps(mine)
        ax.plot([r["u"] for r in rec], [r["raw"] for r in rec], "-", color=col, lw=1.0, alpha=0.9)
        ax.scatter(
            [r["u"] for r in rec],
            [r["raw"] for r in rec],
            s=22 if mk == "*" else 9,
            marker=mk,
            color=col,
            zorder=3,
            label=f"{name} ({len(rec)} record steps)",
        )
        last = rec[-1]
        ax.annotate(
            f"{last['raw']:.3g}",
            (last["u"], last["raw"]),
            textcoords="offset points",
            xytext=(3, -8),
            fontsize=6,
            color=col,
        )
    ax.scatter([0.246], [2.23e-8], s=60, facecolors="none", edgecolors=C["grey"], zorder=4)
    ax.annotate(
        "AndreasHad04 passes our raw\n2.23e-8 at util 0.246",
        (0.246, 2.23e-8),
        xytext=(0.30, 3.4e-8),
        fontsize=6.5,
        color=C["grey"],
        arrowprops=dict(arrowstyle="->", color=C["grey"], lw=0.7),
    )
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlim(0.095, 0.5)
    ax.set_ylim(1.0e-8, 4.5e-8)
    ax.set_xticks([0.1, 0.15, 0.2, 0.3, 0.4, 0.5])
    ax.set_xticklabels(["0.1", "0.15", "0.2", "0.3", "0.4", "0.5"])
    ax.set_yticks([1e-8, 1.5e-8, 2e-8, 3e-8, 4e-8])
    ax.set_yticklabels(["1e-8", "1.5e-8", "2e-8", "3e-8", "4e-8"])
    ax.minorticks_off()
    ax.set_xlabel("utilisation (billed FLOPs / 2^41)")
    ax.set_ylabel("raw final-layer MSE")
    ax.set_title(
        "F5  Raw vs utilisation, record-raw steps (axes clipped to util <= 0.5)", fontsize=8
    )
    ax.legend(frameon=False, loc="upper center", bbox_to_anchor=(0.5, -0.14), ncol=3, fontsize=6.5)
    ax.grid(which="major", lw=0.4, alpha=0.4)
    fig.tight_layout()
    p = OUT / "F5_rival_trajectories.png"
    fig.savefig(p)
    plt.close(fig)
    return p


def fig1_v16(extra=(), leader=None, leader_name="J2W", tag="v16", last="v80_kk") -> Path:
    ladder = [
        ("v0", "2026-09-27", 3.93e-7),
        ("v11", "2026-10-04", 1.0934e-8),
        ("v21_rb", "2026-10-06", 9.22e-9),
        ("v42_g92", "2026-10-07", 7.06e-9),
        ("v49", "2026-10-08", 5.59e-9),
        ("v51", "2026-10-08", 5.46e-9),
        ("v55", "2026-10-08", 5.23e-9),
        ("v57", "2026-10-09", 5.23e-9),
        ("v58_ne", "2026-10-10", 4.98e-9),
        ("v59_p05", "2026-10-12", 4.92e-9),
        ("v77_fsc", "2026-10-12", 4.87e-9),
        ("v77_fuse", "2026-10-13", 4.92e-9),
        ("v78_p02", "2026-10-13", 4.80e-9),
        ("v80_kk", "2026-10-15", 4.84e-9),
    ] + list(extra)
    leader = leader or 1.36e-8 * 0.1065148461  # J2W raw x util, unrounded (board prints 1.4e-9)
    d = lambda s: dt.strptime(s, "%Y-%m-%d")  # noqa: E731
    fig, ax = plt.subplots(figsize=(3.4, 2.9))
    ax.set_yscale("log")
    ax.axhline(
        leader,
        color=C["red"],
        lw=1.2,
        ls="--",
        label=f"{leader_name} {leader:.3g}e (raw x util)".replace("e ", " "),
    )
    ax.plot(
        [d(t) for _, t, _ in ladder],
        [v for _, _, v in ladder],
        "-o",
        color=C["blue"],
        ms=3.5,
        lw=1.2,
        label="graded (ours)",
    )
    for n, t, v in ladder:
        if n in {"v0", "v11", "v21_rb", "v51", last}:
            ax.annotate(
                n,
                (d(t), v),
                textcoords="offset points",
                xytext=(-14, 6) if n == last else (4, 3),
                fontsize=6,
                color=C["blue"],
            )
    ax.set_ylim(1e-9, 8e-7)
    ax.set_xlim(d("2026-09-26"), d("2026-10-17"))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %d"))
    ax.xaxis.set_major_locator(mdates.DayLocator(interval=4))
    ax.set_ylabel("graded adjusted score (log)")
    ax.set_title(
        f"F1  Graded ladder to {last}"
        if tag != "v16"
        else f"F1  Graded ladder to {last} vs the {leader_name} level"
    )
    ax.legend(loc="upper right", frameon=False)
    ax.grid(axis="y", which="major", lw=0.4, alpha=0.4)
    fig.tight_layout()
    p = OUT / f"F1_graded_ladder_{tag}.png"
    fig.savefig(p)
    plt.close(fig)
    return p


if __name__ == "__main__":
    print(fig5())
    print(fig1_v16())
    # V18 (2026-10-16): graded lineage from research/rebuild/calibration.jsonl; leader = marius_binner raw 1.10e-8 x util 0.123 (insights)
    print(
        fig1_v16(
            extra=[
                ("v84", "2026-10-16", 4.72e-9),
                ("v87_p02", "2026-10-16", 4.60e-9),
                ("v88_stk", "2026-10-16", 4.52e-9),
                ("v90_al", "2026-10-16", 4.43e-9),
                ("v95_khs", "2026-10-17", 4.41e-9),
            ],
            leader=1.10e-8 * 0.123,
            leader_name="marius_binner",
            tag="v19",
            last="v95_khs",
        )
    )
