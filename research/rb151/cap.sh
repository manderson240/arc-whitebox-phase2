#!/usr/bin/env bash
# usage: ARM=A0|A2|A2r cap.sh <mid> ... ; teacher-forced capture (lc_src151 = lc_src130 driver + rb142 s117 chain, free-SSC env), NW parallel, resumable
cd ~/cohezion-labs/arc-whitebox/research/rb151
export PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=${OMP:-2} OPENBLAS_NUM_THREADS=${OMP:-2} MKL_NUM_THREADS=${OMP:-2}
export SSC=1 AUG=ssc FREE=1 QCOEF=~/cohezion-labs/arc-whitebox/research/rebuild/qcoefF2.npz LAMBDA=~/cohezion-labs/arc-whitebox/research/rebuild/lambda_F2.npz AGE=6 RANK=4 NESTED=1 GSCALE=0.92 LCSCALE=1.2
export ARM=${ARM:-A0} CHAIN=${CHAIN:-$(echo ${ARM:-A0} | tr A-Z a-z)}
ulimit -v 16000000
PY=~/cohezion-labs/arc-whitebox/whest-starterkit/.venv/bin/python
printf '%s\n' "$@" | xargs -P ${NW:-6} -I{} nice -n 19 $PY lc_src151.py tf {}
