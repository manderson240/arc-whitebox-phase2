#!/usr/bin/env bash
# G-RB155 twin chunk (compute-only -> shared timing lock via bg.sh): run.sh <arms.json> <fit12|valid20|nets:a,b> <out.jsonl>
cd ~/cohezion-labs/arc-whitebox/research
export PYTHONDONTWRITEBYTECODE=1 NW=${NW:-4} OMP=${OMP:-2}
ulimit -v 12000000
nice -n 19 ~/cohezion-labs/arc-whitebox/whest-starterkit/.venv/bin/python rb155/drive155.py "$1" "$2" "$3" > "$3.log" 2>&1
