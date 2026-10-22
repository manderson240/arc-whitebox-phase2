#!/usr/bin/env bash
# G-RB155 dump pass with a SCRUBBED env (no AGE/PRUNE/NESTED/GSCALE/SECT/L0/MEM/EXTRA): dump.sh <avg|exact> <tag> nets...
M=$1; tag=$2; shift 2
cd ~/cohezion-labs/arc-whitebox/research/rebuild
ulimit -v 12000000
env -i HOME="$HOME" PATH=/usr/bin:/bin PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=4 OPENBLAS_NUM_THREADS=4 \
  AUG=ssc FREE=1 QCOEF=qcoefF2.npz LAMBDA=lambda_dumpF.npz METRIC="$M" \
  DUMP=~/cohezion-labs/arc-whitebox/research/rb155/dumps/dump_$tag.npz \
  nice -n 19 ~/cohezion-labs/arc-whitebox/whest-starterkit/.venv/bin/python ../rb155/dump155.py "$tag" "$@" \
  > ../rb155/dump_$tag.log 2>&1
echo "rc=$?" >> ../rb155/dump_$tag.log
