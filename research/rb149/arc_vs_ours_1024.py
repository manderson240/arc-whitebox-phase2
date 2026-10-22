"""rb149 (1)/(2): ARC reference kprop (research/rb149/ref, MIT) vs our srcchain_aug on the SAME synthetic net (seed 9000, make_mlp: He N(0,2/n), 16 ReLU layers, n=1024)
against the 1e7-sample MC reference r1_data/ref_9000.npy.  Both with NO fitted kappa4 (g=kappa=0) so the baselines are comparable.
usage: arc_vs_ours_1024.py arc_simple|arc_aug|arc_k2  [net=9000] [dtype=f32] [L=16]
       AUG=off|arc python arc_vs_ours_1024.py ours   (no-kappa4 ours;  AUG env read by srcchain_aug)"""
import sys, os, time, types, json
from pathlib import Path
import numpy as np
HERE = Path(__file__).resolve().parent; RB = HERE.parent / "rebuild"; RES = HERE.parent
mode = sys.argv[1]; net = int(sys.argv[2]) if len(sys.argv) > 2 else 9000; dt = sys.argv[3] if len(sys.argv) > 3 else "f32"; L = int(sys.argv[4]) if len(sys.argv) > 4 else 16
ref = np.load(RES / "r1_data" / f"ref_{net}.npy")
if mode.startswith("arc"):
    jt = types.ModuleType("jaxtyping"); jt.Float = type("Float", (), {"__class_getitem__": classmethod(lambda c, k: object)}); sys.modules.setdefault("jaxtyping", jt)
    sys.path.insert(0, str(HERE / "ref" / "src")); sys.path.insert(0, str(RES))
    import torch; torch.set_grad_enabled(False); torch.set_num_threads(8)
    import proto_r2 as R
    from mlp_kprop.mlp import MLP
    from mlp_kprop.kprop_harmonic import mlp_kprop, SIMPLE, AUGMENT
    ws = R.make_mlp(net); n = ws[0].shape[0]; T = torch.float32 if dt == "f32" else torch.float64
    mlp = MLP(input_dim=n, hidden_dim=n, output_dim=n, num_layers=L + 1).to(T)
    for l in range(L): mlp.Ws[l].weight.copy_(torch.from_numpy(ws[l].astype(np.float64)).T.to(T)); 
    mlp.Ws[L].weight.zero_()
    K_in = {1: torch.zeros(n, dtype=T), 2: torch.eye(n, dtype=T)}
    kw = dict(arc_simple=dict(k_max=3, factor=True), arc_aug=dict(k_max=3, kind=AUGMENT, factor=True), arc_k2=dict(k_max=2))[mode]
    t0 = time.time(); out = mlp_kprop(mlp, K_in, output_all=True, up_to_layer=f"act{L-1}", **kw)
    est = np.stack([out[f"act{l}"][1].to_tensor().double().numpy() for l in range(L)])
    secs = time.time() - t0
else:
    sys.path.insert(0, str(HERE)); sys.path.insert(0, str(RB)); sys.path.insert(0, str(RES))
    import srcchain_aug_fix as S, proto_r2 as R, proto_sectcost as SC
    S.RF["on"], S.RF["power"] = True, 1
    gs = float(os.environ.get("GS", "0")); g = SC.load_g() * gs; kappa = np.load(RB / "kappa_table.npz")["kappa"] * gs
    ws = R.make_mlp(net); t0 = time.time()
    est = S.src_closure(ws, g, kappa, rank=4, aged=[("own", 5, 384), (8, 224)], mc_seed=net); secs = time.time() - t0
mse = ((est - ref) ** 2).mean(1)
np.save(HERE / f"est_{mode}{os.environ.get('AUG','')}{os.environ.get('GS','')}_{net}.npy", est)
print(json.dumps(dict(mode=mode, aug=os.environ.get("AUG"), net=net, secs=secs, final=mse[-1], layers=[float(f"{m:.3e}") for m in mse])))
