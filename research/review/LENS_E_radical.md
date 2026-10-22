# LENS E — radical representations for E[ReLU(z_L)] at util ≤ 0.13 (theory-only consult, 2026-10-10)

Agent: lens-E (Fable 5.1), ~2 h, no heavy compute. One numpy check (< 1 min, 200k-sample generator-net cache, §3.3). Files read: BREAKTHROUGH, NEWREP, GAP504,
MODEL_ERROR, ERROR_BUDGET, DESIGN, COV_CLOSURE_DERIVATION, FINITE_WIDTH_LIT, SYNTHESIS, LENS_B, LENS_C §4, OPERATING_MODEL §5, R2_GO_NOGO G-RB50–60.
Nothing edited outside this file. Closed families (sampling/QMC/hybrids/CV, k-mode, polarized CP, fold-at-birth, fixed-width hubs, young-only/slice-only,
final-layer tricks, learned-head refits) are not re-proposed; where a direction below reduces to one of them, it is killed by that pointer.

Units: 1 "matmul" = one dense n×n×n product = 2n³ FLOPs ≈ 2.15e9. Budget 2^41 ⇒ 1024 matmuls at util 1.0, 64/layer; util 0.10 = 6.4 matmuls/layer natural,
≈ 12.5 dense-equivalents when every dense product is billed at Strassen d5 (×0.513). Covariance Σ_z = WᵀΣ_hW costs 2 (1.5 symmetric), billed ≈ 1.
**So util ≤ 0.13 ⇒ ≤ 8.3 natural ⇒ ≤ 16 dense-equivalents/layer at d5 ⇒ ≤ 14 for everything that is not Σ.** Our young tier costs 4 matmuls/source-layer
(2 transports + 2 contractions, DESIGN S2); the old tier 1.5/0.875; v57 ≈ 30 units/layer.

## 0. Verdict first (blunt)

1. **No representation I can derive reaches util ≤ 0.13 at raw ≤ 2.2e-8.** The budget arithmetic above allows ≤ 3–4 CP sources alive in the P/A/read form
   (≤ 7 in a one-leg, no-read form), and YOUNG_CHAIN measured 4 sources at 6.7e-7 (×27). Every compression of OUR κ3 content has cliffed (G-RB44/60, G-FW,
   G-RB59). The structural reason (§1) is that **odd cumulants are quenched disorder** — κ3_z,i = Σ_{abc} W_ai W_bi W_ci κ3_h(abc) is a random-sign sum whose
   per-neuron value needs the full n³ tensor — while **even cumulants self-average** (positive weights W²W² ⇒ the (2,2)/(3,1) sectors collapse to a
   common-mode scale law, COV_CLOSURE §3). That asymmetry is why scalar/matrix closures work for κ4 and fail by ×40 for κ3, and it is not negotiable by
   representation choice: the information is n³ per layer unless the leaders' κ3 is *born* lower-rank than ours (unknown, not in any prose).
2. Of the brief's five directions, four are dead by derivation or by the numbers in §3 (adjoint all-layer is O(L²n³); scalar carriers lose the (1,1,1) part;
   chaos in an input basis is the k-mode kill; the 1/n perturbative mean correction IS the common-mode GSM κ4 law the chain already carries, and its
   analytic ensemble value is wrong by 1.5–3.2× for fixed W). The arc-cosine closure seat is already exact to all orders in C for the Gaussian part and
   first-order Edgeworth for κ3/κ4 — the missing content there is sector inputs, not the kernel.
3. What survives is two **zero-util** closure candidates (§2 G, H) with a combined prior ≈ 25 % of moving raw by ≥ 10 % (≈ 5.2e-9 → 4.7e-9), plus one new,
   specific, unmeasured seat: **the κ3 (1,1,1) transport is gated at zeroth order in C (f₁∘legs = Φ_aΦ_bΦ_c) while the exact gate is the trivariate orthant
   probability P(z_a,z_b,z_c > 0)**, whose first-order-in-C correction is ≈ 8 % rms relative at depth (ρ_rms 0.13, §2.G). Exact treatment is n⁴ (Khatri–Rao
   wall); its cheapest oracle is 1 h. Nothing here is a route to the leaders' ×2 on util.

## 1. Why the κ3 state is irreducible (the argument the brief asked to be taken seriously, with the answer)

Linearised transport: z_l = W_lᵀ h_{l−1}, h = ReLU(z); to first order the κ3 tensor of z transports as a congruence with W̃_l := diag(Φ_{l−1}) W_l
(Φ = gate probability = f₁): κ3_z^l ≈ κ3_z^{l−1}[W̃_l, W̃_l, W̃_l] + births. Over k layers the product P_{s→l} = W̃_{s+1}⋯W̃_l acts on the source born at s.

- **Per-entry scale.** With κ3_h(abc) off-diagonal ≈ 1/n (BREAKTHROUGH §3) the transported diagonal κ3_z,iii = Σ_{abc} P P P κ3(abc) sums n³ random-sign
  terms of size n^{−3/2}·n^{−1} → ≈ 1/n per entry, the same as the diagonal/(2,1) parts, but the (1,1,1) part carries n³ entries vs n (energy ×n²), so the
  next layer's reads are dominated by it (the √n factor BREAKTHROUGH measured). Measured: κ3_z rms 8.6e-3 at l=15 ≈ 9/n.
- **No matrix recursion.** Define the half-contraction R^l(i;a) := Σ_{bc} W̃_bi W̃_ci κ3^l(abc). Then R^{l+1}(i′;a′) = Σ_a W̃_{aa′} Σ_{bc} (W̃W̃′)_{bi′}(W̃W̃′)_{ci′} κ3^l(abc):
  the probe side composes multiplicatively (needs κ3^l again on NEW probes). No closed recursion on an n×n object exists; the state is the tensor.
- **No sufficient statistic smaller than the tensor.** The set of all future probes {columns of P_{s→l}, l > s} spans R^n (LENS_B §1a: column norms of the
  products have CV 0.03–0.13 — the products do not concentrate; no Lyapunov subspace at n=1024, G-RB46).
- **Generic rank.** The sum of 15 rank-n CP sources has CP rank ≤ 15n ≪ n²/6 (generic rank of a symmetric n×n×n tensor) — no algebraic compression; any
  truncation is the measured cliff.
- **Odd vs even.** κ4_z,i = Σ W_ai⁴ κ4_h(a) + 6Σ_{a<b} W_ai²W_bi² Q_h(ab) + random-sign terms. The positive-weight W²W² sum is coherent and self-averages →
  the measured law Q_z(ab) = (g/3)(σ_a²σ_b² + 2C_ab²), K31 = κ C — exactly a Gaussian scale mixture z = √s·ξ with Var(s) = g/3, which is PDLT's metric
  fluctuation V/n read along x instead of along W. A GSM is closed under linear maps (same s), so the common-mode κ4 transports exactly for free; the
  per-neuron 25 % scatter is the quenched remainder (G-RB30/37: corr 0.3, R² 0.03–0.15). Odd cumulants have no positive-weight sum, hence no law.

Consequence for cost: fewer sources alive is the only lever on κ3 cost, and that lever cliffs on our content. The leaders' bill (≈ 11–14 dense-equivalents
for κ3) therefore implies a κ3 content that is *intrinsically* ≤ 3-source-equivalent at equal accuracy — a different birth, not a different carrier.

## 2. Candidates (ranked by expected adjusted gain × prior). Ledgers per layer, matmuls; "d5" = billed at Strassen depth 5 (×0.513 on dense products).

### G. Exact-gating κ3 transport — the trivariate-orthant correction to the (1,1,1) sector (NEW seat; cheap forms only)
**Math.** Edgeworth to first order in κ3 and all orders in C: E[f_a f_b f_c] ∋ Σ_{p+q+r=3} κ_{pqr}/(p!q!r!) E_G[f^{(p)}_a f^{(q)}_b f^{(r)}_c]. For the (1,1,1)
component the coefficient is E_G[1_{z_a>0} 1_{z_b>0} 1_{z_c>0}] = P₃(a,b,c), the orthant probability, NOT Φ_aΦ_bΦ_c. The chain gates every transported leg by
f₁ = Φ (DESIGN step 4, eq 19), i.e. uses P₃ ≈ ΦΦΦ. First order in C:
  P₃ − Φ_aΦ_bΦ_c = C_ab g_a g_b Φ_c + C_ac g_a g_c Φ_b + C_bc g_b g_c Φ_a + O(C²),  g := f₂ = φ(α)/σ.
So the exact transported tensor is κ3_z ∘ (ΦΦΦ + Δ), a Hadamard product — the (2,1)/(3) slices get this exactly inside `relu_step_ext` (series all orders
in C), the (1,1,1) part does not. Size: per pair, relative correction ρ_ab·(σg)_a(σg)_b/(Φ_aΦ_b); for active neurons (|α| < 1, 40 % of them) (σg)² /Φ² ≈
0.36, ρ_rms = 0.13 at l=15 (COV_CLOSURE §0: Σ_z off rms 0.022 / var 0.17) → ≈ 0.047 per pair, three pairs → **≈ 8 % rms relative, random sign (sign of
C_ab), growing with depth** (ρ is inherited and grows; layer-1 ρ ≈ 2v/√n/v ≈ 0.06). Transported through random W, an 8 % random-sign perturbation of the
(1,1,1) tensor is an ≈ 8 % error of the next layer's κ3 state — the same order as the Tz seat MODEL_ERROR measured (−40 %/−16 %). No prose or gate has
isolated it. ARC's n^{−1/2} counting of C would call it O(1/n) (same order as κ4 — which they keep); at depth ρ is 4× the n^{−1/2} estimate, so the
counting under-prices it.
**Cost.** Exact: Hadamard of a rank-J CP tensor with Σ_pairs (C∘ggᵀ)⊗Φ — with C∘ggᵀ = Σ_m λ_m u_m u_mᵀ (flat bulk: rank ≈ n) → rank J·n; or per target
neuron a bilinear form in W_i → **n⁴ per layer. Dead exact (Khatri–Rao wall).** Rank-1 (norm mode, 10 % of the C variance): +3 gated transports + 3
contractions per source-layer = +6 matmuls/source-layer ≈ +9 pt util for ≤ 10 % of the correction: KILL on cost. **Cheap forms (the only ones worth an
oracle): (G1) mean-field gate renormalisation** Φ → Φ̃ = Φ + c·g∘(C(g∘Φ))·(something per layer) — the (b,c)-summed coherent part of Δ; n² per layer, util
+0; **(G2) learned per-neuron gate** Φ̃_a = Φ_a(1 + Σ_k θ_k ψ_k(a)) with ψ ∈ {g_a Σ_b C_ab g_b, g_a Σ_b C_ab² , α, Φ, φ/σ}, ≤ 10 constants per layer fit to the
oracle residual; util +0 (and the HEAD arm rule applies: refit MIX2 or show the uncorrected gain survives the shipped head).
| ledger (per layer) | exact | rank-1 | G1/G2 |
|---|---|---|---|
| natural matmuls | ∝ n (n⁴) | +6 per source-layer (≈ +60) | 0 (n²) |
| d5 billed | — | ≈ +30 | 0 |
**Oracle (1–2 h, FIT 0/2/4, N = 2^19 samples per net, one layer l ∈ {6, 12}; f32 forward; memory ≈ 2 GB per layer of h samples at 2^19).**
κ3_sample[(W_{l+1}ᵀ δh_l)_i] is the exact next-layer diagonal κ3 (truth); κ3_sample[(W̃ᵀ δz_l)_i] with W̃ = diag(Φ_l)W_{l+1} is the ΦΦΦ-gated transport of the
FULL κ3_z^l (all sectors); their difference D_i = births + slice-gating corrections (which the chain adds analytically) + the (1,1,1) orthant correction
(which it does not). Compute the chain's analytic birth+slice diagonal read B_i at that layer from MC-exact inputs (`relu_step_ext` + eq 18/20 blocks'
(3)-slice; the diagonal read is n² per column); residual E_i = D_i − B_i. A/B halves (2^18 each) give the noise floor: var(E) debiased = ⟨E_A E_B⟩.
**Kill bar:** debiased rms(E) < 3 % of rms(κ3_z^{l+1}) at l=12 (truth noise at 2^18: sqrt(15·var³/N) ≈ 2.1e-4·… ≈ 1.2e-3 per neuron; the A·B cross-term
resolves ≈ 1.2e-3/√1024 ≈ 4e-5 ≈ 0.5 % of 8.6e-3 — the bar is attainable). Secondary read: corr(E, first-order Δ-predicted correction computed from
MC κ3_z... not formable at n³) → instead regress E on the G1 mean-field vector g∘(C(g∘Φ))∘(Wᵀ-row structure) and on the ψ_k: **R² < 0.2 kills G1/G2**
even if the seat is real (then it is bulk-dominated, n⁴, and recorded as "the leaders' trick territory" with a number).
**Prior:** seat ≥ 20 % of the fresh κ3-state error: 25 %. G1/G2 capture ≥ half of it: 20 % conditional → **5 % joint for ≥ 10 % raw; ≈ 20 % for the
diagnostic to land a measured seat.** Predicted raw if G2 works: −8…−15 % uncorrected, ≈ half net of head.

### H. Learned pair-level Σ_h corrector with per-neuron-modulated sector features (util +0)
**Math.** MODEL_ERROR: Σ_h given its inputs carries 38 % (24–27 % net of κ4 inputs); G-RB27's ≤ 3 constants/layer on the three sector *terms* read R² ≈ 0
in-sample. Those constants scaled whole terms; the residual that matters is per-entry (my calibration: a per-entry rms error ε of Σ_h off-diagonal enters
var_z through the random projection Σ_{a≠b} W_ai W_bi δC_h(ab) with rms 0.02ε — structure-blind — and δμ_h = (φ/2σ)δσ²; ε ≈ 1–2 % ↔ 1.5e-9/layer fresh
(cross-checked against K=2's 1.3e-7 at ε ≈ 0.06 from the T-term, §3.3). So every O(1/n) pair term is at the needed scale and the fit must be
per-entry. Ansatz: δΣ_h(a,b) = Σ_k [u_kᵀΘ_k v_k](a,b) ∘ M_k(a,b), M_k ∈ {C, C², C³, T, Tᵀ, T∘C, 1}, u, v ∈ {1, Φ, φ/σ, αφ/σ², He₂φ/σ³, κ3·f, κ4·f} per
neuron (7×7 Θ per M_k ⇒ ≈ 340 constants, shared across layers 4–14 and nets; or per-layer × 4 depth bands). Least squares on the A-half residual
Σ_h^{MC,A} − Σ_h^{closure}(MC-exact inputs), scored on the B-half cross-product (A·B debiasing kills the 1.3 % MC floor that made G-RB27 read zero).
**Ledger:** 7 Hadamard-weighted n² terms ≈ 0.1 matmul-equivalent/layer (≈ 0.1 pt util), no dense product. d5 irrelevant.
**Oracle (1 h):** `proto_cov4.sectors` dumps on nets 9000/9001 (exist, layers 1–14, two halves). Fit on 9000, score on 9001: explained fraction of the
COHERENT residual energy ⟨r_A r_B⟩. **Kill bar: held-out explained fraction < 10 %, or the fitted δΣ raises the one-step var_z error on 9001.** Then e2e
FIT 0/2/4 uncorrected ≤ 0.95 AND the shipped-head arm ≤ 0.98 (SYNTHESIS standing rule).
**Prior:** 15 % (G-RB27/29 found per-neuron and per-layer reductions carry nothing; a bilinear per-neuron×pair form is the next cell up, untested; the
risk is that the residual is quenched like κ3 — G-RB27's "pair-structured, not derivable" reading). Predicted raw if it works: −8…−12 % (⅓ of the seat).

### I. The 1/n perturbative mean correction (brief's direction 5) — resolved, not a candidate
The O(1/n) correction to E[ReLU(z_i)] "from the covariance alone" is κ4_i/24·f₄ with κ4 the common-mode (self-averaging) part: κ4_i = g_l var_i². The chain
carries it (lean), with g_l from a universal table (FINITE_WIDTH_LIT: g self-averages to ±0.003) scaled ×0.92. The analytic ensemble value 15(l−1)/n
over-predicts fixed-W g by 1.5–3.2× (common-mode subtraction; FINITE_WIDTH_LIT §4), so "computed analytically" is worse than the table. The O(n^{−1/2})
term — κ3_i/6·f₃ — is the quenched one and dominates the carried-mean error; no covariance-only formula gives it (§1). The per-neuron κ4 remainder:
the quenched diagonal-excess transports as Σ_a W_ai⁴ κ4^{exc}_h(a) with Σ_a W_ai⁴ ≈ 12/n → **diluted to ≈ 4 % of κ4_z (0.012 × 6e-3 vs 1.9e-3)**: it is
not the 25 % scatter; the scatter is the transported off-diagonal κ4 content (G-RB37 Form B corr 0.3) — n⁴, dead. The one-layer identity
g = 3[Var_x‖A‖² − 2trC²]/[(trC)² + 2trC²] is exact but needs Var_x‖A‖² (a fourth-order statistic with no propagation rule). **KILL as a carried-mean fix;
prior ≤ 5 %.** What it DOES license: the GSM transport of the κ4 sector is exact and free (the chain already uses it), and any future κ4 sector work should be
phrased as "quenched remainder of a GSM", not as a new core.

### J. Adjoint / probe dual (brief's direction 1) — derived; O(L n³) exists for the FINAL layer only
With gates frozen from a K=2 pre-pass (Φ accurate to 1e-3, LENS_B §1 — a 1e-3 relative gate error moves the κ3 mean term by ≈ 2e-6, negligible), all
transport maps are known. Backward chain Q_L = I, Q_{l} = W̃_{l+1} Q_{l+1}: one matmul/layer gives every P_{s→L} = Q_s simultaneously; the final-layer κ3
diagonal of ALL sources is then Σ_j Π_m (Q_sᵀ m_j^{(s)})_i: 2 matmuls per source (P leg = Q_sᵀ free) → **≈ 3L = 45 matmuls for the whole net (0.045 util)
with no aging truncation.** Worth ≈ nothing: aging costs 2.7 % raw in total (ERROR_BUDGET) and the final-layer read is ≤ 8 % even with MC-exact κ3
(G-RB47); it is also a "final-layer trick" (closed). **All layers:** the output needs Σ_{s<l} cubic_s(Q_{s→l}) for every pair (s,l); the products Q_{s→l}
share no factor across s at fixed l (and none across l at fixed s except by the forward recursion the chain already runs), so any exact scheme is
Θ(L²) matmuls — the forward chain IS the optimal ordering. Reweighting by output sensitivity: dead (CV ≤ 0.13, LENS_B §1a). **No candidate.**

### K. Per-neuron scalars / n×n matrices instead of tensors (brief's direction 2) — what is lost, with numbers
Lost: the (1,1,1) part, i.e. n³ − 3n² entries carrying ×n² the energy of the slices (§1); measured as slice-only/memoryless 9e-7 (×40) and G-RB60
(old tier as a live-state functional: held-out R² 0.69, 25–35 % irreducible). **KILL.** The even-cumulant analogue WORKS (GSM law, §1) — already in the chain.

### L. Wiener/Hermite chaos in a learned input basis (direction 3) — KILL by existing measurement
h_L(x) retains ≈ 0.73 of its variance per layer in the linear chaos → 0.6 % at L=16 (LENS_B §5); conditioning on the top-128 covariance modes with exact
moments reaches only 3.5e-8 (G-RB46), tracking captured variance with no concentration. A degree-k chaos in an r-dim input basis costs r^k coefficients
per output and captures the variance fraction of that basis. **Prior 2 %.**

### M. Arc-cosine kernel + Edgeworth as the closure seat (direction 4) — the kernel is already exact
The Gaussian part of Cov(ReLU_a, ReLU_b) is the Mehler series to all orders in C (KH=8 converged, ERROR_BUDGET: KH 10/12 identical). The non-Gaussian part
is first-order Edgeworth in the exact bivariate cumulants (κ3 diag, T, Tᵀ, κ4 diag, K31, Q) — all orders in C per term. Second-order κ3×κ3 is **killed
by the number in §3.3** (1 % of the first-order T term, 0.06 % of Σ_h). Higher common-mode cumulants (κ6 of the scale mixture) are O(Var(s)) ≈ 2 % of the
κ4 term ≈ 0.01 % of Σ_h. **The seat is sector inputs (K4 −30 %, Tz) and the one new term is G above.** No candidate.

### N. Sample-carried (1,1,1) κ3 (hybrid analytic/particle) — KILL by noise
A particle representation of κ3_h with N columns costs 2N/n matmuls/layer for all sources at once (2 at N=n) — the only representation that is O(L n³)
for the whole state. Its per-neuron κ3 noise is √(15 var³/N) = 6.0e-3 at N=2048 vs the signal 8.6e-3; to reach 5 % of signal needs N ≈ 8e5 → ≈ 1600
matmuls/layer. **Prior 0.**

## 3. Numbers used (and the one check run)

3.1 Budget: 2^41 / (2·1024³) = 1024 matmuls; 64/layer; util 0.10 → 6.4 natural, 12.5 d5-equivalent; 0.13 → 8.3 / 16.
3.2 Required accuracy: final MSE 1e-8 ↔ 1e-4 per neuron; κ3 term κ3/6·f₃ ≈ 1–2e-3 ⇒ κ3 per neuron to ≈ 5 %; κ4 term κ4/24·f₄ ≈ 4e-4 ⇒ κ4 to ≈ 25 %
(the measured 26 % per-neuron error ↔ ≈ 3e-5/neuron/layer ↔ Σ_l gain_l·1e-9 ≈ 7e-9 ≈ 30 % of 2.3e-8 — reproduces the K4 seat from first principles).
3.3 **Check run** (`mc_cache_alllayers_mlp0_N200000.npz`, generator net, z-side exact T_z, κ3_z, μ, var; layers 8/12/15; off-diagonal rms):
| l | first-order T term T_ab f₂_aΦ_b/2 (+sym) | κ3_a T_ab/12 f₅Φ_b | κ3_a T_ba/12 f₄ f₂ | κ3_aκ3_b/36 f₃f₃ | T²/8 f₄f₂ | TTᵀ/4 f₃f₃ | rms κ3 | rms T |
|---|---|---|---|---|---|---|---|---|
| 8 | 7.8e-4 | 6.0e-6 | 1.0e-6 | 2.9e-7 | 7.2e-7 | 4.6e-7 | 1.08e-2 | 3.9e-3 |
| 12 | 6.7e-4 | 6.6e-6 | 7.9e-7 | 2.1e-7 | 5.8e-7 | 3.9e-7 | 9.7e-3 | 3.5e-3 |
| 15 | 5.9e-4 | 6.7e-6 | 6.4e-7 | 1.7e-7 | 5.0e-7 | 3.2e-7 | 8.6e-3 | 3.1e-3 |
Reading: the κ3 T-term is ≈ 6 % of Σ_h off-diagonal rms (0.010); every second-order κ3×κ3 term is ≤ 1 % of it (≤ 0.07 % of Σ_h) → consistent with
`cl2_second1`'s ±1–5 % noise and G-V4; the second-order block is not a seat. Also used for H's calibration (ε ≈ 0.06 from dropping T ↔ K=2's 1.3e-7).
3.4 G's size: ρ_rms(l=15) = 0.022/0.17 = 0.13; (σf₂)²/Φ² ≈ 0.36 for |α| < 1; per-pair 0.047; ×√3 ≈ 8 %.
3.5 I's dilution: Σ_a W_ai⁴ = n·(2/n)²·3 = 12/n = 0.012.

## 4. Ranked table (adjusted = raw × util; v57 ≈ 2.25e-8 × 0.236 = 5.3e-9)

| # | name | util | predicted raw (if it works) | oracle (1–2 h) | kill bar | prior | E[gain]×prior |
|---|---|---|---|---|---|---|---|
| 1 | **G** exact-gating κ3 transport (G2 learned per-neuron gate; G1 mean-field) | 0.236 (+0) | 2.0–2.1e-8 uncorrected, ≈ 2.15e-8 net of head | next-layer diag κ3 from samples minus ΦΦΦ-transport minus analytic births, FIT 0/2/4, l=12, 2^19 | debiased residual < 3 % of κ3 rms, OR R² < 0.2 on the mean-field/ψ_k regressors | seat 25 %, cheap capture 20 % → 5 % (diagnostic lands 20 %) | ≈ 0.5 % |
| 2 | **H** learned pair-level Σ_h corrector | 0.237 (+0.1 pt) | 2.0–2.1e-8 uncorrected | fit 9000 A-half residual, score 9001 ⟨r_A r_B⟩ | held-out coherent energy < 10 % | 15 % | ≈ 1.5 % |
| 3 | **J** backward-adjoint exact final read (all sources, no aging) | 0.236 → ≈ 0.19 if it REPLACED the old tier's final read… it cannot (state needed) | ≈ 1.00 | — (derived) | — | 0 as a score lever | 0 |
| 4 | **I** 1/n analytic mean correction (κ4 common mode) | +0 | ≈ 1.00 (chain already has it); per-neuron excess diluted to 4 % | — | — | ≤ 5 % | 0 |
| 5 | **M** second-order κ3×κ3 / κ6 closure terms | +0 | ≈ 1.00 (≤ 0.07 % of Σ_h) | §3.3 | killed by the number | — | 0 |
| 6 | **K** scalar/matrix κ3 carriers | ≤ 0.10 | ×40 (9e-7) | measured | — | 0 | 0 |
| 7 | **L** input-basis chaos | — | ≥ 3.5e-8 at k=128 | G-RB46 | — | 2 % | 0 |
| 8 | **N** particle (1,1,1) κ3 | 0.03–0.1 | ×100 at N=2n | noise formula | — | 0 | 0 |

Expected gain of the whole lens ≈ 2 % of adjusted score; best case (G and H both land, additive, net of head) ≈ −15 % raw → ≈ 4.5e-9. None of it changes
util. The honest statement for the orchestrator: **the leaders' 0.105 at 1.47e-8 is not reachable by any representation of OUR κ3 content; it requires a
κ3 birth with ≤ 3-source-equivalent dense content, which is not in any prose and which §1 says cannot be derived from ours by compression.** If one
experiment is run from this lens, run G's oracle: it is the only unmeasured seat, it is cheap, and a positive reading would also explain part of the
"equal weight after transport" fact (the dropped gating correction is sign-random and grows with depth, so it inflates late-layer κ3 state error exactly
where LENS_B says the error is born).
