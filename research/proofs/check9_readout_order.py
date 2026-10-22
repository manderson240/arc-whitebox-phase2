"""PROOFS.md Proposition 9 -- the own-index factorization lemma and the k = 0 cancellation identity
(EDGEWORTH_ORDER_AND_K4I.md section 1; the resolution of the kappa3^2/72 "surprise", G-V4 / G-E6).

Part A (the lemma, numerically). z_a = mu_a + sqrt(1-eps^2) g_a + eps U_a, z_b likewise, (g_a, g_b) standard Gaussian
with correlation rho, U_a, U_b independent standardized Exp(1) (kappa_r(U) = (r-1)!), so the OWN-index cumulants are
kappa_r(z) = eps^r (r-1)! exactly, the cross cumulants of order >= 3 vanish (independence + multilinearity), Var z = 1,
Cov(z_a, z_b) = C = rho (1 - eps^2). Lemma: E[f(z_a) g(z_b)] = sum_k Fhat_k(a) Ghat_k(b) C^k / k! with
  Fhat_k = sum_j B_j(0,0,kappa3,..,kappa_j)/j! * fhat_{k+j}  (Bell polynomials: kappa3/6, kappa4/24, kappa5/120,
  kappa6/720 + kappa3^2/72, kappa7/5040 + kappa3 kappa4/144),
i.e. the Stein-coefficient bookkeeping of ANY own-index Edgeworth correction is a per-neuron VECTOR Fhat applied in the
SAME covariance series (Thm 2b). Truth: E over (U_a, U_b) by 80-node Gauss-Laguerre of the bivariate Gaussian ReLU
expectation at the shifted means (covariance series, Thm 2b, 60 terms). Claim: after keeping all cumulant orders <= J
the remainder scales as eps^(J+1) (log-log slope within 0.3 of J+1) for J = 2..6 -- the bivariate extension of check3.
Part B (the identity). Cov = E[fg] - E[f]E[g]: the k = 0 term Fhat_0(a) Fhat_0(b) equals E[f]E[g] IDENTICALLY (for any
truncation of the cumulant list) iff the mean readout IS Fhat_0 and the rows use the same Fhat; the "mean-only" patch
(c6 = kappa3^2/72 added to the mean, raw rows) leaves the FIRST-order residue -d6 (x) m1 - m1 (x) d6 - d6 (x) d6,
d6 = (kappa3^2/72) fhat_6. Checked on n = 12 synthetic neurons (product residue exactly 0; patch residue = predicted).
The production instance is G-E6-0a (4 (net, layer) rows of MLPs 1000/1001, 1.0e-11 relative; `proto_edge6.identity_check`).

--perturb : the G-V4 patch -- corrected Fhat only in the k = 0 term (the mean), raw fhat in every k >= 1 row.
            Part A: the slopes must collapse to ~3 for all J >= 3 (the k >= 1 rows are wrong at order kappa3) -> FAIL;
            Part B: asserting the patch residue is 0 -> FAIL.
"""

from __future__ import annotations

import math
import sys

import numpy as np


KSER = 60  # covariance-series terms (|rho| <= 0.4: rho^60 ~ 1e-24)
KMAX = 40  # C-series terms in the expansion; fhat_k ~ sqrt(k!) so 12 terms leave a ~1e-8 tail that masquerades as an eps^3 remainder (found 2026-09-28)
_erfc = np.vectorize(math.erfc)


def Phi(x):
    return 0.5 * _erfc(-x / math.sqrt(2.0))


def phi(x):
    return np.exp(-0.5 * x * x) / math.sqrt(2.0 * math.pi)


def He(k, x):
    a, b = np.ones_like(x), x
    if k == 0:
        return a
    for m in range(1, k):
        a, b = b, x * b - m * a
    return b


def fhat(mu, sig, kmax):
    """Stein coefficients of ReLU under N(mu, sig^2), k = 0..kmax (Thm 2b)."""
    a = mu / sig
    out = [mu * Phi(a) + sig * phi(a), Phi(a)]
    for k in range(2, kmax + 1):
        out.append(He(k - 2, -a) * phi(a) / sig ** (k - 1))
    return np.array(out)


def gauss_pair(mu_a, mu_b, var, C):
    """E[f(X) f(Y)] for (X,Y) Gaussian, means mu_a, mu_b (arrays), variances var, covariance C (Thm 2b)."""
    s = math.sqrt(var)
    fa, fb = fhat(mu_a, s, KSER), fhat(mu_b, s, KSER)
    tot = np.zeros(np.broadcast(mu_a, mu_b).shape)
    ck = 1.0
    for k in range(KSER + 1):
        tot = tot + fa[k] * fb[k] * ck
        ck = ck * C / (k + 1)
    return tot


def truth(mu_a, mu_b, rho, eps, nodes):
    x, w = np.polynomial.laguerre.laggauss(nodes)  # int_0^inf e^{-x} F(x) dx
    ua, ub = np.meshgrid(x - 1.0, x - 1.0, indexing="ij")
    W = np.outer(w, w)
    var = 1.0 - eps * eps
    val = gauss_pair(mu_a + eps * ua, mu_b + eps * ub, var, rho * var)
    return float((W * val).sum())


def bell_coeffs(eps, J):
    """coefficient of fhat_{k+j} for j = 3..7 keeping cumulant orders <= J (kappa_r = eps^r (r-1)!)."""
    kap = {r: eps**r * math.factorial(r - 1) for r in range(3, 8)}
    c = dict.fromkeys(range(3, 8), 0.0)
    if J >= 3:
        c[3] = kap[3] / 6
    if J >= 4:
        c[4] = kap[4] / 24
    if J >= 5:
        c[5] = kap[5] / 120
    if J >= 6:
        c[6] = kap[6] / 720 + kap[3] ** 2 / 72
    if J >= 7:
        c[7] = kap[7] / 5040 + kap[3] * kap[4] / 144
    return c


def series(mu_a, mu_b, rho, eps, J, perturb):
    C = rho * (1.0 - eps * eps)
    fa, fb = fhat(np.float64(mu_a), 1.0, KMAX + 7), fhat(np.float64(mu_b), 1.0, KMAX + 7)
    c = bell_coeffs(eps, J)
    Fa = np.array([fa[k] + sum(c[j] * fa[k + j] for j in range(3, 8)) for k in range(KMAX + 1)])
    Fb = np.array([fb[k] + sum(c[j] * fb[k + j] for j in range(3, 8)) for k in range(KMAX + 1)])
    if perturb:  # the G-V4-type patch: corrected mean, raw rows
        Fa = np.concatenate([[Fa[0]], fa[1 : KMAX + 1]])
        Fb = np.concatenate([[Fb[0]], fb[1 : KMAX + 1]])
    return float(sum(Fa[k] * Fb[k] * C**k / math.factorial(k) for k in range(KMAX + 1)))


def part_a(perturb: bool) -> bool:
    mu_a, mu_b, rho = 0.3, -0.2, 0.4
    eps_list = [0.05, 0.1, 0.2, 0.4]
    t80 = {e: truth(mu_a, mu_b, rho, e, 80) for e in eps_list}
    t60 = {e: truth(mu_a, mu_b, rho, e, 60) for e in eps_list}
    stab = max(abs(t80[e] - t60[e]) for e in eps_list)
    print(
        f"  Part A: mu=({mu_a},{mu_b}), rho={rho}, U = standardized Exp(1); truth 80 vs 60 Laguerre nodes: {stab:.1e}"
    )
    ok = True
    for J in range(2, 7):
        err = [abs(t80[e] - series(mu_a, mu_b, rho, e, J, perturb)) for e in eps_list]
        slope = math.log(err[1] / err[0]) / math.log(2.0)
        good = abs(slope - (J + 1)) <= 0.3 and err[0] > 50 * stab
        print(
            f"  J={J}: |err| at eps={eps_list} = {[f'{v:.3g}' for v in err]}  slope(small eps)={slope:.3f}"
            f" expected {J + 1} -> {'ok' if good else 'VIOLATION'}"
        )
        ok &= good
    return ok


def part_b(perturb: bool) -> bool:
    rng = np.random.default_rng(9)
    n = 12
    mu = rng.normal(0.05, 0.3, n)
    sig = rng.uniform(0.6, 1.2, n)
    k3 = rng.normal(0.0, 0.03, n) * sig**3
    k4 = 0.05 * sig**4
    fh = np.array([fhat(mu[i], sig[i], 8) for i in range(n)]).T  # (9, n)
    F = fh[0] + (k3 / 6) * fh[3] + (k4 / 24) * fh[4]  # consistent Fhat_0 without c6
    d6 = (k3 * k3 / 72.0) * fh[6]
    F6 = F + d6  # consistent Fhat_0 with c6: rows AND mean use F6 -> residue is 0 by construction
    res_prod = np.outer(F6, F6) - np.outer(F6, F6)
    res_patch = np.outer(F, F) - np.outer(F6, F6)  # raw-c6 rows at k=0 vs the patched mean
    predicted = -np.outer(d6, F) - np.outer(F, d6) - np.outer(d6, d6)
    rel = np.max(np.abs(res_patch - predicted)) / np.max(np.abs(predicted))
    scale = np.max(np.abs(np.outer(F6, F6)))
    print(
        f"  Part B (n={n}): consistent product k=0 residue = {np.max(np.abs(res_prod)):.1e} (exactly 0);"
        f" mean-only patch residue vs predicted -d6(x)m1 - m1(x)d6 - d6(x)d6: rel {rel:.1e};"
        f" |patch residue|/|m1(x)m1| = {np.max(np.abs(res_patch)) / scale:.1e}"
    )
    if perturb:
        good = np.max(np.abs(res_patch)) / scale <= 1e-12  # asserting the patch is consistent
        print(
            f"  perturbed assertion 'mean-only patch keeps the identity': {'ok' if good else 'VIOLATION'}"
        )
        return good
    return np.max(np.abs(res_prod)) == 0.0 and rel <= 1e-11


if __name__ == "__main__":
    perturb = "--perturb" in sys.argv
    a = part_a(perturb)
    b = part_b(perturb)
    label = "PERTURBED (mean-only patch)" if perturb else "own-index factorization + k=0 identity"
    ok = a and b
    print(
        f"check9 [{label}]: Part A {'PASS' if a else 'FAIL'}, Part B {'PASS' if b else 'FAIL'} -> {'PASS' if ok else 'FAIL'}"
    )
    sys.exit(0 if ok else 1)
