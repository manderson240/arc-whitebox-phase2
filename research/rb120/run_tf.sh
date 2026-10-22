#!/usr/bin/env bash
cd ~/cohezion-labs/arc-whitebox/research/rb120
ulimit -v 16000000
OMP=2 NW=5 nice -n 19 ~/cohezion-labs/arc-whitebox/whest-starterkit/.venv/bin/python drive120.py arms_tf.json tf80 results_tf.jsonl > tf.out 2>&1
