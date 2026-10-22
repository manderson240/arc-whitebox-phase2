"""G-RB67 step 1: dump the f64 shipped-twin chain's own per-layer state (mu_z, var_z, Sigma_z, Phi) on FIT nets via the
existing `lc_hook` of srcchain.src_closure (the hook returns the carried mean UNCHANGED: the chain is not modified).
Config = results.jsonl cfg `src_r4_rf1_agedown:6:384,8:224` (rank 4, range-finder power 1, own basis 384 at age 6, nested 224 at age 8).
usage: python rb67_capture.py --nets 0 2 4
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

import numpy as np


HERE = Path(__file__).resolve().parent
REB = HERE.parent / "rebuild"
sys.path.insert(0, str(REB))
sys.path.insert(0, str(REB.parent))
import k3chain as K  # noqa: E402
import proto_sectcost as SC  # noqa: E402
import srcchain as S  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--nets", type=int, nargs="+", default=[0])
    args = ap.parse_args()
    S.RF["on"], S.RF["power"] = True, 1
    aged = [("own", 6, 384), (8, 224)]
    g = SC.load_g()
    kappa = np.load(REB / "kappa_table.npz")["kappa"]
    for mid in args.nets:
        ws, truth = K.load_net(mid)
        store = {}

        def hook(l, d, store=store):
            # last layer passes placeholders for Sig/T; we keep mu_z/var_z/Sig_z (the real pre-activation state) at every layer
            store[f"mu_z_{l}"] = d["mu_z"].astype(np.float64)
            store[f"var_z_{l}"] = d["var_z"].astype(np.float64)
            store[f"Sig_z_{l}"] = d["Sig_z"].astype(
                np.float32
            )  # 4 MB per layer; spectrum needs ~1e-7 relative, f32 is fine
            # G-RB68: the chain's z-side kappa3 read Tz (all sources) and the closure's h-side slice T_h (placeholders at the last layer)
            store[f"Tz_{l}"] = d["Tz"].astype(np.float32)
            store[f"Th_{l}"] = d["T"].astype(np.float32)
            return d["mu"]

        t0 = time.time()
        est = S.src_closure(
            ws, g, kappa, rank=4, aged=aged, log=lambda s: print(s, flush=True), lc_hook=hook
        )
        final = K.mse(est[-1], truth[-1])
        print(
            f"net {mid} final uncorrected MSE {final:.4e} ({time.time() - t0:.0f}s)  control: G-RB44 gate-5 rows 2.5788/4.3529/3.2995e-8 were rank 4 own:5",
            flush=True,
        )
        np.savez(HERE / f"state_{mid:05d}.npz", final=final, **store)


if __name__ == "__main__":
    main()
