"""rb149 paired comparison: ARC SIMPLE factorized K=3 (research/rb149/ref, MIT) on official-format nets from research/lc/data (VALID split only).
usage: arc_valid.py mid...   -> arc_valid_<mid>.npy (16,1024 act means), arc_valid.jsonl (final mse vs 1e9 truth, torch FLOPs)"""
import sys, time, types, json
from pathlib import Path
import numpy as np
HERE = Path(__file__).resolve().parent; DATA = HERE.parent / "lc" / "data"
SPLIT = json.load(open(HERE.parent / "lc" / "split.json"))
jt = types.ModuleType("jaxtyping"); jt.Float = type("Float", (), {"__class_getitem__": classmethod(lambda c, k: object)}); sys.modules.setdefault("jaxtyping", jt)
sys.path.insert(0, str(HERE / "ref" / "src"))
import torch; torch.set_grad_enabled(False); torch.set_num_threads(8)
from torch.utils.flop_counter import FlopCounterMode
from mlp_kprop.mlp import MLP
from mlp_kprop.kprop_harmonic import mlp_kprop
L = 16
for mid in [int(x) for x in sys.argv[1:]]:
    assert mid in SPLIT["VALID"], "only VALID nets"
    ws = np.load(DATA / f"w_{mid:05d}.npy", mmap_mode="r"); truth = np.load(DATA / f"truth_{mid:05d}.npz")["all_layer_means"]
    n = ws.shape[1]; mlp = MLP(input_dim=n, hidden_dim=n, output_dim=n, num_layers=L + 1).float()
    for l in range(L): mlp.Ws[l].weight.copy_(torch.from_numpy(np.asarray(ws[l], dtype=np.float32)).T)
    mlp.Ws[L].weight.zero_()
    t0 = time.time()
    if True:
        out = mlp_kprop(mlp, {1: torch.zeros(n), 2: torch.eye(n)}, k_max=3, factor=True, output_all=True, up_to_layer=f"act{L-1}")
    est = np.stack([out[f"act{l}"][1].to_tensor().double().numpy() for l in range(L)])
    np.save(HERE / f"arc_valid_{mid:05d}.npy", est)
    row = dict(net=mid, secs=time.time() - t0, final_mse=float(((est[-1] - truth[-1]) ** 2).mean()), torch_flops=0,
               layer_mse=[float(((est[l] - truth[l]) ** 2).mean()) for l in range(L)])
    print(json.dumps({k: v for k, v in row.items() if k != "layer_mse"}), flush=True)
    with open(HERE / "arc_valid.jsonl", "a") as f: f.write(json.dumps(row) + "\n")
