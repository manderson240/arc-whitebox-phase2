"""Numerical checks for V30 Appendix P1 (sampled-truth oracle bias) and P2 (Gram-solve admission).

Each check is built to FAIL if the stated result is wrong:
  P1: E[R(m_hat)] - R(m) = tr(H Sigma)/(2N) + O(N^-2) for a quadratic-plus-cubic R; the
      two-half Richardson estimate 2 R(full) - mean(R(half_a), R(half_b)) has bias O(N^-2).
      With Gaussian samples the cubic term has zero mean, so p1() tests only the quadratic case;
      p1_skew() uses skewed samples and asserts that the Richardson residual falls as N^-2.
      Falsifier: the same extrapolation applied to a reading whose bias is NOT ~1/N
      (here R(m) = |m|, non-smooth at 0) must NOT come out unbiased.
  P2: Q F with F = (Q^T Q)^-1 Q^T X equals the orthogonal projection of X onto span(Q),
      for non-orthonormal Q. Falsifier: the naive Q Q^T X differs when Q is not orthonormal.
"""

import numpy as np


rng = np.random.default_rng(0)


def p1(trials=200_000, d=3, N=64):
    m = np.array([0.3, -0.2, 0.5])
    L = rng.normal(size=(d, d)) * 0.5
    Sigma = L @ L.T + 0.2 * np.eye(d)
    A = rng.normal(size=(d, d))
    H = A + A.T  # Hessian of the quadratic part
    c = rng.normal(size=d)

    def R(x):  # smooth reading: quadratic + small cubic
        x = np.atleast_2d(x)
        dx = x - m
        return 0.5 * np.einsum("ti,ij,tj->t", dx, H, dx) + 0.1 * (dx @ c) ** 3

    Ch = np.linalg.cholesky(Sigma)
    z = rng.normal(size=(trials, N, d)) @ Ch.T + m
    full = z.mean(1)
    ha, hb = z[:, : N // 2].mean(1), z[:, N // 2 :].mean(1)
    bias_full = R(full).mean() - 0.0
    pred = np.trace(H @ Sigma) / (2 * N)
    rich = (2 * R(full) - 0.5 * (R(ha) + R(hb))).mean()
    se = R(full).std() / np.sqrt(trials)
    print(f"P1 bias(full)={bias_full:.3e}  predicted tr(HS)/2N={pred:.3e}  SE={se:.1e}")
    print(f"P1 Richardson residual={rich:.3e} (should be ~0 within SE)")
    assert abs(bias_full - pred) < 4 * se, "P1 leading-term bias formula FAILED"
    assert abs(rich) < 4 * se, "P1 Richardson extrapolation FAILED"

    # falsifier: non-smooth reading at the truth, bias ~ N^-1/2, extrapolation must not zero it
    m0 = np.zeros(d)
    z0 = z - m + m0
    Rn = lambda x: np.abs(x[:, 0])
    rich0 = (
        2 * Rn(z0.mean(1)) - 0.5 * (Rn(z0[:, : N // 2].mean(1)) + Rn(z0[:, N // 2 :].mean(1)))
    ).mean()
    se0 = Rn(z0.mean(1)).std() / np.sqrt(trials)
    print(f"P1 falsifier (non-smooth) Richardson residual={rich0:.3e} vs SE {se0:.1e}")
    assert abs(rich0) > 10 * se0, "falsifier did not fire: check cannot discriminate"


def p1_skew(trials=400_000, d=3, Ns=(8, 16, 32)):
    """O(N^-2) part of P1. With Gaussian samples the cubic term of the reading has zero mean, so p1()
    exercises only the quadratic case. Here the samples are skewed (centred exponential, kappa3 = 2 per
    coordinate), so the cubic term contributes kappa3/N^2 to the bias and the Richardson residual must
    be nonzero and fall as N^-2 (log-log slope ~ -2). Falsifiers: (a) a residual consistent with 0 at the
    smallest N (the check could not see the O(N^-2) term); (b) a slope near -1 (the extrapolation would
    then not have removed the 1/N term)."""
    rs = np.random.default_rng(1)
    m = np.array([0.3, -0.2, 0.5])
    A = rs.normal(size=(d, d))
    H = A + A.T
    c = rs.normal(size=d)

    def R(x):
        dx = x - m
        return 0.5 * np.einsum("ti,ij,tj->t", dx, H, dx) + 0.5 * (dx @ c) ** 3

    res, ses = [], []
    for N in Ns:
        z = rs.exponential(size=(trials, N, d)) - 1.0 + m
        rich = 2 * R(z.mean(1)) - 0.5 * (R(z[:, : N // 2].mean(1)) + R(z[:, N // 2 :].mean(1)))
        res.append(rich.mean())
        ses.append(rich.std() / np.sqrt(trials))
    slope = np.polyfit(np.log(Ns), np.log(np.abs(res)), 1)[0]
    print(
        "P1 skewed samples: Richardson residual "
        + ", ".join(f"N={N} {r:.2e} (SE {s:.1e})" for N, r, s in zip(Ns, res, ses))
        + f"; log-log slope {slope:.2f} (expect ~ -2)"
    )
    assert abs(res[0]) > 6 * ses[0], "falsifier: O(N^-2) residual not resolved at the smallest N"
    assert -2.6 < slope < -1.5, "P1 O(N^-2) Richardson residual FAILED (slope not ~ -2)"


def p2(n=512, r=96, k=40):
    Q = rng.normal(size=(n, r)) @ np.diag(np.linspace(1, 50, r))  # badly scaled, cond ~ 1e3
    X = rng.normal(size=(n, k))
    F = np.linalg.solve(Q.T @ Q, Q.T @ X)
    Qo, _ = np.linalg.qr(Q)
    proj = Qo @ (Qo.T @ X)
    err = np.abs(Q @ F - proj).max() / np.abs(proj).max()
    naive = np.abs(Q @ (Q.T @ X) - proj).max() / np.abs(proj).max()
    print(
        f"P2 cond(Q)={np.linalg.cond(Q):.1e}  Gram-solve vs QR projection rel err={err:.1e}  naive QQ^T rel err={naive:.1e}"
    )
    assert err < 1e-10, "P2 Gram-solve != orthogonal projection"
    assert naive > 1e-2, "falsifier did not fire"


if __name__ == "__main__":
    p1()
    p1_skew()
    p2()
    print("ALL PASS")
