"""Audit helper: plain K=2 chain of k2_mix_screen.py on one net, per-layer MSE vs all_layer_means.
usage: k2_perlayer.py <net_id>"""
import sys, json
import numpy as np
sys.path.insert(0, __import__("os").path.dirname(__file__))
from k2_mix_screen import chain, D
nid = int(sys.argv[1])
W = np.load(D / f"w_{nid:05d}.npy").astype(np.float64); T = np.load(D / f"truth_{nid:05d}.npz")
n = W.shape[1]
rows = np.sqrt((W[0] ** 2).sum(1) / (2 * np.pi)); cols = np.sqrt((W[0] ** 2).sum(0) / (2 * np.pi))
t0 = T["all_layer_means"][0]
if np.abs(cols - t0).mean() < np.abs(rows - t0).mean():
    W = np.transpose(W, (0, 2, 1))
est = chain(W, np.zeros(n), W[0] @ W[0].T)
pl = [float(np.mean((est[i] - T["all_layer_means"][i]) ** 2)) for i in range(est.shape[0])]
print(json.dumps(dict(net=nid, K2_final=float(np.mean((est[-1] - T["final_means"]) ** 2)), per_layer=pl)), flush=True)
