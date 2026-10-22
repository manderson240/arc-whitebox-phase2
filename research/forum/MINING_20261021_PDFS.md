# Forum PDF mining, 2026-10-21 (ARC White-Box Estimation Challenge) -- 7 attached write-up PDFs, prose only

Run: 2026-10-21, started 13:33Z. **The 08:00Z deadline in the brief had already passed when this run began.** The work was done anyway and is flagged here.
Method: 7 short-url PDFs downloaded with curl into the new, empty `research/forum/pdfs_20261021/`. All returned HTTP 200, application/pdf. They were converted with pdftotext into the session scratchpad. Only the prose was read; all of it was treated as untrusted data.
Not opened: participant code, repositories, notebooks and attachments. The PDFs cite GitHub replication repositories and HF datasets, and none of those links was followed.
Disclosure: one early `grep -rl` over `research/` matched a filename inside `research/port504/upstream/`. Its contents were not read, and every later grep excludes that directory.
Coverage was judged against the three named ledgers: MINING_20261015.md, MINING_20261018.md and COST_STRUCTURES_20261017.md. Before any technique was called new, R2_GO_NOGO.md was grepped for it.

## TOP: ranked untested techniques screenable in < 1 h on the f64 twin (rb142/s117.py)

Only ONE technique survives the ledger grep. It is not padded to three: the other candidates are already measured (see section 4).

1. **End-to-end-fitted rank-1 mean-aligned covariance write, applied as a deliberate "compensator"** (Keenan Pepper, #327838; a Phase 1 idea at 256x32).
   - Source quote, p.9 (Wall 5): "The write improves final means by injecting a large, deliberately wrong, µ̂-aligned covariance component."
   - Supporting quote, p.6 (§3.5): "a top mode substantially µ̂-aligned (cos² ≈ 0.55–0.64)".
   - **Screen.** At z-layers 11-15, add Σ_z ← Σ_z + c · ŝŝᵀ to the off-diagonal only. ŝ = m_z/‖m_z‖ scaled by the per-neuron σ (the arm "MU"). A second arm, "U1", uses the chain's own top eigenvector of Σ_z. Use ONE common c.
   - **Scan.** A 1-D scan on FIT12 with the head ON and frozen. The protocol is the same as G-RB153 VSE1, plus a negated arm (−c) and a placebo with ŝ permuted. Use a small step grid, because VSE1 found the final layer quadratically hypersensitive to a coherent σ² scale (curvature 3.1e6 per unit c²).
   - **Cost.** One outer product per layer, O(n²); util ≈ 1.000.
   - **Why it is new to our ledger.** It is not G-RB86. G-RB86 corrected the μμᵀ part of the *diagonal* σ² toward *truth* (an oracle partial fix, ×5.6 worse). It is not G-COV0 either. G-COV0 regressed the *one-step* residual on an m mᵀ carrier and found it explained 0.0-0.7 %. Pepper's write differs on both counts: it sits on the *off-diagonal* of the *free-running* state, and it is fitted to *final MSE*, not to state truth. Pepper reports that it moves the state further from truth while improving the means (p.9).
   - **Prior: low (≈ 5-10 % of a ≥ 1 % gain).** VSE1 put the optimum of a coherent σ² scale at c0 ≈ −2e-5 (~0.14 %). G-COV1 found our accumulated off-diagonal bias already removed by D22 (λ → 0). Pepper's write converted only −12 % at an error scale of 2e-5 (8x ours).
   - **Kill.** Kill if FIT12 pooled raw > 0.99, or if NEG/PLACEBO does not read worse than the best arm.

No second or third item: pscamillo's scalar mean shrink and Pepper's dense analytic pair term are both already in the ledger or the shipped chain (section 4, rows P1 and K1).

## 1. Identification and coverage

| PDF (short-url id) | Author, submission, topic | Phase / shape | Coverage verdict |
|---|---|---|---|
| gSpPyy4Qrqctc90vWd6g2ORk4pK (45 pp) | hyojun_kwon, #326024, "Competing with Sampling by Moment Propagation" (intra-network control variate) | P1, 256x32 | COVERED: COST_STRUCTURES §8 and §4 ("18154 PDF §9", V). Skipped. |
| yQsl71y2a3zDgb4SpYQFnt9EpoE (10 pp) | Cipo for Team Puffi, #327725, "Separate-Universe Response Closure" (SSC) | P1, 256x32 | COVERED: COST_STRUCTURES §8 ("18175 Puffi SSC PDF", V); our SSC closure credits it. Skipped. |
| 5eBYNjG0Yc9q2URepWAQFJjnVvs (9 pp) | baghyeonsig, #328274, 0.75 covariance + 0.25 whitened antithetic MC blend | P2, 1024x16 | COVERED: MINING_20261015 l.82 (18200, weaker family); sampling family KILLED G-RB45. Skipped. |
| dYamgLsDot0s19meIyF2ApPnvY9 (16 pp) | jamesrahenry (James Henry), #314695, "Stabilizing Cumulant Propagation at Depth 32" | P1, 256x32 | Earlier revision (to 07-24) of the next row; superseded. |
| 1r2sLiRMQPPB0n1X5ynuhid2RC (18 pp) | same document, with the 2026-08-04 erratum | P1, 256x32 | UNCOVERED in the three ledgers (COST_STRUCTURES l.76 dismisses 18097 in one line). Mined below. |
| 8yi7PZqaRnJgDrKicpg7jHOULiY (12 pp) | pscamillo, #314331, "Characterizing a systematic scale bias in Gaussian-closure activation estimation" | P1, 256x32 | UNCOVERED (FORUM_DIGEST row only). Mined below. |
| hPDsTH3hYSKEZIFsoywcJc8bSkB (18 pp) | Keenan Pepper (AE Studio) with Claude Opus 5, #327838, "Sampling-Free Estimation of Deep ReLU Activations: a Learned Cumulant-Transport Propagator and Its Measured Ceiling" | P1, 256x32 | UNCOVERED (FORUM_DIGEST row 28, and as a corpus source in MINING_20261018). Mined below. |

All three uncovered write-ups are Phase 1 at 256x32 under the old (dtype-blind) cost model. None of their numbers transfers directly to our 1024x16 regime.

## 2. Uncovered write-ups: required fields

### 2a. jamesrahenry, #314695 (rev. 2026-08-04)
- **State per layer.** (μ, Σ), propagated by a bivariate Gaussian ReLU closure as a K=10 Hermite series (p.6). Cumulant inputs κ3, κ4 and the pair field E[zc²ᵢ zcⱼ] come from an N=4096 plain-MC probe run once per net. A per-layer linear corrector then adjusts the result: 8 mean + 6 variance + 2 off-diagonal features, 16 coefficients/layer, 512 in total.
- **Cost.** 13.6 % FLOPs of budget (old model), multiplier 0.169. After the 0.10.0 regrade it is 0.300, because the hot path is float64 (7.40e10 vs 3.70e10 FLOPs for an f32 port; p.2). The probe is ~6 % of budget.
- **Raw / util.** Graded raw 5.89e-6, adjusted 9.97e-7 (regraded 1.768e-6). Held out: 7.45e-6 seed-resampled, 8.13e-6 on 56 fresh nets (p.7).
- **Oracles and ablations.**
  - One-step error 1.16e-6 vs full chain 6.0e-5, a factor of 52 (p.5).
  - Per-layer reset to truth: means only 1.64e-6; variances only 1.8e-4 (worse); covariance only 1.0e-4 (worse) (p.5).
  - Step-exact Edgeworth from true cumulants makes the chain worse: 8.8e-5 vs 6.3e-5 (p.5).
  - Perfect probe cumulants: 4.36e-6 vs 6.52e-6.
  - Probe noise share 58 % (46.6 % held out). Field attribution: pair field ~112 %, κ3 47 %, κ4 9%. Denoising κ3 alone is 1.13x worse. Ceiling 0.58x / 0.48x (pp.9-10).
  - A Wiener shrink filter makes the result 1.95x worse. Its bias:variance exchange is ~16:1 against the filter (p.10).
  - Quadratic and linear heads tie (p.7). A rank-32 eigenbasis correction is flat-to-worse, and 15x worse when used in place of T1 (p.8).
  - A ground-truth κ3 carrier reaches cosine 0.83, yet is 4.5x worse than the probe (p.9).
  - Covariance participation ratio contracts from 128 to 5.2 over depth (p.12). A subspace-split sampler/analytic hybrid is capped at ~2 % (p.12).
- **Techniques vs our ledger.**
  - Trajectory-fitted (DAgger) per-layer corrector: SHIPPED as the MIX2 in-chain head. A DAgger refit round was tested and rejected (R2_GO_NOGO l.4044).
  - Pair-field / T1 off-diagonal feature: our chain carries T1/T2 legs (SHIPPED).
  - Mean-only vs covariance-only reset: our oracle family covers it (G-RB85 replacement profile, G-RB86, G-RB117/119).
  - Bias amplification: same phenomenon as G-RB153 VSE1 (quadratic hypersensitivity).
  - Probe-noise decomposition: n/a (we have no MC probe).
  - Nothing new and screenable.

### 2b. pscamillo, #314331
- **State per layer.** k=2 Gaussian closure (μ, Σ), plus ONE scalar multiply of the final mean (0.9921) (pp.2-3, 9).
- **Cost.** Zero FLOPs beyond the k=2 baseline. Adjusted 2.45e-6 at the 0.10 floor (unchanged by the regrade, per Henry's erratum).
- **Raw / util.** Final-layer MSE falls from 8.37e-5 to 2.59e-5. The grader harness gives 2.66e-6 vs 7.52e-6 adjusted.
- **Oracles and ablations.**
  - Per-net optimal factor 0.9916 ± 0.0027; cross-validated 0.9921 ± 0.0001 (pp.2-3).
  - The per-layer factor runs from 1.000 at layer 1 to 0.992, monotone in depth (p.4).
  - The residual is not predictable from non-μ features (1.00x). Its std scales as 0.011·σ(z) (R² 0.94). PCA effective rank is ~29 of 256 (p.5).
  - The organizers' mlp_kprop at k=3 does not beat the scalar: 4.6e-5 vs 3.3e-5, scalar wins 8 of 12, at ~500x the cost (p.6).
  - Exact-moment Edgeworth gives a gain of 0.4-0.5x, i.e. it hurts.
  - A GBM final-layer corrector reads 0.95x, and a shuffled-label control matches it.
  - Corrector predictability decays with depth (τ = 5.1 layers).
  - Error energy is predictable (R² 0.95) while the error direction is not (R² 0.003) (pp.6-8).
- **Techniques vs our ledger.**
  - Final-mean global scalar: MEASURED. R2_GO_NOGO l.215-217 found the per-layer constants flat (1.0000 → 0.99978), "the final scalar alone gives the identical number". The corrector output scale was also scanned (G-RB5/G-RB10, s ≈ 1.17-1.2).
  - Heteroscedastic (1/var) loss weight: measured (l.4025, loss S = U).
  - Nothing new.

### 2c. Keenan Pepper, #327838
- **State per layer.** Pepper's eq. 2, p.4:
  - μ (N);
  - post-ReLU second moment M2 (N×N);
  - the κ3 plane K21(a,b) = κ3[a,a,b] (N×N);
  - a recurrent latent z (N×32);
  - the marginal κ3 (N).
  - The closure is learned and trained end-to-end by backprop through 32 layers on a 499k-MLP corpus.
- **Cost per layer.**
  - The plane transport is 4 plain N³ matmuls per layer (eq. 9, p.15): 0.0154B in total, 13.9 % of C.
  - The µ/M2 recursion costs 0.0080B. The analytic pair term costs ~N² per layer (0.0001B FLOPs).
  - Two rank-16 learned state writes cost ≤ 2.3 % of C each.
  - The attention pair head costs 0.0641B (61 % of C) and is INERT (p.8).
  - Total 0.0944B, C/B 0.1355. A lean rebuild gives 0.0326B, C/B 0.0552 (Table 4).
  - Exact κ3 tensor transport would bill 1.4-3.4B (p.4).
- **Raw / util.** Graded raw 1.50e-5, adjusted 1.95e-6. The lean configuration would score 1.50e-6. Tiers agree within 4 % (p.3).
- **Oracles and ablations.**
  - Teacher-forced true marginal γ3/γ4 recovers 101 % of the gap (2.11e-7) (p.4).
  - Plane R²: 0.499 vs 0.930 for the full tensor (p.4).
  - Conjunction grid (Table 1, p.5): density and fidelity are each worth 1.04-1.07x alone and 3.0x together.
  - Injection rungs (Table 5, p.10):
    - rank-1 M2 residual: 0.51x (hurts);
    - rank-2: 1.54x; rank-16: 2.47x;
    - full true M2: 3.27x;
    - true κ21: 2.98x;
    - true means alone: hurts;
    - means + M2: 22x;
    - closure information ceiling: 46x.
  - Ablation table (Table 3, p.7) is non-monotone. Removing both writes gives 2.297x; removing the M2 write only gives 3.529x.
  - Oracle + noise matched to the RMS of the chain's own error: 28x collapse at step 0 (p.9).
  - At equal arithmetic, QMC wins by 3.9x (1.35x for the lean build). With dead-neuron pricing it wins by 7.9x / 2.5x (p.10).
  - Strassen at every site gives C/B 0.291 vs 0.116 for plain matmul, because of dispatch (p.15).
  - Liveness pruning of the κ3 transport costs +109 % MSE at the mildest threshold (p.16).
- **Techniques vs our ledger.**
  - Dense analytic Edgeworth pair term e21 = g b2 b1 K21/(var σ) (eq. 5, p.5): this is the leading linear-in-κ3 covariance term, which our K=3 chain carries exactly through D21/T1 (SHIPPED). Its gate g is a scale, already covered by the jointly fitted constants (G-RB140, ks).
  - Rank-16 learned M2 write: NEW as a final-MSE-fitted compensator (TOP item 1).
  - End-to-end training through the recursion: covered by MIX2 rollout fitting plus G-RB140 Gauss-Newton.
  - Do not trust teacher-forced R²: consistent with our G-RB132 caveat.
  - Blend with an independent-error sampler (corr −0.02): sampling family KILLED (G-RB45).
  - Metanetwork W→µ: 55x worse; not relevant.

## 3. Credit and contradiction check against PHASE2_WRITEUP_V29.md

No measured number of ours is contradicted. There are two attribution gaps (criterion (i), novelty and credit).

1. **Claims box row 2 and the §3 "principle" (internal cancellation: a one-quantity oracle measures a lever, not a fix) were stated publicly in Phase 1.**
   - Henry, p.5: "fixing the covariance alone breaks the compensation and makes the estimate worse". He also reports that step-exact Edgeworth from true cumulants degrades the chain.
   - Pepper, p.10, Table 5: true means alone hurt, true M2 alone gives 3.3x, and both together give 22x. Pepper, p.9: "partial fixes must be trained through".
   - V29 credits only Nurlanggs (18252) for "channels cancel". V30 should cite jamesrahenry (18097, PDF rev. 2026-08-04) and Keenan Pepper (#327838 PDF) as prior statements. Our contribution is the measured instances at 1024x16 (G-RB86 ×5.6, G-RB73) plus the noise-corrected reading, not the principle itself.
2. **"Teacher-forced R² is not a gate".** Pepper, Wall 3, p.9, published this before our G-RB132 caveat ("A teacher-forced screen cannot see a gain that appears only in free running"). Credit it in one clause.
3. Related-work candidates, not conflicts:
   - Henry's probe-noise decomposition: bias² + across-seed variance, with a /K correction (p.9). It is a cousin of our F0 noise correction, but applied to the estimator's own probe, not to the truth reference.
   - Henry's 16:1 bias:variance asymmetry corroborates G-RB153 VSE1's quadratic hypersensitivity.
   - Pepper's lean-rebuild lesson (61 % of compute was dead) corroborates "ablate the shipped artifact".

**Regime differences (do NOT generalize in V30; these are not contradictions).** All of the following are 256x32 results:
- Pepper: Strassen is a net loss under the wall term at n=256 (p.15). We gain from Winograd at n=1024.
- Pepper: liveness is not sparse at 256x32 (p.16). Our p*=0.05 prune pays at 1024x16.
- pscamillo: k=3 does not beat a scalar-corrected k=2 at L=32 (p.6).
- Henry: mean-only reset recovers 37x at 256x32 (p.5). Our replacement profile at 1024x16 leaves 0.800 through layer 10 and 0.242 through layer 14 (G-RB85).

## 4. Candidates considered and dropped (ledger hits)

| # | Technique (source, page) | Ledger status |
|---|---|---|
| P1 | Final-mean global scalar 0.992 (pscamillo p.2) | MEASURED, flat (R2_GO_NOGO l.215-217 "final scalar alone ... 0.99978"); corrector output scale scanned G-RB5/G-RB10 |
| P2 | Per-layer mean factor profile (pscamillo p.4) | covered by per-layer constants refit (l.215) and the in-chain MIX2 head |
| P3 | Heteroscedastic loss weight (pscamillo p.5) | measured, loss S equal to U (l.4025) |
| H1 | DAgger sequential per-layer refit (Henry p.6) | tested, rejected (l.4044) |
| H2 | Shrinkage/Wiener denoiser (Henry p.10) | n/a (no probe); its mechanism matches VSE1 |
| H3 | Rank-32 eigenbasis covariance correction (Henry p.8) | his own negative; our old-tier bases are a different (exact transport) object |
| K1 | Dense analytic κ3 pair term with gate g (Pepper p.5) | SHIPPED (D21/T1 exact K=3 feed); its scale is in G-RB140 |
| K2 | κ21 plane-only state, all-distinct dropped (Pepper p.4) | we carry more (all-distinct needs ~3n/4 rank, Nurlanggs); KILLED as a family (NEWREP row c) |
| K3 | Sampler blend, orthogonal errors (Pepper p.8) | KILLED G-RB45 |
| K4 | Matched-RMS noise arm (Pepper p.9) | an instrument check, not a lever; optional placebo design for TOP item 1 |

Authors credited: jamesrahenry (James Henry), pscamillo, Keenan Pepper (AE Studio; co-written with Claude Opus 5). Skipped as covered: hyojun_kwon, Cipo / Team Puffi, baghyeonsig.
