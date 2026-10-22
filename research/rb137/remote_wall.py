"""G-RB137 step 2: time predict() end-to-end in REMOTE mode (flopscope-client 0.12.3 over ZMQ to a fresh flopscope-server
0.12.3 process, the grader's execution mode), reusing research/rebuild/remote_check.py's server/estimator plumbing.

    python3 research/rb137/remote_wall.py submissions/<build> <tag> [nets=0,2]

One fresh server per invocation. Timed span = e.predict() only (setup, server start and the tolist() fetch excluded).
Prints one JSON line per net: wall_s (time.perf_counter around predict), the context's wall/backend/overhead/residual and
per-op_name {calls, backend_s, overhead_s}; plus a setup line. Last line: REMOTE_WALL <json summary>."""

import json
import os
import sys
import tempfile
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "research" / "rebuild"))
import remote_check as rc  # noqa: E402

B = 2**41


def load():
    return open("/proc/loadavg").read().split()[:3]


def main():
    build, tag = sys.argv[1].rstrip("/"), sys.argv[2]
    nets = [int(x) for x in (sys.argv[3] if len(sys.argv) > 3 else "0,2").split(",")]
    if Path(sys.executable).resolve() != rc.CPY.resolve() and os.environ.get("REMOTE_WALL_REEXEC") != "1":
        os.environ["REMOTE_WALL_REEXEC"] = "1"
        os.execv(str(rc.CPY), [str(rc.CPY), str(Path(__file__).resolve())] + sys.argv[1:])
    import warnings

    import flopscope as flops
    import flopscope.numpy as fnp
    import numpy as np
    from whestbench import SetupContext
    from whestbench.domain import MLP

    workdir = tempfile.mkdtemp(prefix="rwall_", dir=os.environ.get("TMPDIR"))
    p, url, _peak, logp = rc.start_server(workdir)
    if p.poll() is not None or not os.path.exists(url[len("ipc://"):]):
        print("REMOTE_WALL HARNESS " + json.dumps(dict(build=build, why="server did not start", log=open(logp).read()[-800:])))
        sys.exit(3)
    os.environ["FLOPSCOPE_SERVER_URL"] = url
    out_rows = []
    try:
        d, m = rc.load_estimator(build)
        t0 = time.perf_counter()
        e = m.Estimator()
        with flops.BudgetContext(flop_budget=int(1e15), quiet=True):
            e.setup(SetupContext(width=1024, depth=16, flop_budget=B, api_version="1", submission_dir=str(d)))
        print(json.dumps(dict(build=build, tag=tag, setup_s=round(time.perf_counter() - t0, 3))), flush=True)
        for k in nets:
            ws = np.load(rc.DATA / f"w_{k:05d}.npy")
            with flops.BudgetContext(flop_budget=int(1e15), quiet=True):
                mlp = MLP(width=1024, depth=16, weights=[fnp.array(np.asarray(w), dtype=fnp.float32) for w in ws], seed=k)
            la = load()
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                t0 = time.perf_counter()
                with flops.BudgetContext(flop_budget=B, quiet=True) as bc:
                    out = e.predict(mlp, B)
                wall = time.perf_counter() - t0
            util = 100 * bc.flops_used / B
            try:
                sd = bc.summary_dict()
                ops = {name: dict(calls=v["calls"], backend_s=round(v["flopscope_backend_time_s"], 4),
                                  overhead_s=round(v["flopscope_overhead_time_s"], 4))
                       for name, v in sd.get("operations", {}).items()}
            except Exception as ex:  # attribution is secondary; the wall is the instrument
                ops = {"_error": str(ex)}
            with flops.BudgetContext(flop_budget=int(1e15), quiet=True):
                arr = np.asarray(out.tolist(), dtype=np.float64)
            row = dict(build=build, tag=tag, net=k, wall_s=round(wall, 3), ctx_wall_s=bc.wall_time_s,
                       backend_s=bc.flopscope_backend_time_s, overhead_s=bc.flopscope_overhead_time_s,
                       residual_s=bc.residual_wall_time_s, util=round(util, 6), digest=rc.digest(arr),
                       load_before=la, load_after=load(), ops=ops)
            out_rows.append(row)
            print(json.dumps(row), flush=True)
    finally:
        p.terminate()
        try:
            p.wait(5)
        except Exception:
            p.kill()
    print("REMOTE_WALL " + json.dumps(dict(build=build, tag=tag, total_wall_s=round(sum(r["wall_s"] for r in out_rows), 3),
                                           nets=nets)), flush=True)


if __name__ == "__main__":
    main()
