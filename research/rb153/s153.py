"""G-RB85 copy (adds INJ_KEYS k3 = diag-only kappa3 injection; INJECT may be set at runtime as a dict) of the G-RB73 copy of research/rebuild/srcchain_aug.py (2026-10-12) with ONE addition: a K4HOOK (set srcchain_k4p.K4HOOK = f(l, ctx) -> k4z)
called after the layer's kappa4 (4)-slice is final and before the ReLU step / last-layer read; K4HOOK = None reproduces srcchain_aug bit-for-bit.
Original docstring follows. G-RB30/31 copy of srcchain.py: pair-structured kappa4 from live modes (ARC augmented harmonic matrix H / Puffi SSC response closure).
env AUG=off|arc|ssc METRIC=avg|exact FEED=keep|proj LAMBDA=<npz with lam (16,4,4)> DUMP=<npz path for the Lambda fit> DIAG=1.  Rebuild S2: the k3chain `feed_k5 + d21rank16 + adj fit_r16` chain re-expressed PER SOURCE in the {P, A, thin} form
(DESIGN.md "S2/S3 — cost structure"; credit: the collapse is 504aldo's "7 -> 4 units per source-layer", thread 18218 S2.1, re-derived
from the prose; the age-gated shared subspace is their S2.4).  numpy f64; this file is the exactness ORACLE for the flopscope port.

Source b (born at the ReLU of layer b) = sum over hub j of  Sym(alpha P_j (x) X_j (x) Y_j)  for the blocks
  G11 (3): X = A,            Y = A d(f2) + T1 c1 + T2 c2
  G12 (3): X = T2 c3,        Y = A d(f2)
  G21 (1.5): X = T1 c4,      Y = A d(f3)
  feed (1): X = A d(f1),     Y = 3 u 1^T
  adj (1):  X = P,           Y = A d(t) + P d(s) + Z c5
P = I at birth, A = f1 o C_z, D21 ~ U B (rank r), T1 = f1 o B^T, T2 = f2 o U, c1 = U^T d(f3/2), c2 = B d(f2/2), c3 = B/2, c4 = U^T,
u = (kappa/6) f2, Vadj = A d(t) + diag(s) + R, R ~ Z c5.  All of P, A, T1, T2, Z, u are transported X <- Phi o (W^T X); the c's,
f's, t, s are static.  Old tier (age >= gate): P_b = Q F_P, A_b = Q F_A with a shared transported Q (n x r) and static F.
usage: python srcchain.py --nets 0 [--aged 4:384,7:224] [--check est_adj_r16_00000.npy]
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path

import numpy as np


AUG = os.environ.get("AUG", "off")
METRIC = os.environ.get("METRIC", "avg")
FEED = os.environ.get("FEED", "keep")
LAMBDA = np.load(os.environ["LAMBDA"])["lam"] if os.environ.get("LAMBDA") else None
DUMP = os.environ.get("DUMP")
DIAG = bool(os.environ.get("DIAG"))
MODES = ["I", "C", "B4", "H"]
SECT = set(os.environ.get("SECT", "k4,q22,k31").split(","))
QC = (
    np.load(os.environ["QCOEF"])["c"] if os.environ.get("QCOEF") else None
)  # (16,6) Puffi C3 coefficients -> mode 'Q'
FITQ = os.environ.get(
    "FITQ"
)  # path: accumulate the 6x6 normal equations of the Q bases vs the MC (3,1) target per layer/half
MEM = float(os.environ.get("MEM", "0"))  # Puffi D8 response memory beta (-0.3)
FREE = bool(os.environ.get("FREE"))  # G-RB34: free-transport modes only (I, C, Q_free)
EXTRA = [m for m in os.environ.get("EXTRA", "").split(",") if m]
L0 = int(
    os.environ.get("L0", "0")
)  # G-RB54 depth gate: the SSC/ARC closure (and the h-side modes feeding it) are active only on layers l >= L0 (0 = every layer, unchanged)
INJECT = (
    np.load(os.environ["INJECT"]) if os.environ.get("INJECT") else None
)  # G-RB58: MC cache (mc_cache_alllayers_mlp<mid>_N*.npz: mu_z, var_z, T_z per z-layer) whose exact moments replace the chain's at INJ_LAYERS
INJ_LAYERS = {
    int(x) for x in os.environ.get("INJ_LAYERS", "1,2").split(",")
}  # 0-based z-layer index l (l=1 -> the 2nd pre-activation)
INJ_KEYS = set(os.environ.get("INJ_KEYS", "mu,var,T").split(","))
VCAP = None  # G-RB153: list -> capture
VCAL = None  # G-RB153: f(l, mu_z, var_z, k3) -> yhat
VMODE = "diag"
VLAYERS = {11, 12, 13, 14, 15}
OLDALPHA = 1.0
DUMPSRC = os.environ.get(
    "DUMPSRC", ""
)  # G-RB60: npz path prefix; per layer, dump the z-side (2,1) read summed by source AGE (1..5, 6+) + Cz/mu_z/var_z/cdf/f1-3 for the old-tier oracle
_DUMPSRC = []
PRUNE = float(
    os.environ.get("PRUNE", "0")
)  # G-RB59: zero the kappa3 legs (rows) of neurons whose gate probability Phi < PRUNE at the ReLU ageing step
_PRUNE_FRAC = []
PBASIS = bool(
    os.environ.get("PBASIS")
)  # G-RB63: own-tier basis from the P (propagator) leg ALONE; A = P A_b exactly, so A is expressed in that basis (default off = bit-identical)
K4DIAG = os.environ.get(
    "K4DIAG", ""
)  # G-RB37 lead 1: 'w4' = exact per-neuron transport sum_a W_ai^4 k4h_a + 6 lam diag((WoW)^T C_h,off (WoW)) replaces the (4) slice  # G-RB35: extra free modes 'TC' = P_off[(Tz+Tz^T) o Sigma_z]/vbar, 'U' = uz uz^T (transported kappa4-feed vector)
if QC is not None or FITQ:
    MODES = (["I", "C", "Q"] if FREE else ["I", "C", "B4", "Q"]) + EXTRA
_FITQ = []
_LAST_Q = [None]  # which sectors take the aug value (others keep the lean GSM form)
_DUMP = []
_MC = None


HERE = Path("~/cohezion-labs/arc-whitebox/research/rebuild")  # G-RB73: resolve helpers/tables from research/rebuild
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent))
K4HOOK = None
SW = {}  # G-RB91 screen switches (set by run91.py)
PR_LOG = {}
import k3chain as K  # noqa: E402
import proto_cov4 as C4  # noqa: E402
import proto_r2 as R  # noqa: E402
import proto_sectcost as SC  # noqa: E402


N, D = R.N, R.D


def range_finder(G_apply, r, n, seed, power=1):
    """orthonormal Q (n x r) spanning the dominant range of the symmetric PSD operator G (given as a function); randomized,
    one power iteration; QR via numpy (the port uses fnp.linalg.qr). Replaces eigh (pathologically slow on this host)."""
    rng = np.random.default_rng(seed)
    Y = G_apply(rng.standard_normal((n, r + 16)))
    for _ in range(power):
        Y, _ = np.linalg.qr(Y)
        Y = G_apply(Y)
    Q, _ = np.linalg.qr(Y)
    return Q[:, :r]


RF = dict(on=False, power=0)
PROBE = []  # G-RB142 step-0 probe records (per entry / nesting event)


def _admit(Qb, L):
    """G-RB142: coefficients of L in the (transported, non-orthonormal) basis Qb: Gram solve; nosolve = the M2 mutant (Q^T L)."""
    if SW.get("nosolve"):
        return Qb.T @ L
    return np.linalg.solve(Qb.T @ Qb, Qb.T @ L)


RCNT = [0]
K31L = np.ones(16)
Q22L = np.ones(16)  # G-RB97 per-layer Q22 multiplier


def rank_r_rf(M, r, seed, power=0):
    """port-faithful rank-r: randomized range finder (oversample 8, `power` extra iterations), small SVD of Q^T M."""
    rng = np.random.default_rng(seed)
    Y = M @ rng.standard_normal((M.shape[1], r + int(SW.get('os', 8))))
    for _ in range(power):
        Y, _ = np.linalg.qr(Y)
        Y = M @ (M.T @ Y)
    Q1, _ = np.linalg.qr(Y)
    B1 = Q1.T @ M
    U2, s2, Vt = np.linalg.svd(B1, full_matrices=False)
    return Q1 @ U2[:, :r], s2[:r, None] * Vt[:r]


def rank_r(M, r):
    """top-r factorisation M ~ U @ B (U n x r orthonormal). Prototype: exact SVD; the port uses a range finder."""
    if RF["on"] and not SW.get('exact_svd'):
        if SW.get('fixseed'):  # G-RB96: call-counter seed -> arms paired
            RCNT[0] += 1
            return rank_r_rf(M, r, seed=777000 + RCNT[0], power=RF["power"])
        return rank_r_rf(M, r, seed=int(abs(float(M[0, 1])) * 1e9) % 100000, power=RF["power"])
    U, s, Vt = np.linalg.svd(M, full_matrices=False)
    return U[:, :r], s[:r, None] * Vt[:r]


def read_block(alpha, P, X, Y):
    """eq (16) for sum_j Sym(alpha P_j x X_j x Y_j): the (2,1)-slice matrix (diag = (3)-slice)."""
    return (alpha / 3.0) * ((X * Y) @ P.T + (P * Y) @ X.T + (P * X) @ Y.T)


def read_block_identity(alpha, X, Y):
    """read_block with P = I (birth): O(n^2) closed form: (X o Y) + diag(dY) X^T + diag(dX) Y^T  (times alpha/3)."""
    dX, dY = np.diag(X), np.diag(Y)
    return (alpha / 3.0) * ((X * Y) + dY[:, None] * X.T + dX[:, None] * Y.T)


def source_legs_z(s, Qz=None):
    """z-side dense legs of a source (after transport); returns dict of (alpha, X, Y) blocks plus Pz, Az."""
    if Qz is None:
        Pz, Az = s["Pz"], s["Az"]
    else:
        Pz, Az = Qz @ s["FP"], Qz @ s["FA"]
    T1, T2, Z, u = s["T1z"], s["T2z"], s["Zz"], s["uz"]
    f1, f2, f3, t, sv = s["f1"], s["f2"], s["f3"], s["t"], s["s"]
    blocks = [
        (3.0, Az, Az * f2[None, :] + T1 @ s["c1"] + T2 @ s["c2"]),
        (3.0, T2 @ s["c3"], Az * f2[None, :]),
        (1.5, T1 @ s["c4"], Az * f3[None, :]),
        (1.0, Az * f1[None, :], np.outer(3.0 * u, np.ones(N))),
        (1.0, Pz, Az * t[None, :] + Pz * sv[None, :] + Z @ s["c5"]),
    ]
    return Pz, Az, blocks


def post_sig(l, S):
    """cs: Cauchy-Schwarz clip of the off-diagonal of Sigma_h; psd: eigenvalue clip (psd=1 keeps the diagonal, psd=2 does not); shr: (1-a)S + a diag(S)"""
    if 'eps' in SW:
        S = S * (1.0 + float(SW['eps']))
    if not (SW.get('cs') or SW.get('psd') or SW.get('shr')):
        return S
    d = np.diag(S).copy()
    if SW.get('cs'):
        lim = np.sqrt(np.outer(d, d))
        viol = np.abs(S) > lim
        np.fill_diagonal(viol, False)
        PR_LOG.setdefault('cs_viol', {})[l] = int(viol.sum())
        S = np.clip(S, -lim, lim)
    if SW.get('psd'):
        w, V = np.linalg.eigh(0.5 * (S + S.T))
        PR_LOG.setdefault('neg', {})[l] = (int((w < 0).sum()), float(-w[w < 0].sum() / max(w.sum(), 1e-300)))
        S2 = (V * np.maximum(w, 0.0)) @ V.T
        if int(SW['psd']) == 1:
            dd = np.diag(S2)
            sc = np.sqrt(np.maximum(d, 1e-300) / np.maximum(dd, 1e-300))
            S2 = S2 * sc[:, None] * sc[None, :]
        S = S2
    if SW.get('shr'):
        a = float(SW['shr'])
        S = (1 - a) * S + a * np.diag(np.diag(S))
    return S


def relu_step_91(mu_z, Sig_z, Tz, k4, Qoff, K31):
    """C4.relu_step_ext with the optional Stein-consistent m2c (stein=1 replace, 0<stein<1 blend)."""
    if not SW.get('stein'):
        if any(k in SW for k in ('q22S', 'q22T', 'k31S', 'k31T', 'tzS')):
            return relu_step_split(mu_z, Sig_z, Tz, k4, Qoff, K31)
        return C4.relu_step_ext(mu_z, Sig_z, Tz, k4, Qoff, K31, second=bool(SW.get('second')))
    var = np.maximum(np.diag(Sig_z), 1e-12)
    sig, a, pdf, cdf, m1, m2, m3 = R.relu_moments(mu_z, var)
    fh = R.coeffs_relu(sig, a, pdf, cdf, m1, C4.KMAX)
    f2h = R.coeffs_relu2(sig, a, pdf, cdf, m1, m2, C4.KMAX)
    C = Sig_z.copy()
    np.fill_diagonal(C, 0.0)
    k3 = np.diag(Tz)
    Qz = Qoff.copy()
    np.fill_diagonal(Qz, 0.0)
    m1c = m1 + C4.marginal_corr(fh, k3, k4, False, None)
    m2c = m2 + C4.marginal_corr(f2h, k3, k4, False, None)
    Eh = lambda j: fh[j] + k3 / 6.0 * fh[j + 3] + k4 / 24.0 * fh[j + 4]
    m2s = mu_z * m1c + var * Eh(1) + k3 / 2.0 * Eh(2) + k4 / 6.0 * Eh(3)
    PR_LOG.setdefault('stein_gap', []).append( float(np.sqrt(np.mean((m2s - m2c) ** 2)) / np.sqrt(np.mean(m2c**2))))
    lamS = float(SW['stein'])
    m2c = (1 - lamS) * m2c + lamS * m2s
    m3c = m3 + k3 / 6.0 * (6.0 * cdf) + k4 / 24.0 * (6.0 * pdf / sig)
    E11 = C4.expectation_ext(fh, fh, C, k3, Tz, k4, Qz, K31, C4.KH)
    E21 = C4.expectation_ext(f2h, fh, C, k3, Tz, k4, Qz, K31, C4.KH)
    Sig = E11 - np.outer(m1c, m1c)
    T = E21 - np.outer(m2c, m1c) - 2.0 * m1c[:, None] * Sig
    np.fill_diagonal(Sig, np.maximum(m2c - m1c**2, 0.0))
    np.fill_diagonal(T, m3c - 3 * m2c * m1c + 2 * m1c**3)
    return m1c, Sig, T


def relu_step_split(mu_z, Sig_z, Tz, k4, Qoff, K31):
    """C4.relu_step_ext copy (second=False, own_hi=None) with consumer-specific scales (G-RB94): Sigma consumers (E11) use q22S/k31S/tzS,
    the kappa3 consumers (E21) use q22T/k31T; all default 1 -> identical to C4.relu_step_ext."""
    var = np.maximum(np.diag(Sig_z), 1e-12)
    sig, a, pdf, cdf, m1, m2, m3 = R.relu_moments(mu_z, var)
    fh = R.coeffs_relu(sig, a, pdf, cdf, m1, C4.KMAX)
    f2h = R.coeffs_relu2(sig, a, pdf, cdf, m1, m2, C4.KMAX)
    C = Sig_z.copy()
    np.fill_diagonal(C, 0.0)
    k3 = np.diag(Tz)
    Qz = Qoff.copy()
    np.fill_diagonal(Qz, 0.0)
    m1c = m1 + C4.marginal_corr(fh, k3, k4, False, None)
    m2c = m2 + C4.marginal_corr(f2h, k3, k4, False, None)
    m3c = m3 + k3 / 6.0 * (6.0 * cdf) + k4 / 24.0 * (6.0 * pdf / sig)
    g_ = lambda k: float(SW.get(k, 1.0))
    E11 = C4.expectation_ext(fh, fh, C, k3, Tz * g_('tzS'), k4, Qz * g_('q22S'), K31 * g_('k31S'), C4.KH)
    E21 = C4.expectation_ext(f2h, fh, C, k3, Tz, k4, Qz * g_('q22T'), K31 * g_('k31T'), C4.KH)
    Sig = E11 - np.outer(m1c, m1c)
    T = E21 - np.outer(m2c, m1c) - 2.0 * m1c[:, None] * Sig
    np.fill_diagonal(Sig, np.maximum(m2c - m1c**2, 0.0))
    np.fill_diagonal(T, m3c - 3 * m2c * m1c + 2 * m1c**3)
    return m1c, Sig, T


def src_closure(
    ws, g_table, kappa, *, rank=16, aged=None, log=None, trim=True, lc_hook=None, mc_seed=None
):
    global _MC
    mu = np.zeros(N)
    Sig = np.eye(N)
    modes_h = None  # G-RB30/31: h-side response modes of the previous layer (B4 matrix, H vector); C is carried as Sig, I is implicit
    cdf_prev = None
    srcs = []  # young sources (dense P, A)
    old = []  # old sources (FP, FA in the shared basis Q)
    Q = None  # shared basis, h side (n x r)
    Q2 = None  # G-RB142: shared NESTED basis (n x r2), h side; sources with grp == 2 read through it
    PROBE.clear()
    rows = []
    for l, w_ in enumerate(ws):
        t0 = time.time()
        last = l == D - 1
        W = w_.astype(np.float64)
        mu_z = W.T @ mu
        Sig_z = W.T @ Sig @ W
        var_z = np.maximum(np.diag(Sig_z), 1e-12)
        Cz = Sig_z.copy()
        np.fill_diagonal(Cz, 0.0)
        # ---- transport + read
        Tz = np.zeros((N, N))
        per_src_T = []
        Qz = W.T @ Q if Q is not None else None
        Q2z = W.T @ Q2 if Q2 is not None else None  # G-RB142
        for s in old:
            if "Qb" in s:
                s["Qbz"] = W.T @ s["Qb"]
        for s in srcs + old:
            s["Pz"] = W.T @ s["P"] if "P" in s else None
            s["Az"] = W.T @ s["A"] if "A" in s else None
            for k in ("T1", "T2", "Z"):
                s[k + "z"] = W.T @ s[k]
            s["uz"] = W.T @ s["u"]
            Pz, Az, blocks = source_legs_z(s, None if "P" in s else (s["Qbz"] if "Qb" in s else (Q2z if s.get("grp") == 2 else Qz)))  # G-RB142: grp 2 -> shared nested basis
            if last and trim:
                d3 = sum(alpha * np.sum(Pz * X * Y, axis=1) for alpha, X, Y in blocks)
                Tb = np.diag(d3)
            else:
                Tb = sum(read_block(alpha, Pz, X, Y) for alpha, X, Y in blocks)
            if OLDALPHA != 1.0 and any(s is o for o in old):  # G-RB153 AM3: old-tier damping of the transported old-source read
                Tb = OLDALPHA * Tb
            per_src_T.append(Tb)
            Tz += Tb
        if (
            INJECT is not None and l in INJ_LAYERS
        ):  # G-RB58 oracle injection of the exact z-moments at this layer
            if "mu" in INJ_KEYS:
                mu_z = INJECT["mu_z"][l].copy()
            if (
                "Sig" in INJ_KEYS
            ):  # full exact covariance (official-net caches, mc_official_cache.py)
                Sig_z = INJECT["Sig_z"][l].copy()
                var_z = np.maximum(np.diag(Sig_z), 1e-12)
                Cz = Sig_z.copy()
                np.fill_diagonal(Cz, 0.0)
            if "var" in INJ_KEYS:
                Sig_z = Sig_z.copy()
                _lam = float(INJECT.get("lam", 1.0)) if isinstance(INJECT, dict) else 1.0  # G-RB85: chain + lam (inj - chain)
                np.fill_diagonal(Sig_z, np.diag(Sig_z) + _lam * (INJECT["var_z"][l] - np.diag(Sig_z)))
                var_z = np.maximum(np.diag(Sig_z), 1e-12)
                Cz = Sig_z.copy()
                np.fill_diagonal(Cz, 0.0)
            if "T" in INJ_KEYS:
                Tz = INJECT["T_z"][l].copy()
            if "k3" in INJ_KEYS:  # G-RB85: exact per-neuron kappa3 diag only (off-diagonal (2,1) slice kept)
                Tz = Tz.copy()
                _lam = float(INJECT.get("lam", 1.0)) if isinstance(INJECT, dict) else 1.0
                np.fill_diagonal(Tz, np.diag(Tz) + _lam * (INJECT["k3_z"][l] - np.diag(Tz)))
        if VCAP is not None and l in VLAYERS:  # G-RB153 capture of the chain's own z-state at the injection point (read-only)
            _sd = np.sqrt(var_z)
            VCAP.append(dict(l=l, mu_z=mu_z.copy(), var_z=var_z.copy(), k3=np.diag(Tz).copy()))
        if VCAL is not None and l in VLAYERS:  # G-RB153 sigma^2 calibration channel: var_z <- var_z (1 + yhat)
            _f = 1.0 + VCAL(l, mu_z, var_z, np.diag(Tz))
            if VMODE == "corr":
                _dd = np.sqrt(_f)
                Sig_z = Sig_z * _dd[:, None] * _dd[None, :]
            else:
                Sig_z = Sig_z.copy()
                np.fill_diagonal(Sig_z, np.diag(Sig_z) * _f)
            var_z = np.maximum(np.diag(Sig_z), 1e-12)
            Cz = Sig_z.copy()
            np.fill_diagonal(Cz, 0.0)
        if DUMPSRC:  # G-RB60 oracle dump (additive; read-only w.r.t. the chain's state)
            buckets = {k: np.zeros((N, N)) for k in ("T1", "T2", "T3", "T4", "T5", "T6p")}
            for s, Tb in zip(srcs + old, per_src_T):
                age = l - s["b"]
                buckets["T%d" % age if age <= 5 else "T6p"] += Tb
            _DUMPSRC.append(
                dict(
                    l=l,
                    Cz=Cz.astype(np.float32),
                    mu_z=mu_z.copy(),
                    var_z=var_z.copy(),
                    **{k: v.astype(np.float32) for k, v in buckets.items()},
                )
            )
        k3 = np.diag(Tz).copy()
        g_ = float(g_table[l])
        kap = float(kappa[l])
        aug_sect = None
        if AUG != "off" and modes_h is not None and l >= L0:
            # ---- transported modes: I -> M = W^T W (exact) or diag(m_i) (avg metric); C -> Sig_z (already formed); B4 -> W^T B4 W; H -> W^T diag(H) W
            m_i = np.einsum("ai,ai->i", W, W)
            Mt = W.T @ W if METRIC == "exact" else np.diag(m_i)
            B4t = W.T @ modes_h["B4"] @ W
            Ht = W.T @ (modes_h["H"][:, None] * W)
            Bt = {"I": Mt, "C": Sig_z, "B4": B4t, "H": Ht}
            if (FITQ or QC is not None) and FREE:
                # G-RB34 free-transport bases at z: v̄ Σ_z, ½ m̄ (Tz+Tzᵀ), tz μᵀ + μ tzᵀ, vz vzᵀ, (Wᵀ1)(Wᵀ1)ᵀ   (t, v, 1 transported as vectors)
                tz = W.T @ modes_h["t"]
                vz = W.T @ modes_h["v"]
                oz = W.T @ np.ones(N)
                Qb = [
                    0.5 * float(modes_h["mbar"]) * (Tz + Tz.T),
                    np.outer(tz, mu_z) + np.outer(mu_z, tz),
                    np.outer(vz, vz),
                    np.outer(oz, oz),
                ]  # v̄ Σ_z basis dropped: collinear with the C mode (G-RB34 rung 1)
                for q in Qb:
                    np.fill_diagonal(q, 0.0)
            elif FITQ or QC is not None:
                Qb = [W.T @ q @ W for q in modes_h["Qb"]]  # the six C3 bases, transported
            if FITQ:
                if _MC is None:
                    _MC = np.load(HERE.parent / f"mc_oracle_{mc_seed}_N300000.npz")
                OFF_ = ~np.eye(N, dtype=bool)
                Xq = np.stack([(q + q.T)[OFF_] for q in Qb], 1)
                rec = dict(l=l, A=Xq.T @ Xq)
                for hf in ("A", "B"):
                    K31m = C4.sectors(_MC, hf, l)["K31"]
                    y = (K31m + K31m.T)[OFF_]
                    rec["b" + hf] = Xq.T @ y
                    rec["yy" + hf] = float(y @ y)
                _FITQ.append(rec)
                Bt["Q"] = np.zeros(
                    (N, N)
                )  # c-fit pass: record the bases, no Q feedback into the chain (Puffi fit Q to measured targets first)
            else:
                Bt["Q"] = sum(float(QC[l - 1, k]) * Qb[k] for k in range(len(Qb))) / float(
                    modes_h["vbar"]
                )
            if "TC" in EXTRA:
                tc = (Tz + Tz.T) * Sig_z / float(modes_h["vbar"])
                np.fill_diagonal(tc, 0.0)
                Bt["TC"] = tc
            if "U" in EXTRA:
                uz_ = W.T @ modes_h["u"]
                Bt["U"] = np.outer(uz_, uz_)
            if MEM != 0.0 and modes_h.get("Bmem") is not None:
                Bmem = {k: W.T @ v @ W for k, v in modes_h["Bmem"].items()}
            d = {k: np.diag(v).copy() for k, v in Bt.items()}
            if MEM != 0.0 and modes_h.get("Bmem") is not None:
                dm = {k: np.diag(v).copy() for k, v in Bmem.items()}
            if AUG == "arc":
                lam = np.zeros((4, 4))
                lam[0, 3] = lam[3, 0] = 1.0  # kappa4 = g(H) = S(I,H) + S(H,I)
            else:
                lam = LAMBDA[l]
            k4z = np.zeros(N)
            Q22a = np.zeros((N, N))
            K31a = np.zeros((N, N))
            Fproj = np.zeros((N, N))
            for ia, na in enumerate(MODES):
                for ib, nb in enumerate(MODES):
                    L_ = lam[ia, ib]
                    if L_ == 0.0:
                        continue
                    k4z += 3.0 * L_ * d[na] * d[nb]  # (4):      3 Ba_ii Bb_ii
                    Q22a += L_ * (
                        np.outer(d[na], d[nb]) + 2.0 * Bt[na] * Bt[nb]
                    )  # (2,2):    Ba_ii Bb_jj + 2 Ba_ij Bb_ij
                    K31a += L_ * (
                        2.0 * d[na][:, None] * Bt[nb] + Bt[na] * d[nb][None, :]
                    )  # (3,1): 2 Ba_ii Bb_ij + Ba_ij Bb_ii
                    Fproj += (
                        L_ * float(d[na].mean()) * Bt[nb]
                    )  # (2,1,1) first term, hub-averaged: mean_i(Ba_ii) Bb_jk
            if (
                MEM != 0.0 and modes_h.get("Bmem") is not None
            ):  # Puffi D8: beta x the previous layer's closure, gated and transported
                lp = modes_h["lam_prev"]
                for ia, na in enumerate(MODES):
                    for ib, nb in enumerate(MODES):
                        L_ = MEM * lp[ia, ib]
                        if L_ == 0.0:
                            continue
                        k4z += 3.0 * L_ * dm[na] * dm[nb]
                        Q22a += L_ * (np.outer(dm[na], dm[nb]) + 2.0 * Bmem[na] * Bmem[nb])
                        K31a += L_ * (2.0 * dm[na][:, None] * Bmem[nb] + Bmem[na] * dm[nb][None, :])
            np.fill_diagonal(Q22a, 0.0)
            np.fill_diagonal(K31a, 0.0)
            np.fill_diagonal(Fproj, 0.0)
            if FEED == "proj":
                kap = 3.0 * float(np.sum(Fproj * Cz) / max(np.sum(Cz * Cz), 1e-300))
            aug_sect = (Q22a, K31a)
            if "k4" not in SECT:
                k4z = g_ * var_z**2
            if K4DIAG == "w4" and modes_h.get("k4h") is not None:
                W2 = W * W
                k4z = (W2 * W2).T @ modes_h["k4h"] + 6.0 * float(kappa[l - 1]) * np.einsum(
                    "ai,ab,bi->i", W2, modes_h["Choff"], W2
                )
            if K4DIAG == "w4q" and modes_h.get("k4h") is not None:
                # G-RB37 corrected form (= check_k4diag.py): exact W^{x4} transport of the (4) + (2,2) h-slices; the (2,2) slice is the chain's own
                # central kappa4(h_a,h_a,h_b,h_b) (power-cumulant series), NOT lambda*C_h; ordered pairs a!=b carry 4!/(2!2!)/2 = 3
                W2 = W * W
                k4z = (W2 * W2).T @ modes_h["k4h"] + 3.0 * np.einsum(
                    "ai,ab,bi->i", W2, modes_h["Qh"], W2
                )
            if DUMP:
                _DUMP.append(
                    dict(
                        l=l,
                        d=np.stack([d[k] for k in MODES]),
                        k4z=k4z.copy(),
                        B=np.stack([Bt[k] for k in MODES if k != "H"]).astype(np.float32),
                    )
                )
            if DIAG:
                mc = ""
                if mc_seed is not None:
                    if _MC is None:
                        _MC = np.load(HERE.parent / f"mc_oracle_{mc_seed}_N300000.npz")
                    k4mc = C4.sectors(_MC, "A", l)["k4"]
                    mc = f" MC {k4mc.mean():.3e} (ratio {k4z.mean() / k4mc.mean():.2f})"
                print(
                    f"  l={l} k4z mean {k4z.mean():.3e} min {k4z.min():.2e} lean {float(g_ * (var_z**2).mean()):.3e}{mc} kap {kap:+.3e} (table {float(kappa[l]):+.3e})",
                    flush=True,
                )
        else:
            k4z = g_ * var_z**2
        if K4HOOK is not None:  # G-RB73
            k4z = K4HOOK(
                l,
                dict(
                    k4z=k4z,
                    mu_z=mu_z,
                    Sig_z=Sig_z,
                    Tz=Tz,
                    var_z=var_z,
                    g=g_,
                    Q22=aug_sect[0] if aug_sect is not None else None,
                    K31=aug_sect[1] if aug_sect is not None else None,
                    W=W,
                    last=last,
                    mu_h=mu,
                    Sig_h=Sig,
                    modes_h=modes_h,
                ),
            )
        sig, a, pdf, cdf, m1, m2, m3 = R.relu_moments(mu_z, var_z)
        fh = R.coeffs_relu(sig, a, pdf, cdf, m1, 5)
        if last:
            m1c_last = m1 + k3 / 6.0 * fh[3] + float(SW.get('g4t', 1.0)) * k4z / 24.0 * fh[4]
            if (
                lc_hook is not None
            ):  # last layer: mean-only readout; Sig/T placeholders (only the LITE features are meaningful here)
                Zn_ = np.zeros((N, N))
                m1c_last = lc_hook(
                    l,
                    dict(
                        mu=m1c_last,
                        Sig=Zn_,
                        T=Zn_,
                        mu_z=mu_z,
                        Sig_z=Sig_z,
                        Tz=np.diag(k3),
                        var_z=var_z,
                        g=g_,
                    ),
                )
            rows.append(m1c_last)
            break
        Q22, K31 = C4.model_sectors(
            var_z, Sig_z, g_
        )  # GSM sectors, as in k3chain (kappa_l sets only the feed amplitude)
        if aug_sect is not None:
            if "q22" in SECT:
                Q22 = aug_sect[0]
            if "k31" in SECT:
                K31 = aug_sect[1]
        np.fill_diagonal(Q22, 0.0)
        _ed = 'E' if l <= 7 else 'D'
        if 'q22s' in SW or ('q22s' + _ed) in SW:
            Q22 = Q22 * SW.get('q22s', 1.0) * SW.get('q22s' + _ed, 1.0)
        if 'k31s' in SW or ('k31s' + _ed) in SW:
            K31 = K31 * SW.get('k31s', 1.0) * SW.get('k31s' + _ed, 1.0)
        K31 = K31 * float(K31L[l])
        Q22 = Q22 * float(Q22L[l])
        if SW.get('al07'):  # G-RB103: al07 two-term (3,1) law, added term b2 * kappa3_a T_aab / v_a (kai_leal_gonzalez #18246 prose)
            _v = np.maximum(np.diag(Sig_z), 1e-12)
            _T = Tz.T if SW.get('al07T') else Tz
            _add = float(SW['al07']) * (np.diag(Tz)[:, None] * _T / _v[:, None])
            np.fill_diagonal(_add, 0.0)
            K31 = K31 + _add
        m1c, Sig_h, T_h = relu_step_91(mu_z, Sig_z, Tz, k4z, Q22, K31)
        Sig_h = post_sig(l, Sig_h)
        if AUG != "off" and l + 1 >= L0:
            # ---- h-side modes for the next layer. H = h_{<=2}(kappa4[h]) (ARC Thm S.2.4, r=4): diagonal because only the (4) and (2,2) slices exist at the step
            fhK = R.coeffs_relu(sig, a, pdf, cdf, m1, C4.KMAX)
            f2hK = R.coeffs_relu2(sig, a, pdf, cdf, m1, m2, C4.KMAX)
            f2h5 = R.coeffs_relu2(sig, a, pdf, cdf, m1, m2, 5)
            m2c = m2 + C4.marginal_corr(f2h5, k3, k4z, False, None)
            m3c = m3 + k3 / 6.0 * (6.0 * cdf) + k4z / 24.0 * (6.0 * pdf / sig)
            k4h = K.relu_k4_marginal(mu_z, var_z, k3, k4z, m1c, m2c, m3c)
            Qoff_ = Q22.copy()
            np.fill_diagonal(Qoff_, 0.0)
            E22 = C4.expectation_ext(
                f2hK, f2hK, Cz, k3, Tz, k4z, Qoff_, K31, C4.KH
            )  # E[h_a^2 h_b^2]  (power cumulant, ARC 4.1 item 1)
            E21 = C4.expectation_ext(f2hK, fhK, Cz, k3, Tz, k4z, Qoff_, K31, C4.KH)  # E[h_a^2 h_b]
            E11 = Sig_h + np.outer(m1c, m1c)
            ma, mb = m1c[:, None], m1c[None, :]
            c22 = (
                E22
                - 2.0 * mb * E21
                - 2.0 * ma * E21.T
                + mb**2 * m2c[:, None]
                + ma**2 * m2c[None, :]
                + 4.0 * ma * mb * E11
                - 3.0 * ma**2 * mb**2
            )
            vh_ = np.maximum(m2c - m1c**2, 1e-300)
            Qh = c22 - np.outer(vh_, vh_) - 2.0 * Sig_h**2
            np.fill_diagonal(Qh, 0.0)
            tr_ = k4h + Qh.sum(1)
            tr2 = float(tr_.sum())
            Hvec = (tr_ - tr2 / N) / (N + 4.0) + tr2 / (2.0 * N * (N + 2.0))
            gs = (cdf - cdf.mean()) / max(cdf.std(), 1e-12)
            B4 = 0.5 * (gs[:, None] + gs[None, :]) * Sig_h
            # Puffi C3 bases (h side): v = diag Sig_h, vbar, t = kappa_iii, K = kappa_iij (= T_h), D_m = diag(m)
            vh = np.diag(Sig_h).copy()
            vbar = float(vh.mean())
            th = np.diag(T_h).copy()
            Qb = [
                vbar * Sig_h,
                Sig_h * Sig_h,
                0.5 * (m1c[:, None] * T_h.T + T_h * m1c[None, :]),
                np.outer(th, m1c) + np.outer(m1c, th),
                np.outer(vh, vh),
                vbar**2 * np.ones((N, N)),
            ]
            for q in Qb:
                np.fill_diagonal(q, 0.0)
            Bmem = None
            if (
                MEM != 0.0 and aug_sect is not None
            ):  # gate the z-side modes of THIS layer with Phi on both sides -> h-side memory modes for the next layer
                Bmem = {k: (cdf[:, None] * cdf[None, :]) * v for k, v in Bt.items() if k in MODES}
            Choff = Sig_h.copy()
            np.fill_diagonal(Choff, 0.0)
            modes_h = dict(
                B4=B4,
                H=Hvec,
                Qb=Qb,
                vbar=vbar,
                Bmem=Bmem,
                lam_prev=(lam if aug_sect is not None else None),
                t=th,
                v=vh,
                mbar=float(m1c.mean()),
                u=(kap / 6.0) * fh[2],
                k4h=k4h,
                Choff=Choff,
                Qh=Qh,
            )
            if DIAG:
                print(
                    f"    h-modes l={l}: k4h mean {k4h.mean():.3e} rowQ mean {Qh.sum(1).mean():.3e} H mean {Hvec.mean():.3e} min {Hvec.min():.2e}",
                    flush=True,
                )
        if (
            lc_hook is not None
        ):  # learned-corrector hook (research/lc contract): may replace the carried mean; Sig/T untouched
            _m_old = m1c
            m1c = lc_hook(
                l, dict(mu=m1c, Sig=Sig_h, T=T_h, mu_z=mu_z, Sig_z=Sig_z, Tz=Tz, var_z=var_z, g=g_)
            )
            if SW.get('jm'):  # G-RB94 B7: Sigma_h re-centred on the head-corrected mean (partial: T untouched)
                _dl = (m1c - _m_old) * float(SW['jm'])
                Sig_h = Sig_h - np.outer(_m_old, _dl) - np.outer(_dl, _m_old) - np.outer(_dl, _dl)
        if SW.get('eg'):  # G-RB94 A11: Edgeworth-corrected gate P(z>0) = Phi(a) + pdf(a) [g1/6 (a^2-1) + g2/24 (3a - a^3)]
            _eg = float(SW['eg'])
            _ega = cdf + _eg * pdf * (k3 / sig**3 / 6.0 * (a * a - 1.0) + k4z / sig**4 / 24.0 * (3.0 * a - a**3))
            _ega = np.clip(_ega, 0.0, 1.0)
            cdf = _ega
            fh = list(fh)
            fh[1] = _ega
        f1, f2, f3 = fh[1], fh[2], fh[3]
        if DUMPSRC and _DUMPSRC and _DUMPSRC[-1]["l"] == l:
            _DUMPSRC[-1].update(
                cdf=cdf.copy(),
                f1=f1.copy(),
                f2=f2.copy(),
                f3=f3.copy(),
                mu_h=m1c.copy(),
                varh=np.diag(Sig_h).copy(),
            )
        # ---- age all legs (h = Phi o z)
        _pthr = PRUNE
        if 'pe_thr' in SW and l <= int(SW.get('pe_l', 7)):
            _pthr = float(SW['pe_thr'])
        if SW.get('nolast') and l == D - 2:
            _pthr = 0.0
        if 'pthr_all' in SW:
            _pthr = float(SW['pthr_all'])
        PR_LOG[l] = float((cdf < _pthr).mean()) if _pthr > 0 else 0.0
        if _pthr > 0.0:
            _PRUNE_FRAC.append(float((cdf < _pthr).mean()))
            cdf = cdf * (cdf >= _pthr)
        Phi = cdf[:, None]
        for s in srcs + old:
            if "P" in s:
                s["P"], s["A"] = Phi * s["Pz"], Phi * s["Az"]
            for k in ("T1", "T2", "Z"):
                s[k] = Phi * s[k + "z"]
            s["u"] = cdf * s["uz"]
        if Qz is not None:
            Q = Phi * Qz
        if Q2z is not None:
            Q2 = Phi * Q2z  # G-RB142
        for s in old:
            if "Qb" in s:
                s["Qb"] = Phi * s["Qbz"]
        # ---- birth
        D21 = Tz.copy()
        np.fill_diagonal(D21, 0.0)
        A1 = f1[:, None] * Cz
        new = dict(b=l, f1=f1, f2=f2, f3=f3)
        if l > 0:
            U, B = rank_r(D21, rank)
        else:  # layer 0: D21 = 0
            U, B = np.zeros((N, rank)), np.zeros((rank, N))
        new["T1"] = f1[:, None] * B.T
        new["T2"] = f2[:, None] * U
        new["c1"] = U.T * (0.5 * f3)[None, :]
        new["c2"] = B * (0.5 * f2)[None, :]
        new["c3"] = 0.5 * B
        new["c4"] = U.T.copy()
        new["u"] = (kap / 6.0) * f2
        # coincident entries of everything live at the h side: aged sources = Phi^2 Phi o their z-read; new blocks at P = I
        That = (
            sum((cdf * cdf)[:, None] * cdf[None, :] * Tb for Tb in per_src_T)
            if per_src_T
            else np.zeros((N, N))
        )
        if SW.get('bern') and per_src_T:  # A3/B15: independent-Bernoulli coincident entries for the aged part of That
            _Tt = sum(per_src_T)
            _off = _Tt * (cdf[:, None] * cdf[None, :]) + 2.0 * ((cdf * (1.0 - cdf) * mu_z)[:, None] * cdf[None, :]) * Cz
            np.fill_diagonal(_off, np.diag(That))
            That = _off
        T1n, T2n = new["T1"], new["T2"]
        blocks_new = [
            (3.0, A1, A1 * f2[None, :] + T1n @ new["c1"] + T2n @ new["c2"]),
            (3.0, T2n @ new["c3"], A1 * f2[None, :]),
            (1.5, T1n @ new["c4"], A1 * f3[None, :]),
            (1.0, A1 * f1[None, :], np.outer(3.0 * new["u"], np.ones(N))),
        ]
        That = That + sum(read_block_identity(alpha, X, Y) for alpha, X, Y in blocks_new)
        Dadj = T_h - That
        d3 = np.diag(Dadj).copy()
        np.fill_diagonal(Dadj, 0.0)
        Voff = 3.0 * Dadj.T  # Vadj[:, j] = 3 Dadj[j, :]
        _colE = np.einsum("ij,ij->j", A1, A1)
        _rho = float(SW.get('tf_rho', 0.0))
        tfit = np.einsum("ij,ij->j", Voff, A1) / np.maximum(_colE, max(_rho * float(_colE.mean()), 1e-300))
        Rres = Voff - A1 * tfit[None, :]
        Zn, c5 = rank_r(Rres, rank)
        # the rank-r residual has a spurious diagonal (Rres is zero-diagonal); the exact (3)-slice is d3, so cancel it in s
        new.update(t=tfit, s=d3 - np.einsum("ij,ji->i", Zn, c5), Z=Zn, c5=c5, P=np.eye(N), A=A1)
        srcs.append(new)
        # ---- old tier: move sources of age >= gate into the shared basis
        if (
            aged is not None and aged[0][0] == "own"
        ):  # per-source fixed basis Q_b (n x r) at entry, transported like a leg
            _, gate, r_sh = aged[0]
            for s in [s for s in srcs if l + 1 - s["b"] >= gate]:
                srcs.remove(s)
                L = (
                    s["P"] if PBASIS else np.concatenate([s["P"], s["A"]], 1)
                )  # G-RB63: P-only basis
                Qb = range_finder(
                    lambda X: L @ (L.T @ X), r_sh, N, seed=3000 + l, power=RF["power"]
                )
                s["Qb"], s["FP"], s["FA"] = Qb, Qb.T @ s["P"], Qb.T @ s["A"]
                s["r"] = r_sh
                del s["P"], s["A"]
                old.append(s)
            # G-RB12: nested OWN tiers -- at age >= gate_i the source's coefficient block F = [F_P|F_A] (r x 2n) is projected on the top-r_i
            # eigenvectors of F F^T (r x r eigh, never n x n); Q_b <- Q_b V2, F <- V2^T F. Thin legs unchanged. (prose rank law, 18218 S2.4)
            for gate2, r2 in aged[1:]:
                for s in old:
                    if l + 1 - s["b"] >= gate2 and s["r"] > r2:
                        # the CURRENT legs are L = Q_b F with Q_b transported (no longer orthonormal): Q_b = U R (thin QR),
                        # L L^T = U (R F F^T R^T) U^T -> top-r2 eigenvectors V2 of the r x r matrix; Q_b <- U V2, F <- V2^T R F
                        U_, R_ = np.linalg.qr(s["Qb"])
                        F = R_ @ (
                            s["FP"] if PBASIS else np.concatenate([s["FP"], s["FA"]], 1)
                        )  # G-RB63
                        _ev, V = np.linalg.eigh(F @ F.T)
                        V2 = V[:, -r2:]
                        s["Qb"] = U_ @ V2
                        s["FP"], s["FA"] = V2.T @ (R_ @ s["FP"]), V2.T @ (R_ @ s["FA"])
                        s["r"] = r2
        elif aged is not None and SW.get("shared") == "fixed":
            # G-RB142: TWO shared transported bases, projection-only admission. Q (n x r) is formed ONCE from the first entrant
            # (same joint [P|A] range finder + seed as the own branch), then only transported; later entrants are admitted by the
            # Gram solve F = (Q^T Q)^-1 Q^T [P|A] (Q is not orthonormal after transport), residual dropped. Q2 (n x r2) likewise from the
            # first nesting (own-branch eigh), then transported; later oldest sources are moved by the Gram solve onto Q2.
            # switches: placebo (random orthonormal Q at formation), nosolve (Q^T L instead of the solve: M2), refresh224 (A2r), probe.
            gate, r_sh = aged[0]
            _probe = bool(SW.get("probe"))
            movers = [s for s in srcs if l + 1 - s["b"] >= gate]
            if movers:
                srcs = [s for s in srcs if s not in movers]
                for s in movers:
                    L = np.concatenate([s["P"], s["A"]], 1)
                    if Q is None:
                        if SW.get("placebo"):
                            Q, _ = np.linalg.qr(np.random.default_rng(424242 + l).standard_normal((N, r_sh)))
                        else:
                            Q = range_finder(lambda X: L @ (L.T @ X), r_sh, N, seed=3000 + l, power=RF["power"])
                        F = Q.T @ L
                    else:
                        F = _admit(Q, L)
                        if _probe:
                            Qo = range_finder(lambda X: L @ (L.T @ X), r_sh, N, seed=3000 + l, power=RF["power"])
                            e = float(np.sum(L * L))
                            PROBE.append(dict(l=l, event="entry", r=r_sh, res_shared=float(np.sum((L - Q @ F) ** 2)) / e,
                                              res_own=float(np.sum((L - Qo @ (Qo.T @ L)) ** 2)) / e, condQ=float(np.linalg.cond(Q))))
                    s["FP"], s["FA"] = F[:, :N], F[:, N:]
                    s["r"], s["grp"] = r_sh, 1
                    del s["P"], s["A"]
                    old.append(s)
            if len(aged) > 1:
                gate2, r2 = aged[1]
                movers2 = [s for s in old if s.get("grp") == 1 and l + 1 - s["b"] >= gate2 and s["r"] > r2]
                if movers2 and SW.get("refresh224") and Q2 is not None:
                    # A2r: rebuild Q2 from the whole oldest stack lifted to n, re-admit every grp-2 source by the solve
                    Lall = [Q2 @ np.concatenate([s["FP"], s["FA"]], 1) for s in old if s.get("grp") == 2]
                    Lall += [Q @ np.concatenate([s["FP"], s["FA"]], 1) for s in movers2]
                    Lall = np.concatenate(Lall, 1)
                    Q2n = range_finder(lambda X: Lall @ (Lall.T @ X), r2, N, seed=2000 + l, power=RF["power"])
                    for s in old:
                        if s.get("grp") == 2:
                            Fn = _admit(Q2n, Q2 @ np.concatenate([s["FP"], s["FA"]], 1))
                            s["FP"], s["FA"] = Fn[:, :N], Fn[:, N:]
                    Q2 = Q2n
                for s in movers2:
                    F = np.concatenate([s["FP"], s["FA"]], 1)
                    if Q2 is None:
                        U_, R_ = np.linalg.qr(Q)
                        RF_ = R_ @ F
                        _ev, V = np.linalg.eigh(RF_ @ RF_.T)
                        V2 = V[:, -r2:]
                        Q2 = U_ @ V2
                        Fn = V2.T @ RF_
                    else:
                        L2 = Q @ F
                        Fn = _admit(Q2, L2)
                        if _probe:
                            Qo = range_finder(lambda X: L2 @ (L2.T @ X), r2, N, seed=2000 + l, power=RF["power"])
                            e = float(np.sum(L2 * L2))
                            PROBE.append(dict(l=l, event="nest", r=r2, res_shared=float(np.sum((L2 - Q2 @ Fn) ** 2)) / e,
                                              res_own=float(np.sum((L2 - Qo @ (Qo.T @ L2)) ** 2)) / e, condQ=float(np.linalg.cond(Q2))))
                    s["FP"], s["FA"] = Fn[:, :N], Fn[:, N:]
                    s["r"], s["grp"] = r2, 2
        elif aged is not None:
            gate, r_sh = aged[0]
            movers = [
                s for s in srcs if l + 1 - s["b"] >= gate
            ]  # age at the next layer's transport
            if movers:
                srcs = [s for s in srcs if s not in movers]
                L = [np.concatenate([s["P"], s["A"]], 1) for s in movers]
                if Q is not None:
                    L.append(Q @ np.concatenate([s["FP"] for s in old] + [s["FA"] for s in old], 1))
                L = np.concatenate(L, 1)
                Qn = range_finder(lambda X: L @ (L.T @ X), r_sh, N, seed=1000 + l)
                for s in old:
                    s["FP"], s["FA"] = (Qn.T @ Q) @ s["FP"], (Qn.T @ Q) @ s["FA"]
                for s in movers:
                    s["FP"], s["FA"] = Qn.T @ s["P"], Qn.T @ s["A"]
                    del s["P"], s["A"]
                    old.append(s)
                Q = Qn
            if (
                len(aged) > 1 and old
            ):  # nested smaller basis for the oldest (prototype: project their F onto top-r2 of their own stack)
                gate2, r2 = aged[1]
                oldest = [s for s in old if l + 1 - s["b"] >= gate2]
                if oldest:
                    F = np.concatenate([s["FP"] for s in oldest] + [s["FA"] for s in oldest], 1)
                    V2 = range_finder(lambda X: F @ (F.T @ X), r2, F.shape[0], seed=2000 + l)
                    for s in oldest:
                        s["FP"], s["FA"] = V2 @ (V2.T @ s["FP"]), V2 @ (V2.T @ s["FA"])
        mu, Sig = m1c, Sig_h
        rows.append(mu)
        if log is not None:
            log(f"  l={l} young {len(srcs)} old {len(old)} {time.time() - t0:.1f}s")
    if DUMPSRC and _DUMPSRC:
        np.savez(
            DUMPSRC, **{f"{k}_{r['l']}": v for r in _DUMPSRC for k, v in r.items() if k != "l"}
        )
        print(f"  DUMPSRC -> {DUMPSRC} ({len(_DUMPSRC)} layers)", flush=True)
        _DUMPSRC.clear()
    if PRUNE > 0.0 and _PRUNE_FRAC:
        print(
            f"  PRUNE {PRUNE}: mean pruned fraction over layers {float(np.mean(_PRUNE_FRAC)):.3f} per-layer {[round(x, 3) for x in _PRUNE_FRAC]}",
            flush=True,
        )
        _PRUNE_FRAC.clear()
    return np.stack(rows)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--nets", type=int, nargs="+", default=[0])
    ap.add_argument("--rank", type=int, default=16)
    ap.add_argument("--aged", default="")
    ap.add_argument("--check", default="")
    ap.add_argument("--tag", default="")
    ap.add_argument(
        "--rf",
        type=int,
        default=-1,
        help="range-finder rank-r with this many power iterations (-1 = exact SVD)",
    )
    ap.add_argument(
        "--gscale",
        type=float,
        default=1.0,
        help="G-RB13: multiply the 16-entry g table (kappa4 = g var^2)",
    )
    ap.add_argument(
        "--kscale",
        type=float,
        default=1.0,
        help="G-RB13: multiply the 16-entry kappa table (K31 slope / feed amplitude)",
    )
    args = ap.parse_args()
    if args.rf >= 0:
        RF["on"], RF["power"] = True, args.rf
    aged = None
    if args.aged:
        if args.aged.startswith("own:"):
            parts = args.aged.split(",")
            _, gate, r_ = parts[0].split(":")
            aged = [("own", int(gate), int(r_))] + [
                tuple(int(x) for x in p.split(":")) for p in parts[1:]
            ]
        else:
            aged = [tuple(int(x) for x in p.split(":")) for p in args.aged.split(",")]
    g = SC.load_g() * args.gscale
    kappa = np.load(HERE / "kappa_table.npz")["kappa"] * args.kscale
    for mid in args.nets:
        ws, truth = K.load_net(mid)
        t0 = time.time()
        est = src_closure(
            ws, g, kappa, rank=args.rank, aged=aged, log=lambda s: print(s, flush=True)
        )
        per_layer = [K.mse(est[i], truth[i]) for i in range(D)]
        row = dict(
            net=mid,
            cfg=f"src_r{args.rank}"
            + (f"_rf{args.rf}" if args.rf >= 0 else "")
            + (f"_aged{args.aged}" if args.aged else "")
            + (f"_g{args.gscale:g}" if args.gscale != 1.0 else "")
            + (f"_k{args.kscale:g}" if args.kscale != 1.0 else ""),
            final=per_layer[-1],
            layer_mse=per_layer,
            secs=time.time() - t0,
            tag=args.tag,
        )
        if args.check:
            ref = np.load(HERE / args.check)
            row["check_maxdiff"] = float(np.max(np.abs(ref - est)))
            row["check_rel_final"] = float(
                np.max(np.abs(ref[-1] - est[-1])) / np.max(np.abs(ref[-1]))
            )
        print(json.dumps({k: v for k, v in row.items() if k != "layer_mse"}), flush=True)
        with open(HERE / "results.jsonl", "a") as f:
            f.write(json.dumps(row) + "\n")
        if DUMP:
            np.savez(
                DUMP,
                **{f"d{r['l']}": r["d"] for r in _DUMP},
                **{f"k4z{r['l']}": r["k4z"] for r in _DUMP},
            )


if __name__ == "__main__":
    main()
