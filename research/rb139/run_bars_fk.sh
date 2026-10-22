#!/usr/bin/env bash
# G-RB139 (Amendment 1) v110 = submissions/v110_fk: f64 identity vs v105, remote_check, then a FRESH wall re-measure vs v105 (round-robin, rep 2 reversed)
cd "$(dirname "$0")/../.."
PY=whest-starterkit/.venv/bin/python
export OMP_NUM_THREADS=8
(ulimit -v 24000000; nice -n 19 $PY research/rb122/cmp64.py submissions/v110_fk b139fk 0 2)
$PY - <<'PY'
import numpy as np
for n in (0,2):
    a=np.load(f"research/rb122/out64_b134ref_{n:05d}.npy"); b=np.load(f"research/rb122/out64_b139fk_{n:05d}.npy")
    print("BAR1 net",n,"final-layer max|dev|/max|ref| =",np.abs(a[-1]-b[-1]).max()/np.abs(a[-1]).max(), " all-layer =",np.abs(a-b).max()/np.abs(a).max())
PY
python3 research/rebuild/remote_check.py submissions/v110_fk --nets 2
research/rb139/run_wall.sh research/rb139/wall2.jsonl submissions/v105_sw submissions/v110_fk
