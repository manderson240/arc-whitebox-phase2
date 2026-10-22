"""torch FlopCounterMode FLOPs of ARC SIMPLE factored K=3 (L=16) at small n, fitted to c*n^p to extrapolate to n=1024 (counter at n=1024 OOMs under the ulimit)."""
import sys, types, math
import numpy as np
jt = types.ModuleType("jaxtyping"); jt.Float = type("Float", (), {"__class_getitem__": classmethod(lambda c, k: object)}); sys.modules.setdefault("jaxtyping", jt)
sys.path.insert(0, "ref/src")
import torch; torch.set_grad_enabled(False)
from torch.utils.flop_counter import FlopCounterMode
from mlp_kprop.mlp import MLP
from mlp_kprop.kprop_harmonic import mlp_kprop
res = {}
for n in (64, 128, 192):
    torch.manual_seed(1); mlp = MLP(input_dim=n, hidden_dim=n, output_dim=n, num_layers=17).float()
    with FlopCounterMode(display=False) as fc:
        mlp_kprop(mlp, {1: torch.zeros(n), 2: torch.eye(n)}, k_max=3, factor=True, up_to_layer="act15")
    res[n] = fc.get_total_flops(); print(n, res[n], res[n] / n**3, "flops/n^3 (=2*MAC units)")
ns = np.array(list(res)); fl = np.array(list(res.values()), float)
p, lc = np.polyfit(np.log(ns), np.log(fl), 1); print("fit exponent", p)
print("extrapolated n=1024 (power-law):", math.exp(lc) * 1024 ** p / 1024**3 / 2, "n^3 MAC units")
print("per-n^3 at largest n scaled (exponent 3):", fl[-1] / ns[-1] ** 3 / 2, "n^3 MAC units;  paper Table 1: 30 L^2 + 39 L =", 30 * 256 + 39 * 16)
