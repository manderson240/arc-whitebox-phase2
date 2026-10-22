#!/usr/bin/env bash
# G-RB155 control (b) + arm (c) refit with the control-(a)-validated alpha grid 1e-3,1e-2,1e-1,1 (NOQLAST=1).
R=~/cohezion-labs/arc-whitebox/research/rb155
B=~/cohezion-labs/arc-whitebox/research/rebuild
PY=~/cohezion-labs/arc-whitebox/whest-starterkit/.venv/bin/python
"$R/fitlam.sh" "$R/dumps/dump_avg.npz" "$R/lambda_LAMD.npz" 1 "$R/fit_avg2.log" 1e-3,1e-2,1e-1,1
echo "ctl-b $($PY "$R/cmplam.py" "$R/lambda_LAMD.npz" "$B/lambda_F2.npz" | tail -1)"
"$R/fitlam.sh" "$R/dumps/dump_exact.npz" "$R/lambda_MEXR.npz" 1 "$R/fit_exact2.log" 1e-3,1e-2,1e-1,1
echo "MEXR vs F2 (difference expected): $($PY "$R/cmplam.py" "$R/lambda_MEXR.npz" "$B/lambda_F2.npz" | tail -1)"
