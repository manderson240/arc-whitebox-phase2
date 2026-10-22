# What noise-corrected oracles show about a cumulant-propagation estimator: the standard noise-ceiling correction, applied to oracle injection



**ARC White-Box Estimation Challenge 2026, Phase 2. Algorithmic-contribution write-up.**
Participant: michael_anderson7 (individual).

**Corresponding submission: v117_kd, AIcrowd #337578, graded 4.00e-9, 0 failed; nominations in B.4.**

---

## Abstract

**When the truth is Monte-Carlo sampled, an oracle reading is biased, and we measured by how much.** In our cumulant-propagation estimator of the per-neuron output mean of random 1024 × 16 ReLU MLPs, an exact per-neuron σ² reads 0.776 of baseline MSE uncorrected, 0.511 corrected (90 % CI 0.44–0.58; layers 11–15 only 0.635, head frozen); a control that must read ≈ 0 up to the Hermite-truncation floor reads 0.305 uncorrected and 0.002 corrected. **The noise correction used is not new.** It is the noise-ceiling subtraction of computational neuroscience (Sahani & Linden 2003; Pospisil & Bair 2021), equivalently a two-point Richardson extrapolation in 1/N of a nested Monte-Carlo reading (Rainforth et al. 2018), and other participants measured or corrected Monte-Carlo noise in their own oracles and references (Nurlanggs, Artyom_Mazur, kai_leal_gonzalez, hyojun_kwon; Appendix I.1). What is ours, stated narrowly and not as a first: a known-answer control (0.305 → 0.002, §3; scalar toy, Appendix G), a 5× dose check, and the measured size of the misreading (0.776 vs 0.511); the corrector-in-place judging rule (§4); the measured truncation ceiling (§5); and the engineering results (the wall knapsack, §7A, and shared transported bases, §7B). Oracle injection (replacing one internal quantity by sampled ground truth) is a common diagnostic for such estimators (Nurlanggs, forum 18252; Susupro, forum 18254). The noise SE is ≈ 0.9 of the chain's own error at z8 and ≈ 0.33 of it at z15, so an uncorrected oracle understates the lever it measures, by an amount that depends on the estimator's accuracy as well as on the sample count. **A second trap:** in a chain whose errors cancel internally, a one-quantity oracle measures a lever size, not a fix (§3). **Consequence:** removing every truncation knob in our chain at unlimited cost reaches only 0.815 of raw MSE (0.807 with the head refit): a KILL for those knobs, not a bound on the family. **Engineering:** two shared transported old-tier bases in place of nine per-source bases took graded adjusted 4.21e-9 → 4.01e-9 (v112_sb, AIcrowd #337384, 0 failed; §7B). Two constants on top of it give our corresponding submission, v117_kd #337578 (4.00e-9, 0 failed; §7B, B.4). Bars were pre-registered, with the exceptions listed in the ledger-exceptions paragraph (§8, "Exceptions"); the gate behind v112 is one of them (its bar was derived after the preceding gate's data were seen, §7B).

> **Terms.** **G-RBnn:** a pre-registered gate in `research/R2_GO_NOGO.md` (records in `research/rebuild/gates.jsonl`). **Head:** our learned mean-drift corrector, added to the carried mean. **Twin:** the f64 research copy of a shipped build, scored on FIT nets against ~1e9-sample truth. **Seat:** the drop in final MSE when one quantity is replaced by truth; a lever size, not an error share. **pt:** 0.01 of (metered FLOPs / 2^41), one util point; a dense 1024³ product is 2^31 FLOPs, so 1 util = 1024 products.

## Summary

> **The three prize criteria, one line each.**
> (i) **Novelty, narrow:** the noise correction is standard and others handled oracle or truth noise (§1.2); ours is a known-answer control, a 5× dose check and the measured size of the misreading (0.776 vs 0.511), plus two procedural results (§4, §5).<br>
> (ii) **Clarity and accuracy:** each claim carries a tag ([proved], [measured], [argument], [A, unreplicated]) and names its gate or file where one exists; bars were pre-registered except the exceptions in §8; proofs carry falsifiers (Appendix P); Appendix E gives the reproduction commands.<br>
> (iii) **Checkable impact:** graded v58_ne 4.98e-9 → v117_kd 4.00e-9 (−19.7 %), from constant screens, exact-cost work and shared transported bases (table below); the only graded step from an algorithmic idea is the §6 closure (−2.3 %, with a corrector refit); the three diagnostics changed what was not built.

**Graded impact** (condensed from Appendix B.0; AIcrowd graded adjusted scores).

| what | graded step | effect |
|---|---|---|
| κ4 response closure (§6) | v49 #334744 5.59e-9 → v51 #334768 5.46e-9 | −2.3 %, closure plus a corrector refit; closure-only evidence is ungraded: VALID-20 OFF/ON 1.0327 raw, 17/20 nets worse |
| constant screens, one prune change, exact-cost work, wall-budgeted levels (B.0 items 5–7) | v77_fuse #335642 4.92e-9 → v110 #337268 4.21e-9 | −10.4 % through v95 #336648 4.41e-9 (constant screens and the prune); the rest exact-cost and wall work, step by step in B.0 |
| shared transported old-tier bases (§7B) | v110 #337268 4.21e-9 → v112_sb #337384 4.01e-9 | −4.8 %, 0 failed; v117_kd #337578 (two constants on top) 4.00e-9, below the meter's resolution |
| noise-corrected oracle, corrector-in-place rule, truncation ceiling (§3–5) | none | no graded impact; the rule stopped two shipments (the dense closure and the κ4 predictor) |
| head-to-head against the organizers' simple factorized K = 3 (claim 9) | not graded | 0.533× its final-layer MSE (95 % CI 0.49–0.59), lower on 8/8 nets, at 388 vs 3040 n³ FLOPs |

**Corresponding submission:** v117_kd, AIcrowd #337578. It graded 4.00e-9 adjusted: final-layer MSE × util, util 0.187 (raw 2.13e-8; grader feed, `writeup/proofs/p2_rows_20261021T2034Z.json`), 0 failed MLPs. It is v112_sb #337384 (4.01e-9) with two constants changed.

**What this is.** A cumulant-propagation estimator (K = 3 plus a κ4 closure). Our contribution is not mainly the estimator. It is **a measured account of where its error lives and why it sits where it does.** Each claim below names the artifact it rests on. From the release root, claim 1, the Appendix P checks and the FIT12 readings of claim 2 each reproduce with one command (below). Claim 2's 3-net knob meter and the K = 2 comparison rest on shipped outputs (`writeup/proofs/meter*.out`, `k2_perlayer_1340.out`), whose input nets are not in the release. Claim 3's numbers are ledger records (`research/R2_GO_NOGO.md`); their raw rows are not in the release.

### Three results ARC can reuse on any estimator

**1. Sampled-truth oracles are biased, and the standard fix makes them usable** (§3, proof P1).

- Injecting a Monte-Carlo estimate of a quantity is a sampled-truth oracle. It overstates the remaining error by tr(HΣ)/(2N) + O(N⁻²), a bias linear in 1/N at leading order (for smooth readings; ours are piecewise smooth, and the 1/N law is checked by a dose test, Appendix P1).
- Two-half Richardson extrapolation removes it. This is the noise-ceiling correction of computational neuroscience; Sahani & Linden 2003 and Rainforth et al. 2018 (Thm 3, its bounded-second-derivative case) are credited. Other participants measured or corrected Monte-Carlo noise in their own oracles and references (Nurlanggs, Artyom_Mazur, kai_leal_gonzalez, hyojun_kwon; Appendix I.1). Ours, narrowly: a known-answer control, a 5× dose check and the measured size of the misreading (0.776 vs 0.511).
- Known-answer control: 0.305 uncorrected → 0.002 corrected.
- Corrected, an exact per-neuron σ² takes raw MSE to 0.51× (90 % CI 0.44-0.58; v95 twin, 6 nets, head frozen), against 0.78× uncorrected: the uncorrected oracle understated the lever. Layers 11-15 alone give 0.635× [0.589, 0.680]. These are lever sizes, not forecasts.
- From the release root (https://github.com/manderson240/arc-whitebox-phase2): `python3 research/rb119/ci119.py` (rows `var`, `varL1115`, `var_k3_k4_h0`; it rewrites `research/rb119/ci119.json` in place, byte-identically) and `python3 writeup/proofs/check_p1_p2.py`.

![Figure 1 — oracle noise bias](figs/F0_oracle_noise_bias.png)

**Figure 1.** Monte-Carlo noise in a sampled-truth oracle inflates the MSE ratio it reads; split-half extrapolation to zero noise (r∞ = 2·full − mean(A, B)) removes it; this is the same subtraction as the neuroscience noise-ceiling correction (Pospisil & Bair 2021, eqs. 10–11). (a) Pooled raw-MSE ratio vs noise level (1 = full mean, 2 = one half, 5 = ±2 dose; the dose exists for σ² only) for the all-layer σ² oracle (0.776 → 0.511, 90 % CI 0.438–0.581) and the known-answer control, which must read ≈ 0 up to the Hermite-truncation floor and reads 0.305 raw but 0.002 (−0.043–0.046) extrapolated. **The control has only two noise points, so its extrapolation is a two-point line with no dose check.** (b) Uncorrected vs corrected for σ² all layers, σ² layers 11–15 (0.710 → 0.635 [0.589, 0.680]) and the control; CIs are a between-net bootstrap over six nets (tails understated). Source: `research/rb119/ci119.json`, recomputed by `figs/make_f0_oracle_bias.py`. Gate: G-RB119.

**2. The final layer is quadratically hypersensitive to coherent σ² error, so cost-neutral constant tuning has reached the resolution of our instruments** (§7C Final-layer hypersensitivity).

- Scaling σ²_z at layers 11-15 by (1 ± 10⁻³) multiplies raw MSE by about 4, and ±4·10⁻³ by about 50 (FIT12, 12 nets, head frozen): a quadratic (quadratic coefficient 3.1·10⁶ per unit c²; it predicts the ±4·10⁻³ points to within 1 %) whose fitted optimum is at c ≈ −2·10⁻⁵, worth about 0.14 %. Points nearer zero were registered but not run.
- We scanned 7 cost-neutral knobs at 28 settings: corrector strength, deep-layer corrector factor, the LITE scale, a coherent σ² scale, old-tier damping α, a rank-1 covariance compensator, and σ² calibration channels. We also scanned 4 cost-changing knobs (prune threshold, Price–Mehler pair-series order `_KH`, feedback-leg rank, oversampling) at 8 settings, plus 2 two-knob combinations. No setting improved the shipped chain by more than 0.3 % adjusted (v112's chain, v117_kd's parent, for the FIT12 knobs), and for every knob the shipped value is the best tested setting or within 0.3 % of it; the fitted optima of the three scalar knobs (σ² scale, α, CMP) lie within 0.21 % of the shipped chain. Most off-optimum settings are much worse (old-tier α = 0.9: ×1.25). Instruments: FIT12 twin, or a 3-net meter whose nets were also used for selection. A dense-M closure mode with Λ refit reads 0.9985 raw but costs about 4 % util (hand estimate; not metered).
- Old-tier damping: no tested α beats α = 1 (α = 0.9: ×1.25; α = 1.2: ×1.75; FIT12). A quadratic through those points puts the optimum within 0.01 of α = 1.
- We read this as: the coherent part of the σ² error is already at its optimum, so what σ² error remains is incoherent per-neuron error, which a better covariance closure, not better constants, would have to remove [inference]. Exact σ² would leave 0.51× of raw, so σ² is not the only remaining error. Artyom_Mazur reports an analogous parabola for a coherent scale of all layers' variances (p.18: c = 1e-3 costs ×200) and a similar reading; his Proposition 1 (forum 18249, p.19) makes a neuron's next-layer variance error a coherent level from tr ΔC plus noise independent across neurons, and a model of the neuron's own state cannot see that noise (p.20); abhimanyu_singh (forum 18264, prose; n = 256) measures a quadratic law for iid noise on the D21 and D3 slice read-outs (added MSE ≈ 0.91σ² and 0.60σ²) and finds that bias propagates while zero-mean noise attenuates. A consistency note on the leader's raw MSE is in Appendix F.7.
- From the release root: `python3 research/rb153/tab153.py research/rb153/res_vse1_fit12.jsonl` (σ² scale) and `python3 research/rb153/tab153.py research/rb153/res_s1_fit12.jsonl research/rb155/res_fit12.jsonl` (α, σ² channels, CMP, MEX/MEXR); the 3-net knob meter outputs are `writeup/proofs/meter117.out`, `meter119.out` and `meter121.out`–`meter123.out` (net-0 probe meter: `meter116.out`).

**3. Partial fixes break internal cancellation; judge upstream changes with the learned corrector in place** (§2-4).

- The σ² error is a joint closure error. Correcting only its μμᵀ part makes raw ×5.6 worse.
- A per-neuron κ4 predictor that passes its bar reads 0.874 alone but 1.100 with the shipped corrector.
- The principle was stated publicly earlier: in Phase 1 by James Henry (topic 18097, #314695, rev. 2026-08-04, p.5) and Keenan Pepper (#327838, Table 5 p.10, and p.9: 'partial fixes must be trained through'), and in Phase 2 by Nurlanggs (forum 18252) and Artyom_Mazur (forum 18249, item 4, p.2: exact variance alone can make the result worse (×1.09, one net), while exact variance, κ3 and κ4 together gave ×0.12). We credit them. Ours are the measured n = 1024, depth-16 instances.
- From the release root (ledger records; raw rows not shipped): `grep -n "G-RB86 KILL\|G-RB76 KILL\|1.10 with the SHIPPED head" research/R2_GO_NOGO.md`.

### Supporting results

- **Head-to-head against the organizers' code:** claim 9 and B.0 item 8b (row 5 of the table above).
- **Why κ3 is necessary:** a K = 2 chain from first principles is 167× worse than our shipped chain on the same net (Appendix F.7).
- **Proofs with falsifiers:** P1–P4 (Appendix P).
- In full: Appendix F.12.

**What did not work, and what we would try next:** Appendix F.8, with other negatives in F.0.

*LLM-use disclosure: see §10.*

### Claims box

| # | claim | evidence |
|---|---|---|
| 1 | Sampled-truth oracles are biased by Monte-Carlo noise. An exact per-neuron σ² at every layer reads 0.776 uncorrected and ≈ 0.511 corrected (90 % CI 0.44–0.58; layers 11–15 only 0.635× [0.589, 0.680]; v95 twin, 6 nets): a lever size (the gain if σ² were exact, head frozen), not a forecast. Known-answer control 0.305 uncorrected, 0.002 corrected (vs the head-ON twin). The correction is standard and others handled oracle or truth noise (Appendix I.1); ours, narrowly: its known-answer control, a 5× dose check and the measured size of the misreading. | [measured] G-RB117, G-RB119, G-RB120 |
| 2 | A one-quantity oracle in an internally cancelling chain measures a lever size, not a fix (μμᵀ-only σ² fix ×5.6 worse; κ4 gain is an unpredictable cross term). The principle was stated publicly earlier (Henry, Pepper, Nurlanggs; in Phase 2 also Artyom_Mazur, forum 18249, item 4 p.2: exact variance alone up to ×1.09, with κ3 and κ4 ×0.12; §3); ours are the measured n = 1024, depth-16 instances. | [measured] G-RB86, G-RB73; credits §3 |
| 3 | The untruncated chain reads 0.815 (head frozen), 0.807 (head refit; 0.810 FIT12 held out) against a bar of 0.60: KILL for those knobs, not a family bound; constants re-tuned on it are untested. | [measured] G-RB117, G-RB120 |
| 4 | With the head in place, 4 independent accuracy gains (5 gate rows, two chains) were cut to ≤ 3 % after a head refit, and 3 of them reversed with the head frozen (one row has no frozen reading); 0 of 2 cost gates were absorbed. | [measured] 7 gates; cost side n = 2 |
| 5 | A free-transport κ4 response closure cost +0.04 pt; the graded step that includes it was −2.3 % (#334744 5.59e-9 → #334768 5.46e-9), which is the closure plus a corrector refit together. Closure-only evidence: the v58_ne OFF/ON ablation, 1.0327 raw, 17/20 nets worse. | [measured], held out |
| 6 | Exact carried mean through layer 10 still leaves 0.800 of final raw MSE; read as a lever share under non-additivity, not an error share, that is layers 11–15 (75–79 % by the diagonal adjoint, which recovers 0.86–0.90 on two nets). | [A, unreplicated] adjoint; [measured] G-RB85 |
| 7 | Our κ3 birth's exact read costs 4 products per young source-layer; the cheaper re-association reads 6–10 % wrong; a 3-product floor rests on an unmeasured premise. | T1 [proved, n ≤ 96]; [measured, n = 1024]; T2 [argument] |
| 8 | Two shared transported old-tier bases (Gram-solve admission) replace nine per-source bases: raw ×1.0145 on 40 held-out nets, metered −1.23 pt, graded 4.21e-9 → 4.01e-9. Two constants on top (v117_kd, the corresponding submission) graded 4.00e-9, a difference below the meter's resolution (§7B). | [measured] G-RB144 (held out); G-RB143 KILL on cost; G-RB157 addendum |
| 9 | Against one configuration of the organizers' reference code, simple factorized K = 3 (MIT-licensed, run unmodified, f32, no fitted constants; their augmented variant did not fit in memory at n = 1024, so it is not compared), the corresponding submission's chain (v117_kd, which includes our learned corrector, fitted on 60 FIT nets) has 0.53× the final-layer MSE (0.533, 95 % CI 0.49–0.59, lower on 8/8 of nets 1300–1307; its parent v112_sb: 0.532) at about an eighth of its matmul cost (388 vs 3040 n³ FLOPs, the latter 1.48× the 2048 n³ budget, so the reference is compared at a cost no Phase 2 entry may spend; ours counted with every op, theirs matmul-only; their App. J polynomial gives 8304 n³ in the paper's own FLOP accounting, which the op counter did not reproduce). Nets 1300–1307 were never used for fitting; they were part of the 40-net held-out bar that admitted v112 (G-RB144), and the same 40 nets were the pass/fail bar of G-RB130, G-RB140 and G-RB151 (all KILL), so they have been read four times. | [measured] G-RB149 and its CORRECTION 2 in the ledger; `research/rb149/compare_heldout_table_v117_kd.md`; `research/rb149/ORACLE_COMPARISON.md` (its "1/4", "1520 MAC units" and "never in any fit/selection" lines are superseded by CORRECTION 2) |

> **Method box, a recipe for running a bias-corrected sampled-truth oracle, and the oracle/ceiling ladder (Figure 4):** Appendix H.

---

## 1. Problem, definitions, and what is not ours

### 1.1 Problem, notation and definitions

Predict E_x[h] per neuron for a fixed MLP of width n = 1024 and 16 layers, W_l i.i.d. N(0, 2/n), no bias, x ~ N(0, I). Score = mean over graded MLPs of the final-layer MSE × max(0.1, C/B), C the metered FLOPs, B = 2^41 (util = C/B; one util point, "pt", is 0.01). Pure Python plus `flopscope`; un-metered Python time is capped at 0.4 s per MLP; the worker has 8192 MB.

- **Layer index (one convention throughout).** Layers are 0-based: z_0 = xW_0, h_l = ReLU(z_l), z_l = h_{l−1}W_l for l = 1…15. The scored output is h_15; "the final read" is z_15 → h_15. A κ3 *source* is born after z-layer s ∈ {0…14}, first transported at s+1 and read at every later layer; its *age* at layer l is l − s. Over layers 1–14 there are Σ_{l=1}^{14} l = 105 (source, layer) pairs; exactly 60 have age ≤ 5 (*young*: 1 + 2 + 3 + 4 + 5 + 9 × 5); at layer 15 all 15 sources are read, diagonal only (Appendix P4, Conditions).
- μ, Σ: mean and covariance of z (σ² its diagonal). T, Q, K31: the (2,1), (2,2), (3,1) cumulant slices. **f₁ = Φ(μ/σ), f₂ = φ(μ/σ)/σ** are Price coefficients (derivatives of E[ReLU] in the mean and the covariance), not orthonormal Hermite coefficients.
- **Head** (MIX2, Appendix F.3): *frozen* (shipped weights), *refit* (retrained on the changed chain) or *off*.
- **SSC:** Puffi's name for the response closure; our free-transport build (`_SSC_CLOSURE`, v51_sscf) is §6. **al07:** the two-term (3,1) κ4 closure term κ3_i T_iij / v_i (credit kai_leal_gonzalez).
- **Per-source cost floor:** the fewest dense n×n×n products that form one young source-layer's (2,1) read.
- **Instrument definitions.**
  1. *Nets.* The official public Mini split (`hf://aicrowd/arc-whestbench-public-2026@v2-phase2`): 100 nets, W_l i.i.d. N(0, 2/n), width 1024, depth 16. FIT 60 / VALID 20 / TEST 20 by `default_rng(2026092901)` on mlp_id (`lc/split.json`); oracle gates use FIT nets 0, 2, 4, 5, 6, 7 (these six are among the 60 FIT nets the MIX2 head was fitted on; arm and baseline share that frozen head, so ratios compare like with like); FIT12 = 12 FIT nets. *Mini-10* = 10 official nets through the grader's subprocess runner.
  2. *Truth.* Official ~1e9-sample references; oracles use z-moments from two independent 2^22-sample MC halves (seeds 7001+net, 8001+net).
  3. *Oracle injection.* At every z-layer 1–15 (or 11–15 where stated), one per-neuron quantity of the pre-ReLU z marginal (σ² = diag Σ_z, κ3 or κ4 diagonal) is replaced by MC truth. The chain runs free, not teacher-forced: its carried mean, off-diagonal slices and all other quantities stay as shipped.
  4. *Pooled ratio* = Σ_nets MSE_cand / Σ_nets MSE_base, final-layer MSE against truth; the base is the twin as shipped (head ON) unless a row names another. Ratios are pooled unless marked "per net".
  5. *Roles.* *Port*: the real `predict()`. *VALID-20*: never gradient-fit, but chose head checkpoints and constants. *Graded*: the only held-out instrument.
- **Tags.** [proved]: a passing machine check plus a perturbed variant that must fail; [measured]: a gate measurement; [derived]: no machine check; [argument]: reasoned; [A, unreplicated]: agent-reported, not re-run; [H]: hypothesis.

### 1.2 What is new, and what is not ours

**The correction is not ours.** The split-half extrapolation r∞ = 2·r(full) − mean(r(A), r(B)) is the standard noise-ceiling correction for a squared-error reading against a noisy reference (Sahani & Linden 2003; Schoppe et al. 2016; Cadena et al. 2019; Pospisil & Bair 2021) and the standard bias removal for a nested Monte-Carlo reading (Rainforth et al. 2018; Giles 2015; Blanchet, Glynn & Pei 2019); for a quadratic reading the 1/N law is exact (Appendix I). **Ours, narrowly and not as a first:** a known-answer control, a 5× dose check and the measured size of the misreading (0.776 vs 0.511; §3). Others handled Monte-Carlo noise in their own oracles and references (Nurlanggs, Artyom_Mazur, kai_leal_gonzalez, hyojun_kwon; James Henry in Phase 1); Appendix I.1 says what each did, with pages. Also ours, as a procedural lesson rather than a method (we searched only the organizers' paper and code and the forum prose and PDFs cited in Appendix I.1): judging each upstream change with the learned corrector in place (§4), the measured truncation ceiling (§5), and the engineering results (the wall knapsack, §7A; shared transported bases, §7B). The known-answer control is standard practice, applied here. **Not new:** correcting oracle or truth noise as such, oracle injection itself, cancellation between channels and ranking terms by scored output (Nurlanggs and Susupro, below); the K = 3 representation, response closure and corrector idea, Strassen–Winograd and the cost structures credited below.

Every other credit (ARC, Team Puffi, Team 504aldo, Nurlanggs, Susupro, Artyom_Mazur, kai_leal_gonzalez, hyojun_kwon, James Henry, abhimanyu_singh, other participants, textbooks) is itemised in Appendix I.1, moved there in V30 for length; nothing was removed from it.

### 1.3 Source statement

Every submission from v21_rb on was written from public prose, the ARC paper and our own prototypes. 504aldo's MIT-licensed code was cloned into the same workspace, but the rebuild agent's ledger records that it was not opened; the rebuild is prose-derived, not clean-room. Full statement and timeline: Appendix D.4.

---

## 2. Finding 1: an exact carried mean through layer 10 still leaves 0.800 of final raw MSE (a lever share under non-additivity, not an error share)

A mean error d_l reaches the output through T_l = Π_{k>l} diag(Φ_k) W_kᵀ (Φ from a K = 2 chain).

**Diagonal adjoint attribution [A, unreplicated; `research/review/LENS_B_math.md` §1].** Each layer's local residual fresh_l = d_l − Φ_l∘(W_lᵀ d_{l−1}) is weighted by gain_l, the mean squared column norm of T_l: 1 at l = 15, 0.435 at l = 9, 0.047 at l = 1. It is diagonal: it recovers 2.57e-8 of 2.58e-8 on net 0 but 0.86 and 0.90 of the final MSE on nets 2 and 4 (the rest is cross terms, §3). Shares: l15 20–27 %; **the last five 75–79 %**; layers ≤ 2 ≤ 0.2 % (uncorrected f64 chain, no closure, K = 2 gates, FIT 0/2/4, age 5; Figure 3, Appendix F.9).

**Replacement depth profile [measured; G-RB85 row 10a].** A second estimator with a different failure mode: on the v59_p05 twin, head on, the carried mean is replaced by 1e9-sample truth (noise-free) through h-layer k. Pooled final raw reads 0.99 / 0.975 / 0.966 / 0.933 / 0.800 / 0.609 / 0.440 / 0.242 at k = 2 / 4 / 6 / 8 / 10 / 12 / 13 / 14: the final read alone leaves 24 %, and an exact carried mean through layer 10 still leaves 0.800, which an additive reading would assign to layers 11–15 (≈ 80 %, a lever share under non-additivity, not an error share). §3 shows errors cancel internally, so read these as lever shares, not additive origins.

**What transfers.** Two estimators, two chains: both put most of the lever at layers ≥ 11, though the replacement above swaps only the carried mean. Appendix F.0 does not show that early layers do not matter: exact early-layer snaps (a noisy 2^21-sample oracle) made the chain +79 % worse, and skipping the layer-1 birth gave raw ×10.2 (Appendix F.0). The exact-σ² injection of §3 places about a quarter of the seat at layers 1–10 (0.635 for layers 11–15 against 0.511 for all layers).

---

## 3. Finding 2: sampled-truth oracles are biased, and a one-quantity oracle measures a lever size, not a fix

**Provenance first.** The noise correction in this section is a known method, not a new one: the noise-ceiling subtraction of computational neuroscience (Sahani & Linden 2003; Pospisil & Bair 2021), equivalently Richardson extrapolation of a nested Monte-Carlo reading (Rainforth et al. 2018; Giles 2015). What this section adds, narrowly and not as a first, is a known-answer control, a 5× dose check and the measured size of the misreading (0.776 vs 0.511); others' handling of oracle and truth noise is credited in Appendix I.1, and Appendix I has the sources.

The mean recursion μ_{l+1} = W_{l+1}ᵀ E[h_l] is exact and linear, and E[h_l,j] depends only on neuron j's 1-D marginal of z, so all error enters through per-neuron marginals. The chain summarises each marginal by (μ, σ², κ3, κ4) and reads E[ReLU] through a truncated Hermite series (order 8 in the twin; the closed-form Hermite coefficients of ReLU^p are ARC's Prop. S.3.8).

**The two oracle tables on one basis.** Head ON, frozen, noise-corrected; brackets are 90 % bootstrap CIs over the six nets.

| exact at every z-layer 1–15 | v59_p05 twin, FIT 0/2/4, two-half M0 (G-RB85) | v95 twin, 6 FIT nets, split-half extrapolated (G-RB119) |
|---|---|---|
| per-neuron σ² | 0.57 (dose-law range 0.57–0.62) | **0.511** [0.438, 0.581] |
| κ3 diagonal | 0.79 | – |
| κ4 diagonal | 0.78 | 0.852 [0.793, 0.916] |
| κ3 + κ4 | 0.57 | – |
| σ² + κ3 | 0.33 | 0.253 [0.182, 0.320] |
| σ² + κ3 + κ4 | 0.32 (noise-flagged; λ-parabola 0.31) | 0.209 [0.122, 0.311] |
| σ² at z-layers 11–15 only | – | 0.635 [0.589, 0.680] |

*Noise correction.* Each oracle uses two independent 2^22-sample halves; their mean's SE is ≈ 5e-4 relative on σ² (noise SE over chain error ≈ 0.9 at z8 and ≈ 0.33 at z15), against the chain's own σ² error of 5.6e-4 at z8 and 1.5e-3 at z15. The uncorrected averaged-halves ratios (σ² 0.776, σ² + κ3 0.545, all three 0.512, κ4 0.868) were therefore upper bounds, off by 0.27–0.30 for the σ² arms, so we extrapolate r∞. Checks: (i) a 5× noise dose matched the linear prediction (σ² 1.840 and 1.839 against 1.841; the reading is a nonlinear, piecewise-smooth function of the sampled mean; its bias is linear in 1/N at leading order (Appendix P1), which the dose check confirms at our N; cf. Rainforth et al. 2018, Thm 3, its bounded-second-derivative case, with the bias step in its App. D proof); (ii) **known-answer control**: σ², κ3 and κ4 are exact at every layer and the head is off; μ is not stated to be exact. It tests that the sampled-truth pipeline plus extrapolation returns ≈ 0 when those three are exact, not μ or quantities beyond κ4. E[h] depends only on the marginals as far as the truncated Hermite read represents them, so the ratio (against the head-ON twin, the ledger's base for head-off arms) must be ≈ 0 up to that truncation floor (raising the pair-series (Hermite) order `_KH` 8 → 12 or 16 changes nothing, 1.0000, §5). It reads 0.002 [−0.043, 0.046] extrapolated and 0.305 uncorrected: the control passes only after correction, and what the truncation and the κ≥5 terms contribute is indistinguishable from zero at ±0.045 of baseline MSE. The control has only two noise points, so no dose check. Limits: MC noise only; CIs are between-net spread over six nets (tails understated); the six oracle nets are among the 60 FIT nets the MIX2 head was fitted on (arm and baseline share the frozen head; the caveat is not sized).

*Relation to published oracle tables:* Appendix I.2 (moved in V30 for length).

**The noise-corrected σ² seat.** An exact per-neuron σ² at every layer takes raw to ≈ 0.51× (90 % CI 0.44–0.58); at layers 11–15 only, 0.635× [0.589, 0.680], about 75 % of the all-layer gain. This is a lever size, the gain if σ² were exact with the head frozen, not a forecast of what a construction would deliver (§5: our constructions stop at ≈ 0.81×). Head on, the σ² and κ4 CIs do not overlap, so σ² is the larger single seat. **Head off, the order is not established:** σ² 0.664 [0.596, 0.731] against κ4 0.713 [0.691, 0.733] overlap (ratios against the head-ON base). **Withdrawn:** the §5 gate's rule "exact σ² > 0.62 ⇒ no σ²-only construction reaches 0.60" fired on the uncorrected oracle (0.776) but would not on the corrected one; its KILL rests on constructive arms that do not use the oracle (§5). No σ² build followed: a construction recovers only part of an oracle, and our one pair-step construction (second-order κ3×κ3) read 1.042.

**The principle, with its two measured instances.** The principle was stated publicly earlier: in Phase 1 by James Henry (topic 18097, #314695, rev. 2026-08-04, p.5) and Keenan Pepper (#327838, Table 5 p.10, and p.9: 'partial fixes must be trained through'), and in Phase 2 by Nurlanggs (forum 18252) and Artyom_Mazur (forum 18249, item 4, p.2: exact variance alone can make the result worse (×1.09, one net), while exact variance, κ3 and κ4 together gave ×0.12). We credit them. Ours are the measured n = 1024, depth-16 instances.

- **σ².** σ² = wᵀ(E[hhᵀ] − μμᵀ)w. Its μμᵀ part and its second-moment part each carry about 3× the total σ² error, and they are anti-correlated. Correcting only the μμᵀ part makes the final raw **×5.6 worse**. The σ² error is a joint closure error that cancels internally.
- **κ4 (§4, row 4).** A per-neuron κ4 predictor on 43 O(n²) features passes its pooled bar (debiased R² 0.644 vs 0.418 for the shipped κ4). It reads 0.874 uncorrected but **1.100 with the shipped head**. The mechanism, measured at layer 15: the oracle's gain is a cross term between the inherited mean error and the part of κ4 *not* predictable from chain state (corr −0.26 / −0.24). The head already holds the predictable part, so adding a state predictor double-corrects.


**What transfers.** An oracle for one quantity reads the error it would remove *if every other error stayed put*. When errors cancel internally, a partial correction breaks the cancellation, so a seat is the size of a lever, never a forecast of a fix. Before building a carrier for X, inject a *partial* or *predicted* X and read it with the head in place.

---

## 4. Finding 3: judge upstream changes with the learned corrector in place; it cut 4 of 4 accuracy gains to ≤ 3 % and reversed 3 of them with the head frozen

The head is load-bearing (−20.2 % raw on VALID-20, 20/20 nets [A, Lens D]; negated, 1.75–1.90× worse) and unexplained, though §3 shows it holds the state-predictable part of κ4. Seven gate rows judged an upstream change with it in place (rows 4 and 5 share one predictor; rows 1–3 ran on the pre-closure lean pair, rows 4–7 on later chains):

| # | gate | change | without the head | head frozen | head refit |
|---|---|---|---|---|---|
| 1 | G-RB13 | common g rescale | −13 % (FIT) | +7.7 % worse | −2.6 % VALID (v42_g92) |
| 2 | G-RB33 | dense response closure | 0.763 (FIT) | +18 % worse | raw 0.9715 at +3.57 pt (adjusted 1.113) |
| 3 | G-RB54b | κ4 closure at layers ≥ 13 | 0.918 (FIT) | – | VALID adjusted 1.047 |
| 4 | G-RB73 | learned κ4 predictor (§3) | 0.874 (FIT) | 1.100 | see row 5 |
| 5 | G-RB76 | head refit on the predictor chain | 0.874 (FIT) | – | VALID raw 1.0050 |
| 6 | G-RB59 | fire-rate prune p* = 0.17 (cost) | +56 % | +75 % | – |
| 7 | G-RB61 | prune p* = 0.05; old tier 224 → 160 (cost) | 1.0369; 1.0616 | – | 1.0392; 1.0622 |

*Reading the table.* Cells mix net sets (FIT or VALID, as labelled; unlabelled cells follow the ledger gate) and value types (raw or adjusted, as labelled). Rows are not directly comparable; read each against its own baseline.

**What the table supports, and what it does not.**

- **Accuracy gains (rows 1–5: 4 independent gains).** With the head frozen, rows 1, 2 and 4 reversed; row 3 has no frozen-head reading (only a refit, 1.047 adjusted). After a refit, rows 1–2 kept at most 2.6–2.9 %, rows 3 and 5 nothing.
- **Cost losses (rows 6–7, n = 2).** The head absorbed none: row 7's refit was unchanged or slightly larger, and in row 6 it *amplified* the loss (+56 % → +75 %, predicted +2–6 %).

**The rule is procedural.** Judge every upstream change, accuracy or cost, with the learned head in place, and pre-register the head arm's bar; an uncorrected ratio is an upper bound on the pair's gain, never a forecast. The gain/loss asymmetry rests on 4 independent gains (5 gate rows) and 2 cost gates: an observation, not a law.

---

## 5. Finding 4: the truncation ceiling we measured

**The experiment (pre-registered).** On the v95 twin (f64, 12 FIT nets) we gave every truncation knob its best case at any cost, with the MIX2 head and v95 constants **frozen** in every arm (`w117.py`). Pooled ratios against the twin (mean raw 2.1648e-8):

| arm | ratio |
|---|---|
| second-order κ3×κ3 Gram–Charlier in the pair step | 1.042 (2/12 improve) |
| Price–Mehler pair-series order `_KH` 12 or 16 (the twin runs 8; the shipped v112 port runs 4, v117_kd 3) | 1.0000 |
| exact SVD; no pruning; no ageing | 0.995; 0.964; 0.975 |
| untruncated (no ageing, no pruning, exact SVD) at rank 16 / 64 / 256 | 0.897 / 0.852 / 0.825 |
| **untruncated at rank 1024: no truncation anywhere** | **0.815** (per net 0.69–0.93) |

**Verdict, worded to what was tested.** Against a bar of 0.60, the truncation knobs we tried, at infinite cost with the head and constants frozen, bottom out at **0.815**: **KILL for those knobs, not a bound on the chain family**. A refit can move a reading by about 10 points (§4), so a second gate refit the head on the untruncated chain (same recipe; twin control bit-identical): FIT12 **0.8151 frozen → 0.8071 refit** (in-sample) **→ 0.8100** with FIT12 held out of the head fit. The refit is worth under one point, an order of magnitude below §4's movement, so the 0.815 belongs to the chain as built, not to the frozen head. Untested axis: constants re-tuned on the untruncated chain. An exact σ² at every layer would reach 0.511 (layers 11–15 only 0.635) and a carried κ4 core is limited by its seat (0.852), but none of our constructions gets below 0.807. Whether a different estimator closes that gap is open [H]. The organizers' remark on the asymptotic Hermite series, and two published candidates we have not tested, are in Appendix I.2.

**What transfers.** Before chasing a cost structure, measure the uncosted ceiling of your family, corrector frozen *and* refit; ours (0.815, 0.807) sat far above our 0.60 bar.

---

## 6. Finding 5: the κ4 closure that paid

**The form is Team Puffi's.** Let S(A,B)_ijkl = A_ij B_kl + A_ik B_jl + A_il B_jk. After each ReLU the closure regenerates the fourth cumulant as κ4 ≈ Σ_ab Λ_ab S(B_a, B_b), where the B_a are a few n×n *response modes* of the live state and Λ is a small signed coupling fitted by ridge. In Puffi's full closure transport is factored, S(B_a,B_b) → S(WᵀB_aW, WᵀB_bW) (an exact identity, Appendix P3.2), and every slice the step needs is O(n²). In our free build only C = Σ_z is transported in that sense: I is the diagonal of a transported δ, and Q_free is rebuilt at z from transported quantities (Appendix P3). ARC's augmented K = 3 has the same S-form, with modes {I, H} and Λ_IH = Λ_HI = 1 [proved: Appendix P3.1; D.2]. ARC's repository notes that the paper's §S.4.2 description is to be amended (`TODO.md`, read 2026-10-20), so the form is confirmed but the exact term set of their augmented estimate is not.

**Ours is the mode set:** three modes built only from quantities the chain already transports, plus n² matvecs: I = diag(Σ_a W_ai²), C = Σ_z, and a free Q mode from the transported T_z, μ_z and diag Σ_h (Appendix D.3). Modes needing their own n³ transport (C∘C, B4, the exact D_m K term) were dropped. Λ (16 × 3 × 3) and c (16 × 4) were fit on own nets 9000/9001. **Price:** pre-registered +0.18 pt, **measured +0.04 pt**; the dense form costs +3.57 pt.

**Rungs (v51 vs v49; v51 adds Λ and c and refits the corrector, so the graded step is closure plus refit; closure-only evidence is the v58_ne ablation below, 1.0327 raw, 17/20).** VALID-20 prototype: uncorrected 0.8885, refit head 0.9677 (16/20); port adjusted 0.9708 (17/20); **graded #334744 5.59e-9 → #334768 5.46e-9 (−2.3 %, closure plus refit), held out.**

**On the ablation code:** Appendix B.1.

**Reading.** The closure moves the uncorrected chain by −11 %; the head absorbs most of that (Finding 3), leaving 2–4 % shipped for 0.04 pt. Puffi's Phase 2 raw (1.22e-8, snapshot of 2026-10-17) suggests the family can carry more.

---

## 7. Finding 6 (supporting): a per-source cost floor for our κ3 birth

No score effect. Our κ3 birth's exact read costs 4 dense products per young source-layer [proved at n = 32–96]; the cheaper re-association reads 6–10 % wrong at n = 1024; a 3-product floor rests on an unmeasured premise [argument]. Full text: Appendix F.10.

---

## 7A. Finding 7 (supporting): the meter prices FLOPs; the wall cap prices memory traffic

The score meters FLOPs but the 120 s wall cap prices memory traffic, so extra exact Winograd levels became a knapsack priced in util per predicted second, which chose v110 (4.21e-9, 102.3 s max wall). Full text: Appendix J.

---

## 7B. Finding 8 (supporting): two shared transported bases replace nine per-source old-tier bases

**Result.** v112_sb #337384 graded **4.01e-9** (public split 4.005e-9; pre-registered range 4.05–4.15e-9 [H], submission-time prediction 4.04e-9, ratio 0.993 to the latter), 100/100 MLPs completed, 0 failed, grader wall 87.2 s mean and 95.6 s max under the 105 s nomination rule. It replaced v110_fk (4.21e-9) as our nominated #1 on 2026-10-20: −4.8 % adjusted score, with 6.7 s less max wall. It is the graded parent of the corresponding submission, v117_kd (below).

**Idea.** Sources aged ≥ 6 live in the same forward-dominant subspace of the recent transport product, yet the chain carried nine per-source bases, each with its own QR and eigh. We replace them with two shared, transported bases: Q384 for ages 6–7 and Q224 for ages ≥ 8. New legs are admitted by a Gram solve F = (QᵀQ)⁻¹Qᵀ[P|A], whose image QF is the orthogonal projection of [P|A] onto span(Q), computed without re-orthonormalising (Q is no longer orthonormal after transport; Appendix P2) and with no eigh. An early gate had measured shared r384 at +0.2 % raw against +1.4 % for per-source bases on one net (net 0), and dropped it because the merged-basis eigh took 877 s/run. Rank, age and regeneration cuts of the old tier sit at about 2 % raw per 1 % util (R ≈ 2); this change drops no content, and the end-to-end gate (Appendix F.7) reads R ≈ 0.45, the first old-tier cut below 1.

**Evidence ladder** (Appendix F.7). A proxy gate was a KILL; the end-to-end gate passed its adjusted clause (0.9653) but failed its metered-cost clause (S = 1.228 < 1.5 pt) and stays a KILL; the gate that admitted v112 was registered on the passing clause after those reads (an exception, §8) and passed on 40 unseen nets (pooled raw 1.0145, 40/40 ≤ 1.10, worst 1.064).

**Clock miss and limits** (Appendix F.7): the calibrated clock under-predicted v112's grader max (87.9 s against 95.6 s); the f64 Gram solves bill 0.66 pt, and the 1.23 pt saving was metered on net 0 only.

**The corresponding submission, v117_kd #337578,** is v112_sb with two constants changed (pair-series order `_KH` 4 → 3, deep-layer corrector 0.9 → 0.95; `writeup/v117_kd_vs_v112.diff`): graded 4.00e-9 against 4.01e-9, grader wall max 89.2 s against 95.6 s, 0 failed. It combines the best two of six one-constant variants scored on 3 meter nets, and that meter cannot rank builds closer than about 0.3 %, so we cite v117_kd as the nominated build, not as evidence of a better method (selection disclosure and counterexamples: Appendix F.7).

---

## 7C. Final-layer hypersensitivity to coherent σ² error (supporting; measured 2026-10-21)

Summary result 2 states this finding. These arms ran on v112's chain (v117_kd's parent; the f64 FIT12 twin, 12 FIT nets, head frozen) or on the 3-net meter that selected v117_kd (§7B); the K = 2 comparison is against v117_kd itself (f32 port, net 1340). The arms, all in Appendix F.7, are: the coherent σ² scale (VSE1); the knob scan, including Pepper's off-diagonal compensator (CMP, #327838 p.9); old-tier damping; the reading [inference] with its consistency note on the leader's raw MSE; why κ3 is necessary (K = 2 from first principles); and what we would try next.

---

## 8. How we tested

**Pre-registration.** Every lever is a gate in `research/R2_GO_NOGO.md`; for most, mechanism, instrument, control, bar and a numeric prediction were written before the run.

- **Ledger.** `research/rebuild/gates.jsonl` (153 records through G-RB147, 2026-10-20; KILL 73, PASS 40, MISS 12, INFO 6, STOP 2, UNKNOWN 20) plus `research/R2_GO_NOGO.md` for G-RB148–149 (read-only lanes, not gates).
- **Exceptions.** The ledger is not globally append-only: four records lack a pre-run block, one arm is post-hoc, and some result stamps were edited in place (F.4). The gate behind v112 is a further exception: it was registered after the end-to-end gate's FIT12 and VALID-20 reads, with that gate's failed cost clause dropped and its passing clause turned into the bar (§7B). Its held-out nets are genuinely unseen, but the gate is not pre-registered in the strict sense.

**Adversarial review.** Seven agents (Lenses A–G, `research/review/`) attacked our floor claim; three reviewed V21.

---

## 9. Limitations

1. **The gap** (v117_kd vs the leader in the 2026-10-21 20:34 UTC feed snapshot: 3.10× score, 1.95× raw, 1.57× util, C.1; the 2026-10-18 halves in C.1 were computed on v101r and are not re-measured). Finding 4 bounds only the truncation knobs tried with the head frozen; Appendix C.2 gives an inference about the util half.
2. **Which chain each number came from.** Five chains are involved; Appendix A.2 maps each finding to its chain and its distance from the ablation build.
3. **Inference on selection data.** VALID-20 chose head checkpoints and constants (Appendix A); screens of about 35 / 50 / 42 arms had no multiplicity correction; bootstrap intervals exist only for the §3 oracles. Graded readings are single numbers, and our best graded score carries a winner's-curse bias of unknown size.
4. **Breadth.** The adjoint rests on three FIT nets, the §3 oracles on six.
5. **Theory.** The closure is an ansatz with a fitted Λ; D.2's S-form identity is now machine-checked (Appendix P3), but the free-transport hypothesis H-FT is not; T2 is argued, T1 is checked at n ≤ 96 only.
6. **Timing margins and two util meters** (Appendix B.2).
7. **Billing and arena persistence:** Appendix F.11.
8. **Scope.** One shape (1024 × 16); the g, κ, Λ and c tables are shape-specific.
9. **Verification boundary:** Appendix F.11 and B.5.

---

## 10. LLM-use and uncertainty disclosure

- **Writing and code.** Anthropic Claude models (Claude Fable 5.1 and Claude Opus 5.5), running as Claude Code agents that I orchestrated, wrote every draft of this document and the submitted code from v21_rb onward; the graded v11_sw (#334046) was built by a Hermes coding agent (kimi-k2.7-code) around a Claude-written Strassen kernel. I wrote none of the code or prose.
- **Decisions.** I set the goals and guardrails (source rule, pre-registration, ship bars), approved or declined each submission, and chose which to submit and designate.
- **Checks.** Every measurement and proof check was run by an agent; I re-ran none of them and have not independently re-derived the mathematics. Claude agents audited V30 against its source files and re-ran Appendix E from a fresh unzip; V16–V31 were each edited by a Claude agent from the previous version (`writeup/V31_CHANGELOG.md`).
- **Councils, for ideas only, each checked against the ledger.** Three Ollama-cloud model councils (kimi and deepseek, glm timed out; a ~04Z council on the leaders' score histories; kimi, deepseek and glm, whose GLM-5.3 proposed the copula idea of Appendix F.7). Adversarial review was by agents (Claude, Ollama Cloud and local open-weight councils), not by me.
- **Full disclosure and the list of uncertain items:** Appendix K.

---

## Appendix A. What is fitted, and which chain each number came from

### A.1 Fitted objects

| object | fitted on | selected on |
|---|---|---|
| MIX2 corrector (≈ 15 KB; output scale 1.2) | teacher-forced one-step drift, 60 FIT nets | VALID-20 checkpoint; scale by a paired VALID-20 scan |
| 16 g_l (excess kurtosis) | own generator nets (seeds 5000–5023) | × 0.92 on 12 FIT nets, with a refit (v42_g92) |
| 16 κ_l; Λ (16 × 3 × 3); c (16 × 4) | own nets 9000/9001 | – |
| v80_kk (κ × 0.8, K31 × 0.9), v84_k8q96 (deep K31 × 0.8, Q22 × 0.96), v95_khs (κ × 0.875, deep corrector × 0.9) | – | FIT-screened among ≈ 35 / ≈ 50 arms (G-RB91, G-RB96) or FIT12 (G-RB106/109); confirmed on VALID-20: 0.9743 (20/20), 0.9788 (17/20), 0.9901 (16/20) |
| structure: RK, ranks 384/224, ages 6/8, port Price–Mehler pair-series order `_KH` 4 (G-RB24) | – | gated |
| v117_kd (port Price–Mehler pair-series order `_KH` 4 → 3, deep corrector × 0.9 → 0.95) | – | 3-net meter (VALID 10/13/16): the best two of six one-constant variants of v112, combined (`meter117.out`; §7B) |

v58_ne is v57_azs with near-exact cost trims and no refit; its corrector weights are bit-identical to v51's (v49 plus Λ and c, refit on its own chain). Nothing was fit on TEST nets or on grader feedback, but graded scores informed which candidates we submitted. **Mechanistic:** the representation (ARC), the accuracy steps (504aldo's prose), the closure form (Puffi) and our free-transport build. **Fitted:** everything in the table.

### A.2 Which chain each number came from

| result | chain | distance from the ablation build (v58_ne) |
|---|---|---|
| Finding 1, adjoint | uncorrected f64, K = 2 gates, age 5 | no closure, no head |
| Finding 1, depth profile; Finding 2, G-RB85 column | f64 twin of v59_p05, head on | adds a prune threshold; f64 |
| Finding 2, G-RB119 column; Finding 4 | f64 twin of v95_khs, head on | adds Appendix B's v80–v95 constants, RK 2, al07; f64 |
| Finding 3 | rows 1–3 pre-closure lean pair; rows 4–7 as gated | mixed |
| Finding 5 ablation | shipped v58_ne, VALID-20 | the ablation build |
| Finding 6 | lean f64 age-6, no closure | no closure, no head |

## Appendix B. Score lineage, the ablation, timing and nomination

### B.0 Measured performance impact on graded submissions (moved from the V29 front matter)

> **Measured performance impact on graded submissions.** Scores are AIcrowd graded adjusted; ids from Appendix B.1 and `research/rebuild/calibration.jsonl`.
>
> 1. **Noise-corrected oracle + known-answer control (§3; the correction is a known method applied here): no graded impact.** It produced no build ("No σ² build followed"); its effect was on direction: it withdrew G-RB117's σ²-only rule and left the σ² lever (0.511) unclaimed. A diagnostic, not a lever.
> 2. **Judge-with-the-head-in-place rule (§4): no graded gain; it stopped two shipments.** The dense closure (G-RB33, +3.57 pt, adjusted 1.113) and the κ4 predictor (G-RB73, 1.100 with the head) were not submitted. The avoided loss is not quantified on graded nets.
> 3. **Truncation ceiling (§5): no graded impact.** 0.815 frozen / 0.807 refit against a 0.60 bar closed the podium route (G-RB117/120); nothing was built from it.
> 4. **Free-transport κ4 closure (§6): −2.3 % graded, 5.59e-9 → 5.46e-9 (v49 → v51 #334768), +0.04 pt; the step is closure plus a corrector refit (Appendix A.1), not closure-only.** The only graded delta attributed to an algorithmic idea; graded v49_age6k4 #334744 → v51_sscf #334768 (`PROGRESS.md`). The clean closure-only evidence is the v58_ne OFF/ON ablation: 1.0327 raw, 17/20 nets worse (VALID-20, `ladder/*.json`).
> 5. **Constant screens with the head refit (A.1: v80_kk, v84_k8q96, v95_khs) and one prune change (v87_p02, G-RB100): v77_fuse #335642 4.92e-9 → v80 #336255 4.84 → v84 #336329 4.72 → v87 #336372 4.60 → v95 #336648 4.41e-9 (−10.4 % cumulative; `calibration.jsonl`).** VALID-20 ratios 0.9743 / 0.9788 / 0.9901; graded ids as listed.
> 6. **Exact-cost work (B.5, B.1): v95 #336648 4.41e-9 → v98 #336789 4.28 → v99r #336957 4.28 (−10.3 % ops, output-identical, no score change) → v105 #337002 4.24e-9 (two exact Σz cuts, −0.9 %); extra exact Winograd levels → v100r #336949 4.19, v101r #336941 4.18, v102 #336978 4.14e-9 (best score; disqualified by wall 116.5 s and Mini-10 0.371 s).**
> 7. **Wall-budgeted level allocation (G-RB137/139): v105 #337002 4.24e-9 → v110 #337268 4.21e-9 (−0.7 %) at 102.3 s max wall (not selected), vs v106 #337067 4.16e-9 at 113.2 s (over the 105 s rule).** Predicted max 97.6 s; actual 102.3 s (one +4.7 s outlier). The only shipped change selected by a wall model this write-up describes.
> 8. **Shared transported old-tier bases (§7B, G-RB142/143/144): v110 #337268 4.21e-9 → v112_sb #337384 4.01e-9 (−4.8 %), 0 failed, grader wall 87.2 s mean / 95.6 s max; nominated #1 on 2026-10-20, then the graded parent of the corresponding submission.** v117_kd #337578 (two constants on v112, §7B) graded 4.00e-9, a difference below the meter's resolution, with max wall 89.2 s. The wall clock under-predicted v112 (predicted max 87.9 s, actual 95.6 s; §7B).
> 8b. **Paired comparison against the organizers' reference K = 3 (MIT-licensed code, `github.com/alignment-research-center/mlp_cumulant_propagation` at the commit pinned in Appendix E, run unmodified as an oracle, f32, no fitted constants; `research/rb149/ORACLE_COMPARISON.md`).** Our side is the corresponding submission v117_kd, including its learned corrector (fitted on 60 FIT nets); V29 measured its parent v112_sb, and both rows are given. On 8 full-split nets 1300–1307 (official truth, N = 1e9 per the dataset's full config; analytic noise correction avg_variance/N ≈ 7e-11, identical in both arms; never used for fitting, but part of the 40-net held-out bar that admitted v112 in G-RB144, earlier the bar of G-RB130 and G-RB140 and later of G-RB151, all three KILL) v117_kd's final-layer MSE is 2.076e-8 vs 3.893e-8 for the reference: ratio 0.533 (net-bootstrap 95 % CI [0.489, 0.592]), paired difference CI [−2.2e-8, −1.4e-8], lower on 8/8 nets (v112_sb: 2.07e-8, ratio 0.532, CI [0.488, 0.591], 8/8). On 8 VALID nets (also used by our ship ladder) v112_sb's ratio is 0.547 [0.51, 0.59], 8/8 (`research/rb149/compare_valid_table.md`; not re-run for v117_kd). Cost, both in FLOPs: 388 n³ for v117_kd (388 for v112; the full flopscope meter, every op) vs 3040 n³ for the reference (a matmul-only count; its App. J polynomial gives 8304 n³ in the paper's own FLOP accounting), so roughly an eighth, and the matmul-only count understates the reference's total. Scope: one reference configuration (simple factorized K = 3); the augmented variant runs out of memory at n = 1024 in its own code.
> 9. **Late gates G-RB130/131/132/136/140 (Appendix F): all KILL, 0 graded impact.** Net: every graded gain after v58_ne (4.98e-9 → 4.00e-9, −19.7 %) came from constant screens, exact-cost engineering and one near-exact cost cut (shared old-tier bases, raw ×1.0145, §7B); the three transferable findings changed what was *not* built.

### B.1 Selected graded ladder (the rows a finding or nomination cites; the full ladder is in `research/rebuild/calibration.jsonl`; all failed = 0 unless noted)

**Lineage (moved verbatim from the V30 header in V31).** **This document corresponds to one submission: v117_kd, AIcrowd #337578 (graded adjusted 4.00e-9, 0 failed; nominated together with v105_sw #337002, B.4)**, folder `submissions/v117_kd/`, which contains the closure (rules v14 §6). v117_kd is v112_sb (#337384, 4.01e-9, its graded parent) with two constants changed (`writeup/v117_kd_vs_v112.diff`, §7B). v112 is v110_fk (#337268, 4.21e-9) with the old tier on two shared transported bases (§7B); v110 is v105_sw (#337002, 4.24e-9) plus exact extra Winograd levels, and v105 is v99r_rm (#336957, 4.28e-9) plus two exact Σz cuts, all with the same closure; the §6 closure ablation was run on v58_ne (#335139, 4.98e-9). Nominations: B.4. Our then-best build, v101r_xp (4.18e-9), ranked 80 of 300 on 2026-10-18, when the leader was at 1.32e-9 (1.29e-9 in the 2026-10-21 20:34 UTC feed snapshot, C.1), and we do not claim the best estimator.

| graded id | what changed | util | graded adjusted |
|---|---|---|---|
| #332561 v0 | starter-kit covariance propagation | – | 3.93e-7 |
| #334046 v11 | own factored κ3 chain + learned corrector (prior lineage) | 0.380 (Mini-100) | 1.0934e-8 |
| #334468 v21_rb | from-prose rebuild of the factored K = 3 chain (D.1) | 0.394 | 9.22e-9 |
| **#335139 v58_ne (ablation build)** | quadrant views + entry trims (near-exact) | **0.2235** | **4.98e-9** |
| #336853 v99_rm | v98 with 10.3 % fewer flopscope ops (14,841 vs 16,545) | – | **FAILED** (remote transpose, B.5) |
| #336876 v100_xs | + exact extra Winograd level on sites T, T2 | – | **FAILED** (same) |
| #336890 v101_xp | + the same on M2, paired qa quadrants | – | **FAILED** (same) |
| **#336957 v99r_rm (base of v105)** | v99 with varargs transpose | – | 4.28e-9 |
| #336941 v101r_xp (former #2) | v101 with varargs transpose | 0.198 (feed) | 4.18e-9 |
| **#337002 v105_sw (selected)** | v99r + only v102's two exact Σz cuts (no extra Winograd levels) | – | 4.24e-9 |
| **#337578 v117_kd (selected; corresponding submission)** | v112 + port pair-series order `_KH` 4 → 3 + deep corrector 0.9 → 0.95 (§7B); wall 85.3 / 89.2 s | 0.187 (feed) | **4.00e-9** |
| #337587 v120_kdl (tied; not selected) | v117_kd + LITE × 0.9; wall max 93.2 s | 0.188 (feed) | 4.00e-9 |
| #337610 v122_rk3 / #337612 v123_rk3lt (probes; §7B) | v117_kd variants scored 0.9994 / 0.9987 on the 3-net meter (failed count not recorded) | – | 4.02e-9 / 4.02e-9 |
| **#337384 v112_sb (graded parent of v117_kd; selected 2026-10-20, replaced 2026-10-21)** | v110 + two shared transported old-tier bases with Gram-solve admission (G-RB142/143/144, §7B); wall 87.2 / 95.6 s | 0.1898 (fingerprint) | **4.01e-9** |
| **#337268 v110_fk (not selected)** | v105 + exact extra Winograd levels on old-tier sites F0 and K0, chosen by util per wall-second (G-RB139); wall 94.0 / 102.3 s | 0.2021 (fingerprint) | **4.21e-9** |
| **#336978 v102_sz (best score before v112; not nominated)** | v101r + two exact Σz cuts (G-RB124); wall 116.5 s, Mini-10 worst 0.371 s | – | **4.14e-9** |
| **#337067 v106_1x (not selected; 113.2 s wall)** | v105 + exact extra Winograd level on site T only (G-RB134); wall 113.2 s | 0.200 (fingerprint) | **4.16e-9** |

Sources: `PROGRESS.md`, `research/rebuild/calibration.jsonl`, the 2026-10-17 snapshot. **Calibration:** graded/predicted has median **0.9976** over 22 prospective builds (v78–v112, graded before 2026-10-20T23Z, the V29 cutoff; 0.9977 over the 17 through v101r; the 17-build median is the same without the v91 duplicate), range 0.987–1.006. The four backfilled rows (v58_ne–v77_fuse) are excluded. v98_fd was predicted at 4.29e-9 and graded 4.28e-9; v101r_xp 4.19e-9 and 4.18e-9. The three failed builds have no ratio. Six builds graded on 2026-10-21 fall outside that cutoff: v116_a7 1.022, v116_r448 1.428 (the unvalidated Q448 probe, a single-net tail blow-up, G-RB157), v117_kd 1.000, v120_kdl 1.000, v122_rk3 1.005 and v123_rk3lt 1.0075; over all 28 rows the median is 0.9989 and the range 0.987–1.428.

**Ablation.** `research/rebuild/ladder/v58_ne_noclose_vs_v58_ne_screen_valid.json` (VALID-20 OFF/ON 1.0327 raw, 17/20 nets worse).

**On the ablation code.** `submissions/v58_ne_noclose/` is v58_ne with the closure off (`_SSC_CLOSURE = False`), each arm carrying the head fitted on its own chain; never submitted. On VALID-20, OFF vs ON reads pooled raw 1.0327 and adjusted 1.0309, 17 of 20 nets worse (Figure 2, Appendix B.1): a validation reading.

![Figure 2 — closure OFF/ON on v58_ne](figs/F3_closure_on_off_v58ne.png)

**Figure 2.** Per-net raw-MSE ratio, closure OFF / ON on v58_ne (VALID-20), sorted. Source: the ladder JSON above.


### B.2 Timing and meters (worst per-net residual, grader's subprocess runner, this host; cap 0.400 s)

Clean-session readings: v58_ne 0.342, v95_khs 0.341, v98_fd **0.37297**, v99r_rm 0.323, v101r_xp 0.354, v102_sz 0.371. Margins were thin (v96_d6 failed at 0.4016 s, not submitted, G-RB112; v78_p02 read 0.397 s clean). **Timing is read in process, not through the grader's remote client.** **Two util meters:** the ladder meter read v95 → v97 as 20.94 → 20.71 pt (G-RB113); `fingerprint.py` read v97 → v98 as 20.9223 → 20.5468 pt, so v97 differs by 0.21 pt between meters.

**B.3 v98_fd designation.** v98_fd met the conditions as finally registered, not every bar: the in-process residual bar was waived as a tie, the band widened from 0.373 s to 0.378 s (pre-registered before any v98 Mini-10 reading), and the ladder's 0.345 s ship bar read FAIL. The slot rule passed (graded 4.28e-9 < 4.36e-9, failed 0).

### B.4 Nomination (set 2026-10-21; changeable until 2026-10-22 23:59 UTC)

**Selected on AIcrowd: v117_kd #337578 and v105_sw #337002** (`writeup/USER_DECISIONS.md`, UPDATE 2026-10-21 ~19:20Z, user-approved, verified on a fresh page load). The write-up corresponds to v117_kd #337578 (rules v14: exactly one successfully graded submission). **Why v117_kd replaced v112_sb #337384** (selected 2026-10-20): it is v112 with two constants changed (§7B) and is at least as good on every graded axis we checked (raw MSE is tied at 2.13e-8 in the feed): score 4.00e-9 vs 4.01e-9; public 4.001e-9 vs 4.005e-9; worst public MLP 4.98e-9 vs 4.99e-9; IQR 3.64–4.33e-9 vs 3.65–4.35e-9; grader wall mean / max 85.3 / 89.2 s vs 87.2 / 95.6 s; 0 failed. The score differences are below the meter's resolution (§7B); the wall margin is what matters for the private re-run, because the selection page states that selections are re-scored on a freshly generated hidden test set, so wall is re-measured. v120_kdl #337587 tied (public 4.000e-9) with a worse worst MLP (5.04e-9) and max wall 93.2 s, so it was not chosen. A rule written before #337610 and #337612 graded froze the nomination: a later build would replace v117_kd only if it beat 4.00e-9 by ≥ 0.5 %, with worst public MLP ≤ 4.98e-9 and max wall ≤ 89 s. Neither did (both 4.02e-9). **Why v105_sw is the other selection:** it was chosen (2026-10-21, participant-approved) as the different-failure-mode fallback: it is an older chain without the shared old-tier bases (§7B), so a defect specific to the shared-basis path cannot zero both selections. Its max wall (89.4 s) is now slightly above v117_kd's (89.2 s), so the V29 wall-margin argument below no longer applies.

**Superseded V29 text (2026-10-20), kept as history.**

The write-up corresponds to v112_sb #337384 (rules v14: exactly one successfully graded submission, which need not have placed); v105_sw #337002 is the second fallback, after v110_fk (USER_DECISIONS.md, UPDATE 2026-10-20 19:50Z; v99r_rm #336957 was the last fallback in the superseded 04:37Z block and is kept only as the graded base of v105), and v58_ne is cited only for the §6 closure ablation. v105 is v99r plus two exact Σz cuts with the same closure.

**Selected on AIcrowd (2026-10-20 ~20:55Z, both slots set, changeable until 2026-10-22 23:59 UTC): slot 1 v112_sb #337384, slot 2 v105_sw #337002** (`writeup/USER_DECISIONS.md`, UPDATE 2026-10-20 ~21Z, superseding the 19:50Z recommendation of v106 as #2 and the 04:37Z recommendation of v110 as #1). v112 graded 4.01e-9 with 0 failed and a 95.6 s max wall (87.2 s mean), so it meets the pre-registered G-RB144 rule (graded < 4.21e-9, failed 0, max wall ≤ 105 s). **Clock calibration miss:** the calibrated clock predicted a max wall of 87.9 s for v112; the grader read 95.6 s (+8.8 %), an under-prediction for a build faster than v105 (r = 0.987). v110 graded 4.21e-9 with 0 failed and a 102.3 s max wall, so it also meets the rule and is the alternate. The rule is grader public max wall ≤ 105 s (G-RB128): v105 89.4 s and v99r 94.2 s pass. v106_1x (v105 plus one exact extra Winograd level on site T, G-RB134) graded 4.16e-9 with 0 failed but a 113.2 s max wall. Why v105 and not v106 in slot 2: the selection page states that selections are re-scored on a freshly generated hidden test set after the phase closes (public scores do not carry over), so wall time is re-measured. Slot 2 is therefore insurance against slot 1 failing, not upside: v106 trails v112 by 3.7 % on the same nets, a systematic gap that a fresh draw is unlikely to reverse, and v112's one plausible failure is a slower re-run grader. That failure removes v106 (113.2 s) and v110 (102.3 s) first; v105 has the most wall margin (89.4 s max). For the record, v106 dominates v101r_xp (4.18e-9, 109.5 / 113.5 s), which it replaced. The single site cost +16.9 s mean wall, about 90 % of the two-site cost, so the one-site prediction (~100 s) was wrong. v102_sz #336978 (4.14e-9) fails both rules (wall 116.5 s; Mini-10 0.371 > 0.365 s) and is not nominated. v105_sw (v99r plus only v102's two exact Σz cuts, G-RB129) met all five pre-registered conditions: graded 4.24e-9 (predicted 4.24e-9), 100/100 completed, grader wall 85.7 s mean / 89.4 s max (its timing bar had missed by 1.1 ms and passed a re-measure with a disclosed condition breach). The 04:37Z block listed v99r_rm #336957 (4.28e-9) as a further fallback; the 19:50Z block does not. Never nominate #336853, #336876 or #336890 (failed). With nothing selected, the two best public scores enter automatically. The dates come from the challenge announcement of 2026-10-17 08:28Z, read at 21:40Z (`writeup/USER_DECISIONS.md`), not from RULES_v14: Phase 2 submissions close 2026-10-21 23:59 UTC, nominations are due 2026-10-22 23:59 UTC, and the write-up is due 2026-10-28 23:59 UTC.

### B.5 The output-identical ratchet v99–v101 and the remote-mode gate

After v98 we kept the output fixed and cut cost (G-RB118, G-RB121, G-RB122): v99 has 10.3 % fewer flopscope ops; v100 adds an exact extra Winograd level on sites T and T2 (util −2.03 %); v101 the same on M2 plus paired qa quadrants (−0.235 %); the loop stopped when a step gained under 0.5 %. The final-layer f64 identity with the previous build is about 3e-15 throughout. Graded: v101r 4.18e-9 (predicted 4.19e-9), v100r 4.19e-9, v99r 4.28e-9, all failed 0. The first submissions of v99–v101 failed on the grader (§9, item 9; full text in Appendix F.11); the repair is G-RB123, and `remote_check.py` now requires the same output digest and metered util under flopscope-client 0.12.3 against flopscope-server 0.12.3 as in process. Grader wall time later proved the binding constraint (§7A).

## Appendix C. The board and the gap

### C.1 Board numbers, each with its source

| date / source | leader | ours |
|---|---|---|
| 2026-10-18 live (leaderboard feed) | marius_binner 1.32e-9 (raw 1.09e-8, util 0.121) | v101r_xp rank 80 of 300 (v102_sz 4.14e-9 graded later that day) |

Selected for the private re-evaluation (set 2026-10-21): v117_kd #337578 (4.00e-9, max wall 89.2 s) and v105_sw #337002 (4.24e-9, max wall 89.4 s); the corresponding submission is v117_kd (B.4). Grader feed snapshot 2026-10-21 20:34 UTC (`writeup/proofs/p2_rows_20261021T2034Z.json`, sha256 321f94476625cd18ac7f63a3fe726770139a9a81aafcf3e6c9d1ed3b604120c0): leader marius_binner #337453 adjusted 1.29e-9 (raw 1.09e-8, util 0.119); v117_kd adjusted 4.00e-9 (raw 2.13e-8, util 0.187).

Gaps against the live leader (2026-10-18): 4.18/1.32 = 3.17× score, 2.11/1.09 = 1.94× raw, 0.198/0.121 = 1.64× util. The ERROR_MAP target of 0.618 comes from J2W's 1.4e-8 on the 2026-10-13 board.

### C.2 The util half of the gap [inference]

Each leader's latest submissions sit at a near-fixed util (marius_binner 0.122–0.126, J2W 0.105–0.107, mliston 0.110–0.113, oliver_chen 0.126–0.128; insights rows, failed = 0). On our v90_al (21.13 pt), 88 % of FLOPs are matmul/einsum: ≈ 11.9 billed dense products per layer. At the same matmul share, util 0.121 would allow ≈ 6.8 per layer; that share is assumed, not measured, so this addresses only the util half (1.64×) of the gap, not the raw half (1.94×).

## Appendix D. The rebuilt chain and the closure's derivation

### D.1 The rebuilt chain (G-RB1; `research/rebuild/DESIGN.md`)

Per layer:

1. Linear step: μ_z, Σ_z = WᵀΣ_hW, and the κ3 slice T_z from transported factors by eq. (16).
2. κ4 from the §6 closure.
3. Our n×n ReLU closure (F.3).
4. Births in hub form: the κ2κ2 diagram, the D21/Q22 diagrams of eq. (18), and the κ4 (2,1,1) feed.
5. Ageing by f₁ (eq. 19).

Sources of age ≥ 6 share a rank-384 basis; sources of age ≥ 8 share a nested rank-224 one. The hub-form blocks match the paper's explicit sum to 5e-16 [proved].

Our reading of the prose's "exact κ4 diagonal" diverged (NaN by layer 9). That is a failure of our reading, not of 504aldo's method.

### D.2 ARC's augmented κ4 in S-notation [derived]

ARC's augmented K = 3 tracks η̃4 = h_{≤2}(κ4[h]) as an n×n matrix H.

- **Same form.** Summing over the six index pairings of δ⊗H gives **g(H) = S(I, H) + S(H, I)**, which is ARC's Definition S.2.2 in S-notation. Augmented K = 3 therefore has the same form as a response closure with modes {I, H} and Λ_IH = Λ_HI = 1 (both off-diagonal entries: a single one is not index-symmetric, so it is not a fourth cumulant; Appendix P3, falsifier P3a). After the linear step ARC's I mode becomes the dense M = WᵀW (Appendix P3.2); ours (D.3) is diag(M), a third object, and off-diag(M) is 0.706 of ‖M‖_F at n = 1024 (Appendix P3, (c)). H is in the span of neither Puffi's mode set nor ours, so we claim only "same form", not containment.
- **Measured.** With the 1/(n+4) coefficient in place, H̃ = Wᵀdiag(H)W reproduces the MC marginal κ4 (mean ratio 1.06 → 0.87). It is nonetheless 1.42–1.54× worse end to end (per-neuron R² 0.03–0.15): KILL. **Scope of that KILL:** the organizers' repository (`TODO.md`, read 2026-10-20) states that the paper's §S.4.2 description of the augmented algorithm is to be amended (the diagram cap in eq. 14 is K+1 for the augmented variant) and that factorized-augmented computes a different estimate from unfactorized augmented. We ran the organizers' MIT reference code (`research/rb149/`, interim, not in the release). ARC's augmented factorized K = 3 does not fit in memory at n = 1024 (`research/rb149/out_arc_aug.txt`), so no augmented-vs-augmented check of our port exists at that size; against ARC's *simple* factorized K = 3 our H-mode estimate differs smoothly (rms 1.3e-5 at L1 to 1.8e-4 at L15, net 9000, one 1e7-sample reference whose noise floor (about 7e-8) exceeds the MSE differences being compared, so only the paired profile is read). This excludes a layer-localised defect but does not verify the augmented term set. In ARC's own code at depth 16 (own MC, n = 128 and 256) augmentation helps early and middle layers (about 1.5× averaged over layers) and its effect at the final layer is mixed (n = 128: 0.86×, worse; n = 256: 1.16× better). Our KILL is a KILL of our port at n = 1024, depth 16. Whether a correct augmented K = 3 would help at the scored layer is unknown, both because §S.4.2 is flagged by its authors as to-be-amended and because the n = 256 sign differs from ours. V21's parenthetical reconciling the omitted coefficient with a measured ×264 is deleted, because the source file states the reconciliation two incompatible ways.

### D.3 The closure's free modes

I = diag(m_i), with m_i = Σ_a W_ai². C = Σ_z. Q_free = P_off[½c₂ m̄ (T_z + T_zᵀ) + c₃ (t_z μ_zᵀ + μ_z t_zᵀ) + c₄ v_z v_zᵀ + c₅ (Wᵀ1)(Wᵀ1)ᵀ] / v̄, with t_z = Wᵀt and v_z = Wᵀdiag Σ_h (one n² matvec each). The shipped Λ is indefinite on 8 of the 14 fitted layers (minimum eigenvalue −7.9e-3), outside the exact Gaussian-scale-mixture case of Appendix P3.4; on those layers the form is a fitted ansatz with no generative model behind it.

### D.4 Source statement behind §1.3

Every submission from v21_rb on was written from public prose (thread 18218), the ARC paper and our own prototypes. 504aldo's MIT-licensed code was cloned into the same workspace on 2026-10-06 13:03 UTC for a separate attributed port (staff ruling, thread 18240), which failed 6 of 10 MLPs in our worker and was not submitted; no number here comes from it. The rebuild agent's ledger records that the clone was not opened, but the rebuild and the clone were different agents in one workspace and no tool log was audited. A name-level check found five def/class names in common (four harness-mandated, plus `_buf`). The rebuild is therefore prose-derived, not clean-room; this paragraph supersedes the graded docstrings saying "No participant code was read".

## Appendix E. Reproduction

Release: https://github.com/manderson240/arc-whitebox-phase2 (same files as arcwb_phase2_release_v31.zip; sha256 printed in RELEASE_ZIP.sha256 at the repo root)

> **Reproduce in 5 minutes.** Commands are given relative to the root of `arcwb_phase2_release_v31.zip` (its sha256 is in `writeup/arcwb_phase2_release_v31.zip.sha256` next to the zip; per-file hashes in `SOURCES.md`). Copy the whole `research/` tree, not single folders: `ci119.py` reads `../rb117/results_seat.jsonl` by relative path, so step 2 must be run as written, from the root. Outputs are verbatim (first lines shown where long). Every step below was re-run on 2026-10-22 (UTC) from a fresh unzip of that zip into an empty directory; `writeup/V31_REPRO_FINAL.md`, next to the zip (not in it), records PASS/FAIL per step. `ci119.py`, `tab119.py` and `compare_heldout.py` rewrite their outputs in place (byte-identical when correct), so run them on a copy. Evidence scripts need Python 3.10+ and numpy; run them with `python3 -I`, except the mpmath-based checks of step 11, which need `python3 -P` when mpmath is installed in the user site (`-I` hides `~/.local`).
>
> ```bash
> # 1. The headline's mechanism, with no chain in it (Appendix G)
> python3 -I writeup/oracle_bias_toy.py
> # -- full-mean SE 5e-4: half SE 7.07e-04, full SE 5.00e-04
> # z8: rho=0.89  r(half)=1.594  r(full)=0.797  corrected=-0.000
> # z15: rho=0.33  r(half)=0.223  r(full)=0.111  corrected=-0.000
> # -- half SE 5e-4: half SE 5.00e-04, full SE 3.54e-04
> # z8: rho=0.63  r(half)=0.797  r(full)=0.398  corrected=-0.001
> # z15: rho=0.24  r(half)=0.111  r(full)=0.056  corrected=+0.000
>
> # 2. Claim 1: corrected σ² seat 0.511 [0.438,0.581]; control 0.305 → 0.002 [−0.043,0.046] (§3 table, Figure 1)
> (cd research/rb119 && python3 -I ci119.py)
> # var                full 0.776 extrap 0.511 CI90 [0.438,0.581] LOO [0.482,0.544] per-net [0.524, 0.65, 0.607, 0.41, 0.519, 0.355]
> # varL1115           full 0.710 extrap 0.635 CI90 [0.589,0.680] ...
> # var_k3_k4_h0       full 0.305 extrap 0.002 CI90 [-0.043,0.046] LOO [-0.015,0.022] ...
> # (also k4 0.868→0.852, var_k3 0.545→0.253, var_k3_k4 0.512→0.209, var_h0 0.929→0.664, k4_h0 0.730→0.713)
>
> # 3. Claim 3: untruncated ceiling 0.815 frozen; rank ladder; pair-series order; head refit 0.807 / 0.810 (§5)
> (cd research/rb117 && python3 -I tab.py results_r64.jsonl results_r256.jsonl results_r1024.jsonl) && (cd research/rb120 && python3 -I tab120.py)
> # u_all_r1024          n=12 pooled 0.8151 impr 12/12 0.931 0.881 0.784 0.761 0.776 0.798 0.761 0.873 0.824 0.694 0.874 0.856
> # FIT12    frozen     n=12 pooled 0.8151 improve 12/12 ...
> # FIT12    refit60    n=12 pooled 0.8071 improve 12/12 ...
> # FIT12    refit48    n=12 pooled 0.8100 improve 12/12 ...     <- "0.8100 with FIT12 held out" in §5
>
> # 4. Claim 5 ablation and the graded ladder's calibration (§6; B.1)
> python3 -I -c "import json; d=json.load(open('research/rebuild/ladder/v58_ne_noclose_vs_v58_ne_screen_valid.json'))['rung_data']['valid']; b={r['net']:r for r in d['base']}; c={r['net']:r for r in d['cand']}; ns=sorted(b); print('closure OFF/ON pooled raw %.4f adj %.4f worse %d/%d'%(sum(c[n]['raw'] for n in ns)/sum(b[n]['raw'] for n in ns), sum(c[n]['adj'] for n in ns)/sum(b[n]['adj'] for n in ns), sum(c[n]['raw']>b[n]['raw'] for n in ns), len(ns)))"
> # closure OFF/ON pooled raw 1.0327 adj 1.0309 worse 17/20
> # 4b. Calibration with the V29 cutoff (rows graded before 2026-10-20T23Z; the ledger has grown since, see B.1)
> python3 -I -c "import json,statistics; g=[json.loads(l) for l in open('research/rebuild/calibration.jsonl')]; g=[r for r in g if r.get('status')=='graded' and 'ratio' in r and not r['t'].startswith('backfill') and r['t']<'2026-10-20T23']; print(len(g),'graded builds, median graded/predicted %.4f, range %.3f-%.3f'%(statistics.median(r['ratio'] for r in g),min(r['ratio'] for r in g),max(r['ratio'] for r in g))); [print(r['build'],r['id'],r['graded']) for r in g if r['build'] in ('v95_khs','v99r_rm','v105_sw','v106_1x','v110_fk','v102_sz','v112_sb')]"
> # 22 graded builds, median graded/predicted 0.9976, range 0.987-1.006
> # v95_khs 336648 4.41e-09 / v99r_rm 336957 4.28e-09 / v102_sz 336978 4.14e-09 / v105_sw 337002 4.24e-09 / v106_1x 337067 4.16e-09 / v110_fk 337268 4.21e-09 / v112_sb 337384 4.01e-09
> # 4c. The rows after the cutoff, including the corresponding submission
> python3 -I -c "import json; [print(r['build'],r['id'],r['graded'],round(r['ratio'],4)) for r in map(json.loads,open('research/rebuild/calibration.jsonl')) if r.get('status')=='graded' and '2026-10-20T23'<=r['t']<'backfill']"
> # v116_a7 337548 4.14e-09 1.0222
> # v116_r448 337549 5.81e-09 1.4275
> # v117_kd 337578 4e-09 1.0
> # v120_kdl 337587 4e-09 1.0
> # v122_rk3 337610 4.02e-09 1.005
> # v123_rk3lt 337612 4.02e-09 1.0075
>
> # 5. Finding 7: the wall knapsack that chose v110, and the clock's calibration against the grader (§7A, F)
> (cd research/rb139 && python3 -I tab.py wall1.jsonl) && (cd research/rb137 && python3 -I tab_wall.py wall.jsonl | head -9)
> # | v110_t2 | ... | 1.0677 | 95.4 | 20.2237 | -0.0987 | 0.0163 |
> # | v110_f0 | ... | 1.0496 | 93.8 | 20.2560 | -0.0664 | 0.0150 |
> # | v110_k0 | ... | 1.0255 | 91.7 | 20.2715 | -0.0509 | 0.0223 |
> # | v110_fk | ... | 1.0729 | 95.9 | 20.2051 | -0.1173 | 0.0180 |
> # v105/v99r=0.9761 (|.-1|<=0.05: True)  v106/v105=1.2010 ([1.12,1.28]: True)  v102/v105=1.2985 ([1.18,1.36]: True)  order v105<v106<v102: True
> # CALIBRATION PASS
> # remote v106-v105 backend+overhead delta (sum over 4 predicts) 39.40 s; per class:
> #   add            +20.09 s ( 51.0 %)  calls +690
> #   subtract       +13.42 s ( 34.1 %)  calls +504
>
> # 6. Finding 8: shared old bases on 40 held-out nets (§7B, G-RB144)
> (cd research/rb142 && python3 -I tab144.py res_144_heldout.jsonl)
> # A0 vs rb130 SHIPPED: n=40 max|rel| 0.000e+00 -> VALID; bit-identical True
> # A2/A0 HELD-OUT: n=40 pooled 1.0145 nets<=1.10 40/40 improve 11/40 worst 1.064 -> PASS (bar <= 1.038, >= 24/40)
>
> # 7. Summary result 2 / §7C: final-layer hypersensitivity (VSE1) and the FIT12 knobs (OD, σ² channels, CMP, MEX/MEXR)
> python3 -I research/rb153/tab153.py research/rb153/res_vse1_fit12.jsonl
> # CTL vs rb142 A2: n=12 max rel 1.87e-12 (OK <= 1e-9)
> # VSE1_+1e-03      n=12 raw 4.21259 ... impr 0/12 ...
> # VSE1_+2e-03      n=12 raw 13.61786 ...
> # VSE1_+4e-03      n=12 raw 51.13151 ...
> # VSE1_-1e-03      n=12 raw 3.95174 ...
> # VSE1_-2e-03      n=12 raw 13.03779 ...
> # VSE1_-4e-03      n=12 raw 49.50049 ...
> python3 -I research/rb153/tab153.py research/rb153/res_s1_fit12.jsonl research/rb155/res_fit12.jsonl
> # CTL vs rb142 A2: n=12 max rel 1.87e-12 (OK <= 1e-9)
> # (selected lines)
> # CMP+0.00025      n=12 raw 0.99879 ... impr 7/12 ...
> # CMP-0.00025      n=12 raw 1.00435 ...
> # MEX              n=12 raw 0.99773 ... impr 9/12 ...
> # MEXR             n=12 raw 0.99853 ... impr 7/12 ...
> # OD0              n=12 raw 22.60757 ...
> # OD0.5            n=12 raw 6.45116 ...
> # OD0.8            n=12 raw 1.90916 ...
> # OD0.9            n=12 raw 1.24528 ...
> # OD1.2            n=12 raw 1.75170 ...
> # VS1              n=12 raw 1.18113 ... / VS1c 1.15785 / VS2 1.10335 / VS3 1.14878
>
> # 8. Claim 9 / item 8b: the corresponding submission v117_kd vs the organizers' reference K = 3 on nets 1300-1307 (G-RB149)
> SUB=v117_kd python3 -I research/rb149/compare_heldout.py
> # ratio of means ours/ARC = 0.533, net-bootstrap 95% CI [0.489, 0.592]; n nets = 8; wins for ours 8/8
> # SUMMARY: ours 2.08e-08 vs ARC 3.89e-08 final-layer MSE (noise-corrected), paired diff CI [-2.2e-08, -1.4e-08], FLOPs 388 vs 1520 n^3 units, 8 nets
> ```
>
> **Step 8 notes.** It re-reads the stored per-net outputs of both arms (`research/rb149/heldout_port_v117_kd_*.npy`, `heldout_arc_*.npy`) against the 8 official truth files shipped in `research/full/data` (CC-BY-4.0); the ARC code itself is not shipped. The reference outputs were produced by github.com/alignment-research-center/mlp_cumulant_propagation at main commit 93d091a4c26c042bfffa28f2e76a81bc0aba94bb (2026-08-04; MIT licence; the `research/rb149/ref/` tree we ran is byte-identical to that commit's 52 source files, verified by git blob sha; a stub jaxtyping module replaces that dependency, the ARC source is untouched) via `research/rb149/arc_heldout.py`; clone it at that commit to re-run them. **Units:** the SUMMARY line prints ours in FLOPs (388 n³, the full flopscope meter) but ARC in matmul MACs (1520 n³ = 3040 n³ FLOPs, matmul only); in one unit that is 388 vs 3040 n³ FLOPs. Without `SUB` the script reproduces V29's table for the parent v112_sb byte for byte (ratio 0.532, CI [0.488, 0.591], 8/8). It rewrites `research/rb149/compare_heldout_table_v117_kd.md` in place (byte-identical when correct).
>
> ```bash
> # 9. Appendix P1-P2: oracle bias and its Richardson removal; the Gram-solve admission is a projection (numpy only)
> python3 -I writeup/proofs/check_p1_p2.py
> # P1 bias(full)=-1.014e-02  predicted tr(HS)/2N=-1.016e-02  SE=4.9e-05
> # P1 Richardson residual=-2.394e-05 (should be ~0 within SE)
> # P1 falsifier (non-smooth) Richardson residual=3.268e-02 vs SE 9.4e-05
> # P1 skewed samples: Richardson residual N=8 -5.63e-03 (SE 5.3e-04), N=16 -1.37e-03 (SE 2.6e-04), N=32 -4.08e-04 (SE 1.3e-04); log-log slope -1.89 (expect ~ -2)
> # P2 cond(Q)=6.2e+01  Gram-solve vs QR projection rel err=3.7e-15  naive QQ^T rel err=6.1e+05
> # ALL PASS
>
> # 10. Appendix P3-P4: the κ4 S-form identities and slices; transport cost Θ(L²) / Θ(wL) / shared bases (numpy only)
> python3 -I writeup/proofs/check_p3_p4.py
> # == P3a: six pairings of delta (x) H  ==  S(delta,H) + S(H,delta)
> # PASS  max|g(H) - [S(I,H)+S(H,I)]| = 3.6e-15 (n=7)
> # ...  (32 PASS and 9 FIRED lines; identical, blank lines aside, to writeup/proofs/out/check_p3_p4.out)
> # PASS  attribution is complete: sites + outside ops = 1.2279 pt = total difference
> # ALL CHECKS PASS AND ALL FALSIFIERS FIRE
>
> # 11. V29's proof checks (research/proofs): each must PASS, and FAIL with --perturb; -P, not -I, for the mpmath checks
> for f in research/proofs/check*.py; do python3 -P "$f" >/dev/null 2>&1 && a=PASS || a=FAIL; python3 -P "$f" --perturb >/dev/null 2>&1 && b=PASS || b=FAIL; echo "$(basename $f) normal=$a perturb=$b"; done
> # check10_selfbirth.py normal=PASS perturb=FAIL
> # check1_cumulant_transport.py normal=PASS perturb=FAIL
> # check2_relu_moments.py normal=PASS perturb=FAIL
> # check3_edgeworth.py normal=PASS perturb=FAIL
> # check4_error_propagation.py normal=PASS perturb=FAIL   <- Parts A and B only, see below
> # check5_6_kurtosis_selfavg.py normal=PASS perturb=FAIL
> # check7_bivariate_cov_correction.py normal=PASS perturb=FAIL
> # check8_sect_transport.py normal=PASS perturb=FAIL
> # check9_readout_order.py normal=PASS perturb=FAIL
> ```
>
> **Step 11 caveat.** `check4_error_propagation.py` Part C silently skips in a fresh copy: it needs the six Monte-Carlo caches `research/mc_cache_alllayers_mlp{0..5}_N200000.npz` (134 MB each), which are not shipped. Its PASS from the release therefore covers Parts A and B only; the six Part C rows in `research/proofs/check4_out.txt` (growth exponents p = 0.93–1.70, mean 1.35) come from the workspace and cannot be reproduced from the release.
>
> **Λ refit reproducibility note.** Refitting Λ with `research/rebuild/fit_lambda_sect.py` (a workspace script, not shipped) needs the shipped α grid, `ALPHAS=1e-3,1e-2,1e-1,1`; the script's default grid (1e-4…1) misses the shipped Λ by 3.9 % (G-RB155 control).
>
> **Re-running the corresponding submission** needs the starter kit (`whest`, README): `whest run --estimator submissions/v117_kd/estimator.py --dataset hf://aicrowd/arc-whestbench-public-2026@v2-phase2 --split mini --n-mlps 10 --runner subprocess --format json`. `--estimator` takes the `estimator.py` file; a folder path exits with `SETUP_ERROR: Estimator module file not found`. Run from a fresh unzip of the release (an earlier build of the release, sha256 fe907c00…454a32, whose `submissions/` is byte-identical to this one's; `estimator.py` sha256 147afa4a…5ff30f, the graded file) on an idle host under the exclusive timing lock (load 4.78 at start; the starter-kit venv, whestbench 0.16.1 / flopscope 0.12.1), it completed 10/10 Mini MLPs with 0 failed: adjusted 4.13e-9 (per MLP 3.61–4.49e-9; the graded 4.00e-9 is over the grader's 100 MLPs), mean util 0.187, residual wall 0.328–0.398 s against the 0.400 s cap (`writeup/proofs/out/mini_v117_kd_fromzip.json`). The largest, MLP 0 at 0.3976 s, leaves 2.4 ms. An earlier idle run of a staged copy read the same scores with MLP 0 at 0.3997 s (`mini_v117_kd_v30final.json`), and a run on a loaded host (load 9–14) failed 4 of 10 MLPs on that cap (`writeup/V30_REPRO_REPORT.md`, not shipped). The local residual-wall margin is thin; the grader's 100/100 completed run is the reference. Not reproducible from the release: §2 (needs `k4lib`/`k3chain`/truth files), §4's seven rows and §3's G-RB86/G-RB73 numbers (ledger prose; `research/k4pred/eval_k4.jsonl` holds G-RB73's raw rows), §6's graded 5.59 → 5.46e-9, §7's `rb80_floor_check.py`, and the 3-net knob meter and K = 2 runs of §7C, whose input nets are not shipped (their outputs are, in `writeup/proofs/`).


*Everything else in this appendix is procedure: it needs the official starter kit and the ~1e9-sample truth files, which are not shipped.*


Python is `whest-starterkit/.venv/bin/python`, run from `~/cohezion-labs/arc-whitebox`; in-process checks run under `ulimit -v 12000000` and `OMP_NUM_THREADS ≤ 8`. Paths refer to the code release that accompanies this write-up, `arcwb_phase2_release_v31.zip`. It contains `submissions/v117_kd` (the corresponding submission, byte-identical to the graded #337578) and its parent `submissions/v112_sb`, the other graded builds v58_ne / v99r / v101r / v105 / v106 / v110, `research/rb142/`, `rb146/`, `rb149/`, `rb151/`, `rb152/`, `rb153/`, `rb155/`, the gate ledger (`research/R2_GO_NOGO.md`, `gates.jsonl`), the scripts and JSONL for T1, G-RB117/119/120, G-RB136/137/139/140 and G-RB142/143/144, the Appendix P checks in `writeup/proofs/`, the toy `writeup/oracle_bias_toy.py`, the V29 and V30 write-ups as history, and `SOURCES.md` with the sha256 of every file.

- **Corresponding submission** (same flags for the ablation build, `submissions/v58_ne/estimator.py`): `whest run --estimator submissions/v117_kd/estimator.py --dataset hf://aicrowd/arc-whestbench-public-2026@v2-phase2 --split mini --n-mlps 10 --runner subprocess --format json`.
- **Ladder and closure ablation:** `research/rebuild/ladder.py --base submissions/v58_ne --cand submissions/v58_ne_noclose --rungs screen,valid --no-stop`.
- **Findings:**
  - Finding 1: `research/rb85/run_map.py` (row 10a).
  - Finding 2: `research/rb85/analyze.py`, `research/k4pred/eval_k4.py`, `research/rb119/ci119.py` (reads the G-RB117 seat arms and the G-RB119 halves).
  - Finding 4: `research/rb117/tab.py results_r1024.jsonl results_build.jsonl`; `research/rb120/tab120.py`.
  - Finding 6: `research/rb67/rb67_{capture,oracle,slice}.py`, `research/rb80/RESULT.md`.
  - Finding 8: `research/rb142/tab144.py res_144_heldout.jsonl`, `tab142.py`; metering `meter2.out`; port bars `port_fp.out`, `port_rc.out`, `port_f64.out`, `wall_v112.jsonl`.
  - §7C: `research/rb153/tab153.py`; `writeup/proofs/meter3.py` and `meter117.out`, `meter119.out`, `meter121.out`–`meter123.out` (3-net knob meter; net-0 probe meter: `meter116.out`); `writeup/proofs/k2_perlayer.py`, `meter_full.py`, `k2_mix_screen.py` (K = 2).
- **Proof checks:** `writeup/proofs/check_p1_p2.py`, `check_p3_p4.py` (Appendix P; built-in falsifiers that must fire); `research/proofs/check*.py`, each with a `--perturb` variant that must fail.
- **Figure:** `writeup/figs/make_f6_ladder_v27.py`, `writeup/figs/make_f0_oracle_bias.py`. **Toy:** `python -I writeup/oracle_bias_toy.py` (Appendix G).

- **Compliance:** a static audit of v95_khs, v90_al and v87_p02 passed (`research/COMPLIANCE_AUDIT_20261017.md`).

## Appendix F. Other negatives and our components

**Late gates (2026-10-19; each pre-registered except as listed under Exceptions in §8; each re-computed by an orchestrating agent from the raw result files, not by me).**

- **Head data scaling (G-RB130): KILL.** Refitting the MIX2 head on FIT60 plus 150 or 300 official full-split nets reads 0.9950 and 0.9940 pooled raw on 40 held-out full nets (27/40 improved; bar 0.98): the head is data-saturated. hyojun_kwon (forum 18255) reports the same flat curve for his own corrector.
- **Transported parent features (G-RB132): KILL.** Three features passed through W and W∘W add +0.0009 teacher-forced R² (bar +0.02; the placebo adds nothing). A teacher-forced screen cannot see a gain that appears only in free running; Keenan Pepper (#327838, p.9) published this caveat in Phase 1, before ours.
- **Matched dead-unit cut and saturated-row removal (G-RB131; Artyom_Mazur, forum 18249, prose): KILL as analogues, not replications.** On 12 paired nets the matched cut reads 1.177 of our prune, and dropping saturated rows reads ~54×: those rows are our chain's linear transport core. Our shipped prune costs nothing against no prune (0.963 vs 0.964).
- **The missing non-tree C·κ3 birth (G-RB136; Susupro, forum 18254, prose): real, but worth ≈ 1 % in a K = 3 chain.** Derived to first order in C and checked by Monte Carlo (n = 64, 1e6 samples: coefficient 1.02–1.05; `research/rb136/DERIVATION.md`). Carried exactly and uncosted on FIT 0/2/4 with the head frozen it reads 0.9919 (bar 0.85); the negated term reads 1.066 and a placebo C 1.040. Susupro's 1.56× was measured inside a K = 4 chain, where this term feeds κ4 births.
- **Wall-budgeted level allocation (G-RB137/G-RB139): a calibrated clock turns the wall cap into a knapsack.** The local client–server harness reproduces the grader's v106/v105 and v102/v105 wall ratios to ≈ 0.01; the grader's MAX grows 1.32× faster than its mean, so a predicted max is 89.4 × (1 + 1.32 (r − 1)). Pricing each single-site extra level on v105 in util saved per predicted second (T2 0.016, F0 0.015, K0 0.022 pt/s) selected F0 + K0 under a 100 s predicted max. v110 graded 4.21e-9 at 102.3 s max (predicted 97.6 s; one +4.7 s outlier). The same clock under-predicted v112 (87.9 s against 95.6 s; §7B).
- **Joint constant fit (G-RB140; idea from hyojun_kwon, forum 18255, prose): KILL.** A damped Gauss–Newton fit of our six scalar chain constants on pooled final MSE (FIT60, head frozen) improves the fit set by only 0.12 %, and reads 0.9982 on 40 held-out full nets (bar 0.985) and 0.9984 on VALID-20: the scanned constants were already within ≈ 0.1–0.2 % of a joint optimum.
- **Grader wall depends on op kind, not op count (G-RB127/G-RB134):** see the exchange rates at the end of Appendix J. v106 (one site) graded 4.16e-9 at 113.2 s max wall and was not selected (B.4).


### F.0 Everything else we measured (verdicts are the ledger's own)

| what | result |
|---|---|
| regenerating the old κ3 tier from O(n²) state (G-RB60) | held-out R² ≈ 0.69 at layers ≥ 10 (bars 0.90 / 0.95) |
| exact early-layer snaps; skipping early κ3 births (G-RB93) | a 2^21-sample oracle made it +79 % worse; skipping the layer-1 birth gave raw ×10.2 |
| thinner/low-rank legs, larger old ranks, per-MLP g, final-layer read corrector (G-RB92) | KILL; 0 of 42 arms reached the bar |
| depth profiles (G-RB97); constants refit on cut chains (G-RB98); entry Strassen depth (G-RB99) | the l ≥ 8 step is optimal within 0.7 %; refits recover 19 % / 9 % of the loss; 0.3–0.5 % |
| the al07 term on our twin (G-RB103/103b); constants on the al07 chain (G-RB106/106b); age 6 → 5 (G-RB110); one-at-a-time constant moves (G-RB111) | ≈ 1.2 % on the twin, yet −2.0 % graded on both bases when ported (G-RB104); best 0.9926 against a 1 % bar; 1.0251; all within ±0.2 % |
| head-seed ensemble of 5 MIX2 heads on the v95 twin (G-RB125) | KILL: FIT12 ens/single 0.9977 (bar 0.993); not worth ~5× head FLOPs |
| κ4 sector scatter (G-RB75, G-RB37) | (2,2) and (2,1,1)+(1,1,1,1) parts anti-correlated −0.68 to −0.84; exact (4)+(2,2) transport alone reads ×1.32–1.67 worse |
| six cost *expansions* on the v84 twin (G-RB102): own age 6 → 7, old group 224 → 288/320, own rank 384 → 448, RK 4 → 6/8 | 0.4–0.6 % raw per 1 % util, against ≈ 2 % per 1 % lost by our cuts (G-RB98); best o320 raw 0.9813 against a bar of 0.942: the frontier is asymmetric at our point |

### F.1 Seats by state injection (G-RB25/65; own nets 9000/9001; uncorrected, lower bounds)

| replaced by MC truth, layers ≥ 8 | 9000 | 9001 |
|---|---|---|
| Σ_h, the step's output covariance (state) | −39 % | −38 % |
| κ4 inputs (diag, Q, K31) | −32 % | −28 % |
| both | −57 % | −55 % |

### F.3 Our components inside the chain

- **The n×n ReLU closure.** It computes (μ_h, Σ_h, T_h) for all n² pairs with no matrix product, by the bivariate Price–Mehler series (order 4; order 3 in the corresponding submission v117_kd) with Edgeworth terms [proved]. Exact closed forms for the bivariate ReLU second moment under Gaussian inputs exist (arXiv:2601.22307, §2; arXiv:2601.16830, Thm 1); the order-4 truncation of that part is our choice, not a necessity.
- **Excess kurtosis.** The row-averaged excess kurtosis concentrates at g* = 3[Var‖A‖² − 2trC²]/[(trC)² + 2trC²] [proved; six nets × 16 layers, max |g − g*| 0.0024].
- **One-mode closure.** A common fluctuation of ‖h‖² gives κ4 = v·S(Σ,Σ), a one-mode response closure [proved under the model]. The same pairing structure with a depth-growing scalar is the leading 1/n connected four-point function of the weight ensemble at fixed input (Yaida 2019, eqs. V and 17); that is the annealed problem, not ours, so it corroborates the form without deriving it.
- **The MIX2 corrector.** From layer 4, a small MLP reads 21 per-neuron features the chain already computes and adds a signed correction to the carried mean. It costs ≈ 15 KB and 0.006 pt. About 70 % of its −20.2 % comes through feeding the corrected mean forward (Lens D).

### F.4 Ledger exceptions

- Two gates ran before any registration was written.
- One gate was judged against bars in the coordinator's recipe with no standalone block.
- One gate closed without a run.
- G-RB59's p* = 0.05 arm is post-hoc.
- One instrument was amended after a Phase-0 failure.
- G-RB61 re-priced its arms after the first read (conservative direction).
- G-RB80 is PASS by its pre-registered rule, with two numeric statements corrected.
- G-RB144 was registered after G-RB143's FIT12 and VALID-20 reads, with the failed cost clause removed (§7B).

### F.6 T1 at small n (G-RB80)

- **Read error.** The re-association's read error is 0.28–0.46, 0.16–0.29 and 0.106–0.168 at r/n = 1/8, 1/4 and 1/2 (random W, summed ages 1–4, n ≤ 96). The leg-optimal diagonal birth loses 93–99 %.
- **Not reproduced.** The claimed ×1.5–2 amplification of a leg's norm error read 0.74–1.88 (median 1.18) at n ≤ 96, so it stays [measured, n = 1024] only.

### F.7 §7B and §7C detail: v112's port bars, VSE1, the knob scan and the K = 2 run (moved verbatim from §7B and §7C in V30 for length); the §7B evidence ladder, v117_kd paragraph, clock miss and limits, and §7C's damping, reading and next step (moved verbatim in V31)

- *Port bars.* Metered util 18.9772; remote_check PASS; f64 agreement with twin A2 within 1.1e-4 (net 0) and 8.0e-3 (net 2); calibrated wall r(v112/v105) = 0.987. 17 of 18 QRs and 7 of 8 eighs are removed.

*§7B evidence ladder (moved verbatim from §7B in V31).*

**Evidence ladder.**

- *G-RB142 step 0 (proxy KILL).* Rule: KILL if the residual outside the fixed Q exceeds 3× the entrant's own top-384 residual at any layer ≥ 8. The ratio was 5.0–5.2 at l8 and 8.4–8.6 at l14, because each own basis sharpened with age while the shared residual stayed flat (3–4 % in norm). **Lesson: gate on the end-to-end quantity, not on a proxy against a moving baseline.**
- *G-RB143 (end-to-end).* Valid instrument (A0 bit-identical at OMP 2; A3 0.9746; random Q 2.50; M2 diverges). Raw FIT12 1.0192, VALID-20 1.0277 (20/20 nets ≤ 1.10). Metered saving S = 1.228 pt (20.2051 → 18.9772) against a ≥ 1.5 clause: **a KILL on its cost leg, and it stays one**, although its adjusted clause passed (0.9653).
- *G-RB144 (unseen nets).* G-RB143 failed its metered-cost clause (S = 1.228 < 1.5 pt) and stays a KILL. G-RB144 was then registered on G-RB143's passing adjusted clause only (bar: held-out raw ≤ 1.038 = 0.975 × 20.2051/(20.2051 − 1.228), with ≥ 24/40 nets ≤ 1.10), with the failed cost clause dropped and after FIT12 1.0192 and VALID-20 1.0277 had been seen, so a reading near those values was expected to pass. It was judged on 40 nets the A2 arm had never touched (ids 1300–1339): pooled raw 1.0145, 40/40 ≤ 1.10, worst 1.064, 11/40 improve; A0 matched the shipped control bit-identically. The held-out nets are genuinely held out and the graded 4.01e-9 stands, but the gate was not pre-registered in the strict sense: its bar was derived from data already seen. The decision to ship rests on this held-out read and the slot rule; the cost bar it replaced was not met.

*§7B, the corresponding submission (moved verbatim from §7B in V31).*

**The corresponding submission, v117_kd #337578.** v117_kd is v112_sb with two constants changed and identical weight files (`writeup/v117_kd_vs_v112.diff`): the order `_KH` of the Price–Mehler pair series in the n×n ReLU closure (F.3), 4 → 3 (the per-neuron Hermite recursion depth `_KGC = _KH + 4` moves 8 → 7 with it), and the deep-layer corrector factor (layers 8–14; the last-layer head is unchanged) 0.9 → 0.95. Graded 4.00e-9 (predicted 4.00e-9) against v112's 4.01e-9; worst public MLP 4.98e-9 against 4.99e-9; grader wall max 89.2 s against 95.6 s; 0 failed (`research/R2_GO_NOGO.md`, G-RB157 and its addendum; `writeup/USER_DECISIONS.md`, 2026-10-21 ~19:20Z, a workspace file not shipped). **Selection disclosure.** It combines the best two of six one-constant variants of v112 scored on the same 3 meter nets (VALID 10/13/16; `writeup/proofs/meter3.py`, `meter117.out`), so its meter reading is selection-biased. Afterwards 13 more single-knob variants (of v112 or of v117_kd) were run on those nets: 10 gave readings (`meter119.out`, `meter121.out`–`meter123.out`) and 3 crashed or ran out of memory. v120_kdl's reading is not in a shipped file, and four earlier probes were metered on net 0 only (`meter116.out`). None of them was nominated. It is tied with v120_kdl #337587 (v117_kd + LITE ×0.9; also 4.00e-9; worst MLP 5.04e-9, wall max 93.2 s). **Counterexamples.** Two later variants, v122_rk3 #337610 and v123_rk3lt #337612, both graded 4.02e-9 although the 3-net meter read 0.9994 and 0.9987 against v117_kd (`research/rebuild/calibration.jsonl` l.67–70). The 3-net meter therefore cannot rank builds whose readings differ by less than about 0.3 %, and v117_kd's 0.1 % score gain over v112 (public 4.001e-9 against 4.005e-9) is below that resolution; its wall gain (89.2 s against 95.6 s max) is one grader reading. We cite v117_kd as the nominated build, not as evidence of a better method.

**VSE1 (G-RB153).** Scale σ²_z at z-layers 11–15 by (1 + c). FIT12 pooled raw against the control: c = −4e-3 49.50, −2e-3 13.04, −1e-3 3.952, +1e-3 4.213, +2e-3 13.62, +4e-3 51.13; 0/12 nets improve in every arm (`research/rb153/res_vse1_fit12.jsonl`). A quadratic through the ±1e-3 points (quadratic coefficient 3.1·10⁶ per unit c²) predicts the ±4e-3 points to within 1 % and puts the optimum at c ≈ −2·10⁻⁵, worth about 0.14 %. Points nearer zero were registered but not run.

**The knob scan** (7 cost-neutral knobs at 28 settings, 4 cost-changing knobs at 8 settings, 2 two-knob combinations; knobs and verdict in the summary, result 2). Readings (FIT12 unless marked): σ² calibration channels 1.10–1.18; Pepper's off-diagonal compensator (CMP, #327838 p.9) best 0.9988 at c = +2.5e-4, its negation 1.0044 (G-RB155); dense-M closure mode 0.9977, with Λ refit 0.9985, both at about +4 % util (hand estimate; not metered).

**Why κ3 is necessary: K = 2 from first principles (G-RB154).** On net 1340 (outside the held-out nets 1300–1339; nothing fitted), a K = 2 chain with exact rectified-Gaussian variances and converged Mehler-series covariances (orders 12 and 48 agree) has final MSE 3.45e-6: 167× our shipped chain on the same net (2.07e-8), already 230× at layer 1, the second layer (1.59e-7 against 6.89e-10), and still 153× with our learned corrector switched off (2.26e-8) (`writeup/proofs/k2_perlayer_1340.out`, `meter_full_1340.out`, `meter_full_1340_headoff.out`). [argument] Each ReLU makes the next pre-activation a sum of n non-Gaussian terms, so non-Gaussianity is born at every layer; κ3 is O(n^−1/2) per neuron but coherent across neurons. Conditioning on the top 1–2 input directions (Gauss–Hermite, 8–16 nodes) recovers only 1.2–1.7 % of the K = 2 error (`writeup/proofs/k2_mix_screen.py`), so a few linear directions do not carry it.


*§7C old-tier damping and reading (moved verbatim from §7C in V31).*

**Old-tier damping (G-RB153, arms OD).** Scaling the transported old tier by α reads α = 0 22.6, 0.5 6.45, 0.8 1.91, 0.9 1.25, 1.2 1.75; 0/12 nets improve in any arm. No tested α beats α = 1; a quadratic through 0.9, 1 and 1.2 puts the optimum within 0.01 of 1. An Ollama-cloud model council had proposed an interior optimum in retained old content (the "council2 hypothesis" of the G-RB153 verdict); in our family it is falsified.

**Reading [inference].** The coherent part of the σ² error is already at its optimum, so what σ² error remains is incoherent per-neuron error, which a better covariance closure, not better constants, would have to remove. Exact σ² would leave 0.51× of raw (§3), so σ² is not the only remaining error. *Consistency note, not a proof:* the leader's graded raw MSE over ours is 1.09e-8 / 2.13e-8 = 0.51 (grader feed snapshot 2026-10-21 20:34 UTC, `writeup/proofs/p2_rows_20261021T2034Z.json`), close to our exact-σ² oracle, 0.51; the two are measured on different chains and nets, and this may be coincidence (first raised by a model in the ~04Z council, §10). *Related observation:* James Henry (#314695, rev. 2026-08-04, p.10) reports a 16:1 bias:variance asymmetry against a shrink filter at 256 × 32; his probe-noise decomposition (p.9) is a cousin of the noise correction we apply (Figure 1). Artyom_Mazur (forum 18249, p.18) reports an analogous parabola for a coherent scale of all layers' variances and a similar coherent/incoherent reading.

*§7C, what we would try next (moved verbatim from §7C in V31).*

**What we would try next.** Gaussian-copula pair moments with exact (Edgeworth) marginals, non-perturbative in ρ, in place of our truncated Price–Mehler pair closure (F.3; order 3 in v117_kd, order 4 in v112). It targets the incoherent per-neuron σ² error above. The idea is a model suggestion, not ours: GLM-5.3 proposed it in an Ollama-cloud council of three models (G-RB156), whose other proposals were either already measured in our ledger (the transported pair-kurtosis matrix, G-RB90) or variants of the same copula idea. A related measured bound: an exact (2,2)-slice κ4 oracle reads only 0.953 at layers 8–14 against a 0.85 bar, and exact h-side transport is ×1.5 worse (G-RB90).

*§7B clock miss and limits (moved verbatim from §7B in V31).*

**Clock calibration miss.** The calibrated clock predicted a grader max of 87.9 s; the grader read 95.6 s (+8.8 %), an under-prediction for a build faster than v105. The rule held with 9.4 s to spare; the miss is recorded for the next calibration.

**Limits.** The Gram solves run in f64 because cond(Q384) reaches ≈ 5e3 by l14, and bill 0.66 pt. The saving is 1.23 pt, not the hand-estimated ≈ 2.6 pt: gross 1.89 pt (matmul/einsum 1.25, Strassen add/subtract glue 0.09, qr/eigh 0.55) less the 0.66 pt of solves (plus 0.002 pt of other ops; total 1.2279 pt, Appendix P4 (c)), and the hand ledger treated old-Q rows and columns as linear shares of site cost when the leaf dimensions shrink only 11–14 %. The fixed Q224 nesting carries most of the raw price (refreshing it reads 1.0069 against 1.0192, at more util). S was metered on net 0 only.

### F.8 What did not work, and what we would try next (moved verbatim from the V30 two-page summary in V31)

#### What did not work (measured, so nobody needs to repeat it)
An exact (2,2)-slice κ4 oracle (0.953 at layers 8-14, against a 0.85 bar; exact h-side transport ×1.5 worse), the dense WᵀW closure mode with Λ refit (0.9985, +~4 % util, hand estimate; not metered), corrector (head) refits after a chain change (≈ 1.00 six times: G-RB18, G-RB29, G-RB61 ×2, G-RB76 1.005, G-RB151 1.004; G-RB120's refit moved 1 %), old-tier damping, σ² calibration channels (1.10-1.18), larger shared ranks (a tail blow-up on one MLP), and Strassen-depth variants (failed remote_check: arena KeyError, shape assertion; not measured). The ledger lists all ~160 gates (`research/rebuild/gates.jsonl`, 162 records) with their bars, pre-registered except where §8 'Exceptions' says otherwise.

#### What we would try next
Gaussian-copula pair moments with exact Edgeworth marginals, non-perturbative in ρ (proposed by an LLM council, G-RB156). This targets the incoherent per-neuron σ² error that result 2 points to.

### F.9 Figure 3: error origin by layer (moved from §2 in V31)

![Figure 3 — error origin by layer](figs/F2_error_origin_by_layer.png)

**Figure 3.** Share of final-layer MSE by layer of origin (diagonal adjoint, net 0) [A, unreplicated]. Each layer's local residual is weighted by gain_l, the mean squared column norm of its adjoint T_l; uncorrected f64 chain, no closure, K = 2 gates, age 5. Shares and caveats in §2.

### F.10 §7 in full: a per-source cost floor for our κ3 birth (moved verbatim from §7 in V31)

No score effect; uncorrected lean f64 age-6 chain without the §6 closure, FIT 0/2/4, registered before the runs.

- **T1 [proved at n = 32–96, G-RB80, perturbed falsifiers included].** The exact (2,1) read of a young source costs 4 dense products per layer (Nurlanggs, forum 18252, independently counts 4 logical n³ products per (source, layer) pair: 2 transports, 2 readouts); the only saving re-association, diag + rank r, costs 2 + 4r/n and reads 9–10 % wrong at r = 128 and 6–7 % at r = 256 at layer 14 (n = 1024, 2 % bar; G-RB67, KILL).
- **Δ [measured, G-RB68].** A slice-only chain misses 0.40–0.49 of the (1,1,1)-induced read Δ by norm (0.16–0.24 by energy). **T2 [argument]:** if P is dense (unmeasured, relayed from `LENS_F`), each young source needs ≥ 3 products per layer; this is not a theorem and covers re-associations of this birth only.
- We make no claim about what the leaders can afford.

### F.11 §9 items 7 and 9 in full (moved verbatim from §9 in V31)

7. **Billing.** A rebill of v77_fuse, v46_y5c and v78_p02 with 14 community billing-fix PRs matches exactly, with a planted control that changes (`research/billing_fix_check/REPORT.md`); none is recorded for v80_kk or later. **Arena persistence (disclosure):** since about v24, including v58_ne, scratch buffers and views persist on the estimator across `predict()` calls; the views' `reshape` is billed once per worker. On v101r_xp the first call bills 20.0821 pt and later calls 19.8490 pt: 0.233 pt per MLP, ≈ 1.2 % of score (v99r_rm 0.2025 pt), against ≈ 0.01–0.03 pt for v58-era builds. The starter-kit FAQ (`docs/troubleshooting/faq.md`) treats state built across `predict()` calls as a permitted optimisation that must not affect correctness; the NaN-poisoning probe shows it does not (bit-identical; `research/review/ARENA_PERSISTENCE_20261018.md`).

<!-- separate lists so that item 9 keeps its number -->

9. **Verification boundary.** v99, v100 and v101 as first submitted failed on the grader (ESTIMATOR_EXCEPTION, 100/100 MLPs) after passing every local rung: the grader runs flopscope in remote mode, and flopscope-client 0.12.3's `RemoteArray.transpose(*axes)` does not unwrap numpy's one-tuple `.transpose(perm)`. Our ladder ran in process; three lines fixed it, and a fail-closed gate (`research/rebuild/remote_check.py`) now precedes the ladder.

### F.12 Supporting results as listed in the V30 two-page summary (moved verbatim in V31)

- **Head-to-head against the organizers' code** (MIT reference, commit 93d091a): our graded parent v112_sb reads 0.532× (95 % CI 0.488-0.591; lower on 8/8 of nets 1300-1307, never used for fitting, but used as a selection bar) of ARC's simple factorized K = 3 raw MSE, at 388 vs 3040 n³ FLOPs (both in FLOPs; ours counts every op, theirs only matmuls, so theirs is understated; 3040 is 1.48× the Phase 2 budget).
- **Why κ3 is necessary** (first principles): a K = 2 chain (exact rectified-Gaussian variances, converged Mehler-series covariances) is 167× worse than our shipped chain on the same net (1340; 3.45e-6 vs 2.07e-8), and already 230× worse at layer 1, the second layer; with our learned corrector switched off the gap is still 153× (`writeup/proofs/k2_perlayer.py`, `meter_full.py`). [argument] Each ReLU makes the next pre-activation a sum of n non-Gaussian terms. On one net (1340), conditioning on the top 1-2 input directions (Gauss-Hermite, 8-16 nodes) recovers only 1.2-1.7 % of the K = 2 error.
- **Proofs with falsifiers** (Appendix P):
  - P1, the oracle bias;
  - P2, the shared-basis Gram admission is an exact projection;
  - P3, the κ4 closure's six-pairing identity and transport law;
  - P4, cost growth: per-source transport is Θ(L²), and shared bases make only the transport Θ(L).
  P1-P2: 4 checks and 2 falsifiers (`check_p1_p2.py`; its skewed-sample check also fails when the extrapolation is removed); P3-P4: 32 checks and 9 falsifiers (`check_p3_p4.py`). Each falsifier is a case where the proved statement must not hold, and it fires.

## Appendix G. A scalar toy of the oracle noise bias

`writeup/oracle_bias_toy.py` (no chain in it; constants from §3: the chain's σ² relative error 5.6e-4 at z8 and 1.5e-3 at z15, truth SE ≈ 5e-4). The chain's relative error e and the truth noise of each half are independent normals; a *perfect* oracle (true ratio 0, the known-answer control) leaves only the truth noise, so its reading is r = E[noise²]/E[e²]. We then form r∞ = 2·r(full) − r(half).

The script is `writeup/oracle_bias_toy.py` (21 lines; numpy, seed 0, 2,000,000 draws per row): it draws the chain error e and two independent truth halves nA, nB as normals, forms r(half), r(full) and r∞ = 2·r(full) − r(half), and prints the rows below. It is shipped in the release.

```python
"""Scalar toy: Monte-Carlo noise in a sampled-truth oracle biases its reading.
A PERFECT oracle (true ratio 0, the known-answer control) leaves only truth noise, so its
reading is r = E[noise^2]/E[e^2], e = chain relative sigma^2 error (loss ~ squared error).
Constants from V27 s3: e has SD 5.6e-4 (z8), 1.5e-3 (z15); truth-noise SE 5e-4."""
import numpy as np

rng = np.random.default_rng(0)
M = 2_000_000
CHAIN_ERR = {"z8": 5.6e-4, "z15": 1.5e-3}
# V27 s3 gives 5e-4 as the SE of the MEAN of the two halves; the brief reads it as one half's.
for label, se_full in (("full-mean SE 5e-4", 5e-4), ("half SE 5e-4", 5e-4 / np.sqrt(2))):
    se_half = se_full * np.sqrt(2)
    print(f"-- {label}: half SE {se_half:.2e}, full SE {se_full:.2e}")
    for layer, eps in CHAIN_ERR.items():
        e = rng.normal(0, eps, M)                  # chain error, independent of truth noise
        nA, nB = rng.normal(0, se_half, (2, M))    # two independent truth halves
        base = np.mean(e**2)
        r_half = 0.5 * (np.mean(nA**2) + np.mean(nB**2)) / base
        r_full = np.mean(((nA + nB) / 2) ** 2) / base
        r_inf = 2 * r_full - r_half                # split-half extrapolation to zero noise
        print(f"{layer}: rho={se_full/eps:.2f}  r(half)={r_half:.3f}  r(full)={r_full:.3f}  corrected={r_inf:+.3f}")
```

Printed output, verbatim:

```
-- full-mean SE 5e-4: half SE 7.07e-04, full SE 5.00e-04
z8: rho=0.89  r(half)=1.594  r(full)=0.797  corrected=-0.000
z15: rho=0.33  r(half)=0.223  r(full)=0.111  corrected=-0.000
-- half SE 5e-4: half SE 5.00e-04, full SE 3.54e-04
z8: rho=0.63  r(half)=0.797  r(full)=0.398  corrected=-0.001
z15: rho=0.24  r(half)=0.111  r(full)=0.056  corrected=+0.000
```

- **Reading.** Every row is a perfect oracle, yet it reads well above 0 before correction. §3 states the mean-of-halves SE as ≈ 5e-4; the first block uses that, the second treats 5e-4 as the single-half SE. Extrapolation recovers 0 in both (|corrected| ≤ 0.001). The toy is an identity, not a measurement: in this independent-normal model noise variance scales as 1/N, so the line through the half and full points hits zero at 1/N → 0 (the quadratic-loss case of the nested-Monte-Carlo bias, Rainforth et al. 2018, and the numerator bias of Pospisil & Bair 2021, eq. 10).
- **What it shows and what it does not.** The bias is a property of the estimator's accuracy, not only of the sample count: it is ≈ 7× smaller at z15 than at z8 (0.111 against 0.797) because the chain's error is ≈ 2.7× larger there and the reading scales as 1/error². It does not reproduce our measured readings (0.776 or 0.305 above), which come from the real chain; the toy omits correlation between chain error and truth noise, non-Gaussian tails and the head.

## Appendix H. Oracle method box, recipe and the oracle/ceiling ladder, Figure 4 (moved from the V29 front matter)

![Figure 4 — oracle and ceiling ladder](figs/F6_oracle_ceiling_ladder_v27.png)

**Figure 4.** Pooled final raw MSE vs the twin as shipped (head ON); each group names its twin and nets. Blue: uncosted constructions, head frozen. Dark orange: G-RB119 MC oracles, split-half extrapolated, 90 % bootstrap CI over 6 nets. Pale orange: uncorrected (G-RB117). Pink: G-RB85 oracles, noise-corrected. Last blue: G-RB120 head refit.

> **Method box.** (1) Run the f64 twin of a shipped build on FIT nets. (2) Inject one quantity (§1.1) and read the pooled ratio against the twin, head ON and frozen unless a row says otherwise. (3) MC truth uses two independent halves; G-RB85 and G-RB119 extrapolate to zero noise, r∞ = 2·r(full) − mean(r(A), r(B)) (first-order Richardson extrapolation in 1/N, Giles 2015 §2.3; the same zero-noise extrapolation as Sahani & Linden 2003 §3, and equivalent to subtracting the split-half estimate of the truth-noise variance); averaging halves (G-RB117) is an upper bound. (4) Verdict against the pre-registered bar in `research/rebuild/gates.jsonl`.

> **Recipe: how to run a first-order bias-corrected sampled-truth oracle** (what G-RB119 did; §3).
>
> 1. Compare the truth's standard error with the estimator's error on the injected quantity (ours: 5e-4 against 5.6e-4 at z8 and 1.5e-3 at z15, so the bias is not small).
> 2. Draw the truth as two independent halves (ours: 2^22 samples each) and keep the full-mean reading.
> 3. Read the pooled ratio with each half and the full mean, head in place and frozen; report r∞ = 2·r(full) − mean(r(A), r(B)), never the averaged-halves ratio alone.
> 4. Dose check where affordable (σ² only): inject 5× the noise and require the reading to sit on the line (ours 1.840 and 1.839 against 1.841).
> 5. Known-answer control: make every marginal quantity exact, head off; the corrected ratio must be ≈ 0 up to the truncation floor (ours 0.002 [−0.043, 0.046]; uncorrected 0.305).
> 6. Report each reading as a lever size with its corrector state (§3, §4), and a bootstrap CI over nets (six nets understate the tails).

## Appendix I. Related work and credits (moved from the former §1A and §1.2)

The sources below come from a literature search by a Claude agent that read each cited text (`writeup/DRAFT_RELATED_WORK.md` lists what it read and what it could not reach); I read none of them. The credits added in V31 (I.1, "Monte-Carlo noise") were read by a Claude agent from the participants' PDFs in `research/forum/pdfs_20261021/` and `pdfs_20261022/` and from forum prose; no participant code was opened.

**The noise correction is standard in two literatures.** In computational neuroscience the "noise ceiling" problem is ours: a model's squared error against a trial-averaged response contains the averaging noise, so even a perfect model reads a non-zero error. Sahani & Linden (NeurIPS 2002, §2–3) estimate signal power from repeated trials and extrapolate performance to zero noise; Schoppe et al. (2016) derive the ceiling from a split-half correlation; Cadena et al. (2019, eq. 23) subtract an estimate of the noise variance from the MSE; Pospisil & Bair (2021, eqs. 9–15) write the numerator's bias as trial variance over trial count and subtract an unbiased estimate (their Fig. 3A: the bias depends on signal-to-noise, our "depends on the estimator's accuracy"). Our r∞ is the same subtraction with the noise variance estimated from two halves. In the Monte-Carlo literature a reading f(sampled mean) with nonlinear f is a nested estimator with O(1/M) bias (Rainforth et al. 2018, Thm 3, its bounded-second-derivative case; the bias step is in its App. D proof), exact for quadratic f, which is why Appendix G's two-point line passes through zero. Richardson extrapolation is textbook (Giles 2015, §2.3); randomised multilevel estimators remove the bias exactly (Rhee & Glynn 2012; Blanchet, Glynn & Pei 2019; Goda et al. 2016).

**The estimator family is the organizers'.** Wu et al. (arXiv:2605.05179) propagate cumulants through a random MLP with a Hermite-based diagram formula (Thm A.2), power cumulants and a one-scalar κ4 trace (§4.1), and a factorized K = 3 algorithm (§S.4.3) that never forms the n³ tensor. It carries a dense n×n covariance, drops the (3, 1) slice of κ4, and costs 30n³L² + 39n³L + … FLOPs by their fitted polynomial (their Appendix J, Table 1; ReLU experiments). They conjecture MSE ≤ c_K(L/n)^K and test at width 256 with up to 12 hidden layers, with 2^34-sample truth so reference noise is negligible. The paper has no oracle injection, learned corrector, rank or age truncation, or discussion of sampled-truth bias, and treats the Hermite/diagram series as asymptotic in width (§S.6.2). Their repository's `TODO.md` says the §S.4.2 description of the augmented algorithm is to be amended and that factorized-augmented computes a different estimate from unfactorized augmented (see D.2). Our chain (D.1) is the factorized K = 3 skeleton plus ageing, ranks, the (3, 1) slice, a response closure and a learned corrector.

**Other background.** Exact closed forms for the mean and covariance of a ReLU layer under Gaussian input exist (arXiv:2601.22307, §2; arXiv:2601.16830, Thm 1), so our order-4 Price–Mehler pair step truncates a quantity others compute exactly. (Order 3 in v117_kd; see F.3.) Yaida (arXiv:1910.00019) gives the finite-width four-point function of the weight ensemble at fixed input, the annealed problem rather than ours (F.3). Benson & Ballard (2015), Huang et al. (arXiv:1611.01120) and Ballard et al. (arXiv:1507.00687) cover Strassen-like algorithms, their addition and memory-movement costs, and their error bounds (§7A).

### I.1 Credits (moved from §1.2)

- **ARC (Wu et al. 2026, arXiv:2605.05179):** the factored K = 3 representation (§S.4.3), the Hermite-based diagram summation formula (Thm A.2), power cumulants (§4.1), the diagonal adjustment (§S.4.3 step d.ii), the one-scalar κ4 trace (§4.1), augmented K = 3 (§S.4.2), the MSE ≤ c_K(L/n)^K conjecture (§5), and the FLOP polynomials of their Appendix J. Their factorized K = 3 drops the (3, 1) slice we carry (§S.4.3 step b.i). Code: github.com/alignment-research-center/mlp_cumulant_propagation (MIT).
- **Team Puffi (#327725, Cipo1 on behalf of Team Puffi):** the response-closure form, its ridge-fitted Λ, the mode set {C, Q, v̄I, B4}, and the mean-error transport picture §2 measures. Earlier Puffi and mliston write-ups are the source of our learned corrector. We read Puffi's prose only; their Phase 2 results (rank 11, raw 1.22e-8 at util 0.165, snapshot of 2026-10-17) are better than ours and their method is not public to us.
- **Team 504aldo (forum 18218; prose only):** the accuracy steps on ARC's chain (memoryless κ4 core, D21 feedback, exact last-layer trim); the cost structure (thin legs, aged basis, deep Strassen); the pre-activation κ4 law, the Khatri–Rao wall, the ε²-law and the slice-only floors.
- **Nurlanggs (forum 18252; team NullPointer; prose and PDF):** oracle-injection tables at layers 8–15 (exact variance, C_off, D21, d3 + g4); the finding that channels cancel (an exact (2,2) slice alone raises MSE) and the rule to rank terms by effect on the scored output; a count of 4 logical n³ products per (source, layer) pair (§7).
- **Susupro (forum 18254; prose, code not opened):** the first public full K = 4 run; a birth-type ablation placing the gain in non-tree C·κ3 births; handing a K = 3 chain the exact covariance of his deterministic K = 4 chain (0.64×); a carried-state per-layer corrector (0.887× raw on 50 nets). These are ratios of deterministic chains, not sampled truth (`research/forum/MINING_20261018.md` line 30), so §3's noise bias does not apply. Nurlanggs's tables are oracle injections with sampled truth like ours, and his PDF measures the noise: a 16M-path oracle carries a +4.2e-9 MSE floor on its own net (var_h / N), and scoring injections against the oracle's own paths reads 0.564 against 0.520 when scored against the organizers' independent 1e9-path truth (forum 18252, p.23; the injections are on p.7); these are later lab-chain readings than the forum-post pair 0.610/0.508 in I.2. His remedy is to score against the independent truth ("use them as the metric", p.23); ours extrapolates away the noise in the injected quantity itself.
- **hyojun_kwon (forum 18255; prose, code not opened):** a frozen third-order cumulant estimator plus a 6,594-parameter terminal corrector of the final-layer mean, with "state-matched" coefficient tables fitted to pooled final MSE (3.7978e-9 → 3.6473e-9, −4.0 %). Its corrector data scaling agrees with our G-RB130 (`research/forum/MINING_20261020.md`).
- **Monte-Carlo noise in oracles and references (read from the PDFs in V31).**
  - *Artyom_Mazur (forum 18249).* His oracle substitutions use 10⁷ samples with two independent seeds "so that the oracle's own noise can be measured and subtracted" (p.4; also p.3). He reports an "exact" covariance substitution that read worse because its 4·10⁶-sample oracle's noise was coherent (p.19, N50), an off-diagonal-covariance payoff of ×0.55–0.68 "noise-corrected two ways" (p.20), and a split-half noise ceiling of 0.87–0.98 for his linear model of the covariance error (p.20). This is the closest public work to the correction we apply: noise measured from two seeds and subtracted in the substituted quantity. Ours, narrowly: a known-answer control, a 5× dose check and the measured size of the misreading (0.776 vs 0.511). His item 4 (p.2) states the compensation principle (exact variance alone can make the result worse, ×1.09 on one net; variance, κ3 and κ4 together ×0.12; summary result 3), and his Proposition 1 (p.19) the coherent-plus-independent structure of per-neuron variance error (summary result 2).
  - *kai_leal_gonzalez (forum 18246).* Estimates the noise of the organizers' truth, his dumps and an independent bake from three independent estimates (p.2), and notes that injected slices carry Monte-Carlo noise, so oracle gains are "if anything, understated" (p.9), the direction we measured.
  - *hyojun_kwon (forum 18255, revision of 18 October).* Gates scored against "split-half-corrected Monte Carlo references" (p.27; split-half noise subtraction, p.26).
  - *James Henry (Phase 1, topic 18097, #314695, rev. 2026-08-04).* Decomposes per-seed final MSE into bias² plus across-seed variance, correcting the K-seed mean's residual noise by /K (p.9).
  - *abhimanyu_singh (forum 18264, prose).* A quadratic law for iid noise on the D21 and D3 slice read-outs (added MSE ≈ 0.91σ² and 0.60σ², n = 256) and a bias/variance asymmetry: truncation bias propagates while zero-mean noise attenuates (summary result 2).
- **Others (prose):** marius_binner (fire-rate pruning), mliston (a 1.5n κ3 carrier), AndreasHad04 (a capped (2,2) carrier), trim_qewas (oracle substitution), kai_leal_gonzalez (the al07 law, forum 18246), il.miscusi (the scale mode, forum 18248). **Textbook:** cumulant transport, Price/Mehler, Edgeworth, Wiener–Hermite chaos, Strassen–Winograd (Benson & Ballard 2015; Huang et al. 2016; stability: Ballard et al. 2016).

### I.2 Relation to published oracle tables (moved from §3; regime caveats added in V30)

*Relation to published oracle tables.* Susupro (18254) substitutes the exact covariance of his *deterministic* K = 4 chain (0.64×, `research/forum/MINING_20261018.md` line 30): no sampled truth, so the bias does not apply. Nurlanggs (18252) reports readings under two truth sets (16M-path on net 0, and 1e9-path; MINING_20261018.md line 16): exact variance 0.687 → 0.647; exact C_off 0.778 → 0.819; exact d3 + g4 0.610 → 0.508. Two of three fall with the cleaner truth, the direction the correction predicts; C_off moves the other way, and the sets may differ in nets as well as noise. This is not a controlled dose comparison or an external confirmation; we did not re-measure their chains [H]. His PDF measures that oracle's own noise floor, +4.2e-9 (forum 18252, p.23; I.1); he concludes his lever 'is not sample-noise tracking' (p.7).

**Regime caveats (Phase 1 results at 256 × 32, not generalised to 1024 × 16):** Pepper's Strassen loss and dense liveness, pscamillo's finding that k = 3 does not beat a scalar-corrected k = 2, and Henry's 37× mean reset (`research/forum/MINING_20261021_PDFS.md`).

*From §5 (moved verbatim in V31).* Raising the pair-series (Hermite) order not helping agrees with the organizers' remark that the Hermite/diagram expansion is asymptotic in width rather than convergent at fixed width (arXiv:2605.05179, §S.6.2). Published candidates we have not tested: non-tree C_jk·κ3 births, whose removal costs 5.39× in Susupro's full K = 4 (forum 18254), and scale-mode extraction with a carried κ4 core (il.miscusi, forum 18248).

## Appendix J. Meter versus wall: table and mechanism (moved from §7A)

*§7A as it stood in V30 (moved verbatim in V31).* The score meters FLOPs, but the 120 s per-MLP wall cap prices memory traffic: extra exact Winograd levels cut metered FLOPs and add large elementwise add/subtract sweeps, which took 85 % of v106's added backend time on a calibrated local remote-mode clock (G-RB137). Pricing each candidate level in util saved per predicted second turned the cap into a knapsack (G-RB139) that chose v110 (4.21e-9, 102.3 s max wall). We pre-registered max wall ≤ 105 s for nomination (G-RB128). The per-build table, the mechanism, the literature and our exchange rates are in Appendix J (moved there in V30 for length).

The Phase 2 hard cap is 120 s of wall per MLP (zero-prediction fallback beyond it); the score meters FLOPs. Our local ladder measured neither. Metered util (pt) and flopscope ops are fingerprint readings (G-RB118/121/122/124); grader wall per MLP is from the owner-visible ledger (`research/R2_GO_NOGO.md`, G-RB128 and G-RB124).

| build | metered util (pt) | flopscope ops | grader wall mean / max (s) |
|---|---|---|---|
| v98 | 20.55 | 16,545 | 89.5 / 103.3 |
| v99r | 20.55 | 14,841 | 86.1 / 94.2 |
| v105 | 20.32 | 14,863 | 85.7 / 89.4 |
| v106 (v105 + level on site T only) | 20.00 | 15,284 | 102.6 / 113.2 |
| v110 (v105 + levels on F0, K0) | 20.21 | 15,186 | 94.0 / 102.3 |
| v100r | 20.13 | 15,765 | 105.1 / 115.4 |
| v101r | 20.08 | 15,998 | 109.5 / 113.5 |
| v102 | 19.89 | 16,019 | 109.4 / 116.5 |
| v112 (shared old bases, §7B) | 18.98 | 14,395 | 87.2 / 95.6 |

Wall is not linear in op count (v98 has more ops than v100r, less wall). The rise tracks the extra exact Winograd levels, which cut metered FLOPs but add large elementwise add/subtract sweeps (the Winograd transforms and recombination). This was measured with a calibrated local remote-mode clock (G-RB137; it reproduces the grader's v106/v105 and v102/v105 wall ratios to ≈ 0.01, `research/rb137/tab_wall.out`): 85 % of v106's added backend time is add/subtract on strided 10–20 M-element views, 11 % matmul. The grader's TIME BREAKDOWN column agrees: ~94 % backend, ~6 % overhead, for both builds. The cost is bandwidth, not per-op dispatch, and this holds for the grader's remote mode. This is the mechanism the fast-matrix-multiplication literature designs around: Huang et al. (2016) fold the extra additions of multi-level Strassen-like algorithms into the GEMM packing because memory movement limits them (Benson & Ballard 2015, §2.1, show Winograd's 15 additions are optimal for a 7-multiplication 2×2 scheme), Ballard et al. (2016) bound the error of recursive levels (our levels are output-identical to ≈ 3e-15, B.5), and the organizers note that their own wall-clock is dominated by a small fraction of FLOPs, which they attribute to inefficient pure-Python implementation rather than to the meter (arXiv:2605.05179, Appendix I); our measurement attributes ours to add/subtract memory passes on the grader's remote backend (G-RB137). v99r and v100r were graded within the same hour, so their 19 s gap is most likely build-driven (same-hour grading controls for slow drift, not for load; Nurlanggs, forum 18252, reports one file grading clean one day and losing ≈ 10 % of the suite to timeouts the next). We pre-registered max wall ≤ 105 s for nomination (G-RB128): v105, v99r, v98, v110 (102.3 s) and v112 pass; v100r, v101r, v102 and v106 fail. v102 is our best score yet 3.5 s from the cap, and also missed the 0.365 s Mini-10 rule (0.371 s). Nominations and the reasons for them are in B.4. **To organisers:** publish the per-MLP wall ledger with the scoring documents, or state the wall cap next to the FLOP meter.

> **Exchange rates we measured (one shape, one chain; priors, not laws).**
>
> - **Cuts vs expansions.** Our cuts lose ≈ 2 % raw per 1 % util; six expansions buy only 0.4–0.6 % raw per 1 % util (G-RB102, G-RB98; Appendix F.0).
> - **Meter vs wall.** The grader wall costs ≈ 2 ms per glue op removed (1,704 ops cut 3.4 s) but ≈ 40 ms per op of an extra exact Winograd level (421 ops added +16.9 s) (G-RB127/134): the added ops are large add/subtract sweeps (85 % of the added backend time, G-RB137), so the wall cap prices memory passes.
> - **Submissions as probes.** Once local predictions matched grades (graded/predicted median 0.9977 over 17 prospective builds), a submission carried information only where the grader knows more: wall time, memory, billing (v78_p02 timed out locally yet graded failed = 0; G-RB100).

## Appendix K. LLM-use and uncertainty disclosure (moved verbatim from §10 in V31)

Every draft of this document and the submitted code from v21_rb onward were written by Anthropic Claude models (Claude Fable 5.1 and Claude Opus 5.5; Opus for review, claim auditing and the V30 assembly) running as Claude Code agents that I orchestrated; the graded v11_sw (#334046) was built by a Hermes coding agent (kimi-k2.7-code) around a Claude-written Strassen kernel. I set the goals and guardrails (source rule, pre-registration, ship bars), approved or declined each submission, chose which to submit and designate, and wrote none of the code or prose myself. I have not independently re-derived the mathematics: Appendix D.2, the F.0 identities and §7 are agent derivations (D.2's identity and the §7B Gram-solve projection now also have machine checks with falsifiers, Appendix P, likewise written and run by agents); only T1's structural statements (G-RB80) and the F.3 results with failing perturbed variants meet the [proved] bar. Every measurement was run by an agent and most trace to a ledger gate; the adjoint attribution (§2), the −20.2 % corrector figure (§4) and the F.3 checks trace only to `LENS_B_math.md`, `LENS_D_redteam.md` and `research/PROOFS.md`. I re-ran none of them. Adversarial review was by agents (Claude, Ollama Cloud and local open-weight councils), not by me. V16–V30 were each edited by a Claude agent from the previous version (`writeup/V29_CHANGELOG.md`, `writeup/V30_CHANGELOG.md`). For V30, Claude agents audited the inserted drafts (the summary, Appendix P) against their source files twice (`writeup/V30_CLAIM_AUDIT.md`, `V30_REVERIFY.md`; workspace files, not shipped), wrote the Appendix P proofs and checks, assembled this version, and re-ran Appendix E from a fresh unzip (`writeup/V30_REPRO_FINAL.md`, next to the zip). Text written during assembly (the header, abstract and claims rows 8–9, §7B's v117_kd paragraph (now Appendix F.7), §7C, A.1, B.0 items 8–9, B.1, B.4, C.1, I.2's regime caveats, Appendix E, §9 item 5 and this section) was then fact-checked once by an independent Claude agent (`writeup/V30_ASSEMBLY_AUDIT.md`, workspace file, not shipped); its corrections were applied. Three Ollama-cloud model councils (G-RB150: kimi and deepseek, glm timed out; a ~04Z council on the leaders' score histories, which proposed §7C's old-tier damping arm and its consistency note (now Appendix F.7); G-RB156: kimi, deepseek, glm) were used for ideas only, each checked against the ledger; all our own runs were local, and graded scores and wall times are the grader's; the related-work search (Appendix I) was run by a Claude agent, and sources it could not reach are marked UNKNOWN in its log; the toy script of Appendix G was written and run by an agent.

**Uncertain:** the MIX2 corrector is unexplained; T2 is an argument; the adjoint attribution is unreplicated; the σ² seat is an oracle (a lever size, not a construction); the claim that Nurlanggs's 16M-path oracle tables are noise-biased is a hypothesis [H] we did not test (his two truth sets agree in direction for 2 of 3 quantities, nothing more; his PDF, forum 18252 p.23, measures that oracle's own noise floor, +4.2e-9; he concludes his lever 'is not sample-noise tracking', p.7); the constants re-tune on the untruncated chain is untested; [derived] and [argument] items were not machine-checked.

## Appendix P. Proofs behind claims made empirically in the main text

Each result below comes with a numerical check, `writeup/proofs/check_p1_p2.py`, plus a falsifier. A falsifier is a case where the result must NOT hold, so a check that cannot fail does not count as evidence. None of these results is new mathematics. P1 is the delta-method form of the nested-Monte-Carlo bias (cf. Rainforth et al. 2018, Thm 3: for f with bounded second derivative it tightens the MSE bound to O(1/N + 1/M²); the O(1/M) bias step is in its App. D proof). What this appendix adds is the statement of exactly what our §3 and §7B readings rely on, and under which conditions.

### P1. Bias of a sampled-truth oracle reading, and why two-half extrapolation removes it (§3)

**Setting.** An oracle arm replaces a chain quantity by its Monte-Carlo estimate m̂ = (1/N) Σ_k x_k, with x_k i.i.d., mean m and covariance Σ. The reading is R(m̂), where R is the final raw MSE ratio as a function of the injected quantity. The target is R(m), the reading with exact truth.

**Proposition P1.** If R is four times differentiable with bounded fourth derivatives (globally, or with tails controlled so that E|remainder| ≤ C·E|δ|⁴), with Hessian H at m, and x has finite fourth moments, then
  E[R(m̂)] = R(m) + tr(HΣ)/(2N) + O(N⁻²).
For two independent halves of size N/2, the estimate r∞ = 2R(m̂_N) − ½[R(m̂_a) + R(m̂_b)] satisfies E[r∞] = R(m) + O(N⁻²).

**Proof.** Write δ = m̂ − m, so E[δ] = 0 and E[δδᵀ] = Σ/N. Taylor-expand to third order with remainder: R(m̂) = R(m) + ∇Rᵀδ + ½δᵀHδ + (1/6)D³R[δ,δ,δ] + O(|δ|⁴).

- The linear term has zero mean.
- The quadratic term has mean ½ tr(H E[δδᵀ]) = tr(HΣ)/(2N).
- For a mean of i.i.d. terms, E[δ_iδ_jδ_k] = κ3,ijk/N² and E|δ|⁴ = O(N⁻²), so the cubic and remainder terms are O(N⁻²).
Each half has bias tr(HΣ)/N + O(N⁻²). Hence E[r∞] = 2[R(m) + tr(HΣ)/(2N)] − [R(m) + tr(HΣ)/N] + O(N⁻²) = R(m) + O(N⁻²). ∎

**What this licenses in §3.** (a) The uncorrected reading is biased by an amount linear in 1/N. Our 5× dose check is the measured instance: 1.840 and 1.839 against the linear prediction 1.841. (b) A reading near 1 can mean "no lever" or "lever plus noise bias", and only the extrapolated value separates the two. The known-answer control reads 0.305 uncorrected and 0.002 extrapolated. (c) The sign of the bias is the sign of tr(HΣ). For an MSE-type reading near its optimum H is positive semidefinite, so uncorrected oracle tables overstate the remaining error. Read the other way, they understate the lever. This is why G-RB117's σ² 0.776 was an upper bound on the corrected 0.511. [argument: it needs the truth to sit near the minimiser of R, which partial truths need not do (§2-4); for our σ² seat the sign is measured, 0.776 > 0.511.]

**Conditions, and where they could fail.** R must be smooth at the truth. The Hermite read is smooth, but the MIX2 and LITE heads are piecewise linear (ReLU hidden units, `estimator.py` l.1413, l.1539-1540) and the chain clamps variances, so our head-on readings are not C⁴ and P1 applies to them only approximately [argument]. Our evidence that their bias is linear in 1/N is empirical: the dose check at two noise levels (1.840/1.839 vs 1.841). A reading with a kink at the truth (a threshold, |·|, a max) has bias of order N^(−1/2), and the extrapolation does not remove it. The falsifier in the check (R = |m₀|) shows this: its extrapolated residual is 3.3e-2, against an SE of 9.4e-5. The O(N⁻²) term is small only when N is large relative to the curvature. Our only test of that is the dose law, at two noise levels.

**Check.** d = 3, N = 64, 2×10⁵ trials. Bias −1.014e-2 against the predicted −1.016e-2 (SE 4.9e-5; H is indefinite and tr(HΣ) < 0 for this draw, so the predicted bias is negative). Richardson residual −2.4e-5, within SE. The samples are Gaussian, so the cubic term has zero mean and this case exercises only the quadratic part. A second case uses skewed samples (centred exponential, κ3 ≠ 0): its Richardson residual is −5.63e-3, −1.37e-3 and −4.08e-4 at N = 8, 16 and 32 (SEs 5.3e-4, 2.6e-4, 1.3e-4), a log-log slope of −1.89, and the check asserts a slope in (−2.6, −1.5). Its falsifier: with the extrapolation removed (the plain full-N reading, bias ∝ 1/N) the slope assert fails.

### P2. The Gram-solve admission of §7B is an orthogonal projection, with or without orthonormality

**Setting.** After transport, a shared basis Q (n × r, full column rank) is no longer orthonormal. A new leg X (n × k) is admitted as coordinates F = (QᵀQ)⁻¹QᵀX and represented as QF.

**Proposition P2.** QF = P_Q X, where P_Q is the orthogonal projector onto span(Q). The representation error is therefore exactly ‖(I − P_Q)X‖, the part of the leg outside the shared subspace.

**Proof.** P = Q(QᵀQ)⁻¹Qᵀ is symmetric. It is idempotent, since P² = Q(QᵀQ)⁻¹(QᵀQ)(QᵀQ)⁻¹Qᵀ = P. It fixes span(Q), since PQ = Q, and its range is span(Q). A symmetric idempotent matrix is the orthogonal projector onto its range, and QF = PX. ∎

**What this licenses.** §7B states that v112 "drops no content" relative to a per-source basis only up to the outside-subspace residual, and P2 says that residual is the whole approximation. The admission step adds no error of its own, whatever the conditioning of Q. Conditioning enters only through floating point: for cond(Q) ≈ 5e3 at l14, the normal equations lose about 2·log₁₀(5e3) ≈ 7.4 digits. That is why the solves run in f64 (§7B, Limits). The naive admission QQᵀX, correct only for orthonormal Q, is wrong by a relative 6e5 in the check. So P2 is what separates the shipped step from a step that would silently corrupt every admitted leg once transport breaks orthonormality.

**Check.** n = 512, r = 96, cond(Q) = 62. The Gram solve matches the QR-based projection to 3.7e-15.

### P3. The κ4 closure in S-notation: what is an identity, and what is a hypothesis (§6, D.2, D.3)

Checks: `writeup/proofs/check_p3_p4.py` (P3a–P3e). Output: `writeup/proofs/out/check_p3_p4.out`.

**Setting.** S is the three-pairing product that the code evaluates (`submissions/v112_sb/estimator.py`, lines 1387–1391):
  S(A,B)\_ijkl = A_ij B_kl + A_ik B_jl + A_il B_jk,
for symmetric n×n matrices A and B. The block that holds the first index i carries A. The closure sets κ4 ≈ Σ_ab Λ_ab S(B_a,B_b) with a symmetric Λ. The shipped Λ (16 × 3 × 3, `weights.npz`) is symmetric to the bit. ARC's cup (arXiv:2605.05179, Definition S.2.2, read in our local copy `research/lit/arc_2605.05179.txt`) is g(H)\_{i1i2i3i4} = Σ_{u<v} δ_{iu,iv} H_{rest}. The sum runs over the 6 pairs {u,v} ⊂ {1,2,3,4}. The M-cup g_M replaces δ by a matrix M. Linear transport is (T⊙W)\_{abcd} = Σ T_ijkl W_ia W_jb W_kc W_ld (Def. S.2.3), with z = Wᵀh.

**Lemma P3.1 (six pairings).** g(H) = S(δ,H) + S(H,δ). As a closure, this is Σ_ab Λ_ab S(B_a,B_b) with modes {δ, H}, Λ_δH = Λ_Hδ = 1 and Λ_δδ = Λ_HH = 0.

*Proof.* A pair {u,v} and its complement form a perfect matching of {1,2,3,4}. There are three matchings: {12|34}, {13|24} and {14|23}. Each matching yields exactly two of the six pairs, one per block, and each such pair contributes the term with δ on that block and H on the other. So g(H) holds, for each matching, both the term with δ on the block containing index 1 and the term with H on that block. S(δ,H) is by definition the sum over matchings of the first kind of term, and S(H,δ) the sum of the second. ∎

**Lemma P3.2 (transport is exact on the S-form).** S(A,B)⊙W = S(WᵀAW, WᵀBW). Hence g(H)⊙W = g_M(WᵀHW), with M = WᵀW.

*Proof.* Each term A_ij B_kl is a product of two 2-tensors, and ⊙W acts on each index separately: Σ A_ij B_kl W_ia W_jb W_kc W_ld = (WᵀAW)\_ab (WᵀBW)\_cd, and likewise for the other two pairings. Apply this to Lemma P3.1 with δ ↦ WᵀδW = M. ∎

**Lemma P3.3 (the slices the code reads).** Write D_a = diag(B_a). Then
  (4)\_i = 3 Σ Λ_ab D_ai D_bi,  (2,2)\_ij = Σ Λ_ab (D_ai D_bj + 2 B_a,ij B_b,ij),  (3,1)\_ij ≡ κ4_iiij = Σ Λ_ab (2 D_ai B_b,ij + B_a,ij D_bi).
*Proof.* Substitute (i,i,i,i), (i,i,j,j) and (i,i,i,j) into the three pairings. ∎ These are, term for term, `ssc_k4`, `ssc_q22` and `ssc_k31` in the code.

**Proposition P3.4 (when the form is exact).** Let x | ε ~ N(0, C(ε)), with C(ε) = C0 + Σ_a ε_a B_a positive semidefinite almost surely, E ε = 0 and Cov ε = Λ. Then κ4[x] = Σ_ab Λ_ab S(B_a,B_b) exactly.

*Proof.* By Isserlis, E[x_i x_j x_k x_l | ε] = S(C(ε), C(ε))\_ijkl, and E[x xᵀ] = E C(ε) = C0. For a zero-mean x, κ4 = m4 − S(C0,C0). Expand E S(C(ε),C(ε)) with S bilinear: the cross terms in E ε vanish, which leaves S(C0,C0) + Σ_ab E[ε_a ε_b] S(B_a,B_b). ∎ (This is the conditionally Gaussian, "separate-universe" reading of Puffi's closure. It needs Λ to be PSD to be realised by a distribution.)

**Hypothesis H-FT (free transport). This is not a theorem, and we do not prove it.** At every z-layer 1–14, the (4), (2,2) and (3,1) slices of κ4[z] that the next step reads are well approximated by Σ_ab Λ_ab S(B_a,B_b), under four conditions:

1. The modes are B ∈ {diag(M), Σ_z, Q_free}, each built from quantities the chain already transports, plus n² matvecs (D.3).
2. One fitted Λ_l per layer, fitted on own nets 9000/9001, transfers to other nets.
3. The neglected parts are small, or are absorbed into Λ_l and the head: the conditional non-Gaussianity that P3.4 excludes, the off-diagonal part of M, and the modes that need their own n³ transport (C∘C, B4, the exact D_m K term).
4. At layer 15 only the (4) slice is used, and it involves only diagonals.

The evidence for H-FT is empirical and is the evidence of §6: the v58_ne OFF/ON ablation (1.0327 raw, 17/20 nets) and the G-RB34 rungs. P3 adds nothing to that evidence.

**What this licenses.**

- (a) D.2's "same form" claim is an exact identity (P3.1), with one tightening: "Λ_IH = 1" has to mean both off-diagonal entries. With Λ_IH = 1 and Λ_HI = 0 the tensor is S(I,H) alone, which is not index-symmetric and so is not a fourth cumulant (falsifier P3a: asymmetry 7.25).
- (b) The modes {I, H} live on the h side. After the linear step, ARC's object has modes {M, WᵀHW} with M = WᵀW dense (P3.2). Keeping δ instead of M is wrong by a relative 0.77 (falsifier P3b).
- (c) Our I mode, diag(m_i) = diag(M), is a third object, equal to neither δ nor M. It is exact on the (4) slice and on every D-term. It drops the off-diagonal entries of M in the 2B_a,ijB_b,ij term of (2,2) and the B_a,ijD_bi term of (3,1). At n = 1024 on a real layer, ‖offdiag M‖_F/‖M‖_F = 0.706, and the spectrum of M spans [0, 7.89] against diag ≈ 2. This approximation is not small. It is one of the things the fitted Λ and the head must absorb, and H-FT states it as an assumption, not a negligible error.
- (d) The three slice expressions in the code (`ssc_k4`, `ssc_q22`, `ssc_k31`) are exactly κ4_iiii, κ4_iijj and κ4_iiij of a symmetric S-form (P3.3, check P3c). P3c does not trace their consumers (the 1/24, 1/4 and 1/6 Edgeworth factors and the orientation in which `ssc_k31` is read downstream); that wiring is covered only by the port checks of §6.

**Conditions, and where they could fail.**

- P3.4 needs a PSD Λ. The shipped Λ is indefinite on 8 of the 14 fitted layers (1, 7, 9–14). Its negative eigenvalues are small (minimum −7.9e-3, against leading eigenvalues 87–2.6e4, so it is close to rank one), but no conditionally Gaussian mixture realises it exactly. For those layers the form is a fitted ansatz with no generative model behind it.
- P3.4 also needs conditional Gaussianity. A uniform conditional gives a κ4 that the form misses by a relative 166 (falsifier P3d).
- §6's sentence "Transport is factored, S(B_a,B_b) → S(WᵀB_aW, WᵀB_bW)" describes the full SSC (G-RB33) exactly. Of the free build's modes, only C = Σ_z = WᵀΣ_hW is a transported mode in that sense. I is the diagonal of a transported δ, and Q_free is rebuilt at z from the transported T_z, μ_z and two matvecs. It is not the transport of an h-side mode.
- Lemmas P3.1–P3.3 are independent of the 1/(n+4) normalisation of H, which sits inside H.

**Check.**

- P3a, n = 7, full n⁴ tensors: max|g(H) − [S(δ,H) + S(H,δ)]| = 3.6e-15. Dropping any one of the six pairings errs by at least 3.83.
- P3b, n = 6: transport identities to 5.7e-14.
- P3c: code slices against brute force with the shipped Λ of layer 5, relative errors 2.1e-19 for (4), 1.1e-16 for (2,2) and 1.7e-18 for (3,1). Setting the (2,2) factor to 1 instead of 2 errs by 0.50.
- P3d: an exact finite mixture (no Monte Carlo) matches the form to 6.9e-14.

### P4. Transport cost in a factored chain: Θ(L²) per source, Θ(wL) with an age window; v112 makes the old-tier *transport* Θ(L) but not the old tier (§7, §7B)

Checks: `check_p3_p4.py` (P4a toy, P4b real code). The real-code shapes come from `writeup/proofs/count_sites.py`, which wraps `sw_matmul` in one real predict per build (n = 1024, depth 16, net 0, run through `bg.sh`). Its metered totals reproduce §7B: 20.2051 pt (v110_fk) and 18.9772 pt (v112_sb).

**Cost model.** One unit is one dense n×n×n product. A (p×q)(q×r) product costs pqr/n³ units, whether or not it is computed by Strassen–Winograd. Strassen changes the constant per site, not the exponent in L. The model does not count three things:

- the O(n²) elementwise work, including the per-source Hadamard read, which is itself Θ(L²n²);
- thin products, i.e. legs of width O(1);
- the pruning of the transport's inner dimension, which is data-dependent and at most n.

A source born after layer s is transported and read at layers s+1, …, L−1. Its age at layer l is l − s. A source with per-source dense legs costs c_y units per (source, layer) pair: c_y = 4 = 2 transports + 2 contractions (T1, §7). In the code the newest source's P = I transport is free.

**Proposition P4.**

1. *Per source, no window.* The total is c_y · #pairs = c_y · L(L−1)/2 + O(L) = Θ(L²).
2. *Window w (sources older than w leave the young tier).* Per layer there are at most w young pairs, so the young total is c_y Σ_l min(l, w) = c_y(wL − O(w²)) = Θ(wL).
3. *Old tier on G shared transported bases of ranks r_G, with per-source static coefficients F_b (r × 2n).* Per layer, the old tier costs
   - (2/n) Σ_G r_G for the transport WᵀQ_G and one trailing contraction per group, and
   - (4/n) Σ_{old b} r_{G(b)} for each old source's in-basis formation F (Qz F_b) and contraction K ([LP|LA] F_bᵀ).

   Summed over layers, the shared terms are at most 2GrL/n = Θ(L). The per-source F/K terms are (4r/n) · #old pairs = Θ(rL²/n).

4. *Per-source old bases (v110).* Each old source carries its own transport and trailing contraction, so the old tier costs (6/n) Σ_{old b} r_{G(b)} per layer, which is Θ(rL²/n).

*Proof.* Each item is a sum over layers of a per-layer count. At layer l there are l live sources. min(l, w) of them are young and l − w are old (for l > w). The per-pair costs are read off the product shapes: a transport n×n·n×n and a contraction n×n·n×n for each dense leg; an n×r·r×2n formation and an n×2n·2n×r in-basis contraction (2r/n units each) for each old source; and one n×n·n×r transport plus one n×r·r×n contraction (r/n each) for each shared basis. The sums Σ_{l<L} l = Θ(L²) and Σ_{l<L} min(l, w) = Θ(wL) are elementary. ∎

**Lemma P4.5 (sharing is algebraically free).** If old legs are P_b = Q F_Pb and A_b = Q F_Ab, then transport and ageing by a gate (a row scaling, diag(φ)) act on Q alone, and Σ_b (LP_b Pz_bᵀ + LA_b Az_bᵀ) = (Σ_b [LP_b | LA_b][F_Pb ; F_Ab]ᵀ) Qzᵀ.
*Proof.* Wᵀ diag(φ) Q F = (Wᵀ diag(φ) Q) F, and the matrix product distributes over the sum over b. ∎ Together with P2, the only approximation in v112's old tier is the admission residual.

**What this licenses.**

- (a) The per-source design pays Θ(L²). The age window is what makes the young tier Θ(wL) (§7's 4 products per young source-layer give 60 young pairs × 4 at depth 16).
- (b) **v112 does not make the old tier Θ(L).** It makes the old-tier *transport and trailing contraction* Θ(L). The per-source in-basis F and K products remain, because the read stack needs each old source's dense Pz_b and Az_b. Per old pair, v112 costs 4r/n against v110's 6r/n, a one-third cut of that term. In the real code at depth 16:
  - The old tier's shared-able volume falls from 24.54 to 9.42 units.
  - The F+K volume is 55.00 units in both builds.
  - So 85 % of v112's old-tier product volume (55.0 of 64.4 units) still scales with the number of old sources.
  - The F+K volume grows from 3.88 units at l8 to 9.12 at l14, so the claim "the v112 old tier is Θ(L) in products" is refuted by the run's own shapes (a check, not a falsifier).
- (c) §7B's metered saving, attributed from the flopscope op log of the two real runs [measured; the attribution closes to the total, 1.2279 pt]:
  - matmul inside the large-product sites: T (transport) 0.370, C (trailing contraction) 0.329, E1a + E1b (the entry sketches, one per old-tier entry, so Θ(L) events) 0.440, for 1.139 pt;
  - Strassen add/subtract glue inside those sites: 0.091 pt;
  - matmul and einsum outside the sites (thin and entry products v110 had, net of v112's Gram einsums and M21): 0.111 pt;
  - qr 0.385 and eigh 0.162, for 0.547 pt (V29: 0.55);
  - minus the f64 Gram solves, 0.661 pt (V29: 0.66).

  So the gross saving is 1.25 (matmul/einsum) + 0.09 (glue) + 0.55 (qr/eigh) = 1.89 pt, less 0.66 for the solves. V29 §7B writes "gross 1.78 pt (matmul 1.23 plus qr/eigh 0.55) less the solves", which does not close (1.78 − 0.66 = 1.12, not 1.23): it leaves out the 0.09 pt of Strassen glue, and its matmul figure (1.23) is below the measured 1.25. None of the saving comes from the F or K sites, whose metered cost is identical in the two builds.

  - A further Θ(L) old tier would need a read that never forms a per-source dense n×n leg. v112 does not have one.

**Conditions, and where they could fail.**

- Ages are counted by the code's rule. Sources are born after layers 0–14, first transported at s+1, young for ages ≤ 5, in the 384 group at ages 6–7 and in the 224 group at ages ≥ 8. The per-layer group sizes predicted from that rule match the transport and contraction widths of both real runs exactly.
- Labels. The code has 15 sources, born after layers 0–14; at layer 15 it reads all 15, diagonal only. V29's 105 pairs is the code's pair count over layers 1–14, and its 60 young pairs match too. V29's own label ("born at z-layer s ∈ {1…14}, read at s+1…15") describes a different set of pairs that happens to have the same size; the counts in §1.1 are right, the label is not the code's.
- The real estimator runs its source machinery only at n = 1024 and depth 16 (`use_stack = n == _CAL_WIDTH and depth == _CAL_DEPTH`, with `_CAL_WIDTH, _CAL_DEPTH = 1024, 16`; v117_kd `estimator.py` lines 88 and 1100–1102), so L cannot be varied in the real code. Exponents in L are tested on the toy chain. The real code supplies the constants and the per-layer growth in l: the cost through layer l of a depth-16 chain equals that of a depth-(l+1) chain except for the last-layer read, which reads only the diagonal (no K site, no C site at layer 15).
- The model counts products, not wall time. §7A shows that wall time is priced by memory traffic.

**Check.**

- *P4a (toy, n = 32, w = 5, r = n/4, a counting matmul).* Counted units equal the closed forms exactly at L = 8, 16, 32, 64 and 128, for all three policies:
  - per source, 2(L−1)(L−2): 32004 at L = 128;
  - window: 2480;
  - v112 structure: 9921.5 = 2480 young + 60.5 shared-basis terms + 7381 F/K.

  Log-log slopes over L = 32–128 are 2.05 (per source), 1.07 (window) and 1.73 (v112 structure, which tends to 2). The shared-basis read equals the per-source read to 3.7e-16 (P4.5). Falsifiers:

  - the per-source per-layer count is not flat in l (0 to 248 units);
  - per-source totals do not fit a line (relative residual 0.14);
  - the window closed form misfits the per-source counts by up to 228 units per layer.
- *P4b (real code).* F and K volume per layer equals 2(384·m384 + 224·m224)/n in both builds. The transport rows and contraction widths match the schedule: v110 adds r_b per old source, v112 adds one r_G per present group. The old-tier width read from v112's transport shapes takes only the values 0, 384 and 608 (at most one 384 and one 224 basis); falsifier: v110's grows to 2560 columns at l14. The metered v110 − v112 difference is attributed by site and op, and the attribution closes to the total (1.2279 pt).

*Note.* P4 is corrected. Shared bases make only the old-tier transport and trailing contraction Θ(L). The in-basis formation F and contraction K stay per-source, Θ(rL²/n), and are 85 % of v112's old-tier volume.

### V29 errata found by this appendix (fixed in place in V30; old → new text in `writeup/V30_CHANGELOG.md`)

1. §7B arithmetic: "gross 1.78 pt ... less the solves" does not close (1.78 − 0.66 = 1.12). Measured: 1.25 matmul/einsum + 0.09 Strassen glue + 0.55 qr/eigh = 1.89, less 0.66 solves = 1.23 (plus 0.002 of other ops; total 1.2279).
2. D.2 "Λ_IH = 1" should read Λ_IH = Λ_HI = 1. A single off-diagonal entry is not index-symmetric, so it is not a fourth cumulant.
3. D.2/D.3: after the linear step ARC's I mode becomes the dense M = WᵀW. Ours is diag(M), a third object (off-diag(M) is 0.706 of ‖M‖_F at n = 1024).
4. The shipped Λ is indefinite on 8 of 14 layers (min eig −7.9e-3), outside the exact Gaussian-scale-mixture case of P3.
5. §6's "transport is factored, S(B_a,B_b) → S(WᵀB_aW, WᵀB_bW)" describes the full Puffi closure. In our free build only C = Σ_z is transported; I is a diagonal and Q_free is rebuilt at z.
6. §1.1 source labels: the code births sources after layers 0-14. The pair counts (105 pairs, 60 young) are right.
7. §7B "not a projection" is wrong: the Gram solve is the orthogonal projection onto span(Q) (P2); what it avoids is orthonormalising Q. → "a Gram solve F = (QᵀQ)⁻¹Qᵀ[P|A], whose image QF is the orthogonal projection of [P|A] onto span(Q), computed without re-orthonormalising (Q is no longer orthonormal after transport)".
8. §1A (l.108) and §3 (l.150) cite Rainforth et al. 2018 Thm 1 for the bias; the relevant result is Thm 3 (bounded-second-derivative case; the bias step is in App. D).
9. §3 (l.150) "the reading is a quadratic function of the sampled mean, so its bias is exactly linear in 1/N" → "the reading is a nonlinear, piecewise-smooth function of the sampled mean; its bias is linear in 1/N at leading order (Appendix P1), which the dose check confirms at our N".
