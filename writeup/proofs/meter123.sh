cd ~/cohezion-labs/arc-whitebox
export PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=8 OPENBLAS_NUM_THREADS=8
ulimit -v 14000000
for b in submissions/v117_kd submissions/v122_rk3 submissions/v123_dc100 submissions/v123_rk3lt submissions/v123_rk3kh2; do nice -n 19 research/remote/venv/bin/python writeup/proofs/meter3.py $b >> writeup/proofs/meter123.out 2>&1; done
