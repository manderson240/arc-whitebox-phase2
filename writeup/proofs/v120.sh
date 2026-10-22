cd ~/cohezion-labs/arc-whitebox
python3 research/rebuild/remote_check.py submissions/v120_kdl --nets 1 2>&1 | tail -1 | cut -c1-400
export PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=8 OPENBLAS_NUM_THREADS=8
nice -n 19 research/remote/venv/bin/python writeup/proofs/meter3.py submissions/v112_sb submissions/v117_kd submissions/v120_kdl
