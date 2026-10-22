"""One command = the full ship rule (screen -> VALID-20 -> interleaved subprocess Mini-10 -> ship checks). Never submits.

usage: uv run python research/rebuild/ladder.py --base submissions/<base> --cand submissions/<cand>
           [--rungs screen,valid,mini10,ship] [--output-identical] [--head-ref MSE] [--also submissions/<x> ...]
           [--mini10-repeats N] [--wait-load-below L] [--wait-cap-s S] [--no-stop]

Reuses (does not reimplement): lever46/cmp.py (screen, VALID chunks, f64 identity / head check), mini10_ab.sh (official subprocess
Mini-10), eval_mem.py (net-0 VmPeak), `whest validate` / `whest package`. Bars live in BARS (one dict, each with its source gate).
Writes research/rebuild/ladder/<cand>_vs_<base>.json and appends one ISO-UTC line to PROGRESS.md. stdlib only.
"""

from __future__ import annotations

import argparse
import fcntl
import json
import os
import resource
import shutil
import signal
import subprocess
import sys
import tarfile
import tempfile
import time
from datetime import datetime, timezone

UTC = timezone.utc  # noqa: UP017  (venv is Python 3.10: datetime.UTC needs 3.11)
from pathlib import Path


HERE = Path(__file__).resolve().parent  # research/rebuild
ROOT = HERE.parent.parent  # arc-whitebox
PY = ROOT / "whest-starterkit/.venv/bin/python"
WHEST = ROOT / "whest-starterkit/.venv/bin/whest"
OUTDIR = HERE / "ladder"
FIT = [0, 2, 4]
VALID20 = [10, 11, 13, 16, 18, 20, 27, 28, 35, 41, 48, 55, 59, 61, 65, 81, 84, 85, 89, 91]
CHILD_AS_KB = 16_000_000  # ulimit -v 16000000 for every child
HEAD_NET = 10

# Every bar as data. "cmp": le = value must be <= limit; eq = must equal. "src" = the gate that set it.
BARS = {
    "screen_adj": dict(
        limit=0.985,
        cmp="le",
        rung="screen",
        src="G-RB35/G-RB43: FIT 0/2/4 in-process f32, adj = mean raw x mean util vs base",
    ),
    "valid_adj": dict(
        limit=0.98,
        cmp="le",
        rung="valid",
        src="G-RB43: fresh-process-chunk VALID-20 pooled adjusted vs base",
    ),
    "valid_worst_raw": dict(
        limit=1.10, cmp="le", rung="valid", src="G-RB43: worst per-net raw ratio on VALID-20"
    ),
    "mini10_complete": dict(
        limit=10,
        cmp="eq",
        rung="mini10",
        src="advisor/G-RB50: JSON must hold 10 per_mlp rows (mini10_ab.sh always logs exit 0)",
    ),
    "mini10_failed": dict(
        limit=0,
        cmp="le",
        rung="mini10",
        src="G-RB39: 0 failed in the subprocess runner (8 GB RLIMIT_AS worker)",
    ),
    "mini10_residual": dict(
        limit=0.345,
        cmp="le",
        rung="mini10",
        src="G-RB50/RESUME: worst per-net residual (grader cliff 0.400 s)",
    ),
    "mini10_adj": dict(
        limit=0.98, cmp="le", rung="mini10", src="ship rule: adjusted <= 0.98 x base, same session"
    ),
    "eval_mem": dict(
        limit=6500,
        cmp="le",
        rung="ship",
        src="G-RB39: eval_mem net-0 VmPeak MB (worker sees >= +1.1 GB more; 6921 failed)",
    ),
    "archive": dict(
        limit=True,
        cmp="eq",
        rung="ship",
        src="whest package -> tar holds estimator.py + every .npz -> whest validate OK",
    ),
    "f64_identity": dict(
        limit=1e-10,
        cmp="le",
        rung="ship",
        src="G-RB39/40: --output-identical: f64 net-0 max rel dev vs base (replaces 0.98x)",
    ),
    "mini10_adj_not_worse": dict(
        limit=1.0,
        cmp="le",
        rung="mini10",
        src="--output-identical: a ratchet must not be adjusted-worse than base",
    ),
    "mini10_worker_vmpeak": dict(limit=None, cmp="le", rung="mini10", src="G-RB51 (opt-in --worker-mem-max MiB): grader worker VmPeak, polled every 0.1 s, by identity"),
    "head_check": dict(
        limit=0.02,
        cmp="le",
        rung="ship",
        src="G-RB34b: f64 WITH head on net 10 within 2 % of prototype-with-head",
    ),
}
GUARDS = dict(min_free_gb=3.0, max_load_1m=16.0)


# ---------------------------------------------------------------- pure bar evaluator (unit-tested) --
def applicable_bars(rungs, output_identical: bool, head_check: bool):
    out = []
    for name, b in BARS.items():
        if b["rung"] not in rungs:
            continue
        if output_identical and name in (
            "screen_adj",
            "valid_adj",
            "valid_worst_raw",
            "mini10_adj",
        ):
            continue  # accuracy bars replaced by f64 identity
        if not output_identical and name in ("f64_identity", "mini10_adj_not_worse"):
            continue
        if name == "head_check" and not head_check:
            continue
        if b["limit"] is None:  # opt-in bar whose limit was not set for this run
            continue
        out.append(name)
    return out


def _check(name, value):
    b = BARS[name]
    if value is None:
        return "NOT_RUN"
    if b["cmp"] == "le":
        return "PASS" if value <= b["limit"] else "FAIL"
    return "PASS" if value == b["limit"] else "FAIL"


def evaluate_bars(results: dict, rungs, output_identical=False, head_check=False):
    """results: {bar_name: measured value or None}. Returns ({bar: {value, limit, verdict}}, overall).
    overall PASS only if EVERY applicable bar is PASS (NOT_RUN never passes)."""
    per = {}
    for name in applicable_bars(rungs, output_identical, head_check):
        v = results.get(name)
        per[name] = dict(
            value=v, limit=BARS[name]["limit"], verdict=_check(name, v), src=BARS[name]["src"]
        )
    overall = "PASS" if per and all(x["verdict"] == "PASS" for x in per.values()) else "FAIL"
    return per, overall


def summarize_mini10(doc) -> dict:
    """Parse a whest run JSON (or None / broken). Empty or truncated -> n_rows < 10 (fails mini10_complete)."""
    try:
        r = doc["results"]
        pm = r["per_mlp"]
    except (TypeError, KeyError):
        return dict(n_rows=0)
    res = [m["residual_wall_time_s"] for m in pm]
    flags = (
        "budget_exhausted",
        "time_exhausted",
        "residual_wall_time_exhausted",
        "combined_budget_exhausted",
    )
    fails = [m["mlp_index"] for m in pm if any(m.get(k) for k in flags) or m.get("traceback")]
    srt = sorted(res)
    return dict(
        n_rows=len(pm),
        adjusted=r["adjusted_final_layer_score"],
        raw=r["final_layer_mse"],
        util=r["mean_compute_utilization"],
        failed=int(r["n_failed_mlps"]),
        failed_idx=fails,
        res_min=srt[0] if srt else None,
        res_med=srt[len(srt) // 2] if srt else None,
        res_max=srt[-1] if srt else None,
        res_argmax=pm[res.index(srt[-1])]["mlp_index"] if srt else None,
        residuals=res,
        per_net_raw=[m["final_layer_mse"] for m in pm],
    )


def pooled_adj(rows):
    raw = sum(r["raw"] for r in rows) / len(rows)
    util = sum(r["util"] for r in rows) / len(rows)
    return raw * util, raw, util


# ---------------------------------------------------------------- host guards / runners --
def now():
    return datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def load3():
    return [float(x) for x in open("/proc/loadavg").read().split()[:3]]


def free_gb(path="/home"):
    return shutil.disk_usage(path).free / 1e9


def cpu_psi_avg10():
    try:
        return float(open("/proc/pressure/cpu").read().split()[1].split("=")[1])
    except (OSError, IndexError, ValueError):
        return None


def py_speed_s(n=3_000_000):
    """Single-thread interpreter speed (the residual clock IS Python glue time): seconds for a fixed n-step loop."""
    t = time.perf_counter(); acc = 0
    for i in range(n):
        acc += i
    return time.perf_counter() - t


SPEED_GATE = True
DEADLINE = None  # epoch seconds; set from --deadline (ISO UTC): stop waiting for a quiet host after it
SPEED_REF = OUTDIR / ".speed_ref"   # best (lowest) py_speed_s ever seen on this host: a ratchet that only gets stricter


def _speed_ok(tol=1.10):
    v = min(py_speed_s() for _ in range(3))
    try:
        ref = float(SPEED_REF.read_text())
    except (OSError, ValueError):
        ref = v
    if v < ref:
        ref = v
        try:
            SPEED_REF.write_text(f"{v:.4f}")
        except OSError:
            pass
    return v <= tol * ref, v, ref


PSI_START_MAX = 25.0  # coordinator 2026-10-09: start only when CPU PSI some avg10 < 25 %
PSI_ABORT = 40.0      # ... and abort a run in flight if it rises above 40 %


def _sustained_quiet(below, checks=4, every_s=30.0):
    """G-RB57: one 1-min-load reading under the gate let a contaminated run start (the v57_azs CONTROL then failed 6/10 on residual).
    Require the load gate to hold for `checks` readings `every_s` apart (90 s) AND single-thread Python speed within 10 % of the best
    ever seen here (CPU PSI was tried first: it sat at 70-84 % even at load 5, so it does not discriminate on this host)."""
    for i in range(checks):
        psi = cpu_psi_avg10()
        if load3()[0] >= below or (psi is not None and psi >= PSI_START_MAX) or (SPEED_GATE and not _speed_ok()[0]):
            return False
        if i < checks - 1:
            time.sleep(every_s)
    return True


def wait_load(below: float, cap_s: float, poll_s: float, log):
    t0 = time.time()
    if below >= 100:  # explicit "no gate" (screen / VALID / ship rungs measure FLOPs, raw and memory, not residual)
        return dict(ok=True, waited_s=0, load_at_start=load3()[0], samples=[], gate="disabled")
    samples = []
    while True:
        l1 = load3()[0]
        samples.append((now(), l1))
        if l1 < below and _sustained_quiet(below):
            return dict(
                ok=True, waited_s=round(time.time() - t0), load_at_start=l1, samples=samples[-20:]
            )
        if time.time() - t0 >= cap_s or (DEADLINE is not None and time.time() >= DEADLINE):
            return dict(
                ok=False, waited_s=round(time.time() - t0), load_at_start=l1, samples=samples[-20:]
            )
        log(f"waiting: load {l1:.2f} (gate {below}), cpu psi avg10 {cpu_psi_avg10()} (gate {PSI_START_MAX}), py speed {_speed_ok()[1:]} "
            f"({round(time.time() - t0)} s of {cap_s:.0f})")
        time.sleep(poll_s)


def _limits():
    resource.setrlimit(resource.RLIMIT_AS, (CHILD_AS_KB * 1024, CHILD_AS_KB * 1024))


def child_env():
    e = dict(os.environ)
    e["OMP_NUM_THREADS"] = "8"
    return e


def run(cmd, cwd, env=None, timeout=7200):
    """One heavy child at a time, ulimit -v 16 GB, OMP 8. Returns (rc, stdout, stderr, load_before, load_after)."""
    lb = load3()
    p = subprocess.run(
        cmd,
        cwd=cwd,
        env=env or child_env(),
        preexec_fn=_limits,
        capture_output=True,
        text=True,
        timeout=timeout,
    )
    return p.returncode, p.stdout, p.stderr, lb, load3()


def _descendants(pid):
    kids = {}
    for d in os.listdir("/proc"):
        if d.isdigit():
            try:
                ppid = int(open(f"/proc/{d}/stat").read().rsplit(")", 1)[1].split()[1])
                kids.setdefault(ppid, []).append(int(d))
            except (OSError, IndexError, ValueError):
                pass
    out, stack = [], [pid]
    while stack:
        p = stack.pop()
        for c in kids.get(p, []):
            out.append(c)
            stack.append(c)
    return out


def _vmpeak(pid):
    try:
        for line in open(f"/proc/{pid}/status"):
            if line.startswith("VmPeak:"):
                return int(line.split()[1]) // 1024
    except OSError:
        return None


def _identify(pid):
    """cmdline + RLIMIT_AS (MiB) of a live pid, so the worker is found by identity rather than by size rank."""
    out = {}
    try:
        out["cmd"] = open(f"/proc/{pid}/cmdline").read().replace("\0", " ")[:160]
        for line in open(f"/proc/{pid}/limits"):
            if line.startswith("Max address space"):
                soft = line.split()[3]
                out["as_limit_mb"] = None if soft == "unlimited" else int(soft) // 2**20
    except OSError:
        pass
    return out


def cmp_rows(sub: Path, tag: str, nets, f64=False):
    env = child_env()
    if f64:
        env["F64"] = "1"
    rc, out, err, lb, la = run(
        [str(PY), str(HERE / "lever46/cmp.py"), str(sub), tag, *map(str, nets)],
        cwd=ROOT / "research",
        env=env,
    )
    rows = [json.loads(l) for l in out.splitlines() if l.startswith("{")]
    return dict(rc=rc, rows=rows, load_before=lb, load_after=la, err_tail=err[-600:] if rc else "")


def mini10_one(sub: Path, tag: str, abort_psi=None):
    """mini10_ab.sh for ONE build (so each run gets its own load record + worker VmPeak poll)."""
    name = sub.name
    js = HERE / "whest" / f"{name}_{tag}.json"
    if js.exists():
        raise SystemExit(f"refusing to overwrite {js}")
    lb = load3()
    t0 = time.time()
    p = subprocess.Popen(
        ["bash", str(HERE / "mini10_ab.sh"), tag, str(sub)],
        cwd=ROOT,
        env=child_env(),
        preexec_fn=_limits,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        start_new_session=True,  # own process group, so a mid-run abort can stop the whole whest tree
    )
    aborted = None
    peak = {}
    ident = {}
    loads = []
    kids, next_scan, next_load = [], 0.0, 0.0
    while p.poll() is None:
        now_t = time.time()
        scanned = now_t >= next_scan
        if scanned:  # the full /proc walk is the expensive part: every 2 s; the VmPeak reads below every 0.1 s
            kids, next_scan = _descendants(p.pid), now_t + 2.0
        for c in kids:
            v = _vmpeak(c)
            if v:
                peak[c] = max(peak.get(c, 0), v)
                if c not in ident or (scanned and "subprocess_worker" not in ident[c].get("cmd", "")):
                    # re-read until the worker shows its post-exec identity: a fork caught before exec has an empty cmdline and the
                    # parent's RLIMIT_AS (G-RB57: v58_ne run 2's worker was cached as cmd '' / 15625 MiB, so worker_vmpeak read None)
                    ident[c] = _identify(c)
        if now_t >= next_load:
            loads.append(load3()[0]); next_load = now_t + 30.0
            psi = cpu_psi_avg10()
            if abort_psi is not None and psi is not None and psi > abort_psi and aborted is None:
                aborted = dict(t=now(), psi_avg10=psi, load=load3())
                os.killpg(p.pid, signal.SIGTERM)
        time.sleep(0.1)  # 0.5 s missed the between-predict payload-decode peak (8028 vs 8120 MiB, G-RB51)
    try:
        doc = json.load(open(js))
    except (OSError, ValueError):
        doc = None
    s = summarize_mini10(doc)
    vals = sorted(peak.values())
    s.update(
        build=name,
        tag=tag,
        json=str(js.relative_to(ROOT)),
        wall_s=round(time.time() - t0),
        load_before=lb,
        load_after=load3(),
        load_samples=loads,
        rc=p.returncode,
        aborted=aborted,
        # largest descendant = runner (mmaps the 6.3 GB set); second largest = worker (polled every 0.5 s: a lower bound)
        proc_vmpeak_mb=vals[::-1][:3],
        # identity, not size rank: the grader's worker is the process running subprocess_worker with RLIMIT_AS = 8192 MiB
        procs=[dict(pid=c, vmpeak_mb=peak[c], **ident.get(c, {})) for c in sorted(peak, key=peak.get, reverse=True)[:4]],
        worker_vmpeak_mb=max((peak[c] for c in peak if "subprocess_worker" in ident.get(c, {}).get("cmd", "")), default=None),
    )
    return s


def eval_mem(sub: Path):
    rc, out, err, lb, la = run(
        [str(PY), str(HERE / "eval_mem.py"), str(sub), "-", "0"], cwd=ROOT / "research"
    )
    rows = [json.loads(l) for l in out.splitlines() if l.startswith("{")]
    return dict(
        rc=rc,
        vm_peak_mb=rows[0]["vm_peak_mb"] if rows else None,
        row=rows[0] if rows else None,
        load_before=lb,
        load_after=la,
        err_tail=err[-600:] if rc or not rows else "",
    )


def archive_check(sub: Path, stamp: str):
    tgz = OUTDIR / f"submission-{sub.name}-{stamp}.tar.gz"
    rc, out, err, lb, la = run(
        [
            str(WHEST),
            "package",
            "--estimator",
            ".",  # the FOLDER: passing estimator.py packages it alone and drops weights.npz / lc_weights.npz (caught live 2026-10-08)
            "--output",
            str(tgz),
            "--yes",
            "--format",
            "plain",
        ],
        cwd=sub,
    )
    info = dict(package_rc=rc, archive=str(tgz.relative_to(ROOT)), package_tail=(out + err)[-400:])
    if rc or not tgz.exists():
        return False, info
    need = {"estimator.py"} | {p.name for p in sub.glob("*.npz")}
    with tarfile.open(tgz) as t:
        names = {Path(n).name for n in t.getnames()}
        info["members"] = sorted(names)
        info["missing"] = sorted(need - names)
        tmp = Path(tempfile.mkdtemp(prefix="ladder_arch_", dir=os.environ.get("TMPDIR")))
        t.extractall(tmp, filter="data")
    est = next(tmp.rglob("estimator.py"), None)
    if est is None or info["missing"]:
        return False, info
    rc2, out2, err2, _, _ = run(
        [str(WHEST), "validate", "--estimator", str(est), "--format", "plain"], cwd=est.parent
    )
    info.update(validate_rc=rc2, validate_tail=(out2 + err2)[-400:])
    shutil.rmtree(tmp, ignore_errors=True)
    return rc2 == 0, info


def f64_rel_dev(base: Path, cand: Path, stamp: str):

    tb, tc = f"LD{stamp}_b64", f"LD{stamp}_c64"
    rb = cmp_rows(base, tb, [0], f64=True)
    rcnd = cmp_rows(cand, tc, [0], f64=True)
    code = (
        "import numpy as np,sys;a=np.load(sys.argv[1]);b=np.load(sys.argv[2]);"
        "print(float(np.abs(a[-1]-b[-1]).max()/np.abs(b[-1]).max()))"
    )
    p = subprocess.run(
        [
            str(PY),
            "-c",
            code,
            str(HERE / f"lever46/out_{tc}_00000.npy"),
            str(HERE / f"lever46/out_{tb}_00000.npy"),
        ],
        capture_output=True,
        text=True,
    )
    try:
        return float(p.stdout.strip()), dict(base=rb, cand=rcnd)
    except ValueError:
        return None, dict(base=rb, cand=rcnd, err=p.stderr[-400:])


# ---------------------------------------------------------------- the ladder --
def main(argv=None):
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument("--base", required=True)
    ap.add_argument("--cand", required=True)
    ap.add_argument("--rungs", default="screen,valid,mini10,ship")
    ap.add_argument("--output-identical", action="store_true")
    ap.add_argument("--deadline", default=None, help="ISO UTC (e.g. 2026-10-10T05:00Z): stop waiting for a quiet host after it")
    ap.add_argument("--abort-psi", type=float, default=PSI_ABORT, help="abort + re-run a Mini-10 run if CPU PSI avg10 exceeds this mid-run")
    ap.add_argument("--mini10-max-attempts", type=int, default=6)
    ap.add_argument("--mini10-max-sessions", type=int, default=4, help="re-run the whole Mini-10 session when the control is not clean")
    ap.add_argument("--control-max-residual", type=float, default=0.36, help="session void if the base control's worst residual exceeds this")
    ap.add_argument("--psi-log-only", action="store_true", help="(now the default; kept for old command lines)")
    ap.add_argument("--psi-gate", action="store_true", help="opt in to the CPU-PSI start gate / abort (off by default: on this host PSI sits at 66-84 %% even at load 2, so the gate never opens; lesson 9, G-RB53b/77)")
    ap.add_argument("--no-speed-gate", action="store_true", help="python-speed ratchet logged only")
    ap.add_argument("--adj-max", type=float, default=None, help="override the Mini-10 adjusted-ratio bar (e.g. 1.01 for a safety variant, G-RB52)")
    ap.add_argument("--worker-mem-max", type=int, default=7900, help="bar: grader worker VmPeak MiB (G-RB51; default 7900 since G-RB57; 0 disables)")
    ap.add_argument(
        "--head-ref",
        type=float,
        default=None,
        help="prototype-with-head f64 final MSE on net 10 (G-RB34b check)",
    )
    ap.add_argument(
        "--also",
        action="append",
        default=[],
        help="extra build(s) timed in the same Mini-10 session (reported, no bars)",
    )
    ap.add_argument(
        "--mini10-repeats", type=int, default=1, help="passes; order alternates (A B C, C B A, ...)"
    )
    ap.add_argument(
        "--mini10-close-with-base",
        action="store_true",
        help="append one more base run at the end of the session",
    )
    ap.add_argument("--wait-load-below", type=float, default=GUARDS["max_load_1m"])
    ap.add_argument("--wait-cap-s", type=float, default=3 * 3600)
    ap.add_argument("--wait-poll-s", type=float, default=120)
    ap.add_argument("--no-stop", action="store_true", help="keep climbing after a failed rung")
    ap.add_argument("--out", default=None)
    a = ap.parse_args(argv)
    rungs = [r.strip() for r in a.rungs.split(",") if r.strip()]
    BARS["mini10_worker_vmpeak"]["limit"] = a.worker_mem_max or None
    global DEADLINE, PSI_START_MAX, SPEED_GATE
    if not a.psi_gate:
        PSI_START_MAX, a.abort_psi = float("inf"), None
    SPEED_GATE = not a.no_speed_gate
    if a.deadline:
        DEADLINE = datetime.strptime(a.deadline.rstrip("Z"), "%Y-%m-%dT%H:%M").replace(tzinfo=UTC).timestamp()
    if a.adj_max is not None:
        BARS["mini10_adj"]["limit"] = BARS["mini10_adj_not_worse"]["limit"] = a.adj_max
    base, cand = (ROOT / a.base).resolve(), (ROOT / a.cand).resolve()
    extras = [(ROOT / x).resolve() for x in a.also]
    for d in [base, cand, *extras]:
        if not (d / "estimator.py").exists():
            raise SystemExit(f"no estimator.py in {d}")
    OUTDIR.mkdir(exist_ok=True)
    out = (ROOT / a.out).resolve() if a.out else OUTDIR / f"{cand.name}_vs_{base.name}.json"
    stamp = datetime.now(UTC).strftime("%m%d%H%M")
    log = lambda m: print(f"{now()} {m}", flush=True)

    if free_gb() < GUARDS["min_free_gb"]:
        raise SystemExit(f"REFUSE: /home free {free_gb():.1f} GB < {GUARDS['min_free_gb']} GB")
    lock = open(OUTDIR / ".lock", "w")
    try:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        raise SystemExit(
            "REFUSE: another ladder run holds research/rebuild/ladder/.lock (one heavy process)"
        )

    rep = dict(
        base=base.name,
        cand=cand.name,
        also=[e.name for e in extras],
        rungs=rungs,
        output_identical=a.output_identical,
        head_ref=a.head_ref,
        started=now(),
        host=dict(free_gb_start=round(free_gb(), 1), load_start=load3()),
        bars_def=BARS,
        rung_data={},
    )
    res = {}
    wait = wait_load(a.wait_load_below, a.wait_cap_s, a.wait_poll_s, log)
    rep["host"]["wait"] = wait
    if not wait["ok"]:
        rep["aborted"] = f"load stayed >= {a.wait_load_below} for {a.wait_cap_s:.0f} s"
    stop = lambda r: (
        (not a.no_stop)
        and any(
            evaluate_bars(res, [r], a.output_identical, a.head_ref is not None)[0][k]["verdict"]
            != "PASS"
            for k in evaluate_bars(res, [r], a.output_identical, a.head_ref is not None)[0]
        )
    )
    halted = rep.get("aborted")

    if not halted and "screen" in rungs and not a.output_identical:
        log("rung screen: cmp.py FIT 0/2/4, one process per build")
        sb = cmp_rows(base, f"LD{stamp}_{base.name}", FIT)
        sc = cmp_rows(cand, f"LD{stamp}_{cand.name}", FIT)
        rep["rung_data"]["screen"] = dict(base=sb, cand=sc)
        if len(sb["rows"]) == len(FIT) == len(sc["rows"]):
            res["screen_adj"] = pooled_adj(sc["rows"])[0] / pooled_adj(sb["rows"])[0]
        halted = "screen" if stop("screen") else None

    if not halted and "valid" in rungs and not a.output_identical:
        log("rung valid: VALID-20 in fresh-process chunks of 5")
        rb, rc_ = [], []
        for i in range(0, 20, 5):
            ch = VALID20[i : i + 5]
            rb += cmp_rows(base, f"LD{stamp}_V{i}_{base.name}", ch)["rows"]
            rc_ += cmp_rows(cand, f"LD{stamp}_V{i}_{cand.name}", ch)["rows"]
        rep["rung_data"]["valid"] = dict(base=rb, cand=rc_)
        if len(rb) == 20 == len(rc_):
            res["valid_adj"] = pooled_adj(rc_)[0] / pooled_adj(rb)[0]
            res["valid_worst_raw"] = max(c["raw"] / b["raw"] for b, c in zip(rb, rc_))
            rep["rung_data"]["valid"]["n_improve"] = sum(
                c["raw"] < b["raw"] for b, c in zip(rb, rc_)
            )
        halted = "valid" if stop("valid") else None

    if not halted and "mini10" in rungs:
        builds = [base, cand, *extras]
        order = []
        for k in range(a.mini10_repeats):
            order += builds if k % 2 == 0 else builds[::-1]
        if a.mini10_close_with_base:
            order.append(base)
        voided = []
        for sess in range(a.mini10_max_sessions):
            runs = []
            for i, b in enumerate(order):
                # every run is its own timing sample: re-gate on load before EACH one (G-RB51: external load arrived mid-session and
                # pushed even the base to 7/10 failed; one start-gate cannot protect a 35-min session). Settle 60 s after our own run.
                if i:
                    time.sleep(60)
                attempts = []
                for att in range(a.mini10_max_attempts):  # a run aborted on CPU pressure mid-flight is re-gated and re-run (fresh tag)
                    w = wait_load(a.wait_load_below, a.wait_cap_s, a.wait_poll_s, log)
                    if not w["ok"]:
                        break
                    log(f"rung mini10: run {i + 1}/{len(order)} {b.name} attempt {att + 1} (load {load3()[0]:.2f}, psi {cpu_psi_avg10()}, waited {w['waited_s']} s)")
                    sp = _speed_ok()
                    r = mini10_one(b, f"L{stamp}s{sess}r{i}a{att}", abort_psi=a.abort_psi)
                    r["gate_wait"] = w
                    r["py_speed_s"], r["py_speed_ref_s"] = round(sp[1], 4), round(sp[2], 4)
                    attempts.append(r)
                    if not r.get("aborted"):
                        break
                    log(f"  ABORTED mid-run: {r['aborted']}")
                if not attempts or attempts[-1].get("aborted"):
                    rep["aborted"] = f"mini10 run {i + 1} ({b.name}) never completed on a quiet host before the deadline/cap"
                    runs.append(dict(build=b.name, n_rows=0, aborted_attempts=attempts))
                    log(rep["aborted"])
                    break
                runs.append(dict(attempts[-1], aborted_attempts=attempts[:-1]))
                log(
                    f"  -> adj {runs[-1].get('adjusted')} failed {runs[-1].get('failed')} res max {runs[-1].get('res_max')}"
                )
                r_ = runs[-1]
                if r_.get("build") == base.name and r_.get("n_rows") == 10 and (r_["failed"] > 0 or r_["res_max"] > a.control_max_residual):
                    break  # control already dirty: stop spending this session, void it below

            # G-RB57 validity rule (coordinator 2026-10-10): the in-session CONTROL (base) must itself be clean, else the session is void
            bad = [r for r in runs if r.get("build") == base.name and r.get("n_rows") == 10
                   and (r["failed"] > 0 or r["res_max"] > a.control_max_residual)]
            if rep.get("aborted") or not bad:
                break
            log(f"SESSION {sess} VOID: control {base.name} failed {[r['failed'] for r in bad]} / worst residual "
                f"{[round(r['res_max'], 3) for r in bad]} (> {a.control_max_residual}); retrying the whole session")
            voided.append(runs)
        rep["rung_data"]["mini10_voided_sessions"] = voided
        rep["rung_data"]["mini10"] = runs
        # bars use the FIRST base run and the FIRST cand run (same session, adjacent); worst residual / failed over ALL cand runs
        rb = [r for r in runs if r["build"] == base.name]
        rc_ = [r for r in runs if r["build"] == cand.name]
        # G-RB66 (2026-10-11): when every session is VOID the last one holds only the dirty control, so rc_ is empty -- record
        # NOT_RUN (and the void) instead of crashing before the report is written (the crash lost the session's JSON once).
        if len(voided) == a.mini10_max_sessions:
            rep["mini10_all_sessions_void"] = True
        res["mini10_complete"] = min((r["n_rows"] for r in rc_ + rb), default=0) if rc_ else 0
        if rb and rc_ and all(r["n_rows"] == 10 for r in rb + rc_):
            res["mini10_failed"] = max(r["failed"] for r in rc_)
            res["mini10_residual"] = max(r["res_max"] for r in rc_)
            if BARS["mini10_worker_vmpeak"]["limit"] is not None:
                wv = [r.get("worker_vmpeak_mb") for r in rc_]
                res["mini10_worker_vmpeak"] = None if None in wv else max(wv)
            ratio = rc_[0]["adjusted"] / rb[0]["adjusted"]
            res["mini10_adj_not_worse" if a.output_identical else "mini10_adj"] = ratio
        halted = "mini10" if stop("mini10") else None

    if not halted and "ship" in rungs:
        log("rung ship: eval_mem net 0")
        em = eval_mem(cand)
        res["eval_mem"] = em["vm_peak_mb"]
        log("rung ship: whest package + archive validate")
        ok, info = archive_check(cand, stamp)
        res["archive"] = ok
        rep["rung_data"]["ship"] = dict(eval_mem=em, archive=info)
        if a.output_identical:
            log("rung ship: f64 identity net 0")
            dev, info2 = f64_rel_dev(base, cand, stamp)
            res["f64_identity"] = dev
            rep["rung_data"]["ship"]["f64"] = info2
        if a.head_ref is not None:
            log("rung ship: f64 with head on net 10 vs prototype")
            hc = cmp_rows(cand, f"LD{stamp}_h64_{cand.name}", [HEAD_NET], f64=True)
            rep["rung_data"]["ship"]["head"] = hc
            if hc["rows"]:
                res["head_check"] = abs(hc["rows"][0]["raw"] / a.head_ref - 1)

    per, overall = evaluate_bars(res, rungs, a.output_identical, a.head_ref is not None)
    rep.update(
        bars=per,
        verdict=overall,
        halted_at=halted,
        finished=now(),
        host_end=dict(load=load3(), free_gb=round(free_gb(), 1)),
    )
    out.write_text(json.dumps(rep, indent=1, default=str))
    fails = [k for k, v in per.items() if v["verdict"] != "PASS"]
    notpass = "; ".join(f"{k}={per[k]['value']}:{per[k]['verdict']}" for k in fails)
    line = (f"- {now()} ladder {cand.name} vs {base.name} rungs={','.join(rungs)}: {overall}"
            + (f" (not PASS: {notpass})" if fails else "") + f"; report {out.relative_to(ROOT)}; nothing submitted\n")
    with open(ROOT / "PROGRESS.md", "a") as fo:
        fo.write(line)
    log(line.strip())
    return 0 if overall == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
