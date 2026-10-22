cd ~/cohezion-labs/arc-whitebox
export PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=8 OPENBLAS_NUM_THREADS=8
nice -n 19 research/remote/venv/bin/python research/rb149/eval_port_full.py submissions/v117_kd - 1300 1301 1302 1303 1304 1305 1306 1307
