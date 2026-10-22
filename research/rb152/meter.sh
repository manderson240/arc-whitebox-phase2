#!/usr/bin/env bash
# G-RB152 step 0 meter: rb142/meter.py (G-RB143 step-3 instrument) under flopscope 0.12.3 (research/remote/venv). usage: meter.sh <out> <build> ...
cd ~/cohezion-labs/arc-whitebox
export PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=8 OPENBLAS_NUM_THREADS=8
ulimit -v 14000000
out=$1; shift
nice -n 19 research/remote/venv/bin/python research/rb142/meter.py "$@" > "$out" 2>&1
