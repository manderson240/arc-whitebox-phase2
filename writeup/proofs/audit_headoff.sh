cd ~/cohezion-labs/arc-whitebox
export PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=8 OPENBLAS_NUM_THREADS=8
ulimit -v 14000000
nice -n 19 research/remote/venv/bin/python writeup/proofs/meter_full.py writeup/proofs/v117_kd_headoff 1340 > writeup/proofs/meter_full_1340_headoff.out 2>&1
