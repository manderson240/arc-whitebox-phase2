"""PROOFS.md Theorem 8 (G-SECT) -- the source-state correction: exact transport of the coincident-index entries of
the third-cumulant tensor into the DISTINCT entries of the next layer, as one merged same-leg n-hub source.

Setting (linear step only; the ReLU birth/ageing model is NOT under test here). h in R^n with exact third-cumulant
tensor K_h; z = h W (W stored (in,out)); Thm 1: K_z[ijk] = sum_{abc} W_ai W_bj W_ck K_h[abc] over ALL h-triples.
The factored-source chain carries a symmetric hub-form tensor S = sum_c w_c Sym3(A_c (x) A_c (x) E_c) that models
ONLY the pairwise-distinct entries D_h of K_h; its own coincident entries S2[a,c] = S[a,a,c], S_aaa = S[a,a,a] are
NOT T_h[a,c] = K_h[a,a,c], kappa3_h(a) = K_h[a,a,a]. Transporting S over all triples therefore (i) carries the wrong
coincident entries forward and (ii) omits the true ones. Theorem 8 (an identity, for ANY symmetric S agreeing with K_h
on distinct triples):

  (W^T)^{(x)3} K_h  =  (W^T)^{(x)3} S  +  sum_a Sym3( W_a (x) W_a (x) E_a ),
  E_a = ((T_h - S2)_off W)_a + ((kappa3_h(a) - S_aaa)/3) W_a,     i.e.  E = (M2 W)^T,
  M2 = (T_h - S2) with diagonal replaced by (kappa3_h - S_aaa)/3,  W_a = row a of W,

so the correction is ONE same-leg hub source with n hubs, legs A1 = W^T (rows of W), weights 1 -- exactly the
`sect` source of research/proto_gaphunt_e2e.py (same S2/S_aaa/M2 formulas). It transports and contributes its own S2
to the next layer's correction like any live source (checked over TWO linear layers below).

Distribution (explicit, exact cumulants): h = B (u^2 - 1) + D y + s o xi with u_k ~ N(0,1) iid (kappa3(u^2) = 8),
y_p = e_p - 1, e_p ~ Exp(1) iid (kappa3 = 2), xi_a = e_a - 1 iid (kappa3 = 2), all independent; every column of D has
exactly two non-zeros, so the D and xi terms touch only coincident entries and the chain's source S = 8 sum_k B_k^{(x)3}
(hub-form, hubs k, A1 = E = B, w = 8/3) equals K_h on every distinct triple while S2 != T_h and S_aaa != kappa3_h.
K_h = 8 sum_k B_k^{(x)3} + 2 sum_p D_p^{(x)3} + 2 diag(s^3) exactly (independence + multilinearity, Thm 1).
A plain-MC control (N = 2e5) confirms the tensor to its noise (info line; not the check).

Check (float64, n = 8 -> 8 -> 7): max |chain state - exact K_z| / max |K_z| <= 1e-12 at BOTH layers, all entries.
--perturb drop_diag : E without the (kappa3_h - S_aaa)/3 W_a term  -> must FAIL.
--perturb flip_s2   : M2 = T_h + S2 instead of T_h - S2               -> must FAIL.
(The un-corrected chain, 'no sect', is printed for size, not as a mutant.)
"""

from __future__ import annotations

import sys

import numpy as np


TOL = 1e-12


def sym3_hub_dense(A, E, w):
    """sum_c w_c [A_c x A_c x E_c + A_c x E_c x A_c + E_c x A_c x A_c] as a dense (n,n,n) tensor."""
    Aw = A * w[None, :]
    t = np.einsum("ac,bc,dc->abd", Aw, A, E)
    return t + t.transpose(0, 2, 1) + t.transpose(2, 0, 1)


def contract(W, K):
    return np.einsum("ai,bj,ck,abc->ijk", W, W, W, K, optimize=True)


def coincident(K):
    """(T[a,c] = K[a,a,c] with zero diagonal, kappa3(a) = K[a,a,a])."""
    n = K.shape[0]
    T = np.array([[K[a, a, c] for c in range(n)] for a in range(n)])
    k3 = np.diag(T).copy()
    np.fill_diagonal(T, 0.0)
    return T, k3


def source_s2(live):
    """S2[a,c] = S[a,a,c] and S_aaa from the legs of the live same-leg hub sources (as in proto_gaphunt_e2e)."""
    n = live[0][0].shape[0]
    S2 = np.zeros((n, n))
    Saaa = np.zeros(n)
    for A1, E, w in live:
        wv = w[None, :]
        S2 += (A1 * A1 * wv) @ E.T + 2.0 * ((A1 * E) * wv) @ A1.T
        Saaa += 3.0 * (A1 * A1 * E) @ w
    np.fill_diagonal(S2, 0.0)
    return S2, Saaa


def sect_source(W, T_h, k3_h, live, perturb: str | None):
    S2, Saaa = source_s2(live)
    sign = +1.0 if perturb == "flip_s2" else -1.0
    M2 = T_h + sign * S2
    np.fill_diagonal(M2, 0.0 if perturb == "drop_diag" else (k3_h - Saaa) / 3.0)
    G = M2 @ W
    return (W.T.copy(), G.T.copy(), np.ones(W.shape[0]))


def transport(W, live):
    return [(W.T @ A1, W.T @ E, w) for A1, E, w in live]


def dense_state(live):
    return sum(sym3_hub_dense(A1, E, w) for A1, E, w in live)


def make_distribution(rng, n=8, K=5, P=6):
    B = rng.standard_normal((n, K)) * 0.4
    D = np.zeros((n, P))
    for p in range(P):
        a, c = rng.choice(n, 2, replace=False)
        D[a, p], D[c, p] = rng.uniform(0.3, 0.8, 2)
    s = rng.uniform(0.3, 0.7, n)
    K_h = (
        8.0 * np.einsum("ak,bk,ck->abc", B, B, B)
        + 2.0 * np.einsum("ap,bp,cp->abc", D, D, D)
        + 2.0 * np.einsum("abc,a->abc", np.eye(n)[:, :, None] * np.eye(n)[:, None, :], s**3)
    )
    return B, D, s, K_h


def mc_control(rng, B, D, s, K_h, N=200_000):
    n, K = B.shape
    P = D.shape[1]
    u = rng.standard_normal((N, K))
    y = rng.exponential(1.0, (N, P)) - 1.0
    xi = rng.exponential(1.0, (N, n)) - 1.0
    h = (u * u - 1.0) @ B.T + y @ D.T + xi * s[None, :]
    hc = h - h.mean(0)
    K_mc = np.einsum("na,nb,nc->abc", hc, hc, hc) / N  # third central moment = third cumulant
    return np.max(np.abs(K_mc - K_h)) / np.max(np.abs(K_h))


def run(perturb: str | None) -> bool:
    rng = np.random.default_rng(8)
    n, m1, m2 = 8, 8, 7
    B, D, s, K_h = make_distribution(rng, n=n)
    W1 = rng.standard_normal((n, m1)) * np.sqrt(2.0 / n)
    W2 = rng.standard_normal((m1, m2)) * np.sqrt(2.0 / m1)
    # the chain's birth source: hub-form, exact on distinct triples, wrong on coincident ones
    S_live = [(B.copy(), B.copy(), np.full(B.shape[1], 8.0 / 3.0))]
    S_dense = dense_state(S_live)
    distinct = np.ones((n, n, n), bool)
    for a in range(n):
        distinct[a, a, :] = distinct[a, :, a] = distinct[:, a, a] = False
    print(
        f"  MC control (N=2e5): max|K_mc - K_h|/max|K_h| = {mc_control(rng, B, D, s, K_h):.2e} (noise-level, info)"
    )
    print(
        f"  S == K_h on distinct triples: {np.max(np.abs((S_dense - K_h)[distinct])):.1e};"
        f" S2 != T_h: {np.max(np.abs((S_dense - K_h)[~distinct])):.2e} (the defect Thm 8 removes)"
    )
    ok = True
    # ---------------- layer 1 ----------------
    K_z1 = contract(W1, K_h)
    T_h, k3_h = coincident(K_h)
    base1 = dense_state(transport(W1, S_live))
    sect1 = sect_source(W1, T_h, k3_h, S_live, perturb)
    live1 = transport(W1, S_live) + [sect1]
    state1 = dense_state(live1)
    e_base = np.max(np.abs(base1 - K_z1)) / np.max(np.abs(K_z1))
    e1 = np.max(np.abs(state1 - K_z1)) / np.max(np.abs(K_z1))
    print(
        f"  layer 1 (n={n}->{m1}): no-sect rel err {e_base:.2e} | chain+sect vs exact K_z1: {e1:.2e}"
        f" {'ok' if e1 <= TOL else 'VIOLATION'}"
    )
    ok &= e1 <= TOL
    # ---------------- layer 2: the correction transports and feeds the next correction ----------------
    K_z2 = contract(W2, K_z1)
    T_z1, k3_z1 = coincident(state1)  # from the CHAIN's own propagated state, not the oracle
    sect2 = sect_source(W2, T_z1, k3_z1, live1, perturb)
    state2 = dense_state(transport(W2, live1) + [sect2])
    e_base2 = np.max(np.abs(dense_state(transport(W2, transport(W1, S_live))) - K_z2)) / np.max(
        np.abs(K_z2)
    )
    e2 = np.max(np.abs(state2 - K_z2)) / np.max(np.abs(K_z2))
    print(
        f"  layer 2 (n={m1}->{m2}): no-sect rel err {e_base2:.2e} | chain+sect vs exact K_z2: {e2:.2e}"
        f" {'ok' if e2 <= TOL else 'VIOLATION'}"
    )
    ok &= e2 <= TOL
    return ok


if __name__ == "__main__":
    perturb = None
    if "--perturb" in sys.argv:
        i = sys.argv.index("--perturb")
        perturb = sys.argv[i + 1] if i + 1 < len(sys.argv) else "drop_diag"
    label = f"PERTURBED ({perturb})" if perturb else "sect identity"
    ok = run(perturb)
    print(f"check8 [{label}]: {'PASS' if ok else 'FAIL'}")
    sys.exit(0 if ok else 1)
