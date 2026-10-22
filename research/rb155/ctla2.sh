#!/usr/bin/env bash
# G-RB155 control (a) retry: alpha grid without 1e-4 (l=2 matched exactly at alpha 1e-3; every 1e-4 layer differed).
R=~/cohezion-labs/arc-whitebox/research/rb155
B=~/cohezion-labs/arc-whitebox/research/rebuild
PY=~/cohezion-labs/arc-whitebox/whest-starterkit/.venv/bin/python
for q in 1 0; do
  "$R/fitlam.sh" "$B/aug_dumpF2.npz" "$R/lam_ctla2_q$q.npz" $q "$R/ctla2_q$q.log" 1e-3,1e-2,1e-1,1
  echo "q$q $($PY "$R/cmplam.py" "$R/lam_ctla2_q$q.npz" "$B/lambda_F2.npz" | tail -1)"
done
