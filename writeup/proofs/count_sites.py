"""P4 grounding: per-LAYER logical dense-product shapes of one real predict (n = 1024, depth 16, f32, net 0).

Wraps the build's sw_matmul (every large product goes through it) and attributes each call to the layer being
processed by iterating mlp.weights through a list subclass that records the current index. Records the LOGICAL
shape of each call (batch, rows, inner, cols) -- the product before Strassen-Winograd -- so the counts are the
structural quantity the P4 cost model talks about, independent of the Strassen depth.  Also records the metered
matmul/einsum flops per layer from the flopscope op log.

usage: count_sites.py submissions/<build> out.json
Run through research/rebuild/bg.sh (about 1-2 min and ~6 GB per build).
"""

import collections
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


ROOT = Path.home() / "cohezion-labs/arc-whitebox"
B = 2**41
d = ROOT / sys.argv[1]
spec = importlib.util.spec_from_file_location("e", d / "estimator.py")
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

CUR = {"l": -1}


class LayerList(list):
    def __iter__(self):
        for i, x in enumerate(list.__iter__(self)):
            CUR["l"] = i
            yield x


ws = [np.asarray(w) for w in np.load(ROOT / "research/lc/data/w_00000.npy")]
mlp = MLP(width=1024, depth=16, weights=LayerList([fnp.array(w, dtype=fnp.float32) for w in ws]), seed=0)
e = m.Estimator()
e.setup(SetupContext(width=1024, depth=16, flop_budget=B, api_version="1", submission_dir=str(d)))

calls = []
orig = m.sw_matmul
BC = {}


def wrapped(A, Bm, site, *a, **k):
    bc = BC["bc"]
    f0, o0 = bc.flops_used, len(bc.op_log)
    r = orig(A, Bm, site, *a, **k)
    mm = sum(o.flop_cost for o in bc.op_log[o0:] if o.op_name in ("matmul", "einsum"))
    calls.append(dict(layer=CUR["l"], site=str(site.name), A=list(A.shape), B=list(Bm.shape),
                      flops=bc.flops_used - f0, mm=mm, o0=o0, o1=len(bc.op_log)))
    return r


m.sw_matmul = wrapped
per_layer_mm = collections.defaultdict(float)
with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    with flops.BudgetContext(flop_budget=B, quiet=True) as bc:
        BC["bc"] = bc
        # layer boundaries in the op log (index of the first op of each layer); the last layer runs to the end of the log
        bounds = []

        def it(self):
            for i, x in enumerate(list.__iter__(self)):
                bounds.append(len(bc.op_log))
                CUR["l"] = i
                yield x

        LayerList.__iter__ = it
        e.predict(mlp, B)
    bounds.append(len(bc.op_log))
    for i in range(len(bounds) - 1):
        per_layer_mm[i] = sum(o.flop_cost for o in bc.op_log[bounds[i]:bounds[i + 1]] if o.op_name in ("matmul", "einsum"))
# flops by op name OUTSIDE sw_matmul calls, per layer (Gram einsums, solves, qr, eigh, thin matmuls, glue)
inside = set()
for c in calls:
    inside.update(range(c["o0"], c["o1"]))
outside_by = collections.defaultdict(lambda: collections.defaultdict(float))
for i in range(len(bounds) - 1):
    for j in range(bounds[i], bounds[i + 1]):
        if j not in inside:
            o = bc.op_log[j]
            outside_by[i][o.op_name] += o.flop_cost
print(f"{sys.argv[1]}: total util {100 * bc.flops_used / B:.6f} pt, sw_matmul calls {len(calls)}")
json.dump(
    dict(
        build=sys.argv[1],
        total=bc.flops_used,
        calls=calls,
        per_layer_mm={int(k): v for k, v in per_layer_mm.items()},
        outside_by={int(k): dict(v) for k, v in outside_by.items()},
    ),
    open(sys.argv[2], "w"),
)
