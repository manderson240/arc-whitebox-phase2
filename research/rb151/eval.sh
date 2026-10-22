#!/usr/bin/env bash
# G-RB151 eval, same session: arms A2 (shipped head) vs A2h (head refit on the A2 chain), VALID-20 then HELD-OUT-40 (full:300-340)
cd ~/cohezion-labs/arc-whitebox/research
export PYTHONDONTWRITEBYTECODE=1 NW=${NW:-8} OMP=2
ulimit -v 12000000
PY=~/cohezion-labs/arc-whitebox/whest-starterkit/.venv/bin/python
nice -n 19 $PY rb142/drive144.py rb151/arms_151.json valid20 rb151/res_151_valid20.jsonl > rb151/res_151_valid20.jsonl.log 2>&1
nice -n 19 $PY rb142/drive144.py rb151/arms_151.json full:300-340 rb151/res_151_heldout.jsonl > rb151/res_151_heldout.jsonl.log 2>&1
