"""G-RB146 lever scan: dump the FULL flopscope op ledger of one build on net 0 (in-process, f32, BudgetContext),
one JSON line per op {i, op, flops, shapes, subscripts}. Read-only on the build. Same predict path as
research/rebuild/fingerprint.py. Output: argv[2] (jsonl). ~1 min at OMP 8. Run under timing_lock SHARED via bg.sh.

    whest-starterkit/.venv/bin/python research/rb146/opledger146.py submissions/v112_sb <out.jsonl>
"""

import importlib.util
import json
import sys
import warnings
from pathlib import Path

import flopscope as flops
import flopscope.numpy as fnp
import numpy as np
from whestbench import SetupContext
from whestbench.domain import MLP


ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "research" / "lc" / "data"
B = 2**41


def main():
    d = (ROOT / sys.argv[1]).resolve()
    out = Path(sys.argv[2])
    spec = importlib.util.spec_from_file_location(f"ol_{d.name}", d / "estimator.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    ws = [np.asarray(w) for w in np.load(DATA / "w_00000.npy")]
    mlp = MLP(width=1024, depth=16, weights=[fnp.array(w, dtype=fnp.float32) for w in ws], seed=0)
    e = m.Estimator()
    e.setup(
        SetupContext(width=1024, depth=16, flop_budget=B, api_version="1", submission_dir=str(d))
    )
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        with flops.BudgetContext(flop_budget=B, quiet=True) as bc:
            e.predict(mlp, B)
    with out.open("w") as f:
        for i, r in enumerate(bc.op_log):
            rec = dict(
                i=i,
                op=r.op_name,
                flops=int(r.flop_cost),
                shapes=[list(map(int, s)) for s in (r.shapes or ())],
            )
            sub = getattr(r, "subscripts", None)
            if sub:
                rec["sub"] = sub
            f.write(json.dumps(rec) + "\n")
    print(
        json.dumps(
            dict(
                build=sys.argv[1],
                ops=len(bc.op_log),
                util_pt=round(100 * bc.flops_used / B, 4),
                out=str(out),
            )
        )
    )


if __name__ == "__main__":
    main()
