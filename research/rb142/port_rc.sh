#!/usr/bin/env bash
cd ~/cohezion-labs/arc-whitebox
export PYTHONDONTWRITEBYTECODE=1
python3 research/rebuild/remote_check.py submissions/v112_sb > research/rb142/port_rc.out 2>&1
