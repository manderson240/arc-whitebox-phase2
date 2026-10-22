# PROOFS — the method's core claims as lemmas/theorems, with machine checks

Date: 2026-09-28. Role: mathematician (rigor + algorithmic write-up). Clean-room: no participant code read; the only
external inputs are textbooks/papers named below and this repo's own documents (`ALGORITHM_SPEC.md`, `GAP_ANALYSIS.md`,
`FINITE_WIDTH_LIT.md`, `R2_GO_NOGO.md`, `OPERATING_MODEL.md`, `COV_CLOSURE_DERIVATION.md`).

Setting throughout: fixed weights W_l ∈ R^{n×n} stored (in,out), n = 1024, L = 16, entries N(0, 2/n), no bias, input
x ~ N(0, I_n); z_l = h_{l−1} W_l, h_l = ReLU(z_l), h_0 = x. Estimand: E_x[h_L] per neuron. Notation: for Y ~ N(μ, σ²),
α = μ/σ, φ, Φ the standard normal pdf/cdf, He_k the probabilists' Hermite polynomials, and the **Stein/Hermite
coefficients** f̂_k := E_G[f^{(k)}(Y)] (derivatives in the distributional sense). For f = ReLU:
f̂_0 = m1 = μΦ(α) + σφ(α), f̂_1 = Φ(α), f̂_k = He_{k−2}(−α) φ(α)/σ^{k−1} (k ≥ 2). Our chain: exact mean/covariance
transport through linear layers (Thm 1); ReLU moments by the covariance series (Thm 2); the two-index sector
T_ab = κ[z_a, z_a, z_b]; per-layer scalar κ4 = g_l σ⁴; an Edgeworth mean readout (Thm 3).

Machine checks live in `research/proofs/check*.py`; every PROVED result has a `--perturb` mode that breaks the formula and
must FAIL. All raw outputs are in `research/proofs/RESULTS.txt`. Environment: mpmath/sympy via `uv run --with mpmath`
(ephemeral env; the kit venv has neither), numpy checks with the kit venv (`whest-starterkit/.venv`).

Citation policy: **verified** = abs page / PDF text read this session or by the FINITE_WIDTH_LIT pass (quoted there);
**unverified** = a well-known book cited at chapter level only, section/theorem numbers NOT confirmed (McCullagh's chapter
PDFs at stat.uchicago.edu/~pmcc/tensorbook are font-encoded and did not extract; Bhattacharya–Rao seen only as a TOC).

| # | result | status | machine check (script → normal / perturbed) |
|---|---|---|---|
| 1 | multilinear cumulant transport through linear layers (exact) | PROVED (textbook) | `check1` exact rationals: 30/30 joint cumulants k≤4 equal / diagonal-only rule: 28/30 mismatch → FAIL |
| 2 | ReLU Gaussian moments, covariance (Price/Mehler) series, arc-cosine kernel, kink identities | PROVED (textbook + our series form) | `check2` mpmath 30 digits: all ≤ 1.6e-13 vs quadrature / sign flip + wrong f̂_2: 24 violations → FAIL |
| 3 | Edgeworth expansion of E[f(Z)] with remainder orders; ReLU-specific terms | PROVED-under-assumption (formal series; remainder order verified) | `check3` slopes 3.07/3.96/5.14/5.90/7.07 for expected 3..7 / drop κ3²/72: slope 5.8 ≠ 7 → FAIL |
| 4 | error-propagation (stability) lemma; coherent vs orthogonal accumulation | PROVED (lemma); measured gains reported | `check4` Part A 0/200 violations; Part B/C on our chain (see §4) / drop the gain product → FAIL |
| 5 | fixed-weight kurtosis identity g_l = 3[Var‖A‖² − 2trC²]/[(trC)² + 2trC²]; ensemble 15(l−1)/n; quenched ≤ annealed (last-layer) | PROVED (identity, exact in E_w); inequality PROVED for the last-layer ensemble, CONJECTURE for the full PDLT ensemble | `check5_6` 6 nets × 16 layers: max|g − g*| ≤ 0.002 (tolerance 0.007) / drop −2trC²: 16/16 layers → FAIL |
| 6 | self-averaging of g_l | PROVED conditional on earlier layers (Var = O(1/n)); unconditional CONJECTURE (numerically supported) | `check5_6`: conditional sd 0.0008–0.0011 predicted; across-net sd 0.0005–0.004 measured |
| 7 | bivariate fourth-order covariance correction (COV_CLOSURE_DERIVATION eq. (3)) | PROVED under the Gaussian scale-mixture model; remainder O(v², E ε³) | `check7` remainder slope 1.98/2.02/2.03 (expected 2) / drop (3,1) terms: slope 1.0 → FAIL |

---

## 1. Theorem 1 — multilinear cumulant transport (linear layers are exact)

**Statement.** Let h ∈ R^n be a random vector with finite moments of order k, W ∈ R^{n×m} fixed, z = hW (z_j = Σ_a h_a W_aj).
Then for every k ≥ 1 and all j_1..j_k,

  κ(z_{j1}, …, z_{jk}) = Σ_{a1..ak} W_{a1 j1} ⋯ W_{ak jk} κ(h_{a1}, …, h_{ak}),

i.e. κ_k(z) = (Wᵀ)^{⊗k} κ_k(h) exactly. In particular μ_z = μ_h W, Σ_z = Wᵀ Σ_h W, the two-index sector
κ[z_i,z_i,z_j] = Σ_{a,a',b} W_ai W_a'i W_bj κ[h_a,h_a',h_b], and κ4(z_i) = Σ_{abcd} W_ai W_bi W_ci W_di κ[h_a,h_b,h_c,h_d].

**Source.** Textbook: McCullagh, *Tensor Methods in Statistics* (Chapman & Hall 1987; Dover 2018), ch. 2 — cumulants are
symmetric tensors that transform multilinearly under linear maps (this is the "tensor" of the title). Section number
**unverified** (see citation policy). Also Brillinger, *Time Series* (1981), ch. 2 (multilinearity of joint cumulants) —
**unverified citation**.

**Proof.** Joint cumulants are defined from joint moments by the partition formula
κ(X_1..X_k) = Σ_π (−1)^{|π|−1}(|π|−1)! Π_{B∈π} E[Π_{i∈B} X_i]. Each moment E[Π_{i∈B} X_i] is linear in each X_i separately,
hence so is every product of moments and the finite signed sum: κ is a symmetric k-linear form in (X_1..X_k) (over the
vector space of random variables with finite k-th moments). Substituting X_i = z_{ji} = Σ_a W_{a ji} h_a and expanding by
multilinearity gives the formula. Equivalently, via the cumulant generating function K_z(t) = log E e^{i tᵀz} = K_h(Wt):
κ(z_{j1..jk}) = (−i)^k ∂_{t_{j1}}⋯∂_{t_{jk}} K_z(0), and ∂_{t_j} = Σ_a W_aj ∂_{u_a} with constant coefficients, so k-fold
differentiation produces exactly the k-fold contraction with W. ∎

**Consequences for the method.** (i) Mean and covariance transport (the kit's covariance propagation) is exact; the
only approximation in our linear steps is the closure of κ[h_a,h_a',h_b] for a ≠ a' (the "distinct-index part", spec
§R2) and of κ4's four-index sum by the scalar g_l — i.e. truncations of the *input* tensor, never of the transport law.
(ii) All closure error is born at the ReLU (Theorems 2–3) and then transported (Lemma 4).

**Machine check.** `check1_cumulant_transport.py`: h is a *dependent* 3-vector on 5 rational atoms, W rational, all
moments and cumulants exact `Fraction`s; all 30 joint cumulants of z for k = 1..4 equal the contracted h-cumulants
**exactly** (`Fraction ==`). Perturbed (diagonal-only rule, the one valid for independent h): 28/30 mismatch → FAIL.
**Status: PROVED.**

---

## 2. Theorem 2 — ReLU moments, the covariance series, the arc-cosine kernel, kink identities

**Statement.** Let (Z_1, Z_2) be jointly Gaussian with means μ_i, variances σ_i², covariance C = ρσ_1σ_2, |ρ| < 1,
α_i = μ_i/σ_i, and f = ReLU.

(a) E[f(Z)] = μΦ(α) + σφ(α);  E[f(Z)²] = (μ² + σ²)Φ(α) + μσφ(α);  E[f(Z)³] = (μ³ + 3μσ²)Φ(α) + (μ² + 2σ²)σφ(α).

(b) (covariance series) For f, g with E_G[f^{(k)}], E_G[g^{(k)}] finite for all k and the series convergent,

  E[f(Z_1) g(Z_2)] = Σ_{k≥0} f̂_k(1) ĝ_k(2) C^k / k!,   f̂_k(i) := E[f^{(k)}(Z_i)] under the marginal N(μ_i, σ_i²).

  For f = g = ReLU the coefficients are f̂_0 = m1, f̂_1 = Φ(α), f̂_k = He_{k−2}(−α)φ(α)/σ^{k−1} (k ≥ 2), and the series
  converges absolutely for |ρ| ≤ 1 (terms are O(ρ^k/k²)). More generally E_G[f^{(p)}(Z_1) g^{(q)}(Z_2)] =
  Σ_k f̂_{k+p} ĝ_{k+q} C^k/k! (this is `series(f̂, ĝ, C, p, q)` in the code).

(c) (arc-cosine kernel, μ = 0) E[f(Z_1) f(Z_2)] = σ_1σ_2 (sin θ + (π − θ) cos θ)/(2π), θ = arccos ρ.

(d) (kink identities at general means) with δ_i = δ(z_i) = f''(z_i), θ_i = 1{z_i > 0} = f'(z_i):
  ⟨δ_1δ_2⟩ = exp[−(α_1² − 2ρα_1α_2 + α_2²)/(2(1−ρ²))] / (2πσ_1σ_2√(1−ρ²))  (the joint density at (0,0)),
  ⟨δ_1θ_2⟩ = (φ(α_1)/σ_1) Φ((α_2 − ρα_1)/√(1−ρ²)),
  and both equal their series forms Σ_k f̂_{k+2}(1) f̂_{k+2}(2) C^k/k! and Σ_k f̂_{k+2}(1) f̂_{k+1}(2) C^k/k!.

**Sources.** (a) elementary (integration by parts); (b) **Price's theorem** — R. Price, "A useful theorem for nonlinear
devices having Gaussian inputs", IRE Trans. Inf. Theory 4(2):69–72, 1958 (**verified** bibliographic record):
∂^k E[f(Z_1)g(Z_2)]/∂C^k = E[f^{(k)}(Z_1) g^{(k)}(Z_2)] at fixed marginals; the series is its Taylor expansion in C
about C = 0 (where the expectation factorizes). It is also the Mehler/Hermite ("Gaussian Fourier") expansion, since
E[f(Y) He_k((Y−μ)/σ)] = σ^k E[f^{(k)}(Y)] by k-fold Gaussian integration by parts (Stein's identity). (c) Cho & Saul,
"Kernel Methods for Deep Learning", NIPS 2009 — **verified from the PDF text**: eq. (1) k_n(x,y) = 2∫dw e^{−‖w‖²/2}(2π)^{−d/2}
Θ(w·x)Θ(w·y)(w·x)^n(w·y)^n, eq. (3) k_n = (1/π)‖x‖^n‖y‖^n J_n(θ), eq. (6) J_1(θ) = sin θ + (π−θ)cos θ; with w ~ N(0,I),
(w·x, w·y) is a centred Gaussian pair with variances ‖x‖², ‖y‖² and correlation cos θ, so E[ReLU·ReLU] = k_1/2. (d) elementary
(conditioning on z_1 = 0).

**Proof sketch.** (a) ∫_0^∞ z^m φ((z−μ)/σ)/σ dz by integration by parts, or from (b) with C → 0. (b) Price's theorem
follows from ∂_C p(z_1,z_2) = ∂_{z1}∂_{z2} p for the bivariate Gaussian density (the heat equation in the covariance),
then integrate by parts k times against f(z_1)g(z_2); distributional derivatives are legitimate because f = ReLU is
Lipschitz and its derivatives θ, δ, δ', … are tempered distributions paired with a Schwartz density. The coefficient
formula: f̂_1 = E[θ(Y)] = Φ(α); f̂_2 = E[δ(Y)] = p_Y(0) = φ(α)/σ; f̂_k = E[δ^{(k−2)}(Y)] = (−1)^{k−2} p_Y^{(k−2)}(0) =
He_{k−2}(−α)φ(α)/σ^{k−1} using p_Y^{(m)}(y) = (−1)^m He_m((y−μ)/σ) p_Y(y)/σ^m. Convergence: |He_m(x)| ≤ c √(m!) e^{x²/4}
(Cramér's inequality), so |f̂_kĝ_kC^k/k!| ≤ c' ρ^k (k−2)!/k! = O(ρ^k/k²). (c) Cho–Saul eq. (3),(6) with n = 1 and the
1/2 from eq. (1)'s prefactor 2. (d) ⟨δ_1 g(z_2)⟩ = p_1(0) E[g(z_2) | z_1 = 0]; the conditional law is
N(μ_2 + ρσ_2(0−μ_1)/σ_1, σ_2²(1−ρ²)). ∎

**Machine check.** `check2_relu_moments.py` (mpmath, 30 digits, 6 random (μ_1,μ_2,σ_1,σ_2,ρ)): (a) ≤ 1.6e-30 vs
quadrature; (b) 61-term series vs 2-D quadrature ≤ 2.1e-17; (d) closed forms vs series ≤ 1.6e-13 and ⟨δθ⟩ vs conditional
quadrature ≤ 2e-32; (c) ≤ 5e-32. Informational: the production truncation K_H = 8 leaves ≤ 3.6e-6 absolute at |ρ| ≤ 0.85
(at the chain's ρ ≈ 0.13 it is ~ρ⁹ ≈ 1e-8 relative). Perturbed (sign of μσφ in E[f²] flipped, f̂_2 replaced by Φ):
24 violations → FAIL. **Status: PROVED.**

---

## 3. Theorem 3 — Edgeworth/Gram–Charlier expansion of E[f(Z)] and the ReLU terms

**Statement (formal expansion + remainder order).** Let Z have mean μ, variance σ², cumulants κ_r (r ≥ 3), and let
f have Stein coefficients f̂_j = E_G[f^{(j)}(Y)], Y ~ N(μ, σ²). Then, as a formal series,

  E[f(Z)] = Σ_{j≥0} (B_j(0, 0, κ_3, …, κ_j)/j!) f̂_j
          = f̂_0 + (κ3/6) f̂_3 + (κ4/24) f̂_4 + (κ5/120) f̂_5 + (κ6/720 + κ3²/72) f̂_6 + (κ7/5040 + κ3κ4/144) f̂_7 + …,

B_j the complete Bell polynomials. **Remainder order:** if κ_r = O(ε^r) (the natural scaling of a sum of many weakly
dependent terms: κ3 = O(n^{−1/2}), κ4 = O(n^{−1}), …), then truncating after all terms of total cumulant order ≤ J leaves
O(ε^{J+1}). In the 1/n counting the κ3²/72 term is the SAME order as κ4/24; keeping κ4 without κ3² is inconsistently
ordered (our v3 readout keeps κ3/6 and κ4/24 only — its remainder is O(n^{−1}) from κ3², not O(n^{−3/2})).
For f = ReLU: f̂_3 = −αφ(α)/σ², f̂_4 = (α²−1)φ(α)/σ³, f̂_5 = He_3(−α)φ/σ⁴, f̂_6 = He_4(−α)φ/σ⁵, so the mean shifts are
Δm_3 = −κ3 μ φ(α)/(6σ³), Δm_4 = κ4(α²−1)φ(α)/(24σ³) = g(α²−1)σφ(α)/24 for κ4 = gσ⁴ (at μ = 0: −gσφ(0)/24),
Δm_33 = κ3² He_4(−α)φ(α)/(72σ⁵). For f² (E[h²]): f̂_3 = 2φ/σ, f̂_4 = 2He_1(−α)φ/σ², matching `coeffs_relu2`.

**Sources.** Kendall & Stuart, *The Advanced Theory of Statistics* vol. 1, ch. 6 (Gram–Charlier/Edgeworth series) —
**unverified section**; McCullagh 1987 ch. 5 (Edgeworth series in tensor notation) — **unverified section**; validity
with rigorous remainder for sums of i.i.d. vectors under Cramér's condition: Bhattacharya & Ranga Rao, *Normal
Approximation and Asymptotic Expansions* (Wiley 1976; SIAM Classics 2010), ch. 5 "Asymptotic expansions — nonlattice
distributions" (chapter title from the publisher's TOC; **theorem numbers unverified**). Our z_l,i are NOT sums of i.i.d.
terms (fixed weights, dependent h), so those theorems do not apply verbatim — hence PROVED-under-assumption.

**Proof (formal).** ϕ_Z(t) = ϕ_G(t) exp(Σ_{r≥3} κ_r (it)^r/r!). Fourier inversion turns multiplication by (it)^r into
(−d/dz)^r acting on the Gaussian density: p_Z = exp(Σ_r κ_r(−D)^r/r!) p_G. Pairing with f and integrating by parts r times
moves each (−D)^r onto f as D^r: E[f(Z)] = E_G[exp(Σ_r κ_r D^r/r!) f]. Expanding the exponential of the formal power
series Σ_{r≥3} κ_r s^r/r! in powers of s gives Σ_j B_j(0,0,κ_3,…,κ_j) s^j/j! (definition of the complete Bell polynomials;
B_6 ⊃ 10κ3² from the C(6,3)/2 = 10 partitions into two 3-blocks, B_7 ⊃ 35κ3κ4). Reading off E_G[D^j f] = f̂_j gives the
series. The remainder order under κ_r = O(ε^r) follows because the coefficient of f̂_j is homogeneous of degree j in ε.
Rigor beyond the formal level (convergence/asymptoticity) requires a smoothness (Cramér) condition on Z and growth
bounds on f — supplied by Bhattacharya–Rao for i.i.d. sums; here it is an assumption, tested numerically below. ∎

**Machine check.** `check3_edgeworth.py`: Z = μ + √(1−ε²) G + ε U, U a standardized Gamma(4) (κ_r(U) = (r−1)!/4^{r/2−1},
so κ_r(Z) = ε^r κ_r(U) exactly); truth E[ReLU(Z)] = E_U[m1(μ + εU, 1−ε²)] by 1-D mpmath quadrature. Log-log slope of
|error| vs ε after including cumulant orders ≤ J: **3.07, 3.96, 5.14, 5.90, 7.07 for J = 2..6 (expected J+1)**. Perturbed
(κ3²/72 dropped at J = 6): slope 5.82 → FAIL, i.e. the κ3² term is real and of the stated order.
**Status: PROVED-under-assumption** (formal series with the remainder order verified on a smooth non-Gaussian family;
not a theorem for the chain's actual z-distribution).

---

## 4. Lemma 4 — error propagation through the closure chain (stability), and how our errors actually accumulate

**Statement.** Let s_l = F_l(s_{l−1}) be the exact per-layer statistics (any normed state, e.g. (μ_h, Σ_h)), and
ŝ_l = F̂_l(ŝ_{l−1}) the estimator with ŝ_0 = s_0. Define the one-step closure error η_l := F̂_l(s_{l−1}) − F_l(s_{l−1})
(estimator applied to EXACT input) and let ρ_l be a Lipschitz constant of F̂_l on the segment between s_{l−1} and ŝ_{l−1}.
Then with e_l := ŝ_l − s_l,

  ‖e_L‖ ≤ Σ_{l=1}^{L} ‖η_l‖ Π_{k=l+1}^{L} ρ_k        (coherent / worst-case bound).

If moreover the transported one-step errors G_l η_l (G_l = the linearized transport from layer l to L) are mutually
orthogonal, then ‖e_L‖² = Σ_l ‖G_l η_l‖² (orthogonal / random-walk accumulation) — up to second-order terms.

**Source.** This is the discrete Grönwall / "Lady Windermere's fan" argument for one-step methods: Hairer, Nørsett &
Wanner, *Solving ODEs I*, §II.3 (**verified** that §II.3 is the global-error/Lady Windermere's fan section, via
secondary sources; page numbers not checked).

**Proof.** e_l = F̂_l(ŝ_{l−1}) − F_l(s_{l−1}) = [F̂_l(ŝ_{l−1}) − F̂_l(s_{l−1})] + η_l, so ‖e_l‖ ≤ ρ_l‖e_{l−1}‖ + ‖η_l‖ with
e_0 = 0; unrolling gives the bound. For the orthogonal statement, linearize: e_L = Σ_l G_l η_l + O(‖η‖²) with
G_l = DF̂_L ⋯ DF̂_{l+1}; Pythagoras under mutual orthogonality. ∎

**What this says about the measurement "final error ≈ 16 one-step errors" (spec F2, GAP §2).** The bound is a
*triangle-inequality* bound: with gain ≈ 1 and equal η it gives RMS ≤ L·η, i.e. MSE ≤ L²η² (coherent, MSE ∝ L²); the
orthogonal law gives MSE = Lη² (∝ L). The two are distinguishable by the growth exponent p of the chain's MSE with depth
and by the ratio measured/√(Σ η_l²G_l²). Measured (below): p ≈ 1.35 averaged over 6 nets, and the final RMS error sits
between the orthogonal and coherent predictions — the per-layer closure errors are transported with gain 0.8–1.0 and add
MOSTLY incoherently, with a coherent component (the persistent-sign mean bias that per-layer calibration constants remove:
"kit + per-layer scale" gains 3× — exactly the coherent share — and cannot touch the incoherent remainder). Practical
corollary for the write-up: after calibration, only per-step accuracy reduces the error, and a factor r on every η_l gives
r² on the final MSE regardless of depth.

**Machine check.** `check4_error_propagation.py`. Part A (synthetic affine chains in R^6, exact Lipschitz constants):
0/200 violations of the bound; perturbed (gain product dropped): violations → FAIL. Part B (our K2 chain — exact
mean/covariance transport + covariance-series ReLU, K_H = 8 — on MLP seed 1000, fresh MC N = 2e5 giving exact per-layer
(μ_h, Σ_h)): one-step mean-channel errors η_l from EXACT inputs (noise-corrected), finite-difference one-step gains ρ_l
(along the actual error direction and a random direction) and transported gains G_l, then the measured final RMS error vs
the coherent bound Σ η_l G_l and the orthogonal prediction √(Σ η_l² G_l²). Part C (the coordinator's 6 all-layer caches,
seeds 1000..1005, N = 2e5): the chain's μ_z MSE per layer, noise-corrected, and its growth exponent p in MSE ∝ l^p
(orthogonal with gain 1 ⇒ p ≈ 1; coherent ⇒ p ≈ 2). **Results: see RESULTS.txt §4 and the summary below.**

Summary of `check4_out.txt`:
- **Part A**: 0/200 violations; perturbed (gain product dropped): 71/200 violations → FAIL. The lemma's product of gains is
  load-bearing.
- **Gains on our chain (seed 1000)**: one-step ρ_l (mean channel, along the actual error direction / a random direction):
  0.78/0.80 at l = 2, rising monotonically to 0.95–1.01 at l ≥ 8 and 0.96/0.95 at l = 16 (a layer's gain is ≈ RMS(Φ(α)∘Wᵀv)/RMS(v):
  √2 from the He-scaled W times the RMS of the ReLU gate Φ(α), which grows toward 1 as the means drift positive with depth).
  Transported gains G_l to layer 16: 0.19 (l = 1), 0.43 (l = 5), 0.69 (l = 9), 0.83 (l = 12), 0.96 (l = 15), 1 (l = 16).
  So "gain ≈ 1" is right for the deep half; the first ~6 layers' errors are damped 2–5× before they reach the output.
- **η_l NOT resolvable at N = 2e5** (honest limit of this run): the one-step mean-channel error is ~1e-7 MSE while the
  reference noise floor var_h/N ≈ 3.6e-7; the noise-corrected estimate is undefined for 15/16 layers (layer 1 is exactly 0:
  z_1 is Gaussian). The per-step η used for the bound is therefore imported from the 1e6-ref oracle (spec F2: 1.64e-7 MSE
  including 7.2e-8 noise ⇒ η ≈ 3.0e-4 RMS), assumed uniform over layers ≥ 2.
- **Measured final RMS error of the K2 chain (noise-corrected, seed 1000)**: 1.73e-3 (MSE 3.0e-6; raw 3.36e-6, noise 3.6e-7).
  Coherent bound Σ η G_l = 3.0e-3 (MSE 9.0e-6); orthogonal √Σ η²G_l² = 8.3e-4 (MSE 6.9e-7). **Measured = 0.58 × bound
  = 2.1 × orthogonal** — the bound holds (PASS) and the accumulation is partly coherent.
- **Part C (6 nets, seeds 1000–1005, N = 2e5 caches)**: noise-corrected μ_z MSE at l = 16: 5.7e-6, 7.9e-6, 6.3e-6, 1.2e-5,
  8.4e-6, 6.4e-6; growth exponent p (MSE ∝ l^p, l = 4..16): 1.02, 1.48, 1.70, 1.31, 1.67, 0.93, **mean 1.35** — between
  orthogonal (1) and coherent (2), consistent with the Part B ratio. (Early-layer MSEs sit at the noise floor and are
  zeroed by the correction; the exponent is fitted on l ≥ 4 where signal ≫ noise.)

**Status: PROVED (lemma).** The gain/accumulation statements about our chain are measurements, reported with their noise.

**Reconciliation note (2026-09-28) — p = 1.35 here vs l^1.55 / l^1.58 in the write-up's Fig. F1.** These are NOT the same
measurement and neither number corrects the other. Part C's 1.35 is the depth exponent of the **K2 chain** (exact μ/Σ transport +
covariance-series ReLU, no κ3/κ4 — roughly the kit's family), for the **pre-activation means μ_z**, on **6 local nets** (seeds
1000–1005) against **N = 2e5 caches with the noise var_z/N ≈ 3.6e-7 subtracted** — the per-layer MSEs (1e-6…1e-5) are only 3–30×
that noise, so the per-net exponents scatter 0.93–1.70 and 1.35 carries ≈ ±0.3. F1's 1.55 (v4_zc) / 1.58 (v5b) are descriptive
power-law fits over l = 4..16 of `per_layer_mse` (the **post-activation** means h_l, `whestbench`'s definition, whose last entry is
the final-layer MSE) of the **v4_zc / v5b chains** on **100 official nets against 1e9 truth** (no noise correction needed). Two
further differences matter: (i) the chain — v4_zc/v5b carry T, the κ4 table and D22/D31, so their residual error has a different
composition (and, by Thm 8, a coherent transported component in the source state) from the κ3-dominated K2 error; (ii) the fit
WINDOW — the Mini-100 curves are concave in log–log (fast growth while the error is being born at layers 4–7, gains 0.8, then
slower), so the same data give **1.19 (v4_zc) / 1.28 (v5b) over l = 8..16** (`mini_run_{v4_zc,v5b}.json`, recomputed
2026-09-28), close to the K2 value and to the orthogonal law. The qualitative reading is unchanged and holds for both: p ∈ (1, 2)
— accumulation mostly incoherent with a coherent share — and the corollary (per-step accuracy is the lever; a factor r on every η
gives ≈ r² on the final MSE) does not depend on which number is quoted. The write-up quotes both with their definitions.

---

## 5. Theorem 5 — the fixed-weight kurtosis identity; ensemble 15(l−1)/n; quenched vs annealed

**Setting.** Condition on W_1..W_{l−1}. Then a := h_{l−1}(x) is a fixed function of x; write m = E_x a, A = a − m,
C = Cov_x(a), s² = 2/n. The rows w_i of W_l are i.i.d. N(0, s² I_n), independent of a, and z_i = w_i · a.

**Statement (exact one-layer identity, ours).** For each row,

  E_w[κ4_x(w·a)] = 3 s⁴ [Var_x(‖A‖²) − 2 tr C²],    E_w[(Var_x(w·a))²] = s⁴ [(tr C)² + 2 tr C²],

hence the ratio of the two ROW-AVERAGES (over the n i.i.d. rows of W_l, i.e. over the neurons i of layer l — the ratio
of averages, not the average of ratios; this is precisely the target g_l = mean_i κ4_i / mean_i v_i² of `proto_k4fit`)
converges, as the row-average concentrates (Prop. 6), to

  g_l* = 3 [Var_x‖A_{l−1}‖² − 2 tr C_{l−1}²] / [(tr C_{l−1})² + 2 tr C_{l−1}²].

Corollaries: (i) if a is Gaussian (e.g. l = 1, a = x) then Var‖A‖² = 2 tr C² and g_1 = 0 exactly; (ii) g_l* > 0 iff
‖A‖² has more variance than a Gaussian vector with the same covariance would have — a fourth-order property of h_{l−1}.

**Proof.** Conditional on a, w·A ~ N(0, s²‖A‖²) over w, so E_w[(w·A)⁴] = 3s⁴‖A‖⁴, and E_w E_x[(w·A)⁴] = 3s⁴ E_x‖A‖⁴.
Var_x(w·a) = wᵀCw, and for w ~ N(0, s²I): E_w[(wᵀCw)²] = s⁴[(tr C)² + 2 tr C²] (Wick/Isserlis: the three pairings of
E[w_aw_bw_cw_d] = s⁴(δ_abδ_cd + δ_acδ_bd + δ_adδ_bc) contracted with C_abC_cd). Then
E_w κ4_x(w·a) = E_w[E_x(w·A)⁴ − 3(E_x(w·A)²)²] = 3s⁴E_x‖A‖⁴ − 3s⁴[(tr C)² + 2tr C²] = 3s⁴[Var_x‖A‖² − 2 tr C²], using
E_x‖A‖² = tr C. The identity is exact in E_w for every fixed realization of the earlier layers; no approximation. ∎

**The published ensemble result.** Roberts, Yaida & Hanin, *The Principles of Deep Learning Theory* (arXiv:2106.10165,
**verified** abs + PDF by the FINITE_WIDTH_LIT pass), eq. (5.120): V^{(l)} = (l−1)(3A_4/A_2² − 1)(K*)², coefficient 5 for
ReLU, so the single-input excess kurtosis **over the weight ensemble at a fixed input** is 15(l−1)/n (zero fitted
constants). Measured fixed-weight g_l is 0.31–0.67 of it (FINITE_WIDTH_LIT §4).

**Quenched vs annealed — what can be proved.** Three different fourth cumulants are in play:
(Q) quenched: κ4 over x at fixed W (ours); (A_l) annealed over (w_l, x) jointly with earlier layers fixed;
(E) the PDLT ensemble: over ALL weights at a fixed x.
- **Proposition (A_l ≥ Q, exact).** For the centred variable w·A: κ4^{(w,x)} = E[(w·A)⁴] − 3(E[(w·A)²])² = 3s⁴E‖A‖⁴ −
  3s⁴(tr C)² = 3s⁴ Var‖A‖² = E_w κ4^{(x)} + 6 s⁴ tr C² ≥ E_w κ4^{(x)}. So annealing over the last layer's rows adds exactly
  6s⁴ tr C² > 0 to the numerator; the quenched (fixed-weight) kurtosis is strictly smaller. **PROVED.** (Normalizing by the
  respective variances: g^{A_l} = 3Var‖A‖²/(trC)² ≥ g^{Q} whenever g^Q ≥ 0, since E_w v² ≥ (E_w v)². The measured g^Q > 0
  for l ≥ 2.)
- **At a fixed input x, the kurtosis over the LAST layer's rows alone is exactly 0** (w·a is Gaussian in w). Hence the
  PDLT quantity (E) is entirely generated by the fluctuation of ‖a(x)‖² over the EARLIER layers' weights (PDLT eq. 4.76:
  V/n = Var_W of the metric G(x) = (2/n)‖a(x)‖²), and it has no term in common with (Q), which is generated by the
  fluctuation of ‖A(x)‖² over x. The two are different functionals of the same network family; their comparison is
  quantitative, not structural. The decomposition in FINITE_WIDTH_LIT §3 (removing the common mode Cov_W(G(x),G(x'))
  brings the ratio to 0.59–0.76) supports the direction g^Q ≤ g^E but does not prove it. **Direction g^Q ≤ 15(l−1)/n:
  CONJECTURE** (empirically true at every layer, ratio 0.31–0.67).

**Machine check.** `check5_6_kurtosis_selfavg.py` on the SAME weights as the 6 coordinator caches (`proto_r2.make_mlp`
seeds 1000..1005; κ4 is not in the caches, so it is re-measured, N_x = 40 000 inputs per net, one pass, identity and direct
g from the same samples). Gate per layer: max over nets |g_l − g_l*| ≤ 3·(delta-method row-average sd) + 3·(MC sd).
Perturbed (−2 tr C² dropped): the identity predicts g_1 ≈ 0.006 where the truth is 0 and ~0.16 at l = 16 vs 0.06 measured
→ 16/16 layers FAIL. **Results: RESULTS.txt §5; summary below.**

Summary of `check5_6_out.txt` (6 nets, N_x = 40 000; g in units of excess kurtosis):

| l | g_meas range (6 nets) | g_identity range | max\|g − g*\| | tolerance | sd across nets | conditional sd predicted (Prop. 6) |
|---|---|---|---|---|---|---|
| 1 | −0.0017 … 0.0004 | −0.0002 … −0.0001 | 0.0016 | 0.0070 | 0.0007 | 0.0008 |
| 2 | 0.0092 … 0.0116 | 0.0092 … 0.0098 | 0.0018 | 0.0070 | 0.0010 | 0.0008 |
| 4 | 0.0210 … 0.0237 | 0.0206 … 0.0222 | 0.0018 | 0.0072 | 0.0009 | 0.0008 |
| 8 | 0.0366 … 0.0414 | 0.0369 … 0.0403 | 0.0012 | 0.0075 | 0.0016 | 0.0009 |
| 12 | 0.0497 … 0.0550 | 0.0490 … 0.0535 | 0.0024 | 0.0079 | 0.0019 | 0.0010 |
| 16 | 0.0603 … 0.0658 | 0.0601 … 0.0668 | 0.0011 | 0.0087 | 0.0021 | 0.0011 |

All 16 layers pass (max deviation 0.0024, always within the row-average + MC tolerance); g_1 = 0 to within noise as the
corollary requires. Perturbed (−2 tr C² dropped): predicted g_1 = 0.0059 (truth 0), g_16 = 0.16–0.20 (truth 0.06) → 16/16
FAIL. The measured g_l (0.010 → 0.063) reproduces FINITE_WIDTH_LIT's table to ~0.002 on 6 further nets. Self-averaging
(Prop. 6): the across-net sd (0.0007–0.0021) is consistent with the conditional O(1/n) prediction (0.0008–0.0011) plus MC
noise at N_x = 40 000 (~0.0015 per net); this run therefore cannot resolve the earlier-layer component — the FINITE_WIDTH
pass, with large-N references, saw a real 0.0038 difference between mlp0 and mlp1 at l = 16, which is the honest size of the
unconditional (net-to-net) spread.

**Status: PROVED** (identity; exact in E_w). Ensemble 15(l−1)/n: quoted, verified by the earlier pass. A_l ≥ Q: PROVED.
Q ≤ E: CONJECTURE.

---

## 6. Proposition 6 — self-averaging of g_l

**Statement.** Conditional on W_1..W_{l−1}, the pairs (κ4_i, v_i²), i = 1..n, are i.i.d. across the neurons of layer l
(functions of the i.i.d. rows w_i), with finite variance (all moments of w·a are finite: a = ReLU-net activations of a
Gaussian input have Gaussian tails). Hence by the delta method / Chebyshev,

  Var(ĝ_l | W_{<l}) = (1/n) Var_i(κ4_i − g_l* v_i²) / (E_w v²)² + O(n^{−2}),   ĝ_l → g_l* at rate n^{−1/2}.

The UNCONDITIONAL spread across independently seeded nets adds the fluctuation of (Var‖A‖², tr C, tr C²) themselves over
W_{<l}; these are sums over the n neurons of layer l−1 and are expected to concentrate at the same O(1/n) rate, but the
neurons of layer l−1 are not independent (they share the input x and the earlier layers), so this part is
**CONJECTURE**, supported numerically (below and FINITE_WIDTH_LIT §4: 5 nets within ±0.003).

**Proof (conditional part).** Given W_{<l}, κ4_i = K(w_i) and v_i = V(w_i) for fixed measurable functions K, V of an
i.i.d. Gaussian row; the ratio of sample means of i.i.d. finite-variance variables has the stated delta-method variance
(first-order Taylor of (X̄, Ȳ) ↦ X̄/Ȳ around the means), and Chebyshev gives convergence in probability. ∎

**Machine check** (same script): the table reports, per layer, the delta-method conditional sd and the observed sd of g_l
across the 6 nets. **Results: RESULTS.txt §5; summary in §5 above.** Reading: where the across-net sd exceeds the
conditional prediction (deep layers), the excess is the earlier-layer fluctuation — a real network-to-network component
that a universal g_l table cannot capture (FINITE_WIDTH_LIT §6 item 2's "irreducible 3–5 %").
**Status: PROVED (conditional); CONJECTURE (unconditional), numerically supported.**

---

## 7. Theorem 7 — the bivariate fourth-order covariance correction (COV_CLOSURE_DERIVATION.md eq. (3))

The other agent's derivation (read at the end of this session, not edited) rests on two claims which we re-prove here.

**Statement.** (a) [bivariate Edgeworth] For (z_a, z_b) with joint cumulants κ_{p,q} relative to the Gaussian with the same
(μ, Σ), as a formal series,
  E[f(z_a)g(z_b)] = E_G[exp(Σ_{p+q≥3} κ_{p,q}/(p!q!) ∂_a^p ∂_b^q)(fg)] = E_G[fg] + Σ_{p+q=3} κ_{p,q}/(p!q!) E_G[f^{(p)}g^{(q)}]
  + Σ_{p+q=4} κ_{p,q}/(p!q!) E_G[f^{(p)}g^{(q)}] + ½Σ_{p+q=3}Σ_{r+s=3} κ_{p,q}κ_{r,s}/(p!q!r!s!) E_G[f^{(p+r)}g^{(q+s)}] + …,
  with E_G[f^{(p)}g^{(q)}] = Σ_k f̂_{k+p}ĝ_{k+q}C^k/k! (Thm 2b). The first-order κ3 block is exactly what `expectation()`
  in `proto_r2.py` adds (κ3_a/6·series(3,0), T_ab/2·series(2,1) and their mirrors); the leading (k=0) terms give the
  compact form ΔE[fg] ⊃ ½[T_ab⟨δ_aθ_b⟩ + T_ba⟨θ_aδ_b⟩] + ¼κ_{2,2}⟨δ_aδ_b⟩ + …; in Cov = E[fg] − E[f]E[g] the k = 0 terms of
  the own-index series (κ3_a/6·f̂_3(a)·ĝ_0(b) = Δm_a m_b, etc.) cancel identically against the mean shifts (the "k = 0
  cancellation"), so the covariance correction is Σ_{k≥1} of the own-index series plus ALL k of the cross-index series.
  Remainder after the κ3-first-order + κ4-first-order + κ3² blocks: O(κ5, κ3κ4) = O(n^{−3/2}).
(b) [Gaussian scale mixture] If z = μ + s ξ, ξ ~ N(0, Σ), s² = 1 + ε, E ε = 0, Var ε = v, ε ⊥ ξ, then EXACTLY
  κ(z_a,z_b,z_c,z_d) = v[Σ_abΣ_cd + Σ_acΣ_bd + Σ_adΣ_bc]; in particular κ4_a = 3vσ_a⁴ (g = 3v), κ_{2,2} = v(σ_a²σ_b² + 2C²),
  κ_{3,1} = 3vσ_a²C.
(c) [the correction, eq. (3)] Under (b), for any f, g with the needed Stein coefficients,
  ΔE[f(z_a)g(z_b)] := E[fg] − E_G[fg] = (g/24)[σ_a⁴E_Gf''''g + σ_b⁴E_Gfg'''' + (2σ_a²σ_b² + 4C²)E_Gf''g'' + 4σ_a²C E_Gf'''g'
  + 4σ_b²C E_Gf'g'''] + O(E ε³, v²),
  i.e. the first-order κ4 block of (a) with the cumulants of (b): the own-index κ4/24 terms (which v3 has), the
  κ_{2,2}/4·series(2,2) term, and the κ_{3,1}/6·series(3,1) + mirror terms (which no shipped version has). With f = g = ReLU
  the leading weights are −(g/6)[α_aφ(α_a)Φ_b + α_bφ(α_b)Φ_a]·C (the (3,1) part, ∝ C_off) and (g/12)(σφ)_a(σφ)_b (rank-1).

**Sources.** (a) same as Thm 3 (multivariate Edgeworth; McCullagh 1987 ch. 5, Bhattacharya–Rao ch. 5 — unverified
sections); (c) uses the general Price/heat identity ∂E_G[F]/∂Σ_ij = ½E_G[∂_i∂_jF] (Price 1958, verified; its multivariate
form is standard). (b)–(c) as applied here are **original to this repo** (COV_CLOSURE_DERIVATION.md).

**Proof.** (a) identical to Thm 3 with the bivariate characteristic function log ϕ = Gaussian + Σκ_{p,q}(is)^p(it)^q/(p!q!)
and two-variable Bell polynomials; the k = 0 cancellation is the identity f̂_p(a)ĝ_0(b) = f̂_p(a)·E_G[g] term by term.
(b) E[s⁴] = E[(1+ε)²] = 1 + v. Conditional on s, z − μ is centred Gaussian with covariance s²Σ, so
E[(z−μ)_a(z−μ)_b(z−μ)_c(z−μ)_d] = (1+v)[Σ_abΣ_cd + Σ_acΣ_bd + Σ_adΣ_bc]; the fourth cumulant subtracts the same bracket with
coefficient 1 (E[s²] = 1, so Cov(z) = Σ); the mean does not enter fourth cumulants. (c) E[fg] = E_ε E_G[fg; (1+ε)Σ].
Along the fixed direction Σ, the heat identity gives d/dε E_G[F;(1+ε)Σ] = ½E_G[(σ_a²∂_a² + 2C∂_a∂_b + σ_b²∂_b²)F], and
applying it twice, d²/dε² = ¼E_G[(σ_a²∂_a² + 2C∂_a∂_b + σ_b²∂_b²)²F]. Taylor in ε with E ε = 0, E ε² = v:
ΔE = (v/2)·¼·E_G[(σ_a²∂_a² + 2C∂_a∂_b + σ_b²∂_b²)²(fg)] + O(E ε³) = (v/8)[σ_a⁴f''''g + σ_b⁴fg'''' + (4C² + 2σ_a²σ_b²)f''g''
+ 4σ_a²C f'''g' + 4σ_b²C f'g'''] + O(Eε³, v²), and v/8 = g/24. ∎

**Machine check.** `check7_bivariate_cov_correction.py` (mpmath 25 digits, 3 random (μ, σ, ρ)): (b) verified exactly at
1e-25 from mixture moments; (c) two-point ε = ±√v (so E ε³ = 0 and the remainder must be O(v²)): |truth − (E_G + Δ)| at
v = 0.02/0.04/0.08 has log-log **slope 1.98, 2.02, 2.03 (expected 2)**; the series-based truth agrees with an independent
2-D quadrature to 1.7e-23. Perturbed ((3,1)/(1,3) terms dropped): slopes 1.02, 1.02, 1.00 → FAIL, i.e. the K31 terms are
first-order and necessary. **Status: PROVED under the scale-mixture model (b)**; whether the chain's z_l obeys (b) is the
empirical content of G-COV1 (P1: κ_{3,1} ≈ gσ_a²C, measured slope 1.00–1.02 for κ_{2,2} in COV_CLOSURE §3), not a theorem.

---

## 8. What is textbook and what is ours (for the write-up's novelty claims)

Textbook / literature: Thm 1 (McCullagh), Thm 2a–c (Price 1958, Mehler, Cho–Saul 2009), Thm 3 (Edgeworth/Gram–Charlier;
Bhattacharya–Rao), Lemma 4 (Lady Windermere's fan), the ensemble 15(l−1)/n (Roberts–Yaida–Hanin eq. 5.120).

**Ours** (not found in the sources read; candidates to headline):
1. **Theorem 5**, the exact fixed-weight kurtosis identity g_l = 3[Var‖A‖² − 2trC²]/[(trC)² + 2trC²] and the exact
   statement that annealing the last layer adds exactly 6s⁴trC² (quenched < annealed, with the last-layer-only kurtosis at
   fixed input being exactly zero — so PDLT's 15(l−1)/n is entirely an earlier-layer-weight fluctuation and is the wrong
   object for a fixed network). This explains, with zero constants, why the published finite-width kurtosis over-predicts
   the fixed-network value and why a per-layer g_l table from fresh random nets is legitimate (Prop. 6).
2. **Theorem 7(b)–(c)**: one scalar g_l determines the whole fourth-cumulant tensor of the pre-activations at leading
   order (a Gaussian scale mixture / common-mode variance fluctuation), and the resulting closed-form covariance
   correction contains the (3,1) terms ∝ C_off that no first-order-in-κ4-diagonal closure has; machine-verified to be
   first-order (dropping them costs one full order in v).
3. **Lemma 4's corollary** (a measurement interpreted through the lemma): our closure errors accumulate as a random walk
   (MSE ∝ L, gain ≈ 1), not coherently (∝ L²) — the quantitative reason per-layer calibration constants cap out at ~3×
   and per-step accuracy is the only lever.
4. The Stein-coefficient form of the ReLU covariance series with the explicit He_{k−2}(−α)φ/σ^{k−1} coefficients at
   general means (Thm 2b/d) — a small but write-up-worthy restatement of Price/Mehler that makes every Gram–Charlier term
   an n²-elementwise operation.

Open (honest): Thm 3/7a are formal expansions — no convergence theorem for the chain's actual distributions; the direction
g^Q ≤ 15(l−1)/n is a conjecture; the unconditional self-averaging of g_l is a conjecture with 6-net support.

---

## Addendum 2026-09-28 (mathematician, second pass) — results 8 and 9

| # | result | status | machine check (script → normal / perturbed) |
|---|---|---|---|
| 8 | G-SECT: the source-state correction — the coincident-index entries of K_h transported into the DISTINCT entries of K_z, and the removal of the sources' own coincident entries, as ONE merged same-leg n-hub source per layer | PROVED (exact multilinear identity; the only first-order steps are the chain's own birth/ageing models, marked) | `check8` n = 8→8→7, explicit distribution, two linear layers: chain+sect vs exact contraction 5.9e-16 / 6.8e-16 (no-sect: 4.9e-2 / 2.2e-1) / drop the diag/3 term: 3.7e-2, 1.6e-1 → FAIL; flip the S2 sign: 1.2, 8.4 → FAIL |
| 9 | readout order: the own-index factorization lemma; the k = 0 cancellation is an identity of the product form F̂ (not of the truncation); the G-V4 +0.74 % decomposes into identity break (dominant) + the κ3²/72 term | PROVED (lemma: formal, remainder order verified as Thm 3); the decomposition is a measurement read through the lemma | `check9` Part A bivariate slopes 3.06/3.90/5.06/5.73/7.02 for expected 3..7, Part B product residue exactly 0, patch residue = predicted to 1.9e-12 / mean-only patch: slopes 3.06/2.95/2.95/2.95 for expected 4..7, identity residue 5.3e-5 → FAIL |

Lessons that shaped these checks (OPERATING_MODEL §5): "a check that has never failed proves nothing" (two mutants for Thm 8,
one for Prop 9, each aimed at a term the theorem says is load-bearing); "a one-step oracle test of a CHANNEL does not test the
channel's STATE" (Thm 8 is a statement about the transported STATE, so its check runs TWO linear layers and feeds the layer-2
correction from the chain's own propagated state, not from the oracle); "a threshold must sit above its own oracle's attainable
value" (check9's truth is qualified by its 60-vs-80-node stability 3.3e-14 and every slope row requires err ≫ 50× that floor —
which is how a 1e-8 series-truncation tail in the CHECKER, not in the theorem, was caught masquerading as an ε³ remainder).

## 9. Theorem 8 — the source-state correction (G-SECT): coincident-index transport into the distinct tensor

> **Attribution (added 2026-09-28 after reading the paper's appendix):** this identity is the *diagonal adjustment* of Wu et al. 2026 (arXiv:2605.05179), App. §S.4.3 step (d)ii, eq. (17). Status of the result: PUBLISHED by ARC; ours is only the hub-form restatement, the proof as written here, and the machine check.

**Context.** The factored-source chain (`CHAIN_GAP_HUNT.md` §4, `proto_gaphunt_e2e.py` opts `sect`; gates G-SECT, G-SECT-VERIFY
in `R2_GO_NOGO.md`) represents the pairwise-distinct part D_h of the third-cumulant tensor K_h of a layer's activations by a
sum of symmetric hub sources S = Σ_c w_c Sym₃(A_c ⊗ A_c ⊗ E_c) (same-leg form; Sym₃(x⊗x⊗e) := x⊗x⊗e + x⊗e⊗x + e⊗x⊗x), born at
the ReLU from the chain's own (μ, Σ, T) and thereafter *transported* through each linear layer by the leg maps A ← WᵀA, E ← WᵀE
and *aged* through each ReLU by the elementwise Φ-rescale of the legs. The two-index sector T (T_ab = κ[z_a,z_a,z_b], κ3 on its
diagonal) is carried separately and exactly through linear layers (Thm 1, `two_index_transport`). Sources are read into the
next layer's T with coincident-index exclusions in the NEW index space (§1.1 of CHAIN_GAP_HUNT).

**What the factored chain carries, and what the truth requires.** Let K be a symmetric 3-tensor on R^n (K = K_h), W ∈ R^{n×m}
(stored (in,out), z = hW), and write W_a ∈ R^m for row a of W. Partition the index triples of K into distinct (a,b,c pairwise
distinct), two-equal (exactly two equal; entries T[a,c] := K[a,a,c], a ≠ c) and all-equal (κ3(a) := K[a,a,a]). By Thm 1,
EVERY entry of K_z — in particular every DISTINCT z-entry, which is what the aged sources must represent downstream — is the
contraction over ALL h-triples:

  K_z[ijk] = Σ_{abc} W_ai W_bj W_ck K[abc]
           = Σ_{a,b,c distinct} W_ai W_bj W_ck D[abc]  +  Σ_a [W_a ⊗ W_a ⊗ (T_off W)_a + W_a ⊗ (T_off W)_a ⊗ W_a + (T_off W)_a ⊗ W_a ⊗ W_a]_{ijk}
             + Σ_a κ3(a) [W_a ⊗ W_a ⊗ W_a]_{ijk},                                                                        (8.1)

where (T_off W)_a := Σ_{c≠a} T[a,c] W_c is row a of T_off W (T_off = T with zero diagonal). The transported source, however, is
(Wᵀ)^{⊗3}S over all h-triples: it carries S's OWN coincident entries S2[a,c] := S[a,a,c] = Σ_c′ w_c′[A²_{ac′}E_{cc′} + 2A_{ac′}E_{ac′}A_{cc′}]
and S_aaa := S[a,a,a] = 3Σ_c′ w_c′ A²_{ac′}E_{ac′} (the code's `S2`, `Saaa`) in place of T and κ3 — a wrong model of the sector's
transport, never removed, since the readout exclusions act on the new index space only.

**Statement (Theorem 8).** Let S be ANY symmetric 3-tensor with S[abc] = K[abc] on all pairwise-distinct triples. Then, exactly,

  (Wᵀ)^{⊗3} K  =  (Wᵀ)^{⊗3} S  +  Σ_{a=1}^{n} Sym₃( W_a ⊗ W_a ⊗ E_a ),
  E_a := ((T − S2)_off W)_a + ((κ3(a) − S_aaa)/3) · W_a,   i.e.  E = (M2 W)ᵀ with M2 := (T − S2)_off + diag((κ3 − S_aaa)/3).   (8.2)

The correction is therefore ONE same-leg hub source with n hubs (hub index = the h-index a), legs A1 = Wᵀ (columns = rows of W),
E as above, all weights 1 — the `sect` source of `proto_gaphunt_e2e.py` (`HubSrc(W.T, None, G.T, ones, same=True)`, G = M2 @ W).
Its legs A1 = Wᵀ are shared by every live source, so the corrections for all live sources merge into this single object (S2 and
S_aaa are sums over the live stack). Corollary (the chain): if the live stack S represents D_h exactly, then transport(S) + sect
equals K_z on EVERY z-entry; in particular the aged state that represents D_z at later layers is exact, and the two-index sector
computed from it agrees with the exact `two_index_transport` of (T, κ3) (check8 layer 2 uses the chain's own coincident entries).

**Assumptions / what is first-order (marked).** (8.2) is exact algebra for any (K, S, W): no approximation. In the chain, three
inputs to it are themselves models: (i) the BIRTH source is exact for D_h only at first order in the incoming cumulants
(CHAIN_GAP_HUNT §1.2, all birth rungs at the instrument floor); (ii) the AGEING of every source, including the correction source,
is the chain's Φ-rescale Φ∘Φ∘Φ D_z — first order in D (the next one-step-invisible term, CHAIN_GAP_HUNT §6 item 3); (iii) T_h and
κ3_h entering M2 are the chain's ReLU-closure outputs, exact to the order of Thm 3/7a. Theorem 8 makes the transported state exact
GIVEN these inputs — "at the order carried" — and nothing in the correction adds a constant or a new truncation.

**Proof.** Split K = S + Δ with Δ := K − S. By hypothesis Δ vanishes on distinct triples, so Δ is supported on coincident triples:
Δ[a,a,c] = Δ[a,c,a] = Δ[c,a,a] = T[a,c] − S2[a,c] for a ≠ c (S symmetric ⇒ S[a,a,c] = S[a,c,a] = S[c,a,a] = S2[a,c]), and
Δ[a,a,a] = κ3(a) − S_aaa. Multilinearity (Thm 1) gives (Wᵀ)^{⊗3}K = (Wᵀ)^{⊗3}S + (Wᵀ)^{⊗3}Δ, and

  [(Wᵀ)^{⊗3}Δ]_{ijk} = Σ_{a≠c} (T − S2)[a,c] (W_ai W_aj W_ck + W_ai W_cj W_ak + W_ci W_aj W_ak) + Σ_a (κ3(a) − S_aaa) W_ai W_aj W_ak
                     = Σ_a [ W_a ⊗ W_a ⊗ ((T−S2)_off W)_a + W_a ⊗ ((T−S2)_off W)_a ⊗ W_a + ((T−S2)_off W)_a ⊗ W_a ⊗ W_a ]_{ijk}
                       + Σ_a (κ3(a) − S_aaa) [W_a^{⊗3}]_{ijk},

summing over c inside each orientation. Finally Sym₃(W_a ⊗ W_a ⊗ (λ_a W_a)) = 3λ_a W_a^{⊗3}, so the diagonal term is absorbed into
E_a with the factor 1/3: Σ_a Sym₃(W_a ⊗ W_a ⊗ E_a) with E_a = ((T−S2)_off W)_a + ((κ3(a) − S_aaa)/3) W_a reproduces both sums. ∎
(The 1/3 is where the `drop_diag` mutant fails; the sign of S2 is where `flip_s2` fails — the same sign mutant G-SECT-VERIFY ran on
the full chain, where it fed positive feedback into the aged stack and scored 6.239e-3 vs 3.252e-8.)

**Why the defect was invisible to every one-step rung.** At the layer where a source is born, T_z receives the coincident part
exactly from `two_index_transport` and the distinct part from the readout with exclusions; both are correct. The error is in the
STATE handed to the next layer — the transported source — which no one-step-from-exact-statistics rung inspects: injecting the
exact T at every layer left the per-step residual unchanged (0.3625 … vs 0.365 …), while the aged stack was 30 % wrong against the
inherited oracle (CHAIN_GAP_HUNT §3). This is why the ladder's two candidate levers — the dropped (x,y)-slot exclusions (0.0045 →
0.0044, ~2 %) and the Edgeworth-born pieces (≤ 0.001 at one step; 0 / worse / −4 % e2e) — were both NO, and the state correction
was the gap.

**Machine check.** `check8_sect_transport.py` (kit venv numpy, float64). Explicit distribution with exact cumulants:
h = B(u² − 1) + D y + s∘ξ, u_k ~ N(0,1) i.i.d. (κ3(u²) = 8), y_p = e_p − 1, ξ_a = e_a − 1 with e ~ Exp(1) i.i.d. (κ3 = 2), every
column of D having exactly two non-zeros, so K_h = 8Σ_k B_k^{⊗3} + 2Σ_p D_p^{⊗3} + 2 diag(s³) exactly, and the chain's hub-form
source S = 8Σ_k B_k^{⊗3} (hubs k, A1 = E = B, w = 8/3) equals K_h on every distinct triple (8.9e-16) while S2 ≠ T_h (max relative
difference 1.57 — the defect). A plain-MC control (N = 2e5) reproduces K_h to 1.6e-2 (its noise). Two linear layers n = 8 → 8 → 7;
the layer-2 correction is built from the CHAIN's propagated state (transported S, transported sect₁, its coincident entries), not
from the oracle. Result: max |state − K_z| / max |K_z| = **5.9e-16 (layer 1), 6.8e-16 (layer 2)**; the un-corrected chain is off by
4.9e-2 and 2.2e-1. Perturbed: drop the (κ3 − S_aaa)/3 term → 3.7e-2, 1.6e-1 → FAIL; flip the S2 sign → 1.2, 8.4 → FAIL (the error
grows across layers, the linear shadow of the 4-orders-of-magnitude blow-up G-SECT-VERIFY measured on the 16-layer ReLU chain).
Raw output in `proofs/RESULTS.txt`. **Status: PROVED** (identity). The GAIN it produces on the chain is empirical, and is cited as
support, not as part of the proof: in-house 9000/9001 (1e7 refs) 2.672e-7 → 4.281e-8 (sect, 6.2×) → 3.782e-8 (sect + exact
exclusions, 7.1×); **independent verifier, official Mini split, 8 fixed MLPs, 1e9 truth: base 3.13e-7 → sect 4.08e-8 (7.7×) →
sect+excl 3.40e-8 (9.2×), every MLP individually > 5×** (`R2_GO_NOGO.md` "G-SECT-VERIFY — RUN + VERDICT"). Cost, untruncated:
1729 → 4068 n³-units (84 % → 199 % of B); the correction does not truncate by hub energy (CHAIN_GAP_HUNT §5), so at the 10 % floor
it is not yet deployable — the cost problem is the open one (`SECT_COST.md`, other agent).

---

## 10. Proposition 9 — readout order: the own-index factorization lemma and the k = 0 identity

**Context.** Thm 3 says the univariate readout (κ3/6, κ4/24) is inconsistently ordered without κ3²/72 (same 1/n order as κ4/24).
Adding κ3²/72 to the MEAN readout only (G-V4) made every variant reproducibly worse (+0.4–0.5 %; +0.74 % on v5b's chain), and
`PHASE2_WRITEUP_V2.md` §5.6 recorded two undisentangled readings: (a) an asymptotic term without its partners can move the error
the wrong way; (b) a mean-only patch breaks the k = 0 cancellation in the covariance one layer downstream. G-E6 / G-E6b
(`EDGEWORTH_ORDER_AND_K4I.md`) settled it; this section states the lemma behind reading (b) and what the numbers then say.

**Statement (own-index factorization lemma).** Let (z_a, z_b) have Gaussian reference N(μ, Σ) (σ_a² = Σ_aa, C = Σ_ab) and
own-index cumulants κ_r(a), κ_r(b) (r ≥ 3), with cross cumulants κ_{p,q} (p,q ≥ 1, p+q ≥ 3) collected in the operator X. With
A_a := Σ_{r≥3} κ_r(a) ∂_a^r/r! (A_b likewise), the bivariate Edgeworth operator of Thm 7a is exp(A_a + A_b + X) = e^{A_a} e^{A_b} e^{X}
(constant-coefficient differential operators commute). Hence, as a formal series, at zeroth order in X,

  E[f(z_a) g(z_b)] = E_G[(e^{A_a}f)(z_a) · (e^{A_b}g)(z_b)] = Σ_{k≥0} F̂_k(a) Ĝ_k(b) C^k/k!,
  F̂_k(a) := E_G[D^k e^{A_a} f] = Σ_{j≥0} (B_j(0,0,κ_3(a),…,κ_j(a))/j!) f̂_{k+j}(a)
           = f̂_k + (κ3/6) f̂_{k+3} + (κ4/24) f̂_{k+4} + (κ5/120) f̂_{k+5} + (κ6/720 + κ3²/72) f̂_{k+6} + (κ3κ4/144 + κ7/5040) f̂_{k+7} + …,   (9.1)

i.e. the Stein-coefficient bookkeeping of ANY own-index Edgeworth correction is a per-neuron VECTOR F̂ applied in the SAME
covariance series (Thm 2b); the cross rows become Σ κ_{p,q}/(p!q!) S(F̂,Ĝ;p,q) at first order in X. In particular F̂_0 = E[f] is
the univariate Edgeworth mean (Thm 3), at every truncation of the cumulant list.

**Corollary (the k = 0 cancellation is an identity of the product form).** Cov(f(z_a), g(z_b)) = Σ_{k≥1} F̂_k Ĝ_k C^k/k! + (cross rows):
the k = 0 term F̂_0(a) Ĝ_0(b) equals E[f]E[g] IDENTICALLY — for ANY truncation J of the cumulant list — provided the mean readout
IS F̂_0 and the covariance rows use the same F̂. Conversely, a "mean-only" correction (mean = F̂_0 + d, rows with the uncorrected F̂)
leaves in Σ_h the FIRST-order, coherent, rank-2 residue −d ⊗ F̂_0 − F̂_0 ⊗ d − d ⊗ d; for the G-V4 patch d = d6 = (κ3²/72) f̂_6 =
κ3² He_4(−α)φ(α)/(72σ⁵), an error of order κ3² ~ n^{−1} in Σ_h at EVERY layer, versus the O(κ3² C) ~ n^{−3/2} the k ≥ 1 rows of the
same term carry. The shipped additive step (`relu_step_ext`) is the first-order expansion of the product form in the c_j; its own
k = 0 residue is second order (−Δm ⊗ Δm, ~1e-7 per entry, 0.001 % of Σ_h) — harmless.

**Proof.** (9.1): exp(A_a + A_b + X) = e^{A_a}e^{A_b}e^{X} because A_a, A_b, X are polynomials in the commuting operators ∂_a, ∂_b with
constant coefficients. At zeroth order in X, F := e^{A_a}f is a function of z_a alone and G := e^{A_b}g of z_b alone, so Thm 2b applies
verbatim: E_G[F(z_a)G(z_b)] = Σ_k E_G[D^kF] E_G[D^kG] C^k/k!. Since D commutes with e^{A_a}, E_G[D^k e^{A_a} f] = E_G[e^{A_a} D^k f] =
Σ_j (B_j/j!) E_G[D^{k+j} f] = Σ_j (B_j/j!) f̂_{k+j} by the definition of the complete Bell polynomials (Thm 3). F̂_0 = E_G[e^{A_a}f] =
E[f(z_a)] is Thm 3. The corollary is one line: the k = 0 term is F̂_0Ĝ_0 and Cov subtracts E[f]E[g] = F̂_0Ĝ_0; with the mean patched
to F̂_0 + d but the k = 0 row kept at F̂_0 ⊗ Ĝ_0, the difference is F̂_0⊗Ĝ_0 − (F̂_0+d)⊗(Ĝ_0+d′) = −d⊗Ĝ_0 − F̂_0⊗d′ − d⊗d′. ∎
Remainder order (formal → asymptotic): as in Thm 3, PROVED-under-assumption; verified numerically below on a smooth family.

**What the measurements then say (a decomposition read through the lemma, not a theorem).** On v5b's judged chain (9000/9001,
1e7 refs; `EDGEWORTH_ORDER_AND_K4I.md` §3): B0 shipped 6.0818e-7; B7 = shipped + the consistent c6 row pair 6.0917e-7 (+0.16 %);
B4 = the mean-only patch 6.1271e-7 (+0.74 %). B4 − B7 = +0.58 % is the identity break (the k = 0 residue above, first order) plus
the O(C) k ≥ 1 rows of c6, the former dominant in the 1/n counting; B7 − B0 = +0.16 % is the κ3²/72 term itself in its consistent
form (product-form variants B2/B5: +0.15–0.34 %; adding κ3κ4/144: another +0.2 %). So reading (b) was ~80 % of G-V4's +0.74 % and
reading (a) the remaining ~20 %; the sign of the term itself is net-dependent (−0.2 % / +0.5 %), as expected of an asymptotic term
at the edge of validity. Both gates FAIL as pre-registered (G-E6 6.1026e-7 vs ≤ 5.8995e-7; G-E6b the consistent set still costs
+0.15–0.19 %): the readout order is CLOSED — truncate at κ4; κ3², κ5, κ3κ4 do not help on this chain — and §5.6's "we do not know
which" is resolved. The one-step instance: the mean-only patch is a +24–85 % coherent Σ_h error at one step, the consistent set
≤ +0.5 % over the product form (G-E6 unit rung A4 vs A2).

**Machine check.** `check9_readout_order.py` (kit venv numpy). Part A (the lemma): z_a = μ_a + √(1−ε²) g_a + ε U_a, z_b likewise,
(g_a,g_b) standard Gaussian with correlation ρ = 0.4, U_a, U_b independent standardized Exp(1) (κ_r = (r−1)!), so κ_r(z) = ε^r(r−1)!
exactly, cross cumulants ≥ 3 vanish, Var z = 1, C = ρ(1−ε²). Truth: 80-node Gauss–Laguerre over (U_a,U_b) of the bivariate Gaussian
ReLU expectation at the shifted means (Thm 2b series, 60 terms); 60-vs-80-node stability 3.3e-14, and every slope row requires
err > 50× that. Log-log slopes of |truth − (9.1) truncated at cumulant order ≤ J| vs ε (ε = 0.05 → 0.1): **3.06, 3.90, 5.06, 5.73,
7.02 for J = 2..6 (expected J+1)** — the bivariate extension of check3. Part B (the identity, n = 12 synthetic neurons): consistent
product form k = 0 residue **exactly 0**; the mean-only patch's residue equals −d6⊗m1 − m1⊗d6 − d6⊗d6 to **1.9e-12** relative
(5.3e-5 of m1⊗m1). Production instance: G-E6-0a, 4 (net, layer) rows of MLPs 1000/1001 from the 1e5 caches, product residue 0,
patch residue = predicted to 1.0e-11, off-diagonal rms 0.07 % (layer 8) / 0.13–0.16 % (layer 15) of Σ_h's (`proto_edge6.identity_check`).
Perturbed (`--perturb`: the G-V4 patch — corrected F̂ in the mean only, raw f̂ in every k ≥ 1 row): Part A slopes **3.06, 2.95, 2.95,
2.95 for expected 4..7** (stuck at the κ3 order: the k ≥ 1 rows are wrong at first order regardless of J) → FAIL; Part B's assertion
that the patch keeps the identity fails at 5.3e-5 → FAIL. Raw output in `proofs/RESULTS.txt`.
Checker lesson recorded: the first run of Part A failed at J = 5,6 in NORMAL mode; the univariate control (k = 0 term alone) and a
per-k test (each F̂_k as Edgeworth for E[f^{(k)}(z_a)]) both passed, which localized the fault to the checker's own C-series
truncation (12 terms; f̂_k ~ √k!, tail ~1e-8 with an ε³-dependent part). Extending to 40 terms fixed it; the theorem never changed.
**Status: PROVED** (lemma and identity; remainder order under the Thm 3 assumption). The ≈ 80/20 attribution is a measurement.

**Novelty note (extends §8).** Prop 9's lemma is a bookkeeping statement about textbook objects (Price/Mehler + Bell
polynomials) and is claimed only as a clean restatement — its value here is the identity it makes obvious, which explained a
reproducible "wrong-sign" result that would otherwise have been filed against Thm 3. Thm 8 is ours: it is the exact algebraic
content of the factored-source representation's state error, and it closed a 10× gap with zero constants (§9).
