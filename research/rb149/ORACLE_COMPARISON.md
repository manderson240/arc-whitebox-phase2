# rb149 ORACLE_COMPARISON - ours (v112_sb, shipped) vs ARC reference SIMPLE factorized K=3 (MIT)

Nets: 8 VALID-split nets (10 11 13 16 18 20 27 28; research/lc/split.json), official-format He n=1024 L=16, truth = 1e9-sample official mini refs. No TEST nets.
Ours: `eval_port.py submissions/v112_sb` (the shipped f32 estimator under the flopscope meter). ARC: `arc_valid.py` (research/rb149/ref, f32, factor=True, k_max=3, no fitted constants, ~7 s/net on the idle box).
Noise correction: the stored truth is a single 1e9-sample mean (no A/B halves exist), so the correction is analytic: MSE_true = MSE_obs - avg_variance/1e9 (about 8e-11, 0.4% of ours); identical for both arms, so paired differences are unchanged. (Over-sample split needs a fresh 1e9-scale MC and was not run.)
Caveat: v112_sb's learned corrector was fitted on FIT nets; VALID is held out of that fit.

| net | ours (v112_sb) | ARC simple K=3 | ours - ARC | 95% CI (neuron bootstrap) | ours budget % | ARC torch FLOPs (n^3 MAC units) |
|---|---|---|---|---|---|---|
| 10 | 2.268e-08 | 3.631e-08 | -1.36e-08 | [-1.7e-08, -1.0e-08] | 18.89 | 1520 |
| 11 | 2.308e-08 | 3.823e-08 | -1.51e-08 | [-2.0e-08, -1.1e-08] | 18.91 | 1520 |
| 13 | 2.135e-08 | 4.458e-08 | -2.32e-08 | [-2.8e-08, -1.9e-08] | 18.98 | 1520 |
| 16 | 1.829e-08 | 3.124e-08 | -1.30e-08 | [-1.6e-08, -9.5e-09] | 18.90 | 1520 |
| 18 | 2.234e-08 | 3.863e-08 | -1.63e-08 | [-2.1e-08, -1.2e-08] | 19.00 | 1520 |
| 20 | 2.093e-08 | 4.191e-08 | -2.10e-08 | [-2.6e-08, -1.7e-08] | 19.05 | 1520 |
| 27 | 1.674e-08 | 3.569e-08 | -1.90e-08 | [-2.3e-08, -1.5e-08] | 18.95 | 1520 |
| 28 | 2.052e-08 | 3.651e-08 | -1.60e-08 | [-2.0e-08, -1.2e-08] | 18.84 | 1520 |
| **mean** | **2.074e-08** | **3.789e-08** | **-1.71e-08** | net-bootstrap [-2.0e-08, -1.5e-08] | 18.94 | 1520 |

ratio of means ours/ARC = 0.547, net-bootstrap 95% CI [0.508, 0.586]; n nets = 8; wins for ours 8/8

FLOPs: ours = flopscope meter, 18.94% of 2^41 = 388 n^3 units (1 unit = n^3, so 2048 units = budget). ARC simple: torch FlopCounterMode (matmul/bmm only, counts 2*MACs) at n=64/128/192, exactly 3040 n^3 flops = **1520 n^3 MAC units at L=16** (74% of budget by that convention); the paper's Table 1 polynomial (30 L^2 + 39 L = 8304 n^3) is a different accounting (symmetric discount, own units) and is 5.5x larger; the true flopscope bill of ARC's code was not measured (it is torch, not flopscope). Adjusted-score proxy: ours 2.07e-8 x 0.189 = 3.9e-9; ARC 3.79e-8 x 0.74 = 2.8e-8 (7x worse).
Reading: at about 1/4 of ARC's matmul cost our chain has 0.55x the final-layer MSE (ratio CI [0.51, 0.59], 8/8 nets). Earlier net-9000 comparison (ref-noise-limited, fitted AUG=off 3.9e-8 vs ARC 4.9e-8) pointed the same way.

Incidents: (1) the 19:28-19:37Z rb149 jobs (ours-nok4, arc-simple, ours-aug, arc-aug, scale) ran via bg.sh without timing_lock.sh: my error; all later jobs used timing_lock with TIMING_LOCK_SHARED_RE='rb149/'. (2) rb149-valid-arc (rc=1) and -arc2 (rc=1) died with a torch allocator error: the first because torch FlopCounterMode retained tensors under ulimit -v 14 GB, the second from heap fragmentation running 8 nets in one process under the same cap alongside the other job; fixed by one process per net, MALLOC_ARENA_MAX=2, ulimit -v 16 GB (a 2 GB deviation from the 12 GB rule). (3) `rebuild/srcchain_aug.py` crashes under AUG=arc when QCOEF is unset (`Bt["Q"]` branch lost its guard in the G-RB34 edit); not patched in rebuild/; patched copy `srcchain_aug_fix.py` here.

## HELD-OUT 1300-1307

Official full-split nets (research/full/data; HELD-OUT-40 of G-RB130: never in any fit/selection; 1e9-sample truth; not TEST). Same scripts adapted to the full-split path (`eval_port_full.py`, `arc_heldout.py`, `compare_heldout.py`), same analytic noise correction (avg_variance/1e9 from each truth file), one process per net, ulimit -v 12000000 (12 GB sufficed for both arms), all jobs bg.sh + timing_lock COMPUTE (shared).

| net | ours (v112_sb) | ARC simple K=3 | ours - ARC | 95% CI (neuron bootstrap) | ours budget % | ARC torch FLOPs (n^3 MAC units) |
|---|---|---|---|---|---|---|
| 1300 | 2.152e-08 | 4.060e-08 | -1.91e-08 | [-2.4e-08, -1.5e-08] | 18.95 | 1520 |
| 1301 | 1.962e-08 | 2.737e-08 | -7.74e-09 | [-1.1e-08, -4.8e-09] | 18.95 | 1520 |
| 1302 | 1.967e-08 | 3.269e-08 | -1.30e-08 | [-1.6e-08, -9.8e-09] | 18.96 | 1520 |
| 1303 | 2.008e-08 | 4.180e-08 | -2.17e-08 | [-2.6e-08, -1.7e-08] | 18.98 | 1520 |
| 1304 | 2.244e-08 | 3.695e-08 | -1.45e-08 | [-1.9e-08, -1.1e-08] | 18.92 | 1520 |
| 1305 | 1.859e-08 | 3.824e-08 | -1.96e-08 | [-2.4e-08, -1.5e-08] | 19.00 | 1520 |
| 1306 | 2.382e-08 | 5.122e-08 | -2.74e-08 | [-3.3e-08, -2.2e-08] | 18.99 | 1520 |
| 1307 | 1.999e-08 | 4.259e-08 | -2.26e-08 | [-2.7e-08, -1.8e-08] | 18.89 | 1520 |
| **mean** | **2.072e-08** | **3.893e-08** | **-1.82e-08** | net-bootstrap [-2.2e-08, -1.4e-08] | 18.96 | 1520 |

ratio of means ours/ARC = 0.532, net-bootstrap 95% CI [0.488, 0.591]; n nets = 8; wins for ours 8/8

Held-out result matches the VALID result (ratio 0.53 vs 0.55; 8/8 nets each), so the VALID-rung selection did not inflate the comparison.
