"""Numerical checks for Appendix P3 (the kappa4 closure in S-notation) and P4 (transport-cost scaling).

Exit 0 only if every check passes AND every falsifier fires. A falsifier is a deliberately wrong variant
that must disagree; a check whose falsifier does not fire cannot discriminate and counts as a failure.

P3 (all exact identities, small n, full n^4 tensors):
  P3a  ARC's cup g(H) (sum over the 6 pairs u<v of [4]) == S(delta,H) + S(H,delta).
       Falsifiers: drop one of the six pairings; S(delta,H) alone (it is not index-symmetric).
  P3b  Transport by multilinearity: S(A,B) (.) W == S(W^T A W, W^T B W), hence g(H) (.) W == g_M(W^T H W), M = W^T W.
       Falsifier: g(W^T H W) (delta NOT mapped to M) must disagree.
  P3c  The slice formulas of submissions/v112_sb/estimator.py (lines 1388-1393, copied verbatim) == brute-force
       (4), (2,2), (3,1) slices of sum_ab Lam_ab S(B_a, B_b), with the SHIPPED Lam of layer 5 and modes shaped as in
       the code (I diagonal, Q with zero diagonal). Falsifier: drop the factor 2 in the (2,2) term.
  P3d  Gaussian scale mixture: x | eps ~ N(0, C0 + sum_a eps_a B_a), E eps = 0, Cov eps = Lam  =>
       kappa4 == sum_ab Lam_ab S(B_a, B_b) exactly (finite mixture, exact moments, no Monte Carlo).
       Falsifier: the same mixture with a NON-Gaussian conditional (uniform) must disagree.
  P3e  [measurement, no pass/fail] what the free-transport build drops: ||offdiag(M)|| / ||M|| at n = 1024 on a real
       layer, and the eigenvalue signs of the shipped Lam (indefinite Lam lies outside P3d).

P4 (cost model: one unit = one dense n x n x n product; an n x k x m product counts k*m/n^2 units):
  P4a  Toy factored chain at small n with a COUNTING matmul, three policies, L in {8,...,128}:
       per-source (no window), window w, and v112's old tier (shared transported bases + per-source F/K).
       Counted units must equal the closed forms exactly; log-log slopes are reported.
       Algebra: the shared-basis contraction equals the per-source contraction (legs in span Q).
       Falsifiers: per-source per-layer count must NOT be flat in l (and its total must not fit a line);
       the window closed form must NOT fit the per-source counts.
  P4b  Grounding in the real code: per-layer LOGICAL product volume by site from one real predict of v110_fk and
       v112_sb (n = 1024, depth 16, net 0), read from writeup/proofs/out/sites_<build>.json written by count_sites.py.
       Checks the predicted per-layer old-tier widths from the age schedule, that v112's shared terms are flat in the
       number of old sources and that v112's F+K volume still grows with l (the honest finding).
"""

import itertools
import json
import sys
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[2]
rng = np.random.default_rng(20261020)
FAILS = []


def check(cond, msg):
    print(("PASS  " if cond else "FAIL  ") + msg)
    if not cond:
        FAILS.append(msg)


def falsifier(fired, msg):
    print(("FIRED " if fired else "SILENT") + " falsifier: " + msg)
    if not fired:
        FAILS.append("falsifier silent: " + msg)


# ---------------------------------------------------------------- P3 helpers
def sym2(n):
    A = rng.normal(size=(n, n))
    return A + A.T


def S(A, B):
    """S(A,B)_ijkl = A_ij B_kl + A_ik B_jl + A_il B_jk (the pair holding index i carries A)."""
    return (
        np.einsum("ij,kl->ijkl", A, B)
        + np.einsum("ik,jl->ijkl", A, B)
        + np.einsum("il,jk->ijkl", A, B)
    )


def cup(H, M=None, drop=None):
    """ARC Definition S.2.2: g_M(H)_{i1..i4} = sum_{u<v} M_{iu,iv} H_{rest}; M = delta gives the plain cup g."""
    n = H.shape[0]
    M = np.eye(n) if M is None else M
    letters = "ijkl"
    out = np.zeros((n,) * 4)
    for t, (u, v) in enumerate(itertools.combinations(range(4), 2)):
        if t == drop:
            continue
        rest = [letters[s] for s in range(4) if s not in (u, v)]
        out += np.einsum(f"{letters[u]}{letters[v]},{rest[0]}{rest[1]}->ijkl", M, H)
    return out


def transport(K, W):
    """(K (.) W)_{abcd} = sum_{ijkl} K_ijkl W_ia W_jb W_kc W_ld (ARC Def. S.2.3, z = W^T h)."""
    return np.einsum("ijkl,ia,jb,kc,ld->abcd", K, W, W, W, W, optimize=True)


def is_fully_symmetric(K):
    return max(np.abs(K - K.transpose(p)).max() for p in itertools.permutations(range(4)))


def p3a(n=7):
    print("\n== P3a: six pairings of delta (x) H  ==  S(delta,H) + S(H,delta)")
    H = sym2(n)
    I = np.eye(n)
    g = cup(H)
    s = S(I, H) + S(H, I)
    err = np.abs(g - s).max()
    check(err < 1e-12, f"max|g(H) - [S(I,H)+S(H,I)]| = {err:.1e} (n={n})")
    check(is_fully_symmetric(g) < 1e-12, "g(H) is fully symmetric (as a fourth cumulant must be)")
    errs = [np.abs(cup(H, drop=t) - s).max() for t in range(6)]
    falsifier(min(errs) > 0.1, f"drop one of the 6 pairings -> min max-err {min(errs):.2f}")
    asym = is_fully_symmetric(S(I, H))
    falsifier(
        asym > 0.1, f"S(I,H) alone (Lam_IH=1, Lam_HI=0) is not index-symmetric: asym {asym:.2f}"
    )


def p3b(n=6):
    print("\n== P3b: transport is exact on the S-form; delta goes to M = W^T W")
    A, Bm, H = sym2(n), sym2(n), sym2(n)
    W = rng.normal(size=(n, n)) * np.sqrt(2 / n)
    lhs = transport(S(A, Bm), W)
    rhs = S(W.T @ A @ W, W.T @ Bm @ W)
    check(
        np.abs(lhs - rhs).max() < 1e-10 * np.abs(lhs).max(),
        f"S(A,B)(.)W == S(WtAW, WtBW): {np.abs(lhs - rhs).max():.1e}",
    )
    M = W.T @ W
    lhs2 = transport(cup(H), W)
    rhs2 = cup(W.T @ H @ W, M)
    check(
        np.abs(lhs2 - rhs2).max() < 1e-10 * np.abs(lhs2).max(),
        f"g(H)(.)W == g_M(WtHW): {np.abs(lhs2 - rhs2).max():.1e}",
    )
    bad = np.abs(lhs2 - cup(W.T @ H @ W)).max() / np.abs(lhs2).max()
    falsifier(bad > 0.05, f"g(WtHW) with delta kept (not mapped to M): rel err {bad:.2f}")


def p3c(n=7):
    print("\n== P3c: the code's slice formulas == brute-force slices of sum Lam S(B_a,B_b)")
    lam_all = np.load(ROOT / "submissions/v112_sb/weights.npz")["lam"].astype(np.float64)
    lam_l = lam_all[5]
    m_i = rng.uniform(1.5, 2.5, n)
    cov_pre = sym2(n) + 2 * n * np.eye(n)
    Qf = sym2(n)
    np.fill_diagonal(Qf, 0.0)
    Bst = np.stack([np.diag(m_i), cov_pre, Qf], axis=0)
    Dl = np.stack([m_i, np.diag(cov_pre), np.diag(Qf)], axis=0)
    # ---- verbatim from submissions/v112_sb/estimator.py (fnp -> np)
    ssc_k4 = 3.0 * np.einsum("ab,ai,bi->i", lam_l, Dl, Dl)
    ssc_q22 = np.einsum("ab,ai,bj->ij", lam_l, Dl, Dl) + 2.0 * np.einsum(
        "ab,aij,bij->ij", lam_l, Bst, Bst
    )
    ssc_k31 = 2.0 * np.einsum("ab,ai,bij->ij", lam_l, Dl, Bst) + np.einsum(
        "ab,aij,bi->ij", lam_l, Bst, Dl
    )
    # ---- brute force
    K = sum(lam_l[a, b] * S(Bst[a], Bst[b]) for a in range(3) for b in range(3))
    ii = np.arange(n)
    k4 = K[ii, ii, ii, ii]
    q22 = np.einsum("iijj->ij", K)
    k31 = np.einsum("iiij->ij", K)
    sc = np.abs(K).max()
    e4, e22, e31 = (
        np.abs(x - y).max() / sc for x, y in ((ssc_k4, k4), (ssc_q22, q22), (ssc_k31, k31))
    )
    check(max(e4, e22, e31) < 1e-13, f"(4) {e4:.1e}  (2,2) {e22:.1e}  (3,1) {e31:.1e}  (relative)")
    check(
        is_fully_symmetric(K) / sc < 1e-13,
        "sum Lam S(B_a,B_b) is fully symmetric with the shipped (symmetric) Lam",
    )
    bad = np.einsum("ab,ai,bj->ij", lam_l, Dl, Dl) + 1.0 * np.einsum(
        "ab,aij,bij->ij", lam_l, Bst, Bst
    )
    falsifier(
        np.abs(bad - q22).max() / sc > 1e-3,
        f"(2,2) with factor 1 instead of 2: rel err {np.abs(bad - q22).max() / sc:.1e}",
    )


def p3d(n=4, P=6):
    print("\n== P3d: Gaussian scale mixture => kappa4 = sum Lam S(B_a,B_b) exactly")
    Bm = [sym2(n) * 0.1 for _ in range(3)]
    C0 = sym2(n) + 3 * n * np.eye(n)
    E = rng.normal(size=(P, 3))
    pi = rng.dirichlet(np.ones(P))
    E -= pi @ E  # zero mean
    lam = (E * pi[:, None]).T @ E  # Cov eps
    Cs = [C0 + sum(E[p, a] * Bm[a] for a in range(3)) for p in range(P)]
    assert all(np.linalg.eigvalsh(C).min() > 0 for C in Cs)
    m4 = sum(
        pi[p] * S(Cs[p], Cs[p]) for p in range(P)
    )  # Isserlis: E[x_i x_j x_k x_l | eps] = S(C,C)
    k4 = m4 - S(C0, C0)  # second moment is C0 (E eps = 0)
    form = sum(lam[a, b] * S(Bm[a], Bm[b]) for a in range(3) for b in range(3))
    err = np.abs(k4 - form).max() / np.abs(form).max()
    check(err < 1e-12, f"exact mixture kappa4 vs sum Lam S: rel err {err:.1e}")
    # falsifier: uniform (non-Gaussian) conditional x = L_p u, u iid uniform var 1 (kappa4_u = -1.2)
    k4u = np.zeros((n,) * 4)
    for p in range(P):
        Lp = np.linalg.cholesky(Cs[p])
        k4u += pi[p] * (-1.2 * np.einsum("im,jm,km,lm->ijkl", Lp, Lp, Lp, Lp) + S(Cs[p], Cs[p]))
    k4u -= S(C0, C0)
    bad = np.abs(k4u - form).max() / np.abs(form).max()
    falsifier(bad > 0.5, f"non-Gaussian (uniform) conditional: rel err {bad:.1f}")


def p3e():
    print("\n== P3e [measurement]: what the free build drops, and the sign of the shipped Lam")
    _sl = Path(__file__).resolve().parent / "data_w00000_layer3.npy"  # shipped 4 MB slice (layer 3 of dataset net 0)
    w = (np.load(_sl) if _sl.exists() else np.load(ROOT / "research/lc/data/w_00000.npy", mmap_mode="r")[3]).astype(np.float64)
    M = w.T @ w
    off = M - np.diag(np.diag(M))
    print(
        f"      n={M.shape[0]}: mean M_ii {np.diag(M).mean():.3f}; ||offdiag M||_F/||M||_F = "
        f"{np.linalg.norm(off) / np.linalg.norm(M):.3f}; spectrum of M in [{np.linalg.eigvalsh(M)[[0, -1]].round(3)}]"
    )
    lam = np.load(ROOT / "submissions/v112_sb/weights.npz")["lam"].astype(np.float64)
    neg = [l for l in range(1, 15) if np.linalg.eigvalsh(lam[l]).min() < 0]
    print(
        f"      shipped Lam symmetric: max|Lam-Lam^T| = {np.abs(lam - lam.transpose(0, 2, 1)).max():.1e}; "
        f"layers with a negative eigenvalue: {neg}; min eigenvalue {min(np.linalg.eigvalsh(lam[l]).min() for l in range(16)):.1e}"
    )


# ---------------------------------------------------------------- P4a toy chain with a counting matmul
class Counter:
    def __init__(self, n):
        self.n, self.units, self.calls = n, 0.0, 0
        self.by_layer = {}
        self.layer = None

    def mm(self, A, B):
        r, k = A.shape
        k2, c = B.shape
        assert k == k2
        u = r * k * c / self.n**3
        self.units += u
        self.calls += 1
        self.by_layer[self.layer] = self.by_layer.get(self.layer, 0.0) + u
        return A @ B


def toy_chain(n, L, policy, w=5, r=None):
    """A factored chain: at z-layer s = 1..L-2 a source is born with dense legs (P, A); it is read at layers s+1..L-1.
    Per (source, layer): 2 transports (W^T P, W^T A) + 2 read contractions (LP Pz^T, LA Az^T) = 4 units (T1, Sec. 7).
      'per'    : every source keeps per-source dense legs forever.
      'window' : sources older than w are dropped.
      'shared' : sources aged > w are admitted (Gram solve) into ONE shared basis Q (n x r) transported once per layer;
                 per old source per layer: F = Qz [F_P|F_A] (2 r/n) and K = [LP|LA] [F_P;F_A]^T (2 r/n) units;
                 per layer: one Q transport (r/n) + one trailing contraction (r/n) -- the v112 structure.
    Returns (counter, list of per-layer reads) so the shared and per-source algebra can be compared."""
    r = r or n // 4
    cnt = Counter(n)
    reads = []
    young = []  # (birth, P, A)
    old = []  # (birth, FPA)  (r, 2n) static coefficients
    Q = None
    gate = 0.5 + 0.5 * rng.random(n)
    for l in range(1, L):
        cnt.layer = l
        W = rng.normal(size=(n, n)) * np.sqrt(2 / n)
        T = np.zeros((n, n))
        # young: transport + contract
        for b, (s, P, A) in enumerate(young):
            Pz, Az = cnt.mm(W.T, P), cnt.mm(W.T, A)
            LP, LA = gate[:, None] * Pz, gate[:, None] * Az  # stand-in Hadamard read
            T += cnt.mm(LP, Pz.T) + cnt.mm(LA, Az.T)
            young[b] = (
                s,
                gate[:, None] * Pz,
                gate[:, None] * Az,
            )  # ageing: h = Phi o z (row scaling)
        if old:
            Qz = cnt.mm(W.T, Q)
            acc = np.zeros((n, r))
            for s, FPA in old:
                PAz = cnt.mm(Qz, FPA)  # F site: dense per-source legs from the shared basis
                Pz, Az = PAz[:, :n], PAz[:, n:]
                LP, LA = gate[:, None] * Pz, gate[:, None] * Az
                acc += cnt.mm(np.concatenate([LP, LA], axis=1), FPA.T)  # K site, in the basis
            T += cnt.mm(acc, Qz.T)  # ONE trailing contraction
            Q = gate[:, None] * Qz  # the basis ages; the coefficients are static
            Q = np.linalg.qr(Q)[0]  # toy only, NOT counted: keeps the 128-layer toy well conditioned (span unchanged)
        reads.append(T)
        # births (none at the last layer)
        if l < L - 1:
            P = np.eye(n) + 0.1 * rng.normal(size=(n, n))
            A = rng.normal(size=(n, n))
            if (
                policy == "shared" and Q is not None
            ):  # keep legs inside span(Q) so the algebra check is exact
                P, A = Q @ rng.normal(size=(r, n)), Q @ rng.normal(size=(r, n))
            elif policy == "shared":
                Q = np.linalg.qr(rng.normal(size=(n, r)))[0]
                P, A = Q @ rng.normal(size=(r, n)), Q @ rng.normal(size=(r, n))
            young.append((l, P, A))
        # ageing out of the young tier
        keep = []
        for s, P, A in young:
            if l + 1 - s > w and policy in ("window", "shared"):
                if policy == "shared":
                    G = Q.T @ Q
                    FPA = np.linalg.solve(
                        G, Q.T @ np.concatenate([P, A], axis=1)
                    )  # P2 admission (exact: legs in span Q)
                    old.append((s, FPA))
            else:
                keep.append((s, P, A))
        young = keep
    return cnt, reads


def closed_form(L, policy, n, w=5, r=None):
    """Predicted units per layer l = 1..L-1. Sources born at s = 1..L-2, age at layer l is l - s >= 1."""
    r = r or n // 4
    out = {}
    for l in range(1, L):
        ages = [l - s for s in range(1, min(l, L - 1))]
        if policy == "per":
            out[l] = 4.0 * len(ages)
        elif policy == "window":
            out[l] = 4.0 * sum(1 for a in ages if a <= w)
        else:
            m_old = sum(1 for a in ages if a > w)
            out[l] = (
                4.0 * sum(1 for a in ages if a <= w)
                + (4 * r / n) * m_old
                + ((2 * r / n) if m_old else 0.0)
            )
    return out


def p4a(n=32, w=5):
    print("\n== P4a: toy factored chain, counting matmul (unit = one n x n x n product)")
    Ls = [8, 16, 32, 64, 128]
    tot = {p: [] for p in ("per", "window", "shared")}
    for p in tot:
        for L in Ls:
            cnt, _ = toy_chain(n, L, p, w)
            pred = closed_form(L, p, n, w)
            exact = all(abs(cnt.by_layer.get(l, 0.0) - pred[l]) < 1e-9 for l in pred)
            check(
                exact,
                f"{p:6s} L={L:3d}: counted {cnt.units:9.2f} units == closed form {sum(pred.values()):9.2f}",
            )
            tot[p].append(cnt.units)
    for p in tot:
        sl = np.polyfit(np.log(Ls[2:]), np.log(tot[p][2:]), 1)[0]
        print(f"      log-log slope of total units vs L (L=32..128), {p:6s}: {sl:.3f}")
    # exact totals: per = 2 (L-1)(L-2); window = 4 * sum_s min(w, L-1-s)
    L = 128
    check(
        abs(tot["per"][-1] - 2 * (L - 1) * (L - 2)) < 1e-9,
        "per-source total = 2(L-1)(L-2) = Theta(L^2)",
    )
    check(
        abs(tot["window"][-1] - 4 * sum(min(w, L - 1 - s) for s in range(1, L - 1))) < 1e-9,
        "window total = 4 sum_s min(w, L-1-s) = Theta(wL)",
    )
    # decomposition of the shared policy: shared terms Theta(L), per-source F/K Theta(L^2)
    r = n // 4
    shared_terms = sum(
        2 * r / n for l in range(1, L) if l - 1 > w
    )  # layers with at least one old source
    fk = sum(4 * r / n * sum(1 for s in range(1, min(l, L - 1)) if l - s > w) for l in range(1, L))
    check(
        abs(tot["shared"][-1] - (tot["window"][-1] + shared_terms + fk)) < 1e-9,
        f"shared = young {tot['window'][-1]:.0f} + shared-basis terms {shared_terms:.1f} [Theta(L)] + F/K {fk:.1f} [Theta(r L^2/n)]",
    )
    # algebra: with legs P_b = Q F_Pb, A_b = Q F_Ab, transport and row-gate ageing commute with the basis, and
    # sum_b (LP_b Pz_b^T + LA_b Az_b^T) = (sum_b [LP_b|LA_b] [F_Pb;F_Ab]^T) Qz^T exactly
    rr, m = n // 4, 6
    Q = rng.normal(size=(n, rr))
    Fs = [rng.normal(size=(rr, 2 * n)) for _ in range(m)]
    Wt = rng.normal(size=(n, n)) * np.sqrt(2 / n)
    phi = rng.random(n)
    per = np.zeros((n, n))
    for F in Fs:
        PA = phi[:, None] * (Q @ F)  # aged per-source legs
        PAz = Wt.T @ PA
        L_ = phi[:, None] * PAz  # stand-in Hadamard read
        per += L_[:, :n] @ PAz[:, :n].T + L_[:, n:] @ PAz[:, n:].T
    Qz = Wt.T @ (phi[:, None] * Q)
    acc = np.zeros((n, rr))
    for F in Fs:
        PAz = Qz @ F
        L_ = phi[:, None] * PAz
        acc += L_ @ F.T
    err = np.abs(acc @ Qz.T - per).max() / np.abs(per).max()
    check(err < 1e-12, f"shared-basis read (one trailing contraction) == per-source read: rel err {err:.1e}")
    # falsifiers
    cntP, _ = toy_chain(n, 64, "per", w)
    counted = [cntP.by_layer.get(l, 0.0) for l in range(1, 64)]
    falsifier(
        np.ptp(counted) > 100,
        f"per-source per-layer count is NOT flat in l: range {min(counted):.0f}..{max(counted):.0f}",
    )
    lin = np.polyfit(Ls, tot["per"], 1)
    resid = np.abs(np.polyval(lin, Ls) - tot["per"]).max() / max(tot["per"])
    falsifier(
        resid > 0.05, f"per-source totals do not fit a line in L: max rel residual {resid:.2f}"
    )
    winpred = closed_form(64, "window", n)
    mism = max(abs(counted[l - 1] - winpred[l]) for l in winpred)
    falsifier(
        mism > 10,
        f"window closed form applied to per-source counts: max per-layer mismatch {mism:.0f} units",
    )


# ---------------------------------------------------------------- P4b grounding in the real code
SCHED_NOTE = "age at transport layer l of a source born at layer s is l - s"


def schedule(depth=16, age_old=6, age_old2=8):
    """Predicted per-layer group membership from the code's rules: a source is born at every non-last layer s
    (its legs are first transported at s+1); it enters the old tier when l + 1 - s >= age_old after layer l, i.e. it is
    transported in the old tier from layer s + age_old on; likewise the 224 group from s + age_old2 on."""
    rows = {}
    for l in range(depth):
        srcs = [s for s in range(0, l)]  # born at layers 0..l-1, transported at l
        young = [s for s in srcs if l - s < age_old]
        g384 = [s for s in srcs if age_old <= l - s < age_old2]
        g224 = [s for s in srcs if l - s >= age_old2]
        rows[l] = (len(young), len(g384), len(g224))
    return rows


def p4b():
    print(
        "\n== P4b: real code, per-layer logical product volume by site (n = 1024, depth 16, net 0)"
    )
    out = ROOT / "writeup/proofs/out"
    data = {}
    for b in ("v110_fk", "v112_sb"):
        f = out / f"sites_{b}.json"
        if not f.exists():
            check(
                False,
                f"{f} missing: run  BG_MEM_GB=8 research/rebuild/bg.sh 0.5 p4-count -- whest-starterkit/.venv/bin/python writeup/proofs/count_sites.py submissions/{b} {f}  (from the arc-whitebox root)",
            )
            return
        data[b] = json.load(open(f))
    n = 1024
    vol = {}
    for b, d in data.items():
        v = {}
        for c in d["calls"]:
            A, B_ = c["A"], c["B"]
            # logical product: (batch, rows, inner) @ (batch, inner, cols); batched leading dims multiply
            bat = int(np.prod(A[:-2])) if len(A) > 2 else 1
            u = bat * A[-2] * A[-1] * B_[-1] / n**3
            key = (c["layer"], c["site"])
            v[key] = v.get(key, 0.0) + u
        vol[b] = v
        sites = sorted({s for (_, s) in v})
        print(f"   {b}: total metered {100 * d['total'] / 2**41:.4f} pt; sites {sites}")
        print("      layer " + " ".join(f"{s:>7s}" for s in sites))
        for l in range(16):
            print(f"      {l:5d} " + " ".join(f"{v.get((l, s), 0.0):7.3f}" for s in sites))
    sched = schedule()
    print(
        "      predicted (young, 384-group, 224-group) per layer: "
        + ", ".join(f"{l}:{sched[l]}" for l in range(16))
    )
    r1, r0 = 384 / n, 224 / n
    # F and K: per old source, 2 r/n units each, identical in both builds (the per-source in-basis terms)
    ok_fk = True
    for b in data:
        for l in range(15):
            _, m1, m0 = sched[l]
            pred = 2 * (m1 * r1 + m0 * r0)
            got_F = vol[b].get((l, "F0"), 0) + vol[b].get((l, "F1"), 0)
            got_K = vol[b].get((l, "K0"), 0) + vol[b].get((l, "K1"), 0)
            if abs(got_F - pred) > 1e-9 or abs(got_K - pred) > 1e-9:
                ok_fk = False
                print(
                    f"      mismatch {b} l={l}: F {got_F:.4f} K {got_K:.4f} predicted {pred:.4f} each"
                )
    check(
        ok_fk,
        "F and K volume per layer = 2(m384*384 + m224*224)/n each, in BOTH builds (per-source, unchanged by v112)",
    )
    # T site rows: old-tier transported width; v110 sum over sources of r_b, v112 sum over present groups
    ok_t = True
    for b in data:
        rows_by_l = {c["layer"]: c["A"][-2] for c in data[b]["calls"] if c["site"] == "T"}
        split_l = {c["layer"] for c in data[b]["calls"] if c["site"] == "T2"}  # the prune split moves 2 blocks to T2
        for l, rows in rows_by_l.items():
            k_y, m1, m0 = sched[l]
            old_w = (m1 * 384 + m0 * 224) if b == "v110_fk" else (384 * (m1 > 0) + 224 * (m0 > 0))
            # opT rows = (2k-1)n young + old width + n (Sigma_h) - 2n exactly when T2 runs (no 32-row pad: _D6_T is False)
            base = (2 * k_y - 1) * n if k_y else 0
            pred = base + old_w + n - (2 * n if l in split_l else 0)
            if rows != pred:
                ok_t = False
                print(f"      T rows {b} l={l}: got {rows}, predicted {pred}")
    check(
        ok_t,
        "T-site rows (transported width) match the schedule: v110 adds r_b per old source, v112 one r_G per group",
    )
    # C site: merged contraction inner width kk = 2 n k_y + old width (rounded up to 64 with exact-zero padding)
    ok_c = True
    for b in data:
        for c in data[b]["calls"]:
            if c["site"] != "C":
                continue
            l = c["layer"]
            k_y, m1, m0 = sched[l]
            old_w = (m1 * 384 + m0 * 224) if b == "v110_fk" else (384 * (m1 > 0) + 224 * (m0 > 0))
            kk = 2 * n * k_y + old_w
            if c["A"][-1] not in (kk, -(-kk // 64) * 64):
                ok_c = False
                print(f"      C width {b} l={l}: got {c['A'][-1]}, predicted {kk}")
    check(ok_c, "C-site inner width = 2n*k_young + old width (v110: sum_b r_b; v112: sum_G r_G), up to 64-padding")
    # old-tier logical volume per layer (units), split into shared-able terms (Q transport rows in T, trailing
    # contraction in C) and per-source in-basis terms (F, K)
    print("      old-tier logical units per layer [Q-transport + trailing-contraction | F + K]:")
    tot_sh = {}
    for b in data:
        sh_l, fk_l = [], []
        for l in range(16):
            k_y, m1, m0 = sched[l]
            old_w = (m1 * 384 + m0 * 224) if b == "v110_fk" else (384 * (m1 > 0) + 224 * (m0 > 0))
            Tcall = [c for c in data[b]["calls"] if c["site"] == "T" and c["layer"] == l]
            inner = Tcall[0]["A"][-1] if Tcall else n
            sh = old_w * inner * n / n**3 + (n * old_w * n / n**3 if l < 15 else 0.0)
            fk = sum(vol[b].get((l, s), 0) for s in ("F0", "F1", "K0", "K1"))
            sh_l.append(sh)
            fk_l.append(fk)
        tot_sh[b] = sum(sh_l)
        print(f"      {b}: " + " ".join(f"{a:.2f}|{c:.2f}" for a, c in zip(sh_l, fk_l)))
        print(f"      {b}: totals  shared-able {sum(sh_l):.2f} units, F+K {sum(fk_l):.2f} units")
    rem = tot_sh["v110_fk"] - tot_sh["v112_sb"]
    print(f"      removed by v112 (logical, pre-Strassen): {rem:.2f} units = {rem * 2 * n**3 / 2**41 * 100:.2f} pt "
          f"(V29 7B: net metered saving 1.23 pt, after Strassen-Winograd and net of the f64 solves)")
    ent = {b: sum(u for (l, st), u in vol[b].items() if st in ("E1a", "E1b", "E2")) for b in data}
    rem_e = ent["v110_fk"] - ent["v112_sb"]
    print(f"      entry sketches removed (E1a/E1b): {rem_e:.2f} units; transport+contraction+sketch = {rem + rem_e:.2f} units = "
          f"{(rem + rem_e) * 2 * n**3 / 2**41 * 100:.2f} pt logical (pre-Strassen; the metered split is printed below)")
    # old-tier transported width READ FROM THE RUN: T rows minus the young blocks and Sigma_h (young count min(l,5))
    ow = {}
    for b in data:
        split_l = {c["layer"] for c in data[b]["calls"] if c["site"] == "T2"}
        ow[b] = []
        for c in sorted((c for c in data[b]["calls"] if c["site"] == "T"), key=lambda c: c["layer"]):
            l = c["layer"]
            k_y = min(l, 5)
            ow[b].append(c["A"][-2] - (2 * k_y - 1) * n - n + (2 * n if l in split_l else 0))
    print(f"      old-tier transported width per layer from the runs: v110 {ow['v110_fk']}  v112 {ow['v112_sb']}")
    check(set(ow["v112_sb"]) <= {0, 224, 384, 608}, "v112: at most one 384 and one 224 basis transported at any layer (from the run's shapes)")
    falsifier(max(ow["v110_fk"]) > 608, f"v110 old transported width grows past two bases: max {max(ow['v110_fk'])} columns")
    # honest-finding checks
    fk112 = [
        sum(vol["v112_sb"].get((l, s), 0) for s in ("F0", "F1", "K0", "K1")) for l in range(16)
    ]
    check(fk112[14] > fk112[8] + 1.0,
          f"claim 'the v112 old tier is Theta(L) in products' REFUTED: per-source F+K volume grows l8 {fk112[8]:.2f} -> l14 {fk112[14]:.2f} units")
    # metered (post-Strassen) accounting of the v110 -> v112 difference, from the flopscope op log
    P = lambda x: 100 * x / 2**41
    diff_tot = data["v110_fk"]["total"] - data["v112_sb"]["total"]
    by_site = {}
    for b, sgn in (("v110_fk", 1), ("v112_sb", -1)):
        for c in data[b]["calls"]:
            k = c["site"]
            by_site.setdefault(k, [0.0, 0.0])
            by_site[k][0] += sgn * c.get("mm", 0.0)
            by_site[k][1] += sgn * c["flops"]
    out_ops = {}
    for b, sgn in (("v110_fk", 1), ("v112_sb", -1)):
        for l, ops in data[b].get("outside_by", {}).items():
            for op, f in ops.items():
                out_ops[op] = out_ops.get(op, 0.0) + sgn * f
    acc = sum(v[1] for v in by_site.values()) + sum(out_ops.values())
    print(f"      metered v110 - v112 = {P(diff_tot):.4f} pt; inside sw_matmul by site (matmul part | all): "
          + ", ".join(f"{k} {P(v[0]):+.3f}|{P(v[1]):+.3f}" for k, v in sorted(by_site.items()) if abs(v[1]) > 1e3))
    big = sorted(((op, f) for op, f in out_ops.items() if abs(P(f)) >= 0.005), key=lambda t: -abs(t[1]))
    print("      outside sw_matmul by op (v110 - v112, pt): " + ", ".join(f"{op} {P(f):+.3f}" for op, f in big))
    check(abs(acc - diff_tot) <= 1e-6 * data["v110_fk"]["total"], f"attribution is complete: sites + outside ops = {P(acc):.4f} pt = total difference")


if __name__ == "__main__":
    p3a()
    p3b()
    p3c()
    p3d()
    p3e()
    p4a()
    p4b()
    print(
        "\n"
        + (
            "ALL CHECKS PASS AND ALL FALSIFIERS FIRE"
            if not FAILS
            else f"{len(FAILS)} FAILURE(S):\n  " + "\n  ".join(FAILS)
        )
    )
    sys.exit(0 if not FAILS else 1)
