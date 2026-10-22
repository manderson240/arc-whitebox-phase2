#!/usr/bin/env bash
# G-RB155 MEXR pipeline (one shared-lock job): control (a) -> avg dump + refit (control b) -> exact dump + refit (arm).
R=~/cohezion-labs/arc-whitebox/research/rb155
B=~/cohezion-labs/arc-whitebox/research/rebuild
PY=~/cohezion-labs/arc-whitebox/whest-starterkit/.venv/bin/python
echo "start $(date -u +%T)"
"$R/fitlam.sh" "$B/aug_dumpF2.npz" "$R/lam_ctla_q1.npz" 1 "$R/ctla_q1.log"
$PY "$R/cmplam.py" "$R/lam_ctla_q1.npz" "$B/lambda_F2.npz" > "$R/cmp_ctla_q1.txt"
tail -1 "$R/cmp_ctla_q1.txt"
Q=1
if ! grep -q PASS "$R/cmp_ctla_q1.txt"; then
  "$R/fitlam.sh" "$B/aug_dumpF2.npz" "$R/lam_ctla_q0.npz" 0 "$R/ctla_q0.log"
  $PY "$R/cmplam.py" "$R/lam_ctla_q0.npz" "$B/lambda_F2.npz" > "$R/cmp_ctla_q0.txt"
  tail -1 "$R/cmp_ctla_q0.txt"; Q=0
fi
echo "stage a done $(date -u +%T) NOQLAST=$Q"
bash "$R/dump.sh" avg avg 9000 9001
"$R/fitlam.sh" "$R/dumps/dump_avg.npz" "$R/lambda_LAMD.npz" $Q "$R/fit_avg.log"
$PY "$R/cmplam.py" "$R/lambda_LAMD.npz" "$B/lambda_F2.npz" > "$R/cmp_ctlb.txt"
tail -1 "$R/cmp_ctlb.txt"
echo "stage b done $(date -u +%T)"
bash "$R/dump.sh" exact exact 9000 9001
"$R/fitlam.sh" "$R/dumps/dump_exact.npz" "$R/lambda_MEXR.npz" $Q "$R/fit_exact.log"
echo "stage c done $(date -u +%T)"
