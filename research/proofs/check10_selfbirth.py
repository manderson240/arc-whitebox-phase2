"""SELF_BIRTH.md Proposition 10 -- the self-consistent stack (extension of PROOFS.md Thm 8) and the merge obstruction.

Setting as check8: same-leg hub sources S = sum_c w_c Sym3(A_c, A_c, E_c) in h-space (n x n_h legs), linear layer
z = h W (W stored (in,out)), ReLU ageing modelled by the elementwise rescale Phi (any positive vector: the identity
is algebraic, it does not depend on Phi being a cdf).

(a) S-1  the layer-l T-readout of the stack IS its coincident slice in z-space, and the aged stack's coincident objects
         are its Phi-rescale:
           off_l[i,j] := sum_s [(P^2 w) Q^T + 2((P Q) w) P^T]_ij = K_z[i,i,j]  (P = W^T A, Q = W^T E; diag = hubdiag)
           S2_aged[i,j] := N + 2M' of the aged legs (Phi o P, Phi o Q) = Phi_i^2 Phi_j off_l[i,j],  Saaa_aged = Phi^3 hubdiag.
         Consequence: the N / M' matmuls per cohort-layer of the S-0 algebra recompute what the readout already holds.
    --perturb phi1   : S2_aged predicted with Phi_i Phi_j (one Phi short)          -> must FAIL
    --perturb drop_m : off without the 2((P Q) w) P^T piece                        -> must FAIL
(b) S-3  2 (W o (N W))^T W + 4 (W o (M' W))^T W = 2 (W o (S2 W))^T W  for S2 = N + 2M'  (the exact exclusions need S2 only).
    --perturb s3     : S2 replaced by N + M'                                       -> must FAIL
(d) k1 leg  the rho^1 coefficient of kappa[h_a,h_a,h_c] for Gaussian z is 2 m_a (1-Phi_a) Phi_c s_a s_c (quadrature vs closed form);
    --perturb k1     : (1 - Phi_a) dropped                                          -> must FAIL
(c) merge obstruction (numerical, with a control): per hub the pair  w Sym3(a,a,e) + Sym3(e,e,m)  (birth term + its
    sect/diagonal-adjustment term) is NOT one three-leg factor Sym6(x,y,z): the best rank-1-factor fit leaves a relative
    residual >= 0.05 for orthonormal legs (the large-n case; random 3-d legs reported as info), while a genuine
    Sym6(x,y,z) control fits to <= 1e-10.  Fitter: Levenberg-Marquardt, 40 restarts (a plain ALS stalls near 1e-3).  (Algebra: in the basis
    (a,e,m) the pair is the cubic e (w a^2 + e m); w a^2 + e m is an irreducible quadratic, so the cubic is not a product
    of three linear forms.)
"""

from __future__ import annotations

import sys

import numpy as np


TOL = 1e-12


def sym3_hub_dense(A, E, w):
    Aw = A * w[None, :]
    t = np.einsum("ac,bc,dc->abd", Aw, A, E)
    return t + t.transpose(0, 2, 1) + t.transpose(2, 0, 1)


def contract(W, K):
    return np.einsum("ai,bj,ck,abc->ijk", W, W, W, K, optimize=True)


def coincident_from_legs(live):
    n = live[0][0].shape[0]
    N_ = np.zeros((n, n))
    M_ = np.zeros((n, n))
    Saaa = np.zeros(n)
    for A, E, w in live:
        wv = w[None, :]
        N_ += (A * A * wv) @ E.T
        M_ += ((A * E) * wv) @ A.T
        Saaa += 3.0 * (A * A * E) @ w
    return N_, M_, Saaa


def part_a(rng, perturb):
    n, m = 8, 7
    live = [
        (rng.standard_normal((n, 5)), rng.standard_normal((n, 5)), rng.uniform(0.5, 1.5, 5)),
        (rng.standard_normal((n, 3)), rng.standard_normal((n, 3)), rng.uniform(0.5, 1.5, 3)),
    ]
    W = rng.standard_normal((n, m)) * np.sqrt(2.0 / n)
    Phi = rng.uniform(0.2, 0.9, m)
    K_h = sum(sym3_hub_dense(A, E, w) for A, E, w in live)
    K_z = contract(W, K_h)
    off = np.zeros((m, m))
    hd = np.zeros(m)
    aged = []
    for A, E, w in live:
        P, Q = W.T @ A, W.T @ E
        Pw = P * P * w[None, :]
        off += Pw @ Q.T + (0.0 if perturb == "drop_m" else 2.0) * ((P * Q) * w[None, :]) @ P.T
        hd += 3.0 * (Pw * Q).sum(1)
        aged.append((Phi[:, None] * P, Phi[:, None] * Q, w))
    slice_z = np.array([[K_z[i, i, j] for j in range(m)] for i in range(m)])
    e1 = np.max(np.abs(off - slice_z)) / np.max(np.abs(slice_z))
    e1d = np.max(np.abs(np.diag(off) - hd)) / np.max(np.abs(hd))
    N_, M_, Saaa = coincident_from_legs(aged)
    S2_aged = N_ + 2.0 * M_
    pred = (
        Phi[:, None] * Phi[None, :] if perturb == "phi1" else (Phi * Phi)[:, None] * Phi[None, :]
    ) * off
    e2 = np.max(np.abs(S2_aged - pred)) / np.max(np.abs(S2_aged))
    e3 = np.max(np.abs(Saaa - Phi**3 * hd)) / np.max(np.abs(Saaa))
    ok = e1 <= TOL and e1d <= TOL and e2 <= TOL and e3 <= TOL
    print(
        f"  (a) readout == coincident slice of K_z: {e1:.1e} (diag {e1d:.1e}) | aged S2 == Phi^2 Phi o off: {e2:.1e} | "
        f"aged Saaa == Phi^3 hubdiag: {e3:.1e}  {'ok' if ok else 'VIOLATION'}"
    )
    return ok


def part_b(rng, perturb):
    n, m = 9, 8
    N_ = rng.standard_normal((n, n))
    M_ = rng.standard_normal((n, n))
    W = rng.standard_normal((n, m))
    S2 = N_ + (1.0 if perturb == "s3" else 2.0) * M_
    lhs = 2.0 * (W * (N_ @ W)).T @ W + 4.0 * (W * (M_ @ W)).T @ W
    rhs = 2.0 * (W * (S2 @ W)).T @ W
    e = np.max(np.abs(lhs - rhs)) / np.max(np.abs(lhs))
    ok = e <= TOL
    print(f"  (b) excl-all needs S2 only: {e:.1e}  {'ok' if ok else 'VIOLATION'}")
    return ok


def sym6(x, y, z):
    t = np.einsum("i,j,k->ijk", x, y, z)
    return sum(
        t.transpose(p) for p in [(0, 1, 2), (0, 2, 1), (1, 0, 2), (1, 2, 0), (2, 0, 1), (2, 1, 0)]
    )


def sym3(x, x2, y):
    t = np.einsum("i,j,k->ijk", x, x2, y)
    return t + t.transpose(0, 2, 1) + t.transpose(2, 0, 1)


E3 = np.eye(3)


def _jac(x, y, z):
    cols = []
    for slot in range(3):
        for k in range(3):
            v = [x, y, z]
            v[slot] = E3[k]
            cols.append(sym6(*v).ravel())
    return np.stack(cols, 1)


def _lm(T, p0, iters=400):
    """Levenberg-Marquardt on the 27 residuals of Sym6(x, y, z) - T (9 parameters, analytic Jacobian)."""
    p = p0.copy()
    lam = 1e-3

    def res(q):
        return (sym6(q[:3], q[3:6], q[6:]) - T).ravel()

    r = res(p)
    c = r @ r
    for _ in range(iters):
        J = _jac(p[:3], p[3:6], p[6:])
        H = J.T @ J
        step = np.linalg.solve(H + lam * np.diag(np.diag(H) + 1e-12), -(J.T @ r))
        pn = p + step
        rn = res(pn)
        cn = rn @ rn
        if cn < c:
            p, r, c = pn, rn, cn
            lam = max(lam / 3.0, 1e-12)
        else:
            lam *= 4.0
        if lam > 1e12:
            break
    return np.sqrt(c) / np.linalg.norm(T)


def best_single_factor(T, rng, restarts=40):
    """min over (x, y, z) of |T - Sym6(x, y, z)| / |T| (the set of single factors is closed, so a positive value is a
    genuine floor; a plain ALS on this problem stalls at ~1e-3 and must not be used)."""
    return min(_lm(T, rng.standard_normal(9)) for _ in range(restarts))


def part_c(rng):
    w = 0.7
    can = w * sym3(E3[0], E3[0], E3[1]) + sym3(E3[1], E3[1], E3[2])  # legs orthonormal: the large-n case
    a, e, m = (rng.standard_normal(3) for _ in range(3))
    pair = w * sym3(a, a, e) + sym3(e, e, m)
    control = sym6(rng.standard_normal(3), rng.standard_normal(3), rng.standard_normal(3))
    r_can = best_single_factor(can, rng)
    r_pair = best_single_factor(pair, rng)
    r_ctrl = best_single_factor(control, rng)
    ok = r_can >= 0.05 and r_ctrl <= 1e-10
    print(
        f"  (c) one-factor fit residual: birth+sect pair, orthonormal legs {r_can:.3f} (must stay >= 0.05; random 3-d legs "
        f"{r_pair:.2e}, info: the Frobenius distance depends on the leg geometry) | genuine Sym6 control {r_ctrl:.1e} (must reach <= 1e-10)  {'ok' if ok else 'VIOLATION'}"
    )
    return ok


def part_d(rng, perturb):
    """(d) the k1 diagonal leg.  For Gaussian (z_a, z_c) with z_c = mu_c + s_c (rho u + sqrt(1-rho^2) v), u, v iid N(0,1):
    d/drho kappa[h_a, h_a, h_c] at rho = 0 = s_c E[1_{z_c>0}] E[(h_a - m_a)^2 u] = s_c Phi_c E[(h_a - m_a)^2 u]   (v-independence),
    and the claim behind the k1 leg is E[(h_a - m_a)^2 u] = 2 s_a m_a (1 - Phi_a) (Gaussian integration by parts), so the rho^1
    coefficient is 2 m_a (1-Phi_a) Phi_c s_a s_c = what the newborn's 2 w_a d_a A_ca reproduces with d_a = m_a (1-Phi_a)/f2_a.
    The IBP step is verified by a fine 1-d trapezoid (4e6 points on [-12, 12]) of the kinked integrand -- a Gauss-Hermite rule is
    NOT accurate on ReLU (its first run gave 7e-2 'errors' that were the rule's own).  --perturb k1: (1 - Phi_a) dropped -> FAIL."""
    from math import erf, exp, pi, sqrt

    Phi = lambda t: 0.5 * (1 + erf(t / sqrt(2)))
    phi = lambda t: exp(-0.5 * t * t) / sqrt(2 * pi)
    u = np.linspace(-12.0, 12.0, 4_000_001)
    pdf = np.exp(-0.5 * u * u) / np.sqrt(2 * np.pi)
    ok = True
    worst = 0.0
    for _ in range(4):
        mu_a = rng.uniform(-1.0, 1.0)
        s_a = rng.uniform(0.5, 1.5)
        h = np.maximum(mu_a + s_a * u, 0.0)
        m_num = np.trapezoid(h * pdf, u)
        lhs = np.trapezoid((h - m_num) ** 2 * u * pdf, u)
        aa = mu_a / s_a
        m_a = mu_a * Phi(aa) + s_a * phi(aa)
        fac = 1.0 if perturb == "k1" else (1.0 - Phi(aa))
        rhs = 2.0 * s_a * m_a * fac
        err = abs(lhs - rhs) / abs(lhs)
        worst = max(worst, err)
        ok &= err <= 1e-8
    print(
        f"  (d) k = 1 leg: E[(h_a-m_a)^2 u] vs 2 s_a m_a (1-Phi_a) (rho^1 coefficient of kappa[h_a,h_a,h_c] / (s_c Phi_c)): "
        f"worst rel err {worst:.1e}  {'ok' if ok else 'VIOLATION'}"
    )
    return ok


if __name__ == "__main__":
    perturb = None
    if "--perturb" in sys.argv:
        i = sys.argv.index("--perturb")
        perturb = sys.argv[i + 1] if i + 1 < len(sys.argv) else "phi1"
    rng = np.random.default_rng(10)
    ok = part_a(rng, perturb)
    ok &= part_b(rng, perturb)
    ok &= part_d(rng, perturb)
    if perturb is None:
        ok &= part_c(rng)
    label = f"PERTURBED ({perturb})" if perturb else "self-consistent stack + obstruction"
    print(f"check10 [{label}]: {'PASS' if ok else 'FAIL'}")
    sys.exit(0 if ok else 1)
