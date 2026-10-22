#!/usr/bin/env bash
cd ~/cohezion-labs/arc-whitebox/research/rb120
ulimit -v 16000000
PY=~/cohezion-labs/arc-whitebox/whest-starterkit/.venv/bin/python
export OMP=2 NW=6
for a in ctl refit60 refit48 frozen; do nice -n 19 $PY drive120.py arms_$a.json fit12 results_fit12_$a.jsonl; done
V=$($PY -c "import json;print(','.join(map(str,json.load(open('../lc/split.json'))['VALID'])))")
for a in ctl frozen refit60; do nice -n 19 $PY drive120.py arms_$a.json nets:$V results_valid_$a.jsonl; done
