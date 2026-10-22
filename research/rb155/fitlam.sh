#!/usr/bin/env bash
# G-RB155: run rebuild/fit_lambda_sect.py (unchanged) on a dump prefix -> out npz. usage: fitlam.sh <dump_prefix.npz> <out.npz> <NOQLAST 0|1> <log> [ALPHAS]
cd ~/cohezion-labs/arc-whitebox/research/rebuild
ulimit -v 14000000
env -i HOME="$HOME" PATH=/usr/bin:/bin PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=4 OPENBLAS_NUM_THREADS=4 SEEDS=9000,9001 NOQLAST="$3" \
  ALPHAS="${5:-1e-4,1e-3,1e-2,1e-1,1}" \
  nice -n 19 ~/cohezion-labs/arc-whitebox/whest-starterkit/.venv/bin/python fit_lambda_sect.py "$1" "$2" > "$4" 2>&1
echo "rc=$?" >> "$4"
