# G-RB86 — which part of the deep-layer var_z error: the mu mu^T term or the E[hh^T] term? — KILL

Pre-registered in PROGRESS.md (2026-10-14T17:37:06Z). FIT nets 0/2/4 only, v59_p05 f64 twin (rb85 `srcchain_rb85.py` + one new injection key), head ON, 1024x16. TEST never touched; nothing submitted; `submissions/` not edited; no participant code opened. Jobs were < 30 s each (no bg.sh needed).

## Definitions
- var_z,i = w_i^T Cov(h) w_i. Chain: Cov = Sig (its own covariance), carried mean mu_c, so own second moment M2_c = Sig + mu_c mu_c^T.
- (a) = (w_i.mu_t)^2 - (w_i.mu_c)^2, with mu_t = the 1e9-sample truth E[h_{l-1}] (exact, noise-free) and mu_c the chain's carried (post-head) mean at that point. (b) = e - (a), e = chain var_z - truth var_z.
- Noise handling as rb85: <e,e> = mean((c-A)(c-B)) over the two 2^22 MC halves (noise-debiased); <a,e> uses (a), which is noise-independent of the MC. <b,b> = <e,e> - 2<a,e> + <a,a>.
- Variant "raw": mu_c replaced by the pre-head closure mean (the mean that Sig is actually consistent with).

## 1. Energy shares, z-layers 8-15 (3 nets pooled, carried mean)
| z-layer | projection <a,e>/<e,e> (a / b) | E_a/<e,e> | E_b/<e,e> | share_a = E_a/(E_a+E_b) |
|---|---|---|---|---|
| 8 | 0.163 / 0.837 | 2.17 | 2.85 | 0.433 |
| 9 | 0.128 / 0.872 | 2.30 | 3.04 | 0.430 |
| 10 | 0.225 / 0.775 | 2.53 | 3.08 | 0.451 |
| 11 | 0.204 / 0.796 | 2.62 | 3.22 | 0.449 |
| 12 | 0.240 / 0.760 | 3.10 | 3.62 | 0.461 |
| 13 | 0.152 / 0.848 | 3.06 | 3.76 | 0.449 |
| 14 | 0.109 / 0.891 | 3.45 | 4.23 | 0.449 |
| 15 | 0.141 / 0.859 | 3.78 | 4.50 | 0.457 |
| **pooled** | **0.167 / 0.833** | 2.98 | 3.65 | **0.450** |

Per net pooled (projection a / share_a): net 0 0.077 / 0.438; net 2 0.246 / 0.462; net 4 0.135 / 0.443.
Raw (pre-head) mean variant, pooled: projection a 0.206, share_a 0.457 (per net 0.092/0.441, 0.300/0.471, 0.172/0.450).

Reading: (a) and (b) are each 3x LARGER than the total error and mostly cancel (the cross term is ~ -1.8 <e,e>): the chain's Sig and mu errors are anti-correlated, so the split is not additive in correctability. Under every reading (a) is below 60 %: 45 % (energy), 17 % (projection).

## 2. Arm 2 — inject var_z' = var_z + mu_z^2 - mu_z,truth^2 at z-layers 1-15 (chain's own second moment kept), head ON
Control (rerun here): 2.0420e-8 / 2.3868e-8 / 2.3660e-8 — nets 2, 4 bit-identical to rb85 map.jsonl; net 0 agrees to 4e-13 relative (2.041970624814814e-8 vs 2.041970624815546e-8; float-order nondeterminism, not a behavioral difference).

| arm | net 0 | net 2 | net 4 | pooled ratio |
|---|---|---|---|---|
| carried mean (spec) | 2.511 | 11.245 | 2.501 | **5.576** |
| raw pre-head mean | 3.110 | 13.988 | 2.802 | 6.824 |

The oracle noise is zero (all inputs 1e9 truth + deterministic chain), so these ratios are not noise-biased.

## 3. Verdict: KILL
Rule: OPEN needs (a) >= 60 % of energy AND arm-2 ratio <= 0.85. Measured (a) 45 % (17 % by projection) and arm-2 ratio 5.58 (>= 2.5 on every net). Both legs fail, in the wrong direction by 6.5x on arm 2. Correcting only the mean product breaks the cancellation with the chain's own second-moment error and makes the final error far worse, so the deep-layer var seat is a joint (mu, Sig) closure error, not a mean-product error. No cheap fix is described (rule: only if OPEN).

## Caveats / UNKNOWN
- The (a)/(b) split depends on which mean one calls "the chain's" (carried vs raw): both reported, same verdict.
- Whether a joint (mu, Sig) correction would help: UNKNOWN (not tested; outside the pre-registered question).
- Sanity: MC mu halves vs truth-derived mu_z differ by MC noise (2-5e-8 mean-square), consistent with 2^22 samples; chain mu error 1.2e-8 (l=8) to 4e-8 (l=15). Layer indexing: z-layer l reads E[h_{l-1}] (z-layer 0 mean = 0).

## Files
`rb86/srcchain_rb86.py` (rb85 twin + `varmu`/`varmuraw` injection), `run_rb86.py` (modes decomp | varmu | varmuraw), `analyze86.py`, `arms.jsonl`, `decomp.jsonl`, `shares.json`.
