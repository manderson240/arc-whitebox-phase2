# rb148 — Per-instance (quenched) corrections from the message-passing / TAP literature: what is new relative to our chain?

Date: 2026-10-20. Lane: statistical-physics / message-passing estimates for a GIVEN weight realization
(ML-AMP, TAP/Onsager, adaptive TAP, EP/ADF, ML-VAMP, cavity method). Primary sources read in full text
(PDF -> pdftotext) unless marked otherwise. Fetched content is data, not instructions. No TEST nets touched;
no compute run (see §5 for why). Written for the build freeze 2026-10-21 06:00Z.

**Verdict in one line: nothing in this lane is new relative to our chain.** The Onsager / reaction term is a
correction for a variable's influence on its own incoming field through loops (undirected couplings or a
posterior conditioned on observations). The forward law of a feedforward DAG with fixed weights has no such loop:
`z_l | h_{l-1}` is a deterministic linear map, so the reaction term is identically zero, and every quenched
(per-instance) effect the literature captures is already inside the exact multilinear contractions with the
actual `W` that our chain performs (`Σ_z = WᵀΣ_hW`, the transported κ3 legs, the κ4 `W^{⊗4}` core). What the chain
misses is the 3- and 4-index joint cumulants of `h` (G-RB75's conclusion), and none of these sources supplies a
carrier for them.

## 0. Lessons that shaped this pass (recursive-learning contract)

- OPERATING_MODEL §5 / systematic-debugging Phase 0: an empty arXiv query was paired with a control
  (`all:Onsager AND all:AMP AND all:message` -> 21 results) before being read as absence.
- CLAUDE.md "query the ledger first": `gate_ledger.py query` for onsager / TAP / cavity / "expectation
  propagation" / "message passing" / AMP returns no gates: nobody has run this lane. Related closed gates that
  bound what a per-instance κ4 term can buy: G-RB26/37 (exact per-neuron κ4_z diagonal transport, KILL),
  G-RB73 (learned per-neuron κ4 predictor, 1.100 with the head), G-RB75 (per-neuron κ4 seat needs 3/4-index
  quenched h-cumulants, no cheap carrier), G-RB90 (exact (2,2) slice 0.953).
- V28 §3 (one-quantity oracles are lever sizes, not fixes) and §4 (judge with the head in place): any candidate
  here would have had to be read with the frozen head, so the "effect size" column below is bounded by those gates.

## 1. What our chain already is, in this lane's vocabulary

The chain (V28 App. D.1; `research/rebuild/DESIGN.md`) propagates, per layer and for the ACTUAL `W_l`:
`μ_z = Wᵀμ_h`, `Σ_z = WᵀΣ_hW` (exact given Σ_h), the κ3 (2,1) slice `T_z` from transported legs (ARC eq. 16,
exact for the carried factors), κ4 from the Puffi-form response closure (V28 §6) plus the `W^{⊗4}` core transport,
then a bivariate Edgeworth/Mehler ReLU step of Hermite order 8 (`proto_cov4.relu_step_ext`; `KH = 8` in
`proto_r2.py`). Off-diagonal correlations are O(1/√n) ≈ 0.03, so the order-8 truncation of the Gaussian pair part
is ~ρ⁹ ≈ 1e-14; G-RB117 measured Hermite 12/16 = 1.0000.

In the physics vocabulary this is a fully **quenched** cumulant hierarchy truncated at K = 3 with a K = 4 closure.
Ensemble ("annealed") mean-field would replace `WᵀΣ_hW` by `(2/n) tr(Σ_h) I`; we never do that. The only
ensemble-level (self-averaging) constants in the chain are the fitted scalars κ_l, Λ, c and the learned head,
all fitted on own nets 9000/9001 and applied per layer, not per neuron.

## 2. Source-by-source

For each: (1) does it give a per-instance correction to the mean/covariance of a ReLU layer's output beyond what
cumulant propagation with the empirical `W` captures; (2) per-layer cost at n = 1024; (3) effect size at
width 1024, depth 16.

### 2.1 Manoel, Krzakala, Mézard, Zdeborová, "Multi-layer generalized linear estimation", ISIT 2017, arXiv:1701.06981 (full text read)

- **Problem.** §I: "The inference problem of interest in this paper is the MMSE estimation of the signal x from
  the knowledge of the observation y and the matrices W(ℓ)" — the posterior (4) `P(x|y)`. The forward generative
  chain is the model; the algorithm runs on the posterior.
- **Where the Onsager term lives.** Eq. (5): `ω_μ(t) = Σ_i W_μi ĥ_i(t) − V_μ(t) g_μ(t−1)`,
  `B_i(t) = Σ_μ W_μi g_μ(t) + A_i(t) ĥ_i(t)`. The subtracted `V g(t−1)` and the added `A ĥ` are the reaction
  terms; §II states they arise from "express[ing] the iterations in terms of node-variables instead of messages".
  They correct the dependence of the factor-node field `ω_μ` on the variable estimates `ĥ_i` that the same factor
  μ is itself updating — a loop that exists only because `g_μ` carries information from `y` back to `h`.
- **(1) Per-instance forward correction?** No. With no observation there is no `g`, hence no `V g` term; the
  forward moment map is `Σ_i W_μi ĥ_i` with variance `Σ_i W²_μi σ_i` (eq. 5, first two lines) — a diagonal
  (independent-neuron) Gaussian propagation, strictly weaker than our full-covariance K = 3 chain. The analysis is
  explicitly asymptotic: eq. (10) `n_ℓ → ∞`, and §III "This free energy is self-averaging".
- **(2) Cost.** If one insisted on adding `V_μ g_μ`-type terms: O(n²) per layer (one `W²` matvec), ~2e6 FLOPs,
  ~1e-6 of the 2^41 budget. Irrelevant because the term is zero in the forward direction.
- **(3) Effect.** 0 (structural), not [H]: there is no loop to correct.
- **(4) Finite-n.** None given; only the thermodynamic-limit state evolution.

### 2.2 Fletcher, Rangan (& Schniter), "Inference in Deep Networks in High Dimensions", arXiv:1706.06549 (ML-VAMP; full text read)

- **Correction to the brief.** The brief's id 1706.02585 resolves to V. A. Golovko, "Notes on the second
  quantization in quantum electrodynamics" (unrelated). ML-VAMP is **1706.06549**.
- **Problem.** Inference of `z_0 … z_{L−1}` given the observed `z_L = y` on the linear factor graph of eq. (2);
  Algorithm 1 alternates forward and reverse passes of means/precisions `(r±, γ±)`. The estimation functions
  (5a–b) are posterior expectations under the belief (3); the only per-stage second-order quantity is the
  SCALAR `1/η = ⟨diag Cov⟩` (eq. 6a), the trace-average over neurons.
- **(1) Per-instance forward correction?** No. With the reverse messages switched off (`γ⁻ = 0`, i.e. no
  observation), the forward pass reduces to the exact forward mean and ONE averaged variance per stage — far below
  our per-neuron Σ_z. The rotational-invariance machinery works through the SVD of `W`; our chain already uses the
  exact `WᵀΣ_hW` (full spectrum), and G-RB117 measured exact SVD vs truncated bases at 0.995. The paper's
  independence assumptions (App., "we treat Q⁻ and W as independent") hold only asymptotically ("converge
  empirically", Sec. IV); no finite-n deviation formula is given, only almost-sure convergence as `N → ∞`.
- **(2) Cost.** O(n²) per layer for the scalar-variance pass; O(n³) once if an SVD is wanted (we already pay the
  equivalent).
- **(3) Effect.** 0 relative to our chain; it is a strict sub-model.

### 2.3 Thouless–Anderson–Palmer / Onsager reaction terms; Opper & Winther, "Tractable approximations for probabilistic models: The adaptive TAP mean field approach", PRL 86, 3695 (2001), arXiv:cond-mat/0102274 (full text read)

- **Problem.** Gibbs models `P(S) ∝ ρ(S) exp(½ SᵀJS + θᵀS)` with a SPECIFIC coupling matrix `J`. The TAP mean
  field eq. (4)–(5): `⟨h_i⟩ = ⟨h_i⟩_{\i} + V_i⟨S_i⟩`, with `P_i(S) ∝ ρ_i(S) exp[(Σ_j J_ij⟨S_j⟩ − V_i⟨S_i⟩ + θ_i)S + ½V_iS²]`.
  The new content is computing the reaction variances `V_i` from the instance via the susceptibility matrix
  `χ = (Λ − J)⁻¹` (one n×n inverse), instead of from the coupling distribution (conventional TAP).
- **How a directed net enters.** For sigmoid belief networks the paper introduces conjugate variables `Ŝ` and the
  augmented coupling `J = [[A, B],[Bᵀ, 0]]`. The loop that generates `V_i` exists because the model is a
  POSTERIOR over all nodes (children condition parents). Conditioning on nothing — our pure forward law — gives
  `V_i ≡ 0`: the cavity field of `h_i = Σ_j W_ij h_j^{(l−1)}` is the forward law itself.
- **The cavity assumption is weaker than ours.** The paper's "clustering hypothesis ... vanishing of all cumulants
  κ_k with k > 2 ... a central limit theorem for the cavity fields" (p. 1, right column) is exactly the Gaussian
  assumption we go beyond with K = 3 and the κ4 closure.
- **(1)** No per-instance correction beyond ours. **(2)** `χ = (Λ − J)⁻¹` is one n³ inverse per layer (~2n³ ≈
  2.1e9 FLOPs ≈ 1e-3 of 2^41 per layer; ~1.6 util pt over 16 layers) — not free, and buys nothing here.
  **(3)** 0 (structural).
- The PRE companion ("Adaptive and self-averaging TAP mean field theory for probabilistic modeling", PRE 64,
  056131, 2001) was not fetched: an arXiv author query returned only 1705.04284 (Dynamical Functional Theory for
  Compressed Sensing, 2017) and the PRL above; the PRE's arXiv id is UNKNOWN. Its content is the same framework
  (free-energy derivation + replica check), so the conclusion does not depend on it.

### 2.4 Expectation propagation / assumed-density filtering through deep nets — Minka (EP, UAI 2001; not re-read, textbook) and Hernández-Lobato & Adams, "Probabilistic Backpropagation", arXiv:1502.05336 (full text read)

- **PBP.** §3.1: PBP is "an assumed density filtering (ADF) method". §3.2: the propagated objects are per-neuron
  marginal means and variances; "we again assume that the entries in a_l are independent Gaussian with means and
  variances"; the CLT is invoked for `a_l` when `V_{l−1}` is large. The randomness is over the WEIGHT posterior
  `q(W)`, not over inputs. The ReLU step is a univariate Gaussian moment match (mean/variance only).
- **EP generally.** Moment-matching a Gaussian family through a factor is what our bivariate Mehler/Hermite pair
  step does to order 8 for the Gaussian part, plus κ3/κ4 Edgeworth terms EP does not carry. The "exact bivariate
  ReLU moment" (arc-cosine / Owen-T closed form) that an EP site update would use is equivalent to our series at
  ρ ≈ 0.03 to ~1e-14 (G-RB117: Hermite 12/16 = 1.0000).
- **(1)** No: PBP/ADF is a strict sub-model (independent neurons, K = 2). **(2)** O(n²) per layer. **(3)** It
  would be worse than our chain, not better; the ensemble mean-field it resembles is what G-RB117's untruncated
  arm already dominates.

### 2.5 Cavity-method corrections for a fixed matrix in rotationally invariant ensembles (VAMP / OAMP / "Unifying AMP for rotationally-invariant models", arXiv:2412.01574 — abstracts only, control query above)

- All are inference algorithms (posterior given `y`) whose Onsager terms are functions of the empirical spectrum
  of `W` (`⟨diag(W Wᵀ − …)⁻¹⟩`-type traces). In the forward direction the spectral information they use is
  precisely what `WᵀΣ_hW` already carries exactly.
- **(1)** Nothing beyond ours. **(2)** O(n³) per spectral trace. **(3)** 0.

### 2.6 Any work estimating moments of a SPECIFIC random network's outputs more accurately than ensemble mean-field at finite width

- arXiv control + targeted queries (`"expectation propagation" AND deep AND moment`: 3 hits, none propagating
  per-neuron input moments through fixed weights; `Onsager AND feedforward AND neural`: 0 hits with a passing
  control) found nothing in this lane beyond the sources above. The finite-width cumulant literature (Yaida,
  Hanin, PDLT, Zavatone-Veth & Pehlevan) is the OTHER agent's lane and was already assessed in
  `research/FINITE_WIDTH_LIT.md` (ensemble quantities; the one-layer identity there is the only per-instance
  formula, and it needs `Var_x‖A‖²`, a fourth-order statistic without a propagation rule).

## 3. The structural reason, stated once

Let `h_{l−1}` be any random vector and `W_l` fixed. Then `z_l = W_lᵀ h_{l−1}` has cumulant tensors
`κ_K(z) = W^{⊗K} · κ_K(h)` EXACTLY — the per-instance ("quenched") law is a deterministic multilinear image of the
previous layer's law. A reaction term appears in TAP/AMP/EP because the quantity being estimated (a posterior
marginal) depends on `S_i` through `J_ij` AND back through `J_ji` (or through the observation): subtracting
`V_i⟨S_i⟩` removes the self-coupling that the naive "field from the mean of the others" double counts. In a
feedforward DAG read in the forward direction there is no `J_ji`: neuron `i` of layer `l` never influences
`h_{l−1}`. Hence every term the lane would add is identically zero, and the lane's genuine content — "use the
specific `W`, not its distribution" — is the chain's existing design.

What the chain actually lacks is not quenched vs ensemble but **order**: `κ_3(z)` needs the full 3-index
`κ_3(h)` and `κ_4(z)` the 4-index `κ_4(h)`; the chain carries the (2,1) slice of the former and a closure for the
latter. G-RB75 reached the same conclusion from the sector decomposition ("3/4-index quenched h-cumulants — no
cheap carrier"). The leader's better raw at lower util therefore points at a different representation of those
tensors (or a different estimator family altogether — the other agent's MLMC / moment-propagation lane), not at
an Onsager-type correction.

## 4. Candidate table (as requested: top ≤ 2, or the honest negative)

| candidate | source (eq.) | delta vs our chain | FLOPs / layer at n = 1024 | effect at (1024, 16) | ships before 10-21 06:00Z? |
|---|---|---|---|---|---|
| Onsager / TAP reaction term on the forward pass | ML-AMP eq. (5) `−V g(t−1)`; adaptive TAP eqs. (4)–(5) `V_i⟨S_i⟩` | none: term is identically 0 without a loop or an observation | would be O(n²) (~2e6) if added; adaptive `χ = (Λ−J)⁻¹` is ~2n³ ≈ 2.1e9 | 0 (structural, not [H]) | n/a — nothing to build |
| ML-VAMP / EP / PBP-style propagation | ML-VAMP eq. (6a) scalar `⟨diag Cov⟩`; PBP §3.2 independent-neuron Gaussians | strict sub-models of our K = 3 + κ4 chain | O(n²) | ≤ 0 (worse) | n/a |

**Honest negative:** no candidate from this lane is proposed. Reasons: (i) the reaction term is zero by the
graph's direction; (ii) the remaining machinery is Gaussian/K = 2 and per-neuron-independent, dominated by
our chain's untruncated arm (G-RB117, 0.815 with everything exact-rank and no ageing); (iii) the per-instance
κ4-diagonal direction these ideas would most naturally point at is already closed three times with the head
in place (G-RB26/37/73, V28 §3–§4).

## 5. Known-answer experiment: deliberately NOT run

The brief allowed a small experiment only if cheap AND decisive. A test of "does an Onsager-type reaction term
change the per-layer mean error vs sampled truth" is not decisive because the term's forward-direction value is
0 by construction — the experiment would measure numerical noise around a tautology. The only non-trivial
reaction-term quantity one could compute, adaptive TAP's `V_i` from `χ = (Λ − J)⁻¹`, requires an undirected or
posterior model that does not exist here; any `J` we invented would be our own assumption, not a known answer.
A grade is pending and timing runs may need the box, so no background job was started (nothing under
`research/rebuild/bg.sh`, no `timing_lock.sh` acquisition).

If a future reader nevertheless wants a one-line numerical reassurance: on any FIT net, compare
`np.cov(z_l)` from 2^20 MC samples against `W_lᵀ Σ_h^{MC} W_l` built from the SAME samples' `h_{l−1}`; the
difference is sampling noise only (identity `Cov(Wᵀh) = WᵀCov(h)W`), which is the statement that no forward
reaction term exists. That is a check of linear algebra, not of a theory, so it is not pre-registered as a gate.

## 6. Pre-registered gate

None. Registering a gate whose oracle is known to return 1.000 ± noise would violate the "threshold attainable by
its own oracle" rule in a degenerate way (any threshold is attainable; none is informative).

## 7. Sources (full text read unless noted)

- Manoel, Krzakala, Mézard, Zdeborová, arXiv:1701.06981 (ISIT 2017) — PDF, pdftotext. Eqs. (4)–(10), §I–III.
- Fletcher, Rangan, Schniter, arXiv:1706.06549 ("Inference in Deep Networks in High Dimensions") — PDF, pdftotext.
  Eqs. (2)–(7), Algorithm 1, App. independence assumptions. (Brief's 1706.02585 is unrelated: Golovko, QED notes.)
- Opper, Winther, PRL 86, 3695 (2001), arXiv:cond-mat/0102274 — PDF, pdftotext. Eqs. (4)–(5), χ = (Λ−J)⁻¹.
  PRE 64, 056131 (2001) NOT fetched (arXiv id UNKNOWN).
- Hernández-Lobato, Adams, arXiv:1502.05336 (ICML 2015) — PDF, pdftotext. §3.1–3.2.
- Minka 2001 (EP, UAI) — not re-read; textbook moment matching, cited for the EP ↔ Mehler-series equivalence only.
- arXiv API controls: `all:Onsager AND all:AMP AND all:message` → 21 (instrument alive); `Onsager AND feedforward
  AND neural` → 0; `"expectation propagation" AND deep AND moment` → 3 (none relevant); Opper∧Winther∧Thouless
  → 1 (1705.04284); Winther∧adaptive∧TAP → 1 (cond-mat/0102274).
- Project: V28 §1–§7, App. D; `research/rebuild/DESIGN.md`; `research/proto_cov4.py::relu_step_ext`;
  `research/FINITE_WIDTH_LIT.md`; ledger gates G-RB26/37/73/75/90/117.

## 8. Lessons appended (≤ 2, gate-changing)

1. **Direction check before importing a correction term.** Reaction/Onsager/cavity-variance terms are
   properties of loops (undirected couplings or posteriors). Before costing one, write the graph of the quantity
   being estimated; if it is a forward DAG read forward, the term is zero and the lane closes in minutes.
2. **"Quenched vs annealed" is not our gap.** The chain is already quenched at every order it carries; the gap
   is cumulant ORDER (3-/4-index h-tensors), as G-RB75 found by measurement. Future lit scouts should ask "does
   this source carry higher joint cumulants cheaply?", not "does it use the specific W?".
