#!/usr/bin/env bash
# usage: fit.sh <tag>   (rb130/fit.sh settings: OMP 8)
cd ~/cohezion-labs/arc-whitebox/research/rb151
export PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=8 OPENBLAS_NUM_THREADS=8 MKL_NUM_THREADS=8
ulimit -v 24000000
nice -n 19 ~/cohezion-labs/arc-whitebox/whest-starterkit/.venv/bin/python fit151.py $1 > fit_$1.out 2>&1
