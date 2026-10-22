"""G-RB137 step 1b: diff the flopscope op_log (op_name + operand shapes) of two builds on one net.
python opdiff.py submissions/<a> submissions/<b> [net]  -> json lines + summary table to stdout."""

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


def oplog(build, net):
    d = ROOT / build
    spec = importlib.util.spec_from_file_location(f"od_{d.name}", d / "estimator.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    e = m.Estimator()
    e.setup(SetupContext(width=1024, depth=16, flop_budget=B, api_version="1", submission_dir=str(d)))
    ws = [np.asarray(w) for w in np.load(ROOT / f"research/lc/data/w_{net:05d}.npy")]
    mlp = MLP(width=1024, depth=16, weights=[fnp.array(w, dtype=fnp.float32) for w in ws], seed=0)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        with flops.BudgetContext(flop_budget=B, quiet=True) as bc:
            e.predict(mlp, B)
    return list(bc.op_log), bc.flops_used


def key(r):
    return (r.op_name, r.subscripts, str(r.shapes))


a, b = sys.argv[1], sys.argv[2]
net = int(sys.argv[3]) if len(sys.argv) > 3 else 0
la, fa = oplog(a, net)
lb, fb = oplog(b, net)
ca, cb = collections.Counter(map(key, la)), collections.Counter(map(key, lb))
ta, tb = collections.defaultdict(float), collections.defaultdict(float)
fla, flb = collections.defaultdict(int), collections.defaultdict(int)
for r in la:
    ta[key(r)] += r.flopscope_backend_duration_s or 0.0
    fla[key(r)] += r.flop_cost
for r in lb:
    tb[key(r)] += r.flopscope_backend_duration_s or 0.0
    flb[key(r)] += r.flop_cost
print(json.dumps(dict(a=a, b=b, net=net, ops_a=len(la), ops_b=len(lb), util_a=100 * fa / B, util_b=100 * fb / B)))
rows = []
for k in set(ca) | set(cb):
    dn = cb[k] - ca[k]
    if dn:
        rows.append(dict(op=k[0], sub=k[1], shapes=k[2], n_a=ca[k], n_b=cb[k], d=dn,
                         dflop=flb[k] - fla[k], dback_ms=round(1e3 * (tb[k] - ta[k]), 2)))
rows.sort(key=lambda r: -abs(r["d"]))
byop = collections.Counter()
byopneg = collections.Counter()
for r in rows:
    (byop if r["d"] > 0 else byopneg)[r["op"]] += r["d"]
print("BY_OP added", json.dumps(byop.most_common()))
print("BY_OP removed", json.dumps(byopneg.most_common()))
byname_a = collections.Counter(r.op_name for r in la)
byname_b = collections.Counter(r.op_name for r in lb)
print("NET_BY_OP", json.dumps({k: byname_b[k] - byname_a[k] for k in set(byname_a) | set(byname_b) if byname_b[k] != byname_a[k]}))
print("LOCAL_BACKEND_s a=%.3f b=%.3f" % (sum(r.flopscope_backend_duration_s or 0 for r in la), sum(r.flopscope_backend_duration_s or 0 for r in lb)))
for r in rows:
    print(json.dumps(r))
