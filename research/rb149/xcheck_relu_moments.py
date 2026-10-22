"""rb149 oracle cross-check (FIT/random synthetic inputs only; f64; seconds).
Compares the ReLU-under-Gaussian formulas used in submissions/v110_fk/estimator.py (lines ~1395-1470, re-typed here in
numpy f64 with the same recursion) against INDEPENDENT oracles:
  (O1) ARC's relu_wick_coef (alignment-research-center/mlp_cumulant_propagation, MIT) - loaded by file path, RUN only, not copied.
  (O2) scipy.integrate.quad direct integration (1-D for moments; conditional-Gaussian reduction for the bivariate moments).
  (O3) Cho-Saul / neural-tangents arc-cosine closed form for the zero-mean bivariate case.
Run: ~/dev/cohezion/.venv/bin/python research/rb149/xcheck_relu_moments.py  ARC_WICK=<path to wick.py>
"""
import importlib.util, math, os, sys, types
import numpy as np
from scipy import integrate, special

# ---- load ARC wick.py (needs a jaxtyping shim; nothing else outside torch/numpy)
jt = types.ModuleType("jaxtyping"); jt.Float = type("Float", (), {"__class_getitem__": classmethod(lambda c, k: object)})
sys.modules.setdefault("jaxtyping", jt)
wick_path = os.environ["ARC_WICK"]
spec = importlib.util.spec_from_file_location("arc_wick", wick_path)
wick = importlib.util.module_from_spec(spec); spec.loader.exec_module(wick)
import torch
def arc(mean, var, k, p=1):
    return wick.relu_wick_coef(torch.tensor(mean, dtype=torch.float64), torch.tensor(var, dtype=torch.float64), k, p).numpy()

# ---- OUR formulas (estimator.py lines 1395-1433, f64)
def ours_F(mu, var, KGC=8):
    sig = np.sqrt(var); inv_sig = 1 / sig; inv_var = inv_sig ** 2
    a = mu * inv_sig
    pdf = np.exp(-0.5 * a * a) / math.sqrt(2 * math.pi); cdf = 0.5 * special.erfc(-a / math.sqrt(2))
    sp = sig * pdf
    m1 = mu * cdf + sp
    fh2 = pdf * inv_sig; y = -a * inv_sig; fh3 = y * fh2
    mu2 = mu * mu
    m2 = (mu2 + var) * cdf + mu * sp
    m3 = (mu2 * mu + 3 * mu * var) * cdf + (mu2 + 2 * var) * sp
    fh = [m1, cdf, fh2, fh3]
    for k in range(3, KGC):                      # kinv = (k-2)*inv_var, fh[k+1] = y*fh[k] - (k-2)*inv_var*fh[k-1]
        fh.append(y * fh[k] - (k - 2) * inv_var * fh[k - 1])
    Fh = np.stack(fh, 0)
    F2h = np.concatenate([m2[None], 2 * Fh[:KGC]], 0)
    return Fh, F2h, m1, m2, m3

rng = np.random.default_rng(149)
N = 400
mu = rng.uniform(-1.2, 1.2, N); var = rng.uniform(0.3, 3.0, N)       # alpha=mu/sig spans about [-2.2, 2.2]
def rel(a, b): return np.abs(a - b) / np.maximum(np.abs(b), 1e-300)
out = {}

# T1/T2: coefficients vs ARC
Fh, F2h, m1, m2, m3 = ours_F(mu, var)
d_F = max(rel(Fh[k], arc(mu, var, k)).max() for k in range(0, 8))
d_F2 = max(rel(F2h[k], arc(mu, var, k, 2)).max() for k in range(0, 7))
d_m3 = rel(m3, arc(mu, var, 0, 3)).max()
out["T2 Fh[0..7] vs ARC relu_wick_coef(p=1)"] = d_F
out["T2 F2h[0..6] vs ARC relu_wick_coef(p=2)"] = d_F2
out["T2 m3 vs ARC relu_wick_coef(k=0,p=3)"] = d_m3

# T1: m1,m2,m3 vs quad
def qmom(m, v, p):
    s = math.sqrt(v)
    f = lambda x: max(x, 0.0) ** p * math.exp(-0.5 * ((x - m) / s) ** 2) / (s * math.sqrt(2 * math.pi))
    return integrate.quad(f, 0, m + 12 * s, epsabs=1e-15, epsrel=1e-13, limit=200)[0]
idx = range(0, N, 8)
q = np.array([[qmom(mu[i], var[i], p) for p in (1, 2, 3)] for i in idx])
out["T1 m1 vs quad"] = rel(m1[list(idx)], q[:, 0]).max()
out["T1 m2 vs quad"] = rel(m2[list(idx)], q[:, 1]).max()
out["T1 m3 vs quad"] = rel(m3[list(idx)], q[:, 2]).max()

# T3/T4: bivariate. exact E[g(x) relu(y)] by conditioning y|x, 1-D quad over x>0
def m1f(m, v): s = math.sqrt(v); a = m / s; return m * 0.5 * math.erfc(-a / math.sqrt(2)) + s * math.exp(-0.5 * a * a) / math.sqrt(2 * math.pi)
def exact_pair(mx, vx, my, vy, c, power_x):
    sx, sy = math.sqrt(vx), math.sqrt(vy); rho = c / (sx * sy)
    def f(x):
        cm = my + c / vx * (x - mx); cv = vy * (1 - rho * rho)
        return max(x, 0.0) ** power_x * math.exp(-0.5 * ((x - mx) / sx) ** 2) / (sx * math.sqrt(2 * math.pi)) * m1f(cm, cv)
    return integrate.quad(f, 0, mx + 12 * sx, epsabs=1e-15, epsrel=1e-13, limit=300)[0]

def series(Fa, Fb, c, K):  # sum_{k=1..K} Fa[k] Fb[k] c^k / k!
    return sum(Fa[k] * Fb[k] * c ** k / math.factorial(k) for k in range(1, K + 1))

res = {r: {"K4": 0, "K12": 0, "K4_211": 0, "K12_211": 0, "ref": 0} for r in (0.05, 0.3, 0.7, 0.95)}
for rho in res:
    worst = {k: 0.0 for k in res[rho]}
    for t in range(60):
        i, j = rng.integers(0, N, 2)
        mx, vx, my, vy = mu[i], var[i], mu[j], var[j]
        c = rho * math.sqrt(vx * vy)
        Fi, F2i, m1i, _, _ = ours_F(np.array([mx]), np.array([vx]), 14)
        Fj, _, m1j, _, _ = ours_F(np.array([my]), np.array([vy]), 14)
        Fi, F2i, Fj = Fi[:, 0], F2i[:, 0], Fj[:, 0]
        ex_cov = exact_pair(mx, vx, my, vy, c, 1) - m1i[0] * m1j[0]
        ex_c2 = exact_pair(mx, vx, my, vy, c, 2) - qmom(mx, vx, 2) * m1j[0]          # Cov(relu_i^2, relu_j)
        ex_k211 = ex_c2 - 2 * m1i[0] * ex_cov                                          # joint cumulant (h_i,h_i,h_j)
        sc = max(abs(ex_cov), 1e-300)
        k211 = lambda K: series(F2i, Fj, c, K) - 2 * m1i[0] * series(Fi, Fj, c, K)
        worst["K4"] = max(worst["K4"], abs(series(Fi, Fj, c, 4) - ex_cov) / sc)
        worst["K12"] = max(worst["K12"], abs(series(Fi, Fj, c, 12) - ex_cov) / sc)
        s2 = max(abs(ex_k211), 1e-300)
        worst["K4_211"] = max(worst["K4_211"], abs(k211(4) - ex_k211) / s2)
        worst["K12_211"] = max(worst["K12_211"], abs(k211(12) - ex_k211) / s2)
        # ARC-coefficient version of the same series (independent coefficients)
        Fia = [arc(np.array([mx]), np.array([vx]), k)[0] for k in range(13)]
        Fja = [arc(np.array([my]), np.array([vy]), k)[0] for k in range(13)]
        worst["ref"] = max(worst["ref"], abs(series(Fia, Fja, c, 12) - series(Fi, Fj, c, 12)) / sc)
    res[rho] = worst
out["T3/T4 bivariate (max rel err vs exact conditional-quad; K=series order)"] = res

# T5: zero-mean arc-cosine closed form (Cho-Saul / neural-tangents ReLU NNGP) vs series
w = 0.0
for rho in (0.05, 0.3, 0.7, 0.95):
    vx, vy = 1.7, 0.6; c = rho * math.sqrt(vx * vy)
    F1, _, m1a, _, _ = ours_F(np.array([0.0]), np.array([vx]), 40); F2, _, m1b, _, _ = ours_F(np.array([0.0]), np.array([vy]), 40)
    th = math.acos(rho)
    exact = math.sqrt(vx * vy) / (2 * math.pi) * (math.sin(th) + (math.pi - th) * math.cos(th)) - m1a[0] * m1b[0]
    ser = sum(F1[k, 0] * F2[k, 0] * c ** k / math.factorial(k) for k in range(1, 40))
    w = max(w, abs(ser - exact) / abs(exact))
    # NOTE zero-mean series converges slowly near rho->1 (K=40 here)
out["T5 zero-mean arccos closed form vs K=39 series (rho<=0.95)"] = w
for k, v in out.items(): print(k, "=>", v)
