#!/usr/bin/env bash
# G-RB153 meter: rb142/meter.py under flopscope 0.12.3 (research/remote/venv). usage: meter.sh <out> <build> ...
cd ~/cohezion-labs/arc-whitebox
export PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=4 OPENBLAS_NUM_THREADS=4
ulimit -v 14000000
out=$1; shift
nice -n 19 research/remote/venv/bin/python research/rb142/meter.py "$@" > "$out" 2>&1
