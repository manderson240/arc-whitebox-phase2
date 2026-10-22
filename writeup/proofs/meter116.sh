cd ~/cohezion-labs/arc-whitebox
export PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=8 OPENBLAS_NUM_THREADS=8
ulimit -v 14000000
nice -n 19 research/remote/venv/bin/python research/rb142/meter.py submissions/v112_sb submissions/v116_a5 submissions/v116_o7 submissions/v116_a7 submissions/v116_r448 > writeup/proofs/meter116.out 2>&1
