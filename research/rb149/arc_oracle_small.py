"""rb149 (1): ARC reference kprop (MIT, research/rb149/ref) on small random He-init ReLU MLPs, f64, vs big-sample MC truth.
Compares per-layer activation-mean error of K=2, K=3 (simple/augment, factored/unfactored).  Synthetic nets only (seeds 7000+; no TEST/FIT nets).
usage: python arc_oracle_small.py n L [seeds...]"""
import sys, time, types
import numpy as np
jt = types.ModuleType("jaxtyping"); jt.Float = type("Float", (), {"__class_getitem__": classmethod(lambda c, k: object)})
sys.modules.setdefault("jaxtyping", jt)
sys.path.insert(0, "ref/src")
import torch
torch.set_grad_enabled(False); torch.set_num_threads(4)
from mlp_kprop.mlp import MLP
from mlp_kprop.kprop_harmonic import mlp_kprop, SIMPLE, AUGMENT, BASE
n, L = int(sys.argv[1]), int(sys.argv[2]); seeds = [int(s) for s in sys.argv[3:]] or [7000]
def mc(mlp, N=4_000_000, chunk=100_000):
    g = torch.Generator().manual_seed(1); acc = None; cnt = 0
    for _ in range(N // chunk):
        x = torch.randn(chunk, n, generator=g, dtype=torch.float64); hs = []
        for i, W in enumerate(mlp.Ws):
            x = W(x)
            if i < len(mlp.Ws) - 1: x = torch.relu(x)
            hs.append(x.mean(0))
        v = torch.stack(hs); acc = v if acc is None else acc + v; cnt += 1
    return (acc / cnt).numpy()
cfgs = [("K1", dict(k_max=1)), ("K2", dict(k_max=2)), ("K3 simple unfact", dict(k_max=3)), ("K3 simple fact", dict(k_max=3, factor=True)),
        ("K3 aug unfact", dict(k_max=3, kind=AUGMENT)), ("K3 aug fact", dict(k_max=3, kind=AUGMENT, factor=True))]
for seed in seeds:
    torch.manual_seed(seed)
    mlp = MLP(input_dim=n, hidden_dim=n, output_dim=n, num_layers=L).double()
    truth = mc(mlp)  # (L, n) layer means incl. final linear layer
    se = 1.0 / np.sqrt(4_000_000) # MC noise floor on a unit-variance quantity
    print(f"seed {seed} n={n} L={L}  MC sem ~ {se:.1e} (relative to O(1) activations); truth final-layer rms {np.sqrt((truth[-1]**2).mean()):.3f}")
    K_in = {1: torch.zeros(n, dtype=torch.float64), 2: torch.eye(n, dtype=torch.float64)}
    for name, kw in cfgs:
        t0 = time.time()
        try:
            out = mlp_kprop(mlp, K_in, output_all=True, **kw)
        except Exception as e:
            print(f"  {name:18s} FAILED {type(e).__name__}: {str(e)[:100]}"); continue
        keys = [k for k in out.keys()]
        pre = np.stack([out[f"act{l}" if l < L - 1 else f"pre{l}"][1].to_tensor().numpy() for l in range(L)])
        mse = ((pre - truth) ** 2).mean(1)
        print(f"  {name:18s} {time.time()-t0:6.1f}s per-layer MSE vs MC:", " ".join(f"{m:.1e}" for m in mse))
