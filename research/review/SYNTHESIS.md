# Multiperspective adversarial review — synthesis (2026-10-09)

Four independent lenses, each told our "family at its floor" conclusion was wrong.

| Lens | Verdict on the floor claim | What survived as a lever |
|---|---|---|
| A rules/metering | Holds; no metering loophole (dtype, setup, per-MLP averaging, shipped tables all checked) | concatenate copies (−0.11 pt, v58_qa built); reshape lever was first-predict only (dead) |
| B math | Holds for the family; corrected the error budget | last 5 layers originate 75–79 % of final MSE; gain 0.78–0.85/layer; depth-gated κ4 carrier (G-RB54) |
| C competitive intel | "Unknowable" is wrong: public feed gives every leader's timeline | leaders' raw steps track the κ4→κ3 feed discussion; leaders carry ~1× n of κ3 width |
| D red-team | No bug or mismeasurement costing a large factor | old-tier entry eigh/oversampling wastes 0.68 pt (est_noeig ≈ −3.3 % adjusted); self-Gram einsum; residual cliff is the main tail risk |

## Convergence
- B + C: late-layer κ4 is where accuracy lives. G-RB54 confirms uncorrected (L0=12: 0.896 for +0.91 pt)
  but the learned head already absorbs it (shipped-head arm 1.03). Standing rule: pre-register the
  HEAD arm for anything upstream of the head.
- A + D: remaining exact/near-exact cost savings ≈ 4 % (v58_ne = v58_qa + noeig + self-Gram + no pad).
- D: the learned corrector is genuinely out-of-sample (×1.25 worse without it on VALID-20).

## Open (as of writing) — verdicts as of 2026-10-09 ~18:10 UTC (convergence-test agent; details: R2_GO_NOGO.md RESULT blocks)
- G-RB56 net-level g predictor — **FAIL (a)**: the 9.9 % per-MLP oracle is 84 % the COMMON g mis-scale (already shipped in G-RB16); the per-net residual is 1.6 % raw and no K2-chain feature predicts it (corr ≤ 0.35, shrinks to the common scale). (b) skipped by rule.
- G-RB55 rank-p κ4→κ3 feed — **KILL**: free p=2 {I,C} −2 %; p=4 (two dense modes, 2.3× the price bar) −8 %; the feed's gain is EARLY-layer (depth-gated to 12–15 it collapses to −1.7 %).
- G-RB54 depth-gated SSC — uncorrected FIT PASS (L0=12 0.896 @ +0.91 pt; L0=13 0.918 @ +0.68 pt) but **G-RB54b head refit at L0=13 FAIL**: +1.8 % WORSE than the shipped lean pair on VALID-20 (4/20 improve; adjusted ≈ 1.047). The late-layer κ4 gain is not additive to the learned head (head TF R² 0.20 → 0.137 on the gated chain). No v59.
- G-RB58 exact layer-1/2 moments (Lens C H2) — **KILL by bound**: the chain's layer-1/2 mean error (7e-10) is already AT the 1e9-sample truth floor and layers ≤ 2 originate ≤ 0.2 % of the final MSE (Lens B adjoint); an MC oracle at N = 2^21 is 2000× noisier than the chain there (arm A: +79 % = injected noise). Phase-0 catch: `mc_cache_alllayers_mlpK` are generator nets 1000+K, not official K.
- G-RB59 fire-rate pruning of the κ3 legs (Lens C H4) — **KILL**: p* = 0.10 drops 22 % of the rows for +17 % raw (adjusted 1.06 even at the formula saving); p* = 0.17 +75 %. Cold neurons' κ3 rows are not dead weight once transported. p* = 0.05 (18 % rows) +0.9 % on FIT-3 but **+3.6 % on VALID-20 (G-RB59b FAIL, adj 0.995 at half the formula saving)** — marginal, port-dependent.
- G-RB57 v58_ne ladder vs v57_azs — another builder's; not in the gate ledger at this writing.
- Standing rule confirmed three more times (G-RB13/33/54/54b/59): pre-register the HEAD arm bar for anything upstream of the learned head — every uncorrected FIT pass this cycle failed net of the head.
- Bottom line for the lenses' convergent prediction: FALSIFIED on this chain net of the head. The K3 + SSC + MIX2 family is at its floor on this metric by every lens we hold; the remaining levers are exact cost savings (v58_ne, ≈ 4 %).

## Bottom line
No lens found a route to the leaders' ~2× lower util at equal accuracy. Expected near-term gain ≈ 4–8 %
(→ ~4.9e-9), not a jump to the top. Reaching #1 needs the undisclosed lower-width κ3 carrier.

> Correction (2026-10-09, from V7 review): the head TF R² baseline quoted above as "0.20" belongs to the g×1 `src` chain; the shipped `src92` head reads 0.1420, so no chain here moved the head R² by ≥ 0.05. The head-substitution finding rests on the VALID-20 results, not on R².
