# LENS F — audit of the floor argument (LENS_E §0/§1): which assumption breaks, if any (2026-10-11)

Agent: floor-audit (Fable 5.1), ~2.5 h. Brief: "find the flaw in our own floor argument, or a construction that beats it" — attack the assumptions
(a) κ3 need not be carried as a tensor (slice-only O(n³) recursion with a good closure), (b) "every source equal weight after transport",
(c) a strong learned component replaces the κ3 machinery, (d) anything silently assumed. Read: LENS_E, BREAKTHROUGH, NEWREP, GAP504, YOUNG_CHAIN,
OPERATING_MODEL §5, DESIGN, MODEL_ERROR, ERROR_BUDGET, SYNTHESIS, thread 18218 prose, arXiv 2605.05179 S.4.3. Two cheap f64 oracles on FIT 0/2/4
(G-RB67, G-RB68; pre-registered in R2_GO_NOGO before running; scripts and rows in `research/rb67/`). TEST untouched, nothing submitted, no
participant code opened, no existing file modified except the append-only ledgers (R2_GO_NOGO, PROGRESS, OPERATING_MODEL §5).

## 0. Verdict (blunt)

1. **No assumption of the floor argument broke.** Two of its PREMISES are wrong, and correcting them does not open a route:
   - LENS_E §1 "Σ_z / C∘ggᵀ is a flat bulk, rank ≈ n": **false at depth.** The off-diagonal Frobenius energy of Σ_z^s outside rank 128 is 0.40 at
     s=0 (W₁ᵀW₁, Wishart-like) but 0.025 at s=6, 0.008 at s=10, 0.003 at s=14 (G-RB67 part A, all three nets within ±0.002). The top eigenmode
     carries 0.4 % → 8.7 % of the trace from s=0 to 14; var_z falls 2.0 → 0.18 (the generator is sub-critical). The A leg of a source born at s ≥ 8
     is therefore 99.5 %+ a (diag + rank-128) image of its P leg. **But the (2,1) read needs the leg to ≈ 1 % in NORM (1e-4 in energy)**: the
     measured summed young-tier read error is 0.09–0.10 at r=128 and 0.06–0.07 at r=256 against a 2 % bar (G-RB67 KILL, §2.5). The read
     amplifies the leg's relative norm error ×1.5–2 (Hadamard self-products), and the ε²-law (504aldo F71: ΔMSE ≈ 4.2e-6 ε²) turns 10 % into
     +0.5–1× raw. This single arithmetic fact is the mechanism of every rank cliff in the ledger (G-FW knee 5n, G-RB44, 504aldo §2.4 "one notch
     lower is a cliff"). The 4-units/young-source-layer bill stands; the cheapest exact-enough form is 3 + 4r/n with r ≈ n.
   - LENS_E §1 "odd cumulants are quenched disorder, no low-rank structure": **half false.** The (1,1,1)-induced part Δ of the next layer's D21 is
     exactly orthogonal to the memoryless (slice-only) read — cos²(Δ, R_mem) < 1e-3 at every layer, Pythagorean ‖R_mem‖² + ‖Δ‖² = ‖Tz‖² (0.80 + 0.20)
     — and its norm share is a constant 0.40–0.49 of D21 at EVERY layer 2–14 on all three nets (energy 0.16–0.24 = 504aldo's 18–23 %, reproduced
     on our chain by an independent instrument). Yet 72–77 % of Δ's energy sits in 32 singular directions at depth (93 % in 128), growing with
     depth as the covariance spectrum concentrates (G-RB68). "Quenched" means W-dependent, not full-rank. **Still KILL** for brief (a): the bar
     (raw ≤ 3e-8) needs Δ recovered to ≤ 10 % of its norm (R² ≥ 0.99); its top-128 subspace holds 93 % of the energy but is not available
     without the tensor (a Tucker read of the whole (1,1,1) sector at R=128 costs ≈ 16 n R³ ≈ 16 units/layer for the core, more than the dense
     tier, and still loses ≥ 7 % energy = 12 % of D21 = +6e-8 raw), and every O(n²) live-state regression measured so far reads ≤ 0.5 (G-RB60,
     504aldo F65 "+0.02 R²").
2. **(a) dies by arithmetic, (b) is confirmed by measurement, (c) dies by information, (d) lists six silent assumptions, none of which is a lever.**
3. **No candidate reaches raw ≤ 3e-8 at util ≤ 0.13. No v67, no ladder run.** The honest statement is unchanged from BREAKTHROUGH §5 but is now
   sharper: the leaders' bill (≈ 1.7–2.1 dense products per source-layer with all 15 sources alive, §1) is **below the 3-product floor of any
   source whose birth has full-rank off-diagonal content** (§2 theorem), so their chain either carries a κ3 birth that is NOT our
   f2∘Sym(I ⊗ DC_off ⊗ DC_off) object, or carries no per-source object at all. Nothing in our content reaches it by re-association or compression.

## 1. The budget, restated (correction to LENS_E §0's "≤ 3–4 CP sources")

1 unit = one n×n×n product = 2n³ FLOPs; budget 2^41 = 1024 units. Strassen at depth d bills (7/8)^d on multiplies PLUS the block adds
4.5n²·Σ_{l≤d}(7/4)^{l−1} (flopscope bills them; 18 adds/level, 15 for Winograd): d5 0.513 + 0.045 = **0.558**, d6 0.449 + 0.081 = **0.530**,
d7 0.393 + 0.144 = 0.537, d8 0.344 + 0.254 = 0.598 (Winograd: d6 0.516, d7 0.513). The FLOP optimum at n = 1024 is d6–d7 at −5…−8 % vs d5 —
ngmitam's −3.5 % graded and "L8 positive" are this curve. **Strassen depth is a ≤ 8 % lever, not a 2× one** (silent assumption (d)-ii below).
Util 0.105–0.13 ⇒ 1024u/0.558 ≈ **193–239 dense-product-equivalents** for the whole net. Covariance Σ_z = WᵀΣ_hW ≈ 1.5/layer × 15 ≈ 22 → κ3 gets
≈ 170–215 over Σ_{l=2}^{15}(l−1) = 105 source-layers if every source is alive: **1.7–2.1 dense products per source-layer.** LENS_E phrased the same
budget as "≤ 3–4 sources at 4 units"; that phrasing suggests the leaders drop sources, which is measured dead (504aldo F61 W=4 1.0e-6, F66 "skipping
one is ~4×", YOUNG_CHAIN 6.7e-7). The phrasing that matches both facts (all sources alive, half our cost, BETTER raw) is **"≤ 2 dense products per
source-layer"**: one for transport and one for the read. §2 asks whether our birth admits that.

## 2. Cost identities of a young source (derived; what each buys) — the ≥ 3-product theorem

Notation (srcchain.py): birth legs P = I and A = f1∘Cz_off (`A1 = f1[:,None]*Cz`, zero diagonal); both are aged by the same linear map
X ← Φ∘(WᵀX), so at every later layer **A_s^l = P_s^l a_s exactly**, a_s = D_s Cz_off^s static (G-RB62/63 used this). The bill: transport P (1),
transport A (1), read with right factor Aᵀ (1), read with right factor Pᵀ (1) = 4 (thin legs, Hadamards and the D3 diagonal are O(n²)).

| # | identity / re-association | dense products per young source-layer | why it does not drop below 4 |
|---|---|---|---|
| 2.1 | form A = P·a_s instead of transporting A | 4 | the product is n³, same as the transport |
| 2.2 | Horner over right factors: Σ_s X_s P_sᵀ = ((X₁W̃₂ᵀ + X₂)W̃₃ᵀ + …) | 4 | l−1 products replace l−1 contractions; the left factors still need the transported A for the Hadamards |
| 2.3 | shared FULL-RANK basis: Σ_z^s ≈ G_sG_sᵀ (G_s = W_sᵀD_{s−1}⋯D₁W₁ᵀ) ⇒ A_s^l ≈ G_l G_sᵀ, P_s^l = G_l G_s^{−1}D_s^{−1} (column scaling passes through the read): all legs of all sources = ONE transported basis × static coefficients — the κ3 tensor is a static core read in input coordinates | 4 | the read needs (G_lM_s) ∘ (G_lN_s) = (G_l⊙G_l)(M_s⊙N_s): Khatri–Rao, n⁴; forming the dense legs is n³ each = the transport. The k-mode / input-chaos idea (G-RB46) is this wall seen from x-space |
| 2.4 | polarization to one leg type: Sym(e⊗b⊗b) = [(e+b)³ + (e−b)³ − 2e³]/6 (G-RB49) | 5 | three cubes (P+A, P−A, P) → 2 transports + 3 Gram-type reads |
| 2.5 | a_s = d(c) + U_rV_rᵀ (+ dropped bulk) ⇒ A = P d(c) + (PU_r)V_rᵀ: thin transport, Hadamard partners formed at n²r, BOTH reads collapse onto right factor Pᵀ (Aᵀ = d(c)Pᵀ + V_r(PU_r)ᵀ) | **3 + 4r/n** | the only re-association that removes a dense product. **G-RB67 measured it: the summed young read is 10 % off at r=128, 6.7 % at r=256 (bar 2 %)** → r ≈ n → 4 |
| 2.6 | sketch the column sum over hubs j (importance-sampled m columns) | 4·m/n | 2 % needs m ≳ 2500 > n |
| 2.7 | fewer hub columns by f2_j / global top-r selection (G-FW, G-V9) | — | knee at 5n total width; column importance flat (504aldo F76) |

**Theorem (this representation).** A source whose birth is Σ_j w_j Sym(e_j ⊗ b_j ⊗ b_j) with B = [b_j] of full off-diagonal rank needs ≥ 3 dense
products per layer: P must be dense (its columns are the hub probes; rank 128 holds 53 % of its energy at age 1), one dense Hadamard partner
A = Pa must exist as an n×n matrix (Hadamard products do not factor: 2.3), and one dense contraction reads them. The 4th product (right factor
Aᵀ) is removable only when a_s is (diag + rank-r) to the read's accuracy, which G-RB67 puts at r ≈ n. A 2-product source needs a_s DIAGONAL —
that is the (3)-slice-only (marginal-Edgeworth) birth, dead at 4–5e-6 (504aldo F60). **Hence the leaders' ≤ 2 products/source-layer is not a
re-association of our birth; it is a different birth (or no per-source object).** LENS_E §1's conclusion holds; its "flat bulk" reason was wrong.

## 3. Brief (a): the slice-only recursion — why exactly it fails, with our own numbers (G-RB68)

Exact statement. Let κ3_h^{l−1} have slices T_h (the closure output, (3)-diagonal exact). The memoryless tensor M = F(I, I, V), V = 3T_offᵀ + diag(D3)
(DESIGN step 5) has the same slices and zero (1,1,1) part; after one transport its read is R_mem = read_block(1, Wᵀ, Wᵀ, WᵀV) — ONE dense leg for
everything, ≈ 2 units/layer total, the leaders' kind of bill. The chain's actual read Tz^l − R_mem =: Δ^l is the (1,1,1)-induced part,
Δ(i,k) = Σ_{a≠b≠c} W̃_ai W̃_bi W̃_ck κ3^{(1,1,1)}(abc) = w̃_iᵀ M_k w̃_i with M_k = Σ_c W̃_ck κ3(:,:,c): a probe of the full tensor along the
NEXT layer's weight columns. Measured (FIT 0/2/4, layers 2–14, `rb67/rb67_slice.jsonl`):

| quantity | value (all nets, all layers) | reading |
|---|---|---|
| ‖off Δ‖/‖off Tz‖ | **0.40–0.49**, no trend with depth | energy 0.16–0.24 = 504aldo F65's "18–23 % of D21 energy", reproduced |
| ‖diag Δ‖/‖diag Tz‖ | 0.25–0.34 | the D3 (skewness) read loses a quarter of its norm too |
| cos²(Δ, R_mem) | < 1e-3 (mostly < 1e-4) | Δ ⟂ R_mem exactly: ‖R_mem‖²/‖Tz‖² + share² = 0.80 + 0.20 = 1.00; the best per-layer scalar λ on R_mem is 0.99–1.01 and buys nothing |
| Δ top-8 / 32 / 128 singular energy | 0.10/0.31/0.71 at l=2 → **0.51/0.77/0.93** at l=14 | NOT structureless; concentrates with depth like Σ_z. Tz itself: top-32 0.67 → 0.96 |
| rms per entry Δ / Tz | 0.0014 / 0.0035 at l=14 | per-entry Δ ≈ 0.4 of the read |

Consequences, by the ε²-law (504aldo F71, ΔMSE ≈ 4.2e-6 ε², ε = relative rms error of D21; our chain sits at ε ≈ 2 %):
- A pure slice-only chain has ε = 0.45 → +8.5e-7: 504aldo's 9.1e-7 (F65) and Puffi's 9.8e-7 (F82) from an instrument that never ran their code.
- The brief's bar (raw ≤ 3e-8, i.e. ≤ +0.8e-8 over our 2.2e-8) needs ε ≤ 4.4 % ⇒ **the closure must regenerate Δ to ≤ 10 % of its norm, R² ≥ 0.99**,
  on a target that is orthogonal to everything the slice transport carries.
- "A better slice recursion": (i) a scalar/diagonal rescaling — λ ≈ 1.00, zero; (ii) Sym(u ⊗ V) terms (the κ4→κ3 feed's form, 2 units each) carry
  the rank-1 component of the P legs — column norms of P have CV 0.03–0.13 and rank 128 holds 53 % of P at age 1 (LENS_B §1a, 504aldo §2.4):
  K ≈ n terms per young source, i.e. the CP chain again; (iii) a low-rank surrogate of Δ itself: its top-128 subspace holds 93 % (residual
  27 % of ‖Δ‖ = 12 % of D21 → +6e-8 raw), and that subspace is a property of the tensor contracted with the NEXT W — the only ways to get it are
  the dense legs (what we do) or a Tucker core: basis range-finder on 30n leg columns (≈ 30R/n units) + projecting 15n hub columns into an
  R³ core (15 nR³ = 15 units at R=128) + read nR³ — more than the dense tier for R ≥ 128 and lossy; at R ≤ 64 it is cheap and loses ≥ 30 %
  (NEWREP §1's Khatri–Rao break-even r < √n ≈ 32); (iv) a regressed/learned closure on O(n²) live-state features: G-RB60 (15 modes incl. the
  exact slice transport) read ≤ 0.5 for the state modes, 504aldo "+0.02 R²", G-YC 0.03. 0.5 ≪ 0.99. **KILL by arithmetic.** The one thing
  G-RB68 adds beyond 504aldo: the lost term is low-rank-dominated and EXACTLY orthogonal to the memoryless read, so it cannot be absorbed by any
  rescaling of what a slice chain already computes — the next closure would have to produce new directions, not new coefficients.

## 4. Brief (b): "every source equal weight after transport" — confirmed for the quantity that matters

The e2e numbers were already measured (drop one source ≈ 4× F66; W=4 1.0e-6 F61; young-only 6.7e-7). For the READ specifically, G-RB67 part B
records each young source's off-diagonal (2,1)-read norm by age at l=14: **0.54 / 0.51 / 0.48 / 0.41** for ages 1–4 (net 0; nets 2/4 0.80/0.67/0.63/0.54
and 0.59/0.50/0.42/0.38): a 25–35 % decline over four ages, not exponential forgetting. At l=6 the decline is steeper (1.37 → 0.46) because the
early layers have var_z 2.0 → 0.6 (births at higher variance read larger) — a variance effect, not an age effect. Per-entry scale of all sectors
≈ 1/n (LENS_E §1) is consistent with this. **Holds.**

## 5. Brief (c): a strong learned component replacing most of the κ3 machinery — dead by information, not by effort

- Measured: on the young-only chain the drift is 22× larger than top-6n's and per-neuron + row-reduction features predict 3 % of it (G-YC, VALID
  R² 0.027–0.029; r1n 0.05); a per-(net, layer) constant explains 0.4 %; 504aldo F46/47/68 "< 0.09 correlation, 1.01×"; our shipped head on the
  FULL chain reads TF R² 0.142 and is feature-limited (G-RB28/29), and five uncorrected upstream gains were absorbed by it (lesson 11).
- Why: what a slice-only or young-only chain lacks is Δ (§3) — an n×n object orthogonal to everything the chain carries, 45 % of the read's norm,
  whose per-entry sign is set by the next layer's weights. A corrector on per-neuron features cannot write n² signed numbers; a corrector that
  could would have to consume the (1,1,1) tensor, i.e. be the chain. The "learned networks that consume the cumulant estimates as features" ARC
  credits to the warm-up winners (PRIOR_ROUNDS §1; 256×8, where the full factorized K=3 is ≈ 30n³L² ≈ 2^35 FLOPs) sit ON a chain, as MIX2
  (−25 %) sits on ours; they do not replace carried state. **KILL.**

## 6. Brief (d): silent assumptions in LENS_E §0/§1, audited

| # | assumption | status | consequence |
|---|---|---|---|
| i | "4 units/source-layer irreducible" | measured (G-RB67): 3 + 4r/n is exact algebra; r ≈ n at the 2 % bar → 4 | holds |
| ii | "everyone bills Strassen d5" | FLOP optimum is d6–d7 at −5…−8 % (adds billed, §1); residual clock caps us at d5 (NEWREP §4) | ≤ 8 % lever, not 2×; the 0.14–0.15 cluster at raw 1.7–2.0e-8 is consistent with 504aldo's chain at d6–d7 with the old tier trimmed, J2W/lode_dockx at 0.10 are not |
| iii | "Σ_z is a flat bulk" | false at depth (99.6 % rank-128 Frobenius at s=14) | no lever: the read needs 1 % norm (§2.5); it does say the old tier's basis law (3n/8 at age 4 …) is the covariance spectrum, not a κ3 property |
| iv | "the lost (1,1,1) term is structureless" | false: 77 % in 32 singular directions at l=14, exactly ⟂ R_mem | no lever (§3 iii): the subspace needs the tensor |
| v | "the leaders carry per-source κ3 objects" | unknowable from prose; their raw is also 1.5–2× BETTER, so they carry MORE content at half the cost | by the §2 theorem their birth is not ours; the one public hint is 504aldo #5: the aug-core's diagonal, not the (2,2) slice, carries their κ4 law — a matrix-core (K=4-type, "augmented") carrier whose (2,1,1) feed is ONE leg per layer, not per source. A full K=3-augmented chain is 72n³L² + 264n³L ≈ 10× budget (Table 1), so if that is the family they run a drastically reduced form of it. Not derivable here. |
| vi | "the generator is critical (gain ≈ 1)" | var_z halves every ~4 layers (2.0 → 0.18): sub-critical; mean-error gain 0.95 (BREAKTHROUGH §1) | explains why early-born sources read larger at l=6 (§4) and why the last 5 layers originate 75–79 % of the final MSE (LENS_B); not a cost lever |

## 7. What would falsify this audit (so the next agent does not re-derive it)

- A measured young-source birth whose a_s is (diag + rank ≤ 64) to **1 % in norm** — G-RB67 says 0.2–0.4 % in energy is the best at depth, i.e.
  4.5–6 % in norm; the gap is ×5 in norm, ×25 in energy. Nothing in the chain's own statistics gets there.
- A regression of Δ^l on O(n²) live-state objects with held-out R² ≥ 0.99 — best measured ≤ 0.5 (G-RB60).
- A Tucker/low-rank read of the (1,1,1) sector at R ≤ 32 with ≥ 90 % of Δ's energy — measured 31 % (l=2) to 77 % (l=14) at R=32.
- Evidence (code or prose, after Oct 17) that a leader's birth tensor is not f2∘Sym(I ⊗ DC_off ⊗ DC_off).

## 8. Files, gates, and what was NOT done

`research/rb67/rb67_capture.py` (lc_hook dump of the f64 shipped-twin state; uncorrected finals 2.5549 / 4.1877 / 3.3144e-8 = the G-RB60 session
control to every digit), `rb67_oracle.py` → `rb67_oracle.jsonl` (G-RB67), `rb67_slice.py` → `rb67_slice.jsonl` (G-RB68), `capture*.log`,
`oracle.log`, `slice.log`, `state_0000{0,2,4}.npz` (3 × 130 MB, deletable). Gates: G-RB67 KILL, G-RB68 KILL (both pre-registered with bars and
predictions; G-RB68's rank-profile prediction was wrong by ×5 and is recorded as such). No v67 folder, no ladder run, no submission, no TEST read.
Expected adjusted gain of this lens: **0**. Correction to LENS_E worth keeping: replace "flat bulk / quenched disorder" by "full-rank-at-birth
Hadamard partners whose read needs 1 % norm accuracy"; the conclusion ("a different birth, not a different carrier") is unchanged and now rests
on a theorem (§2) plus two measurements instead of a spectral intuition.
