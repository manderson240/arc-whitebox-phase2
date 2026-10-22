"""G-RB153 STEP 0: is any state-predictable part of the chain's sigma^2 error left at z-layers 11-15?
Inputs: rb153/cap/cap_a2_<net>.npz (A2 chain mu_z, var_z, k3 at the injection point, uncorrected) and k4pred/mc_<net>.npz (var_A/B).
Energy (registered): E = sum over layers 11-15, neurons, nets of the cross-half debiased (v - v_A)(v - v_B).
Share = 1 - E1/E0, leave-one-net-out (fit on 5, score the 6th, pooled). Fit target r = v_mc/v_c - 1 (v_mc = (A+B)/2).
VS1 per-layer mean r; VS2 per-layer x 3 a-bins mean r; VS3 per-layer ridge of r on vcal153.feats. Sign rule (VS1/VS2): a
layer/bin is kept only if per-net fitted signs agree on >= 5/6 nets (>= 4/5 inside a LONO fold). Writes the full-6 models."""

import json
import sys
from pathlib import Path

import numpy as np


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import vcal153 as V  # noqa: E402


NETS = [0, 2, 4, 5, 6, 7]
LAYERS = [11, 12, 13, 14, 15]
D = {}
for n in NETS:
    c = np.load(HERE / "cap" / f"cap_a2_{n:05d}.npz")
    m = np.load(HERE.parent / "k4pred" / f"mc_{n:05d}.npz")
    for l in LAYERS:
        D[n, l] = dict(
            mu=c[f"mu_z_{l}"],
            v=c[f"var_z_{l}"],
            k3=c[f"k3_{l}"],
            vA=m["var_A"][l],
            vB=m["var_B"][l],
        )


def bins(d):
    a = d["mu"] / np.sqrt(d["v"])
    return np.where(a < -1, 0, np.where(a > 1, 2, 1))


def r_of(d):
    return 0.5 * (d["vA"] + d["vB"]) / d["v"] - 1.0


def fit(form, nets, need):
    P = {}
    for l in LAYERS:
        if form == "scalar":
            per = [float(np.mean(r_of(D[n, l]))) for n in nets]
            allr = np.concatenate([r_of(D[n, l]) for n in nets])
            agree = max(sum(p > 0 for p in per), sum(p < 0 for p in per))
            P[l] = float(allr.mean()) if agree >= need else 0.0
        elif form == "bin":
            ps = []
            for b in range(3):
                per, allr = [], []
                for n in nets:
                    msk = bins(D[n, l]) == b
                    rr = r_of(D[n, l])[msk]
                    if rr.size:
                        per.append(float(rr.mean()))
                        allr.append(rr)
                allr = np.concatenate(allr) if allr else np.zeros(0)
                agree = max(sum(p > 0 for p in per), sum(p < 0 for p in per))
                ps.append(float(allr.mean()) if (allr.size and agree >= need) else 0.0)
            P[l] = ps
        elif form == "ridge":
            X = np.concatenate([V.feats(D[n, l]["mu"], D[n, l]["v"], D[n, l]["k3"]) for n in nets])
            y = np.concatenate([r_of(D[n, l]) for n in nets])
            m, s = X.mean(0), X.std(0) + 1e-12
            Z = np.c_[np.ones(len(y)), (X - m) / s]
            lam = 1e-3 * len(y) * np.eye(Z.shape[1])
            lam[0, 0] = 0.0
            w = np.linalg.solve(Z.T @ Z + lam, Z.T @ y)
            P[l] = dict(w=w.tolist(), m=m.tolist(), s=s.tolist())
    return P


def energy(P, form, nets):
    e0 = e1 = 0.0
    for n in nets:
        for l in LAYERS:
            d = D[n, l]
            y = (
                np.zeros_like(d["v"])
                if P is None
                else V.predict(form, P[l], d["mu"], d["v"], d["k3"])
            )
            v1 = d["v"] * (1 + y)
            e0 += float(np.sum((d["v"] - d["vA"]) * (d["v"] - d["vB"])))
            e1 += float(np.sum((v1 - d["vA"]) * (v1 - d["vB"])))
    return e0, e1


out = {}
for l in LAYERS:  # descriptive: per-layer bias and per-net spread (information)
    per = [float(np.mean(r_of(D[n, l]))) for n in NETS]
    nz = [
        float(np.mean((D[n, l]["vA"] - D[n, l]["vB"]) ** 2) / 4 / np.mean(D[n, l]["v"] ** 2))
        for n in NETS
    ]
    tot = [
        float(
            np.mean((D[n, l]["v"] - D[n, l]["vA"]) * (D[n, l]["v"] - D[n, l]["vB"]))
            / np.mean(D[n, l]["v"] ** 2)
        )
        for n in NETS
    ]
    print(
        f"l={l} mean r per net {' '.join(f'{p:+.2e}' for p in per)} | debiased rel err^2 {np.mean(tot):.2e} | noise rel^2 {np.mean(nz):.2e}"
    )
for form in ("scalar", "bin", "ridge"):
    E0 = E1 = 0.0
    for k in NETS:
        tr = [n for n in NETS if n != k]
        P = fit(form, tr, 4)
        e0, e1 = energy(P, form, [k])
        E0 += e0
        E1 += e1
    share = 1 - E1 / E0
    Pfull = fit(form, NETS, 5)
    e0f, e1f = energy(Pfull, form, NETS)
    out[form] = dict(lono_share=share, insample_share=1 - e1f / e0f, E0=E0)
    json.dump(
        dict(form=form, layers={str(l): v for l, v in Pfull.items()}),
        open(HERE / f"model_{form}.json", "w"),
        indent=1,
    )
    print(
        f"{form:6s} LONO share {share:+.4f}  in-sample {1 - e1f / e0f:+.4f}  -> {'PROCEED' if share >= 0.03 else 'KILL'} (bar 0.03)"
    )
    if form != "ridge":
        print(
            "   full-6 params:",
            {
                l: (round(v, 6) if isinstance(v, float) else [round(x, 6) for x in v])
                for l, v in Pfull.items()
            },
        )
json.dump(out, open(HERE / "step0.json", "w"), indent=1)
