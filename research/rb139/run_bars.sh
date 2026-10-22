#!/usr/bin/env bash
# G-RB139 v110_s bars: f64 identity vs v105 (nets 0,2; v105 ref = rb122/out64_b134ref_*, made by G-RB134 from submissions/v105_sw), util, remote_check
cd "$(dirname "$0")/../.."
PY=whest-starterkit/.venv/bin/python
export OMP_NUM_THREADS=8
(ulimit -v 24000000; nice -n 19 $PY research/rb122/cmp64.py submissions/v110_s b139s 0 2)
$PY - <<'PY'
import numpy as np
for n in (0,2):
    a=np.load(f"research/rb122/out64_b134ref_{n:05d}.npy"); b=np.load(f"research/rb122/out64_b139s_{n:05d}.npy")
    print("BAR1 net",n,"final-layer max|dev|/max|ref| =",np.abs(a[-1]-b[-1]).max()/np.abs(a[-1]).max(), " all-layer =",np.abs(a-b).max()/np.abs(a).max())
PY
$PY research/rebuild/fingerprint.py submissions/v105_sw submissions/v110_s
python3 research/rebuild/remote_check.py submissions/v110_s --nets 2
