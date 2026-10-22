#!/usr/bin/env bash
# G-RB119 batch: control, chain capture, head-ON halves, dose, head-OFF halves. nice 19, ulimit -v per CLAUDE.md.
cd ~/cohezion-labs/arc-whitebox/research/rb119
export OMP=2 NW=8 OMP_NUM_THREADS=2
PY=~/cohezion-labs/arc-whitebox/whest-starterkit/.venv/bin/python
ulimit -v 12000000
NW=1 nice -n 19 $PY drive117.py arms_ctrl.json nets:0 results_ctrl.jsonl
for n in 0 2 4 5 6 7; do nice -n 19 $PY cap119.py $n; done
nice -n 19 $PY drive117.py arms_half_on.json nets:0,2,4,5,6,7 results_half_on.jsonl
nice -n 19 $PY drive117.py arms_dose.json nets:0,2,4,5,6,7 results_dose.jsonl
nice -n 19 $PY drive117.py arms_half_off.json nets:0,2,4,5,6,7 results_half_off.jsonl
