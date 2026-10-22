"""PROOFS.md Theorem 5 (fixed-weight kurtosis identity) + Proposition 6 (self-averaging of g_l).

He-init nets with the SAME weights as the 6 coordinator caches (proto_r2.make_mlp seeds 1000..1005; kappa4 is not in the caches, so it is re-measured here), n=1024, L=16, x~N(0,I). Per layer l (1-based; z_l = h_{l-1} W_l):
  measured  g_l   = mean_i kappa4_x(z_i) / mean_i var_x(z_i)^2         (row-average over the n rows of W_l)
  identity  g_l*  = 3 [Var_x ||A||^2 - 2 tr C^2] / [(tr C)^2 + 2 tr C^2],  A = h_{l-1} - E h_{l-1}, C = Cov(h_{l-1})
Theorem 5 says E_w kappa4_x(w.a) = 3 s^4 [Var||A||^2 - 2 tr C^2] and E_w var_x(w.a)^2 = s^4 [(trC)^2 + 2 trC^2]
exactly (s^2 = 2/n), so g_l -> g_l* as the row-average concentrates.  Gate: |g_l - g_l*| <= 3 * (delta-method
std of the row-average) + MC noise, at every layer, every net.
Proposition 6: Var(g_l | earlier layers) ~ (1/n) Var_i(kappa4_i - g v_i^2)/(mean v^2)^2 (delta method);
reported against the observed across-net spread (which ALSO contains the earlier-layer fluctuation).

Everything is accumulated in ONE pass from the same samples (moments of z per neuron; ||a||^2, ||a||^4,
a ||a||^2, a, a^T a for the previous layer), so the identity and the direct measurement share MC noise.

--perturb : drop the "- 2 tr C^2" term from the numerator -> the identity must FAIL (it then predicts
            g_1 = 6 trC^2/((trC)^2+2trC^2) ~ 6/n = 0.006 at layer 1 where the truth is exactly 0).
"""

from __future__ import annotations

import sys
import time

import numpy as np


n, L = 1024, 16


def run_net(seed: int, Nx: int, chunk: int = 4096):
    rng = np.random.default_rng(seed)
    W = [(rng.standard_normal((n, n)) * np.sqrt(2.0 / n)).astype(np.float32) for _ in range(L)]
    S = np.zeros((L, 4, n))  # raw moments of z per neuron
    Sa = np.zeros((L, n))
    Saa = np.zeros((L, n, n))
    Sq = np.zeros((L, 2))  # sum ||a||^2, sum ||a||^4
    Saq = np.zeros((L, n))  # sum a * ||a||^2
    done = 0
    while done < Nx:
        b = min(chunk, Nx - done)
        a = rng.standard_normal((b, n)).astype(np.float32)
        for l in range(L):
            a64 = a.astype(np.float64)
            q = (a64 * a64).sum(1)
            Sa[l] += a64.sum(0)
            Saa[l] += a64.T @ a64
            Sq[l] += [q.sum(), (q * q).sum()]
            Saq[l] += (a64 * q[:, None]).sum(0)
            z = a @ W[l]
            z64 = z.astype(np.float64)
            p = z64.copy()
            for k in range(4):
                S[l, k] += p.sum(0)
                p *= z64
            a = np.maximum(z, 0.0)
        done += b
    N = Nx
    out = []
    for l in range(L):
        m1, m2, m3, m4 = S[l] / N
        v = m2 - m1**2
        k4 = m4 - 4 * m3 * m1 + 6 * m2 * m1**2 - 3 * m1**4 - 3 * v**2
        g = k4.mean() / (v**2).mean()
        # previous-layer activation statistics
        mu = Sa[l] / N
        C = Saa[l] / N - np.outer(mu, mu)
        Eq, Eq2 = Sq[l] / N
        Eaq = Saq[l] / N
        M2 = Saa[l] / N  # E[a a^T]
        # ||A||^2 = ||a||^2 - 2 a.mu + ||mu||^2 ;  E||A||^2 = trC ;  E||A||^4 from the accumulators:
        mm = mu @ mu
        E_A4 = (
            Eq2 - 4 * (mu @ Eaq) + 4 * (mu @ M2 @ mu) + 2 * mm * Eq - 4 * mm * (mu @ mu) + mm * mm
        )
        trC = np.trace(C)
        trC2 = (C * C).sum()
        varA2 = E_A4 - trC**2
        out.append(dict(g=g, k4=k4, v=v, varA2=varA2, trC=trC, trC2=trC2))
    return out


def main(perturb: bool) -> int:
    Nx = int(sys.argv[1]) if len(sys.argv) > 1 and sys.argv[1].isdigit() else 40000
    seeds = [1000, 1001, 1002, 1003, 1004, 1005]  # the coordinator's 6 cached nets (proto_r2.make_mlp seeds)
    t0 = time.time()
    nets = []
    for s in seeds:
        nets.append(run_net(s, Nx))
        print(f"  net {s} done ({time.time() - t0:.0f}s)", flush=True)
    bad = 0
    print(
        f"  Nx={Nx} per net; columns: l | g_meas (3 nets) | g_identity (3 nets) | max|diff| | 3*sd_delta+noise | sd across nets | sd predicted (1/n, cond.)"
    )
    for l in range(L):
        gm, gi, tol, sdp = [], [], [], []
        for net in nets:
            r = net[l]
            num = r["varA2"] - (0.0 if perturb else 2.0 * r["trC2"])
            gid = 3.0 * num / (r["trC"] ** 2 + 2.0 * r["trC2"])
            g = r["g"]
            v2 = (r["v"] ** 2).mean()
            resid = r["k4"] - g * r["v"] ** 2
            sd_delta = resid.std() / (
                np.sqrt(n) * v2
            )  # row-average fluctuation of g (conditional on earlier layers)
            # MC noise on g from Nx samples: var(k4 estimator) ~ (96 - 24 + ...) sigma^8 / Nx ~ 72 sigma^8/Nx per neuron,
            # averaged over n neurons -> use 96 sigma^8/(Nx n) as a conservative per-layer noise sd
            sd_mc = np.sqrt(96.0 * (r["v"] ** 4).mean() / (Nx * n)) / v2
            gm.append(g)
            gi.append(gid)
            tol.append(3 * sd_delta + 3 * sd_mc)
            sdp.append(sd_delta)
        diff = max(abs(a - b) for a, b in zip(gm, gi))
        ok = diff <= max(tol)
        bad += 0 if ok else 1
        print(
            f"  l={l + 1:2d} | {' '.join(f'{x:.4f}' for x in gm)} | {' '.join(f'{x:.4f}' for x in gi)} | {diff:.4f} | {max(tol):.4f} | {np.std(gm):.4f} | {np.mean(sdp):.4f} {'' if ok else 'VIOLATION'}"
        )
    tag = "PERTURBED (-2trC^2 dropped)" if perturb else "identity"
    print(f"check5 [{tag}]: {bad} layer violations -> {'FAIL' if bad else 'PASS'}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main("--perturb" in sys.argv))
