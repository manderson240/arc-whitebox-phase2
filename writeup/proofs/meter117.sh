cd ~/cohezion-labs/arc-whitebox
export PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=8 OPENBLAS_NUM_THREADS=8
ulimit -v 14000000
nice -n 19 research/remote/venv/bin/python writeup/proofs/meter3.py submissions/v112_sb submissions/v117_lc115 submissions/v117_lc125 submissions/v117_dc95 submissions/v117_pr03 submissions/v117_pr01 submissions/v117_kh3 > writeup/proofs/meter117.out 2>&1
