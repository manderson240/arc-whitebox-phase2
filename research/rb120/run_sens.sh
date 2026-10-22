#!/usr/bin/env bash
cd ~/cohezion-labs/arc-whitebox/research/rb120
ulimit -v 16000000
OMP=2 NW=6 nice -n 19 ~/cohezion-labs/arc-whitebox/whest-starterkit/.venv/bin/python drive120.py arms_sens.json fit12 results_fit12_sens.jsonl > sens.out 2>&1
