#!/usr/bin/env bash
# G-RB144 twin chunk (compute-only -> shared timing lock): run144.sh <arms.json> <full:a-b|...> <out.jsonl>
cd ~/cohezion-labs/arc-whitebox/research
export PYTHONDONTWRITEBYTECODE=1 NW=${NW:-8} OMP=${OMP:-2}
ulimit -v 12000000
nice -n 19 ~/cohezion-labs/arc-whitebox/whest-starterkit/.venv/bin/python rb142/drive144.py "$1" "$2" "$3" > "$3.log" 2>&1
