"""Same-net meter for the V30 claim audit (adapted from meter3.py).
Nets come from research/full/data (w_<id>.npy, truth_<id>.npz), e.g. 1340, the K=2 screen's net.
Prints util (flopscope, 0.12.3 under research/remote/venv), final-layer raw MSE vs the truth, and,
when the estimator returns all layers, per-layer MSE vs all_layer_means.
usage: meter_full.py <build> <net_id> [<net_id> ...]"""

import importlib.util
import json
import sys
import time
import warnings
from pathlib import Path

import flopscope as flops
import flopscope.numpy as fnp
import numpy as np
from whestbench import SetupContext
from whestbench.domain import MLP


ROOT = Path(__file__).resolve().parents[2]
B = 2**41
build = sys.argv[1]
NETS = [int(a) for a in sys.argv[2:]]
d = (ROOT / build).resolve()
spec = importlib.util.spec_from_file_location(f"m_{d.name}", d / "estimator.py")
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
for k in NETS:
    ws = [np.asarray(w) for w in np.load(ROOT / f"research/full/data/w_{k:05d}.npy")]
    tz = np.load(ROOT / f"research/full/data/truth_{k:05d}.npz")
    t0 = time.time()
    mlp = MLP(width=1024, depth=16, weights=[fnp.array(w, dtype=fnp.float32) for w in ws], seed=0)
    e = m.Estimator()
    e.setup(
        SetupContext(width=1024, depth=16, flop_budget=B, api_version="1", submission_dir=str(d))
    )
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        with flops.BudgetContext(flop_budget=B, quiet=True) as bc:
            out = e.predict(mlp, B)
    arr = np.asarray(out, dtype=np.float64)
    final = arr[-1] if arr.ndim == 2 else arr
    rec = dict(
        build=build,
        net=k,
        util_pt=round(100 * bc.flops_used / B, 4),
        raw_final=float(np.mean((final - tz["final_means"]) ** 2)),
        wall_s=round(time.time() - t0, 1),
    )
    if arr.ndim == 2 and arr.shape == tz["all_layer_means"].shape:
        rec["per_layer"] = [
            float(np.mean((arr[i] - tz["all_layer_means"][i]) ** 2)) for i in range(arr.shape[0])
        ]
    print(json.dumps(rec), flush=True)
