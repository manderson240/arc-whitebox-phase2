"""PROOFS.md Theorem 2 -- ReLU Gaussian moments, the covariance-series (Price/Mehler) identity, the arc-cosine
kernel, and the kink identities, checked against high-precision mpmath quadrature (30 digits, 2-D Gauss-Legendre
on the Gaussian tails truncated at 12 sigma; truncation error < 1e-30).

Random (mu_1, mu_2, sigma_1, sigma_2, rho) draws; every closed form must agree with quadrature to 1e-12
(the ReLU kink makes the integrand only C^0, so 2-D quadrature is the limiting factor, not the formulas).

--perturb : flip the sign of the mu*sigma*phi term in E[ReLU^2] and use Phi(a) instead of the correct
            He_{k-2}(-a) phi(a)/sigma^{k-1} coefficient for k=2 in the series -> must FAIL.
"""

from __future__ import annotations

import random
import sys

import mpmath as mp


mp.mp.dps = 30
SQ2PI = mp.sqrt(2 * mp.pi)


def phi(x):
    return mp.exp(-x * x / 2) / SQ2PI


def Phi(x):
    return mp.ncdf(x)


def He(k, x):
    """probabilists' Hermite He_k(x)."""
    a, b = mp.mpf(1), x
    if k == 0:
        return a
    for m in range(1, k):
        a, b = b, x * b - m * a
    return b


def relu_coeffs(mu, sig, kmax, perturb=False):
    """fhat_k = E[ReLU^(k)(Y)], Y~N(mu,sig^2): [m1, Phi(a), He_{k-2}(-a) phi(a)/sig^(k-1) ...]."""
    a = mu / sig
    out = [mu * Phi(a) + sig * phi(a), Phi(a)]
    for k in range(2, kmax + 1):
        c = He(k - 2, -a) * phi(a) / sig ** (k - 1)
        if perturb and k == 2:
            c = Phi(a)
        out.append(c)
    return out


def quad2(f, mu1, s1, mu2, s2, rho):
    """E[f(Z1,Z2)] for bivariate normal, by 2-D quadrature in whitened coordinates."""

    def g(u, v):
        z1 = mu1 + s1 * u
        z2 = mu2 + s2 * (rho * u + mp.sqrt(1 - rho * rho) * v)
        return f(z1, z2) * phi(u) * phi(v)

    # split at the kinks z1=0 -> u0, z2=0 depends on u; integrate u piecewise, v piecewise
    u0 = -mu1 / s1

    def inner(u):
        z1 = mu1 + s1 * u
        v0 = (-mu2 / s2 - rho * u) / mp.sqrt(1 - rho * rho)
        pts = sorted(set([mp.mpf(-12), v0, mp.mpf(12)]))
        pts = [p for p in pts if -12 <= p <= 12] or [mp.mpf(-12), mp.mpf(12)]
        return mp.quad(lambda v: g(u, v), pts)

    pts = sorted(set([mp.mpf(-12), u0, mp.mpf(12)]))
    pts = [p for p in pts if -12 <= p <= 12] or [mp.mpf(-12), mp.mpf(12)]
    return mp.quad(inner, pts)


def quad1(f, mu, s):
    a = -mu / s
    pts = sorted(set([mp.mpf(-12), a, mp.mpf(12)]))
    pts = [p for p in pts if -12 <= p <= 12] or [mp.mpf(-12), mp.mpf(12)]
    return mp.quad(lambda u: f(mu + s * u) * phi(u), pts)


def relu(x):
    return x if x > 0 else mp.mpf(0)


def main(perturb: bool) -> int:
    rng = random.Random(20260927)
    tol = mp.mpf("1e-12")
    worst = {}
    n_bad = 0

    def rec(name, closed, ref):
        nonlocal n_bad
        err = abs(closed - ref)
        worst[name] = max(worst.get(name, mp.mpf(0)), err)
        if err > tol:
            n_bad += 1

    for trial in range(6):
        mu1, mu2 = [rng.uniform(-1.5, 1.5) for _ in range(2)]
        s1, s2 = [rng.uniform(0.3, 2.0) for _ in range(2)]
        rho = rng.uniform(-0.85, 0.85)
        mu1, mu2, s1, s2, rho = map(mp.mpf, (mu1, mu2, s1, s2, rho))
        a1, a2 = mu1 / s1, mu2 / s2
        # (a) univariate moments
        m1 = mu1 * Phi(a1) + s1 * phi(a1)
        m2 = (mu1**2 + s1**2) * Phi(a1) + (mu1 * s1 * phi(a1)) * (-1 if perturb else 1)
        rec("E[ReLU]", m1, quad1(relu, mu1, s1))
        rec("E[ReLU^2]", m2, quad1(lambda x: relu(x) ** 2, mu1, s1))
        # (b) covariance series E[f(Z1)g(Z2)] = sum_k fhat_k ghat_k C^k/k!  (C = rho s1 s2), K=60 terms
        C = rho * s1 * s2
        f1, f2 = relu_coeffs(mu1, s1, 60, perturb), relu_coeffs(mu2, s2, 60, perturb)
        ser = sum(f1[k] * f2[k] * C**k / mp.factorial(k) for k in range(61))
        rec(
            "E[ReLU1 ReLU2] series",
            ser,
            quad2(lambda x, y: relu(x) * relu(y), mu1, s1, mu2, s2, rho),
        )
        # series truncated at K=8 (the production KH) -- reported, not gated
        ser8 = sum(f1[k] * f2[k] * C**k / mp.factorial(k) for k in range(9))
        worst["series K=8 truncation (info)"] = max(
            worst.get("series K=8 truncation (info)", 0), abs(ser8 - ser)
        )
        # (c) kink identities at general means (2-D Gaussian density / conditional CDF)
        r2 = mp.sqrt(1 - rho * rho)
        dd = mp.exp(-(a1**2 - 2 * rho * a1 * a2 + a2**2) / (2 * (1 - rho**2))) / (
            2 * mp.pi * s1 * s2 * r2
        )
        dth = phi(a1) / s1 * Phi((a2 - rho * a1) / r2)
        # <delta_1 delta_2> = sum_k fhat_{k+2} ghat_{k+2} C^k/k!  (series form used in the chain)
        ser_dd = sum(f1[k + 2] * f2[k + 2] * C**k / mp.factorial(k) for k in range(59))
        ser_dth = sum(f1[k + 2] * f2[k + 1] * C**k / mp.factorial(k) for k in range(59))
        rec("<delta1 delta2> closed vs series", dd, ser_dd)
        rec("<delta1 theta2> closed vs series", dth, ser_dth)
        # <delta1 theta2> directly: E[delta(z1) 1{z2>0}] = p1(0) P(z2>0 | z1=0) -- quadrature in z2 only
        cond_mu = mu2 + rho * s2 * (0 - mu1) / s1
        cond_s = s2 * r2
        rec(
            "<delta1 theta2> closed vs cond-quad",
            dth,
            phi(a1) / s1 * quad1(lambda x: 1 if x > 0 else 0, cond_mu, cond_s),
        )
        # (d) arc-cosine kernel at mu=0 (Cho & Saul 2009, degree-1): E[ReLU ReLU] = s1 s2 (sin t + (pi-t) cos t)/(2 pi)
        t = mp.acos(rho)
        acos_k = s1 * s2 * (mp.sin(t) + (mp.pi - t) * mp.cos(t)) / (2 * mp.pi)
        rec(
            "arc-cosine kernel (mu=0)",
            acos_k,
            quad2(lambda x, y: relu(x) * relu(y), mp.mpf(0), s1, mp.mpf(0), s2, rho),
        )

    tag = "PERTURBED" if perturb else "closed forms"
    for k, v in worst.items():
        print(f"  {k:40s} worst |err| = {mp.nstr(v, 3)}")
    print(f"check2 [{tag}]: {n_bad} violations of 1e-12 -> {'FAIL' if n_bad else 'PASS'}")
    return 1 if n_bad else 0


if __name__ == "__main__":
    sys.exit(main("--perturb" in sys.argv))
