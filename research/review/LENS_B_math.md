# LENS B — mathematics / algorithm: is the K3 cumulant chain really at its floor? (adversarial review, 2026-10-09)

Agent: lens-B (Fable 5.1). Stance taken: "the chain is at its floor and nothing cheaper reaches our accuracy" is WRONG; find the algorithm.
Rules kept: FIT nets 0/2/4 only, numpy f64, one heavy process (`ulimit -v 16000000`, OMP 8), no TEST nets, no participant code, nothing
submitted, nothing deleted. Project files touched: this file only. Scratch: `/tmp/claude/p1_xcfg.py`, `/tmp/claude/p2_k2_adjoint.py`,
`/tmp/claude/depthgate/` (a patched COPY of `srcchain.py` with a birth-dependent age gate; its `results.jsonl` holds the 15 runs).
Ledger check before every probe: `gate_ledger.py query` for adjoint / backward / TAP / cavity / mean field / Marchenko / Richardson /
control variate / Wiener / chaos / whole-network / ensemble / layer-dep → **no gate matches** (none of the brief's seven angles had been run).
Baseline for every ratio: the uncorrected f64 chain `src_r4_rf1 own:5:384,8:224` (= v55's f64 twin, no MIX2 head): 2.579e-8 / 4.353e-8 / 3.299e-8
on nets 0/2/4 (reproduced bit-for-bit by the patched copy: control row `dg_ctrl`).

## 0. Verdict in one paragraph

No algorithm in the brief's list beats the chain; four of the seven are dead by derivation (they ARE the chain, or they are ensemble statements
that are per-neuron noise), two are dead by measurement here (Richardson across K; cross-configuration ensembles are real but cost a second chain),
and the adjoint/backward angle produced a **correction to the error budget**, not a new estimator: the final MSE is NOT "≈1.5e-9 fresh per layer at
gain 0.95". Measured with the linearised adjoint (§1): the per-layer fresh mean error grows **×20 with depth** (2.5e-10 at l=1 → 5–10e-9 at l=14–15),
the mean-error transport gain is **≈0.80/layer** (column norms of Π D_k W_kᵀ), and **the last five layers originate 75–79 % of the final MSE** (last
three: 53–60 %). The one route this opens — model upgrades restricted to the last 3–4 layers, where they cost 1/4 of their full-depth price and keep
≈ half their benefit — is priced in §6; its ceiling is a wash-to-modest win (adjusted 0.90–1.00), not the leaders' ×2. The depth structure does NOT
convert into a cost cut (§2: early-born sources are worth MORE per source, not less). The leaders' gap stays where MODEL_ERROR put it: the pair-level
κ4/Σ_h closure at the late layers.

## 1. Adjoint / backward formulation — MEASURED; a budget correction, not an estimator

Mechanism. Only h¹⁶ is scored. A mean error δm^l at layer l reaches the output through the linear map T_l = Π_{k>l} diag(Φ_k) W_kᵀ (Φ_k = gate
probabilities, taken from a K=2 Gaussian chain, 1 s/net, accurate to 1e-3 — more than enough for a sensitivity map). Final error = Σ_l T_l·fresh_l.
Two things an adjoint could buy: (a) spend accuracy on the neurons/layers whose columns of T_l are large; (b) know where the error is born.

(a) Per-neuron sensitivity is UNIFORM. Coefficient of variation of the column norms of T_l: 0.13 (l=0) → 0.03 (l=14); min/max 0.10/0.25 at l=0,
0.86/1.04 at l=14 (net 0; nets 2/4 identical to two digits). Random W spreads every error over every output; there is no neuron worth more
precision than another. **Per-neuron adjoint allocation: KILL by measurement.**

(b) Depth profile — the correction. Decompose the chain's per-layer error d_l = est_l − truth_l into transported + fresh:
fresh_l = d_l − Φ_l∘(W_lᵀ d_{l−1}). Net 0 (nets 2/4 same shape, ×1.3–1.7):

| l | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 | 14 | 15 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| MSE(fresh_l) ×1e-9 | 0.25 | 0.57 | 1.0 | 1.2 | 1.7 | 2.2 | 2.9 | 3.0 | 3.1 | 3.7 | 4.5 | 3.8 | 4.2 | 5.9 | 5.1 |
| gain to output (mean col-norm² of T_l) | .047 | .068 | .097 | .134 | .175 | .221 | .307 | .381 | .435 | .510 | .627 | .710 | .774 | .902 | 1 |

Σ_l gain_l·MSE(fresh_l) = 2.57e-8 vs final 2.58e-8 (nets 2/4: 0.86/0.90 of final — the remainder is cross-layer correlation of fresh errors + truth
noise). The 1e9-sample truth noise (7e-10) is NOT what makes fresh_1 = 2.5e-10, so the profile is real. **Share of the final MSE by layer of origin:
l15 20–27 %, l14 17–21 %, l13 13–17 %, l12 10–11 %, l11 8–11 % → last five layers 75–79 %, layers ≤ 8 together 6–8 %.** Step gain 0.78–0.85,
not 0.95 (BREAKTHROUGH §1 inferred 0.95 from the linear growth of the per-layer MSE; the growth is linear because the fresh error grows ~linearly
while the gain damps — two effects that happened to mimic a constant-rate random walk).
Reading: the fresh MEAN error is driven by the accumulated STATE error (Σ_h, κ3 sources, κ4 sectors), which is why it grows with depth; the mean read
itself is converged (G-RB47). This is consistent with MODEL_ERROR's seats and sharpens them: whatever fixes Σ_h/κ4 must act **at layers ≥ 11** to count.

## 2. Does the depth profile convert into a COST cut? — MEASURED: NO (both directions)

Hypothesis: since early-layer mean errors are damped ×0.05–0.2, sources born early could be aged into the cheap basis sooner. Patched copy of
`srcchain.py` with a birth-dependent gate (`DG_B0`, `DG_GATE`, `DG_MODE`), FIT 0/2/4, pooled raw ratio vs the bit-identical control:

| run | sources folded at age 3 instead of 5 | saving (hand ledger, ≈0.11 pt per young source-layer, G-RB44 scale) | break-even ratio | measured pooled (per net) | verdict |
|---|---|---|---|---|---|
| dg_early | born l ≤ 4 (5 sources) | ≈ 1.1 pt | 1.05 | **1.323** (1.335 / 1.230 / 1.405) | KILL |
| dg_late | born l ≥ 5 (10 sources, 7 effective) | ≈ 1.5 pt | 1.07 | **1.248** (1.249 / 1.189 / 1.308) | KILL |
| dg_early2 | born l ≤ 6 at age 2 | ≈ 2.3 pt | 1.11 | **3.53** | KILL (the G-RB44 cliff) |
| dg_late9 | born l ≥ 10 at age 3 (2 effective) | ≈ 0.3 pt | 1.013 | 1.032 (1.009 / 1.048 / 1.039) | KILL |

Early-born sources cost **6.4 %/source** when folded two layers sooner, late-born **3.6 %/source** — the opposite of the naive adjoint reading.
Mechanism (matches BREAKTHROUGH §3 "every source contributes at equal weight after transport"): a source's κ3 is not a mean error at its birth layer,
it is STATE that feeds the κ3 of every later pre-activation; the late layers that matter (§1) receive all 14 earlier sources at equal weight, and the
early-born ones are exposed to the fold for more layers. The leg count cannot be thinned by birth layer. (G-RB44 folded ALL sources at g3: 1.546;
these two complementary halves give 1.32 × 1.25 ≈ 1.65 — super-additive, so no subset is cheap.)

## 3. Richardson / extrapolation across truncation orders — MEASURED: KILL

K=2 Gaussian chain (μ, Σ; same KH=8 bivariate closure, 1 s/net) vs the K3 chain B. Final-layer test truth − B ≈ α(B − m₂), α fit on two nets,
scored on the third: α = −0.009…−0.016, in-sample R² 0.011–0.030, **held-out ratios 1.013 / 0.970 / 0.980** (≈ noise). With interactions
(d·a, d·φ, d·Φ, d², Φ, φ, aφ): train R² 0.03–0.07, held-out 1.08 / 0.97 / 0.97. One-step version (fresh_l vs the local and the transported
K3−K2 difference, l = 3…15 pooled): R² ≤ 0.03, held-out 1.02 / 0.98 / 0.98.
Why (derivation agrees with the number): the K2→K3 step adds the κ3 term ∝ κ3_i φ''(a_i)/σ²; the missing error is dominated by κ4/pair-sector
terms ∝ κ4_i φ'''(a_i)/σ³ and by Σ_h closure drift. Per neuron, κ3_i and κ4_i (and the Σ_h drift) are different random variables with weak
correlation, so the "next term" is not proportional to the "last term" — there is no asymptotic series in a controllable parameter to extrapolate.
Richardson needs a knob whose error expands as c·h^p with a KNOWN p; K and the rank/age knobs are not such a knob (ERROR_BUDGET: all rank/age knobs
together move raw 3 %, so extrapolating in them is bounded by 3 % even if it worked).

## 4. Ensembles of independent chains ("control variate on the recursion") — MEASURED: real but cost-negative

Using the 22 existing `est_*` configurations on nets 0/2/4 (final layer): truth − B ≈ α(B − A), α fit on one net, scored on the other two.
Best single partners: `feed_k2a5` 0.89 / 0.95 / 0.88, `feed_k5` 0.91–0.93, `d21_k2a5` 0.92–0.94, `lean` 0.93–0.96; α ≈ −0.5…−1.0 (a weighted
AVERAGE of two chains with different truncations, i.e. independent closure errors averaging out). Linear combination of all 21 differences,
2 nets → 1: held-out 0.97 / 0.64 / 0.74 — but the 0.64/0.74 come from the `_g0.8/_g1.2` members (a per-NET g preference; G-RB14 already showed
no observable predicts it) and are unstable (0.97 on net 0). Without the g/k members the gain is the pairwise 5–10 %.
Price: every useful partner is a FULL κ3 chain (`feed_k5` ≈ 0.5 util; `lean` ≈ 0.3); the only cheap partner (K=2, ≈ 0.03 util) carries nothing (§3).
Adjusted: −10 % raw for +130 % util. **KILL on adjusted; recorded because it is the first measured positive-raw lever outside the chain itself.**
A free in-chain analogue (variant reads of the same state) is what the MIX2 corrector already consumes (its 27 columns include skew, k3, g, the Gaussian
read gap `mu_pre − m1`); G-RB28/29 bound that family at R² 0.15 of the one-step drift.

## 5. Angles dead by derivation (no probe spent; the reasoning is the deliverable)

- **TAP / cavity / dynamical mean-field for the given W.** The Onsager reaction term exists only with feedback; a feedforward layer has none. The
  cavity expansion of z_i = Σ_j W_ji h_j in the weak dependence of the h_j IS the cumulant (CLT-correction) expansion: the O(n^{-1/2}) term is κ3,
  the O(n^{-1}) terms are κ4 and κ3×κ3 — exactly the K=3 chain with its memoryless κ4 core. "TAP correction = per-layer mean correction at n²" is the
  κ3-diagonal read the chain already does; nothing new appears at the same order.
- **Free probability / deterministic equivalents / Marchenko–Pastur shrinkage.** These are ENSEMBLE statements over W. The chain already uses the
  realised W exactly in every transport (Σ_z = WᵀΣ_hW has no estimation noise to shrink). Any ensemble-averaged replacement loses the per-neuron
  O(n^{-1/2}) fluctuations the mean read needs to 1e-4 relative (var_z,i fluctuates ±3 % across neurons through Σ_j W_ji²). G-RB30 is the measured
  instance: the ARC harmonic κ4 object is ensemble-right and per-neuron noise (R² 0.03–0.15), e2e ×1.42–1.54 worse. Expect the same from every
  deterministic-equivalent substitution; the leaders' bill is per-realisation dense legs, not ensemble formulae.
- **Wiener chaos / Hermite expansion of the whole network.** E[h¹⁶] is the degree-0 chaos coefficient of f(x); the layerwise chain is the only
  tractable truncation of the chaos propagation (the degree-k chaos of layer l maps to all degrees at l+1 through the ReLU Hermite series; the
  chain keeps the first three cumulants of that map). A whole-network expansion in x is n^K per degree — strictly more expensive than layerwise.
- **MC / control variates / conditional MC** (re-checked against the §1 numbers): N = 6500 samples cost util 0.10; σ²/N = 1.2e-5 ≫ 2.5e-8, so a
  sample-wise control variate needs corr ≥ 0.9992 with h¹⁶(x), i.e. a surrogate network within 4 % output deviation of the given one; at critical
  init weight perturbations propagate at gain ≈ 1, so no compressed surrogate exists. Linear chaos retains ≈ 0.73 of the fluctuation variance per
  layer → 0.6 % after 16 layers. Conditional MC is empty: x is the only randomness (G-RB45 agrees).
- **Whole-network LEARNED estimator.** The target is 75 % an incoherent transported random walk (§1 (a): T_l mixes every neuron into every output with
  uniform weight), so a per-neuron model of the final error is bounded by what the per-layer corrector sees (R² 0.15, feature-limited: G-RB28/29);
  the final-layer-only regression here (§3, rich K2+K3 features) is R² ≤ 0.07 held-out ≈ 1.0. More nets do not help (learning curve flat).
  What a learned model would have to carry is PAIR-level (Σ_h row/κ4 sector) structure — G-RB27/29 measured that per-neuron and per-layer
  reductions of it carry nothing. KILL at the per-neuron level; a pair-level learned closure is the leaders'-trick territory, unpriced.

## 6. Ranked table (adjusted = raw × util; v55 = 2.25e-8 × 0.235 = 5.28e-9)

| # | idea | mechanism | raw | util | adjusted vs v55 | status / next experiment |
|---|---|---|---|---|---|---|
| 1 | **dense κ4 pair carrier on layers ≥ 12 only** (depth-restricted v50-SSC two-mode transports, or the analytic O(ρ) sectors Q_h ≈ α₁α₁ᵀ∘Σ_z, K31_h ≈ β₁γ₁ᵀ∘Σ_z with per-neuron Hermite coefficients, transported as congruences Wᵀ(·)W) | §1: layers ≥ 12 originate 50–55 % of the error; G-RB25 `@12` rows measured the κ4 inputs of the last 4 layers alone at **−12…−14 %**; cost scales with layers touched | ceiling −12…−14 % (uncorrected; ≈ half net of the MIX2 head, G-RB33 pattern) | +0.9 pt (2 modes × 1.59 pt × 4/14) … +3.5 pt (K=4 core loop, F4 ×4/14) | **0.90 (ceiling) … 1.00** | the only live route. Next: `srcchain_aug.py AUG=ssc` gated to l ≥ 12 (env var), FIT 0/2/4, 18 s/net; bar: pooled raw ≤ 0.95 at ≤ +1 pt, then the f64 VALID-20 pair with a refit head. Honest odds: coin-flip; every full-depth κ4 carrier was a wash net of the head |
| 2 | ensemble of two independent truncation chains (§4) | independent closure errors average | −5…−10 % | +0.3…0.5 util | ≥ 2.0× | KILL on adjusted |
| 3 | per-MLP g preference (seen again in §4 via `_g0.8/_g1.2`: ×0.64 on net 2 with the ORACLE weight) | per-net κ4 scale | −10…−30 % with oracle | 0 | 0.7–0.9 oracle only | needs an observable; G-RB14 found none (corr 0.40). Note for lens-C: an oracle-weighted g is the single largest per-net lever anyone has measured — a NET-level feature (e.g. the K2 chain's layer-mean a/σ profile, 1 s) predicting g would be worth testing on the 60 FIT nets before Oct 14 |
| 4 | Richardson across K (§3) | extrapolate truncation | 0 (held-out 1.0) | +0.03 util | ≥ 1.0 | KILL |
| 5 | birth-dependent aging (§2) | cheaper early sources | +25…+32 % | −1.1…−1.5 pt | 1.2–1.25 | KILL both directions |
| 6 | per-neuron adjoint allocation (§1a) | spend where sensitivity is high | — | — | — | KILL: sensitivity CV ≤ 0.13 |
| 7 | TAP/cavity, free probability, Wiener chaos, MC control variates, whole-network learned estimator (§5) | — | — | — | — | dead by derivation; the first three are the chain itself at the same order, the last two are bounded by the random-walk structure of the error |

## 7. What to carry into the write-up / ledger

- Correction to BREAKTHROUGH §1: fresh mean error 2.5e-10 → 5–10e-9 across depth (×20), transport gain 0.78–0.85/layer (adjoint-measured), the
  last five layers originate 75–79 % of the final MSE. The "1.5e-9 per layer at 0.95" picture is replaced; the conclusions it fed (final-layer
  tricks cannot move the score; the lever is the state closure) survive and are sharpened to "…the state closure at layers ≥ 11".
- Three new measured dead ends for `gates.jsonl` (lens-B): Richardson across K; birth-dependent aging (both directions); per-neuron adjoint allocation.
  One measured positive-raw/negative-adjusted family: two-chain ensembles (−5…−10 % raw for a second chain).
- Open: the only unmeasured positive route is depth-restricted κ4 pair carriers (row 1). If it fails the ≤ 0.95-at-≤ +1-pt bar on FIT 0/2/4, the
  K3 family is at its floor for this metric by every lens available to us, and the leaders' ×2 is a representation we do not hold.
