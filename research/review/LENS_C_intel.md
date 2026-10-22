# Lens C — competitive intelligence on the Phase-2 leaders (public metadata and prose only)

- **Date:** 2026-10-09 (UTC). Phase 2 closes 2026-10-17.
- **Premise under attack:** "the leaders' method is undisclosed and unknowable". Verdict: the *content* of the top three
  methods is still undisclosed, but the public submission feed makes their **shape, cost class, pace and the dates of
  their new ideas** knowable, and three of the eleven leaders (mliston, marius_binner, AndreasHad04) have left enough
  prose to name their family. "Unknowable" is wrong; "undisclosed" is right.
- **Sources (clean-room):**
  - AIcrowd public GraphQL feed (`POST https://www.aicrowd.com/graphql`, `challenge.submissionsPage(filter:{participantName})`,
    no login). Fields used: `id, createdAt, status, score (adjusted), scoreSecondary (raw MSE), participant{name,affiliation}, team, round`.
    `utilization := adjusted / raw` (exact when util ≥ 0.1; values printed as 0.100 mean "at or below the floor").
    **The `gradingMessage` field was NOT read** (that is the error-text channel of forum 18217). No submission page, code,
    archive or detail page was opened. Phase 2 exposes **no submission titles or descriptions** — question 2 of the brief
    has a definite answer: there are none to mine.
  - Forum prose via the Discourse JSON endpoints with `<pre>/<code>` stripped: 18218 #2–#6, 18240, 18238, 18237, 18145, 18118 #5–6, 18197 #3–4, 18166.
  - marius_binner's Phase-1 write-up PDF (forum 18166, team name then "skibidi toilet"), prose only, code-shaped lines dropped.
  - GitHub REST profile metadata for the one leader whose AIcrowd profile links one (`masterkoala`, Luna): repo names and
    descriptions only, no file opened.
  - ARC: LessWrong announcement comments; alignment.org blog index + two posts.
  - Local: `research/leaderboard/*.csv` (new snapshot `2026-10-09.csv` written by `leaderboard_snapshot.py`), PRIOR_ROUNDS.md, FORUM_DIGEST.md.
  - Raw data saved beside this file: `LENS_C_timelines.txt` (daily best per leader, all rounds) and `LENS_C_leader_entries.json` (id/time/adj/raw of every graded Phase-2 entry per leader).
- **Instrument failures (Phase 0):** general web search is **UNKNOWN, not absent**. DuckDuckGo HTML returned a bot page,
  Bing returned a results page with zero links for the control query "ARC white-box estimation challenge", Mojeek 403.
  So "no blog/paper by X" below means *not found on the forum, AIcrowd, GitHub profile or ARC pages*, nothing more.
- Tags: **[measured]** = from the feed or a page we fetched; **[author]** = the participant's own prose; **[inference]** = ours.

## 0. Headline findings

1. **The leaderboard page lags the feed.** The board (and our 10-09 snapshot) shows J2W at 1.5e-9 / raw 1.47e-8; the feed has
   J2W graded at **1.454e-9 / raw 1.36e-8 / util 0.106** (ids 334924, 334988, 335019, Oct 8–9), Luna at 1.587e-9 / 1.364e-8,
   marius at 1.588e-9 / 1.167e-8, oliver_chen at 1.65e-9 / 1.23e-8 [measured]. Treat the board as ≥1 day stale.
2. **Two ways to reach the front, and the feed tells them apart.** Smooth slopes with ~3–7 %/day adjusted gains are *cost
   trimming* (every leader did this Sep 1–20: util 0.4–0.97 → 0.10–0.15 with raw nearly flat). Raw steps of 10–30 % at
   constant util are *new content*; there are exactly five of those among the leaders in the last three weeks (§2).
3. **A board-wide raw-improvement wave on Sep 28 – Oct 3** [measured]: marius −18 % (Sep 29–30), shiv_m −18 % (Sep 30),
   mliston −17 % (Oct 2), williawa −10 % (Oct 1–3), AndreasHad04 −8 %, J2W −6 % (Sep 28), lode −7 %, and two newcomers
   (mk1981, oliver_chen) first graded on Oct 2. Control: suliman_tadros's raw was flat at 1.57–1.58e-8 from Sep 24 to Oct 6,
   so this is not a grader-side reference change. The only public event in the window is the Sep 22 κ4-law exchange
   (18218 #4–#5): 504aldo stated the **pre-activation** law `G_off = λ_l·C_pre_off` has R² ≥ 0.95 from layer 3 and gave the
   ladder *no κ4 feed 4.20e-8 → scalar λ 2.23e-8 → dense κ4 channel 2.04e-8*. A one-week implementation lag fits every
   step in the wave [inference, unverified].
4. **Probe-then-compress is the leaders' working method.** J2W (Sep 14–22) and marius (Sep 26) each graded a ~0.93-util
   variant 8 % more accurate than their shipped one, then landed that accuracy at 0.11–0.15 util within 3–14 days (§2.1, §2.3).
   J2W's Sep 14 ladder — util 0.43 / 0.61 / 0.82 / 0.97 → raw 1.76 / 1.68 / 1.57 / 1.54e-8 — is a **size knob with diminishing
   returns: 7× cost buys 18 % raw** [measured]. Three weeks later their 0.107-util entry (1.36e-8) beat that full-budget probe,
   so what moved them was new content, not width.
5. **Cost class:** top-15 util 0.102–0.159, median 0.135 → 13–20 n³-units per layer. Across teams raw and util are
   uncorrelated (top-25: r = −0.11), i.e. spending does not buy accuracy *between* methods; the three floor-huggers
   (lode 0.102, J2W 0.105, mk1981 0.107) span raw 1.36–2.0e-8 while the spenders (marius 0.144, shiv 0.145) span 1.14–1.55e-8 (§4).
6. **The "new names" are explained.** mohanty ruled on Oct 5 (18240) that building on 504aldo's MIT code is prize-eligible
   with credit and "substantial changes". The 1.96e-8 / 0.20 cluster (multi_agent, Nanoloom, Hydrion-Labs, mainguyenanhvu…,
   dozens of identical-raw entries on Oct 9) is that code; shiv_m's Sep 12 step (3.59→2.11e-8, two days after release) and
   mk1981's Oct 2 arrival (2.23e-8 → 1.85e-8 next day) have the port signature [inference]. oliver_chen (1.44e-8 on arrival) does not.
7. **No staff post describes what the Phase-2 top methods share.** ARC's only such statement is the warm-up one on LessWrong
   ("variants on the factorized 3rd cumulant propagation algorithm … combined with learned networks that consume the
   cumulant estimates as features"). Phase-1 results/prizes are still unannounced (overview page, ARC blog index, forum —
   all fetched fine, none mention them: UNKNOWN). Staff will ship a new flopscope, **re-bill affected submissions**, then open
   selection ≥ 1 week before the deadline (18118 #6, Oct 4).

## 1. Who the leaders are (metadata only)

| team / participant | affiliation (AIcrowd) | prior rounds | public prose | P2 entries (graded) |
|---|---|---|---|---|
| J2W / joe_wanza | Numascale AS | P1 #2 (raw 2.78e-7 @ 0.19; 540 graded; util modes 0.4/1.0/0.5/0.1) | none found | 315 (10/day since Aug 28; 1,532 across rounds) |
| Luna / dogus_ozel | Independent; GitHub `masterkoala` (Mac LLM tooling, video utilities — a software engineer's repos, nothing on this problem) | none | none found | 39 |
| marius_binner | University of Bergen | warm-up #4 (0.107 util), P1 #8 as "skibidi toilet" | **P1 PDF** (18166): Kerdock/MUB cubature; process posts | 209 |
| mliston | — ; LinkedIn matthewrliston | warm-up #20, P1 #9 | **P1 PDF** (18170): analytic anchor + GRU | 66 (last Oct 2) |
| oliver_chen | — | none | none | 45 (Oct 2–8) |
| mk1981 | — | none | none | 70 (Oct 2–9) |
| suliman_tadros | — | P1 #79 (sampler, 0.57 util) | none | 106 (last Oct 6) |
| thegamers / williawa | MATS | P1 #42 | one metering bug report (18082) | 117 |
| AndreasHad04 | — | none | 18218 #4 (κ4 (2,2)-slice regression, "cap 3776"), 18118 #5 | 163 |
| shiv_m | Independent | warm-up #3, P1 ~#45 | none | 189 |
| lode_dockx | KU Leuven | P1 #53 | none | 164 |

## 2. Timelines — when each leader's score moved and by how much [measured]

Daily best adjusted; util = adjusted/raw; "step" = ≥10 % raw drop at roughly constant util (new content) vs "slope" = util
drop at flat raw (cost work). Full daily tables in `LENS_C_timelines.txt`.

### 2.1 J2W (joe_wanza) — #1
| date | adj | raw | util | reading |
|---|---|---|---|---|
| Aug 28 | 2.0e-8 | 2.96e-8 | 0.676 | first analytic chain, day 5 of Phase 2 |
| Aug 29 → Sep 13 | 6.7e-9 → 2.7e-9 | 2.35 → 1.91e-8 | 0.285 → 0.142 | **slope**: 12 days of cost trimming, raw −19 % |
| Sep 4 | 3.9e-9 | 1.99e-8 | 0.195 | raw −8 % at flat util (small step) |
| Sep 14–15 | — | 1.76/1.68/1.57/1.54e-8 | 0.43/0.61/0.82/0.97 | **budget ladder** of one knob: 7× cost → −18 % raw |
| Sep 17 | 2.22e-9 | 1.65e-8 | 0.135 | **step −12 % raw** at flat util (new content #1) |
| Sep 21–22 | — | 1.47–1.51e-8 | 0.93–0.94 | second full-budget probe, 8 % below shipped |
| Sep 26 | 1.79e-9 | 1.62e-8 | 0.110 | cost step: util 0.126 → 0.110 at flat raw |
| Sep 28 | 1.68e-9 | 1.53e-8 | 0.110 | step −6 % raw (new content #2) |
| Oct 6 | 1.47e-9 | 1.38e-8 | 0.107 | step −5 % raw (new content #3) |
| Oct 9 | **1.45e-9** | **1.36e-8** | 0.106 | current best; 6–7 entries/day continue |
Also ~1 in 8 J2W entries grades at 0.011–0.04 (zeroed MLPs: budget/residual cliff) — they explore right at the cap.

### 2.2 Luna (dogus_ozel) — #2/3
| Sep 23 | 2.97e-9 | 1.76e-8 | 0.168 | first entry already 17 % better raw than the 504aldo cluster |
| Sep 24–27 | → 1.91e-9 | → 1.42e-8 | → 0.134 | **smooth −12 %/day**, both raw and util: tuning a finished method |
| Oct 3 | 1.68e-9 | 1.41e-8 | 0.119 | cost step only |
| Oct 9 | **1.59e-9** | **1.36e-8** | 0.116 | 39 entries total — the most score per submission on the board |
Reading: developed offline for weeks (local→public transfers 1:1 at this shape, 18199), submitted when ready. Smooth slope, **no step** → no new idea was discovered on the board; the method arrived complete [inference].

### 2.3 marius_binner — #2 (best raw on the board)
| Aug 24–27 | 3.9e-7 → 8.4e-8 | 3.9e-6 → 8.4e-7 | 0.100 | kit/sampler at the floor |
| Aug 29–30 | 1.6e-8 → 7.8e-9 | 2.3 → 1.86e-8 | 0.70 → 0.42 | **switched family**: a K3-class analytic chain 5 days in (his P1 was pure cubature) |
| Sep 2–8 | → 2.76e-9 | → 1.73e-8 | → 0.159 | slope: cost trimming |
| Sep 8–22 | 2.4–2.7e-9 | 1.67–1.70e-8 | 0.15 | **plateau, two weeks** |
| Sep 23 | 2.27e-9 | 1.58e-8 | 0.144 | step −7 % |
| Sep 26 | — | **1.33e-8** | 0.924 | full-budget probe |
| Sep 27 → 30 | 2.15 → **1.70e-9** | 1.44 → 1.28 → **1.15e-8** | 0.148 | **step −31 % raw in one week at constant cost** — the largest leader step of the phase |
| Oct 1–9 | 1.58–1.65e-9 | 1.14–1.17e-8 | 0.136–0.145 | plateau; cost −8 % |
P1 prose [author]: "the analytic and hybrid routes are closed" at 256×32 (Section 6.4) — he reversed that within a week of
Phase 2. Engineering signature from the PDF: Strassen–Winograd at the analytical count, float32 cast once per layer (a
measured 2.00× on the P1 score), pilot-driven neuron pruning by fire rate with an exact compensation, an exact sparse path
for rarely-firing ("cold") neurons, and *exact* layer-1/layer-2 moment "snaps" ("a 0.195 % coherent error in the exact
variance raised final MSE 4.2×").

### 2.4 mliston — #4
| Aug 24–27 | 8.5e-8 → 1.8e-8 | 8.8e-8 → 2.9e-8 | 0.97 → 0.61 | expensive chain first |
| Sep 5 | 5.0e-9 | 2.24e-8 | 0.222 | step −24 % raw + cost halved |
| Sep 20–26 | → 2.17e-9 | → 1.68e-8 | → 0.128 | steady slope |
| Oct 2 | **1.67e-9** | **1.42e-8** | 0.117 | **step −17 % raw** at flat util; nothing since (7 entries that day) |
P1 PDF [author]: rank-capped κ3 carrier (384 terms = 1.5n, not growing with depth), one κ4 per neuron, Hermite covariance
update, Gaussian tail after layer 18, 96-unit GRU (52k frozen params) predicting the closure's centering error (+17–19 %).

### 2.5 The rest
| leader | arrival | steps (raw) | now | reading |
|---|---|---|---|---|
| mk1981 | Oct 2: 2.23e-8 @ 0.242 | Oct 3: 1.85e-8 @ 0.111 (−62 % adj, mostly cost); Oct 6: 1.67e-8 | 1.65e-8 @ 0.107 | port signature: arrives at cluster accuracy, trims cost in one day, 10/day since [inference] |
| oliver_chen | Oct 2: **1.44e-8** @ 0.217 | Oct 5–7: 1.35 → 1.23e-8 | **1.23e-8** @ 0.134 (2nd-best raw) | offline-developed high-accuracy family; not the cluster; cost trimmed 0.22 → 0.13 in 5 days; no entries Oct 9 |
| suliman_tadros | Sep 4: 3.5e-8 @ 0.94 | Sep 5: 2.03e-8 @ 0.19 (−42 %); Sep 23: 1.64e-8 | 1.57e-8 @ 0.122, **flat since Sep 24**, last entry Oct 6 | stalled / locked |
| thegamers (williawa) | Sep 3 kit → Sep 6: 2.26e-8 @ 0.467 | Sep 8: 1.78e-8; plateau 1.78e-8 Sep 8 – Sep 30; Oct 1–5: → 1.47e-8 | 1.47e-8 @ 0.143 | pre-dates 504aldo's post → likely ARC's reference K3 + own work; wave participant |
| AndreasHad04 | Aug 24 | own chain stuck at 9.0e-8 raw for 4 weeks; **Sep 22: 2.23e-8 (−75 %)** — the same day as their forum post saying a κ4→κ3 FEED arm "sat unpriced for a week"; then slope to 1.47e-8 | 1.47e-8 @ 0.131 | the step IS the κ4→κ3 feed (or a port of the chain that has it) [inference, medium-high] |
| shiv_m | Aug 24 sampler at 0.9+ util | Sep 12: 3.59 → 2.11e-8 @ 0.25 (two days after 504aldo's release); Sep 30: 1.97 → 1.61e-8 (−18 %) | 1.55e-8 @ 0.139 | port + one own content step in the wave |
| lode_dockx | Aug 24 | smooth: 1.37e-6 → 4.4e-8 (Sep 7) → 2.0e-8 (Oct 9); **util 0.102 since Sep 24** | 2.03e-8 @ 0.102 | the cheapest chain on the board (13 units/layer), pure accuracy climbing at the floor |
| Puffi (Cipo) | Aug 24 | Sep 7: 1.97e-8 @ 0.146 | 2.0e-8 @ 0.133, **no entries since Sep 25** | the published SSC team has stopped; their P2 chain never beat the cluster |

## 3. Inferred method family per leader

| leader | family | evidence | confidence |
|---|---|---|---|
| J2W | fixed-width factorized-κ3 chain with one continuous size knob (carrier width / rank) + ≥3 discrete content additions (Sep 17, Sep 28, Oct 6); heavy cost engineering (util 0.106 ≈ 13.5 units/layer, the budget of covariance transport plus ~0.8n carrier columns) | Sep 14 ladder; probe-then-compress twice; P1 util modes and 1,532 entries show a brute-force experimentalist; Numascale = HPC/shared-memory engineering | medium (shape), low (content) |
| marius_binner | analytic chain since Aug 29; a single large content addition Sep 23–30 (−31 % raw) that the scalar-κ4 cluster ceiling (2.0e-8) cannot explain; exactness-first engineering (exact low-layer moments, Strassen at count, cold-neuron sparsity) | P1 PDF; feed; his Sep 26 probe | high (family), low (what the Sep 30 content is — κ4 response modes or an in-chain drift channel are the two P1-published candidates that fit the size) |
| Luna | complete method brought in from offline work; smooth tuning only; arrived 17 % below the cluster | 39 entries, no steps, no prior rounds, generic-engineer GitHub | low–medium |
| mliston | 1.5n-capped κ3 carrier + diagonal κ4 + Hermite covariance + frozen GRU corrector on per-neuron channels (his own P1 design, which is exactly the structure PRIOR_ROUNDS §4a says transfers); Oct 2 step = one new content item | P1 PDF continuity; his P1 "through-32 analytic accumulated too much error" is moot at L/n = 1/64 | medium–high |
| oliver_chen | unknown high-accuracy family, not the cluster; cost class 17 units/layer | arrival raw 1.44e-8, 5-day compression | low |
| mk1981, shiv_m, (Luna?) | 504aldo-MIT chain + own changes, now ruled eligible (18240) | timing + arrival-at-cluster signature | medium (mk1981, shiv_m), low (Luna) |
| AndreasHad04 | own κ4-materialising chain (they hold a (2,2) κ4 slice, cap 3776) that gained 4× the day the κ4→κ3 feed was wired | 18218 #4 + feed | medium–high |
| lode_dockx | minimal chain at the 0.1 floor (covariance + small κ3), accuracy-only tuning | util 0.102 flat 2 weeks | medium |
| suliman_tadros, thegamers | K3 chains in the cluster's cost class; suliman stalled since Sep 24 | feed | medium |

**What all eleven have in common [measured + inference]:** every one of them dropped from 0.4–0.97 util to 0.10–0.16 while
raw stayed within ±20 %, and *then* improved raw. Cost first, content second — the opposite order to ours. None sits above
0.16 util; nobody buys accuracy with FLOPs because the score is linear in cost above 0.1 and the between-team raw/util
correlation is nil. The per-layer budget they all converge on (13–20 n³-units) is covariance transport (3–4) plus a
fixed-size κ3 object of about 0.75–1.3n column-equivalents, exactly PRIOR_ROUNDS §4b's arithmetic; a depth-growing cohort
stack cannot sit there. The three leaders with the best raw (marius 1.14, oliver 1.23, J2W/Luna 1.36e-8) are 1.7–1.9×
below the cluster ceiling of the K3 + scalar-κ4 chain (2.04–2.23e-8), which per 504aldo's own ladder is the distance
between "scalar κ4 core" and "something richer than a dense κ4 channel".

## 4. What the util distribution says about per-layer cost structure

- Budget = 2^41 FLOPs ≈ 2048 n³-units at n = 1024, 16 layers → 128 units/layer at full budget; util u ⇒ 128u units/layer.
- Top-15: 0.102 / 0.135 / 0.159 (min / median / max) ⇒ **13 / 17 / 20 units per layer** [measured].
- Fixed charges everyone pays: covariance transport W Σ Wᵀ = 4 units (3 with the symmetric spelling, PRIOR_ROUNDS §5);
  Strassen L5–L7 shaves 0.5–1 point of util (ngmitam, 18218 #6: 25.42 → 24.52 % for L5 → L7 on the grader, less than local).
- So the *variable* part is 9–16 units/layer. At ARC's ≈12 n² per carrier column per layer, that is **0.75–1.3n columns of
  κ3 carrier per layer**, or an equivalent amount of n×n κ4-mode work. Floor-huggers (J2W, mk1981, lode) are at ~0.8n;
  spenders (marius, shiv, thegamers, jlacombe) at ~1.2–1.3n.
- Cost does not buy accuracy across teams (r = −0.11 over the top 25) but does within one method (J2W ladder: 7× → −18 %).
  Translation: a leader's size knob is worth ~5 % raw per doubling of cost; the content steps were worth 12–31 %.
  Anyone optimising width instead of content is tuning the small knob.
- Our 5.23e-9 at util 0.235 (michael_anderson7, raw 2.23e-8): we pay 30 units/layer for cluster-level raw. Halving cost
  alone would put us at 2.6e-9 (#15); the cluster's raw at the floor would give 2.0e-9 (#9). Content, not width, is what
  separates #9 from #1.

## 5. Phase-1 ideas by the same people that plausibly transfer

| idea (owner, P1) | transfer to 1024×16 | why |
|---|---|---|
| Fixed 1.5n κ3 carrier, diagonal κ4, frozen GRU corrector on per-neuron channels (mliston) | **yes** — it is the leaders' cost class and he is #4 with it | O(n²r) per layer with r fixed; learned feature consumers are what ARC named for the warm-up winners |
| Exact low-layer moment snaps (marius): layer-1 mean exact, layer-2 pre-activation variance via the arc-cosine kernel; "0.195 % coherent error → 4.2× MSE" | **yes, cheap** | Layers 1–2 of a cumulant chain admit closed forms for mean, covariance and κ3/κ4; pinning them removes the coherent seed that depth amplifies (hyojun_kwon's unit-gain mean loop, 18154) |
| Fire-rate-gated pruning + exact cold path (marius): drop neurons with gate probability below p* ≈ 0.17–0.2, compensate their mean exactly | **yes, as a cost lever** | A ReLU unit with P(fire) ≈ 0 contributes ~0 to downstream κ3; its carrier columns are dead weight. His P1 cut saved 45 % cost for 1.9 % MSE |
| Strassen–Winograd at the analytical count, float32 cast, allocation arenas (marius, ngmitam) | already done by us (L5, leaf 32) | ngmitam: L7 buys another ~0.9 pt on the grader; L8 gives it back |
| Multi-mode κ4 response closure (Puffi SSC, p ≤ 4) | **yes** | pure n×n work; Puffi themselves stalled at 2.0e-8 in P2 and stopped Sep 25, so SSC *alone* is not the leaders' edge |
| Kerdock/MUB cubature, control variates, "analytic route closed" (marius, suliman, shiv_m, Puffi's score stack) | **no** — all four abandoned it within a week of Phase 2 | sampling at budget is 1.13e-6; marius's own P2 trajectory is the refutation of his P1 §6.4 |

## 6. Top 3 transferable hypotheses, each with a cheap test

**H1 — The missing content is a richer κ4→κ3 feed core, not more κ3 width.**
Evidence: 504aldo's own ladder (no feed 4.20e-8 → scalar λ·C_off 2.23e-8 → dense κ4 channel 2.04e-8); AndreasHad04's R²
for the (2,2) slice decaying from 0.998 (layer 1) to 0.045 (layer 15) — a scalar law underfits at depth in *their*
representation; Puffi's p ≤ 4 response modes; the board-wide wave one week after the pre-activation law was clarified;
the leaders' raw sits 1.7–1.9× below the scalar-core ceiling.
Cheap test (local, Mini-10): in our chain replace the scalar κ4 core with a rank-p fitted response, p ∈ {2, 4}, over
`{C_pre, gated C (½(g_i+g_j)C_ij), mean-variance·I}` with a per-layer indefinite Λ ridge-fit to the next layer's marginal κ4
(or, per Puffi's unintegrated audit, to the consumed mean correction). Pre-register: raw must fall ≥ 9 % (the scalar → dense
gap) at ≤ +2 units/layer. Falsifier: < 3 % at p = 4 → our bottleneck is elsewhere (go to H2).

**H2 — Exact layer-1/2 moments ("snaps") remove a coherent seed error.**
Evidence: marius's P1 mechanism (exactness of early analytic constants is load-bearing; 0.195 % → 4.2×), yujigon's
finding that our kind of per-layer constants absorb *accumulated* drift, the unit-gain mean loop. Layers 1–2 have closed
forms: layer-1 pre-activation is exactly Gaussian (mean 0, cov W₁W₁ᵀ), its ReLU moments and κ3/κ4 are exact; the layer-2
pre-activation covariance is the arc-cosine kernel.
Cheap test (local, one afternoon): inject MC-oracle (N ≥ 1e6, we have `mc_cache_*` files) layer-2 covariance and κ3 into our
chain and run to the output; separately inject the closed-form arc-cosine covariance. Pre-register: if the oracle injection
moves final raw by ≥ 5 %, implement the closed forms (cost ≈ 0); if < 1 %, our layer-2 inputs are already exact enough —
drop it in a day.

**H3 — Run the leaders' probe-then-compress discipline on our own chain to locate our binding error.**
Evidence: J2W's 4-point ladder and both full-budget probes; marius's probe 3 days before his −31 % step. The ladder measures
how much of the deficit is *truncation* (recoverable by width, 5 %/doubling) versus *content* (unrecoverable at any width).
Cheap test (3 local Mini-10 runs): our chain at carrier cap {2n, 4n, uncapped/cohort}. Pre-register: if uncapped raw is
≤ 10 % better than the capped chain, width is not our problem and every remaining day goes to H1/H2; if ≥ 25 % better, the
cap is committing the error and a whole-stack recompression every k layers (PRIOR_ROUNDS L2 regime b) is the lever. Either
result ends the "fixed width vs content" argument with a number, which is what the leaders did on Sep 14 and Sep 26.

**H4 (cost-only rider, zero accuracy risk) — fire-rate pruning of carrier columns.** Drop κ3-carrier columns for neurons whose
gate probability is < 0.17 (marius's measured break-even), compensating their mean exactly. Pre-register ≥ 8 % util drop at
< 1 % raw change. Only worth doing if H1/H2 land, since below 0.1 util there is nothing to collect.

## 7. Watch items before Oct 17

- Staff will re-bill all affected submissions with a new flopscope and only then open selection (18118 #6). Any util number
  above, ours included, may move; raw will not.
- J2W still grades 6–7 entries a day and has moved raw three times in three weeks; marius and Luna are plateaued at
  1.14–1.17e-8 and 1.36–1.40e-8; mliston, suliman and Puffi have gone quiet. Expect J2W and oliver_chen to move again.
- `leaderboard_snapshot.py` reads the stale board; a feed-based snapshot (the GraphQL query in this file's header) is the
  truthful instrument from here on.
