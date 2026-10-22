# G-RB146 LEVER SCAN -- fast-matmul schemes beyond Strassen-Winograd + contraction order (read-only; 2026-10-20T19:15Z)

Base: `submissions/v112_sb` (#337384, pred 4.04e-9, being graded). Nothing built, nothing submitted, no file under `submissions/` or the
ledger touched. Pricing follows G-RB137/G-RB139 (wall knapsack): util saved per predicted grader-max second, grader max = 89.4 x (1 + 1.32 (r - 1)),
r = remote wall / v105's 49.40 s per predict (rb142). Every number below is from a file in this folder or a cited source; estimates are marked [H].

## 0. Instrument and controls

- `opledger146.py` dumped the full flopscope op ledger of v112_sb on net 0 (in-process, f32, same predict path as `fingerprint.py`):
  `ledger_v112_sb.jsonl`, 14,395 ops, **18.9772 pt** -- identical to the G-RB145 fingerprint (14395 / 18.9772), so the instrument reproduces the known answer.
  Run under `timing_lock.sh` SHARED via `bg.sh` (label g146-opledger, 19:07:01Z, load 9.08), ~50 s.
- Billing read from the starter-kit flopscope 0.12.1 (`_flops.py`, `data/default_weights.json`, `_array_ops.py`): matmul `2mkn - mn`; einsum
  `(k-1)*prod(M) + prod(alpha)` per pairwise step; **add / subtract / multiply / stack / concatenate / reshape bill 1 per element** (weight 1.0);
  **transpose / swapaxes / moveaxis bill 0**. So a lower-rank scheme with more additions can LOSE, and every operand slab that is not a pure view is billed.
- Glue-model control (`price146.py`): the per-level Strassen-Winograd model (7 ops per operand side incl. the 3 plain-quadrant copies, 5-add nested
  recombination) summed over every site and depth gives **1.7615 pt vs the ledger's 1.7485 pt** of add+subtract+stack (0.7 %). The scheme pricing below
  rests on that model.
- Wall constants (measured, remote mode): add/subtract sweeps 33.5 s per 4 predicts for +5.8e9 elements/predict (G-RB137 attribution, strided 10-20M-element
  d6 views) = **1.44 ns/element**; large contiguous top-level slabs are faster -- bracket 0.7 ns/element [H]. v112 matmul: 6.35 s/predict for 3.458e11 billed =
  54.5 GFLOP/s effective (`analyze.out`, rb142 rows). v112's remote backend is 43.9 s/predict: add 11.1 + subtract 14.9 + stack 2.9 + concatenate 2.2 = 71 %
  memory sweeps, matmul 6.4 s = 14 %.

## 1. Site inventory (matmul, net 0, v112_sb; `analyze.out` A)

| site | leaf shape (c, m, k, w) x lead | depth | matmul pt | share |
|---|---|---|---|---|
| C merged contraction | (1, 16, 32..170, 16) x 7^6 (qa split 4+3) | 5 + fused d6 | 5.4648 | 34.8 % |
| T young+old transport | (1, 192..275, 24..32, 32) x 7^5 | 5 | 4.4165 | 28.1 % |
| T2 | (1, 64, 32, 32) x 7^5 (+ one 128-row call) | 5 | 1.2820 (+0.1972) | 9.4 % |
| F0 / K0 (224 group) | (6..8, 32, 7, 64) / (32, 64, 7) x 7^5 | 4 + d6 | 0.7325 / 0.6088 | 8.5 % |
| F1 / K1 (384 group) | (2, 32, 12, 64) / (2, 32, 64, 12) x 7^5 | 5 | 0.6840 / 0.6336 | 8.4 % |
| M2 | (3, 16, 32, 16) x 7^5 | 5 | 0.5547 | 3.5 % |
| E2 / E1 (entry) | (1, 24, 64, 128) x 7^4 / (1, 128, 128, 48) x 7^3 | 4 / 3 | 0.4260 / 0.0489 | 3.0 % |
| dense 2-D (56 shapes, 503 calls) | e.g. (224, 384) @ (384, 2048) x 8 = 0.128 pt | 0 | 0.6121 | 3.9 % |
| total matmul | | | **15.7255** | |

Glue: subtract 0.7592, add 0.6578, stack 0.3315, reshape 0.1895, concatenate 0.0442 pt; linalg.solve 0.6609 (the G-RB143 shared-basis Gram solves, f64 billed x2).

## 2. Part A -- fast bilinear schemes at these shapes

### 2.1 What can beat Strassen-Winograd here at all (exponent + divisibility screen)

Every dimension that Strassen halves is a multiple of 32 (1024, 2048, 384, 224 = 7 x 32, K rounded to 32/64, T rows a multiple of 32), so the only
exact alternative is a scheme <p,q,r>:R applied in place of one or more Winograd levels. Compared at EQUAL volume reduction pqr, Winograd gives
(7/8)^(log2(pqr)/3) products; a scheme wins on multiplications only if R/(pqr) is below that:

| scheme (rank) | source | R/(pqr) | Winograd at the same volume | mult verdict | shape fit at our sites |
|---|---|---|---|---|---|
| <2,2,2>:7 Strassen-Winograd | shipped | 0.875 | 0.875 | = (7 is optimal, Hopcroft-Kerr 1971; 15 adds optimal, Probert 1976) | all |
| <2,2,3>:11, <2,3,3>:15, <2,3,4>:20, <2,4,4>:26 | Hopcroft-Kerr 1971 (fmm.univ-lille.fr) | 0.917 / 0.833 / 0.833 / 0.813 | 0.875 / 0.766^(..) -> 0.80 / 0.75 / 0.75 | LOSE | no dim divisible by 3 except 384, 10880 |
| <3,3,3>:23 Laderman | catalogue | 0.852 (exp 2.854) | 2 levels = 0.766 for volume 64 vs 27 -> 0.843 | LOSE | n = 1024 not divisible by 3 |
| <2,4,8>:51 | AlphaEvolve 2025 (catalogue) | 0.797 | 0.766 (two levels, volume 64) | LOSE | -- |
| <5,5,5>:93, <6,6,6>:153 | Moosbauer-Poole 2025, arXiv 2502.04514 (over Z) | 0.744 / 0.708 | 0.725 / 0.681 | LOSE (exp 2.816 / 2.808 > 2.807) | not divisible |
| <4,4,5>:61, <3,4,5>:47, <4,5,5>:76 (AlphaTensor/AlphaEvolve standard arithmetic) | catalogue; Fawzi 2022 (76 confirmed in text) | 0.763 / 0.783 / 0.76 | 0.7366 / 0.74 / 0.73 | LOSE | not divisible |
| **<4,4,4>:48** | AlphaEvolve 2025 (complex); rational point: Dumas-Pernet-Sedoglavic 2025, arXiv 2506.13242 (v7) | **0.750** | 0.766 (Winograd^2 = 49) | **WIN by 1/49 = 2.04 %** | every site (all dims multiples of 32) |

AlphaTensor's own standard-arithmetic 4x4 rank stayed at 49 (the 47 is Z2 only; its README has no rank table; the Nature Fig. 3 table is a raster image --
per-size numbers UNKNOWN from text, only (4,5,5) 80 -> 76 is stated in prose). Kauers-Moosbauer flip graphs: (4,4,4) 49 over any field, 47 only in char 2;
(4,4,5) 62, (5,5,5) 97 (Z) -- all superseded by the catalogue rows above and none beats Winograd per volume. **Conclusion: the ONLY candidate is the
rationalised AlphaEvolve <4x4x4:48>; everything else loses on multiplications before additions are even counted.**

### 2.2 The <4x4x4:48> scheme priced under flopscope billing (`price146.py`, `price.out`)

Facts (arXiv 2506.13242 v7, Sections 4-7): 48 products; A-side and B-side linear forms use only +/-1; C-side needs 2, 1/2, 1/4, 1/8 (dyadic, exact in binary
floating point; valid over any ring with 1/2). Optimised straight-line programs: **104 additions + 4 shifts (A side), 75 + 1 (B side), 110 + 21 (C side) =
289 additions + 26 power-of-two scalings** (naive 1216). Alternative-basis variant: 1+2+3 additions per application but a 312-op change of basis -- for a
single application at a site it is the same cost (used only if the scheme recursed several levels, which it would not here). No stability analysis in the
paper; a "more accurate" variant exists (arXiv 2603.18699, not fetched).

Replacing the TOP TWO Winograd levels of a site (49 -> 48 products of identical leaf shape, the remaining d-2 Winograd levels unchanged):

| site | d_mm pt (-1/49) | d_glue pt (289 adds + 26 scalings + 48 operand copies) | d_glue pt (operands as pure views) | d_util pt | d_util pt (views) | d_wall s/predict [1.44 .. 0.7 ns/el] | pred. grader-max delta s | **E pt per max-s** |
|---|---|---|---|---|---|---|---|---|
| **C** | -0.1115 | +0.0571 | +0.0213 | **-0.0544** | -0.0902 | +1.76 .. +0.83 | +4.2 .. +2.0 | **0.0129 .. 0.027** |
| **T** | -0.0901 | +0.0471 | +0.0326 | **-0.0431** | -0.0575 | +1.45 .. +0.69 | +3.5 .. +1.6 | **0.0124 .. 0.026** |
| T2 (+T2x) | -0.0302 | +0.0159 | +0.0096 | -0.0143 | -0.0206 | +0.49 .. +0.23 | +1.2 .. +0.55 | 0.012 .. 0.026 |
| F1 / K1 / M2 / E2 / E1 | -0.0140 / -0.0129 / -0.0113 / -0.0087 / -0.0010 | +0.0127 / +0.0130 / +0.0117 / +0.0064 / +0.0008 | | -0.0012 / +0.0001 / +0.0004 / -0.0023 / -0.0002 | | +0.4 / +0.4 / +0.4 / +0.2 / +0.03 | | ~0 (below grader resolution, kit rule 7) |
| F0 / K0 | -0.0149 / -0.0124 | +0.0213 / +0.0195 | +0.0179 / +0.0098 | **+0.0064 / +0.0071 (WORSE)** | | +0.67 / +0.61 | | negative |
| all sites | -0.3071 | +0.2055 | | -0.1016 | -0.1913 | +6.4 .. +3.0 | +15.3 .. +7.3 | 0.0067 |

Reading: on the three large sites the scheme is util-POSITIVE after billing its additions (the operand copies are the swing: 48 slabs per side vs Winograd's
3 plain quadrants per side per level; if the 48 left/right operands can be written straight into pre-bound stack buffers they are still billed as adds,
"views" here means the aA/aB programs write their outputs in place with no extra copy). On the small-leaf sites (F/K 224/384 groups, M2, E) it is neutral or
worse: the saved product is small and the 289 block adds are not.

Comparison with the measured level-6 levers (G-RB139 table re-mapped with Amendment 1): T2 0.0124 pt/s, F0 0.0113, K0 0.0169, F0+K0 0.0136; T (G-RB145
fingerprint -0.3006 pt for ~+24 s max, G-RB134) ~0.0125. **The 4x4:48 on C or T sits in the same exchange-rate class at the pessimistic wall rate and
about 2x better at the optimistic rate -- it does NOT clearly dominate the shipped level-6 levers, and it adds 2.0-4.2 s of predicted max per site.**
v112's predicted max is 87.9 s (rb142), so C alone or C+T fits the 100 s rule only if G-RB145's T/T2 level is not also taken (T2 alone -> ~96 s; T -> ~112 s
out; C(4x4) + T2(d6) -> ~98-100 s on paper, additivity unverified).

Also screened and dropped:
- **Alternative-basis Winograd (Karstadt-Schwartz 2017: 12 adds/level instead of 15 + three O(n^2 log n) basis changes).** At depth 5 the finite count is a
  wash: Winograd glue 5 n^2 ((7/4)^5 - 1) = 77 n^2 vs 12/15 of that + ~3 L n^2 = 61.6 + 15 = 76.6 n^2 [H]; the basis-change sweeps are wall. Not a lever at
  L <= 6.
- **One Winograd level on the dense 2-D products** (largest: (224,384)@(384,2048) x 8 = 0.128 pt): -0.016 pt mults, +0.002 pt adds -> -0.014 pt (0.07 %),
  below the grader's resolution (kit rule 7).
- **Flip-graph / AlphaTensor rectangular schemes at the leaf** (e.g. <3,4,7>:63 for K0's (32,7,64) leaves): the leaf products are what the fused d6 level
  already feeds to BLAS; a rank-R leaf scheme would replace ONE batched matmul call by R smaller calls plus block adds -- G-RB137 showed per-call dispatch and
  sweeps, not FLOPs, set the wall at this size. Not priced further; UNKNOWN whether any is util-positive, wall-negative by construction.

### 2.3 Numerical-stability risk of <4x4x4:48> vs the shipped Winograd levels

- Shipped: two extra Winograd levels (d6) pass the f64 final-layer identity bar at ~2e-15 (G-RB139 bars: 2.01e-15 / 1.91e-15), f32 predict unchanged in grade.
- 4x4:48: coefficients up to 2 and down to 1/8 on the C side (304 of 320 non-zero P entries are not +/-1, per the paper's LRP counts); the growth factor of the
  C-side linear forms is therefore larger than Winograd's (Winograd per-level stability constant is already the worst of the 7-product family, Ballard et al.
  2016). The authors wrote a separate "more accurate" variant (arXiv 2603.18699), which is evidence the plain rational scheme has a measurably worse error
  constant. Expected f64 identity vs v112: 1e-14 .. 1e-12 [H] -- the strict 1e-12 identity bar used for exact Winograd levels may FAIL even though the
  scheme is exact; the G-RB34b 2 % f64 precedent bar is the right one. f32 effect on the graded raw: UNKNOWN until the f64/f32 twin runs; risk MEDIUM.

## 3. Part B -- contraction order (opt_einsum 3.4.0 'optimal' and 'dp' vs the shipped path; `analyze.out` C)

flopscope's `fnp.einsum` path-optimises with its vendored opt_einsum (`_einsum.py`: default `optimize="auto"` -> exhaustive 'optimal' for k < 8 operands,
greedy downgrade only at k >= `_LARGE_K_THRESHOLD = 8`) and bills each pairwise step by its accumulation cost. Every multi-operand chain in v112_sb has k = 3:

| chain (shapes) | calls | shipped billed / call | cheapest of the 3 pairwise orders (flopscope billing) | optimal / dp path | saving |
|---|---|---|---|---|---|
| `ki,kij,kj->ij` ((5,1024),(5,1024,1024),(5,1024)) | 75 | 0.00067 pt | 0.00067 (all three orders equal) | [(1,2),(0,1)] | **0** |
| `ab,aij,bij->ij` ((3,3),(3,n,n),(3,n,n)) | 14 | 0.00095 | 0.00095 | [(0,1),(0,1)] | 0 |
| `ab,ai,bj->ij`, `ab,ai,bij->ij`, `ab,aij,bi->ij` (3x3 lambda) | 14 each | 0.00024 | 0.00024 | optimal | 0 |
| `ab,ai,bi->i` | 15 | ~0 | ~0 | | 0 |

The explicit matmul chains in `predict` (`w2.T @ T` then `(...) @ w`; `wT @ (cov @ w)` on M1/M2; `P0 @ (P0.T @ Om2)`; `(V2.T @ R_) @ FPA0`) are already
associated small-side-first. **Nothing beats the shipped contraction orders; the total einsum bill is 0.2893 pt and no order change moves it.** The
2-operand self-Grams (`ki,kj->ij`) are already billed 0.5x by the meter's identity-pattern rule (G-RB138 premise note).

## 4. Shortlist (ranked by util saved per predicted grader-max second) and draft pre-registered gates

Honest headline: **no scheme beats the shipped Strassen-Winograd levels by a margin that clears the knapsack on its own.** One candidate exists, and it
competes with -- rather than dominates -- the level-6 levers already in G-RB145. Nothing in Part B.

1. **<4x4x4:48> (Dumas-Pernet-Sedoglavic 2025) on the top two levels of site C.** d_util -0.054 pt (-0.090 if the 48 operand slabs are in-place
   writes), predicted max +2.0 .. +4.2 s, E 0.013 .. 0.027 pt/s. Stability MEDIUM. Build cost: a 48-term bilinear kernel over the existing arena/qa/nested
   machinery of the C site -- the hardest site to touch (d5 + fused d6 + nested up views), not a 2-3 h port [H]; freeze is 2026-10-21 06:00Z.
2. **Same scheme on site T.** d_util -0.043 (-0.058), +1.6 .. +3.5 s max, E 0.012 .. 0.026. T's rows vary per layer (colnest, 6-add recombination) and
   its inner dim K is rounded to 64 (divisible by 4 at the top level); the 32-row zero pad of G-RB145 already handles the 224 block.
3. **Same scheme on T2.** d_util -0.014 (-0.021), +0.6 .. +1.2 s, E ~0.012 .. 0.026; smallest and simplest site (fixed shapes, nested), the natural
   FIRST port if the kernel is built at all -- but by itself below the grader's resolution (0.07 %).
   All other sites: neutral or negative (F0/K0 lose 0.006-0.007 pt).

Draft gate (G-RB147, if the orchestrator opens it; stricter only):
- Pre-work bar (before any build): transcribe the 48 terms from arXiv 2506.13242 eqs 35-82 (public paper, no participant code) into a standalone f64
  numpy check `research/rb147/dps48_check.py`; it must reproduce `A @ B` for random 4x4 blocks of 256x256 to 1e-13 rel and FAIL a mutant with one sign
  flipped (kit rule 6). Also a Winograd^2-identity control on the same blocks.
- Bars for the port (v114_q4, T2 first, then C): (a) f64 final-layer rel dev vs v112_sb <= 2 % (G-RB34b precedent) on nets 0 and 2 -- and record the actual
  identity figure, expected 1e-14..1e-12 [H]; (b) metered util (fingerprint, net 0): T2 <= 18.9772 - 0.010; C <= 18.9772 - 0.045 (the "copies" row; the
  "views" figure is the target, the copies figure the bar); (c) ops: no bar (G-RB137: op count is not a wall proxy); (d) remote_check PASS, nets 0, 2
  (dyadic coefficients must survive the ZMQ backend -- the negative-step-view class of G-RB118 failure is the risk); (e) calibrated remote wall vs v105_sw,
  2 nets x 2 repeats, exclusive lock, reversed order: r <= 1.0898 (predicted max <= 100 s) INCLUDING whatever G-RB145 level is adopted on the same build
  (additivity measured, not assumed); (f) slot_runner probe rule (VALID adj <= 0.995, Mini-10 adj <= 1.0, 0 failed, VmPeak <= 7900, eval_mem/archive PASS).
  Submission order: only after #337384 grades failed 0 / max <= 105 s and only if G-RB145's winner leaves >= 4 s of predicted headroom. Nominate iff graded <
  min(4.21e-9, v112's grade), failed 0, max <= 105 s. Kill: dps48_check not passing by 2026-10-20 23:00Z; port bars not met by the 06:00Z freeze.
  Prediction: graded x (1 - 0.054/18.98) = -0.3 % (C) .. -0.5 % (C + T) [H] -- within the grader's resolution only in combination; P(ships before freeze) ~15 % [H].

## 5. UNKNOWN (not absent)

- The straight-line programs themselves (289 adds): in the PLinOpt repo (`github.com/jgdumas/plinopt`, data/4x4x4_48_rational_{L,R,P}.slp) -- NOT downloaded
  (file download needs the user's go-ahead); the equation forms 35-82 in the arXiv HTML suffice for a first transcription.
- The 4x4:48 scheme's floating-point error constants (arXiv 2603.18699 not fetched); the f32 effect on raw MSE.
- The per-element wall rate of large top-level slabs in remote mode (bracketed 0.7-1.44 ns/el from the d6 small-view measurement; the only way to know is the
  calibrated clock on a built T2 variant).
- AlphaTensor's full standard-arithmetic rank table (Nature Fig. 3 is a raster image; the repo README has no table; `factorizations_r.npz` not downloaded).
  Not load-bearing: the exponent screen in 2.1 rules out every rectangular shape on volume grounds regardless of the exact rank.
- Catalogue additive complexities: fmm.univ-lille.fr lists no addition counts for any format (confirmed by reading the table columns), so no catalogue
  scheme can be priced under flopscope billing without its explicit program; only the DPS 4x4 paper publishes one.

## 6. Lessons (<= 2, for KIT.md if adopted)

1. Under a meter that bills additions at full weight AND a wall budget dominated by memory sweeps, "fewer multiplications" is the wrong figure of merit: price a
   bilinear scheme by (products saved) - (billed adds + billed operand copies) and by sweep elements per saved FLOP. Here 48-vs-49 survives only on the three
   largest sites and only barely.
2. The exponent-at-equal-volume screen `R/(pqr) vs (7/8)^(log2(pqr)/3)` kills every rectangular catalogue entry in one line; do it before fetching any scheme.

Artifacts: `opledger146.py`, `ledger_v112_sb.jsonl`, `opledger.out`, `analyze146.py`, `analyze.out`, `price146.py`, `price.out` (all in research/rb146/).

## 7. References

Load-bearing (read for this scan): Dumas, Pernet, Sedoglavic 2025, arXiv:2506.13242 v7 (48-term scheme, add counts, coefficient ring); Moosbauer & Poole
2025, arXiv:2502.04514 (5x5:93, 6x6:153 over Z; no add counts); Kauers & Moosbauer 2022, arXiv:2212.01175 (4x4 = 49 over any field, 47 only in char 2);
Fawzi et al. 2022, Nature 610 (4x4 standard arithmetic stays 49; (4,5,5) 80 -> 76 stated in text; Fig. 3 table is an image, not read); fmm.univ-lille.fr
(ranks only, no additive complexity, no field markers); flopscope 0.12.1 sources in whest-starterkit/.venv (billing); G-RB137/139/144/145 (wall clock,
mapping, exchange rates). Stability statements: Higham, Accuracy and Stability of Numerical Algorithms, 2nd ed., ch. 23 (Strassen/Winograd error growth
per level) and Ballard, Benson, Druinsky, Lipshitz, Schwartz 2016 (SIAM J. Matrix Anal. Appl., stability factors of fast schemes) -- cited from memory,
section numbers not re-verified here [H]. Supplied by the coordinator (metadata only, sections NOT verified in this scan; use as pointers, not as
evidence): Knuth, TAOCP Vol. 2 §4.6.4 (bilinear-algorithm multiplication-count bounds -- the 7-is-optimal / 15-adds-optimal facts above are the
Hopcroft-Kerr / Probert results it surveys); Hogben, Handbook of Linear Algebra 2nd ed. (fast matmul and stability chapters); Robey & Zamora, Parallel and
High Performance Computing (roofline model -- the right frame for the 1.44 ns/element sweep rate: the add/subtract sweeps are bandwidth-bound, so a
roofline fit on the rb137/rb142 per-class walls would tighten the 0.7-1.44 ns bracket); Halko, Martinsson, Tropp 2011 (range finder in `_rank_rf`, not
touched by this scan). Full list: vault references/20261020-oreilly-references-arcwb.md.
