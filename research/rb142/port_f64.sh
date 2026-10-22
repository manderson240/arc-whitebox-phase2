#!/usr/bin/env bash
cd ~/cohezion-labs/arc-whitebox/research
export PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=8 OPENBLAS_NUM_THREADS=8 F64=1
ulimit -v 20000000
nice -n 19 ../whest-starterkit/.venv/bin/python rebuild/lever46/cmp.py ../submissions/v112_sb v112f64 0 2 > rb142/port_f64.out 2>&1
