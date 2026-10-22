# LENS D — red-team of our own implementation and measurements (v57_azs ≡ v55_y2q3, graded 5.23e-9)

2026-10-09, adversarial-review agent (lens D). Premise tested: "there is a BUG or a wrong measurement in our pipeline costing a large factor."
Instruments (all in `scratchpad/lensD/`, nothing deleted, no TEST net touched, no submit): `probe.py` (in-process predict, all 16 rows saved,
raw MSE in f64 AND grader-style f32; `probe.jsonl`), `firstcall.py` (per-op bill diff first vs second predict in one process), three one-knob
mutants of v57_azs (`est_lcout`, `est_om2`, `est_noeig`), `opledger_v57.json` (flopscope op ledger, net 0), `analyze.py` (paired ratios).
Runs: one heavy process at a time, `ulimit -v 16000000`, `OMP_NUM_THREADS=8`, `nice 19`, waits for load ≤ 16, ≤ 4 nets per python process
(flopscope's session op-log growth, G-RB34b). Host load during the probes 9–45 (other agents), so residual times here are NOT grader-representative.

**Verdict in one line: no bug and no wrong measurement that costs a large factor was found. The pipeline's numbers reproduce; the one place a
large factor exists is the 0.400 s residual cliff (×10^5 per failed net), where the shipped chain sits at a 1.15–1.25× margin.** Details, with
evidence, impact and confidence, below; §8 lists what was NOT tested.

**Top 3 (the only items with a non-zero expected effect):**
1. **§5 — old-tier entry does 0.68 pt of work that buys nothing**: the oversampling + eigh + rotation after the QR range finder (estimator.py:893–911).
   One-knob mutant `est_noeig`: util 0.23635 → 0.22816, raw +0.1 % on VALID-8 / +0.9 % on FIT-3 ⇒ **adjusted ≈ 0.967 (−3.3 %)**, ops −70, VmPeak unchanged.
   Clears the ladder's screen/VALID bars; needs VALID-20 + subprocess Mini-10 (residual letter) before shipping. Plus −0.11 pt (output-identical) from spelling
   the nested-entry Gram `FPA0 @ FPA0.T` as the 0.5×-billed self-Gram einsum, and ≈ −0.09 pt from dropping the E-site zero pad once r = 384. ≈ −4 % adjusted total.
2. **§7 — the residual cliff is the only large-factor exposure** (a zeroed net costs 3·10^6× our score); margins 1.14–1.26× on a quiet host after the
   depth-5 ratchets. Keep the low-residual hedge designated; stop trading residual for FLOPs.
3. **§3 — the corrector is real, out of sample**: −20.2 % raw on VALID-20, 20/20 nets, in-sample gain smaller than out-of-sample; feeding it forward carries
   70 % of that gain. Everything else checked (prototype parity, f32, truth/MSE formula, ledger consumption, constants) came back clean to ≤ 0.1 %.

## 1. f64 prototype vs shipped flopscope estimator (lens 1) — PARITY up to sketch randomness; no systematic mismatch

Instrument: prototype free run `research/rebuild/lc_cache/free_sscf_00010.npz` (`srcchain_aug.py`, AUG=ssc FREE, uncorrected, net 10 = VALID) vs the port
run at f64 with the corrector removed (`probe.py submissions/v57_azs nolc64 --nolc --f64 10`, `out_nolc64_00010.npy`), compared on ALL 16 carried layer means
(the mean of every layer depends on every carried quantity upstream, so a layer-by-layer mean comparison is a necessary-and-sufficient parity check for the
output; carried Σ/T were not dumped — see §8).

| layer | proto MSE | port f64 MSE | rms(proto − port) / rms(err) | max\|proto − port\| |
|---|---|---|---|---|
| 0 | 7.134e-10 | 7.134e-10 | 2.9e-9 | 8e-14 |
| 1 | 6.567e-10 | 6.564e-10 | 5.8e-3 | 7e-7 |
| 2 | 9.250e-10 | 9.269e-10 | 4.0e-2 | 6e-6 |
| 4 | 2.622e-9 | 2.645e-9 | 6.6e-2 | 1.3e-5 |
| 8 | 8.276e-9 | 8.321e-9 | 9.6e-2 | 4.2e-5 |
| 12 | 1.837e-8 | 1.844e-8 | 1.05e-1 | 5.7e-5 |
| 15 | 3.401e-8 | 3.426e-8 | 9.2e-2 | 7.0e-5 |

- Layer 0 identical to 1e-9 relative (exact Gaussian layer: confirms weights, truth and MSE plumbing agree). Layer 1 differs by 0.6 % of the error — the only
  stochastic object alive there is the layer-0 birth's adjustment-residual range finder. The deviation jumps to 4 % at layer 2, where the first D21
  rank-4 sketch enters, and saturates at ≈ 9–10 % of the error rms from layer 7 on. Final MSE differs by +0.74 % (3.426 vs 3.401e-8).
- Mechanism, CONFIRMED by a control: the port's range-finder test matrix is `w[:, :12]` / `w[:, :392]` (DESIGN S3: "Ω = columns of W_l"), the
  prototype's is a seeded Gaussian (`srcchain.RF`). Mutant `est_om2` (same port, Ω = `w[:, 12:24]` and the LAST 392 columns) reproduces the SAME deviation
  profile against the shipped port on net 10 — rms(om2 − base)/rms(err) = 0.006 / 0.042 / 0.070 / 0.112 / 0.119 / 0.117 at layers 1 / 2 / 4 / 8 / 12 / 15 —
  and its final MSE moves by −1.3…+3.1 % per net (FIT 0/2/4 pooled 0.997, VALID 10/11/13/16 pooled 1.004). So the prototype–port residual IS the rank-4
  sketch's randomness (≈ 0.1² ≈ 1 % of MSE, net-to-net sd ≈ 2 %), not a port defect; consistent with ERROR_BUDGET's "sketch is not a loss" row.
  Corollary for the gates: any two candidates that differ in Ω or in sketch rank differ by ±2 % per net from the sketch alone — a 3-net FIT screen at the
  0.985 bar is inside that noise; the paired VALID-20 is the smallest set that resolves 1 %.
- The corrector's 21 input columns (`lever46/lcx_port_v51_sscf_10.npz` vs `lcfeat.feats` on the prototype's free run): rms rel. deviation ≤ 0.1 % for the 13
  Gaussian/Σ columns, 0.3–1.5 % for the κ3-derived ones (skew, corr_marg, trs_z, trq_z, k3, ts_h), correlation ≥ 0.9998 on every column at layers 4/8/12/14
  (re-measured here; the G-RB34b "within 5 %" statement was conservative). Feature order / folding verified line-by-line against `lc/export_v42.py` RAW
  and `lcfeat.NAMES` (estimator.py:788–813 vs lcfeat.py:17–21); `g` and `layer` bias folding matches the TF caches' columns 9/10 exactly (`tf_sscf_00000.npz`).
- SSC port vs prototype: `qc[l-1]` / `lam[l]` indexing, `Q_free` basis, `/vbar`, zero-diagonal projection, the (2,2)/(3,1) sector formulas and `mbar = mean(m1c)`
  BEFORE the hook all match `srcchain_aug.py:188–250, 378–408` (estimator.py:629–655, 776–778). lam[0] = 0 (lean g_0 path at layer 0), lam[15] has zero Q rows.
- Hook point: prototype calls `lc_hook` AFTER Σ_h/T_h and BEFORE aging/birth and carries the corrected mean into the next layer (srcchain_aug.py:420–423);
  the port does the same (`mu = mu_carry`, estimator.py:819; Sig/Tn/birth use the uncorrected `m1c`). Consistent.

**Impact on adjusted score: 0 (no mismatch to fix).** Confidence HIGH (direct measurement of all 16 carried means + the Ω-swap control).

## 2. Numerical precision (lens 6) — f32 costs nothing measurable; no stage needs f64

Same algorithm, same Strassen depths (T/C/M d=5, F/K d=4/5, E d=2/3), `_DTYPE` f32 vs f64, net 10:

| | raw MSE f32 | raw MSE f64 | ratio |
|---|---|---|---|
| without corrector | 3.42586e-8 | 3.42611e-8 | 0.99993 |
| with corrector (shipped) | 2.37598e-8 | 2.37877e-8 | 0.99883 |

Per-layer f32-vs-f64 deviation of the carried means is 0.3–0.9 % of the error rms at every layer (col. "rms(port32 − port64)/rms(err)" in the probe), i.e.
f32 + depth-5 Strassen-Winograd adds ≈ 1e-5 of MSE. f32 is even 0.1 % "better" (noise). **Stage-wise precision swaps were therefore not run: the whole-chain
swap bounds every stage at ≤ 0.12 %.** The cumulant updates (`kh = m3c − 3 m2c m1c + 2 m1c³`, `vh = m2c − m1c²`, `D21 = Tz − diag`) do not cancel
catastrophically at these magnitudes. (f64 doubles the bill — util 0.4727 — so there is no trade here.)

**Impact: 0.** Confidence HIGH (direct measurement, two configurations, one net; the effect is 100× below anything that matters).

## 3. Does the learned corrector help OUT of sample? (lens 3) — YES, −20.2 % raw on VALID-20, 20/20 nets; in-loop feeding is the right choice

In-process f32, v57_azs with and without `lc_weights.npz` (`e._lc = None`), and the mutant `est_lcout` (corrector added to the OUTPUT rows only, the
uncorrected mean carried forward), paired per net (`analyze.py`):

| variant | VALID-20 pooled raw / shipped | per-net range | nets worse | FIT 0/2/4 pooled |
|---|---|---|---|---|
| no corrector | **1.2536** | 1.075–1.442 (sd 0.116) | 20/20 | 1.2152 (0:1.132 2:1.348 4:1.158) |
| corrector on outputs only, NOT fed forward | 1.1963 | 1.039–1.382 | 20/20 | 1.1690 |

- Out of sample the corrector is worth −20.2 % raw (VALID was never used to fit the head; only for the TF-loss checkpoint and the `_LC_SCALE` scan);
  the in-sample FIT gain (−17.7 %) is SMALLER than the out-of-sample one — no overfit signature. Per-layer the no-corrector ratio is 1.00 at layers 0–3
  (`_LC_L0 = 4`), 1.07 at layer 4, rising monotonically to 1.25 at layer 15: the corrector acts cumulatively through the carried mean.
- Feeding the corrected mean forward (the shipped design, estimator.py:819) carries ≈ 70 % of the gain: output-only correction recovers 1.2536 → 1.1963
  only. The prototype hook has the same semantics (srcchain_aug.py:420–423), so the TF-fit → free-run application is consistent and beneficial.
- Fit-set overlap, for the record: `research/lc/split.json` FIT = 60 nets incl. 0,2,4,5,6,7,8,9; the official Mini-10 (nets 0–9) is therefore **8/10 FIT**
  (nets 1 and 3 are TEST). The team discloses this (G-RB34b). The graded public score (5.23e-9, nets unknown to us) is below the Mini-10 (5.389e-9), so the
  public set is not visibly inflated by in-sample nets; the Private Re-evaluation set is out-of-sample by construction and VALID is the right proxy.
- `_LC_SCALE = 1.2` was chosen on VALID (G-RB5), so the VALID number above is optimistic by at most the scale-scan curvature (1.0 → 1.2 was −0.7 %).

**Impact: the corrector is worth −20 % raw out of sample (≈ −20 % adjusted); removing or distrusting it would COST a factor 1.25.** Confidence HIGH
(20 paired VALID nets, zero sign flips, in-sample gain ≤ out-of-sample gain).

## 4. Truth references and the MSE formula vs the grader (lens 4) — IDENTICAL to ≤ 1e-7 relative

- Grader (`whestbench/src/whestbench/scoring.py:438, 819`): `pred = asarray(predictions, float32)`; `mse = mean((pred[-1] − final_target)**2)` with
  `final_target = asarray(row["final_means"], float32)`; per-MLP score `mse × max(0.1, C/B)`, arithmetic mean over MLPs. Truth sampler
  (`simulation.py:115–144`): x ~ N(0,1) in **float32**, forward `maximum(matmul(x, w), 0)` in float32, sums accumulated in float64, means cast to float32.
- Ours: `research/lc/data/truth_*.npz` are the same parquet rows (`meta.json` → `mini-00000-of-00007.parquet`), stored as float64 up-casts of the baked
  means; `cmp.py` / `ladder.py` compute the MSE in float64 on `all_layer_means[-1]`. Measured gap grader-style-f32 vs our f64 on 30 probe rows:
  **max 8.7e-8 relative** (`raw_f32grader` vs `raw` in `probe.jsonl`). Layer: our row 15 is E[h_16] after the 16th ReLU = the grader's `final_means`
  (layer-0 MSE of the exact Gaussian layer = 6.9e-10 = var_h0 / 1e9: confirms the truth's sample count and that row indices line up).
- Truth noise floor: var_h15 / N = 0.0787 / 1e9 = 7.9e-11 = 0.35 % of our 2.25e-8 (G-RB48 independently found no systematic floor). Not a lever.
- The f32 forward of the truth vs our f64-modelled network: per-sample rounding ~2e-6 is unbiased noise averaged over 1e9 draws; bias ≪ 1e-7 abs ⇒ < 1e-14 in MSE.

**Impact: 0.** Confidence HIGH.

## 5. The FLOP ledger of v57_azs (lens 2) — no unconsumed work; two priced trims, one of them being tested

`opledger_v57.json` (net 0, first predict in a fresh process): util **23.635 %**, 14 323 ops, 946 distinct (op, shape) rows. By op: matmul 20.33 pt,
add 0.58, subtract 0.56, concatenate 0.48, qr 0.44, eigh 0.43, einsum 0.41, multiply 0.21, **reshape 0.17**, everything else < 0.02.

| item | pt | status |
|---|---|---|
| T site (merged transport, d5): rows (2k−1)n + Σr + n, up to 12 800 × n × n | ≈ 6.4 | needed (every leg is Hadamard-consumed) |
| C site (merged contraction, d5) | ≈ 6.6 | needed |
| Σ_z as two d5 products (Σ_h w rides T; M2) | ≈ 1.0 | cheaper than the 0.75×-discounted einsum (1.5) — correct choice |
| F/K sites (old sources' dense Pz/Az formation + in-basis contraction) | ≈ 2.5 | needed in this representation (eq-16 Hadamards need entrywise legs) |
| **old-tier ENTRY (10 entries): E1a/E1b n×n×416 d2 (0.606) + E2 416×n×2n d3 (0.529) + qr(n,392) 0.250 + eigh(392) 0.247 + Vᵀ-rotations (384,392)@(392,n) ×20 0.280 + S self-Grams 0.143** | **2.06 (8.7 % of the bill)** | **FINDING (the one actionable item): the oversampling + eigh + rotation (0.68 pt) only re-orient a 392-dim sketch into its 384 leading directions and buy NO accuracy.** Mutant `est_noeig` (estimator.py:893–911 → `Om2 = w[:, :384]`, `Qb = Q1`, `FP, FA = QP, QA`; no S / eigh / rotation): **raw VALID-8 (10,11,13,16,18,20,27,28) pooled 1.0013 (0.993–1.009, 2/8 better), FIT 0/2/4 1.0092; util 0.22816 vs 0.23635 = −0.82 pt; adjusted 0.9666 on VALID / 0.9742 on FIT**; ops −70, in-process VmPeak 6020 vs 6036 (no new buffers; the E sites are unchanged), residual not grader-measured here. Both screens clear the ladder's 0.985 / 0.98 bars; the sketch-noise floor of §1 (±2 % per net) means the raw-neutrality should be read off the paired VALID-20 (8 of 20 run). Follow-on, same spirit: with r = 384 = 12·32 the `_E_PAD` 416 zero-pad is no longer needed (E sites at 384 width: a further ≈ −0.09 pt). The two n×n×392 sketch products P0(P0ᵀΩ) are a 1-power sketch; a 0-power Y = P0Ω would halve E1 (−0.3 pt) at an unmeasured accuracy price. |
| nested-tier entry (8): qr(n,384) 0.19 + eigh(384) 0.19 + `FPA0 @ FPA0.T` (384,2048)@(2048,384) 0.22 | 0.60 | the Gram is spelled as `matmul`; flopscope bills a self-Gram `einsum("ik,jk->ij", X, X)` at 0.5× (OPERATING_MODEL lesson, 2026-09-28) → **−0.11 pt for free, output-identical** |
| Strassen operand copies (`concatenate` of the 3 plain quadrants per level) + Winograd adds/subs | 0.46 + 1.14 | the price of batching 7^d leaves into one matmul (residual-bound); already measured optimal at d5 vs d4 (G-RB52 v57_t4 +3.5 %) |
| `reshape` of the arena views | 0.168 | **billed once per process** — confirmed op-by-op by `firstcall.py` (two predicts of net 0 in one process: 519 747 002 148 vs 516 054 392 612 FLOPs; the +3.693e9 = 0.1679 pt is 100 % `reshape` rows of the flat arenas, e.g. `reshape((215129600,))` ×4 = 8.6e8, `reshape((122931200,))` ×4 = 4.9e8 …; flopscope registry: "reshape costs numel(input), billed regardless of whether numpy returns a view"). Only the first MLP of a worker pays it (same +0.17 pt on MLP 0 in the Mini-10 JSON). Harmless while the grader keeps one worker per run (whestbench's `SubprocessRunner` does); the `_rel` variants re-pay it on every net (+0.7 % adj) — already known (G-RB52). If a future grader ran one worker per MLP, every net would pay +0.7 %: the fix would be per-role buffers allocated in their final shape (`fnp.empty` is free) at the price of the arena aliasing (memory). |
| last-layer transports for the (3)-diagonal only | ≈ 1.15 | unavoidable: κ3(z_i,z_i,z_i) = Σ_j Σ_blocks α (Pz∘Xz∘Yz)_ij needs every transported leg entrywise |
| closure, marginals, corrector, SSC sectors, range finders, thin legs | < 1.0 total | O(n²) per layer; nothing recomputed that is cached elsewhere |

Checked and found CORRECT (no waste): the newest young source's P = I is never transported (Pz = wᵀ, G-RB17); Σ_h w is computed once (rides T) and reused for
var_pre and Σ_z; `Qf`, `m_i`, `oz` are n² per layer; Hermite order `_KH = 4` is converged (G-RB24); `_zbuf`/`_fill` zero padding is never taken (tot == S_);
no per-layer recomputation of static coefficient blocks (F_P/F_A, c1..c5 are born once).

**Impact: −0.82 pt util at raw +0.1 % (VALID-8) ⇒ adjusted ≈ 0.967 (−3.3 %) from `noeig`; a further −0.11 pt (−0.5 %, output-identical) from the Gram
spelling; ≈ −0.09 pt from dropping the E-site zero pad.** Confidence HIGH on the ledger and util numbers (metered); MEDIUM-HIGH on raw-neutrality (8 VALID +
3 FIT nets, worst per-net +1.2 %, inside the ±2 % sketch noise) — the ladder's VALID-20 → Mini-10 rungs are the proper confirmation before shipping.

## 6. Were the truncation constants tuned on the corrected or the uncorrected chain? (lens 5)

- ERROR_BUDGET §1 (f64 `ablate.py`) ranks every cost approximation on the UNCORRECTED chain; the port screens (ERROR_BUDGET §2, BUDGET_V41 §2, G-RB24,
  G-RB35) re-rank the same knobs WITH the shipped corrector on FIT 0/2/4 → VALID-20. Two findings follow from the team's own tables: (i) the port's raw gains
  are ≈ 2× the prototype's for the same knob (age 6: −5.1 % vs −2.4 %) because the corrector was fit on the age-5 chain and partially "corrects" the age-5
  truncation; (ii) every constant was re-screened on the v51 chain with the refit head (G-RB35: RK 3/2, AGE_OLD2 7/9, R_OLD2 192/256, KH 6/3, LC_SCALE
  1.0/1.4 — all KILL/no-gain). So the constants ARE tuned on the corrected chain, but the corrector was NOT refit per constant setting (only for g × 0.92 and
  for the SSC chain). A joint re-tune (constant + head refit) costs ≈ 1 h per setting (`run_src92.sh` protocol) and is bounded above by ERROR_BUDGET's
  "every cost approximation together ≈ 3–4 % raw" — i.e. ≤ 4 % adjusted even if free. Not a large factor; not run here.

**Impact: ≤ 4 % upper bound; expected ≈ 1–2 %.** Confidence MEDIUM (inference from existing tables, no new run).

## 7. The one real large-factor exposure: the 0.400 s residual cliff (measurement, not FLOPs)

A net whose residual wall time exceeds 0.400 s is zeroed (MSE ≈ 1.5 at multiplier 1.0): one such net in 100 adds ≈ 1.5e-2 to the mean adjusted score —
**3 × 10^6 × our 5.23e-9**. Shipped margins (`ladder/v57_azs_rel_vs_v55_y2q3.json`, quiet host load 2.8–4.2): v55/v57_azs median residual 0.318–0.325 s,
worst 0.325–0.351 s (ratio to the cliff 1.14–1.26×); G-RB50 re-timed v55 at 0.358 worst on a quiet host; the `_rel` variant 0.358/0.351. Every ratchet since
v46 bought FLOPs with residual (depth-5 Strassen on small products, G-RB40/41/42). The team's hedge is the designated #2 (`v46_y5c`, worst 0.289 s). The
grader's host speed and co-tenancy are not under our control; the public grading of #334949 passed once.

**Impact: binary; probability unknown to us (the only item in this review whose expected cost could exceed every accuracy lever combined).** Recommendation:
keep the low-residual hedge designated; do not spend the remaining residual margin on further FLOP ratchets; if a re-grade is possible, prefer the variant
with the larger residual margin at equal FLOPs.

## 8. Not tested (scope limits of this review)

- Carried Σ_z / Tz / κ4 of prototype and port were not dumped: only the 16 layer means were compared (they are downstream of every carried quantity, so a
  mismatch that cancels exactly in every layer mean would be invisible — judged implausible, and the Ω-swap control explains the whole residual).
- Stage-wise f32/f64 swaps (the whole-chain swap bounds every stage at ≤ 0.12 %); joint constant + head refits (bounded ≤ 4 %); `noeig` on the remaining 12
  VALID nets and in the subprocess runner (residual / memory letter); the E-pad and Gram-spelling follow-ons; anything on TEST nets; no submit.
- Residual timings in `probe.jsonl` (0.5–0.9 s) are in-process on a host at load 9–45 and say nothing about the grader (§7 uses the ladder's quiet-host runs).

## 9. Lessons (recursive-learning contract, ≤ 2)
1. A sketch-based chain carries a ±2 %-per-net RANDOM component from its own range finders (measured by swapping Ω); every FIT-3 screen at a 1.5 % bar is
   partly measuring that randomness. Register screens on paired VALID-20 or larger, and treat a "9 % of error rms" prototype-vs-port deviation as the sketch's
   signature before suspecting the port.
2. Grep the ledger for ops that only RE-ORIENT a subspace (eigh + rotation after a QR range finder): the QR range already spans the sketch; the rotation is
   paid every entry and bought nothing here (0.68 pt).
