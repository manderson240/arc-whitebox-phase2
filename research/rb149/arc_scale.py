"""rb149: does ARC's AUGMENT help over SIMPLE at depth 16 as n grows?  synthetic He nets (torch seed 7100+n), MC truth N=1e7 (f32 matmul, f64 accumulation).
Improvement = MSE_simple - MSE_aug is unbiased w.r.t. MC noise (noise adds the same floor to both).  usage: arc_scale.py n L [N]"""
import sys, time, types, json
import numpy as np
jt = types.ModuleType("jaxtyping"); jt.Float = type("Float", (), {"__class_getitem__": classmethod(lambda c, k: object)}); sys.modules.setdefault("jaxtyping", jt)
sys.path.insert(0, "ref/src")
import torch; torch.set_grad_enabled(False); torch.set_num_threads(8)
from mlp_kprop.mlp import MLP
from mlp_kprop.kprop_harmonic import mlp_kprop, AUGMENT
n, L = int(sys.argv[1]), int(sys.argv[2]); N = int(float(sys.argv[3])) if len(sys.argv) > 3 else 10_000_000
torch.manual_seed(7100 + n)
mlp = MLP(input_dim=n, hidden_dim=n, output_dim=n, num_layers=L + 1).float(); mlp.Ws[L].weight.zero_()
g = torch.Generator().manual_seed(5); acc = torch.zeros(L, n, dtype=torch.float64); chunk = 200_000; t0 = time.time()
for _ in range(N // chunk):
    x = torch.randn(chunk, n, generator=g)
    for l in range(L):
        x = torch.relu(mlp.Ws[l](x)); acc[l] += x.sum(0, dtype=torch.float64)
truth = (acc / N).numpy(); print("mc secs", round(time.time() - t0), flush=True)
K_in = {1: torch.zeros(n), 2: torch.eye(n)}
res = {}
for name, kw in [("K2", dict(k_max=2)), ("simple", dict(k_max=3, factor=True)), ("aug", dict(k_max=3, kind=AUGMENT, factor=True))]:
    t0 = time.time(); out = mlp_kprop(mlp, K_in, output_all=True, up_to_layer=f"act{L-1}", **kw)
    est = np.stack([out[f"act{l}"][1].to_tensor().double().numpy() for l in range(L)])
    mse = ((est - truth) ** 2).mean(1); res[name] = mse
    print(name, f"{time.time()-t0:.0f}s final {mse[-1]:.3e} mean-over-layers {mse.mean():.3e}", [float(f"{m:.2e}") for m in mse], flush=True)
print("simple/aug final ratio", res["simple"][-1] / res["aug"][-1], " mean-layers ratio", res["simple"].mean() / res["aug"].mean())
