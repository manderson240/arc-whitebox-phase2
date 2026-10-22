# Cost structures of public K=3 chains, forum + attached PDFs (2026-10-17)

Method: discourse JSON for the whole category (id 2991, 101 topics; control: category list 101 topics, newest 18250). Post prose and attached PDFs converted with pdftotext. No repo/notebook/code opened, nothing posted. Does not repeat MINING_20261015/16 items except where a cost number is new.
Tags: V = VERIFIED-SOURCE (I read it, post or PDF). H = HEARSAY (quoted by someone else).
Unit: 1 unit = one n^3 matmul = 2^31 FLOP; B = 1024 units; util 0.209 = ~214 units.

## 0. Headline
- NO public write-up reaches util 0.10-0.13 at raw 1.1-1.35e-8 on 1024x16. Nobody with a rank under ~10 has published method prose. Best public cost/raw pairs (all V):
  - 504aldo 18218 (2026-09-10): raw 2.13e-8, C/B 0.2526 (V29: 260 units = 0.254 B); old-tier-free bill 0.150 B (raw 1.35-2.9e-7 without old tier).
  - Artyom_Mazur 18249 (2026-10-16): raw 2.03e-8, util 0.1833 (k3z, graded 3.7357e-9), PDF 33 pp.
  - il.miscusi 18248 (2026-10-15): e30_a raw 2.055e-8 at 0.152; carried-G+extraction raw 1.72e-8 at 0.301.
  - DD_team 18250 (2026-10-16): raw 3.206e-8 at 0.8525 B (full-history K3, no tiering).
- Leaders' 0.149 (Puffi) / 0.152 / 0.164 on 2026-09-10 are H, via 504aldo 18218/1 §3. Their mechanism for ~0 cost old content is unpublished. Artyom (18249) says the same: "never got under the floor", gap-to-floor worth x0.55.
- Our 0.209 / 2.12e-8 already beats 504aldo (0.2526) and Artyom (0.183 at 2.03e-8 is slightly better util at equal raw).

## 1. Leg/rank counts, products per layer (numbers)
| Item | Number | Author, post, date | Tag |
|---|---|---|---|
| Reference K3 source = 7 dense products/source-layer; factorized = 4 | "7 -> 4 units per source-layer" (two dense contractions with right factors A,P) | 504aldo 18218/1, 2026-09-10 | V |
| Per young source under Strassen d5 | 2.17 units/layer; at most 4 young alive -> flat 8.7 units/layer from layer 5 | 504aldo 18218/1 §3 | V |
| V29 bill split | 260 units: young 116, old 107, thin/elementwise 25, covariance 7, whole nonlinear closure 6 | 504aldo 18218/1 §3 (F86) | V |
| Old tier marginal cost | ~1.1 unit per extra old source per layer (shared basis) | same | V |
| Old-source basis | n x 384 after age 4, nested n x 224 after age 7; rank law ~3n/8 at age 4, n/4 age 6, 7n/32 age 7; r=256 at age 4 = +22% raw; r=128 at age 7 = +15%; cost 0.478 -> 0.383 -> 0.367 B for +3.4% / +1.2% raw | same | V |
| Residual (D21 feedback) leg rank | 16 (8/16/32 -> 2.17/2.14/2.14e-8) | same | V |
| Artyom cost map (k3z, one net, FLOP share) | leg transport 23.5% (young legs + band basis P^T moved, d5); D pairing 19.9%; band members materialised 16.7%; members' pairing 11.8%; band entry (QR + triangular inverse) 8.2%; covariance 11.5%; ALL step mathematics 3.3% (pair expansion 0.43, closure 0.06, corrector 0.05, readout 1.9, births 0.9); rest 5.1% | Artyom_Mazur 18249 PDF §4.1, 2026-10-16 | V |
| Artyom thin leg | rank 24 (randomized range finder; dropping it x10.5, rank 24 within x1.004 of exact split) | PDF §3.1 | V |
| Artyom band | rank 448 entry age 5 (rank 320/384/448/512 -> x1.228/1.032/1/1.033; age 4/5/6 -> x1.125/1/1.016). Riding band: costs 3% raw, saves 11% of bill (x0.893 adjusted, 100/100) | PDF §3.6, §5 | V |
| miscusi ledger (units of 2^31, budget 1024) | engine @Strassen d3 187.1; dead-neuron thr 6 vs 2.85 +45.5; G transport 28.7; capped (2,1,1) production 31.6; K211 birth 10.6; pK slices 5.1; extraction 0.1; total 307.5 | il.miscusi 18248 PDF, 2026-10-15 | V |
| Carried kappa4 core cost | 2 dense n^3 per layer = 28.7 units; "memo22" also 2 dense/layer (Artyom, beaten by scalar closure at zero products: 3.75e-8 vs 4.25e-8 radial, but wrong per-neuron pattern, corr 0.23-0.53) | miscusi; Artyom §3.2 | V |
| Dense kappa4 per-source channel (paper augmented K3) | 7 units per source-layer, >= 0.95 B | 504aldo 18218/1 | V |
| Leaders' multipliers | 0.149 / 0.152 / 0.164 | 504aldo 18218/1 §3 | H |

## 2. Thin/shared kappa3 carriers (K=2, K=3)
- No post uses a K=2 or K=3 *carrier width* (columns) for legs. Closest: 504aldo thin residual leg rank 16, Artyom thin 24 (V). Phase 1 K3-lowrank dead for final mean (cross cumulants only matter for deeper propagation): topic 18085 (submission 317660 write-up, 2026-07-21, V).
- Hub-column caps ("atoms"): cap 4n D21 rel error 0.39; 8n 0.03-0.14; need 0.02 (504aldo 18218/1, V). AndreasHad04 cap-3776 (18218/4, 2026-09-22, V) already in our killed list.
- Five compressions of K3 that looked cheaper and died (Artyom PDF §6.1, V, N54/N55/N58/N59/N76): shared subspace re-rotated each layer (model 26.3->21.4% B, measured 27.78% vs 26.62% baseline); path leg at rank 256 (break-even before QR); old tail as one rank-n CP block (400x gap, no warm start: adding one source throws error 2.9% -> 48.7%); same by unbiased sampling (needs r~1.5e6 columns); smaller per-layer basis r'=256 (x1.11-1.15 raw), drop three oldest sources (x1.17 raw), D from young only (x9.25). Rule: price the BASIS per layer; only a basis that rides the transport and is never rebuilt wins.
- all-distinct part of kappa3 = 28.8% of next diagonal per layer at 1024x16 and not closed by any O(n^2) state (Artyom §6.2, V).

## 3. Dropping layers or sources
- DD_team 18250 (2026-10-16, V): keep only newest H complete K3 birth generations. H=0/1/2/4 cost 9.13/17.93/27.25/43.81% B; adjusted proxy x12.9/x16.6/x15.9/x11.8 worse than full-history control (5 public MLPs). DEAD.
- 504aldo W=4: raw 1.02e-6, monotone worse as W falls (18218/1, V). Artyom N76 above. Consistent: window cuts are dead; only tiering with a shared basis works.
- Dead-neuron / saturated cuts are ACCURACY GAINS (Artyom §3.5, V): alpha<-2.5 rows out of every contraction (rectangular Strassen padded to quantum): util 26.3->24.8% for +1.4% raw; MATCHED row+column cut (also the dead-side birth columns) x0.950 adjusted 100/100, matched/row = 0.9985/0.9970/0.9928/0.9790/0.9475 at thresholds -3.0..-2.0; production stores legs transposed as one wide stack of hub rows so transport = one row-stack product and D pairing = one contraction. E2: drop rows of D for saturated alpha>2.5 neurons and restore their kappa4 level with one matvec: raw x0.943 (naive removal x1.34). Without matched cuts raw x1.24; without E2 x1.07.
- miscusi: dead threshold -2.85 vs 6 = 45.5 units (15% of his ledger); relaxing to 6 is what carried-G needs (D21 slices corrupted 25% at L4, 58% at L14 by compaction). Fire-rate p*=0.05 (our shipped) is alpha~-1.64, already beyond both.
- miscusi "no K211 from old sources": raw +6.6%, saves 0.029 C/B and 532 ops (18248, V).
- 504aldo last-layer trim (skip D21 and covariance sandwich, 8% of C), Artyom/DD_team same (V). Ours: shipped.

## 4. Cheaper covariance propagation (diagonal + low rank)
- None found for the pre-activation covariance. Covariance = 11.5% FLOPs (Artyom) / 7 units (504aldo): C_pre = W^T(CW) as 3 of 4 symmetric blocks, level 5 (Artyom §3.8: k3t-k3z together x0.931 of the x0.693, i.e. 18.7->18.3%; V).
- flopscope bills repeated-operand einsum("ni,nj->ij", X, X) at 0.502x of the matmul (distinct-element accounting) - hyojun_kwon 18154 PDF §9, 2026-08-12 (V); but the symmetric tag on a tracked-array propagation einsum gives NOTHING in situ and as_symmetric adds validation cost (V). The 2026-10-12 billing-fix PRs (18241) touch einsum symmetry tags: re-meter.
- Perfect two-moment closure scores 5.5e-8 adjusted (5th place); the covariance is not where the leaders' gain is (18182 via 18157 census, H for this note; V in 18182 prose).
- "Rank 2.74 backward operator", "6-dim Lyapunov subspace carries 68% of final error" (18182 post, V) - interesting for a diagonal+low-rank *error* corrector, not for propagation cost.

## 5. Strassen / Winograd
| Item | Number | Source | Tag |
|---|---|---|---|
| STRASSEN_MIN 32->16->8 | C/B 25.42 -> 25.29 -> 24.52% at identical raw 2.13e-8; local L5 0.2670 / L6 0.2624 / L7 0.2592 / L8 0.2597 (bottoms at 8); peak RSS 3.96/4.31/5.08/5.99 GB; grader gains less than local (L5->L7 0.90% vs local ~2.9%) | ngmitam, 18218/6, 2026-10-04 | V |
| Per-contraction pricing by FLOPs saved per wall-second | 0.49 %/s (leg transport) down to 0.27 %/s (D pairing); next site 0.094 %/s, not taken; leaf 64->32 everywhere x0.939 FLOPs but wall x2.2 (~140 s vs 120 s cap), RSS 7.21 of 8 GB | Artyom PDF §6.1 | V |
| Level-5 sites run 8-14 GFLOP/s vs 17-30 at level 4 | | Artyom §4.1 | V |
| Winograd 15-addition form; explicit triangular R^-1 where flopscope bills solve as LU; symmetric C_pre | part of x0.931 above | Artyom §3.8 | V |
| Strassen depth ladder, width 256 sampler (Phase 1): optimum depth 2 once residual billed (depth 5 = 18:1 loss) | | bin_yong_bong 18184, 2026-08-18 | V (Phase 1, not our regime) |
| Row-bucketing vs Strassen substitutes, worse combined (1.11x / 1.18x / 1.19x / 1.02x) | | amalgonim 18151, 2026-08-11 | V |
| out= preallocated buffers, 0.02 ms/op, base chain 0.331->0.170 s residual | | 504aldo 18218/1 | V |
| Rank-40 Tichavsky rectangular | 54->40 block products, 49% of ordinary leaf products | andrei_bulzan via 18157/9 | H |

## 6. Exact algebraic sharing (new, DD_team 18250, V, 2026-10-16)
- B1a: at birth tree-A = I diag(q2) and another B role = I. They share one evolving block U; store/transport U once, apply column coefficients c when reconstructing A (later left transport L and row gains commute). Archived: 2163135147211 -> 1907602996258 FLOPs (-255.5e9, -11.8%); remote bill 98.37% -> 86.75% B; mean final MSE unchanged 3.206e-8.
- B1b: newest identity block deferred at birth (W^T @ I = W^T); transport the rest, insert W^T at next layer. 1907.6e9 -> 1874.8e9 (-32.8e9, -1.7%); 86.75 -> 85.25% B; wall time +25.8% (13.43 -> 16.89 s). Exact up to float32 reassociation.
- Applicability: in a chain where young sources are born with identity legs (504aldo's "P leg is born as identity: full rank at birth"), P and one A role are literally the same transported matrix for the first transport. Whether our factored chain materialises two copies is the check.

## 7. Per-layer budget tables
- 504aldo steady-state per layer: young 8.7 units (4 sources x 2.17), old ~107/ (layers) ~ growing 1.1 per extra old source, covariance 7 total, closure 6 total (18218/1, V).
- miscusi (18248) and Artyom (18249) tables above (V). No per-layer (layer-by-layer) ledgers published by anyone.

## 8. Phase 1 transfer (read)
- 18154 hyojun_kwon: bill composition is its own axis; float32 state -4.06%/-3.2% graded; stats.norm silently float64; repeated-operand einsum 0.502x; a -38% local residual-wall cut moved grader 0% (residual machine-specific). V.
- 18097/18085/18201/18182: sampling/low-rank K3 negative for final mean; no K3 cost structure.
- 18175 Puffi SSC PDF (Cipo, 2026-08-16, V): at 256x32 SSC 0.501 B vs parity-checked factorized K=3 0.373 B vs full K=4 ~10^2 B; kappa4 regenerated from <=4 covariance-response modes coupled by small Lambda; "FreshCrossRepair": up to 64 fresh angular CP columns, transported cross-family block capped at 4; SSC is Puffi's closure, which 504aldo says appears among the 0.149 leaders (H: only the name).
- 18246 kai_leal (2026-10-15, V): extra (3,1) slice closure 3 elementwise n^2 ops/layer, -3.0%; free.

## 9. Ranking: ideas most likely to cut products/layer >= 25% at < 5% raw loss
HONEST CAVEAT: no single public idea is demonstrated to give 25% on a chain already at 0.209. Ranked by expected bill cut x certainty:

1. Ride-the-transport shared basis, never rebuilt (Artyom 18249 PDF §3.6/§6.1; 504aldo rank ladder 18218/1). If our old-tier basis is refit/re-orthonormalised each layer, switch to a fixed-rank basis moved by the same products as the legs, entered once via QR with explicit triangular inverse. Artyom: -11% bill, +3% raw (x0.893 adjusted 100/100). Our old tier is the dominant cost (504aldo: 107/260 = 41%). Tune rank 448 / entry age 5 at n=1024 (sharp optimum, both sides worse).
2. Matched dead row+column cut plus E2 saturated-row removal with kappa4 level restored by one matvec (Artyom §3.5). Accuracy-positive (x0.95 and x0.943 raw) while removing columns from the births and rows from D; production layout = legs transposed as one wide hub-row stack = one row-stack product. Our p*=0.05 gate removes rows; check that the birth columns and D rows are cut to match, and that the kappa4 level is restored.
3. Exact A/B identity sharing + deferred identity transport (DD_team 18250 B1a/B1b): exact, ~-13% of their bill; in our tiered chain probably 4-8% of B, zero raw loss. Cheap to test by counting duplicated transported matrices in the young tier.
Not recommended (verified dead): shorter K3 windows / dropping oldest sources (x1.17, DD_team x12), smaller bases (x1.11+), CP/low-rank re-fits per layer (no warm start), carried kappa4 core + scale extraction (net worse, C/B 0.30; and hurts memoryless chains), L8 Strassen.
Combined 1+2+3 plausibly 15-25% of B; 25% on products/layer needs all three to land.
