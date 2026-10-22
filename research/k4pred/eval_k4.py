"""G-RB73 rung 2: e2e arms on the v59_p05 f64 twin (free-SSC + PRUNE 0.05), with or without the shipped head.
usage: eval_k4.py <arm> <source> <head: none|full> <mid> ...   -> eval_k4.jsonl
  source: ctrl | oracle_A | oracle_B | oracle_AB (MC kappa4 injected, layers 1..15) | model_<tag>.npz (predictor) | mutant_<tag>.npz (SSC + (SSC - pred))
  env LMIN (first injected layer, default 1), LMAX (default 15), MODEL=ridge|mlp (default mlp)."""

import json
import os
import sys
import time

import k4lib as L
import numpy as np


L.set_twin_env()
import k3chain as K  # noqa: E402
import lctrain as T  # noqa: E402
import proto_sectcost as SC  # noqa: E402
import srcchain_k4p as S  # noqa: E402


S.RF["on"], S.RF["power"] = True, 1
AGED = [("own", 6, 384), (8, 224)]
g = SC.load_g() * 0.92
kappa = np.load(L.RB / "kappa_table.npz")["kappa"]
arm, source, headv = sys.argv[1:4]
LMIN, LMAX = int(os.environ.get("LMIN", "1")), int(os.environ.get("LMAX", "15"))
MODEL = os.environ.get("MODEL", "mlp")
head = (
    T.load_any(str(L.HERE.parent / "lc" / "cache" / os.environ.get("HEAD", "corr_sscf_MIX2.npz")), sign=1.2 * float(os.environ.get("HEADSIGN", "1")), Lmax=15)
    if headv == "full"
    else None
)
model = None
if source.startswith("model_") or source.startswith("mutant_"):
    model = True
    predict = L.make_predictor(source.replace("mutant_", "model_"), MODEL)


for m in sys.argv[4:]:
    mid = int(m)
    assert mid not in L.SPLIT["TEST"], "TEST nets are never touched here"
    mc = L.load_mc(mid) if source.startswith("oracle") else None
    swaps = []

    def hook(l, ctx):
        if l < LMIN or l > LMAX or source == "ctrl":
            return ctx["k4z"]
        if source == "oracle_A":
            k = mc["k4_A"][l]
        elif source == "oracle_B":
            k = mc["k4_B"][l]
        elif source == "oracle_AB":
            k = 0.5 * (mc["k4_A"][l] + mc["k4_B"][l])
        elif source.startswith(
            "oracle_lam"
        ):  # SSC + lam * (true - SSC): the e2e response along the true deviation
            lam = float(source[len("oracle_lam") :])
            k = ctx["k4z"] + lam * (0.5 * (mc["k4_A"][l] + mc["k4_B"][l]) - ctx["k4z"])
        elif source.startswith(
            "oracle_noise"
        ):  # true + Gaussian noise of s x the within-layer sd of (true - SSC): random-pattern control
            s_ = float(source[len("oracle_noise") :])
            kt = 0.5 * (mc["k4_A"][l] + mc["k4_B"][l])
            rng_ = np.random.default_rng(100 + l)
            k = kt + s_ * np.std(kt - ctx["k4z"]) * rng_.standard_normal(L.N)
        elif source.startswith(
            "oracle_mean"
        ):  # SSC rescaled to the true per-layer mean only (layer-mean oracle, no scatter)
            kt = 0.5 * (mc["k4_A"][l] + mc["k4_B"][l])
            k = ctx["k4z"] * (kt.mean() / ctx["k4z"].mean())
        elif source.startswith(
            "oracle_mcN"
        ):  # emulated MC estimate of kappa4 from N samples: true + N(0, sqrt(24/N) var^2)
            nsamp = float(source[len("oracle_mcN") :])
            kt = 0.5 * (mc["k4_A"][l] + mc["k4_B"][l])
            rng_ = np.random.default_rng(200 + l)
            k = kt + np.sqrt(24.0 / nsamp) * np.maximum(
                ctx["var_z"], 1e-12
            ) ** 2 * rng_.standard_normal(L.N)
        else:
            k = predict(l, ctx)
            if source.startswith("mutant_"):
                k = 2.0 * ctx["k4z"] - k
            sh = float(os.environ.get("SHRINK", "1"))
            if sh != 1.0:
                k = ctx["k4z"] + sh * (k - ctx["k4z"])
        swaps.append(
            float(
                np.sqrt(np.mean((k - ctx["k4z"]) ** 2))
                / max(np.sqrt(np.mean(ctx["k4z"] ** 2)), 1e-300)
            )
        )
        return k

    S.K4HOOK = hook
    ws, truth = K.load_net(mid)
    t0 = time.time()
    est = S.src_closure(
        ws, g, kappa, rank=4, aged=AGED, lc_hook=head.hook if head is not None else None
    )
    row = dict(
        arm=arm,
        source=source,
        head=headv,
        model=MODEL if model is not None else None,
        head_file=os.environ.get("HEAD", "corr_sscf_MIX2.npz"),
        head_sign=float(os.environ.get("HEADSIGN", "1")),
        lmin=LMIN,
        lmax=LMAX,
        net=mid,
        final=float(np.mean((est[-1] - truth[-1]) ** 2)),
        layer_mse=[float(np.mean((est[i] - truth[i]) ** 2)) for i in range(16)],
        swap_rel=[round(s, 3) for s in swaps],
        secs=round(time.time() - t0, 1),
        utc=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    )
    print(json.dumps({k: v for k, v in row.items() if k not in ("layer_mse",)}), flush=True)
    with open(L.HERE / "eval_k4.jsonl", "a") as f:
        f.write(json.dumps(row) + "\n")
