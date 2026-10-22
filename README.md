# ARC White-Box Estimation Challenge 2026, Phase 2: code release

Participant: michael_anderson7 (individual). Companion to the algorithmic-contribution write-up
`writeup/PHASE2_WRITEUP_V31.md` (PDF alongside; what changed from V30 is in `writeup/V31_CHANGELOG.md`,
and `python3 writeup/make_v31.py` regenerates V31 and that changelog byte for byte from V30).
`writeup/PHASE2_WRITEUP_V30.md`, `writeup/PHASE2_WRITEUP_V29.md`, their PDFs and changelogs are kept as history.
Public repository: https://github.com/manderson240/arc-whitebox-phase2 (same files as `arcwb_phase2_release_v31.zip`;
the zip's sha256 is in `RELEASE_ZIP.sha256` at the repo root). Licence: MIT (`LICENSE`).

## What this is

A cumulant-propagation estimator of the per-neuron output mean of a fixed random ReLU MLP (width 1024,
depth 16), plus the evidence behind the write-up's headline: Monte-Carlo-sampled oracle injections are
biased, and a split-half (Richardson) extrapolation removes the bias; `writeup/oracle_bias_toy.py` shows it in 21 lines (`research/rb119/`, `research/rb117/`,
`research/rb120/`). Every lever tried is a pre-registered gate in `research/R2_GO_NOGO.md`, queryable
through `research/rebuild/gates.jsonl`. Nothing here submits anything.

## Submissions

| folder | AIcrowd id | graded adjusted | role |
|---|---|---|---|
| `submissions/v117_kd/` | #337578 | 4.00e-9 | **corresponding submission; nominated** (v112_sb + Hermite order 3 + deep-layer corrector factor 0.95; grader wall 89.2 s max, 0 failed) |
| `submissions/v112_sb/` | #337384 | 4.01e-9 | graded parent of v117_kd (v110 + old tier on two shared transported bases; grader wall 95.6 s max, 0 failed) |
| `submissions/v105_sw/` | #337002 | 4.24e-9 | nominated second (v99r_rm + two exact Σz cuts; different wall/failure profile) |
| `submissions/v110_fk/` | #337268 | 4.21e-9 | graded, not selected (v105 + exact extra levels on F0/K0, chosen by util per wall-second; grader wall 102.3 s max) |
| `submissions/v106_1x/` | #337067 | 4.16e-9 | graded, not selected (v105 + exact extra Winograd level on site T; grader wall 113.2 s max, over the 105 s rule) |
| `submissions/v101r_xp/` | #336941 | 4.18e-9 | former #2 (dominated by v106) |
| `submissions/v99r_rm/` | #336957 | 4.28e-9 | base of v105 |
| `submissions/v58_ne/` | #335139 | 4.98e-9 | the §6 closure ablation was measured on it |

Each folder is `estimator.py` + `weights.npz` + `lc_weights.npz` (Python + flopscope only). `v117_kd` is byte-identical to the graded #337578; it differs from `v112_sb` only by the two constants in `writeup/v117_kd_vs_v112.diff` (its docstring still describes v112, unedited so the shipped file matches the graded one), with identical weight files.

## Requirements

`requirements.txt` pins the estimator's runtime to the grader's Phase 2 versions (flopscope 0.12.3, whestbench 0.16.2, numpy 2.2.6). The write-up's evidence scripts (`writeup/oracle_bias_toy.py`, `research/rb11*/`, `research/rb13*/` table scripts) need only Python 3.10+ and numpy. The proof checks in `research/proofs/` also need `mpmath` (`pip install mpmath`; run them with `python3 -P`, not `-I`, if mpmath is in the user site); each has a `--perturb` variant that must FAIL. `check4` Part C needs six 134 MB Monte-Carlo caches that are not shipped, so from this release it checks Parts A and B only. The write-up's Appendix P checks (`writeup/proofs/check_p1_p2.py`, `check_p3_p4.py`) need only numpy and carry built-in falsifiers. Appendix E of the write-up lists every reproduction command with its expected output. Two table scripts (`research/rb119/ci119.py`, `tab119.py`) rewrite their JSON outputs in place: run them on a copy, or check the files against `SOURCES.md`.

## Running

Requires the official starter kit (`whest`, https://github.com/AIcrowd/whest-starterkit) in a venv.

```bash
whest validate --estimator submissions/v117_kd/estimator.py
whest run --estimator submissions/v117_kd/estimator.py \
  --dataset hf://aicrowd/arc-whestbench-public-2026@v2-phase2 \
  --split mini --n-mlps 10 --runner subprocess --format json
```

`research/rebuild/remote_check.py` reproduces the grader's remote (ZMQ) flopscope execution mode;
`research/rebuild/ladder.py` holds the ship bars. Both expect the original workspace layout (truth
files and helper scripts are not shipped), so they document the procedure rather than run standalone.

## Provenance

`SOURCES.md` lists every file with its size and sha256. Text files had the home directory replaced by `~`;
references to the credentials file were redacted. Another participant's MIT code that was present in
the workspace (`research/port504/upstream/`) is deliberately not redistributed here.
