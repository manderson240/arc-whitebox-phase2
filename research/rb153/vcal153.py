"""G-RB153 sigma^2 calibration models. build(spec) -> f(l, mu_z, var_z, k3) -> yhat (n-vector), var_z <- var_z (1 + yhat).
spec = {"file": "rb153/<model>.json", "neg": 0|1, "perm": 0|1}. Model json: {"form": scalar|bin|ridge, "layers": {l: params}}.
  scalar: params = c                      yhat = c
  bin:    params = [c_lo, c_mid, c_hi]    bins of a = mu/sigma: a < -1, |a| <= 1, a > 1
  ridge:  params = {"w": [...], "m": [...], "s": [...]}  yhat = w0 + sum_k w_k (x_k - m_k)/s_k, x = feats(...)
perm: yhat permuted across neurons with a fixed seed (placebo, same values); neg: yhat negated (mutant)."""

import json
from pathlib import Path

import numpy as np
from math import erf, sqrt, pi

_erf = np.vectorize(erf)


def _pdf(a):
    return np.exp(-0.5 * a * a) / sqrt(2 * pi)


def _cdf(a):
    return 0.5 * (1.0 + _erf(a / sqrt(2.0)))


R2 = Path(__file__).resolve().parent.parent


def feats(mu_z, var_z, k3):
    sd = np.sqrt(var_z)
    a = mu_z / sd
    return np.stack(
        [a, a * a, _pdf(a), _cdf(a), k3 / sd**3, np.log(var_z / var_z.mean())], 1
    )


def predict(form, p, mu_z, var_z, k3):
    if form == "scalar":
        return np.full(mu_z.shape, float(p))
    a = mu_z / np.sqrt(var_z)
    if form == "bin":
        return np.where(a < -1, p[0], np.where(a > 1, p[2], p[1])).astype(float)
    if form == "ridge":
        X = (feats(mu_z, var_z, k3) - np.array(p["m"])) / np.array(p["s"])
        w = np.array(p["w"])
        return w[0] + X @ w[1:]
    raise ValueError(form)


def build(spec):
    mdl = json.load(open(R2 / spec["file"]))
    form, P = mdl["form"], {int(k): v for k, v in mdl["layers"].items()}
    neg, perm = bool(spec.get("neg")), bool(spec.get("perm"))

    def f(l, mu_z, var_z, k3):
        if l not in P:
            return np.zeros_like(var_z)
        y = predict(form, P[l], mu_z, var_z, k3)
        if spec.get("demean"):
            y = y - y.mean()
        if perm:
            y = y[np.random.default_rng(153000 + l).permutation(y.shape[0])]
        return -y if neg else y

    return f
