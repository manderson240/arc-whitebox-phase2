#!/usr/bin/env bash
cd ~/cohezion-labs/arc-whitebox/research/rb120
ulimit -v 16000000
OMP=2 NW=1 /usr/bin/time -v nice -n 19 ~/cohezion-labs/arc-whitebox/whest-starterkit/.venv/bin/python drive120.py arms_tf.json nets:0 results_tfprobe.jsonl 2> probe.time
