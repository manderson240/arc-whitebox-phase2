# Arena persistence: billing effect on the nominated builds (2026-10-18)

Script: predict() twice on ONE Estimator instance, local flopscope 0.12.1, which bills identically to 0.12.3 (G-RB-billing). Each predict runs inside its own BudgetContext.

| build | call 1 (net 0) util pt | call 2 util pt | Δ | reshape calls / pt, call 1 → call 2 |
|---|---|---|---|---|
| v101r_xp, net 0 twice | 20.0821 | 19.8490 | 0.2331 | 244 / 0.2332 → 30 / 0.0001 |
| v101r_xp, nets 0 then 2 | 20.0821 | 19.7838 | 0.2983 (includes the net difference) | same |
| v99r_rm, nets 0 then 2 | 20.5467 | 20.2482 | 0.2985 | 227 / 0.2025 → 30 / 0.0001 |

- The same-net Δ (0.2331 pt) equals the reshape bill of call 1 (0.2332 pt): the whole effect is view creation billed once per worker.
- That is 1.16 % of v101r's per-MLP bill, so the score is about 1.2 % lower than with views rebuilt on every call.
- Consistent with the grader feed: util 0.198 for #336941, against 0.2008 for a single local call.
- The v58-era estimate was 0.01–0.03 pt (G-RB52/53a). Later builds cache many more views (v98 max-shaped scratch views; v99 nested quadrant views; v100/v101 extra-level views).
- No data crosses MLPs. Contents are fully rewritten on every call; the G-RB53a NaN-overwrite test showed bit-identical output for the v58 era. Re-run 2026-10-18 on v101r_xp (`research/rebuild/warm/persist_probe.py submissions/v101r_xp 0 1`): 48 persistent scratch buffers (4399 MiB) poisoned with NaN after net 0; the 3 constant zero blocks are listed and not poisoned; net 1 on the reused instance is finite with max |reused − fresh| = 0.0. PASS. (A first ad-hoc probe of mine poisoned nothing, because flopscope arrays reject item assignment and my error handler swallowed it. It reported "bit-identical" from an instrument that never acted, so it was discarded; this result comes from the validated probe.)
- The starter-kit FAQ treats state that survives between predict() calls as an optimisation that must not affect correctness. Rules §5.5 invite a written question before relying on a technique. writeup/STAFF_LETTER.md is updated with these numbers; the participant sends it.
