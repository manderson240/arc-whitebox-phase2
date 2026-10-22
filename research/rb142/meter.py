"""G-RB143 step 3: metered util of v110_fk vs the shared-basis stub (same predict path as research/rebuild/fingerprint.py, net 0,
f32, flopscope BudgetContext) + net-0 raw MSE vs the 1e9 truth + per-op-kind pt. usage: meter.py <build-dir-rel-to-repo> ..."""
import collections, hashlib, importlib.util, json, sys, time, warnings
from pathlib import Path
import flopscope as flops
import flopscope.numpy as fnp
import numpy as np
from whestbench import SetupContext
from whestbench.domain import MLP
ROOT = Path(__file__).resolve().parents[2]
B = 2 ** 41
ws = [np.asarray(w) for w in np.load(ROOT / "research/lc/data/w_00000.npy")]
truth = np.load(ROOT / "research/lc/data/truth_00000.npz")["final_means"]
for build in sys.argv[1:]:
  if True:
    d = (ROOT / build).resolve()
    spec = importlib.util.spec_from_file_location(f"m_{d.name}", d / "estimator.py"); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    mlp = MLP(width=1024, depth=16, weights=[fnp.array(w, dtype=fnp.float32) for w in ws], seed=0)
    e = m.Estimator(); e.setup(SetupContext(width=1024, depth=16, flop_budget=B, api_version="1", submission_dir=str(d)))
    t0 = time.time()
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        with flops.BudgetContext(flop_budget=B, quiet=True) as bc:
            out = e.predict(mlp, B)
    arr = np.asarray(out, dtype=np.float64)
    arr = arr[-1] if arr.ndim == 2 else arr  # predict returns per-layer means; score the final layer
    mse = float(np.mean((arr - truth) ** 2))
    agg = collections.defaultdict(float)
    for r in bc.op_log:
        agg[r.op_name] += 100 * r.flop_cost / B
    print(json.dumps(dict(build=build, ops=len(bc.op_log), util_pt=round(100 * bc.flops_used / B, 4), net0_raw=mse, wall_s=round(time.time() - t0, 1),
                          by_op={k: round(v, 4) for k, v in sorted(agg.items(), key=lambda kv: -kv[1])[:12]})), flush=True)
