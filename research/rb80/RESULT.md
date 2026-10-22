# G-RB80 — machine check of the §11.1 per-source floor theorem (small n)

Pre-registration and full result: `research/R2_GO_NOGO.md` (G-RB80, 2026-10-12T18:23:12Z / result stamp in the ledger).
Code: `rb80_floor_check.py`; rows: `rb80_results.jsonl`; pooled numbers: `summary.txt`; log: `run.log`.
Reproduce: `ulimit -v 4000000; OMP_NUM_THREADS=2 python3 rb80_floor_check.py --n 32 64 96 --L 6 --seeds 0 1 2` (0.2 s).

| statement (§11.1 / LENS_F §2) | machine result |
|---|---|
| A_s^l = P_s^l a_s exactly | max rel 1.0e-15 |
| exact read = 4 dense n³ per young source-layer | 4 on every age (merged 2-contraction form == srcchain read_block to 1.1e-16) |
| diag+rank-r form: "3 + 4r/n, saving only for r < n/4" | **2 + 4r/n** (thin units == 4r/n exactly; break-even r < n/2); algebra exact to 6.5e-16 |
| read error at r/n = 1/8, 1/4, 1/2, 1 (summed ages 1–4) | 0.28–0.46, 0.16–0.29, 0.106–0.168, ≤ 3e-15 — monotone, ≫ 2 % wherever the form saves anything |
| "read amplifies leg norm error ×1.5–2" | 0.74–1.88, median 1.18 at n ≤ 96 (relA = √dropped-energy to 0.80–1.18) — not reproduced; keep as [measured, n = 1024] |
| falsifier: slice-only 2-product source (a_s diagonal) | off read error 1.000000000000 (all rows) |
| falsifier: leg-optimal diagonal birth P d(c) | 0.926–0.993 |
| Khatri–Rao: (GM)∘(GN) does not stay rank r | rank = min(n, r(r+1)/2): 3 / 10 / 36 at r = 2 / 4 / 8 |
