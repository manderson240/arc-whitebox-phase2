#!/usr/bin/env bash
cd ~/cohezion-labs/arc-whitebox
export PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=8 OPENBLAS_NUM_THREADS=8
ulimit -v 14000000
nice -n 19 whest-starterkit/.venv/bin/python research/rebuild/fingerprint.py submissions/v112_sb > research/rb142/port_fp.out 2>&1
