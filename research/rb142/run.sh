#!/usr/bin/env bash
# G-RB142 twin chunk (compute-only -> shared timing lock): run.sh <arms.json> <fit12|valid20|nets:a,b> <out.jsonl>
cd ~/cohezion-labs/arc-whitebox/research
export PYTHONDONTWRITEBYTECODE=1 NW=${NW:-6} OMP=${OMP:-4}
ulimit -v 12000000
nice -n 19 ~/cohezion-labs/arc-whitebox/whest-starterkit/.venv/bin/python rb142/drive117.py "$1" "$2" "$3" > "$3.log" 2>&1
