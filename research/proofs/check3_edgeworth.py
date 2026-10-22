"""PROOFS.md Theorem 3 -- Edgeworth / Gram-Charlier expansion of E[f(Z)] for non-Gaussian Z, f = ReLU.

Z = mu + sqrt(1-eps^2) G + eps U,  G ~ N(0,1),  U = standardized Gamma(shape k) (independent), so that
  kappa_2(Z) = 1,  kappa_r(Z) = eps^r kappa_r(U),  kappa_r(U) = (r-1)!/k^(r/2-1)   (r >= 3)   -- all EXACT.
Truth: E[ReLU(Z)] = E_U[ m1(mu + eps U, 1-eps^2) ] -- a 1-D integral over the Gamma density with the closed-form
Gaussian ReLU mean inside (mpmath, 30 digits).

Expansion (Gaussian reference, sigma^2 = 1):  E[f(Z)] = sum_j  B_j(0,0,k3,...,k_j)/j! * E_G[f^(j)],
B_j = complete Bell polynomial, so the j=3..7 coefficients are
  k3/6, k4/24, k5/120, (k6 + 10 k3^2)/720 = k6/720 + k3^2/72, (k7 + 35 k3 k4)/5040.
E_G[ReLU^(j)] = He_{j-2}(-mu) phi(mu)   (sigma = 1).
Claim checked: the remainder after including all terms of cumulant-order <= J scales as eps^(J+1):
log-log slope of |error| vs eps must be within 0.25 of J+1 for J = 2 (Gaussian), 3, 4, 5, 6.

--perturb : use the Gram-Charlier-style j=6 coefficient WITHOUT the k3^2/72 term -> the J=6 slope must
            drop back to 6 (the eps^6 term is no longer cancelled) -> FAIL.
"""

from __future__ import annotations

import sys

import mpmath as mp


mp.mp.dps = 30
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


def m1_gauss(mu, var):
    s = mp.sqrt(var)
    a = mu / s
    return mu * Phi(a) + s * phi(a)


def truth(mu, eps, k):
    """E[ReLU(mu + sqrt(1-eps^2) G + eps U)], U standardized Gamma(k): U = (X - k)/sqrt(k), X ~ Gamma(k,1)."""
    var = 1 - eps * eps
    dens = lambda x: x ** (k - 1) * mp.exp(-x) / mp.gamma(k)
    f = lambda x: m1_gauss(mu + eps * (x - k) / mp.sqrt(k), var) * dens(x)
    return mp.quad(f, [0, k, 4 * k, 10 * k, 40 * k, mp.inf])


def edgeworth(mu, eps, k, J, perturb=False):
    kap = {r: eps**r * mp.factorial(r - 1) / mp.mpf(k) ** (mp.mpf(r) / 2 - 1) for r in range(3, 8)}
    d = lambda j: He(j - 2, -mu) * phi(mu)  # E_G[ReLU^(j)], sigma=1
    val = m1_gauss(mu, 1)
    coef = {
        3: kap[3] / 6,
        4: kap[4] / 24,
        5: kap[5] / 120,
        6: kap[6] / 720 + (0 if perturb else kap[3] ** 2 / 72),
        7: kap[7] / 5040 + kap[3] * kap[4] / 144,
    }
    for j in range(3, J + 1):
        val += coef[j] * d(j)
    return val


def main(perturb: bool) -> int:
    mu, k = mp.mpf("0.3"), 4
    epss = [mp.mpf(e) for e in ("0.05", "0.1", "0.2", "0.4")]
    T = {e: truth(mu, e, k) for e in epss}
    bad = 0
    print(
        f"  mu={mu}, U = standardized Gamma({k}); slopes of |E_true - E_edgeworth(J)| vs eps (expected J+1)"
    )
    for J in (2, 3, 4, 5, 6):
        errs = [abs(T[e] - edgeworth(mu, e, k, J, perturb)) for e in epss]
        slopes = [
            mp.log(errs[i + 1] / errs[i]) / mp.log(epss[i + 1] / epss[i])
            for i in range(len(epss) - 1)
        ]
        s = slopes[0]  # smallest-eps pair: asymptotic regime
        ok = abs(s - (J + 1)) < mp.mpf("0.25")
        bad += 0 if ok else 1
        print(
            f"  J={J}: |err| at eps={[mp.nstr(e, 2) for e in epss]} = {[mp.nstr(x, 3) for x in errs]}  "
            f"slope(small eps)={mp.nstr(s, 4)} expected {J + 1} -> {'ok' if ok else 'VIOLATION'}"
        )
    # the ReLU-specific first-order terms, spelled out (mu general, sigma general): report the symbolic forms once
    print(
        "  ReLU term forms: k3/6 * (-mu phi(a)/sigma^3) ; k4/24 * (a^2-1) phi(a)/sigma^3 ; k3^2/72 * He_4(-a) phi(a)/sigma^5"
    )
    tag = "PERTURBED (k3^2/72 dropped)" if perturb else "full Edgeworth coefficients"
    print(f"check3 [{tag}]: {bad} slope violations -> {'FAIL' if bad else 'PASS'}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main("--perturb" in sys.argv))
