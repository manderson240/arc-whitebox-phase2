cd ~/cohezion-labs/arc-whitebox
export PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=8 OPENBLAS_NUM_THREADS=8
ulimit -v 14000000
nice -n 19 research/remote/venv/bin/python writeup/proofs/meter3.py submissions/v112_sb submissions/v119_lt09 submissions/v119_lt11 submissions/v119_rk4 submissions/v119_os16 > writeup/proofs/meter119.out 2>&1
