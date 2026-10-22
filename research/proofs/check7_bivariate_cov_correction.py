"""PROOFS.md Theorem 7 -- bivariate fourth-order covariance correction under the Gaussian scale-mixture model
(COV_CLOSURE_DERIVATION.md eq. (3); derived there by the other agent, re-proved and machine-checked here).

Model: z = mu + s * xi, xi ~ N(0, Sigma) (2-D), s^2 = 1 + eps, E eps = 0, Var eps = v, eps independent of xi.
(a) Exact fourth cumulants: kappa(z_a,z_b,z_c,z_d) = v [S_ab S_cd + S_ac S_bd + S_ad S_bc]  (so kappa4_a = 3 v sigma_a^4,
    g = 3v; Q_ab = kappa_{2,2} = v (sigma_a^2 sigma_b^2 + 2 C^2); K31_ab = kappa_{3,1} = 3 v sigma_a^2 C).
(b) Correction: Delta E[f(z_a) g(z_b)] = (g/24)[ s_a^4 E_G f''''g + s_b^4 E_G f g'''' + (2 s_a^2 s_b^2 + 4C^2) E_G f''g''
                                            + 4 s_a^2 C E_G f'''g' + 4 s_b^2 C E_G f'g''' ] + O(E eps^3, v^2),
    with E_G[f^(p) g^(q)] = sum_k fhat_{k+p} ghat_{k+q} C^k/k!  (the covariance series, Theorem 2).

Check: eps two-point (+-sqrt v), so the truth is EXACTLY (1/2)[E_G(fg;(1+sqrt v)Sigma) + E_G(fg;(1-sqrt v)Sigma)];
each Gaussian expectation via the 80-term covariance series (verified to 1e-17 in check2) plus ONE independent
2-D quadrature spot check. The remainder after (b) must scale as v^2 (two-point eps has E eps^3 = 0): log-log slope
within 0.15 of 2. Part (a) is checked by direct mixture moments (exact) at 1e-25.

--perturb : drop the two (3,1)/(1,3) terms (the "K31" terms nobody had) -> slope must fall to ~1 -> FAIL.
"""

from __future__ import annotations

import random
import sys

import mpmath as mp


mp.mp.dps = 25
SQ2PI = mp.sqrt(2 * mp.pi)
phi = lambda x: mp.exp(-x * x / 2) / SQ2PI
Phi = mp.ncdf


def He(k, x):
    a, b = mp.mpf(1), x
    if k == 0:
        return a
    for m in range(1, k):
        a, b = b, x * b - m * a
    return b


def relu_coeffs(mu, sig, kmax):
    a = mu / sig
    out = [mu * Phi(a) + sig * phi(a), Phi(a)]
    for k in range(2, kmax + 1):
        out.append(He(k - 2, -a) * phi(a) / sig ** (k - 1))
    return out


def series(fh, gh, C, p, q, K):
    return sum(fh[k + p] * gh[k + q] * C**k / mp.factorial(k) for k in range(K + 1))


def E_G(mu1, mu2, s1, s2, C, K=80):
    f1, f2 = relu_coeffs(mu1, s1, K), relu_coeffs(mu2, s2, K)
    return series(f1, f2, C, 0, 0, K)


def quad2(mu1, s1, mu2, s2, rho):
    relu = lambda x: x if x > 0 else mp.mpf(0)
    r2 = mp.sqrt(1 - rho * rho)

    def inner(u):
        z1 = mu1 + s1 * u
        v0 = (-mu2 / s2 - rho * u) / r2
        pts = sorted({mp.mpf(-10), min(max(v0, -10), 10), mp.mpf(10)})
        return mp.quad(
            lambda v: relu(z1) * relu(mu2 + s2 * (rho * u + r2 * v)) * phi(u) * phi(v), pts
        )

    u0 = min(max(-mu1 / s1, -10), 10)
    return mp.quad(inner, sorted({mp.mpf(-10), u0, mp.mpf(10)}))


def main(perturb: bool) -> int:
    rng = random.Random(7)
    bad = 0
    for trial in range(3):
        mu1, mu2 = mp.mpf(rng.uniform(-1, 1)), mp.mpf(rng.uniform(-1, 1))
        s1, s2 = mp.mpf(rng.uniform(0.5, 1.5)), mp.mpf(rng.uniform(0.5, 1.5))
        rho = mp.mpf(rng.uniform(-0.5, 0.5))
        C = rho * s1 * s2
        # (a) fourth cumulants of the mixture, exactly, at v = 0.1 : kappa_{2,2} and kappa_{3,1} (centered z = s*xi)
        v = mp.mpf("0.1")
        Es4 = 1 + v  # E[(1+eps)^2] = 1 + v
        # E[xi_a^2 xi_b^2] = s1^2 s2^2 + 2C^2 ; E[xi_a^3 xi_b] = 3 s1^2 C  (Wick)
        E22 = Es4 * (s1**2 * s2**2 + 2 * C**2)
        E31 = Es4 * 3 * s1**2 * C
        k22 = (
            E22 - s1**2 * s2**2 - 2 * C**2
        )  # kappa_{2,2} = E[a^2 b^2] - Var_a Var_b - 2 Cov^2 (zero means)
        k31 = E31 - 3 * s1**2 * C  # kappa_{3,1} = E[a^3 b] - 3 Var_a Cov
        if abs(k22 - v * (s1**2 * s2**2 + 2 * C**2)) > mp.mpf("1e-25") or abs(
            k31 - 3 * v * s1**2 * C
        ) > mp.mpf("1e-25"):
            bad += 1
            print("  (a) cumulant structure VIOLATION")
        # (b) correction formula vs exact two-point mixture, slope in v
        f1, f2 = relu_coeffs(mu1, s1, 90), relu_coeffs(mu2, s2, 90)
        base = series(f1, f2, C, 0, 0, 80)
        S = lambda p, q: series(f1, f2, C, p, q, 80)
        errs, vs = [], [mp.mpf(x) for x in ("0.02", "0.04", "0.08")]
        for v in vs:
            g = 3 * v
            r = mp.sqrt(v)
            truth = (
                E_G(mu1, mu2, s1 * mp.sqrt(1 + r), s2 * mp.sqrt(1 + r), C * (1 + r))
                + E_G(mu1, mu2, s1 * mp.sqrt(1 - r), s2 * mp.sqrt(1 - r), C * (1 - r))
            ) / 2
            corr = (g / 24) * (
                s1**4 * S(4, 0)
                + s2**4 * S(0, 4)
                + (2 * s1**2 * s2**2 + 4 * C**2) * S(2, 2)
                + (0 if perturb else 4 * s1**2 * C * S(3, 1) + 4 * s2**2 * C * S(1, 3))
            )
            errs.append(abs(truth - (base + corr)))
        slope = mp.log(errs[1] / errs[0]) / mp.log(vs[1] / vs[0])
        ok = abs(slope - 2) < mp.mpf("0.15")
        bad += 0 if ok else 1
        print(
            f"  trial {trial}: mu=({mp.nstr(mu1, 3)},{mp.nstr(mu2, 3)}) s=({mp.nstr(s1, 3)},{mp.nstr(s2, 3)}) rho={mp.nstr(rho, 3)} | "
            f"|remainder| at v={[mp.nstr(x, 2) for x in vs]} = {[mp.nstr(e, 3) for e in errs]} slope={mp.nstr(slope, 4)} (expected 2) {'ok' if ok else 'VIOLATION'}"
        )
        if trial == 0:
            # independent spot check of the series-based truth against 2-D quadrature at v = 0.04
            r = mp.sqrt(mp.mpf("0.04"))
            t_series = (
                E_G(mu1, mu2, s1 * mp.sqrt(1 + r), s2 * mp.sqrt(1 + r), C * (1 + r))
                + E_G(mu1, mu2, s1 * mp.sqrt(1 - r), s2 * mp.sqrt(1 - r), C * (1 - r))
            ) / 2
            t_quad = (
                quad2(mu1, s1 * mp.sqrt(1 + r), mu2, s2 * mp.sqrt(1 + r), rho)
                + quad2(mu1, s1 * mp.sqrt(1 - r), mu2, s2 * mp.sqrt(1 - r), rho)
            ) / 2
            print(
                f"    spot check: series truth vs 2-D quadrature |diff| = {mp.nstr(abs(t_series - t_quad), 3)}"
            )
            if abs(t_series - t_quad) > mp.mpf("1e-10"):
                bad += 1
    tag = "PERTURBED ((3,1)/(1,3) terms dropped)" if perturb else "eq. (3)"
    print(f"check7 [{tag}]: {bad} violations -> {'FAIL' if bad else 'PASS'}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main("--perturb" in sys.argv))
