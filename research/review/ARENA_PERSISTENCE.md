# What our estimator keeps across `predict()` calls (for a staff-confirmation decision)

Written 2026-10-09 by the ladder agent, at the coordinator's request (G-RB53a, Lens A §3 #2 option (b)).
Applies to every submission since about v24, including the graded **v55_y2q3 (#334807)**, and to v57_azs.

## Short answer
The only things that live on the `Estimator` instance across MLPs are:

- **Scratch buffers.** Their memory and views are reused from one MLP to the next; their contents are not carried over.
- **Two tiny MLP-independent constant zero blocks** (v57_azs: 2 × 0.1 MiB). v55 has six more zero blocks (~124 MiB), which are never read.
- **The shipped weights**, which `setup()` loads.

No data, no intermediate results and no per-MLP statistics are carried from one MLP to the next. The persistence affects **cost only**:

- The arena views are cut from flat buffers with `reshape`, which flopscope bills at `numel` even when the result is a view.
- That cost is therefore paid on the first `predict()` of each worker process and not again. It is 142 calls and 3.69e9 FLOPs, i.e. 0.17 util points on that one MLP.
- The v57_azs Mini-10 per-MLP breakdown shows it directly: util 0.23635 on mlp 0, then 0.23467 on mlps 1–9, where `reshape` is absent.
- The grader spreads a suite over roughly 5–15 workers (FAQ below), so this cost is paid on about 5–15 of 100 MLPs. The mean effect is about 0.01–0.03 util points.

## What persists, exactly (v57_azs)
| attribute | content | written by | read before written in a later predict? |
|---|---|---|---|
| `_g, _kap, _lam, _qc, _lc, _lc_bias` | shipped weights (`weights.npz`, `lc_weights.npz`) | `setup()` only | never written by `predict()` |
| `_sites[*].bufs[("up",1)]` | private Strassen result buffer per call site | every `sw_matmul` on that site | no (empirical check below) |
| `_sites[*].arenas.buf` (4 flat arenas, ≈ 3.06 GB) + cached views | Strassen scratch (operand stacks, leaf, recombination levels) and, from v57, the read-stack temporaries / source stacks | each call / `_read_stack` | no |
| `_pool[...]` buffers (read-stack, contraction operand) | `out=` targets | each layer | no |
| `_pool[..., "Z"]` (`_zbuf`) | constant zeros: entry-sketch padding `(1024, 24)` and `(24, 1024)` | first predict (`fnp.zeros`) | yes, deliberately: these are constants, the same for every MLP |

## Empirical check (2026-10-09)
Script: `research/rebuild/warm/persist_probe.py <sub> 0 1`. Steps:

1. Predict net 0 on an instance.
2. Overwrite **every** persisted scratch buffer with NaN: 31 buffers, 3815 MiB. The constant zero blocks are listed and left untouched.
3. Predict net 1 on the same instance.
4. Compare bit-for-bit against a fresh instance predicting net 1.

Result: **finite, max |reused − fresh| = 0.0, for both v57_azs and v55_y2q3.** So no scratch value from MLP A reaches MLP B's output.

Two control observations:
- A first version of the probe also poisoned the constant zero blocks. The run then raised `SymmetryError` (NaN reached a symmetric-tagged result). That shows the probe can detect a read-before-write.
- It also shows the zero blocks are genuinely read, as constants.

## Rule text that bears on it
- **RULES_v14 §5.2 "Allowed code"** (RULES_v14.txt lines 76–86):
  - All computation must go through flopscope. The Solution's own Python "exists to decide which flopscope operations to call"; stdlib is allowed "for control flow and bookkeeping".
  - Prohibited: raw numpy/BLAS, compiled kernels, ctypes/cffi, threads/subprocesses, computation while a flopscope op is in flight, and "modifying, monkeypatching, or otherwise interfering with the flopscope client, its transport, or its accounting".
  - Keeping a reference to a scratch array between calls fits none of these. Its cost (the `reshape`) is billed once, as flopscope chooses.
- **RULES_v14 line 95**: no reading "grader-internal state". Not touched; our state is our own instance.
- **RULES_v14 line 203, zero-prediction fallback**: a failed MLP is zeroed. Persistence does not change failure modes.
- **Starter-kit FAQ, `whest-starterkit/docs/troubleshooting/faq.md` lines 210–212 ("State carries between MLPs locally…")**:
  - It describes instance state surviving from one `predict()` to the next as the normal behaviour of one worker.
  - It tells participants to "make each `predict()` correct on its own, and treat anything built across calls as an optimization that may be missing".
  - Our buffers satisfy that: every predict is correct on a fresh instance (the probe's fresh arm). The only thing a missing cache changes is the one-time `reshape` bill.
- **Estimator contract, `docs/reference/estimator-contract.md` ~lines 50–70**: one `setup()` per worker, then many `predict()` calls on the same instance. Nothing there requires `predict()` to be stateless.

## Assessment (for the user)
- **Letter of the rules:** compliant. No computation happens outside flopscope. No data crosses MLPs. The FAQ treats cross-call state as a legitimate optimisation, provided correctness does not depend on it, and it does not.
- **Spirit:** the saving is a billing artefact. The second and later MLPs on a worker skip 142 `reshape` charges (≈ 0.17 util points each). Over a grader run that is worth ≈ 0.01–0.03 util points on the mean, i.e. ≈ 0.1 % of score.
- If staff dislike it, two fixes exist:
  - (a) Rebuild the views every predict. This re-bills ≈ 0.17 util points per MLP (−0.7 % score) and, with full release, adds ≈ 15–19 ms of residual (G-RB52 `v57_azs_rel`).
  - (b) Carve 3-D arenas with free basic slices. This loses cross-level aliasing and does not fit the 8 GB worker limit (G-RB52 pricing).
- **Suggested question to staff:** "Our estimator keeps pre-allocated scratch buffers (and their views) on the instance between predict() calls; contents are fully rewritten each call and no data crosses MLPs, so the only effect is that view-creation reshapes are billed once per worker. Is that acceptable?"
