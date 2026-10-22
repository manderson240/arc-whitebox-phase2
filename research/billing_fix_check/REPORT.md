# Billing-fix check (flopscope PRs #286-#294, #299-#303 vs current)  2026-10-13

Question: do designated submissions bill the same FLOPs under the proposed flopscope billing fixes?

## Method
- Current = flopscope 0.12.1 at main 80e72a92. Verified the starter-kit venv install equals `flopscope/src/flopscope` of main (diff: only an unused data/weights.json extra in the repo).
- Proposed = git worktree `fs_merged`: main + PR heads (refs/pull/N/head) merged in order 286,287,288,289,290,291,292,293,294,299,300,301,302,303 (#294 after #288). One conflict, #302 vs #286 in `linalg/_properties.py` (matrix_rank) + cost-model.md: resolved by keeping both (hermitian SVD cost and per-tolerance-pair compares). matrix_rank is not used by any picks.
- Two separate venvs (`venv_main`, `venv_merged`, editable installs of the respective worktrees; whest-starterkit/.venv untouched), OMP_NUM_THREADS=4.
- `bill.py` = in-process `Estimator.predict` under `BudgetContext(2**41)` (same as lever46/cmp.py), FIT nets 0,2,4 (no TEST nets), full op_log dumped per run (res/*.json).

## Result (total billed FLOPs, util = flops/2^41)
| submission | net | FLOPs current | FLOPs proposed | util | delta | ops (n) |
|---|---|---|---|---|---|---|
| v77_fuse | 0 | 474,409,235,578 | same | 0.21574 | 0 | 14281 |
| v77_fuse | 2 | 472,923,896,378 | same | 0.21506 | 0 | 14281 |
| v77_fuse | 4 | 474,531,266,058 | same | 0.21579 | 0 | 14281 |
| v46_y5c | 0/2/4 | 551,081,600,119 | same | 0.25060 | 0 | 12862 |
| v78_p02 | 0 | 475,943,374,794 | same | 0.21643 | 0 | 15283 |
| v78_p02 | 2 | 473,828,504,810 | same | 0.21547 | 0 | 15283 |
| v78_p02 | 4 | 476,332,832,058 | same | 0.21661 | 0 | 15283 |

All 9 (submission, net) pairs: op_log (name, subscripts, shapes, flop_cost, per op) is element-wise identical, and the output vector sum is bit-equal. Relative change 0.000 %; no op accounts for any change.

## Control (harness can see a difference): `control.py`, `control2.py`
| snippet | current | proposed |
|---|---|---|
| np.var(x[8], mean=zeros(1000,1)) (#286) | 2,080 | 66,016 |
| add((64,1),(64,1), out=(64,512)) (#288) | 128 | 65,536 |
| add(ones4, ones4, where=bool(100,4)) (#288) | 424 | 1,216 |
| isclose with array rtol (#301) | RuntimeError (bug in current) | 5,616 |
| ufunc out= same shape as result; polyval 1-elem | 256 / 16 | 256 / 16 (unchanged, as expected) |

## Verdict
SAFE: identical to the FLOP on all tested pairs. Caveat: 3 FIT nets per submission (v46_y5c bills identically on every net, so more nets add nothing; the other two vary by net only through data-dependent paths, none of which touch the changed ops). Not covered: PR heads moving after 2026-10-13 and the #302/#286 manual conflict resolution (irrelevant to used ops).
