"""G-RB155 copy of rebuild/aug_run.py restricted to the Lambda-fit DUMP pass. usage: dump155.py <tag> nets...
env AUG/FREE/QCOEF/LAMBDA/METRIC/DUMP read by rebuild/srcchain_aug (unchanged). Differences vs aug_run.py: no append to rebuild/results.jsonl
(rows go to rb155/dump155.jsonl) and no FITQ branch. DUMP must point into rb155/ (asserted) so rebuild/aug_dump* are never overwritten."""

import json
import os
import sys
import time
from pathlib import Path

import numpy as np


RB = Path("~/cohezion-labs/arc-whitebox/research/rebuild")
HERE = Path(__file__).resolve().parent
RES = RB.parent
sys.path.insert(0, str(RB))
sys.path.insert(0, str(RES))
import proto_r2 as R  # noqa: E402
import proto_sectcost as SC  # noqa: E402
import srcchain_aug as S  # noqa: E402


assert S.DUMP and str(Path(S.DUMP).resolve()).startswith(str(HERE)), S.DUMP
tag = sys.argv[1]
nets = [int(x) for x in sys.argv[2:]]
S.RF["on"], S.RF["power"] = True, 1
g = SC.load_g()
kappa = np.load(RB / "kappa_table.npz")["kappa"]
for mid in nets:
    if mid >= 9000:
        ws = R.make_mlp(mid)
        ref = np.load(RES / f"r1_data/ref_{mid}.npy")
    else:
        raise SystemExit("MC nets only")
    S._DUMP.clear()
    t0 = time.time()
    est = S.src_closure(
        ws,
        g,
        kappa,
        rank=4,
        aged=[("own", int(os.environ.get("AGE", "5")), 384), (8, 224)],
        mc_seed=mid,
    )
    fm = float(np.mean((est[-1] - ref[-1]) ** 2))
    np.savez(
        S.DUMP.replace(".npz", f"_{mid}.npz"),
        **{f"d{r['l']}": r["d"] for r in S._DUMP},
        **{f"k4z{r['l']}": r["k4z"] for r in S._DUMP},
        **{f"B{r['l']}": r["B"] for r in S._DUMP},
    )
    row = dict(
        net=mid,
        tag=tag,
        final=fm,
        secs=time.time() - t0,
        env={
            k: os.environ.get(k)
            for k in ("AUG", "FREE", "METRIC", "LAMBDA", "QCOEF", "AGE", "PRUNE", "DUMP")
        },
    )
    print(json.dumps(row), flush=True)
    with open(HERE / "dump155.jsonl", "a") as f:
        f.write(json.dumps(row) + "\n")
