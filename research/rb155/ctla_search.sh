#!/usr/bin/env bash
# G-RB155 control (a) diagnosis: which fit_lambda_sect.py arguments reproduce lambda_F2 from the existing aug_dumpF2 dumps?
R=~/cohezion-labs/arc-whitebox/research/rb155
B=~/cohezion-labs/arc-whitebox/research/rebuild
PY=~/cohezion-labs/arc-whitebox/whest-starterkit/.venv/bin/python
cd "$B"
ulimit -v 14000000
mkdir -p "$R/srch"
for blk in m,q,k q,k m,k m,q k q m; do
 for al in default 1e-4 1e-3 1e-2 1e-1 1; do
  for q in 0 1; do
   t="b${blk//,/}_a${al}_q$q"
   if [ "$al" = default ]; then A=1e-4,1e-3,1e-2,1e-1,1; else A=$al; fi
   env -i HOME="$HOME" PATH=/usr/bin:/bin PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=4 SEEDS=9000,9001 NOQLAST=$q ALPHAS=$A \
     nice -n 19 $PY fit_lambda_sect.py "$B/aug_dumpF2.npz" "$R/srch/$t.npz" "$blk" > "$R/srch/$t.log" 2>&1
   echo "$t $($PY "$R/cmplam.py" "$R/srch/$t.npz" "$B/lambda_F2.npz" | tail -1)"
  done
 done
done
