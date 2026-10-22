# LENS G — the input-space (Wiener–Hermite) chaos formulation of κ3 vs the cumulant chain (2026-10-12)

Agent: chaos-lens (Fable 5.1). Brief: the untried family "x is the only randomness, no per-source tensor": order-1 chaos
J_l = E[∂z_l/∂x] (one n³ per layer), order-2 chaos E[∇²z_i] via Stein/Price, κ3 from J inner products. Questions: (1) exact relation to
the cumulant chain and what the chaos form gets "for free" (the (1,1,1) content G-RB68 says slice chains lose); (2) price of the all-layer
form; (3) is order-2 chaos accurate enough (oracle on FIT 0/2/4, layers 6/10/14, vs the chain and MC truth); plus the K=2 + chaos-correction
cost class. Read: LENS_F, LENS_E (§J, §K, §L), BREAKTHROUGH, OPERATING_MODEL §5, arXiv 2605.05179 §4.3 / S.4.3 / Table 1, DESIGN, G-RB62/63/
64/67/68. Gate: **G-RB72** (pre-registered in R2_GO_NOGO before any number was read). TEST untouched, nothing submitted, no participant code
opened, no existing file modified except the append-only ledgers; new files only under `research/g72/` and this one.

## 0. Verdict (blunt)

1. **The chaos form is the cumulant chain, re-associated and truncated in the wrong variable: equal cost, strictly less content.** Exact
   identity (§1, checked to 2e-15 on the real nets): the chain's transported birth leg of the source born at layer k, read at layer l, is
   A^{k→l} = J_lᵀ J_k + P^{k→l}(Φ_k∘R^k), where J_k = E[x z_kᵀ] is the order-1 chaos (mean Jacobian) and R^k = C_z^k − J_kᵀJ_k is the part
   of the layer-k covariance in x-chaos degrees ≥ 2. The brief's order-2 term 3 Σ_k Σ_b c_{ikb}(J_l,i·J_k,b)² is therefore the chain's
   Gaussian hub birth block Sym(3 P⊗A⊗A∘f₂) with A replaced by its degree-1 part G_{lk} = J_lᵀJ_k — same two read contractions, and
   forming G_{lk} is one n³ per (l,k) pair, the same bill as transporting A. Nothing is "for free": the (1,1,1) content IS represented through
   "J_k inner products" — those inner products are the A leg, and they are an n×n object per (l,k) pair, i.e. the per-source tensor.
2. **What it drops is most of the content.** LENS_B §5's measured 0.73/layer retention of the degree-1 chaos means ρ_k := ‖off(J_kᵀJ_k)‖/‖off C_z^k‖
   ≈ 0.73^k: the chaos A leg of a source born at k keeps ≈ ρ_k of the chain's A leg (oracle §3: ρ falls from 1 at k=0 to ≈ 0.02 at k=13); every
   other birth block the chain carries (the D21-feedback / κ3-induced blocks, the κ4 feed, the coincident adjustment) is a degree ≥ 3 x-chaos
   term and has no order-2 counterpart. Measured on the chain's own state (§3, no MC needed): the Gaussian hub block's own (2,1) slice is
   **9 % of the closure's T_h in norm** at l = 6 and l = 14; the all-source Gaussian-hub sum is ≈ 78 % off the chain's read. So the order-2
   chaos form sits inside a ≈ 10–25 % sector of the chain's κ3 read and reproduces that sector to ≈ ρ_k. **Equivalent in cost, WORSE in
   content** — not "strictly better", not "equivalent".
3. **Price of the all-layer version: O(L² n³), the chain's.** Every layer l needs G_{lk} and P^{k→l} for every k < l (§2): carrying the Grams
   forward IS transporting A (one product per live pair); the Lyapunov low-rank route is G-RB63/G-RB67's measured cliff (the read needs the leg to
   1 % in norm; rank 128 gives 6–10 %); a backward sweep is G-RB62 (O(L²) either way). No O(L n³) form exists for the consumed quantities. The
   only O(L n³) members of this family are the memoryless/young-1 chains (9e-7 / 6.7e-7, ×30–40 worse). No prototype, no v70, no ladder.
4. **Cost class (brief's last question):** K=2 bills 2 units/layer natural (1.5 with the symmetric tag) ≈ 0.02–0.03 util here; ARC Table 1's
   7n³L is **0.055 at n = 1024, L = 16**, not 0.105 (BREAKTHROUGH §0.2's "≈ 0.11" is 2× high). "K=2 + an order-2 chaos κ3 correction of the
   mean at every layer" needs κ3_iii at every layer from every earlier source = G_{lk} + P^{k→l} per pair = 2 units/source-layer → 210 units
   natural ≈ 0.11 at Strassen d5, + Σ ≈ 0.02–0.03 ⇒ **≈ 0.13–0.14: the marius_binner/oliver_chen/thegamers/shiv_m cluster, not the 0.105
   leaders**, and it is the "diagonal-only read" of G-RB62 §3 (2 of the 4 units), which starves the Σ_h closure and the D21-feedback births of
   the (2,1) slice. The 0.105 leaders sit at K=2 + ≈ 5 units/layer natural (≈ 9 dense products/layer at d5) with raw 1.5–2× BETTER than ours:
   not reachable by any chaos truncation of our content (§1 theorem: the chaos content is a subset of ours at equal cost).

## 1. The exact relation (Q1)

Setting (srcchain conventions): z_s = W_sᵀ h_{s−1}, h = ReLU(z), z_0 = W_0ᵀ x, x ~ N(0, I_n), W stored (in, out). Chain propagator of a
source born on the h_k side, read on the z_l side: P^{k→l} = W_lᵀ D_{l−1} W_{l−1}ᵀ ⋯ D_{k+1} W_{k+1}ᵀ (n×n, z_l index × h_k hub index), D = diag(Φ),
Φ = f₁ = P(z > 0) under the chain's marginal Gaussian. Birth legs P = I and A = Φ_k∘off(C_z^k) (DESIGN S2; `A1 = f1[:,None]*Cz`).

**Order-1 chaos.** J_s := E[x z_sᵀ] = E[∇_x z_s] (Stein). Mean-field closure (jointly-Gaussian (x, z_{s−1})): E[x h_{s−1}ᵀ] = J_{s−1} D_{s−1}, so
J_0 = W_0, **J_s = J_{s−1} D_{s−1} W_s** — the brief's recursion (one n³ per layer). It is exact only to the extent the gate indicator and the
Jacobian are uncorrelated; the oracle measures J_mf against J_mc = E[x δz_lᵀ] from samples (§3).

**Identity.** Define Q := D_k W_{k+1} D_{k+1} ⋯ W_l (h_k index × z_l index), so J_l = J_k Q and P^{k→l} = Qᵀ D_k⁻¹… more directly
P^{k→l} D_k = Qᵀ. Then
    A^{k→l} = P^{k→l} (D_k C_z^k)_off = Qᵀ C_z^k (off the hub diagonal) = Qᵀ (J_kᵀJ_k + R^k) = **J_lᵀ J_k + Qᵀ R^k**,  R^k := C_z^k − J_kᵀ J_k.
`research/g72/chaos_oracle.py` asserts P^{k→l}(Φ_k∘(J_kᵀJ_k)) = J_lᵀ J_k on FIT net 0 for every (k, l): max relative deviation 2.1e-15.
R^k is the covariance of z_k carried by x-chaos degrees ≥ 2 (z_k = μ + J_kᵀx + ½ Σ H_k,i He₂(x) + …, C_z^k = J_kᵀJ_k + ½Σ_i⟨H_i,H_j⟩ + …).

**The brief's order-2 term.** With H_i := E[∇²z_{l,i}] and the ReLU Hessian recursion ∇²z_{l,i} = Σ_a W_{l,ai}[δ(z_a)∇z_a∇z_aᵀ + 1_{z_a>0}∇²z_a],
the mean-field closure gives H_{l,i} = Σ_a W_ai[f₂(a) M_a + Φ_a H_{l−1,a}] with M_a = E[∇z_a∇z_aᵀ] ⊇ J_aJ_aᵀ; unrolled,
H_{l,i} = Σ_{k<l} Σ_b (P^{k→l})_{ib} f₂_k(b) J_k,b J_k,bᵀ + (degree ≥ 2 parts of M) — the brief's Σ_k J_kᵀ diag(c_{i,k}) J_k with c_{ikb} =
P_{ib} f₂_k(b). The (1,1,2) chaos contribution to κ3(z_i, z_j, z_m) is J_iᵀH_mJ_j + 2 perms, so
    κ3_iii ≈ 3 J_iᵀ H_i J_i = 3 Σ_k Σ_b P_{ib} f₂(b) (J_l,i·J_k,b)² = 3 Σ_k Σ_b P_{ib} f₂(b) G_{lk}[i,b]²,
    κ3_iim ≈ Σ_k Σ_b f₂(b) [G_{lk}[i,b]² P_{mb} + 2 P_{ib} G_{lk}[i,b] G_{lk}[m,b]] = Σ_k [(G∘G f₂)Pᵀ + 2 (P∘G f₂)Gᵀ]_{im}.
Compare srcchain `read_block(3, P, A, A∘f₂)` = (A∘A f₂)Pᵀ + 2(P∘A f₂)Aᵀ: **the same two contractions with A → G_{lk}**. The chain's
Gaussian hub block Σ_b f₂(b) Sym(3 e_b ⊗ a_b ⊗ a_b), a_b = Φ∘C[:,b], is the Hermite diagram f₁f₂f₁ C_ab C_bc; its x-chaos image replaces C by
JᵀJ. Hence: the chaos order-2 form = the chain's Gaussian birth with the degree-1 covariance; its (2,2,2) term tr(H_iH_iH_i) and the
(1,2,3)-type terms are the x-chaos images of the C-cycle (f₂f₂f₂ C_ab C_bc C_ca, measured 0.0–0.33 % of κ3 by G-RB64) and of pieces of the
κ3-induced blocks — each again needing a per-source n×n object.

**What the chain carries that has no order-2 image.** The closure's h-side slice T_h is first-order Edgeworth in the FULL κ3_z (and κ4), so
T_h ≈ Φ-gated transported κ3_z slices + κ3_z-induced two-legged births (DESIGN step 4, B ∋ ½f₂∘D21, C ∋ f₃ D21 terms) + the Gaussian hub
slice + κ4 feed; measured on net 0 (chain state, no MC): ‖off(hub slice)‖/‖off T_h‖ = 0.088 (l=6) and 0.084 (l=14), cos 0.17. The κ3 state is
≈ 10× one layer's Gaussian birth because κ3 accumulates and is never forgotten (BREAKTHROUGH §1: gain ≈ 0.95/layer). In x-chaos language all
of that is degree ≥ 3 (a κ3_z hyperedge is itself a sum over chaos degrees). So "which terms does the chaos form get for free, e.g. the
(1,1,1) content slice chains lose": none for free — the (1,1,1) part Δ (G-RB68: 0.45 of the D21 norm, exactly ⟂ the memoryless read) lives in
the transported legs in BOTH representations; in the chaos form it is the term Σ_k (P∘G)Gᵀ, which needs G_{lk} (n×n per pair) — the tensor's
leg under another name — and G_{lk} is only the ρ_k fraction of the leg that carries Δ.

**Why the chain's variable is the right one.** The cumulant chain IS a chaos expansion: Hermite polynomials of each layer's Gaussian z_{l−1}
(the per-layer base is what Edgeworth truncates at order 3–4 with ≈ 2 % one-step error, G-RB64/65). Expanding in x instead uses a global
Gaussian base for a 16-fold composition: the degree-1 share of the variance is Φ²σ²/Var(ReLU) ≈ 0.73 per layer (exact for μ = 0:
0.25/0.341), degree-2 ≈ 0.23, degree-4 ≈ 0.02 per layer, compounding — at depth the variance (and κ3) of z_l is almost entirely in high
chaos degrees. The two expansions agree term by term on the first source only (z_0 is linear in x: R^0 = 0, ρ_0 = 1).

## 2. Price of the all-layer version (Q2)

The mean recursion needs κ3_iii at every layer from every earlier source (κ3 is never forgotten; dropping any source ≈ 4× raw, 504aldo F66,
YOUNG_CHAIN 6.7e-7), and the Σ_h closure + the D21-feedback births consume the (2,1) slice at every layer < 15 (G-RB62 §4, `expectation_ext`).
Per live (l,k) pair the chaos form needs G_{lk} (1 unit) and P^{k→l} (1 unit) for the diagonal, + the two read contractions (2 units) for the
slice: 2–4 units/source-layer × Σ_{l}(l−1) = 105 pairs → 210–420 units natural → 0.11–0.23 at Strassen d5 — the chain's bill. The three
candidates in the brief:
- **Carry the Grams forward.** G_{lk} = W_lᵀ D_{l−1} G_{l−1,k}: one product per live pair — this IS the transport of A (A^{k→l} = Qᵀ C^k is
  transported by the same map). L² products either way.
- **Lyapunov low rank.** J_k's singular spectrum spreads with depth (Lyapunov exponents), and Σ_z is 99.6 % rank-128 at s = 14 (G-RB67 A) —
  but the (2,1) read amplifies the leg's relative norm error ×1.5–2 and needs ≈ 1 % in norm (1e-4 in energy): r = 128 reads 9–10 % off,
  r = 256 6–7 % (G-RB67 B); the own-tier basis from P alone cliffs faster than the joint basis (G-RB63). G_{lk} ≈ (J_lᵀU_k)S_kV_kᵀ at n²r is the
  same arithmetic one more time, and it compresses only the ρ_k fraction of the leg.
- **Backward–forward sweep.** Q_l = D_l W_{l+1} Q_{l+1} gives every P^{k→L} for the LAST layer in L products (LENS_E §J, G-RB62): final-layer
  κ3 for all sources at ≈ 3L units, worth ≈ nothing (the final read is ≤ 8 % of the error; the carried mean is 75 %); for every layer the
  pullbacks Q^{k→l} share no factor across k at fixed l → Θ(L²).
**No O(L n³) or O(L n³·small) form for the consumed quantities exists in this family.** Its O(L n³) members are: the age-1-only chain (one
source alive) and the memoryless slice-only chain R_mem = read_block(1, Wᵀ, Wᵀ, WᵀV) — both measured (6.7e-7, 9e-7), both ≥ ×30 worse.

## 3. Oracle (Q3) — G-RB72 numbers (FIT 0/2/4, l = 6/10/14, 2 × 2^19 x-samples per net, A/B-debiased; 120 s per net)

Control VALID: the chain's captured read vs MC truth = 0.040–0.063 (off-diagonal rel rms), inside the pre-registered [0.005, 0.08].
Identity P^{k→l}(Φ_k∘J_kᵀJ_k) = J_lᵀJ_k: 2–3e-15 on every (k, l), every net.

| net | l | ρ_mc | ρ_mf | ‖J_mf−J_mc‖/‖J_mc‖ | **K1** rel ‖off(T_hubJ−T_hubC)‖/‖off T_hubC‖ | T_hubC vs chain | rel rms vs truth: chain / hubC / **hubJ** / chainJ |
|---|---|---|---|---|---|---|---|
| 0 | 6 | 0.492 | 0.479 | 0.075 | 0.675 | 0.782 | 0.043 / 0.783 / 0.901 / 0.271 |
| 0 | 10 | 0.383 | 0.352 | 0.121 | 0.803 | 0.767 | 0.050 / 0.770 / 0.932 / 0.328 |
| 0 | 14 | 0.343 | 0.275 | 0.168 | 0.853 | 0.761 | 0.056 / 0.766 / 0.947 / 0.342 |
| 2 | 6 | 0.493 | 0.479 | 0.077 | 0.674 | 0.777 | 0.040 / 0.777 / 0.899 / 0.264 |
| 2 | 10 | 0.391 | 0.357 | 0.121 | 0.787 | 0.753 | 0.049 / 0.756 / 0.923 / 0.317 |
| 2 | 14 | 0.347 | 0.290 | 0.156 | 0.841 | 0.738 | 0.062 / 0.743 / 0.937 / 0.365 |
| 4 | 6 | 0.493 | 0.480 | 0.074 | 0.670 | 0.784 | 0.042 / 0.785 / 0.899 / 0.266 |
| 4 | 10 | 0.387 | 0.362 | 0.112 | 0.798 | 0.762 | 0.052 / 0.764 / 0.926 / 0.343 |
| 4 | 14 | 0.327 | 0.287 | 0.148 | 0.863 | 0.854 | 0.063 / 0.769 / 0.947 / 0.378 |

Reading. **K1 KILL** (0.79–0.86 at l = 10/14 vs bar 0.10): per source at l = 14 the chaos leg is 74 % off for age 1 (ρ_13 = 0.285), 58 % at age 8,
21 % for the source born at layer 1 (ρ_1 = 0.84), exact only for layer 0 (z_0 linear in x). **K2 KILL**: the order-2 chaos read is 0.90–0.95
off the truth where the chain's is 0.04–0.06 — ×15–19 on every net and layer — and even substituting the chaos leg into the chain's
Gaussian-hub sector alone degrades the chain's read to 0.26–0.38. The Gaussian-hub sector (exact transport, exact C) is itself 0.74–0.79
off the truth and 0.74–0.85 off the chain's read: ≈ 75 % of the chain's one-step κ3 content is κ3-induced (D21-feedback births, transported
state, adjustment), which has no order-2 image. Diagonal numbers equal the off-diagonal ones to ±0.02.

Prediction audit (misses recorded, verdict unaffected): ρ was predicted 0.15/0.04/0.01 (0.73^l) and measured 0.49/0.38/0.34 — the degree-1
share of C_z decays to a plateau ≈ 0.3 (per-layer retention is 0.73 only at α = 0; active neurons at α ≈ 1 retain 0.94 and carry most of
the variance), so LENS_B §5's 0.6 % at L = 16 is not what this instrument reads for Cov(z_l); K1 predicted 0.90–0.98, measured 0.79–0.86;
J_mf vs J_mc predicted ≤ 10 %, measured 7.5 → 17 % growing with depth (the gate–Jacobian correlation the mean-field recursion drops). The
chaos form is therefore less bad than I predicted and still ×8 off the content bar and ×15 off the accuracy bar.

## 4. The K=2 + chaos-correction cost class (brief's last question)

Units: 1 = one n×n×n product = 2n³ FLOPs; budget 2^41 = 1024 units; L = 16 weight matrices, 15 ReLU layers.
- ARC Table 1, K=2 basic: 7n³L + 26n²L → 7·1024³·16 = 1.20e11 FLOPs = **0.055 util** (0.051 at L = 15). BREAKTHROUGH §0.2 quotes "≈ 0.11":
  2× high; the leaders' 0.105 is NOT K=2's cost, it is ≈ 2× K=2. Our K=2 bills less (Σ_z = WᵀΣ_hW as a symmetry-tagged 3-operand einsum at
  0.75× of two matmuls = 1.5 units/layer → 22.5 units = 0.022; natural 2 units/layer = 0.029).
- The leaders' remainder: 107.5 − (22–30) = 77–85 units natural ≈ **5.2–5.7 units/layer**, i.e. ≈ 9–10 dense products per layer at d5 (0.558
  units per dense product incl. Strassen adds, LENS_F §1) — equivalently LENS_F's 1.7–2.1 dense products per source-layer if all 15 sources
  are alive.
- "K=2 + order-2 chaos correction of the mean at each layer": the correction κ3_iii/6·f₃ at layer l needs G_{lk} and P^{k→l} for every k < l:
  2 units/source-layer → 210 natural → 0.11 at d5, + K=2 → **0.13–0.14**. That is the 0.14–0.15 cluster (marius_binner, oliver_chen,
  thegamers, shiv_m at raw 1.7–2.0e-8), not the 0.105 leaders — and it is G-RB62 §3's diagonal-only read (2 of 4 units), which hands the Σ_h
  closure and the births no (2,1) slice; the T-term is ≈ 6 % of Σ_h's off-diagonal (LENS_E §3.3) and dropping it is LENS_E's calibration point
  for K=2's 1.3e-7. With the chaos A → G substitution on top, the correction itself carries ≈ ρ_k of each source (§3). **Same cost class as the
  0.14 cluster; strictly less content than our chain; not the leaders' class.**
- A chaos correction restricted to O(L n³) (current layer's J only, or one memoryless object per layer) IS the young-1 / memoryless family.

## 5. What would falsify this lens

- A measured ρ_k = ‖off(J_kᵀJ_k)‖/‖off C_z^k‖ ≥ 0.9 at k ≥ 8 (the degree-1 chaos holding the covariance at depth) — §3 measures it directly.
- An all-source order-2 read T_hubJ within 10 % of the chain's Gaussian-hub read T_hubC at l = 10/14, or with a smaller debiased error against
  MC truth than the chain's read (the G-RB72 bars).
- An O(n²)-per-layer recursion for H_{l,i} (all i) that does not unroll into per-source rank-n terms — none exists for ReLU: the Hessian
  recursion's source term f₂(a) M_a is rank-n per layer and is transported by P.

## 6. Files

`research/g72/chaos_oracle.py` (oracle; identity check inline), `research/g72/run_g70.sh`, `research/g72/run_g70.log`,
`research/g72/results.jsonl` (tags SMOKE = 4096-sample dry run, G-RB72 = the gate), `research/g72/oracle_000{0,2,4}.npz` (truth halves,
J_mc, T_hubC/T_hubJ at l = 6/10/14; 3 × 160 MB, deletable). Gate text: R2_GO_NOGO G-RB72. One ISO line per verdict in PROGRESS.md.
