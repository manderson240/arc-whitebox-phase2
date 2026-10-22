#!/usr/bin/env bash
# G-RB152 twin: run.sh <arms.json> <netset> <out.jsonl> (rb142 twin via drive144, NW 8 x OMP 2 as G-RB143/144)
cd ~/cohezion-labs/arc-whitebox/research
export PYTHONDONTWRITEBYTECODE=1 NW=${NW:-8} OMP=${OMP:-2}
ulimit -v 12000000
nice -n 19 ~/cohezion-labs/arc-whitebox/whest-starterkit/.venv/bin/python rb142/drive144.py "$1" "$2" "$3" > "$3.log" 2>&1
