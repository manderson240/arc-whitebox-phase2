#!/usr/bin/env bash
# G-RB139: calibrated remote wall (research/rb137/remote_wall.py), 2 repeats, round-robin, order reversed on repeat 2, nets 0,2.
# usage: run_wall.sh <out.jsonl> <build...>
cd "$(dirname "$0")/../.."
export OMP_NUM_THREADS=8
OUT=$1; shift
FWD=("$@"); REV=(); for ((i=${#FWD[@]}-1; i>=0; i--)); do REV+=("${FWD[$i]}"); done
for rep in 1 2; do
  if [ $rep = 1 ]; then L=("${FWD[@]}"); else L=("${REV[@]}"); fi
  for b in "${L[@]}"; do
    echo "=== $(date -u +%T) rep $rep $b load $(cut -d' ' -f1-3 /proc/loadavg)"
    python3 research/rb137/remote_wall.py "$b" "r$rep" 0,2 | tee -a "$OUT"
  done
done
echo "=== done $(date -u +%T)"
