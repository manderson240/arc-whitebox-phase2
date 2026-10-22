cd ~/cohezion-labs/arc-whitebox
for v in v118_fk46 v118_d6fk1; do echo "=== $v"; python3 research/rebuild/remote_check.py submissions/$v --nets 1 2>&1 | tail -1 | cut -c1-700; done
export PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=8 OPENBLAS_NUM_THREADS=8
nice -n 19 research/remote/venv/bin/python research/rb142/meter.py submissions/v112_sb submissions/v118_fk46 submissions/v118_d6fk1 2>&1 | cut -c1-260
