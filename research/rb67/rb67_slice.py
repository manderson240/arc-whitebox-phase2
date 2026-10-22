"""G-RB68 (pre-registered in R2_GO_NOGO.md BEFORE this ran): the (1,1,1)-induced share of the (2,1) read, per layer.

Memoryless (slice-only) transport of the previous layer's h-side kappa3: M = F(I, I, V), V = 3 T_off^T + diag(D3) (DESIGN step 5),
whose slices equal T_h^{l-1} exactly and whose (1,1,1) part is zero; at layer l its read is R_mem = read_block(1, W^T, W^T, W^T V).
The chain's actual read Tz^l minus R_mem = Delta^l, the (1,1,1)-induced part that every slice-only recursion must regenerate.
Reports: norm share of Delta (off-diag and diag), its top-k singular energy, cos^2 with R_mem and with Tz, per-entry rms.
usage: python rb67_slice.py --nets 0 2 4
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np


HERE = Path(__file__).resolve().parent
REB = HERE.parent / "rebuild"
sys.path.insert(0, str(REB))
sys.path.insert(0, str(REB.parent))
import k3chain as K  # noqa: E402
import srcchain as S  # noqa: E402


N = S.N


def off(M):
    M = M.copy()
    np.fill_diagonal(M, 0.0)
    return M


def cos2(A, B):
    return float(np.sum(A * B) ** 2 / max(np.sum(A * A) * np.sum(B * B), 1e-300))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--nets", type=int, nargs="+", default=[0])
    ap.add_argument("--ks", type=int, nargs="+", default=[8, 32, 128])
    args = ap.parse_args()
    out = open(HERE / "rb67_slice.jsonl", "a")
    for mid in args.nets:
        ws, _ = K.load_net(mid)
        st = np.load(HERE / f"state_{mid:05d}.npz")
        for l in range(
            2, S.D - 1
        ):  # Tz^l needs T_h^{l-1}; layer 1's Tz is the newborn of layer 0 only
            Th = st[f"Th_{l - 1}"].astype(np.float64)
            Tz = st[f"Tz_{l}"].astype(np.float64)
            W = ws[l].astype(np.float64)
            V = 3.0 * off(Th).T + np.diag(np.diag(Th))
            Wt = W.T.copy()
            Rmem = S.read_block(1.0, Wt, Wt, Wt @ V)
            D = Tz - Rmem
            Do, Tzo, Ro = off(D), off(Tz), off(Rmem)
            sv = np.linalg.svd(Do, compute_uv=False)
            e = float(np.sum(sv**2))
            row = dict(
                net=mid,
                layer=l,
                share_off=float(np.linalg.norm(Do) / np.linalg.norm(Tzo)),
                share_diag=float(np.linalg.norm(np.diag(D)) / np.linalg.norm(np.diag(Tz))),
                rmem_over_tz=float(np.linalg.norm(Ro) / np.linalg.norm(Tzo)),
                cos2_delta_rmem=cos2(Do, Ro),
                cos2_delta_tz=cos2(Do, Tzo),
                cos2_rmem_tz=cos2(Ro, Tzo),
                rms_tz=float(np.sqrt(np.mean(Tzo**2))),
                rms_delta=float(np.sqrt(np.mean(Do**2))),
                rms_rmem=float(np.sqrt(np.mean(Ro**2))),
            )
            for k in args.ks:
                row[f"delta_top{k}_energy"] = float(np.sum(sv[:k] ** 2) / e)
            svt = np.linalg.svd(Tzo, compute_uv=False)
            row["tz_top32_energy"] = float(np.sum(svt[:32] ** 2) / np.sum(svt**2))
            # best scalar rescaling of R_mem toward Tz (what a per-layer constant could buy)
            lam = float(np.sum(Ro * Tzo) / max(np.sum(Ro * Ro), 1e-300))
            row["lam_best"] = lam
            row["share_off_after_lambda"] = float(
                np.linalg.norm(Tzo - lam * Ro) / np.linalg.norm(Tzo)
            )
            print(json.dumps(row), flush=True)
            out.write(json.dumps(row) + "\n")
    out.close()


if __name__ == "__main__":
    main()
