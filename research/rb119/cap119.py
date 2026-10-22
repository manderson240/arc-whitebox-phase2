"""G-RB119 step 1: capture the v95 twin's own chain var/k3/k4 (uninjected BASE) per layer for one FIT net. usage: cap119.py <net>"""
import sys, numpy as np
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import w117 as W
S = W.S
rec = {}
orig = S.src_closure
def wrapped(*a, **k):
    def hook(l, ctx):
        rec[l] = (np.diag(ctx["Sig_z"]).copy(), np.diag(ctx["Tz"]).copy(), np.asarray(ctx["k4z"]).copy())
        return ctx["k4z"]
    S.K4HOOK = hook
    return orig(*a, **k)
S.src_closure = wrapped
mid = int(sys.argv[1])
final, secs = W.run(mid, {})
np.savez(HERE / f"chain_{mid:05d}.npz", var=np.stack([rec[l][0] for l in range(16)]), k3=np.stack([rec[l][1] for l in range(16)]),
         k4=np.stack([rec[l][2] for l in range(16)]), final=final)
print(mid, final, secs)
