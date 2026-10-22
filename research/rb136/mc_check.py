"""G-RB136 Step 1 pre-check: Monte-Carlo test of the non-tree birth
    kappa3[h_i,h_j,h_k] (i,j,k distinct) += kappa3[z_i,z_j,z_k] * (f1_i f2_j f2_k C_jk + f2_i f1_j f2_k C_ik + f2_i f2_j f1_k C_ij)
for h = ReLU(z), z = Gaussian + kappa3, f_m = E_G[ReLU^(m)(z)] (Price coefficients: f1 = Phi(mu/sigma), f2 = phi(mu/sigma)/sigma).

Design (n = 64, N = 1e6 samples, common random numbers, central difference in eps):
  z(eps) = mu + L g + M y + eps * Q(y),  g ~ N(0, I_k), y ~ N(0, I_ny) independent.
  'product' neurons a in A load NO y linearly and receive Q_a = sum of products y_p y_q (p != q);
  'y' neurons load exactly ONE y.  Then, at O(eps), the ONLY non-Gaussian cumulant is the all-distinct
  kappa3_abc = eps * sum_{products (p,q) of a} (m_b m_c [b~p, c~q] + [b~q, c~p])  (sym.), with kappa3_aab = kappa3_abb = kappa3_aaa = 0,
  and by Stein's lemma the O(eps) change of kappa3[h] on distinct triples is EXACTLY kappa3_abc * E_G[1_a 1_b 1_c] (1 = Heaviside).
  D = (k3h(+eps) - k3h(-eps)) / (2 eps) removes every even order in eps (incl. the eps^2 variance change).
  Predictors on distinct triples: P0 = f1 f1 f1 K (the chain's ageing), P1 = K o S1 (the registered term), Pex = K o E_G[1 1 1].
Pass: regression D ~ b0 P0 + b1 P1 gives b1 ~ 1 (CI excludes 0); residual(P0+P1) < residual(P0) < residual(P0-P1).
"""

import json
import math
import sys
import time

import numpy as np


rng = np.random.default_rng(136)
n, nA, ny, k = 64, 16, 24, 6
N, CH = int(sys.argv[1]) if len(sys.argv) > 1 else 1_000_000, 125_000
eps = float(sys.argv[2]) if len(sys.argv) > 2 else 0.3

Yn = np.arange(nA, n)  # 48 y-neurons, 2 per y
load = np.repeat(np.arange(ny), 2)  # y index loaded by each y-neuron
M = np.zeros((n, ny))
M[Yn, load] = rng.choice([-1, 1], size=Yn.size) * rng.uniform(0.6, 0.9, size=Yn.size)
L = rng.standard_normal((n, k)) * 0.45 + 0.35 * rng.choice(
    [-1, 1], size=(1, k)
)  # strong common factors -> |rho| ~ 0.3-0.5
mu = rng.uniform(-0.5, 0.5, size=n)
prods = [
    [tuple(rng.choice(ny, 2, replace=False)) for _ in range(3)] for _ in range(nA)
]  # 3 products per A-neuron

# analytic z-side kappa3 / eps (full symmetric tensor)
K = np.zeros((n, n, n))
for a in range(nA):
    for p, q in prods[a]:
        bp, bq = Yn[load == p], Yn[load == q]
        for b in bp:
            for c in bq:
                v = M[b, p] * M[c, q]
                for x, y_, z_ in ((a, b, c), (a, c, b), (b, a, c), (c, a, b), (b, c, a), (c, b, a)):
                    K[x, y_, z_] += v
Sig = L @ L.T + M @ M.T  # covariance at eps = 0 (exact)
sd = np.sqrt(np.diag(Sig))
al = mu / sd
Phi = 0.5 * (1 + np.vectorize(math.erf)(al / math.sqrt(2)))
pdf = np.exp(-0.5 * al**2) / math.sqrt(2 * math.pi)
f1, f2 = Phi, pdf / sd
C = Sig.copy()
np.fill_diagonal(C, 0.0)
rho = C / np.outer(sd, sd)
S1 = (
    f1[:, None, None] * (f2[:, None] * C * f2[None, :])[None, :, :]
    + f1[None, :, None] * (f2[:, None] * C * f2[None, :])[:, None, :]
    + f1[None, None, :] * (f2[:, None] * C * f2[None, :])[:, :, None]
)


def k3_of(H, mean):
    Hc = H - mean
    out = np.empty((n, n, n))
    for a in range(n):
        out[a] = (Hc * Hc[:, a : a + 1]).T @ Hc
    return out


t0 = time.time()
sums = {"p": np.zeros(n), "m": np.zeros(n), "0": np.zeros(n)}
raw = {}
# pass 1: means;  pass 2: central third moments (same seeds -> identical samples)
for pas in (1, 2):
    acc = {key: np.zeros((n, n, n)) for key in ("p", "m")}
    acc3 = np.zeros((n, n, n))  # E_G[1 1 1]
    for c0 in range(0, N, CH):
        r = np.random.default_rng(10_000 + c0)
        g = r.standard_normal((CH, k))
        y = r.standard_normal((CH, ny))
        zG = mu + g @ L.T + y @ M.T
        Qy = np.zeros((CH, n))
        for a in range(nA):
            for p, q in prods[a]:
                Qy[:, a] += y[:, p] * y[:, q]
        for key, s in (("p", eps), ("m", -eps)):
            h = np.maximum(zG + s * Qy, 0.0)
            if pas == 1:
                sums[key] += h.sum(0)
            else:
                Hc = h - raw[key]
                for a in range(n):
                    acc[key][a] += (Hc * Hc[:, a : a + 1]).T @ Hc
        if pas == 2:
            I = (zG > 0).astype(np.float64)
            for a in range(n):
                acc3[a] += (I * I[:, a : a + 1]).T @ I
    if pas == 1:
        raw = {key: sums[key] / N for key in ("p", "m")}
k3p, k3m = acc["p"] / N, acc["m"] / N
EG111 = acc3 / N
D = (k3p - k3m) / (2 * eps)

ii, jj, kk = np.meshgrid(np.arange(n), np.arange(n), np.arange(n), indexing="ij")
dist = (ii != jj) & (jj != kk) & (ii != kk)
sig = dist & (K != 0)
null = dist & (K == 0)
P0 = (f1[:, None, None] * f1[None, :, None] * f1[None, None, :]) * K
P1 = K * S1
Pex = K * EG111
d, x0, x1 = D[sig], P0[sig], P1[sig]
X = np.stack([x0, x1], 1)
beta, *_ = np.linalg.lstsq(X, d, rcond=None)
res = d - X @ beta
s2 = res @ res / (len(d) - 2)
cov = s2 * np.linalg.inv(X.T @ X)
se = np.sqrt(np.diag(cov))
rn = lambda v: float(np.sqrt(np.mean(v**2)))
out = dict(
    n=n,
    N=N,
    eps=eps,
    n_signal_triples=int(sig.sum()),
    n_null_triples=int(null.sum()),
    rho_offdiag_absmean=float(np.abs(rho[~np.eye(n, dtype=bool)]).mean()),
    rho_offdiag_absmax=float(np.abs(rho[~np.eye(n, dtype=bool)]).max()),
    beta_tree=float(beta[0]),
    se_tree=float(se[0]),
    beta_nt=float(beta[1]),
    se_nt=float(se[1]),
    rms_D=rn(d),
    rms_resid_tree_only=rn(d - x0),
    rms_resid_tree_plus_nt=rn(d - x0 - x1),
    rms_resid_tree_minus_nt=rn(d - x0 + x1),
    rms_resid_exact_EG111=rn(d - Pex[sig]),
    rms_nt_term=rn(x1),
    rms_null_D=rn(D[null]),
    secs=round(time.time() - t0, 1),
)
print(json.dumps(out, indent=1))
json.dump(out, open(__file__.replace("mc_check.py", f"mc_check_N{N}_e{eps:g}.json"), "w"), indent=1)
