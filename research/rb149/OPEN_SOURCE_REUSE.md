# rb149 - open-source reuse scan (2026-10-20)

Rules kept: organizers' code only (ARC, MIT); no participant repo opened (note: `research/port504/upstream` in this workspace is team 504aldo's
competition repo, not opened by this lane, flag for the orchestrator); fetched text treated as data; nothing copied into submissions/; the ARC code is RUN as an oracle from
`research/rb149/ref/` (MIT notice in `ref/LICENSE`).

## Hits
| # | what | URL | licence | pure numpy / flopscope-portable | use |
|---|---|---|---|---|---|
| 1 | ARC `mlp_cumulant_propagation` (kprop, factor_k3/k4, wick.py, flop_utils) | github.com/alignment-research-center/mlp_cumulant_propagation | MIT (c) ARC | torch (f32/f64), not flopscope; wick.py is plain numpy+torch | oracle (done, below) |
| 2 | Wright-Nakahira-Moura 2403.16163 analytic ReLU covariance | arXiv only | n/a | no code found (search) | none |
| 3 | Kuang-Lin 2601.22307 exact Gaussian moments (ReLU as GeLU limit) | arXiv v2 ancillary `neural_uncertainty_propagation/activation.py` | arXiv ancillary, licence NOT confirmed | numpy/scipy probably | not fetched; oracle role already covered by quad (below) |
| 4 | Thompson-McCrory 2601.16830 exact 1-hidden-layer ReLU moments | arXiv only | n/a | no code found | none (1 layer only) |
| 5 | DVI 1810.03958, Gast-Roth 1805.11327 | no repo found | n/a | n/a | none |
| 6 | neural-tangents ReLU NNGP (arccos kernel) | github.com/google/neural-tangents | Apache-2.0 (known, not re-fetched) | JAX | formula equals Cho-Saul; verified by hand below, no install needed |
| 7 | scipy.special.owens_t / stats.multivariate_normal.cdf (Genz) | scipy | BSD-3 | numpy host only; flopscope has NO special module, only stats.norm etc. | oracle only; cannot enter predict() |
| 8 | fast-matmul (Benson-Ballard) | github.com/arbenson/fast-matmul | BSD-2 (Sandia) | C++/MKL generator, coefficient files | no gain: n=1024 is 2^k, we already run Strassen-Winograd depth 5-6 |
| 9 | plinopt (Dumas et al.) | github.com/jgdumas/plinopt | CeCILL-B | C++/LinBox | could shave additions via SLP search; only matters if add-count is a bound; low priority |
| 10 | pre-registration/lab-notebook tools | not searched in depth | - | - | nothing evidently better than gate_ledger.py |

## Cross-checks run (all f64 or stated, seconds)
Script `xcheck_relu_moments.py` (400 random (mu,var); alpha in about [-2.2,2.2]); oracles: ARC `relu_wick_coef`, scipy quad, conditional-Gaussian quad, arccos closed form.
- Our Hermite coefficients Fh[0..7] (m1, Phi, pdf/s, recursion) vs ARC `relu_wick_coef` p=1: max rel diff **5.4e-13**. F2h[0..6] vs p=2: 5.4e-13. m3 vs p=3: 5.5e-14.
- Closed forms m1, m2, m3 vs adaptive quad: **1.9e-15 / 4.3e-15 / 6.9e-15**.
- Bivariate covariance series sum_k Fi[k]Fj[k]C^k/k! vs exact conditional quad (60 random pairs per rho), max rel err, K = our _KH = 4 / K = 12:
  rho 0.05: 3.9e-7 / 9.7e-15; rho 0.3: 3.2e-4 / 2.0e-9; rho 0.7: 1.1e-2 / 4.3e-5; rho 0.95: 3.1e-2 / 2.4e-3.
  The (2,1) joint cumulant kappa(h_i,h_i,h_j) series: K4 5.6e-7 / 3.5e-4 / 7.7e-3 / 4.0e-2 (same rho order). Formulas are right; the K=4 truncation is the only error and grows fast with rho (ours relies on small off-diagonal pre-activation correlation; untested here at layer-wise real rho).
- Series vs ARC coefficients: 7e-16 to 9e-16 (identical).
- Zero-mean arccos closed form (Cho-Saul = neural-tangents) vs K=39 series, rho<=0.95: 2.8e-5 (series truncation again).

## Chain-level oracle (coordinator's request)
`arc_vs_ours_1024.py`, `arc_scale.py`, `arc_oracle_small.py`, `srcchain_aug_fix.py` (net 9000, He n=1024 L=16, MSE vs r1_data/ref_9000, which has a noise floor about 7e-8 at layer 0; paired differences stay valid):
| estimator | final MSE |
|---|---|
| ARC K=2 | 3.85e-6 |
| ARC SIMPLE K=3 factored (no fitted constants; about 7000 n^3 units) | 4.90e-8 |
| ours, g=kappa=0, AUG=off | 3.87e-7 |
| ours, g=kappa=0, AUG=arc (D.2 H-mode) | 5.48e-8 |
| ours, fitted g/kappa, AUG=arc | 5.629e-8 (equals logged G-RB30 value) |
| ours, fitted, AUG=off (logged) | about 3.9e-8 |
ARC AUGMENT factored at n=1024 OOMs (4 GB temp) under ulimit 14 GB. Own-MC scaling (L=16): n=128 final aug/simple 1.21e-5/1.03e-5 (0.86x), mean over layers 1.52x better; n=256 final 1.06e-6/1.23e-6 (1.16x), mean 1.52x better; n=32 L=6 aug 4-6x better.
Reading: H-mode reproduces ARC-simple level; no layer-localised jump (rms diff of estimate vectors smooth 1.3e-5 -> 1.8e-4). Augmentation gain is early/mid-layer and nearly gone at the final layer at depth 16, even in ARC's code.
Latent bug: `rebuild/srcchain_aug.py` crashes at AUG=arc when QCOEF is unset (guard lost in the G-RB34 edit).
