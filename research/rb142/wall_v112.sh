#!/usr/bin/env bash
# G-RB144 port bar: calibrated remote wall, v112_sb vs v105_sw, 2 repeats x 2 builds (repeat 2 reversed), nets 0,2; one fresh server per process.
cd ~/cohezion-labs/arc-whitebox
export OMP_NUM_THREADS=8 PYTHONDONTWRITEBYTECODE=1
OUT=research/rb142/wall_v112.jsonl
for rep in 1 2; do
  if [ $rep -eq 1 ]; then L="submissions/v105_sw submissions/v112_sb"; else L="submissions/v112_sb submissions/v105_sw"; fi
  for b in $L; do
    echo "=== $(date -u +%T) rep $rep $b load $(cut -d' ' -f1-3 /proc/loadavg)"
    python3 research/rb137/remote_wall.py "$b" "r$rep" 0,2 | tee -a "$OUT"
  done
done
echo "=== done $(date -u +%T)"
