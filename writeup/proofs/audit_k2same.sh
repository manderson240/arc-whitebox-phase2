cd ~/cohezion-labs/arc-whitebox
export PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=8 OPENBLAS_NUM_THREADS=8
ulimit -v 14000000
nice -n 19 research/remote/venv/bin/python writeup/proofs/meter_full.py submissions/v117_kd 1340 > writeup/proofs/meter_full_1340.out 2>&1
nice -n 19 research/remote/venv/bin/python writeup/proofs/k2_perlayer.py 1340 > writeup/proofs/k2_perlayer_1340.out 2>&1
