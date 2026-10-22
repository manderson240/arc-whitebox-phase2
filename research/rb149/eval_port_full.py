"""Local evaluator for the rebuild port (G-RB3): real whestbench predict() under a flopscope BudgetContext, f32, auto-routing
warnings as errors. Per net: metered budget %, op count, in-process residual, final MSE vs the 1e9 truth, max rel output deviation vs
the f64 oracle (research/rebuild/est_<oracle>_<net>.npy) when present.  usage: eval_port.py <submission_dir> <oracle_cfg|-> nets..."""
import sys, json, time, warnings, importlib.util, statistics
from pathlib import Path
import numpy as np, flopscope as flops, flopscope.numpy as fnp
from whestbench import SetupContext
from whestbench.domain import MLP
OUT = Path(__file__).resolve().parent; HERE = OUT.parent / "rebuild"; DATA = HERE.parent / "full" / "data"; B = 2**41
def load(d):
    spec = importlib.util.spec_from_file_location(f"est_{d.name}_{time.time_ns()}", d / "estimator.py")
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m
def main():
    d = Path(sys.argv[1]).resolve(); oracle = sys.argv[2]; nets = [int(x) for x in sys.argv[3:]]
    mod = load(d); out_rows = []
    for mid in nets:
        ws = [np.asarray(w) for w in np.load(DATA / f"w_{mid:05d}.npy")]
        truth = np.load(DATA / f"truth_{mid:05d}.npz")["all_layer_means"].astype(np.float64)
        mlp = MLP(width=1024, depth=16, weights=[fnp.array(w, dtype=fnp.float32) for w in ws], seed=0)
        e = mod.Estimator(); t0 = time.time()
        e.setup(SetupContext(width=1024, depth=16, flop_budget=B, api_version="1", submission_dir=str(d))); tsetup = time.time() - t0
        with warnings.catch_warnings():
            warnings.filterwarnings("error", message=".*auto-routed.*")
            with flops.BudgetContext(flop_budget=B, quiet=True) as bc:
                out = np.asarray(e.predict(mlp, B), dtype=np.float64)
        row = dict(net=mid, budget_pct=100 * bc.flops_used / B, ops=len(bc.op_log), residual_s=bc.residual_wall_time_s,
                   setup_s=tsetup, final_mse=float(((out[-1] - truth[-1]) ** 2).mean()),
                   layer_mse=[float(((out[i] - truth[i]) ** 2).mean()) for i in range(16)])
        if oracle != "-":
            f = HERE / f"est_{oracle}_{mid:05d}.npy"
            if f.exists():
                ref = np.load(f); row["oracle_final_mse"] = float(((ref[-1] - truth[-1]) ** 2).mean())
                row["max_rel_dev"] = float(np.abs(out[-1] - ref[-1]).max() / np.abs(ref[-1]).max())
                row["mse_ratio"] = row["final_mse"] / row["oracle_final_mse"]
        print(json.dumps({k: v for k, v in row.items() if k != "layer_mse"}), flush=True)
        out_rows.append(row); np.save(OUT / f"heldout_port_{d.name}_{mid:05d}.npy", out)
    with open(OUT / "heldout_port_results.jsonl", "a") as fo:
        for r in out_rows: fo.write(json.dumps(dict(sub=d.name, t=time.strftime("%Y-%m-%dT%H:%M"), **r)) + "\n")
if __name__ == "__main__":
    main()
