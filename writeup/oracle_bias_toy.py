"""Scalar toy: Monte-Carlo noise in a sampled-truth oracle biases its reading.
A PERFECT oracle (true ratio 0, the known-answer control) leaves only truth noise, so its
reading is r = E[noise^2]/E[e^2], e = chain relative sigma^2 error (loss ~ squared error).
Constants from V27 s3: e has SD 5.6e-4 (z8), 1.5e-3 (z15); truth-noise SE 5e-4."""
import numpy as np

rng = np.random.default_rng(0)
M = 2_000_000
CHAIN_ERR = {"z8": 5.6e-4, "z15": 1.5e-3}
# V27 s3 gives 5e-4 as the SE of the MEAN of the two halves; the brief reads it as one half's.
for label, se_full in (("full-mean SE 5e-4", 5e-4), ("half SE 5e-4", 5e-4 / np.sqrt(2))):
    se_half = se_full * np.sqrt(2)
    print(f"-- {label}: half SE {se_half:.2e}, full SE {se_full:.2e}")
    for layer, eps in CHAIN_ERR.items():
        e = rng.normal(0, eps, M)                  # chain error, independent of truth noise
        nA, nB = rng.normal(0, se_half, (2, M))    # two independent truth halves
        base = np.mean(e**2)
        r_half = 0.5 * (np.mean(nA**2) + np.mean(nB**2)) / base
        r_full = np.mean(((nA + nB) / 2) ** 2) / base
        r_inf = 2 * r_full - r_half                # split-half extrapolation to zero noise
        print(f"{layer}: rho={se_full/eps:.2f}  r(half)={r_half:.3f}  r(full)={r_full:.3f}  corrected={r_inf:+.3f}")
