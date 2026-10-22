"""Exploratory screen (not a gate): is a K=2 (mean + full covariance) chain, optionally
averaged over Gauss-Hermite nodes along a few input directions, anywhere near K=3?

K=2 step for h = relu(z), z ~ N(mu, Sigma):
  Hermite coefficients of f(u) = relu(mu + s u):  c0 = mu Phi(a) + s phi(a), c1 = s Phi(a),
  c_k = s He_{k-2}(-a) phi(a) for k >= 2  (Stein: E[f He_k] = E[f^(k)]).
  Cov(h_i, h_j) = sum_{k>=1} c_k(i) c_k(j) rho_ij^k / k!   (Mehler), diagonal exact.
Mixture: X = sum_r t_r v_r + X_perp with t ~ N(0, I_m) on a tensor GH grid; conditional
chain starts from z1 = W1 X with mean W1 V t and covariance W1 (I - V V^T) W1^T.
usage: k2_mix_screen.py <net_id> [<net_id> ...]
"""

import sys
from math import factorial
from pathlib import Path

import numpy as np

try:
    from scipy.special import ndtr
except ImportError:  # starter-kit venv has no scipy
    from math import erf
    _erf = np.frompyfunc(erf, 1, 1)

    def ndtr(v):
        return 0.5 * (1 + _erf(np.asarray(v) / 2**0.5).astype(float))


D = Path(__file__).resolve().parents[2] / "research/full/data"
import os
KMAX = int(os.environ.get("KMAX", "24"))


def herm_coeffs(mu, s):
    a = mu / s
    phi = np.exp(-0.5 * a * a) / np.sqrt(2 * np.pi)
    Phi = ndtr(a)
    C = np.empty((KMAX + 1, mu.size))
    C[0] = mu * Phi + s * phi
    C[1] = s * Phi
    # probabilists' Hermite He_m(-a) by recurrence
    Hm2, Hm1 = np.ones_like(a), -a  # He_0, He_1 at -a
    C[2] = s * Hm2 * phi
    if KMAX >= 3:
        C[3] = s * Hm1 * phi
    x = -a
    for k in range(4, KMAX + 1):
        m = k - 2
        H = x * Hm1 - (m - 1) * Hm2
        C[k] = s * H * phi
        Hm2, Hm1 = Hm1, H
    m2 = (mu * mu + s * s) * Phi + mu * s * phi  # exact E[f^2]
    return C, m2 - C[0] ** 2


def relu_moments(mu, Sig):
    s = np.sqrt(np.maximum(np.diag(Sig), 1e-30))
    C, var = herm_coeffs(mu, s)
    rho = Sig / np.outer(s, s)
    np.fill_diagonal(rho, 0.0)
    cov = np.zeros_like(Sig)
    rk = np.ones_like(rho)
    for k in range(1, KMAX + 1):
        rk = rk * rho
        cov += np.outer(C[k], C[k]) * rk / factorial(k)
    np.fill_diagonal(cov, var)
    return C[0], cov


def chain(W, mu1, Sig1):
    mu, Sig = mu1, Sig1
    out = []
    for l in range(W.shape[0]):
        if l > 0:
            mu = W[l] @ m
            Sig = W[l] @ C @ W[l].T
        m, C = relu_moments(mu, Sig)
        out.append(m)
    return np.array(out)


def main():
    for nid in map(int, sys.argv[1:]):
        W = np.load(D / f"w_{nid:05d}.npy").astype(np.float64)
        T = np.load(D / f"truth_{nid:05d}.npz")
        # orientation check on layer 1: z = W0 @ x  vs  z = x @ W0
        n = W.shape[1]
        rows = np.sqrt((W[0] ** 2).sum(1) / (2 * np.pi))
        cols = np.sqrt((W[0] ** 2).sum(0) / (2 * np.pi))
        t0 = T["all_layer_means"][0]
        if np.abs(cols - t0).mean() < np.abs(rows - t0).mean():
            W = np.transpose(W, (0, 2, 1))
        res = {}
        # plain K=2
        est = chain(W, np.zeros(n), W[0] @ W[0].T)
        res["K2"] = est
        # mixture along top-m right singular vectors of W0 (m = 1, 2), GH nodes
        for m, q in ((1, 8), (2, 4)):
            V = np.linalg.svd(W[0], full_matrices=False)[2][:m].T  # n x m
            x, w = np.polynomial.hermite_e.hermegauss(q)
            w = w / w.sum()
            grids = np.stack(np.meshgrid(*[x] * m, indexing="ij"), -1).reshape(-1, m)
            wts = np.prod(np.stack(np.meshgrid(*[w] * m, indexing="ij"), -1).reshape(-1, m), 1)
            P = np.eye(n) - V @ V.T
            S1 = W[0] @ P @ W[0].T
            acc = 0
            for t, wt in zip(grids, wts):
                acc = acc + wt * chain(W, W[0] @ (V @ t), S1)
            res[f"mix{m}x{q}"] = acc
        tr = T["final_means"]
        for k, v in res.items():
            mse = np.mean((v[-1] - tr) ** 2)
            l1 = np.mean((v[0] - T["all_layer_means"][0]) ** 2)
            print(f"net {nid} {k:8s} final MSE {mse:.3e}  layer1 MSE {l1:.1e}", flush=True)


if __name__ == "__main__":
    main()
