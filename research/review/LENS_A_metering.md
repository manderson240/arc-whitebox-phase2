# Lens A — rules, scoring and metering (adversarial review, 2026-10-09)

Brief: assume "our method family is at its floor; the leaders use an undisclosed cheaper
representation" is wrong or incomplete, and look for any LEGITIMATE way our util could be far
lower at the same accuracy. Read with fresh eyes: Rules v14, starter-kit docs, the whestbench
runner, the installed flopscope 0.12.1 source (grader: 0.12.0 per staff, thread 18202), forum
staff rulings. Probes: one process, `ulimit -v 16000000`, `OMP_NUM_THREADS=8`, starter-kit venv.
No participant code opened; no submission; nothing deleted.

## 0. Verdict in one paragraph

There is **no categorical metering lever**. Every arithmetic op bills weight 1 per FLOP (matmul at
the textbook `2mkn − mn`), every narrower-than-32-bit dtype bills exactly like float32, data
movement that writes bills ≥ 1/element, and the only discounts the model grants (views free,
provably-symmetric outputs at the unique-orbit count) are small for our op mix and partly already
taken. The measured bill of v57_azs (net 9000, local profile) is **5.1975e11 FLOPs = util 0.23635**,
of which **86.0 % is Strassen leaf `matmul`**, 4.8 % Strassen add/subtract, 2.0 % `concatenate`,
0.7 % `reshape`, 1.9 % `linalg.qr`, 1.8 % `linalg.eigh`, 1.7 % `einsum`, 0.9 % `multiply`
(everything else < 0.1 %). The metering-side opportunities below sum to roughly **util 0.236 → ~0.205**
(−13 % score), not to 0.10. The 2.35× gap to the floor is algorithmic (how many n³ products the
representation needs), so the team's conclusion stands — with one correction: the leaders' 0.102–0.107
is not suspicious, it is the natural resting point of a cost knob (see §2.6).

## 1. The scoring facts, checked against code

| Claim | Evidence |
|---|---|
| `s_m = MSE_final,m × max(0.1, C_m/B)`, averaged over MLPs; Phase 2 `C_m = F_m` (flopscope count only) | Rules v14 §5.5 (RULES_v14.txt, "Budget-adjusted leaderboard score"); `whestbench/src/whestbench/scoring.py:660-662` (`float(mse_final) * score_multiplier(...)`), `:673-690` docstring; `whest-starterkit/docs/concepts/scoring-model.md:97-115` |
| Only `predict()` runs inside a `BudgetContext`; `setup()` is off-budget (FLOPs and wall time), 5 s hard cap, re-run 5–15× per submission | `whestbench/src/whestbench/subprocess_worker.py:66-75` (BudgetContext opened around `estimator.predict` only) and `:207` (`estimator.setup(context)` outside); `scoring.py:709-722`; `docs/reference/estimator-contract.md:436-477` ("It is off the FLOP budget, and off the residual too") |
| flopscope ops called outside any BudgetContext still execute (billed to a global default, i.e. to nobody) | probe: `x + x` outside a context "ran, type FlopscopeArray"; `flopscope/src/flopscope/_validation.py:15-22` (`require_budget` falls back to `_get_global_default()`) |
| Data files (weights, lookup tables, precomputed artifacts) are permitted and `load` bills 0 | Rules §5.2 ("Data files remain permitted…"); `flopscope/docs/reference/cost-model.md` I/O table (`load` → `0`, "ingesting previously-computed values is not new compute") |
| A failed MLP (budget, 400 ms residual, 120 s wall, exception, non-finite) is zeroed with multiplier 1.0 | Rules §5.5 "Zero-prediction fallback"; `scoring.py:730-800`; `estimator-contract.md:551-559` |
| Weights reach `predict()` already float32 under the official subprocess runner | `subprocess_worker.py:21` (`fnp.array(fnp.asarray(w, dtype=fnp.float32))`, before the BudgetContext) — the forum "weights arrive float64" warning (18218) applies to the local path; our `w.astype(dt)` at `estimator.py:508` is a 2n² no-op-cost guard, fine |

## 2. Answers to the specific questions

### 2.1 Is `setup()` FLOP usage billed? — No. Is it a lever? — Not for us.
Unbilled (§1). But `setup()` receives no MLP (`SetupContext` = width/depth/budget/seed/dirs), so
anything computed there is MLP-independent and is therefore exactly equivalent to a shipped data
file — which the rules already allow without limit. The doc says "load, don't compute"
(scoring-model.md:13-15, estimator-contract.md:479-481); compute there is not a listed violation,
but it buys nothing a `.npz` doesn't, and the 5 s cap (×5–15 reruns) bounds it. **Our chain has no
MLP-independent heavy step** (every n³ product involves `W`), so this channel is worth ~0 for us.
Status: compliant but useless.

### 2.2 Are 100+ MB precomputed tables allowed and unbilled? — Yes, and we already use the channel.
Rules §5.2 permit "weights, lookup tables and precomputed artifacts"; `load` bills 0; no size limit
appears in Rules v14 or `docs/how-to/ship-weights.md` (network disabled, so everything must be in the
tarball, Rules §5.6). The Sponsor may "decline to treat a bundled file as data" if it is really a
program. Our `weights.npz` (2 KB) + `lc_weights.npz` (15 KB) are this. The question is what a big
table would REPLACE: a lookup replaces transcendental evaluation (16/element) with `take`
(4–5/element, probe: `take 1M` = 5,242,880), but our transcendental spend is **~2.5e6 FLOPs per
MLP** (`stats.norm.pdf/cdf` on n-vectors, 16 calls each) — 0.0005 % of the bill. Nothing to gain.
Status: compliant; no value for this chain.

### 2.3 Does any op class cost less per useful FLOP than matmul? — No.
Weight ladder is `{0, 1, 4, 16}` (`cost-model.md` "Weight-tier policy"; `data/default_weights.json`).
Arithmetic = 1 per op, FMA = 2 (`cost-model.md:79-86`); matmul bills `(2K−1)·M` (`:1126-1140`),
the minimum any multiply-add route can bill because `dot/inner/matmul/einsum` share one engine
("No substitution arbitrage", `:875`). Reductions bill `numel−1`. Anything that writes bills ≥ 1/elem;
`take/where/sort/choose` bill 4/elem; transcendental 16/elem; `norm.cdf` ≈ 96/elem, `norm.pdf` ≈
54/elem (probe). Views (`transpose/swapaxes/split/basic slice/broadcast_to`) are **free** (probe: 0);
**`reshape` is NOT free even when NumPy returns a view** — `numel` unconditionally
(`cost-model.md:191-215`; probe: `reshape (7,n,n)->(7n,n)` = 7,340,032). The only genuine discount
is symmetry: an aliased self-Gram `einsum('ik,jk->ij', W, W)` / `inner(W,W)` bills `(2K−1)·n(n+1)/2`
(probe: 1,074,265,600 vs 2,146,435,072) — **but the `W @ W.T` matmul spelling gets no discount**
(probe: full price); and elementwise/transcendental/`maximum`/`sum` on an `as_symmetric`-tagged
operand bill the unique-orbit count (~half; probe `Ssym*Ssym` 524,800 vs 1,048,576), lost as soon as
one operand is untagged (`Ssym*S` full). Rules §5.5 explicitly bless this ("symmetry-aware pricing …
is there to be used"). We already tag `cov` (`estimator.py:471, 818`) and use the aliased
self-Gram einsum (`:907`). Hazard found: `einsum('ji,jk,kl->il', W, Ssym, W)` (covariance transport
with a tagged S and aliased W) is priced at 3/4 (probe n=256 f64: 100,597,504 vs 133,955,584) but in
**float32 at n=1024 it RAISED `SymmetryError` (max deviation = inf)** — `_pointwise.py:515-537`
validates the result against the tag at `atol=1e-6, rtol=1e-5`, which f32 rounding of a 1024-term
sum fails; on the grader that is a zeroed MLP. Our `estimator.py:623` already works around exactly
this. Do not route n³ products through tagged einsums in f32.

### 2.4 Is there a dtype that bills cheaper? — No.
Rate table (`cost-model.md:314-340`, `default_weights.json → dtype_rates`): bool/int8/int16/int32/
float16/float32/complex64 = 1.0; int64/float64/complex128 = 2.0. Probe: f16, int8 and bool 1024³
matmul each bill 2,146,435,072, identical to f32. Packing values into wider lanes is prohibited by
Rules §5.5 ("Techniques of the first kind include packing…") and `allowed-code.md:302-326`.
Status: nothing legitimate here; f32 is already the floor.

### 2.5 Is util computed per MLP and averaged? — Yes, and it cannot help an analytic method.
`mean_m[ MSE_m × max(0.1, C_m/B) ]` (scoring-model.md:97-100; scoring.py:673-690). Our cost is
shape-determined and identical on every MLP (Mini-10 logs: util constant to 4 digits), so the
average equals the per-MLP value. By Jensen on the convex `max(0.1, ·)`, making cost vary across
MLPs at a fixed mean never lowers the mean multiplier. A "cheap path on easy nets" would only help
if it also lowered the MEAN cost, i.e. it is an algorithmic lever, not a metering one.

### 2.6 How do the leaders land at exactly 0.102–0.107? — It is a knob resting on the floor.
Any analytic method has one or more continuous cost knobs (rank, number of carried sources,
Strassen depth, Hermite order). Below 0.1 the multiplier is flat, so the rational operator turns
the knob UP (more accuracy) until util just exceeds 0.1, and turns it down if it overshoots. The
equilibrium is a cost a few % above 0.10 for everyone whose raw floor sits below the budget — that is
exactly J2W 0.1054, mk1981 0.1065, lode_dockx 0.1022, Luna 0.1175 (research/leaderboard/2026-10-05.csv).
No accounting trick is needed to explain the clustering; 504aldo's own forum ledger (thread 18218)
shows the public chain at 0.25B with the per-layer "units" that make the knob explicit. The
inference "exact floor ⇒ suspicious" is therefore not supported. What IS true: at our raw 2.25e-8,
reaching 0.10 would score 2.25e-9 (≈ rank 9–11 today) — every util point we drop is worth 0.43 %
of score, and the 13.6 points to the floor are worth 58 %. Cost, not raw MSE, is our lever, but it
is an algorithmic cost (n³ products per layer), see §3.

### 2.7 Strassen accounting
Strassen–Winograd written in flopscope ops is billed as what it declares (7 recursive products +
15 n²-adds per level) — confirmed allowed by the sponsor with no depth limit (FORUM_DIGEST.md,
"Strassen-Winograd … confirmed allowed", 2026-09-11 via 18218). Analytic ladder for one 1024-square
product (plain `2n³−n² = 2,146,435,072`), products at `(2·leaf³ − leaf²)·7^L`, adds `15·Σ 7^(l−1)(n/2^l)²`:

| depth L | leaf | total | ratio to plain |
|---|---|---|---|
| 4 | 64 | 1,292,910,592 | 0.6024 |
| **5 (ours)** | 32 | 1,165,062,144 | **0.5428** |
| 6 | 16 | 1,079,010,304 | 0.5027 |
| 7 | 8 | 1,048,892,160 | **0.4887** (minimum) |
| 8 | 4 | 1,101,598,912 | 0.5132 |

Our measured add+subtract share (4.8 %) against matmul (86 %) matches the L=5 row (80.8M/1,084M = 7.5 %
incl. the plain-quadrant copies), so the kernel is billed as modelled.

## 3. Ranked opportunities (metering side)

Score impact is quoted as the change in util points (1 pt = 0.01 of budget = 4.2 % of our current score).

### #1 Strassen depth 5 → 7 on every batched site — up to −2.1 pt util (−9 % score)
- Mechanism: §2.7 ladder; 90.8 % of our bill (matmul + add/sub) is inside the kernel; 0.5428→0.4887
  is −10 % of that, −9.1 % of the bill ≈ util 0.236 → 0.215 (L=6: → 0.220).
- Evidence: probe table above; forum 18218 #6 (ngmitam) measured 5.42→5.23e-9 on the grader going
  STRASSEN_MIN 32→8 at identical raw, and "the grader bills less saving than a local run" (their L5→L7
  −0.9 pt on grader vs −2.9 % locally — attributed to their 1-cold/49-steady split; our billing is
  deterministic, so take the ladder, not their delta).
- Rule status: **compliant** (sponsor ruling above; faithful declaration of a real algorithm).
- Risks: memory — worker peak was 8120/8192 MiB on v57 (`estimator.py` docstring, G-RB52); operand
  stacks grow as `(7/4)^L·n²` floats per side (L5 67 MB, L6 118 MB, L7 205 MB) plus result/recomb
  buffers; ngmitam saw RSS 3.96→5.99 GB L5→L8. Residual time — ~17 python ops per extra level per
  site; grader residual already 0.29–0.36 s of 0.40 (PROGRESS.md Mini-10 rows); local profile today
  showed 0.508 s under load (1 failed MLP in the profile run for that reason).
- Cheap test: build L6 variant (leaf 16) of the kernel only; run net 0 in-process for util/ops/VmPeak
  (`eval_mem` harness used in G-RB22), then a Mini-10 under `--runner subprocess` for the 8 GB
  RLIMIT_AS and the residual bar. Accept only if VmPeak ≤ 7000 MiB and worst residual ≤ 0.36 s.
  f32 rounding of deeper Strassen also perturbs the `as_symmetric` tolerance at `:623` — keep the
  explicit symmetrisation.

### #2 Remove the 142 billed `reshape`s in the arena carving — −0.71 pt util (−3 % score)
- Mechanism: `estimator.py:148` and `:313` carve flat arenas with `b[a:b].reshape(shape)`; flopscope
  bills `reshape` at `numel` even when it is a view (`cost-model.md:191-215`, probe), 3.69e9 FLOPs/MLP.
  Basic slicing, `transpose`, `swapaxes`, `split`, `broadcast_to` are free (probe: 0).
- Fix options: (a) allocate each arena already 3-D as `(K_max, m, m)` per leaf size and carve with
  basic slices `b[:k, :m, :m]` (free, strided views; matmul accepts them, same bill) — keeps
  same-leaf-size aliasing, loses cross-level aliasing (memory: per-level arenas sum to ≈ 1.3× the
  largest; check against the 8 GB wall); (b) keep the flat arena but carve the views ONCE and keep
  them on the estimator instance across `predict()` calls (plumbing, not computation — scratch
  buffers only; the one `reshape` per view is then billed to the first MLP only). Option (b) is
  compliant in letter (no computation, no values reused) but is a cross-MLP persistence pattern the
  rules never discuss — **ask staff before shipping (b); ship (a) if memory allows.**
- Cheap test: count `reshape` calls and FLOPs in the by-op breakdown (`whest run --profile --json`,
  `results.per_mlp[0].breakdowns…operations.reshape`) → target 0.

### #3 Avoid the plain-quadrant `concatenate` copies in the Winograd operand stacks — up to −0.48 pt
- Mechanism: 2.03 % of the bill (1288 calls) is `concatenate` writing quadrants into the batched
  operand stacks; the 6 of 14 Winograd operands that are PLAIN quadrants (A11, A12, A22, B11, B21,
  B22) are copies that exist only to batch — pure movement billed 1/elem. Products M1 = A11·B11 and
  M2 = A12·B21 can be computed as ONE matmul on free views, `A[:h, :] @ B[:, :h]` (same FLOPs as
  M1+M2 at that level), eliminating 4 of the 6 copies (−1.35 % of bill) — but those two products then
  leave the batched recursion and need their own deeper Strassen calls, so op count rises.
- Rule status: compliant (views are the intended free tier; Rules §5.5 "genuinely reducing the
  computation … is the point").
- Cheap test: kernel-level A/B on one site at L5; measure FLOPs and op count; accept if ops stay
  within the residual bar. Expect a small net; do after #1/#2.

### #4 Replace the 18 `linalg.eigh` basis rotations (1.83 %) with a randomized range finder — ~−0.3 pt
- Mechanism: `eigh` bills `9n³` by the standard-algorithm rule (`cost-model.md:1303`), n=384 →
  5.1e8 each (`estimator.py:908, 936`). A sketch `qr(G @ Ω)` for the top 224 vectors bills
  ≈ 2·384²·232 + qr(384, 232) ≈ 2.2e8 — less than half — and `linalg.qr` with `mode='r'` bills half
  of `reduced` when Q is not needed (`cost-model.md:1270-1271`). `qr` is 1.88 % (76 calls).
- Rule status: compliant (algorithm change). Needs an accuracy gate (f64 oracle, nets 0/2/4) — this is
  the same object whose rank law was tuned in G-RB12.

### #5 Symmetric tagging through the n×n closure — < 0.3 pt; not worth the hazard
- Elementwise ops on tagged operands bill ~half (probe), but our n×n elementwise spend is tiny
  (`multiply` 0.87 % total, much of it inside Strassen recombination on non-symmetric blocks) and
  the tag dies on the first mixed operand. The f32 validation raise (§2.3) is a live zeroing hazard.
  Skip.

### Not opportunities (closed)
- Cheaper dtype (§2.4): none. Setup-time compute (§2.1): nothing MLP-independent to move.
  Lookup tables for transcendentals (§2.2): 0.0005 % of bill. Per-MLP averaging (§2.5): Jensen.
  `out=` buffers: never reduce a bill, only widen the rate (`cost-model.md` "Which dtype prices a call";
  einsum `out=` even adds a `copyto` charge, `_einsum.py:908-960`). Nested/own `BudgetContext`,
  `budget_reset()` (thread 18238, unanswered), any client-side interference: prohibited (Rules §5.2 last
  bullet). Batched matmul: billed per product, no discount (forum 18184; probe `(7,n,n)@(7,n,n)` =
  7 × plain). `W @ W.T` vs aliased einsum: we already use the einsum form (`:907`); the `Gm = R_ @
  ((FPA0 @ FPA0.T) @ R_.T)` at `:935` is a Gram in matmul form — switching `FPA0 @ FPA0.T` to
  `fnp.einsum('ik,jk->ij', FPA0, FPA0)` halves that one product (FPA0 is 384×n → ~1.5e8 saved, noise).

## 4. Rule-exposure notes for the pending flopscope re-release
Staff (thread 18118 #6, 2026-10-04): "release a new version of flopscope, re-evaluate all the
affected submissions", then open Phase-2 selection one week before the deadline; billing issues
#264–#278 on GitHub were not individually named and the public issue search returned 0 results
for that range. Our bill is 98.5 % `matmul/add/subtract/concatenate/reshape/qr/eigh/einsum` at
textbook prices with no symmetry claim on the n³ path — low exposure. The one priced discount we use
(aliased self-Gram einsum, 2 calls, `:907`) is documented intent (`cost-model.md:1152-1158`). If a
re-bill changes `reshape`/`concatenate` (the "every byte written is metered" family is the youngest
part of the model), #2/#3 become moot but nothing we ship is at risk.

## 5. Measurement record
- `whest run --estimator submissions/v57_azs/estimator.py --runner local --n-mlps 1 --n-samples 2000
  --seed 9000 --profile --format json --max-threads 8` (whestbench 0.16.1 / flopscope 0.12.1+np2.2.6):
  flops_used 519,747,002,148 (util 0.236354); backend 47.1 s, overhead 4.0 s, residual 0.508 s
  (over the 0.4 cap locally under load → the MLP was zeroed in that run; the FLOP count is unaffected).
  By-op shares as in §0. Note the local profile's raw MSE is meaningless (2000-sample truth).
- Pricing probes: `$TMPDIR/probe_sym2.py` (symmetry/aliasing/dtype/movement), results quoted inline.
