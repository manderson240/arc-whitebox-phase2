#!/usr/bin/env bash
cd ~/cohezion-labs/arc-whitebox/research/rb140
exec 8>.gn.lock
flock -n 8 || { echo "gn already running" >> gn.dup.out; exit 0; }
exec ~/cohezion-labs/arc-whitebox/whest-starterkit/.venv/bin/python gn.py > gn.out 2>&1
