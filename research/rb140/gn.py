"""G-RB140 controller: joint Gauss-Newton fit of 6 chain constants on FIT60 pooled final MSE (see R2_GO_NOGO.md G-RB140 + EXECUTION NOTE 1).
Light (numpy only); every sweep is a separate lock hold via rebuild/timing_lock.sh rb140/run_arm.sh. Resumable (drive skips finished rows)."""
import json, math, os, subprocess, sys
from pathlib import Path
import numpy as np
HERE = Path(__file__).resolve().parent; R = HERE.parent
SHIPPED = {"ks": 0.7, "k31s": 0.72, "k31sD": 0.8, "q22sD": 0.96, "al07": 1.0, "hsD": 0.9}
KEYS = list(SHIPPED)
ENV = dict(os.environ, TIMING_LOCK_SHARED_RE=r"rb130/(cap|eval)\.sh|rb131/s131|rb132/|rb140/")
STEP, BOX, MAXIT = 0.02, 0.10, 3
log = lambda *a: print(*a, flush=True)
def spec_of(th): return {k: round(float(th[k]), 10) for k in KEYS}
def sweep(th, tag, netset="fit60"):
    out = HERE / "res" / f"{tag}.jsonl"; arms = HERE / "res" / f"arms_{tag}.json"
    json.dump({tag: spec_of(th)}, open(arms, "w"))
    subprocess.run([str(R / "rebuild" / "timing_lock.sh"), "rb140/run_arm.sh", str(arms), netset, str(out)], cwd=R, env=ENV, check=True)
    d = {}
    for ln in open(out):
        r = json.loads(ln); d[r["net"]] = r["final"]
    return d
def pooled(d, nets): return sum(d[n] for n in nets)
def main():
    S = json.load(open(R / "lc" / "split.json")); nets = sorted(S["FIT"])
    th = dict(SHIPPED); lam = 0.01
    base = sweep(th, "base_it0")
    assert sorted(base) == nets, (len(base),)
    ctl = {json.loads(l)["net"]: json.loads(l)["final"] for l in open(R / "rb130" / "res_fit12_SHIPPED.jsonl")}
    dmax = max(abs(base[n] / ctl[n] - 1) for n in ctl)
    log("CONTROL FIT12 shipped vs rb130 res_fit12_SHIPPED: max|rel diff|", dmax, "n", len(ctl))
    assert dmax == 0.0, "control failed"
    hist = [dict(it=0, theta=dict(th), pooled=pooled(base, nets))]
    for it in range(MAXIT):
        l0 = np.log(np.array([base[n] for n in nets]))
        G = np.zeros((len(nets), len(KEYS)))
        for j, k in enumerate(KEYS):
            ds = {}
            for sgn, nm in ((+1, "p"), (-1, "m")):
                t2 = dict(th); t2[k] = th[k] * (1 + sgn * STEP)
                ds[nm] = sweep(t2, f"it{it}_{k}_{nm}")
            lp = np.log(np.array([ds["p"][n] for n in nets])); lm = np.log(np.array([ds["m"][n] for n in nets]))
            G[:, j] = (lp - lm) / (math.log(1 + STEP) - math.log(1 - STEP))
        np.save(HERE / "res" / f"G_it{it}.npy", G)
        w = np.exp(l0 - l0.max()); w /= w.sum()
        g = (w[:, None] * G).sum(0); Gc = G - g
        H = (Gc * w[:, None]).T @ Gc
        log(f"it{it} base pooled {pooled(base, nets):.6e}  grad(per dlogtheta) {np.round(g, 4)}  diagH {np.round(np.diag(H), 5)}")
        accepted = False
        for tries in range(4):
            A = H + lam * np.diag(np.diag(H)) + 1e-6 * np.eye(len(KEYS))
            delta = np.clip(-np.linalg.solve(A, g), -BOX, BOX)
            pred = math.log(np.exp(l0 + G @ delta).sum()) - math.log(np.exp(l0).sum())
            t2 = {k: th[k] * math.exp(delta[j]) for j, k in enumerate(KEYS)}
            ver = sweep(t2, f"it{it}_verify{tries}")
            act = math.log(pooled(ver, nets)) - math.log(pooled(base, nets))
            log(f"it{it} try{tries} lam {lam:g} delta {np.round(delta, 4)} predicted dlogJ {pred:.5f} actual {act:.5f} theta {spec_of(t2)}")
            if act < 0:
                th, base, accepted = t2, ver, True; lam = max(lam / 3, 1e-3); break
            lam *= 10
        hist.append(dict(it=it + 1, theta=spec_of(th), pooled=pooled(base, nets), accepted=accepted))
        json.dump(hist, open(HERE / "history.json", "w"), indent=1)
        if not accepted: log("no accepted step; stopping"); break
    json.dump(dict(theta=spec_of(th), fit60_pooled=pooled(base, nets), shipped_fit60_pooled=hist[0]["pooled"]), open(HERE / "final.json", "w"), indent=1)
    log("FINAL", spec_of(th), "FIT60 pooled ratio vs shipped", pooled(base, nets) / hist[0]["pooled"])
main()
