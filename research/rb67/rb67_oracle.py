"""G-RB67 step 2 (pre-registered in R2_GO_NOGO.md BEFORE this ran): is the young A leg a (diag + rank-r) image of the P leg?

Facts used (srcchain.py): birth legs P = I, A = f1 o Cz_off; both aged by X <- Phi o (W^T X)  =>  A_s^l = P_s^l a_s, a_s = D_s Cz_off^s static.
If a_s ~ d(c) + U V^T then A = P d(c) + (P U) V^T and the young source costs 3 + 4r/n units instead of 4 (one dense transport).
Oracle: (A) Frobenius energy of Cz_off^s captured by off(top-r eigen) and by the alternating (diag + rank-r) fit, every layer;
        (B) at layers l in {6,10,14}, sources of age 1..4: exact G11 read  read_block(3, P, A, A o f2_s)  vs the read with A_r = P a_s^r;
            per-source and SUMMED young-tier relative Frobenius error of the (2,1) read (off-diagonal) and of the (3) diagonal.
usage: python rb67_oracle.py --nets 0 2 4 [--layers 6 10 14] [--ranks 32 64 128 256]
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np


HERE = Path(__file__).resolve().parent
REB = HERE.parent / "rebuild"
sys.path.insert(0, str(REB))
sys.path.insert(0, str(REB.parent))
import k3chain as K  # noqa: E402
import proto_r2 as R  # noqa: E402
import srcchain as S  # noqa: E402


N = S.N


def off(M):
    M = M.copy()
    np.fill_diagonal(M, 0.0)
    return M


def relfro(E, Ref):
    return float(np.linalg.norm(E) / max(np.linalg.norm(Ref), 1e-300))


def lowrank_plus_diag(Coff, r, iters=4):
    """alternating projection: off-diagonal target Coff, free diagonal. Returns (U, lam) with C_fit = U diag(lam) U^T."""
    d = np.zeros(N)
    for _ in range(iters):
        M = Coff + np.diag(d)
        lam, U = np.linalg.eigh(M)
        idx = np.argsort(-np.abs(lam))[:r]
        U, lam = U[:, idx], lam[idx]
        d = np.einsum("ij,j,ij->i", U, lam, U)
    return U, lam


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--nets", type=int, nargs="+", default=[0])
    ap.add_argument("--layers", type=int, nargs="+", default=[6, 10, 14])
    ap.add_argument("--ranks", type=int, nargs="+", default=[32, 64, 128, 256])
    ap.add_argument("--ages", type=int, nargs="+", default=[1, 2, 3, 4])
    args = ap.parse_args()
    out = open(HERE / "rb67_oracle.jsonl", "a")
    for mid in args.nets:
        ws, _ = K.load_net(mid)
        st = np.load(HERE / f"state_{mid:05d}.npz")
        print(f"net {mid}: chain final uncorrected {float(st['final']):.4e}", flush=True)
        Phi, f1, f2, Coff, birth_fit = {}, {}, {}, {}, {}
        # ---- part A: rank profile of the birth matrix per layer
        for s in range(S.D - 1):
            mu_z, var_z = st[f"mu_z_{s}"], st[f"var_z_{s}"]
            Sig = st[f"Sig_z_{s}"].astype(np.float64)
            sig, a, pdf, cdf, m1, m2, m3 = R.relu_moments(mu_z, var_z)
            fh = R.coeffs_relu(sig, a, pdf, cdf, m1, 5)
            Phi[s], f1[s], f2[s] = cdf, fh[1], fh[2]
            Coff[s] = off(Sig)
            t0 = time.time()
            lam, U = np.linalg.eigh(Sig)
            idx = np.argsort(-np.abs(lam))
            lam, U = lam[idx], U[:, idx]
            e_off = float(np.sum(Coff[s] ** 2))
            tr = float(np.sum(lam))
            row = dict(
                net=mid,
                part="A",
                layer=s,
                e_off=e_off,
                trace=tr,
                var_mean=float(var_z.mean()),
                off_rms=float(np.sqrt(e_off / (N * (N - 1)))),
                top1_trace_share=float(lam[0] / tr),
                top8_trace_share=float(lam[:8].sum() / tr),
                eigh_s=time.time() - t0,
            )
            for r in args.ranks:
                Cr = (U[:, :r] * lam[:r]) @ U[:, :r].T
                row[f"trunc_r{r}"] = float(
                    np.sum(off(Sig - Cr) ** 2) / e_off
                )  # residual off-diag energy fraction, plain truncation
                row[f"trace_r{r}"] = float(lam[:r].sum() / tr)
                Uf, lf = lowrank_plus_diag(Coff[s], r)
                Cf = (Uf * lf) @ Uf.T
                row[f"fit_r{r}"] = float(
                    np.sum((Coff[s] - off(Cf)) ** 2) / e_off
                )  # residual with free diagonal
                birth_fit[(s, r)] = (Uf, lf)
            print(json.dumps(row), flush=True)
            out.write(json.dumps(row) + "\n")
        # ---- part B: per-source read error of the (2,1)/(3) slices at layers l for sources of age 1..4
        for l in args.layers:
            Wl = ws[l].astype(np.float64)
            tot_exact = np.zeros((N, N))
            tot_r = {r: np.zeros((N, N)) for r in args.ranks}
            for age in args.ages:
                s = l - age
                if s < 0:
                    continue
                # P_s^l = W_l^T Phi_{l-1} W_{l-1}^T ... Phi_{s+1} W_{s+1}^T   (z side at loop l)
                P = ws[s + 1].astype(np.float64).T.copy()
                for m in range(s + 2, l + 1):
                    P = ws[m].astype(np.float64).T @ (Phi[m - 1][:, None] * P)
                a_s = f1[s][:, None] * Coff[s]
                A = P @ a_s
                Y = A * f2[s][None, :]
                Rx = S.read_block(3.0, P, A, Y)
                tot_exact += Rx
                row = dict(
                    net=mid,
                    part="B",
                    layer=l,
                    birth=s,
                    age=age,
                    read_off_fro=float(np.linalg.norm(off(Rx))),
                    read_diag_fro=float(np.linalg.norm(np.diag(Rx))),
                    P_fro=float(np.linalg.norm(P)),
                    A_fro=float(np.linalg.norm(A)),
                )
                for r in args.ranks:
                    Uf, lf = birth_fit[(s, r)]
                    Cf_off = off(
                        (Uf * lf) @ Uf.T
                    )  # = U V^T - diag(.) : the (diag + rank-r) form the port would carry
                    Ar = P @ (f1[s][:, None] * Cf_off)
                    Rr = S.read_block(3.0, P, Ar, Ar * f2[s][None, :])
                    tot_r[r] += Rr
                    row[f"rel21_r{r}"] = relfro(off(Rr - Rx), off(Rx))
                    row[f"rel3_r{r}"] = relfro(np.diag(Rr - Rx), np.diag(Rx))
                    row[f"relA_r{r}"] = relfro(Ar - A, A)
                print(json.dumps(row), flush=True)
                out.write(json.dumps(row) + "\n")
            row = dict(
                net=mid,
                part="B_sum",
                layer=l,
                ages=args.ages,
                read_off_fro=float(np.linalg.norm(off(tot_exact))),
            )
            for r in args.ranks:
                row[f"rel21_r{r}"] = relfro(off(tot_r[r] - tot_exact), off(tot_exact))
                row[f"rel3_r{r}"] = relfro(np.diag(tot_r[r] - tot_exact), np.diag(tot_exact))
            print(json.dumps(row), flush=True)
            out.write(json.dumps(row) + "\n")
    out.close()


if __name__ == "__main__":
    main()
