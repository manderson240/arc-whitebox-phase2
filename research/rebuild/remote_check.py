"""REMOTE-mode gate: run a build's predict the way the AIcrowd grader does (flopscope-client 0.12.3, every op dispatched
over ZMQ to a separate flopscope-server 0.12.3 process) and compare it with the in-process local run.

    remote_check.py submissions/<build> [--nets N] [--no-local]

Why: v99_rm / v100_xs / v101_xp passed every local rung and FAILED on AIcrowd (ESTIMATOR_EXCEPTION, all 100 MLPs):
`RemoteArray.transpose(*axes)` sends `list(axes)`, so numpy's one-tuple spelling `.transpose(perm)` reaches the server
as [[...]] -> TypeError. The local ladder never left local flopscope. (G-RB123, 2026-10-18)

PASS requires, on each of the first N FIT nets (0, 2, 4): no exception, a finite (16, 1024) result that is a genuine
remote handle, and (unless --no-local) the SAME output digest (fingerprint.py's formula) and the same metered util as
the in-process local run. Exit 0 = PASS, 1 = FAIL (the build), 3 = HARNESS (could not run; callers must treat it as
HOLD, never as pass). Last stdout line: `REMOTE_CHECK <PASS|FAIL|HARNESS> <json>`.

Harness facts (research/remote/): venv = flopscope[server]==0.12.3 + whestbench==0.16.2 (server side);
cvenv = flopscope-client==0.12.3 + whestbench 0.16.2 --no-deps + its import deps (client side, the grader's client).
The server's FLOPSCOPE_MAX_ARRAY_BYTES default is 100 MiB, which v98_fd (graded fine) exceeds (860,518,400-byte arena),
so the grader runs with a larger, unknown limit; we raise it to 8 GiB and report each build's peak result array next to
v98's (research/remote/peak_ref.json) -- a peak above v98's is NOT proven safe and is flagged PEAK>V98.
The output digest is BLAS-thread-count sensitive (OMP_NUM_THREADS 8 vs 4 flips v99_rm's net-0 digest): the server and
the local reference MUST inherit the same environment as each other -- never give one of them its own thread setting.
"""

import json
import os
import subprocess
import sys
import tempfile
import time
import traceback
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
RDIR = ROOT / "research" / "remote"
CPY = RDIR / "cvenv" / "bin" / "python"
SPY = Path(
    os.environ.get("REMOTE_CHECK_SERVER_PY", RDIR / "venv" / "bin" / "python")
)  # override: slot_runner self-test only
DATA = ROOT / "research" / "lc" / "data"
PEAK_REF = RDIR / "peak_ref.json"
FIT = [0, 2, 4]
B = 2**41
UTIL_TOL = 0.005  # percentage points. Measured on v98_fd FIT 0/2: remote bills exactly 2**24 FLOPs (0.000763 pp) more
# than in-process local, on both nets, flopscope 0.12.1 and 0.12.3 local alike; outputs bit-identical. Anything beyond
# 0.005 pp means the remote path billed a different op stream.


def emit(verdict, **kw):
    print(f"REMOTE_CHECK {verdict} {json.dumps(kw, default=str)}", flush=True)
    sys.exit({"PASS": 0, "FAIL": 1}.get(verdict, 3))


def digest(arr):
    import hashlib

    import numpy as np

    a = np.asarray(arr, dtype=np.float64)
    return hashlib.sha256(np.round(a / (np.abs(a).max() + 1e-300), 9).tobytes()).hexdigest()[:16]


def load_estimator(build):
    import importlib.util

    d = (ROOT / build).resolve()
    spec = importlib.util.spec_from_file_location(f"rc_{d.name}", d / "estimator.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return d, m


# ---------------------------------------------------------------- local reference (in-process flopscope 0.12.3, venv) --
def local_ref(build, nets, outdir):
    import warnings

    import flopscope as flops
    import flopscope.numpy as fnp
    import numpy as np
    from whestbench import SetupContext
    from whestbench.domain import MLP

    d, m = load_estimator(build)
    e = m.Estimator()
    e.setup(
        SetupContext(width=1024, depth=16, flop_budget=B, api_version="1", submission_dir=str(d))
    )
    for k in nets:
        ws = np.load(DATA / f"w_{k:05d}.npy")
        mlp = MLP(
            width=1024,
            depth=16,
            weights=[fnp.array(np.asarray(w), dtype=fnp.float32) for w in ws],
            seed=k,
        )
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            with flops.BudgetContext(flop_budget=B, quiet=True) as bc:
                out = e.predict(mlp, B)
        arr = np.asarray(out, dtype=np.float64)
        np.save(Path(outdir) / f"local_{k}.npy", arr)
        print(
            json.dumps(
                dict(net=k, digest=digest(arr), util=100 * bc.flops_used / B, ops=len(bc.op_log))
            ),
            flush=True,
        )


# ---------------------------------------------------------------- remote run (client venv) -------------------------
def start_server(workdir):
    sock = os.path.join(workdir, "fs.sock")
    url = f"ipc://{sock}"
    peak = os.path.join(workdir, "peak")
    log = open(os.path.join(workdir, "server.log"), "w")
    env = dict(
        os.environ,
        FLOPSCOPE_MAX_ARRAY_BYTES=os.environ.get("FLOPSCOPE_MAX_ARRAY_BYTES", str(8 << 30)),
    )
    p = subprocess.Popen(
        [str(SPY), str(RDIR / "server_wrap.py"), peak, "--url", url, "--timeout", "900"],
        stdout=log,
        stderr=subprocess.STDOUT,
        env=env,
    )
    for _ in range(150):
        if os.path.exists(sock) or p.poll() is not None:
            break
        time.sleep(0.1)
    return p, url, peak, os.path.join(workdir, "server.log")


def remote_run(build, nets, workdir):
    """Returns (rows, exc_row_or_None). Raises only on harness problems."""
    import flopscope as flops
    import flopscope.numpy as fnp
    import numpy as np
    from flopscope import _remote_array
    from whestbench import SetupContext
    from whestbench.domain import MLP

    remote_type = getattr(_remote_array, "RemoteArray", None)
    if remote_type is None:
        raise RuntimeError("flopscope._remote_array.RemoteArray missing: not the 0.12.x client")
    d, m = load_estimator(build)
    rows = []
    try:
        e = m.Estimator()
        with flops.BudgetContext(flop_budget=int(1e15), quiet=True):
            e.setup(
                SetupContext(
                    width=1024, depth=16, flop_budget=B, api_version="1", submission_dir=str(d)
                )
            )
    except Exception as ex:
        return rows, dict(
            net=None,
            stage="setup",
            exc=f"{type(ex).__name__}: {ex}",
            tb=traceback.format_exc()[-2500:],
        )
    for k in nets:
        ws = np.load(DATA / f"w_{k:05d}.npy")
        with flops.BudgetContext(flop_budget=int(1e15), quiet=True):
            mlp = MLP(
                width=1024,
                depth=16,
                weights=[fnp.array(np.asarray(w), dtype=fnp.float32) for w in ws],
                seed=k,
            )
        t0 = time.time()
        try:
            with flops.BudgetContext(flop_budget=B, quiet=True) as bc:
                out = e.predict(mlp, B)
            util = 100 * bc.flops_used / B  # read before any fetch so the fetch cannot bill
            is_remote = isinstance(out, remote_type)
            with flops.BudgetContext(flop_budget=int(1e15), quiet=True):
                arr = np.asarray(out.tolist(), dtype=np.float64)
        except Exception as ex:
            return rows, dict(
                net=k,
                stage="predict",
                exc=f"{type(ex).__name__}: {ex}",
                tb=traceback.format_exc()[-2500:],
            )
        np.save(Path(workdir) / f"remote_{k}.npy", arr)
        rows.append(
            dict(
                net=k,
                remote_handle=is_remote,
                shape=list(arr.shape),
                finite=bool(np.isfinite(arr).all()),
                digest=digest(arr),
                util=util,
                sec=round(time.time() - t0, 1),
            )
        )
    return rows, None


def main():
    args = sys.argv[1:]
    if (
        args and args[0] == "--local-ref"
    ):  # internal: python remote_check.py --local-ref <build> <outdir> <net...>
        local_ref(args[1], [int(x) for x in args[3:]], args[2])
        return
    if not args or args[0].startswith("-"):
        print(__doc__)
        sys.exit(2)
    build = args[0].rstrip("/")
    n = int(args[args.index("--nets") + 1]) if "--nets" in args else 2
    want_local = "--no-local" not in args
    nets = FIT[: max(1, min(n, len(FIT)))]
    for py in (CPY, SPY):
        if not py.exists():
            emit("HARNESS", build=build, why=f"missing interpreter {py}")
    # 2026-10-21: compare the venv PREFIX, not the resolved executable. Every venv's bin/python is a symlink to the
    # same base interpreter, so .resolve() made the starter-kit venv look like cvenv and the re-exec never happened
    # (HARNESS ImportError _remote_array when launched from whest-starterkit/.venv).
    if (
        Path(sys.prefix).resolve() != (RDIR / "cvenv").resolve()
        and os.environ.get("REMOTE_CHECK_REEXEC") != "1"
    ):
        os.environ["REMOTE_CHECK_REEXEC"] = "1"
        os.execv(str(CPY), [str(CPY), str(Path(__file__).resolve())] + args)
    if not (ROOT / build / "estimator.py").exists():
        emit("HARNESS", build=build, why="no estimator.py")
    workdir = tempfile.mkdtemp(prefix="rcheck_", dir=os.environ.get("TMPDIR"))
    p, url, peakf, logp = start_server(workdir)
    if p.poll() is not None or not os.path.exists(url[len("ipc://") :]):
        emit(
            "HARNESS",
            build=build,
            why="flopscope-server did not start",
            log=open(logp).read()[-1500:],
        )
    os.environ["FLOPSCOPE_SERVER_URL"] = url
    try:
        try:
            rows, bad = remote_run(build, nets, workdir)
        except Exception as ex:
            emit(
                "HARNESS",
                build=build,
                why=f"{type(ex).__name__}: {ex}",
                tb=traceback.format_exc()[-1500:],
            )
    finally:
        p.terminate()
        try:
            p.wait(5)
        except Exception:
            p.kill()
    slog = open(logp).read()
    peak = int(open(peakf).read()) if os.path.exists(peakf) else None
    if bad is not None:
        harnessy = (
            "MemoryError" in bad["exc"] or "MemoryError" in slog or "Connection" in bad["exc"]
        )
        emit("HARNESS" if harnessy else "FAIL", build=build, **bad, peak_bytes=peak)
    for r in rows:
        if not (r["remote_handle"] and r["finite"] and r["shape"] == [16, 1024]):
            emit("FAIL", build=build, why="bad remote output", row=r, peak_bytes=peak)
    cmp = []
    if want_local:
        cp = subprocess.run(
            [str(SPY), str(Path(__file__).resolve()), "--local-ref", build, workdir]
            + [str(k) for k in nets],
            capture_output=True,
            text=True,
            env={k: v for k, v in os.environ.items() if k != "FLOPSCOPE_SERVER_URL"},
            timeout=900,
        )
        loc = {}
        for line in cp.stdout.splitlines():
            if line.startswith("{"):
                j = json.loads(line)
                loc[j["net"]] = j
        if cp.returncode != 0 or set(loc) != set(nets):
            emit("HARNESS", build=build, why="local reference run failed", err=cp.stderr[-1500:])
        import numpy as np

        for r in rows:
            lr = loc[r["net"]]
            a = np.load(Path(workdir) / f"remote_{r['net']}.npy")
            b = np.load(Path(workdir) / f"local_{r['net']}.npy")
            rel = float(np.abs(a - b).max() / (np.abs(b).max() + 1e-300))
            ok = r["digest"] == lr["digest"] and abs(r["util"] - lr["util"]) <= UTIL_TOL
            cmp.append(
                dict(
                    net=r["net"],
                    digest_remote=r["digest"],
                    digest_local=lr["digest"],
                    util_remote=round(r["util"], 6),
                    util_local=round(lr["util"], 6),
                    ops_local=lr["ops"],
                    max_abs_rel=rel,
                    ok=ok,
                )
            )
        if not all(c["ok"] for c in cmp):
            emit(
                "FAIL",
                build=build,
                why="remote output/util differs from local",
                cmp=cmp,
                peak_bytes=peak,
            )
    ref = json.loads(PEAK_REF.read_text()) if PEAK_REF.exists() else {}
    flags = []
    if peak is not None and ref.get("v98_fd") and peak > ref["v98_fd"]:
        flags.append("PEAK>V98")
    emit(
        "PASS",
        build=build,
        nets=nets,
        rows=rows,
        cmp=cmp,
        peak_bytes=peak,
        peak_v98=ref.get("v98_fd"),
        flags=flags,
    )


if __name__ == "__main__":
    main()
