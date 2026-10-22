#!/usr/bin/env bash
cd ~/cohezion-labs/arc-whitebox/research/rb119
export OMP=2 NW=8 OMP_NUM_THREADS=2
ulimit -v 12000000
nice -n 19 ~/cohezion-labs/arc-whitebox/whest-starterkit/.venv/bin/python drive117.py arms_L1115.json nets:0,2,4,5,6,7 results_L1115.jsonl
