"""3-net meter (VALID nets 10, 13, 16; not used to fit the head): per build, util (flopscope 0.12.3 when run with
research/remote/venv) and pooled raw final-layer MSE vs the 1e9 truth. usage: meter3.py <build> ..."""
import importlib.util, json, sys, time, warnings
from pathlib import Path
import flopscope as flops, flopscope.numpy as fnp, numpy as np
from whestbench import SetupContext
from whestbench.domain import MLP
ROOT = Path(__file__).resolve().parents[2]; B = 2 ** 41; NETS = (10, 13, 16)
data = {k: ([np.asarray(w) for w in np.load(ROOT / f"research/lc/data/w_{k:05d}.npy")],
            np.load(ROOT / f"research/lc/data/truth_{k:05d}.npz")["final_means"]) for k in NETS}
for build in sys.argv[1:]:
    d = (ROOT / build).resolve()
    spec = importlib.util.spec_from_file_location(f"m_{d.name}", d / "estimator.py"); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    se = sq = 0.0; utils = []; t0 = time.time(); per = {}
    for k, (ws, truth) in data.items():
        mlp = MLP(width=1024, depth=16, weights=[fnp.array(w, dtype=fnp.float32) for w in ws], seed=0)
        e = m.Estimator(); e.setup(SetupContext(width=1024, depth=16, flop_budget=B, api_version="1", submission_dir=str(d)))
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            with flops.BudgetContext(flop_budget=B, quiet=True) as bc:
                out = e.predict(mlp, B)
        arr = np.asarray(out, dtype=np.float64); arr = arr[-1] if arr.ndim == 2 else arr
        per[k] = float(np.mean((arr - truth) ** 2)); utils.append(100 * bc.flops_used / B)
    print(json.dumps(dict(build=build, util_pt=round(float(np.mean(utils)), 4), raw_pooled=float(np.mean(list(per.values()))),
                          per={str(k): v for k, v in per.items()}, wall_s=round(time.time() - t0, 1))), flush=True)
