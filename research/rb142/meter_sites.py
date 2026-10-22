"""G-RB143 diagnostic: matmul pt by operand shape, both builds (net 0). usage: meter_sites.py <build> ..."""
import collections, importlib.util, sys, warnings
from pathlib import Path
import flopscope as flops, flopscope.numpy as fnp, numpy as np
from whestbench import SetupContext
from whestbench.domain import MLP
ROOT = Path(__file__).resolve().parents[2]; B = 2 ** 41
ws = [np.asarray(w) for w in np.load(ROOT / "research/lc/data/w_00000.npy")]
for build in sys.argv[1:]:
    d = (ROOT / build).resolve()
    spec = importlib.util.spec_from_file_location(f"m_{d.name}", d / "estimator.py"); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    mlp = MLP(width=1024, depth=16, weights=[fnp.array(w, dtype=fnp.float32) for w in ws], seed=0)
    e = m.Estimator(); e.setup(SetupContext(width=1024, depth=16, flop_budget=B, api_version="1", submission_dir=str(d)))
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        with flops.BudgetContext(flop_budget=B, quiet=True) as bc: e.predict(mlp, B)
    agg = collections.defaultdict(lambda: [0, 0.0])
    for r in bc.op_log:
        if r.op_name in ("matmul", "einsum", "linalg.solve", "linalg.qr", "linalg.eigh"):
            k = (r.op_name, str(r.shapes)[:70]); agg[k][0] += 1; agg[k][1] += 100 * r.flop_cost / B
    print(f"=== {build} util {100*bc.flops_used/B:.4f}")
    for k, (c, pt) in sorted(agg.items(), key=lambda kv: -kv[1][1])[:28]: print(f"{pt:8.4f} n={c:4d} {k[0]} {k[1]}")
