#!/usr/bin/env bash
# G-RB137 step 2: 2 repeats x (v99r, v105, v106, v102), repeat 2 reversed; nets 0,2; one fresh server per process.
cd "$(dirname "$0")/../.."
export OMP_NUM_THREADS=8
OUT=research/rb137/wall.jsonl
BUILDS1="submissions/v99r_rm submissions/v105_sw submissions/v106_1x submissions/v102_sz"
BUILDS2="submissions/v102_sz submissions/v106_1x submissions/v105_sw submissions/v99r_rm"
for rep in 1 2; do
  eval "L=\$BUILDS$rep"
  for b in $L; do
    echo "=== $(date -u +%T) rep $rep $b load $(cut -d' ' -f1-3 /proc/loadavg)"
    python3 research/rb137/remote_wall.py "$b" "r$rep" 0,2 | tee -a "$OUT"
  done
done
echo "=== done $(date -u +%T)"
