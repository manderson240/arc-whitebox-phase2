# Compliance audit 2026-10-17 (read-only static audit; nothing executed)
Rules: AIcrowd/whest-starterkit@96e308c docs/concepts/allowed-code.md + CHANGELOG "Allowed code is now an explicit, enforced rule".
Builds: submissions/v90_al, v95_khs, v87_p02 (estimator.py ~1025 lines each; near-identical, differ only by constants and a few lines; line numbers below are the same in all three unless stated).

## 1. Imports (top-level only; zero imports inside functions)
- __future__ annotations (stdlib); pathlib.Path (stdlib)
- flopscope, flopscope as flops, flopscope.numpy as fnp (flopscope client API)
- whestbench.BaseEstimator, SetupContext, whestbench.domain.MLP (harness contract types, allowed)
- norm = flops.stats.norm (estimator.py:511) -> norm.pdf/norm.cdf (:739-740) come from flopscope's scipy-like namespace. No real scipy.
- Weights: Weights.from_file / LCWeights.from_file (:489, :497), classes subclass flopscope.Module (:86). Loading goes through flopscope. No real numpy, no np.load.
- No numpy/scipy/pickle/os/sys/gc import anywhere.

## 2. Forbidden constructs
No threading, subprocess, ctypes, cffi, os.system, multiprocessing, asyncio, concurrent. Only `_` attributes are the estimator's own `self._x` fields and local helpers (_buf, _big_view, _SW_*). No flopscope client/transport/accounting access. Public flops.as_symmetric only. `transport` in docstrings means math (kappa transport), not the flopscope transport.

## 3. Residual compute
No numeric Python loops over n=1024 data. Loops are range(depth/levels/k<=small), list comprehensions slicing fnp views and stacking, and 'for k in range(_KH)' style orchestration of fnp ops. Module-level _KH table (:83) is tiny constant data. Strassen scratch uses pooled fnp.empty buffers with out=; all arithmetic is fnp. PASS.

## 4. Provenance (grep: 504aldo / port / ported / transliterat)
No hit for "transliterat". "port" hits are only "port screen" / "port G-RB70" (our own internal screening, not porting other code), plus "ported to flopscope" at line 29 (our own v21_rb clean-room rebuild).
Hits naming other participants (all three builds unless noted):
- :24 "team 504aldo, thread 18218 S2.4: '7n/32 at age 7'" (a quoted rate law, used for _R_OLD2)
- :33 "the three accuracy steps team 504aldo DESCRIBED in forum thread 18218 ... cost structure re-derived from the prose"
- :37 "Credit: 504aldo (thread 18218) ... No participant code was read."
- :12 and :93 "Team Puffi #327725 write-up, eqs 2/3/C2/C3, credit theirs" (SSC closure, Weights.lam/qc; fitted on our own nets)
- v90_al and v95_khs only, :811: "G-RB103: al07 two-term (3,1) law ... (kai_leal_gonzalez forum #18246 prose; credit theirs)" - NOT in v87_p02.
Assessment: all are described as ideas from forum prose or write-ups, no code. Your rule is "no other participant's code", so none is a literal violation, but the docstring openly builds on 504aldo's, Puffi's and kai_leal_gonzalez's published methods. Needs your judgment for a "designated" build; v87_p02 is the cleanest (no kai_leal).

## 5. Other
- Packing: no bitwise/packed-boolean tricks found (grep). Quantization: none; dtype = module _DTYPE.
- Strassen matmul (depth 2-5) is algorithmic, metered through fnp, not a listed prohibition. Flagging only since "fair accounting" language bans accounting-driven tricks; it reduces real op count rather than packing.
- No compute-while-op-in-flight constructs (no callbacks, lazy objects). Data files are .npz only. Weights loaded in setup() from context.submission_dir.
- Residual 400 ms cap not checked (runtime, out of scope). Weights.npz differs v90 vs v95 (retuned), lc_weights.npz identical across v90/v95/v87.

## Verdict table
| check | v90_al | v95_khs | v87_p02 |
|---|---|---|---|
| 1 imports | PASS | PASS | PASS |
| 2 forbidden/private | PASS | PASS | PASS |
| 3 residual loops | PASS | PASS | PASS |
| 4 provenance (code) | PASS | PASS | PASS |
| 4 provenance (idea credit) | FLAG: 504aldo, Puffi, kai_leal | FLAG: same | FLAG: 504aldo, Puffi |
| 5 other | PASS | PASS | PASS |

## Addendum 2026-10-18T14:37Z: nominated builds v101r_xp #336941 and v99r_rm #336957
- Imports: `__future__`, `pathlib`, `whestbench`, `whestbench.domain`, `flopscope`, `flopscope.numpy` only. No ctypes/cffi/subprocess/threads/asyncio/numpy (grep hits are a docstring and `flopscope.numpy`). Parses under Python 3.10 (grader pin).
- Remote-mode gate PASS (research/rebuild/remote_check.py, flopscope-client 0.12.3; remote = local digest). Both graded on AIcrowd with failed 0 (4.18e-9, 4.28e-9).
- Changes since v98 are output-identical engineering (op batching, exact extra Winograd levels, varargs transpose). No new data files: weights.npz and lc_weights.npz are byte-copies of v98's.
- Verdict: PASS.
