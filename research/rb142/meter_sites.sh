#!/usr/bin/env bash
cd ~/cohezion-labs/arc-whitebox
export PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=8 OPENBLAS_NUM_THREADS=8
ulimit -v 14000000
nice -n 19 whest-starterkit/.venv/bin/python research/rb142/meter_sites.py submissions/v110_fk research/rb142/v143_stub > research/rb142/meter_sites.out 2>&1
