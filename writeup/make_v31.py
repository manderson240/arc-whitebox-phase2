"""Build PHASE2_WRITEUP_V31.md from the frozen PHASE2_WRITEUP_V30.md and emit V31_CHANGELOG.md.

Every edit is an (old, new) pair whose old text must occur exactly once at the time it is
applied. Moves cut a block verbatim and paste the identical string at the destination.
V30 is read only. Run: python3 make_v31.py
"""

from pathlib import Path


HERE = Path(__file__).parent
SRC = HERE / "PHASE2_WRITEUP_V30.md"
DST = HERE / "PHASE2_WRITEUP_V31.md"
LOG = HERE / "V31_CHANGELOG.md"

doc = SRC.read_text()
rows = []  # (id, kind, where, old, new, source)


def R(eid, where, old, new, source):
    global doc
    n = doc.count(old)
    assert n == 1, f"{eid}: old text occurs {n} times"
    doc = doc.replace(old, new)
    rows.append((eid, "edit", where, old, new, source))


def MOVE(eid, where, block, pointer, anchor, insert, source, before=True):
    """Cut `block` (verbatim), leave `pointer` in its place, paste `insert` (which must contain
    `block` unchanged) immediately before (or after) `anchor`."""
    global doc
    assert insert.count(block) == 1, f"{eid}: insert must carry the block verbatim"
    n = doc.count(block)
    assert n == 1, f"{eid}: block occurs {n} times"
    doc = doc.replace(block, pointer)
    m = doc.count(anchor)
    assert m == 1, f"{eid}: anchor occurs {m} times"
    doc = doc.replace(anchor, insert + anchor if before else anchor + insert)
    rows.append(
        (
            eid,
            "move",
            where,
            block,
            pointer,
            source + f" | destination: before '{anchor.strip()[:70]}'" if before else source,
        )
    )


def line_starting(prefix):
    hits = [ln for ln in doc.split("\n") if ln.startswith(prefix)]
    assert len(hits) == 1, f"{prefix!r}: {len(hits)} lines"
    return hits[0]


SRC_NURL = "research/forum/pdfs_20261022/ndk82I7CUSjB0g4dxOqcdtjmaXg.pdf (Nurlanggs, forum 18252, draft 2026-10-18)"
SRC_MAZ = "research/forum/pdfs_20261022/pg4mvIMJnQHWhZqnRClIsvC0ooV.pdf (Artyom_Mazur, forum 18249)"
SRC_KAI = (
    "research/forum/pdfs_20261022/2Sz9qr3S0AaLcSjksKzXXnPYEVp.pdf (kai_leal_gonzalez, forum 18246)"
)
SRC_HYO = "research/forum/pdfs_20261022/9NvFSYXNhGpw4QTKxs6dsd6AR1F.pdf (hyojun_kwon, forum 18255, revision of 18 October 2026)"
SRC_HEN = "research/forum/pdfs_20261021/1r2sLiRMQPPB0n1X5ynuhid2RC.pdf (James Henry, topic 18097, rev. with erratum 2026-08-04)"
SRC_ABH = "forum topic 18264 post #1 (abhimanyu_singh, 2026-10-21T11:27Z), public Discourse JSON read 2026-10-22, prose only"
V30 = "PHASE2_WRITEUP_V30.md"

# ---------------------------------------------------------------- 3. header
old_header = line_starting("**This document corresponds to one submission:")
R(
    "H1",
    "header",
    old_header,
    "**Corresponding submission: v117_kd, AIcrowd #337578, graded 4.00e-9, 0 failed; nominations in B.4.**",
    f"{V30} header (numbers and ids unchanged); the removed lineage is pasted verbatim into B.1 (H2)",
)
R(
    "H2",
    "Appendix B.1, new first paragraph (lineage moved verbatim from the V30 header)",
    "### B.1 Selected graded ladder (the rows a finding or nomination cites; the full ladder is in `research/rebuild/calibration.jsonl`; all failed = 0 unless noted)\n",
    "### B.1 Selected graded ladder (the rows a finding or nomination cites; the full ladder is in `research/rebuild/calibration.jsonl`; all failed = 0 unless noted)\n\n"
    "**Lineage (moved verbatim from the V30 header in V31).** " + old_header + "\n",
    f"{V30} header, verbatim",
)

# ---------------------------------------------------------------- 1+3. abstract
old_abs = line_starting("We built a cumulant-propagation estimator of the per-neuron output mean")
tail_from = "**A second trap:**"
assert old_abs.count(tail_from) == 1
abs_tail = old_abs[old_abs.index(tail_from) :]
new_abs = (
    "**When the truth is Monte-Carlo sampled, an oracle reading is biased, and we measured by how much.** "
    "In our cumulant-propagation estimator of the per-neuron output mean of random 1024 × 16 ReLU MLPs, "
    "an exact per-neuron σ² reads 0.776 of baseline MSE uncorrected, 0.511 corrected (90 % CI 0.44–0.58; layers 11–15 only 0.635, head frozen); "
    "a control that must read ≈ 0 up to the Hermite-truncation floor reads 0.305 uncorrected and 0.002 corrected. "
    "**The noise correction used is not new.** It is the noise-ceiling subtraction of computational neuroscience (Sahani & Linden 2003; Pospisil & Bair 2021), "
    "equivalently a two-point Richardson extrapolation in 1/N of a nested Monte-Carlo reading (Rainforth et al. 2018), and other participants measured or corrected "
    "Monte-Carlo noise in their own oracles and references (Nurlanggs, Artyom_Mazur, kai_leal_gonzalez, hyojun_kwon; Appendix I.1). "
    "What is ours, stated narrowly and not as a first: two-half extrapolation of the MC noise in the injected quantity, checked by a known-answer control "
    "(Appendix G: a 21-line scalar toy), and the measured size of the misreading (0.776 vs 0.511); the corrector-in-place judging rule (§4); "
    "the measured truncation ceiling (§5); and the engineering results (the wall knapsack, §7A, and shared transported bases, §7B). "
    "Oracle injection (replacing one internal quantity by sampled ground truth) is a common diagnostic for such estimators (Nurlanggs, forum 18252; Susupro, forum 18254). "
    "The noise SE is ≈ 0.9 of the chain's own error at z8 and ≈ 0.33 of it at z15, so an uncorrected oracle understates the lever it measures, "
    "by an amount that depends on the estimator's accuracy as well as on the sample count. "
    + abs_tail.replace(
        "the G-RB144 gate behind v112 is one of them (its bar was derived after G-RB143's data were seen, §7B).",
        "the gate behind v112 is one of them (its bar was derived after the preceding gate's data were seen, §7B).",
    )
)
assert "G-RB" not in new_abs
R(
    "A1",
    "Abstract (reordered: measured result first, credit second; narrow novelty; G-RB ids out)",
    old_abs,
    new_abs,
    f"{V30} abstract (every number unchanged: 0.776, 0.511, 0.44–0.58, 0.635, 0.305, 0.002, 0.9, 0.33); credits: {SRC_NURL} p.23; {SRC_MAZ} p.3–4, p.20; {SRC_KAI} p.2, p.9; {SRC_HYO} p.26–27",
)

# ---------------------------------------------------------------- 2. criteria map + impact table
R(
    "S1",
    "Two-page summary, top: prize-criteria map and graded-impact table (condensed from B.0)",
    "## Two-page summary\n\n**Corresponding submission:**",
    "## Two-page summary\n\n"
    "> **The three prize criteria, one line each.**\n"
    "> (i) **Novelty, narrow:** the noise correction is standard and others handled oracle or truth noise (§1.2); ours is two-half extrapolation of the MC noise in the injected quantity, checked by a known-answer control, and the measured size of the misreading (0.776 vs 0.511), plus two procedural results (§4, §5).<br>\n"
    "> (ii) **Clarity and accuracy:** each claim carries a tag ([proved], [measured], [argument], [A, unreplicated]) and names its file; bars were pre-registered except the exceptions in §8; proofs carry falsifiers (Appendix P); Appendix E gives the reproduction commands.<br>\n"
    "> (iii) **Checkable impact:** graded v58_ne 4.98e-9 → v117_kd 4.00e-9 (−19.7 %), from constant screens, exact-cost work and shared transported bases (table below); the only graded step from an algorithmic idea is the §6 closure (−2.3 %, with a corrector refit); the three diagnostics changed what was not built.\n\n"
    "**Graded impact** (condensed from Appendix B.0; AIcrowd graded adjusted scores).\n\n"
    "| what | graded step | effect |\n"
    "|---|---|---|\n"
    "| κ4 response closure (§6) | v49 #334744 5.59e-9 → v51 #334768 5.46e-9 | −2.3 %, closure plus a corrector refit; closure-only evidence is ungraded: VALID-20 OFF/ON 1.0327 raw, 17/20 nets worse |\n"
    "| constant screens, one prune change, exact-cost work, wall-budgeted levels (B.0 items 5–7) | v77_fuse #335642 4.92e-9 → v110 #337268 4.21e-9 | −10.4 % through v95 #336648 4.41e-9 (constant screens and the prune); the rest exact-cost and wall work, step by step in B.0 |\n"
    "| shared transported old-tier bases (§7B) | v110 #337268 4.21e-9 → v112_sb #337384 4.01e-9 | −4.8 %, 0 failed; v117_kd #337578 (two constants on top) 4.00e-9, below the meter's resolution |\n"
    "| noise-corrected oracle, corrector-in-place rule, truncation ceiling (§3–5) | none | no graded impact; the rule stopped two shipments (the dense closure and the κ4 predictor) |\n"
    "| head-to-head against the organizers' simple factorized K = 3 (claim 9) | not graded | 0.533× its final-layer MSE (95 % CI 0.49–0.59), lower on 8/8 nets, at 388 vs 3040 n³ FLOPs |\n\n"
    "**Corresponding submission:**",
    f"{V30} Appendix B.0 items 2, 4, 5, 6, 7, 8, 8b, 9 and claims row 9 (every number and id copied from there; no new number)",
)

old_impact_box = (
    "> **Measured performance impact on graded submissions** (one entry per idea, with graded ids): Appendix B.0. In short, every graded gain after v58_ne "
    "(4.98e-9 → 4.00e-9, −19.7 %) came from constant screens, exact-cost engineering and one near-exact cost cut (shared old-tier bases, raw ×1.0145, §7B); "
    "the three transferable findings changed what was *not* built.\n\n---\n\n\n"
)
R(
    "S2",
    "after the claims box: duplicate impact pointer removed (its sentence is B.0 item 9 verbatim; the table at the top of the summary replaces the pointer)",
    old_impact_box,
    "",
    f"{V30} B.0 item 9 (same sentence, still there)",
)

# ---------------------------------------------------------------- 1. summary result 1 credit + Figure 1 placement
old_r1 = (
    "- Two-half Richardson extrapolation removes it. This is the noise-ceiling correction of computational neuroscience; Sahani & Linden 2003 and Rainforth et al. 2018 "
    "(Thm 3, its bounded-second-derivative case) are credited."
)
R(
    "S3",
    "Summary result 1, second bullet (credit and narrow novelty)",
    old_r1,
    old_r1
    + " Other participants measured or corrected Monte-Carlo noise in their own oracles and references (Nurlanggs, Artyom_Mazur, kai_leal_gonzalez, hyojun_kwon; Appendix I.1). "
    "Ours, narrowly: two-half extrapolation of the MC noise in the injected quantity, checked by a known-answer control, and the measured size of the misreading (0.776 vs 0.511).",
    f"{SRC_NURL} p.23; {SRC_MAZ} p.3–4, p.20; {SRC_KAI} p.2, p.9; {SRC_HYO} p.26–27",
)

old_fig0 = line_starting("![F0 — oracle noise bias]")
old_cap0 = line_starting("**F0.** Monte-Carlo noise in a sampled-truth oracle")
fig0_block = "---\n\n" + old_fig0 + "\n\n" + old_cap0 + "\n\n"
assert doc.count(fig0_block) == 1
new_fig0 = old_fig0.replace("![F0 — oracle noise bias]", "![Figure 1 — oracle noise bias]")
new_cap0 = old_cap0.replace("**F0.**", "**Figure 1.**")
R("F1a", "Figure 1 (was F0) removed from after the summary", fig0_block, "", f"{V30}, moved by F1b")
anchor_r2 = "**2. The final layer is quadratically hypersensitive to coherent σ² error"
R(
    "F1b",
    "Figure 1 (was F0) placed directly after summary result 1; label F0 → Figure 1 (caption otherwise verbatim)",
    anchor_r2,
    new_fig0 + "\n\n" + new_cap0 + "\n\n" + anchor_r2,
    f"{V30} F0 image line and caption, verbatim except the label",
)

# ---------------------------------------------------------------- 1+5. summary result 2: credits, coincidence bullet out
old_infer = line_starting(
    "- We read this as: the coherent part of the σ² error is already at its optimum"
)
R(
    "S4",
    "Summary result 2, [inference] bullet: related Phase 2 work (Mazur Proposition 1; abhimanyu_singh) and a pointer to the consistency note",
    old_infer,
    old_infer
    + " Related: Artyom_Mazur's Proposition 1 (forum 18249, p.19) makes a neuron's next-layer variance error a coherent level from tr ΔC plus noise independent across neurons, "
    "and a model of the neuron's own state cannot see that noise (p.20); abhimanyu_singh (forum 18264, prose; n = 256) measures a quadratic law for iid noise on the D21 and D3 slice read-outs "
    "(added MSE ≈ 0.91σ² and 0.60σ²) and finds that bias propagates while zero-mean noise attenuates. A consistency note on the leader's raw MSE is in §7C.",
    f"{SRC_MAZ} p.1 item 1, p.19 Proposition 1, p.20 Consequence 1; {SRC_ABH} §2 and §4",
)
old_coinc = line_starting("- Consistency note, not a proof: the leader's graded raw MSE over ours")
R(
    "S5",
    "Summary result 2: 'Consistency note … may be coincidence' bullet removed (it remains in §7C 'Reading' and C.1)",
    old_coinc + "\n",
    "",
    f"{V30} §7C 'Reading [inference]' (same note, kept)",
)

# ---------------------------------------------------------------- 1. summary result 3 + §3 principle paragraph (Mazur item 4)
old_p = "and in Phase 2 by Nurlanggs (forum 18252). We credit them. Ours are the measured n = 1024, depth-16 instances, plus the noise-corrected reading."
new_p = (
    "and in Phase 2 by Nurlanggs (forum 18252) and Artyom_Mazur (forum 18249, item 4, p.2: exact variance alone made the result worse, ×1.09, while exact variance, κ3 and κ4 together gave ×0.12). "
    "We credit them. Ours are the measured n = 1024, depth-16 instances."
)
assert doc.count(old_p) == 2
doc = doc.replace(old_p, "@@P1@@", 1)
R(
    "S6",
    "Summary result 3, credit bullet: Mazur item 4 added; 'plus the noise-corrected reading' dropped (that claim is result 1's)",
    "@@P1@@",
    new_p,
    f"{SRC_MAZ} p.2 item 4",
)
rows[-1] = ("S6", "edit", rows[-1][2], old_p, new_p, rows[-1][5])
R(
    "S7",
    "§3 'The principle, with its two measured instances' (same sentence as S6, kept consistent)",
    old_p,
    new_p,
    f"{SRC_MAZ} p.2 item 4",
)

# ---------------------------------------------------------------- 5. summary: what did not work / try next → Appendix F.8
old_wdnw = (
    "### What did not work (measured, so nobody needs to repeat it)\n"
    + line_starting("An exact (2,2)-slice κ4 oracle (0.953 at layers 8-14")
    + "\n\n"
)
old_next = (
    "### What we would try next\n"
    + line_starting(
        "Gaussian-copula pair moments with exact Edgeworth marginals, non-perturbative in ρ (proposed"
    )
    + "\n\n"
)
block = old_wdnw + old_next
pointer = "**What did not work, and what we would try next:** Appendix F.8, with other negatives in F.0.\n\n"
insert = (
    "### F.8 What did not work, and what we would try next (moved verbatim from the V30 two-page summary in V31)\n\n"
    + block.replace("### What did not work", "#### What did not work").replace(
        "### What we would try next", "#### What we would try next"
    )
)
# the insert must carry the block's text verbatim apart from the demoted headings; check the paragraphs
for para in (old_wdnw.split("\n")[1], old_next.split("\n")[1]):
    assert insert.count(para) == 1
global_doc_before = doc
assert doc.count(block) == 1
doc = doc.replace(block, pointer)
anchor_f9 = "\n## Appendix G. A scalar toy of the oracle noise bias"
assert doc.count(anchor_f9) == 1
doc = doc.replace(anchor_f9, "\n" + insert.rstrip("\n") + "\n\n" + anchor_f9.lstrip("\n"), 1)
rows.append(
    (
        "M1",
        "move",
        "Summary 'What did not work' and 'What we would try next' → new Appendix F.8 (paragraphs verbatim; headings demoted ### → ####)",
        block,
        pointer,
        f"{V30} two-page summary",
    )
)

# ---------------------------------------------------------------- 4. F2 → Appendix F.9 as Figure 3 with a full caption
old_fig2 = "![F2 — error origin by layer](figs/F2_error_origin_by_layer.png)\n\n**F2.** Share of final-layer MSE by layer of origin (diagonal adjoint, net 0).\n\n"
R("F2a", "§2: figure F2 and its one-line caption moved to Appendix F.9", old_fig2, "", f"{V30} §2")
f9 = (
    "### F.9 Figure 3: error origin by layer (moved from §2 in V31)\n\n"
    "![Figure 3 — error origin by layer](figs/F2_error_origin_by_layer.png)\n\n"
    "**Figure 3.** Share of final-layer MSE by layer of origin (diagonal adjoint, net 0) [A, unreplicated]. Each layer's local residual is weighted by gain_l, "
    "the mean squared column norm of its adjoint T_l; uncorrected f64 chain, no closure, K = 2 gates, age 5. Shares and caveats in §2.\n\n"
)
R(
    "F2b",
    "Appendix F.9 (new): Figure 3 (was F2) with a full caption built from §2's own text",
    anchor_f9.lstrip("\n"),
    f9 + anchor_f9.lstrip("\n"),
    f"{V30} §2 'Diagonal adjoint attribution' (gain_l definition; 'uncorrected f64 chain, no closure, K = 2 gates, FIT 0/2/4, age 5'; tag [A, unreplicated])",
)
R(
    "F2c",
    "§2 figure reference",
    "layers ≤ 2 ≤ 0.2 % (uncorrected f64 chain, no closure, K = 2 gates, FIT 0/2/4, age 5; F2).",
    "layers ≤ 2 ≤ 0.2 % (uncorrected f64 chain, no closure, K = 2 gates, FIT 0/2/4, age 5; Figure 3, Appendix F.9).",
    "renumbering",
)
R(
    "F3a",
    "§6 figure reference",
    "17 of 20 nets worse (F3, Appendix B)",
    "17 of 20 nets worse (Figure 2, Appendix B.1)",
    "renumbering",
)
R(
    "F3b",
    "B.1 figure alt text",
    "![F3 — closure OFF/ON on v58_ne]",
    "![Figure 2 — closure OFF/ON on v58_ne]",
    "renumbering",
)
R(
    "F3c",
    "B.1 caption label",
    "**F3.** Per-net raw-MSE ratio",
    "**Figure 2.** Per-net raw-MSE ratio",
    "renumbering",
)
R(
    "F6a",
    "claims-box pointer to Appendix H",
    "and the F6 oracle/ceiling ladder:** Appendix H.",
    "and the oracle/ceiling ladder (Figure 4):** Appendix H.",
    "renumbering",
)
R(
    "F6b",
    "Appendix H title",
    "## Appendix H. Oracle method box, recipe and the F6 ladder (moved from the V29 front matter)",
    "## Appendix H. Oracle method box, recipe and the oracle/ceiling ladder, Figure 4 (moved from the V29 front matter)",
    "renumbering",
)
R(
    "F6c",
    "Appendix H alt text",
    "![F6 — oracle and ceiling ladder]",
    "![Figure 4 — oracle and ceiling ladder]",
    "renumbering",
)
R(
    "F6d",
    "Appendix H caption label",
    "**F6.** Pooled final raw MSE vs the twin",
    "**Figure 4.** Pooled final raw MSE vs the twin",
    "renumbering",
)
R(
    "F0a",
    "Appendix E step 2 comment",
    "control 0.305 → 0.002 [−0.043,0.046] (§3 table, F0)",
    "control 0.305 → 0.002 [−0.043,0.046] (§3 table, Figure 1)",
    "renumbering",
)
R(
    "F0b",
    "§7C 'Related observation' figure reference",
    "his probe-noise decomposition is a cousin of our F0 noise correction.",
    "his probe-noise decomposition (p.9) is a cousin of our noise correction (Figure 1).",
    f"renumbering; page from {SRC_HEN} p.9",
)

# ---------------------------------------------------------------- 1. §1.2 novelty + credit list; §1A stub
R(
    "N1",
    "§1.2 'New here, narrowly' (narrow novelty; the false 'found no prior application' sentence removed; credits)",
    "**New here, narrowly:** applying it to a diagnostic that had not used it, the oracle injection of sampled truth into a white-box estimator, with a known-answer control (§3). "
    "A literature search found no prior application of it to oracle injection in the organizers' paper, code or blog, or in the forum prose we read.",
    "**Ours, narrowly and not as a first:** two-half extrapolation of the MC noise in the injected quantity, checked by a known-answer control, and the measured size of the misreading "
    "(0.776 vs 0.511; §3). Others handled Monte-Carlo noise in their own oracles and references: Nurlanggs measured his oracle's noise floor, Artyom_Mazur subtracts oracle noise "
    "measured from two seeds in his substitutions, kai_leal_gonzalez estimated his truth reference's noise and hyojun_kwon split-half-corrected his, and James Henry (Phase 1) "
    "decomposed his probe noise (pages in Appendix I.1).",
    f"{SRC_NURL} p.23; {SRC_MAZ} p.3–4, p.19–20; {SRC_KAI} p.2; {SRC_HYO} p.26–27; {SRC_HEN} p.9",
)
R(
    "N2",
    "§1.2 'Not new' list",
    "**Not new:** oracle injection itself,",
    "**Not new:** correcting oracle or truth noise as such, oracle injection itself,",
    "brief, item 1",
)
R(
    "N3",
    "§1.2 credit list",
    "Every other credit (ARC, Team Puffi, Team 504aldo, Nurlanggs, Susupro, hyojun_kwon, other participants, textbooks)",
    "Every other credit (ARC, Team Puffi, Team 504aldo, Nurlanggs, Susupro, Artyom_Mazur, kai_leal_gonzalez, hyojun_kwon, James Henry, abhimanyu_singh, other participants, textbooks)",
    "Appendix I.1 as amended (N6–N8)",
)
R(
    "N4",
    "§1A stub removed (it was a pointer only; §1.2 already points to Appendix I)",
    "## 1A. Related work\n\nMoved to Appendix I in V30 (for length). §1.2 names the sources of the noise correction; Appendix I.1 itemises every other credit.\n\n---\n\n",
    "",
    V30,
)
R(
    "N5",
    "§3 'Provenance first' (narrow novelty, consistent with §1.2)",
    "What this section adds is its application to sampled-truth oracle injection in a white-box estimator, a known-answer control, and the readings below (Appendix I has the sources).",
    "What this section adds, narrowly and not as a first, is two-half extrapolation of the MC noise in the injected quantity, checked by a known-answer control, and the measured size "
    "of the misreading (0.776 vs 0.511); others' handling of oracle and truth noise is credited in Appendix I.1, and Appendix I has the sources.",
    "brief, item 1",
)

# ---------------------------------------------------------------- 1. claims rows 1-2
R(
    "C1",
    "Claims box row 1 (narrow novelty)",
    "Known-answer control 0.305 uncorrected, 0.002 corrected (vs the head-ON twin). |",
    "Known-answer control 0.305 uncorrected, 0.002 corrected (vs the head-ON twin). The correction is standard and others handled oracle or truth noise (Appendix I.1); "
    "ours, narrowly: two-half extrapolation of the MC noise in the injected quantity, its known-answer control and the measured size of the misreading. |",
    "brief, item 1",
)
R(
    "C2",
    "Claims box row 2 (Mazur item 4)",
    "The principle was stated publicly earlier (Henry, Pepper, Nurlanggs; §3);",
    "The principle was stated publicly earlier (Henry, Pepper, Nurlanggs; in Phase 2 also Artyom_Mazur, forum 18249, item 4 p.2: exact variance alone ×1.09, with κ3 and κ4 ×0.12; §3);",
    f"{SRC_MAZ} p.2 item 4",
)

# ---------------------------------------------------------------- 1. Appendix I / I.1 / I.2
R(
    "N6",
    "Appendix I intro (V31 sources)",
    "(`writeup/DRAFT_RELATED_WORK.md` lists what it read and what it could not reach); I read none of them.",
    '(`writeup/DRAFT_RELATED_WORK.md` lists what it read and what it could not reach); I read none of them. The credits added in V31 (I.1, "Monte-Carlo noise") were read by a Claude agent '
    "from the participants' PDFs in `research/forum/pdfs_20261021/` and `pdfs_20261022/` and from forum prose; no participant code was opened.",
    "V31 process",
)
R(
    "N7",
    "Appendix I.1, Susupro/Nurlanggs bullet: the inaccurate 'as far as the posts show, not noise-corrected' sentence rewritten",
    "Nurlanggs's tables are oracle injections with sampled truth like ours and, as far as the posts show, not noise-corrected; our correction is complementary.",
    "Nurlanggs's tables are oracle injections with sampled truth like ours, and his PDF measures the noise: a 16M-path oracle carries a +4.2e-9 MSE floor on its own net (var_h / N), "
    "and scoring injections against the oracle's own paths reads 0.564 against 0.520 when scored against the organizers' independent 1e9-path truth (forum 18252, p.23; the injections are on p.7). "
    'His remedy is to score against the independent truth ("use them as the metric", p.23); ours extrapolates away the noise in the injected quantity itself.',
    f"{SRC_NURL} p.7, p.23 (also p.15 timeline and p.28 table)",
)
R(
    "N8",
    "Appendix I.1: new bullet crediting Monte-Carlo noise handling and two related Phase 2 results",
    "- **Others (prose):** marius_binner (fire-rate pruning),",
    "- **Monte-Carlo noise in oracles and references (read from the PDFs in V31).**\n"
    '  - *Artyom_Mazur (forum 18249).* His oracle substitutions use 10⁷ samples with two independent seeds "so that the oracle\'s own noise can be measured and subtracted" (p.4; also p.3). '
    'He reports an "exact" covariance substitution that read worse because its 4·10⁶-sample oracle\'s noise was coherent (p.19, N50), an off-diagonal-covariance payoff of ×0.55–0.68 '
    '"noise-corrected two ways" (p.20), and a split-half noise ceiling of 0.87–0.98 for his linear model of the covariance error (p.20). This is the closest public work to our correction: noise measured from two seeds '
    "and subtracted in the substituted quantity. Ours, narrowly: two-half extrapolation of the MC noise in the injected quantity, checked by a known-answer control, and the measured size of the misreading (0.776 vs 0.511); unlike his subtraction it is a two-point extrapolation with a 5× dose check. "
    "His item 4 (p.2) states the compensation principle (exact variance alone ×1.09, variance, κ3 and κ4 together ×0.12; summary result 3), and his Proposition 1 (p.19) "
    "the coherent-plus-independent structure of per-neuron variance error (summary result 2).\n"
    "  - *kai_leal_gonzalez (forum 18246).* Estimates the noise of the organizers' truth, his dumps and an independent bake from three independent estimates (p.2), and notes that "
    'injected slices carry Monte-Carlo noise, so oracle gains are "if anything, understated" (p.9), the direction we measured.\n'
    '  - *hyojun_kwon (forum 18255, revision of 18 October).* Gates scored against "split-half-corrected Monte Carlo references" (p.27; split-half noise subtraction, p.26).\n'
    "  - *James Henry (Phase 1, topic 18097, #314695, rev. 2026-08-04).* Decomposes per-seed final MSE into bias² plus across-seed variance, correcting the K-seed mean's residual noise by /K (p.9).\n"
    "  - *abhimanyu_singh (forum 18264, prose).* A quadratic law for iid noise on the D21 and D3 slice read-outs (added MSE ≈ 0.91σ² and 0.60σ², n = 256) and a bias/variance asymmetry: "
    "truncation bias propagates while zero-mean noise attenuates (summary result 2).\n"
    "- **Others (prose):** marius_binner (fire-rate pruning),",
    f"{SRC_MAZ} p.2–4, p.19–20; {SRC_KAI} p.2, p.9; {SRC_HYO} p.26–27; {SRC_HEN} p.9; {SRC_ABH}",
)
R(
    "N9",
    "Appendix I.2, Nurlanggs truth-set paragraph (his own noise-floor measurement)",
    "This is not a controlled dose comparison or an external confirmation; we did not re-measure their chains [H].",
    "This is not a controlled dose comparison or an external confirmation; we did not re-measure their chains [H]. His PDF measures that oracle's own noise floor, +4.2e-9 (forum 18252, p.23; I.1).",
    f"{SRC_NURL} p.23",
)

# ---------------------------------------------------------------- 6. §10 → short main text + Appendix K (verbatim)
old_s10_body = (
    line_starting("Every draft of this document and the submitted code from v21_rb onward")
    + "\n\n"
    + line_starting("**Uncertain:** the MIX2 corrector is unexplained")
    + "\n"
)
new_s10 = (
    "- **Writing and code.** Anthropic Claude models (Claude Fable 5.1 and Claude Opus 5.5), running as Claude Code agents that I orchestrated, wrote every draft of this document and the "
    "submitted code from v21_rb onward; the graded v11_sw (#334046) was built by a Hermes coding agent (kimi-k2.7-code) around a Claude-written Strassen kernel. I wrote none of the code or prose.\n"
    "- **Decisions.** I set the goals and guardrails (source rule, pre-registration, ship bars), approved or declined each submission, and chose which to submit and designate.\n"
    "- **Checks.** Every measurement and proof check was run by an agent; I re-ran none of them and have not independently re-derived the mathematics. Claude agents audited V30 against its "
    "source files and re-ran Appendix E from a fresh unzip; V16–V31 were each edited by a Claude agent from the previous version (`writeup/V31_CHANGELOG.md`).\n"
    "- **Councils, for ideas only, each checked against the ledger.** Three Ollama-cloud model councils (kimi and deepseek, glm timed out; a ~04Z council on the leaders' score histories; "
    "kimi, deepseek and glm, whose GLM-5.3 proposed §7C's copula idea). Adversarial review was by agents (Claude, Ollama Cloud and local open-weight councils), not by me.\n"
    "- **Full disclosure and the list of uncertain items:** Appendix K.\n"
)
k_app = (
    "## Appendix K. LLM-use and uncertainty disclosure (moved verbatim from §10 in V31)\n\n"
    + old_s10_body
    + "\n"
)
assert doc.count(old_s10_body) == 1
doc = doc.replace(old_s10_body, new_s10)
anchor_p = "## Appendix P. Proofs behind claims made empirically in the main text"
assert doc.count(anchor_p) == 1
doc = doc.replace(anchor_p, k_app + anchor_p)
rows.append(
    (
        "M2",
        "move",
        "§10 body (two paragraphs) → new Appendix K, verbatim; §10 replaced by a five-bullet summary naming every model and council",
        old_s10_body,
        new_s10,
        f"{V30} §10 (every model and council named there is named in the short text: Claude Fable 5.1, Claude Opus 5.5, Hermes kimi-k2.7-code, the three Ollama-cloud councils with kimi/deepseek/glm and GLM-5.3 from §7C, local open-weight councils)",
    )
)
R(
    "K1",
    "Appendix K 'Uncertain' list (logged correction after the verbatim move): Nurlanggs measured his oracle's noise floor",
    "(his two truth sets agree in direction for 2 of 3 quantities, nothing more);",
    "(his two truth sets agree in direction for 2 of 3 quantities, nothing more; his PDF, forum 18252 p.23, measures that oracle's own noise floor, +4.2e-9);",
    f"{SRC_NURL} p.23",
)

# ---------------------------------------------------------------- word budget: §7B ladder and v117_kd paragraph → Appendix F.7 (verbatim)
R(
    "L0",
    "§7B: obsolete pointer bullet '- *Port bars:* Appendix F.7' deleted before the ladder moved into F.7 itself (port bars are already in F.7)",
    "\n- *Port bars:* Appendix F.7 (moved in V30 for length).\n",
    "\n",
    "V30 F.7 (port bars already there)",
)
ladder = (
    "**Evidence ladder.**\n"
    + line_starting("- *G-RB142 step 0 (proxy KILL).*")
    + "\n"
    + line_starting("- *G-RB143 (end-to-end).*")
    + "\n"
    + line_starting("- *G-RB144 (unseen nets).*")
    + "\n\n"
)
ladder_ptr = (
    "**Evidence ladder** (Appendix F.7). A proxy gate was a KILL; the end-to-end gate passed its adjusted clause (0.9653) but failed its metered-cost clause "
    "(S = 1.228 < 1.5 pt) and stays a KILL; the gate that admitted v112 was registered on the passing clause after those reads (an exception, §8) and passed on 40 unseen nets "
    "(pooled raw 1.0145, 40/40 ≤ 1.10, worst 1.064).\n\n"
)
v117 = line_starting("**The corresponding submission, v117_kd #337578.**") + "\n"
v117_ptr = (
    "**The corresponding submission, v117_kd #337578,** is v112_sb with two constants changed (pair-series order `_KH` 4 → 3, deep-layer corrector 0.9 → 0.95; "
    "`writeup/v117_kd_vs_v112.diff`): graded 4.00e-9 against 4.01e-9, grader wall max 89.2 s against 95.6 s, 0 failed. It combines the best two of six one-constant variants "
    "scored on 3 meter nets, and that meter cannot rank builds closer than about 0.3 %, so we cite v117_kd as the nominated build, not as evidence of a better method "
    "(selection disclosure and counterexamples: Appendix F.7).\n"
)
f7_anchor = "**VSE1 (G-RB153).** Scale σ²_z at z-layers 11–15 by (1 + c)."
assert doc.count(ladder) == 1 and doc.count(v117) == 1
doc = doc.replace(ladder, ladder_ptr).replace(v117, v117_ptr)
f7_insert = (
    "*§7B evidence ladder (moved verbatim from §7B in V31).*\n\n"
    + ladder
    + "*§7B, the corresponding submission (moved verbatim from §7B in V31).*\n\n"
    + v117
    + "\n"
)
assert doc.count(f7_anchor) == 1
doc = doc.replace(f7_anchor, f7_insert + f7_anchor)
rows.append(
    (
        "M3",
        "move",
        "§7B 'Evidence ladder' (heading and its 3 gate bullets; the 4th, a pointer to F.7, was deleted by L0) → Appendix F.7, verbatim; replaced by a 3-sentence pointer",
        ladder,
        ladder_ptr,
        f"{V30} §7B (pointer numbers: 0.9653, 1.228, 1.5, 1.0145, 40/40, 1.064, all from the moved bullets)",
    )
)
rows.append(
    (
        "M4",
        "move",
        "§7B 'The corresponding submission, v117_kd #337578' paragraph → Appendix F.7, verbatim; replaced by a 2-sentence summary",
        v117,
        v117_ptr,
        f"{V30} §7B (summary numbers: 4.00e-9, 4.01e-9, 89.2 s, 95.6 s, six variants, 3 nets, 0.3 %, all from the moved paragraph)",
    )
)

# ---------------------------------------------------------------- 7. G-RB ids out of running main-text prose
R(
    "G1",
    "§2",
    "skipping the layer-1 birth gave raw ×10.2 (G-RB93).",
    "skipping the layer-1 birth gave raw ×10.2 (Appendix F.0).",
    "F.0 table row (same reading)",
)
R(
    "G2",
    "§3 noise-correction label",
    "*Noise correction (G-RB119).* Each oracle",
    "*Noise correction.* Each oracle",
    "id removal",
)
R(
    "G3",
    "§3",
    "G-RB117's averaged-halves ratios (σ² 0.776,",
    "The uncorrected averaged-halves ratios (σ² 0.776,",
    "id removal",
)
R(
    "G4",
    "§3",
    "at layers 11–15 only, 0.635× [0.589, 0.680] (G-RB119b), about 75 %",
    "at layers 11–15 only, 0.635× [0.589, 0.680], about 75 %",
    "id removal",
)
R(
    "G5",
    "§3",
    "**Withdrawn:** G-RB117's rule \"exact σ² > 0.62",
    "**Withdrawn:** the §5 gate's rule \"exact σ² > 0.62",
    "id removal (G-RB117 is the §5 experiment)",
)
R(
    "G6",
    "§3 bullet",
    "- **σ² (G-RB86).** σ² =",
    "- **σ².** σ² =",
    "id removal (still in claims row 2 and the §4 table)",
)
R(
    "G7",
    "§3 bullet",
    "- **κ4 (G-RB73).** A per-neuron",
    "- **κ4 (§4, row 4).** A per-neuron",
    "id removal",
)
R(
    "G8",
    "§5",
    "**The experiment (G-RB117, pre-registered).**",
    "**The experiment (pre-registered).**",
    "id removal",
)
R(
    "G9",
    "§5",
    "so G-RB120 refit the head on the untruncated chain",
    "so a second gate refit the head on the untruncated chain",
    "id removal",
)
R(
    "G14",
    "§7B Idea",
    "G-RB2 had measured shared r384",
    "An early gate had measured shared r384",
    "id removal",
)
R(
    "G15",
    "§7B Idea",
    "and G-RB143 reads R ≈ 0.45, the first old-tier cut below 1.",
    "and the end-to-end gate (Appendix F.7) reads R ≈ 0.45, the first old-tier cut below 1.",
    "id removal",
)
R("G16", "§7C", "**VSE1 (G-RB153):** Appendix F.7", "**VSE1:** Appendix F.7", "id removal")


# ---------------------------------------------------------------- word budget: more verbatim moves (V31)
def CUT_PASTE(eid, where, block, pointer, anchor, header, source):
    """Cut block verbatim, leave pointer, paste header + block before anchor."""
    global doc
    assert doc.count(block) == 1, f"{eid}: block count {doc.count(block)}"
    doc = doc.replace(block, pointer)
    assert doc.count(anchor) == 1, f"{eid}: anchor count {doc.count(anchor)}"
    sep = "" if block.endswith("\n\n") else ("\n" if block.endswith("\n") else "\n\n")
    doc = doc.replace(anchor, header + block + sep + anchor)
    rows.append(
        (
            eid,
            "move",
            where,
            block,
            pointer,
            source + f" | destination: before '{anchor.strip()[:60]}'",
        )
    )


# §7C: old-tier damping, Reading [inference] (with the consistency note) and What we would try next -> F.7
c_od = line_starting("**Old-tier damping (G-RB153, arms OD).**") + "\n\n"
c_rd = line_starting("**Reading [inference].** The coherent part of the σ² error") + "\n\n"
c_nx = (
    line_starting(
        "**What we would try next.** Gaussian-copula pair moments with exact (Edgeworth) marginals"
    )
    + "\n"
)
blk = c_od + c_rd
f8_anchor = "### F.8 What did not work, and what we would try next"
CUT_PASTE(
    "M5",
    "§7C 'Old-tier damping' and 'Reading [inference]' paragraphs → Appendix F.7 (verbatim; the Reading carries the F0b renumbering)",
    blk,
    "**Old-tier damping and the reading [inference], with its consistency note on the leader's raw MSE:** moved verbatim to Appendix F.7 in V31; summary result 2 states both.\n\n",
    f8_anchor,
    "*§7C old-tier damping and reading (moved verbatim from §7C in V31).*\n\n",
    f"{V30} §7C",
)
CUT_PASTE(
    "M6",
    "§7C 'What we would try next' paragraph → Appendix F.7 (verbatim)",
    c_nx,
    "**What we would try next:** moved verbatim to Appendix F.7 in V31 (summary version in F.8).\n",
    f8_anchor,
    "*§7C, what we would try next (moved verbatim from §7C in V31).*\n\n",
    f"{V30} §7C",
)

# §7B clock miss and limits -> F.7
b_ck = (
    line_starting(
        "**Clock calibration miss.** The calibrated clock predicted a grader max of 87.9 s"
    )
    + "\n\n"
)
b_lm = line_starting("**Limits.** The Gram solves run in f64 because cond(Q384)") + "\n\n"
CUT_PASTE(
    "M7",
    "§7B 'Clock calibration miss' and 'Limits' paragraphs → Appendix F.7 (verbatim)",
    b_ck + b_lm,
    "**Clock miss and limits** (Appendix F.7): the calibrated clock under-predicted v112's grader max (87.9 s against 95.6 s); the f64 Gram solves bill 0.66 pt, and the 1.23 pt saving was metered on net 0 only.\n\n",
    f8_anchor,
    "*§7B clock miss and limits (moved verbatim from §7B in V31).*\n\n",
    f"{V30} §7B (pointer numbers 87.9, 95.6, 0.66, 1.23 from the moved paragraphs)",
)
R(
    "F7h",
    "Appendix F.7 heading (lists the V31 additions)",
    "### F.7 §7B and §7C detail: v112's port bars, VSE1, the knob scan and the K = 2 run (moved verbatim from §7B and §7C in V30 for length)",
    "### F.7 §7B and §7C detail: v112's port bars, VSE1, the knob scan and the K = 2 run (moved verbatim from §7B and §7C in V30 for length); the §7B evidence ladder, v117_kd paragraph, clock miss and limits, and §7C's damping, reading and next step (moved verbatim in V31)",
    "V31 moves M3–M7",
)

# §7 body -> new F.10; §7A body -> Appendix J
s7_head = "## 7. Finding 6 (supporting): a per-source cost floor for our κ3 birth\n\n"
s7_body = doc.split(s7_head, 1)[1].split("\n---\n", 1)[0]
assert s7_body.startswith("No score effect;") and s7_body.endswith("\n")
anchorG = "## Appendix G. A scalar toy of the oracle noise bias"
CUT_PASTE(
    "M8",
    "§7 body → new Appendix F.10 (verbatim)",
    s7_body,
    "No score effect. Our κ3 birth's exact read costs 4 dense products per young source-layer [proved at n = 32–96]; the cheaper re-association reads 6–10 % wrong at n = 1024; a 3-product floor rests on an unmeasured premise [argument]. Full text: Appendix F.10.\n",
    anchorG,
    "### F.10 §7 in full: a per-source cost floor for our κ3 birth (moved verbatim from §7 in V31)\n\n",
    f"{V30} §7 (pointer = claims row 7 numbers)",
)
s7a_body = (
    line_starting("The score meters FLOPs, but the 120 s per-MLP wall cap prices memory traffic")
    + "\n"
)
CUT_PASTE(
    "M9",
    "§7A body → Appendix J, first paragraph (verbatim)",
    s7a_body,
    "The score meters FLOPs but the 120 s wall cap prices memory traffic, so extra exact Winograd levels became a knapsack priced in util per predicted second, which chose v110 (4.21e-9, 102.3 s max wall). Full text: Appendix J.\n",
    "The Phase 2 hard cap is 120 s of wall per MLP (zero-prediction fallback beyond it);",
    "*§7A as it stood in V30 (moved verbatim in V31).* ",
    f"{V30} §7A (pointer numbers from the moved paragraph)",
)

# §9 items 7 and 9 -> new F.11
i7 = line_starting("7. **Billing.** A rebill of v77_fuse") + "\n"
i9 = (
    line_starting("9. **Verification boundary.** v99, v100 and v101 as first submitted failed")
    + "\n"
)
assert doc.count(i7) == 1 and doc.count(i9) == 1
doc = doc.replace(i7, "7. **Billing and arena persistence:** Appendix F.11.\n").replace(
    i9, "9. **Verification boundary:** Appendix F.11 and B.5.\n"
)
f11 = (
    "### F.11 §9 items 7 and 9 in full (moved verbatim from §9 in V31)\n\n"
    + i7
    + "\n<!-- separate lists so that item 9 keeps its number -->\n\n"
    + i9
    + "\n"
)
assert doc.count(anchorG) == 1
doc = doc.replace(anchorG, f11 + anchorG)
rows.append(
    (
        "M10",
        "move",
        "§9 items 7 (billing, arena persistence) and 9 (verification boundary) → new Appendix F.11 (verbatim; an HTML comment line between them is rendering-only, so that pandoc keeps the number 9); one-line pointers left",
        i7 + i9,
        "7. **Billing and arena persistence:** Appendix F.11.⏎9. **Verification boundary:** Appendix F.11 and B.5.",
        f"{V30} §9",
    )
)
R(
    "X1",
    "B.5 cross-reference after M10",
    "The first submissions of v99–v101 failed on the grader (§9, item 9);",
    "The first submissions of v99–v101 failed on the grader (§9, item 9; full text in Appendix F.11);",
    "M10",
)
R(
    "X2",
    "summary pointer to the consistency note after M5",
    "A consistency note on the leader's raw MSE is in §7C.",
    "A consistency note on the leader's raw MSE is in Appendix F.7.",
    "M5",
)
R(
    "X4",
    "§10 short text after M6",
    "whose GLM-5.3 proposed §7C's copula idea)",
    "whose GLM-5.3 proposed the copula idea of Appendix F.7)",
    "M6",
)
R(
    "G22",
    "§8 Exceptions",
    "G-RB144, the gate behind v112, is a further exception: it was registered after G-RB143's FIT12 and VALID-20 reads, with G-RB143's failed cost clause dropped",
    "The gate behind v112 is a further exception: it was registered after the end-to-end gate's FIT12 and VALID-20 reads, with that gate's failed cost clause dropped",
    "id removal",
)
R(
    "G23",
    "§9 item 3",
    "bootstrap intervals exist only for the G-RB119 oracles.",
    "bootstrap intervals exist only for the §3 oracles.",
    "id removal",
)
R("G24", "§9 item 4", "the G-RB119 oracles on six.", "the §3 oracles on six.", "id removal")

# ---------------------------------------------------------------- word budget, round 3 (V31): summary supporting bullets, §5 tail, §6 ablation paragraph
sup_head = "### Supporting results\n\n"
sup_body = doc.split(sup_head, 1)[1].split(
    "\n**What did not work, and what we would try next:**", 1
)[0]
assert sup_body.startswith("- **Head-to-head against the organizers' code**") and sup_body.endswith(
    "\n"
)
CUT_PASTE(
    "M11",
    "Summary 'Supporting results' bullets (head-to-head, why κ3, proofs list) → new Appendix F.12 (verbatim); three one-line pointers left",
    sup_body,
    "- **Head-to-head against the organizers' code:** claim 9 and B.0 item 8b (row 5 of the table above).\n"
    "- **Why κ3 is necessary:** a K = 2 chain from first principles is 167× worse than our shipped chain on the same net (Appendix F.7).\n"
    "- **Proofs with falsifiers:** P1–P4 (Appendix P).\n"
    "- In full: Appendix F.12.\n",
    anchorG,
    "### F.12 Supporting results as listed in the V30 two-page summary (moved verbatim in V31)\n\n",
    f"{V30} two-page summary (pointer number 167× from the moved bullet)",
)
v_line = line_starting("**Verdict, worded to what was tested.**")
tail_start = "Raising the pair-series (Hermite) order not helping agrees with"
v_tail = v_line[v_line.index(tail_start) :]
assert v_tail.endswith("(il.miscusi, forum 18248).")
CUT_PASTE(
    "M12",
    "§5 'Verdict' paragraph, last two sentences (organizers' asymptotic-series remark; two untested published candidates) → Appendix I.2 (verbatim)",
    v_tail,
    "The organizers' remark on the asymptotic Hermite series, and two published candidates we have not tested, are in Appendix I.2.",
    "## Appendix J. Meter versus wall: table and mechanism",
    "*From §5 (moved verbatim in V31).* ",
    f"{V30} §5",
)
abl = line_starting("**On the ablation code.** `submissions/v58_ne_noclose/`") + "\n\n"
CUT_PASTE(
    "M13",
    "§6 'On the ablation code' paragraph → Appendix B.1, beside the ablation figure (verbatim)",
    abl,
    "**On the ablation code:** Appendix B.1.\n\n",
    "![Figure 2 — closure OFF/ON on v58_ne]",
    "",
    f"{V30} §6",
)

# ---------------------------------------------------------------- word budget, round 4 (V31): §7C pointers collapsed; abstract and §1.2 trimmed
c7_old = doc.split(
    "## 7C. Final-layer hypersensitivity to coherent σ² error (supporting; measured 2026-10-21)\n\n",
    1,
)[1].split("\n---\n", 1)[0]
c7_new = (
    "Summary result 2 states this finding. These arms ran on v112's chain (v117_kd's parent; the f64 FIT12 twin, 12 FIT nets, head frozen) or on the 3-net meter that selected v117_kd (§7B); "
    "the K = 2 comparison is against v117_kd itself (f32 port, net 1340). The arms, all in Appendix F.7, are: the coherent σ² scale (VSE1); "
    "the knob scan, including Pepper's off-diagonal compensator (CMP, #327838 p.9); old-tier damping; the reading [inference] with its consistency note on the leader's raw MSE; "
    "why κ3 is necessary (K = 2 from first principles); and what we would try next.\n"
)
R(
    "C7",
    "§7C: the five one-line pointers (and the intro sentence, kept verbatim) collapsed into one paragraph; G-RB154 dropped",
    c7_old,
    c7_new,
    f"{V30} §7C and moves M5, M6 (no number added)",
)
R(
    "A2",
    "Abstract, engineering sentence: wall times trimmed (they stay in §7B, B.0 item 8 and B.4)",
    "took graded adjusted 4.21e-9 → 4.01e-9 (v112_sb, AIcrowd #337384, 0 failed, grader wall 87.2 s mean / 95.6 s max; §7B). Two constants on top of it give our corresponding submission, v117_kd #337578 (4.00e-9, 0 failed, grader max wall 89.2 s; §7B, B.4).",
    "took graded adjusted 4.21e-9 → 4.01e-9 (v112_sb, AIcrowd #337384, 0 failed; §7B). Two constants on top of it give our corresponding submission, v117_kd #337578 (4.00e-9, 0 failed; §7B, B.4).",
    f"{V30} abstract (cut only)",
)
R(
    "N1b",
    "§1.2 credit sentence shortened (detail is in I.1)",
    "Others handled Monte-Carlo noise in their own oracles and references: Nurlanggs measured his oracle's noise floor, Artyom_Mazur subtracts oracle noise measured from two seeds in his substitutions, kai_leal_gonzalez estimated his truth reference's noise and hyojun_kwon split-half-corrected his, and James Henry (Phase 1) decomposed his probe noise (pages in Appendix I.1).",
    "Others handled Monte-Carlo noise in their own oracles and references (Nurlanggs, Artyom_Mazur, kai_leal_gonzalez, hyojun_kwon; James Henry in Phase 1); Appendix I.1 says what each did, with pages.",
    "N1 text, shortened",
)

# ================================================================ audit pass (V31_AUDIT.md)
AUDIT_START = len(rows)
AUD = "V31_AUDIT.md"
URL = "https://github.com/manderson240/arc-whitebox-phase2"
NEWNARROW = "a known-answer control, a 5× dose check and the measured size of the misreading (0.776 vs 0.511)"
R(
    "AU1",
    "Abstract (NOV-1: narrow claim = control, dose check, measured size; toy attribution clarified)",
    "two-half extrapolation of the MC noise in the injected quantity, checked by a known-answer control (Appendix G: a 21-line scalar toy), and the measured size of the misreading (0.776 vs 0.511);",
    "a known-answer control (0.305 → 0.002; scalar toy, Appendix G), a 5× dose check, and the measured size of the misreading (0.776 vs 0.511);",
    f"{AUD} NOV-1; dose check: §3 check (i) (1.840/1.839 vs 1.841); no participant PDF in research/forum/pdfs_20261021|22 reports a dose check",
)
R(
    "AU2",
    "Summary criteria line (i) (NOV-1)",
    "ours is two-half extrapolation of the MC noise in the injected quantity, checked by a known-answer control, and the measured size of the misreading (0.776 vs 0.511),",
    "ours is " + NEWNARROW + ",",
    f"{AUD} NOV-1",
)
R(
    "AU3",
    "Summary result 1 (NOV-1)",
    "Ours, narrowly: two-half extrapolation of the MC noise in the injected quantity, checked by a known-answer control, and the measured size of the misreading (0.776 vs 0.511).\n",
    "Ours, narrowly: " + NEWNARROW + ".\n",
    f"{AUD} NOV-1",
)
R(
    "AU4",
    "Claims box row 1 (NOV-1)",
    "ours, narrowly: two-half extrapolation of the MC noise in the injected quantity, its known-answer control and the measured size of the misreading. |",
    "ours, narrowly: its known-answer control, a 5× dose check and the measured size of the misreading. |",
    f"{AUD} NOV-1",
)
R(
    "AU5",
    "§1.2 (NOV-1)",
    "**Ours, narrowly and not as a first:** two-half extrapolation of the MC noise in the injected quantity, checked by a known-answer control, and the measured size of the misreading (0.776 vs 0.511; §3).",
    "**Ours, narrowly and not as a first:** a known-answer control, a 5× dose check and the measured size of the misreading (0.776 vs 0.511; §3).",
    f"{AUD} NOV-1",
)
R(
    "AU6",
    "§3 'Provenance first' (NOV-1)",
    "What this section adds, narrowly and not as a first, is two-half extrapolation of the MC noise in the injected quantity, checked by a known-answer control, and the measured size of the misreading (0.776 vs 0.511);",
    "What this section adds, narrowly and not as a first, is " + NEWNARROW + ";",
    f"{AUD} NOV-1",
)
R(
    "AU7",
    "Appendix I.1 Mazur bullet (NOV-1b: unsourced 'unlike his subtraction' clause deleted; Appendix H calls the two equivalent)",
    "Ours, narrowly: two-half extrapolation of the MC noise in the injected quantity, checked by a known-answer control, and the measured size of the misreading (0.776 vs 0.511); unlike his subtraction it is a two-point extrapolation with a 5× dose check.",
    "Ours, narrowly: " + NEWNARROW + ".",
    f"{AUD} NOV-1b; Appendix H method box (3)",
)
R(
    "AU8",
    "Summary result 2 heading (NOV-2: 'new' removed)",
    "(new, §7C Final-layer hypersensitivity).",
    "(§7C Final-layer hypersensitivity).",
    f"{AUD} NOV-2",
)
R(
    "AU9",
    "Summary result 2 [inference] bullet (NOV-2: Mazur p.18 credit)",
    "Related: Artyom_Mazur's Proposition 1",
    "Artyom_Mazur reports an analogous parabola for a coherent scale of all layers' variances (p.18: c = 1e-3 costs ×200) and a similar reading; his Proposition 1",
    f"{AUD} NOV-2; {SRC_MAZ} p.18 (a); forum 18249 posted 2026-10-16T15:17Z, unedited (Discourse version 1)",
)
R(
    "AU10",
    "Appendix F.7 'Reading [inference]' (NOV-2 credit, optional part)",
    "is a cousin of our noise correction (Figure 1).",
    "is a cousin of our noise correction (Figure 1). Artyom_Mazur (forum 18249, p.18) reports an analogous parabola for a coherent scale of all layers' variances and a similar coherent/incoherent reading.",
    f"{AUD} NOV-2; {SRC_MAZ} p.18 (a)",
)
for eid, where in (("AU11", "Summary result 3"), ("AU12", "§3 'The principle'")):
    old = "Artyom_Mazur (forum 18249, item 4, p.2: exact variance alone made the result worse, ×1.09, while"
    assert doc.count(old) == 2 if eid == "AU11" else doc.count(old) == 1
    i = doc.find(old)
    doc = (
        doc[:i]
        + "Artyom_Mazur (forum 18249, item 4, p.2: exact variance alone can make the result worse (×1.09, one net), while"
        + doc[i + len(old) :]
    )
    rows.append(
        (
            eid,
            "edit",
            where + " (×1.09 hedge restored; first remaining occurrence)",
            old,
            "Artyom_Mazur (forum 18249, item 4, p.2: exact variance alone can make the result worse (×1.09, one net), while",
            f"{AUD} S6/S7; {SRC_MAZ} p.2 item 4 ('can make'), p.4 (c) (×1.09 on one network, all neurons)",
        )
    )
R(
    "AU13",
    "Claims box row 2 (×1.09 hedge)",
    "exact variance alone ×1.09, with κ3 and κ4 ×0.12;",
    "exact variance alone up to ×1.09, with κ3 and κ4 ×0.12;",
    f"{AUD} C2; {SRC_MAZ} p.2, p.4 (c)",
)
R(
    "AU14",
    "Summary criteria line (ii)",
    "and names its file;",
    "and names its gate or file where one exists;",
    f"{AUD} S1 (claims rows 5, 7 name none)",
)
R(
    "AU15",
    "§1.2 search scope",
    "and the forum prose cited below)",
    "and the forum prose and PDFs cited in Appendix I.1)",
    f"{AUD} N1b/X-3 (V31 credits read from PDFs, Appendix I intro)",
)
R(
    "AU16",
    "Appendix C.1 snapshot citation (sha256 restored after S5)",
    "Grader feed snapshot 2026-10-21 20:34 UTC (`writeup/proofs/p2_rows_20261021T2034Z.json`): leader",
    "Grader feed snapshot 2026-10-21 20:34 UTC (`writeup/proofs/p2_rows_20261021T2034Z.json`, sha256 321f94476625cd18ac7f63a3fe726770139a9a81aafcf3e6c9d1ed3b604120c0): leader",
    f"{V30} S5 bullet (removed in V31); `sha256sum writeup/proofs/p2_rows_20261021T2034Z.json` re-run 2026-10-22, same hash",
)
R(
    "AU17",
    "Appendix I.1 Nurlanggs/Susupro bullet (PDF vs forum-post numbers reconciled)",
    "(forum 18252, p.23; the injections are on p.7).",
    "(forum 18252, p.23; the injections are on p.7); these are later lab-chain readings than the forum-post pair 0.610/0.508 in I.2.",
    f"{AUD} N7; {SRC_NURL} p.7 (lab chain without E1); research/forum/MINING_20261018.md line 16",
)
R(
    "AU18",
    "Appendix I.1 Nurlanggs bullet label",
    "(forum 18252; team NullPointer; prose):",
    "(forum 18252; team NullPointer; prose and PDF):",
    f"{AUD} X-4",
)
R(
    "AU19",
    "Appendix I.2 Nurlanggs truth-set paragraph (his p.7 conclusion added)",
    "His PDF measures that oracle's own noise floor, +4.2e-9 (forum 18252, p.23; I.1).",
    "His PDF measures that oracle's own noise floor, +4.2e-9 (forum 18252, p.23; I.1); he concludes his lever 'is not sample-noise tracking' (p.7).",
    f"{AUD} N9; {SRC_NURL} p.7",
)
R(
    "AU20",
    "Appendix K 'Uncertain' (his p.7 conclusion added)",
    "measures that oracle's own noise floor, +4.2e-9);",
    "measures that oracle's own noise floor, +4.2e-9; he concludes his lever 'is not sample-noise tracking', p.7);",
    f"{AUD} K1; {SRC_NURL} p.7",
)
R(
    "AU21",
    "Appendix K pointer (optional part)",
    "§7B's v117_kd paragraph, §7C,",
    "§7B's v117_kd paragraph (now Appendix F.7), §7C,",
    f"{AUD} K1; M4",
)
R(
    "AU22",
    "Appendix K pointer (optional part)",
    "proposed §7C's old-tier damping arm and its consistency note;",
    "proposed §7C's old-tier damping arm and its consistency note (now Appendix F.7);",
    f"{AUD} K1; M5",
)
R(
    "AU23",
    "Appendix I heading",
    "## Appendix I. Related work and credits (moved from §1A and §1.2)",
    "## Appendix I. Related work and credits (moved from the former §1A and §1.2)",
    f"{AUD} X-5 (§1A removed by N4)",
)
R(
    "AU24",
    "Summary heading (#16)",
    "## Two-page summary\n",
    "## Summary\n",
    f"{AUD} PDF row (summary spans PDF pp.1–4)",
)
# run-in lists: a blank line before each list that followed a non-blank line
for eid, prefix in (
    ("AU25", "**The principle, with its two measured instances.**"),
    ("AU26", "**What the table supports, and what it does not.**"),
    ("AU27", "**Pre-registration.** Every lever is a gate in"),
    ("AU28", "Per layer:"),
    ("AU29", "ARC's augmented K = 3 tracks η̃4"),
    ("AU30", "**Late gates (2026-10-19; each pre-registered"),
    ("AU31", "**Evidence ladder.**"),
    ("AU32", "No score effect; uncorrected lean f64 age-6 chain"),
):
    line = line_starting(prefix)
    old = line + "\n"
    j = doc.find(old) + len(old)
    nxt = doc[j : j + 3]
    assert doc.count(old) == 1 and (nxt.startswith("- ") or nxt.startswith("1. ")), (eid, nxt)
    doc = doc.replace(old, line + "\n\n")
    rows.append(
        (
            eid,
            "edit",
            "blank line before the list after '" + prefix[:50] + "' (PDF run-in fix)",
            old,
            line + "\n\n",
            f"{AUD} PDF row; rendering only, 0 words",
        )
    )
for eid, prefix in (
    ("AU35", "> **Measured performance impact on graded submissions.** Scores are"),
    ("AU36", "> **Recipe: how to run a first-order bias-corrected sampled-truth oracle**"),
    ("AU37", "> **Exchange rates we measured (one shape, one chain; priors, not laws).**"),
):
    line = line_starting(prefix)
    old = line + "\n"
    assert doc.count(old) == 1
    doc = doc.replace(old, line + "\n>\n")
    rows.append(
        (
            eid,
            "edit",
            "blank quoted line before the list inside the blockquote after '"
            + prefix[2:52]
            + "' (PDF run-in fix; found while verifying #15)",
            old,
            line + "\n>\n",
            "V31_AUDIT.md PDF row (same defect inside blockquotes, B.0, Appendix H recipe, Appendix J); rendering only, 0 words",
        )
    )
R(
    "AU33",
    "Appendix E, first line: public release URL",
    "## Appendix E. Reproduction\n\n",
    "## Appendix E. Reproduction\n\nRelease: "
    + URL
    + " (same files as arcwb_phase2_release_v30.zip; sha256 printed in RELEASE_ZIP.sha256 at the repo root)\n\n",
    "coordinator instruction (URL fixed in advance; at audit time 2026-10-22 the URL returned HTTP 404, so it is not yet public)",
)
R(
    "AU34",
    "Summary result 1 reproduce line: release URL (once)",
    "- From the release root: `python3 research/rb119/ci119.py`",
    "- From the release root (" + URL + "): `python3 research/rb119/ci119.py`",
    "coordinator instruction",
)

# ---------------------------------------------------------------- final read (2026-10-22)
FINAL_START = len(rows)
FRD = "final read 2026-10-22 (independent reader)"
R(
    "FR1",
    "Abstract: the control's numbers are §3's chain control, not the toy's (X-2 residue)",
    "(0.305 → 0.002; scalar toy, Appendix G)",
    "(0.305 → 0.002, §3; scalar toy, Appendix G)",
    f"{FRD}; research/rb119/ci119.json row var_k3_k4_h0 (0.305 → 0.002); `python3 -I writeup/oracle_bias_toy.py` prints corrected −0.000/+0.000, never 0.305",
)
R(
    "FR2",
    "Appendix F.7 'Reading': the correction is not ours (§1.2), so not 'our noise correction'",
    "is a cousin of our noise correction (Figure 1).",
    "is a cousin of the noise correction we apply (Figure 1).",
    f"{FRD}; §1.2 'The correction is not ours'",
)
R(
    "FR3",
    "Appendix I.1 Mazur bullet: same wording fix",
    "This is the closest public work to our correction:",
    "This is the closest public work to the correction we apply:",
    f"{FRD}; §1.2 'The correction is not ours'",
)
R(
    "FR4",
    "Appendix I.1 Mazur bullet: ×1.09 hedge as in result 3 and claims row 2",
    "(exact variance alone ×1.09, variance, κ3 and κ4 together ×0.12; summary result 3)",
    "(exact variance alone can make the result worse, ×1.09 on one net; variance, κ3 and κ4 together ×0.12; summary result 3)",
    f"{FRD}; {SRC_MAZ} p.2 item 4 ('can make'), p.4 (c) ('harmful on one network (×1.09 …)')",
)
R(
    "ZR1",
    "Appendix E first line: release zip renamed to v31",
    "(same files as arcwb_phase2_release_v30.zip;",
    "(same files as arcwb_phase2_release_v31.zip;",
    "coordinator instruction (the release now carries V31)",
)
R(
    "ZR2",
    "Appendix E 'Reproduce in 5 minutes': zip, sha256 file and reproduction record renamed to v31",
    "relative to the root of `arcwb_phase2_release_v30.zip` (its sha256 is in `writeup/arcwb_phase2_release_v30.zip.sha256` next to the zip;",
    "relative to the root of `arcwb_phase2_release_v31.zip` (its sha256 is in `writeup/arcwb_phase2_release_v31.zip.sha256` next to the zip;",
    "coordinator instruction",
)
R(
    "ZR3",
    "Appendix E 'Reproduce in 5 minutes': reproduction record for the v31 zip",
    "`writeup/V30_REPRO_FINAL.md`, next to the zip (not in it), records",
    "`writeup/V31_REPRO_FINAL.md`, next to the zip (not in it), records",
    "writeup/V31_REPRO_FINAL.md (written by this pass from a fresh unzip of the v31 zip)",
)
R(
    "ZR4",
    "Appendix E 'Re-running the corresponding submission': fe907c00… was an earlier build of the release, not of the v31 zip",
    "(an earlier build of this zip, sha256 fe907c00",
    "(an earlier build of the release, sha256 fe907c00",
    "writeup/V30_REPRO_FINAL.md (fe907c00… is a V30 build); `diff -rq` of submissions/ in the v30 and v31 unzips (V31_REPRO_FINAL.md)",
)
R(
    "ZR5",
    "Appendix E paths paragraph: release zip renamed to v31; V29 and V30 both shipped as history",
    "the code release that accompanies this write-up, `arcwb_phase2_release_v30.zip`.",
    "the code release that accompanies this write-up, `arcwb_phase2_release_v31.zip`.",
    "coordinator instruction",
)
R(
    "ZR6",
    "Appendix E paths paragraph: history files",
    "the V29 write-up as history, and `SOURCES.md`",
    "the V29 and V30 write-ups as history, and `SOURCES.md`",
    "writeup/build_release.py FILES (PHASE2_WRITEUP_V29/V30 .md/.pdf and their changelogs)",
)

DST.write_text(doc)

NOTES = """
## Notes for the independent checker

- **Deviation from the benchmark (V30_BENCHMARK.md G1/S2).** The benchmark says no Phase 2 PDF corrects the noise of the injected quantity. Artyom_Mazur's PDF does something close: every oracle substitution uses two independent 10⁷-sample seeds "so that the oracle's own noise can be measured and subtracted" (p.3–4), a substitution misread because of coherent oracle noise is reported (p.19, N50), and a substitution payoff is "noise-corrected two ways" (p.20). V31 therefore states the brief's novelty phrase only as a description of what we did ("narrowly and not as a first"), deletes V30's "A literature search found no prior application …" sentence (§1.2), and credits Mazur as the closest public work (I.1). What remains ours (after the audit pass, AU1–AU7): the known-answer control (0.305 → 0.002), the 5× dose check (no participant PDF we read reports one), and the size measured in our chain (0.776 vs 0.511); the two-half form itself is equivalent to Mazur's two-seed subtraction (Appendix H), so it is not claimed. [AUN1]
- **Relatedness checks (brief item 1, last bullet).** Mazur item 4 (p.2) is the compensation principle: added beside summary result 3, claims row 2 and §3. Mazur Proposition 1 (p.19) is the coherent-plus-independent structure behind result 2's [inference]: added. The closer result, his p.18 (a) variance-scale parabola with a coherent/incoherent reading, was missed in the first pass and credited in the audit pass (AU8–AU10). [AUN2] abhimanyu_singh (forum 18264, prose) is adjacent, not the same object (iid noise on D21/D3 slice read-outs at n = 256, plus a bias/variance asymmetry): added with that scope stated. None skipped.
- **Header interpretation.** The competition/participant line is kept; the bold lineage paragraph became the one-line header (H1) and moved verbatim to B.1 (H2).
- **Renumbering applied inside moved text.** F0b (Figure 1 reference) sits in the §7C 'Reading' moved by M5; F3a (Figure 2 reference) sits in the §6 ablation paragraph moved by M13; K1 edits the 'Uncertain' line after M2. Every other moved line is byte-identical to V30 (checked line by line), except: M1 demotes two headings (### → ####), M10 inserts a rendering-only HTML comment, L0 removes the port-bars pointer bullet from M3's block before the move, and F0b also adds the page '(p.9)'; the audit pass then edits moved text in AU10, AU17, AU20–AU22, AU31 and AU32. [AUN3]
- **G-RB ids left in main-text prose:** the Terms definition, the §2 evidence tag "[measured; G-RB85 row 10a]" (no section holds that row), the §8 ledger description, a grep command in summary result 3, and the Figure 1 caption's "Gate:" line. Tables (claims box, §3, §4) keep their ids by design.
- **Figures.** Figure 1 = V30 F0 (summary, after result 1); Figure 2 = F3 (B.1); Figure 3 = F2 (moved from §2 to new F.9 with a fuller caption built from §2's text); Figure 4 = F6 (Appendix H). "F0 and K0" (old-tier sites) and appendix sections F.0/F.3/F.7 are not figures and were not renamed.
- **Interpretations.** The brief's narrow novelty phrase went into summary result 1 (where the noise result lives), the abstract, §1.2, §3, claims row 1, criteria line (i) and I.1; summary result 3 received the Mazur item-4 credit and lost "plus the noise-corrected reading" (that claim is result 1's). The benchmark said the coincidence note also lives in C.1; it does not (grep), so after S5 and M5 it lives only in Appendix F.7, with a pointer from summary result 2.
- **Cuts and moves beyond the brief, made for the 7,500-word target:** S2, L0, N4, A2, N1b, C7 and M3–M13. Main text ends at __WC__ words after the audit pass and the final read (audit pass: 7,481; first pass: 7,488, not the 7,492 stated before the audit). [AUN4]
- **Inherited rendering.** A list directly after a bold line (the §7B ladder and the §7 body, now in F.7 and F.10) renders as run-in text, as in V30; left verbatim.
- **No new measured claims.** The graded-impact table copies B.0 / claims row 9; the only arithmetic is V30's own −19.7 %.
"""

# ---------------------------------------------------------------- changelog
main_v30 = SRC.read_text().split("\n## Appendix A")[0]
main_v31 = doc.split("\n## Appendix A")[0]
wc = lambda s: len(s.split())
out = [
    "# V31 changelog (from PHASE2_WRITEUP_V30.md, which is frozen and unchanged)",
    "",
    "Built 2026-10-22 by a Claude Opus 5.5 agent with `writeup/make_v31.py` from `PHASE2_WRITEUP_V30.md`, following `V30_BENCHMARK.md` §4 and the user's V31 brief. "
    "Every edit asserts that its old text occurs exactly once before it is applied; moves cut a block and paste the identical string (headings demoted where stated). "
    "No number was added that is not in V30 or in the cited source file. Rows: id | where | old → new | source.",
    "",
    f"**Length** (`wc`-style word split, text above `## Appendix A`): V30 {wc(main_v30)}, V31 {wc(main_v31)}. Whole document: V30 {wc(SRC.read_text())}, V31 {wc(doc)}.",
    "",
]
for k_, (eid, kind, where, old, new, source) in enumerate(rows):
    if k_ == AUDIT_START:
        out += [
            "",
            "## Audit pass (V31_AUDIT)",
            "",
            "Applied 2026-10-22 after the independent fact-check `writeup/V31_AUDIT.md` (its 16 fixes, the optional parts included) and the coordinator's release-URL instruction. The notes below were corrected in the same pass (AUN1–AUN4).",
            "",
        ]
    if k_ == FINAL_START:
        out += [
            "",
            "## Final read",
            "",
            "Applied 2026-10-22 by an independent reader (a Claude Opus 5.5 agent that did not author the text) after checking the 15 audit-pass fix items against the participant PDFs (prose only), V30, calibration and the ledger, and renaming the release zip to v31 (FR = final-read fix, ZR = zip rename).",
            "",
        ]
    o = old.replace("\n", "⏎")
    n = new.replace("\n", "⏎")
    if kind == "move":
        out.append(
            f"- **{eid}** (move) | {where} | moved block: '{o}' | left in place: '{n}' | source: {source}"
        )
    else:
        out.append(f"- **{eid}** | {where} | old: '{o}' | new: '{n}' | source: {source}")
LOG.write_text("\n".join(out) + "\n" + NOTES.replace("__WC__", f"{wc(main_v31):,}"))
print("main text words V30", wc(main_v30), "V31", wc(main_v31), "| edits", len(rows))
