# ARC White-Box Estimation 2026, Phase 2 — algorithm spec (research lead, 2026-09-26)

Shape: width n=1024, depth D=16 ReLU layers, W_l ~ N(0, 2/n) stored (in,out), x ~ N(0,I).
Budget B = 2^41 = 2.2e12 FLOPs/MLP; score = mean_m[ final_MSE_m × max(0.1, F_m/B) ]. 10 % floor = 2.2e11.
Ground truth: 1e9-sample MC (floor 7.5e-11). Leader ≈ 1.66e-8 final MSE (adjusted ≈ 1.7e-9);
our v0 (kit covariance propagation, 51.7 GFLOP = 2.35 %) = 3.9e-6 final MSE (adjusted 3.93e-7).

Companion prototype: `proto_k2plus.py` (numpy, offline only). Raw output: `proto_k2plus_results.txt`.
Local MC reference noise: σ²_final/N with σ²_final = 0.0717 (matches the kit's official 0.0748), i.e.
7.2e-8 at N=1e6 — **anything below ~2e-7 is not resolvable locally at 1e6; 1e7–1e8 samples are needed to
adjudicate at the leader's level.** All numbers below say which N they came from.

---

## 0. Three measured facts that reorder every candidate (2026-09-26, `vr_bench.py` + prototype)

| Fact | Measurement | Consequence |
|---|---|---|
| **F1. σ² per final neuron is 7.2e-2, not the 3.5e-4 assumed in PROGRESS.md.** | `vr_bench.py 1 4`, N_ref=1e6 | Plain MC at 10 % budget (6,553 samples) = **1.09e-5 theory / 1.22e-5 measured** — 3× *worse* than covariance propagation. At 100 % budget MC = 1.1e-6 with multiplier 1.0. **The "leaderboard is variance-reduced MC" thesis in PROGRESS.md is refuted**; the leaders are analytic. Best local VR (orthogonal+antithetic) = 6.9e-6, adjusted 6.9e-7 — still 1.8× worse than v0. |
| **F2. The closure error is ~16 accumulated one-step readout errors.** | Oracle (N=1e6, 2 MLPs): 1 closure step from the MC-exact (μ, Σ) of post-ReLU layer 15 → final MSE **1.64e-7 / 1.77e-7**; 2 steps from layer 14 → **3.5e-7 / 3.7e-7**; 16 steps (the estimator) → 3.6e-6 / 4.9e-6 ≈ 16 × 2.5e-7. Gaussian readout fed the MC-exact (μ,σ) of z₁₆ = 1.64e-7 / 1.77e-7; adding the MC-exact κ₃ term → **2.1e-8 / 2.1e-8**. | The per-step Gaussian closure of E[ReLU(z)] is wrong by ~2e-7 MSE-equivalent, and **~85 % of that is the third cumulant of the pre-activation** (mean \|skew\| = 0.093 at layer 16). Errors then add roughly linearly with depth. Getting κ₃(z_i) (and κ₄) right per neuron per layer is *the* mechanism; the exact-bivariate-covariance fix (write-up 18214) attacks a different, smaller term (7.4 %, reproduced here: 4 %). |
| **F3. κ₃(z) is not cheaply computable at this shape.** | (N=1e6, 2 MLPs) Leading-diagram estimate (diag + two-equal-index + path, 3 matmuls/layer) recovers only **1/3.8 of the κ₃ amplitude** (regression slope MC/est = 3.76 / 3.85; diag alone 1/10–1/15). A rank-8 common-mode model (top PCs of Cov(z₁₆); top PC 9–10 % variance share, skew +0.22, excess kurtosis +0.06–0.08) explains **27–28 %** of κ₃ mean-square (slope 4.2–4.5); participation ratio of Cov(z₁₆) = 47–52; top-32 PCs carry 60 % of variance. | The missing skewness is high-dimensional and needs higher Hermite orders in the 3-point cumulants (pre-activation correlations reach 0.4, so the O(C) truncation is invalid). This is exactly what the paper's full K=3 does — and its cost is prohibitive here (§2). |

---

## 1. Ranked candidates

### R1 (ship first, low risk): exact-K2 closure + K3-lite + shipped per-layer calibration — "closure-plus"
*(i) Math.* Paper Algorithm 2 (K=2) is **identical** to the kit's gain method (c_i = E[φ'(Y)] = Φ(α_i)).
Replace the off-diagonal update by the exact bivariate ReLU covariance series
`Cov(φ_i,φ_j) = Σ_{k=1..K_H} φ̂_k(i) φ̂_k(j) C_ij^k / k!`, with ReLU Hermite coefficients
`φ̂_1 = Φ(α)`, `φ̂_k = He_{k−2}(−α) φ(α) / σ^{k−1}` (k ≥ 2; derived by k-fold integration by parts,
ReLU'' = δ; unit-tested against MC in the prototype). K_H = 6 suffices (|C_ij| ≤ 0.4·σ²).
Add the cheap κ₃ channel (K3-lite): κ₃(z_i) ≈ Σ_a W_ai³ κ₃(h_a) + 6 Σ_c W_ci Φ_c Σ_{a≠c} W_ai² g_a C_ac
+ 3 Σ_b W_bi φ̂₂(b) [ (Σ_{a≠b} W_ai Φ_a C_ab)² − Σ_{a≠b} W_ai² Φ_a² C_ab² ], g_a = m1_a(1−Φ_a);
then Gram–Charlier one-step corrections `E[f(Z)] += κ₃/6 · E_G[f‴]`:
ReLU → −κ₃ μ φ(α)/(6σ³); ReLU² → κ₃ φ(α)/(3σ); ReLU³ → κ₃ Φ(α). Finally multiply each recorded
layer row by a shipped per-layer constant c_l fitted offline (`c_l = <est,ref>/<est,est>` over
training MLPs; ridge/4-basis variants in 18214/18216).
*(ii) Measured final MSE (N=1e6 refs, 2 held-out MLPs; every figure includes the 7e-8 reference noise;
calibration fitted on 6 other MLPs at 3e5 samples).*

| estimator | MLP 0 | MLP 1 | vs kit |
|---|---|---|---|
| kit (v0) | 3.61e-6 | 4.92e-6 | 1.0× |
| k2exact (exact bivariate cov) | 3.48e-6 | 4.73e-6 | −4 % (18214 saw −7.4 %) |
| k3diag | 3.50e-6 | 4.43e-6 | −3…−10 % |
| **k3lite** | **3.10e-6** | **3.98e-6** | **−14…−19 %** |
| kit + per-layer scale | 1.17e-6 | 1.35e-6 | 3.1–3.6× |
| **k3lite + per-layer scale** | **1.07e-6** | **1.12e-6** | **3.4–4.4×** |

Per-layer scale constants: monotone drift 1.000 → 0.9983 over 16 layers (≈ −1.1e-4/layer), i.e. the
closure over-predicts by 0.17 % at layer 16. Two independent Phase-2 write-ups report the same 3.4–3.65×
from calibration (1.23e-6 / 1.13e-6; public adjusted 1.07e-7 for #330001, 1.32e-7 for #329951).
Honest expectation for R1 on the grader: **~1.0–1.1e-6 → adjusted ~1.05e-7** (3.7× better than v0's
3.93e-7). Not near the leader (1.7e-9).
*(iii) Cost.* κ₂: 16 × 3.22e9 (symmetric einsum) + κ₃-lite 3 matmuls × 2.1e9 × 15 = 9.7e10 + Hermite
series 6 × n² × 3 × 16 ≈ 3e8 → total ≈ **1.5e11 = 6.8 %** of budget (< 10 % floor; multiplier stays 0.1).
Drop K3-lite → 2.4 %.
*(iv) flopscope feasibility.* All ops exist: `fnp.einsum("ij,ia,jb->ab")` on `flops.as_symmetric` cov,
`fnp.matmul`, `fnp.multiply/outer/power(int)`, `fnp.fill_diagonal`, `flops.stats.norm.cdf/pdf` (20n/10n,
cast back to float32), `fnp.diag` (free), `fnp.sqrt/maximum`. Hermite recurrence = n-vector ops.
Calibration constants shipped as `.npz` (pickle-free), loaded in `setup()` (allowed: "data files").
**Residual-cap hazards (forum 18202):** zero `float()/bool()` syncs inside the layer loop (the kit's
`_COV_RESCALE_THRESHOLD` check is the known tripwire — delete it; the guard never fires at this shape);
keep ≤ ~200 fnp calls/layer; test with `whest run --profile`, target residual < 0.2 s.
*(v) Cheap wins.* The 0.992 scalar (Phase 1) does **not** transfer as-is: the measured final-layer
scale bias here is **0.9983** (fitted on 6 MLPs; 0.9980–0.9985 per MLP), i.e. 0.17 % vs 0.8 % — consistent with the paper's
c_K (L/n)^K scaling ((32/256)/(16/1024) = 8×). A single scalar removes only ~10 % of MSE at this shape;
the 3× reported in Phase 2 needs per-layer (or 4-basis) constants. Fit them on ≥ 20 local MLPs with
≥ 3e5-sample refs (noise 2.4e-7 ≪ 4e-6 signal).

### R2 (the research bet that can reach the leader tier): two-index K=3 cumulant propagation — "power-cumulant K3"
*(i) Math.* F2/F3 say the missing quantity is the per-neuron κ₃(z_i) (then κ₄), and it is carried by
distributed 3-point structure, not by a few common modes. The paper's K=3 needs the full n³ tensor.
Proposed truncation: track the **two-index sector** T_ij = κ[h_i, h_i, h_j] (n² storage, contains the
diagonal κ₃(h_i) = T_ii) exactly through the linear layer,
`κ[z_i,z_i,z_j] = Σ_ab W_ai² W_bj T_ab + 2 Σ_{a≠a'} W_ai W_a'i W_bj κ[h_a,h_a',h_b]` where the first
term is two matmuls (`(W∘W)ᵀ T W`, 4n³) and the second (distinct-index) term is approximated by its
leading Hermite order (the path diagram, already in K3-lite). At the ReLU, compute T for the outputs
from the trivariate Hermite/diagram formula **to all Hermite orders in the strong-correlation entries**
(the [≤2]-mixed diagrams of the paper's Theorem A.2 restricted to indices {i,i,j}), and close the loop
by feeding κ[z_i,z_i,z_j] into the covariance update: `Cov(φ_i,φ_j) += ½ φ̂₂(i) φ̂₁(j) κ[z_i,z_i,z_j] + sym`
(this is what K3-lite omits — it never corrects Σ, only the readout). Add the paper's "full trace of the
4th-order tensor" scalar (n² cost) which the paper shows is required for the odd-K error order.
*(ii) Expected MSE.* Paper conjecture MSE ≤ c_K (L/n)^K: K=2→3 gains a factor between L/n=1/64 and
1/n (measured K=2 constant c₂≈0.2 here). If the two-index sector carries most of κ₃(z) the gain is
**10–60×** → 6e-8 … 4e-7 (uncalibrated; calibration on top). Leader-tier only if κ₄ follows. **Evidence is
thin**: #330001's "rank-4608 inherited third cumulant channel" gained only 8 %, and F3 shows leading-order
diagrams recover 27 % of κ₃ — the whole bet is that the *all-orders* two-index ReLU closure recovers the
rest. Decisive local test (1 day): compute κ[z_i,z_i,z_j] two ways at layer 16 from MC-exact layer-15
statistics and check the slope against MC κ₃(z₁₆) (harness already prints this for K3-lite).
*(iii) Cost.* κ₂ 5.2e10 + two-index sector 2 matmuls (4.2e9) + κ₃-lite path term 3 matmuls (6.3e9)
+ O(n²) Hermite sums (~10 × 1e6 × 16) → **≈ 2.2e11 ≈ 10.0 %** — right at the floor; drop the T′ overlap
matmul or share `(W∘W)` products to land at ~8 %. Must be metered exactly with `budget_summary()`.
*(iv) flopscope.* Same op set as R1; n² elementwise powers of C are `fnp.multiply` chains (weight 1),
avoid `fnp.power` (weight 16). No unavailable op.
*(v)* Ship R1 while this is built; R2 replaces R1's K3-lite block.

### R3 (reference only — infeasible at 10 %): the paper's cumulant propagation as published
Wu, Lecomte, Winer, Robinson, Hilton, Christiano (arXiv:2605.05179), Appendix J FLOP polynomials:
basic K=3 = 7/3 n⁴L = **4.1e13 (19× budget)**; factorized K=3 = 30 n³L² + 39 n³L = **8.2e12 (3.7×
budget)**; K=4 factorized 24 n⁴L² ≈ 6.8e15. MSE conjecture c_K(L/n)^K, empirically ∝ 1/n^K and ∝ L^K
(their Fig. 3/8, width ≤ 256, L ≤ 12); at width 256 with 8 hidden layers K=4 already **underperforms
sampling**. Code: github.com/alignment-research-center/mlp_kprop (404 for me on 2026-09-26 — verify
manually before relying on it). Conclusion: the leaders' 1.66e-8 at ~10 % cannot be the published
algorithm; it is an unpublished truncation (thylinao1: "Mechanism remains unpublished").

### R4 (refuted here): MC and variance reduction, blends
Plain 1.22e-5 / antithetic 1.08e-5 / orthogonal 1.00e-5 / radial 1.20e-5 / ortho+antithetic 6.9e-6 at
10 % budget (N_ref 1e6). Batch whitening (2.0–2.3× in Phase 1) would give ~5e-6; the 0.75/0.25 blend
(#328274) gave −25 % on a 4e-7 baseline. All ≥ v0. **Do not spend more time here at this shape.**
(Phase 1 was 256×32 where σ² and the closure bias differed by 8×; that is why MC looked competitive.)

---

## 2. Decision

**Ship R1 now** (expected adjusted ~1.1e-7, from 3.93e-7; cost 6.8 %). Start R2 immediately; its
go/no-go is the κ[z_i,z_i,z_j] slope test, not a leaderboard submission. If R2's slope is < 0.5
after the all-orders two-index closure, the remaining lever is κ₄ / the paper's factorized machinery
in a rank-compressed form — and at that point the honest statement is that the leader tier is not
reachable by 2026-10-17 with this team's evidence.

## 3. Implementation risks (Phase 2 rules)
1. **Residual 400 ms cap**: every Python-side `float()` is a sync (18202). R1 has none in the loop.
2. **Smoke test at a non-16×1024 shape** (18214): layer-indexed calibration must guard `l < len(cal)`
   and fall back to 1.0.
3. **Float64 leakage**: `flops.stats.norm.*` promote; cast back or the 2× rate applies to the einsum.
4. **Calibration transfer**: constants fitted on our generator must be validated on the public
   `arc-whestbench-public-2026@v2-phase2` shard before trusting (18216 §8.2 saw width-transfer noise).
5. **Symmetry tag**: `fill_diagonal` voids it; re-`as_symmetric` (7.3 MFLOP) or the einsum bills +25 %.
6. **Local resolution**: differences < 2e-7 need N ≥ 1e7 (7 min/MLP here). Do not claim sub-1e-7 gains
   from 1e6 references.

## 4. Sources
Paper arXiv:2605.05179 (§4.1–4.3, §5, §6.2–6.3, App. B/D/J). Forum: 18063 (0.992 scalar, 3× at 256×32),
18173/18174 (BCH/Walsh–Hadamard MC, 1.55e-7 Phase 1), 18188 (spherical quadrature ceiling = MC),
18193 (oracle decomposition: dependence structure dominates; Edgeworth readout 1.5e-8 with exact inputs),
18200 (0.75/0.25 blend, −25 %), 18202 (residual cap = sync points), 18214 (exact bivariate cov +
per-layer ridge, 1.32e-7 adjusted), 18216 (64 constants ↔ zero-constant κ₃ channel, 1.07e-7 adjusted;
"closure family sits an order of magnitude above leaders"), townhall 18078 (organizers favour cumulant
propagation; effective rank falls with depth), thylinao1.github.io (leader mechanism unpublished).
