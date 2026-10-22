#!/usr/bin/env bash
# G-RB153 twin chunk (compute-only -> shared timing lock via bg.sh): run.sh <arms.json> <fit12|valid20|nets:a,b> <out.jsonl>
cd ~/cohezion-labs/arc-whitebox/research
export PYTHONDONTWRITEBYTECODE=1 NW=${NW:-4} OMP=${OMP:-2}
ulimit -v 12000000
nice -n 19 ~/cohezion-labs/arc-whitebox/whest-starterkit/.venv/bin/python rb153/drive153.py "$1" "$2" "$3" > "$3.log" 2>&1
