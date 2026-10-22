#!/usr/bin/env bash
# usage: run_arm.sh <arms.json> <netset> <out.jsonl>   (one lock hold = one sweep)
cd ~/cohezion-labs/arc-whitebox/research
export PYTHONDONTWRITEBYTECODE=1 NW=${NW:-10} OMP=${OMP:-2}
ulimit -v 12000000
nice -n 19 ~/cohezion-labs/arc-whitebox/whest-starterkit/.venv/bin/python rb130/drive130.py "$1" "$2" "$3" > "$3.log" 2>&1
