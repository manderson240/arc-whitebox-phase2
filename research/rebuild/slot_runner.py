"""Unattended slot runner: ladder each queued candidate, then submit it iff the pre-registered probe rule passes.

  slot_runner.py run [--queue Q] [--dry-run]     process every pending entry in order (one ladder at a time)
  slot_runner.py self-test                       decision-rule tests (must pass before a real run)
Every entry first passes remote_check.py (G-RB123: flopscope REMOTE mode, as the grader runs it) or is HELD "REMOTE-FAIL".

Queue (JSONL, append-only): {"build": "submissions/x", "base": "submissions/y", "base_graded": 4.6e-9, "why": "...",
"gate": "G-RB104"}. Results are appended to slot_runner.jsonl (one line per entry; an entry with a result is never re-run).
Rule (user directive 2026-10-16 "leverage all daily submissions"; widens the 2026-10-13 auto gate to labelled PROBES):
VALID-20 adj <= PROBE_VALID AND Mini-10 adj <= PROBE_MINI AND 0 failed AND eval_mem/archive PASS AND worker VmPeak
<= 7900 AND today's submissions < DAY_CAP. Prediction = base_graded x VALID-20 adj (logged by submit.py).
"""

import json
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PY = str(ROOT / "whest-starterkit/.venv/bin/python")
QUEUE, OUT, CAL = HERE / "slot_queue.jsonl", HERE / "slot_runner.jsonl", HERE / "calibration.jsonl"
PROBE_VALID, PROBE_MINI, VMPEAK, DAY_CAP = 0.995, 1.0, 7900, 10


def decide(bars: dict, n_today: int) -> tuple[bool, str]:
    """bars = ladder.py report['bars'] ({name: {value, verdict}}). Returns (submit?, reason)."""
    v = {k: b.get("value") for k, b in bars.items()}
    checks = [
        (n_today < DAY_CAP, f"day cap {n_today}/{DAY_CAP}"),
        (
            v.get("valid_adj") is not None and v["valid_adj"] <= PROBE_VALID,
            f"valid_adj {v.get('valid_adj')}",
        ),
        (
            v.get("mini10_adj") is not None and v["mini10_adj"] <= PROBE_MINI,
            f"mini10_adj {v.get('mini10_adj')}",
        ),
        (v.get("mini10_failed") == 0, f"failed {v.get('mini10_failed')}"),
        (v.get("mini10_complete") == 10, f"complete {v.get('mini10_complete')}"),
        (bars.get("eval_mem", {}).get("verdict") == "PASS", "eval_mem"),
        (v.get("archive") is True, "archive"),
        (
            (v.get("mini10_worker_vmpeak") or 1e9) <= VMPEAK,
            f"vmpeak {v.get('mini10_worker_vmpeak')}",
        ),
    ]
    bad = [why for ok, why in checks if not ok]
    return (not bad, "PASS" if not bad else "HOLD: " + "; ".join(bad))


def today_count() -> int:
    day = datetime.now(UTC).strftime("%Y-%m-%d")
    rows = [json.loads(ln) for ln in CAL.read_text().splitlines() if ln.strip()]
    return sum(
        1 for r in rows if r.get("status") == "submitted" and str(r.get("t", "")).startswith(day)
    )


CONTROL_MAX = 0.36  # ladder.py --control-max-residual default: a session voids when the base control exceeds it


def base_control_residual(base_name: str, ladder_dir: Path = HERE / "ladder") -> float | None:
    """Best (quiet-machine) worst-net Mini-10 residual recorded for `base_name` (None if never timed).
    2026-10-17: v98 queued with base v97 (0.368-0.375 s) voided every session against the 0.36 s control gate."""
    worst = None
    for f in sorted(ladder_dir.glob("*.json")):
        try:
            sessions = json.loads(f.read_text()).get("rung_data", {}).get("mini10", [])
        except (OSError, ValueError, AttributeError):
            continue
        for x in sessions if isinstance(sessions, list) else []:
            if (
                isinstance(x, dict)
                and x.get("build") == base_name
                and x.get("res_max") is not None
                and not x.get("aborted")
            ):
                worst = (
                    x["res_max"] if worst is None else min(worst, x["res_max"])
                )  # min = quiet-machine speed (loaded sessions only inflate it)
    return worst


LOCK_WAIT_S = (
    4 * 3600
)  # max time a shared job may queue behind a timing run before its own timeout starts to bite
SHARED_RE = r"rb130/(cap|eval)\.sh|rb131/s131|rb132/|remote_check\.py|fingerprint\.py"


def shared_locked(cmd: list[str]) -> tuple[list[str], dict]:
    """2026-10-20 (arcwb_L14): the pre-ladder remote_check + fingerprint ran OUTSIDE timing_lock and took G-RB145's
    exclusive clock window from load 4.6 to 18. Run them as SHARED compute: they wait behind any timing run instead."""
    import os

    return [str(HERE / "timing_lock.sh"), *cmd], {**os.environ, "TIMING_LOCK_SHARED_RE": SHARED_RE}


def remote_gate(
    build: str, extra_env: dict | None = None, nets: int = 2, timeout: int = 900, lock: bool = False
) -> tuple[bool, str]:
    """G-RB123 (2026-10-18): run the build in flopscope REMOTE mode (the grader's client/server split) via remote_check.py.
    v99_rm/v100_xs/v101_xp passed every local rung and failed on AIcrowd with ESTIMATOR_EXCEPTION on all 100 MLPs.
    Fail-closed: only an explicit `REMOTE_CHECK PASS` line with exit 0 and no flags passes; FAIL, HARNESS, a timeout, a
    crash or an unparseable result all HOLD."""
    import os

    env = {**os.environ, **(extra_env or {})}
    cmd = ["python3", str(HERE / "remote_check.py"), build, "--nets", str(nets)]
    if lock:
        cmd, lenv = shared_locked(cmd)
        env["TIMING_LOCK_SHARED_RE"] = lenv["TIMING_LOCK_SHARED_RE"]
        timeout += LOCK_WAIT_S
    try:
        r = subprocess.run(
            cmd,
            cwd=ROOT,
            env=env,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
    except Exception as ex:
        return False, f"REMOTE-FAIL: HARNESS {type(ex).__name__}: {ex}"[:400]
    last = next(
        (ln for ln in reversed(r.stdout.splitlines()) if ln.startswith("REMOTE_CHECK ")), ""
    )
    parts = last.split(" ", 2)
    verdict = parts[1] if len(parts) > 1 else "NONE"
    try:
        info = json.loads(parts[2]) if len(parts) > 2 else {}
    except json.JSONDecodeError:
        info = {}
    if verdict == "PASS" and r.returncode == 0 and not info.get("flags"):
        return True, "REMOTE-PASS"
    detail = (
        info.get("exc")
        or info.get("why")
        or ",".join(info.get("flags") or [])
        or (r.stderr or r.stdout)[-300:]
    )
    return False, f"REMOTE-FAIL: {verdict} {detail}"[:400]


def run(queue: Path, dry: bool) -> None:
    # 2026-10-18: a HOLD with "complete 0" means every Mini-10 session voided (host too loaded); retry it next run
    done = (
        {
            r["build"]
            for r in map(json.loads, OUT.read_text().splitlines())
            if "complete 0" not in str(r.get("decision"))
        }
        if OUT.exists()
        else set()
    )
    for e in [json.loads(ln) for ln in queue.read_text().splitlines() if ln.strip()]:
        if e["build"] in done:
            continue
        subprocess.run(
            [
                "python3",
                str(ROOT / "research/leaderboard/insights.py"),
                "--record-pending",
                "--top",
                "1",
            ],
            cwd=ROOT,
            timeout=180,
            check=False,
        )  # close the loop: record any grade that landed (fail-open)
        name = Path(e["build"]).name
        rep = HERE / "ladder" / f"slot_{name}.json"
        ctl = base_control_residual(Path(e["base"]).name)
        if ctl is not None and ctl > CONTROL_MAX:
            rec = dict(
                build=e["build"],
                gate=e["gate"],
                decision=f"HOLD: base control residual {ctl:.3f} s > {CONTROL_MAX} s (every Mini-10 session would void); requeue with a faster base",
                predicted=None,
                submitted=None,
                t=datetime.now(UTC).strftime("%FT%TZ"),
            )
            with OUT.open("a") as fh:
                fh.write(json.dumps(rec) + "\n")
            print(rec, flush=True)
            continue
        rok, rwhy = remote_gate(
            e["build"], lock=True
        )  # G-RB123: mandatory pre-ladder gate (fail-closed)
        if not rok:
            rec = dict(
                build=e["build"],
                gate=e["gate"],
                decision=f"HOLD: {rwhy}",
                predicted=None,
                submitted=None,
                t=datetime.now(UTC).strftime("%FT%TZ"),
            )
            with OUT.open("a") as fh:
                fh.write(json.dumps(rec) + "\n")
            print(rec, flush=True)
            continue
        fcmd, fenv = shared_locked([PY, str(HERE / "fingerprint.py"), e["base"], e["build"]])
        fp = subprocess.run(
            fcmd,
            cwd=ROOT,
            env=fenv,
            capture_output=True,
            text=True,
            timeout=1500 + LOCK_WAIT_S,
            check=False,
        )
        if fp.stdout.strip().endswith(
            "SAME"
        ):  # 2026-10-17: v91 was a dead-constant no-op that was laddered and submitted
            rec = dict(
                build=e["build"],
                gate=e["gate"],
                decision="HOLD: NO-OP (fingerprint identical to base)",
                predicted=None,
                submitted=None,
                t=datetime.now(UTC).strftime("%FT%TZ"),
            )
            with OUT.open("a") as fh:
                fh.write(json.dumps(rec) + "\n")
            print(rec, flush=True)
            continue
        subprocess.run(
            [
                str(Path.home() / "dev/cohezion/.venv/bin/python"),
                "-m",
                "cohezion.sessions",
                "send",
                "--from",
                "arcwb-d14921a9",
                "all",
                f"ARC White-Box: Mini-10 timing ladder for {name} starting in ~20 min; "
                "please keep CPU load < 5 for ~45 min (timing runs void under load).",
            ],
            cwd=Path.home() / "dev/cohezion",
            timeout=60,
            check=False,
            capture_output=True,
        )  # fail-open
        subprocess.run(
            [
                str(
                    HERE / "timing_lock.sh"
                ),  # 2026-10-18: one timing run at a time across builders
                PY,
                str(HERE / "ladder.py"),
                "--base",
                e["base"],
                "--cand",
                e["build"],
                "--rungs",
                "valid,mini10,ship",
                "--no-stop",
                "--out",
                str(rep.relative_to(ROOT)),
            ],
            cwd=ROOT,
        )
        bars = json.loads(rep.read_text()).get("bars", {}) if rep.exists() else {}
        ok, why = decide(bars, today_count())
        pred = e["base_graded"] * bars["valid_adj"]["value"] if "valid_adj" in bars else None
        sid = None
        if ok and not dry:
            basis = f"{e['gate']} slot_runner: VALID-20 adj {bars['valid_adj']['value']:.4f}, Mini-10 adj {bars['mini10_adj']['value']:.4f}, 0 failed, ship PASS; base {e['base_graded']:.3g} x VALID"
            r = subprocess.run(
                [
                    PY,
                    str(HERE / "submit.py"),
                    e["build"],
                    "--predicted",
                    f"{pred:.3g}",
                    "--basis",
                    basis,
                    "--why",
                    f"PROBE {e['gate']}: {e['why']}",
                ],
                cwd=ROOT,
                capture_output=True,
                text=True,
            )
            sid = r.stdout.strip().splitlines()[-1] if r.stdout.strip() else r.stderr[-300:]
        rec = dict(
            build=e["build"],
            gate=e["gate"],
            decision=why,
            predicted=pred,
            submitted=sid,
            t=datetime.now(UTC).strftime("%FT%TZ"),
        )
        with OUT.open("a") as fh:
            fh.write(json.dumps(rec) + "\n")
        with (ROOT / "PROGRESS.md").open("a") as fh:
            fh.write(
                f"- {rec['t']} slot_runner {e['gate']} {name}: {why}; pred {pred}; submitted {sid}\n"
            )
        print(rec, flush=True)


def self_test() -> None:
    import tempfile

    d = Path(tempfile.mkdtemp())
    (d / "a.json").write_text(
        json.dumps(
            {
                "rung_data": {
                    "mini10": [
                        {"build": "fast", "res_max": 0.34},
                        {"build": "slow", "res_max": 0.375},
                        {"build": "fast", "res_max": 0.59},
                    ]
                }
            }
        )
    )
    assert (
        base_control_residual("slow", d) == 0.375 > CONTROL_MAX
        and base_control_residual("fast", d) < CONTROL_MAX
    )
    assert base_control_residual("never", d) is None
    good = {
        "valid_adj": {"value": 0.98},
        "mini10_adj": {"value": 0.99},
        "mini10_failed": {"value": 0},
        "mini10_complete": {"value": 10},
        "eval_mem": {"value": 5900, "verdict": "PASS"},
        "archive": {"value": True},
        "mini10_worker_vmpeak": {"value": 7500},
    }
    assert decide(good, 3) == (True, "PASS")
    for k, val in [
        ("valid_adj", 0.999),
        ("mini10_failed", 1),
        ("mini10_complete", 9),
        ("archive", False),
        ("mini10_worker_vmpeak", 8000),
        ("mini10_adj", 1.01),
    ]:
        bad = {**good, k: {"value": val}}
        assert decide(bad, 3)[0] is False, k
    assert decide({**good, "eval_mem": {"value": 7000, "verdict": "FAIL"}}, 3)[0] is False
    assert decide(good, DAY_CAP)[0] is False
    assert decide({}, 0)[0] is False  # a missing/aborted ladder report never submits
    # G-RB123 remote gate: REAL minimal reproductions through remote_check.py, not mocks.
    est = """import flopscope.numpy as fnp
from whestbench import BaseEstimator


class Estimator(BaseEstimator):
    def setup(self, context):
        pass

    def predict(self, mlp, budget):
        x = fnp.ones((16, 1024), dtype=fnp.float32)
        return (x.transpose(%s)).transpose(1, 0)
"""
    for nm, spelling in (("ok", "1, 0"), ("onetuple", "(1, 0)")):
        (d / nm).mkdir()
        (d / nm / "estimator.py").write_text(est % spelling)
    ok_, why_ = remote_gate(str(d / "ok"), nets=1, timeout=600)
    assert ok_ and why_ == "REMOTE-PASS", why_
    ok_, why_ = remote_gate(str(d / "onetuple"), nets=1, timeout=600)
    assert (
        not ok_
        and why_.startswith("REMOTE-FAIL: FAIL")
        and "cannot be interpreted as an integer" in why_
    ), why_
    ok_, why_ = remote_gate(
        str(d / "ok"), extra_env={"REMOTE_CHECK_SERVER_PY": str(d / "no_such_python")}, nets=1
    )
    assert not ok_ and why_.startswith("REMOTE-FAIL: HARNESS"), (
        why_
    )  # a harness that cannot start HOLDs
    ok_, why_ = remote_gate(str(d / "missing_build"), nets=1)
    assert not ok_ and why_.startswith("REMOTE-FAIL"), why_
    print("self-test OK (1 pass case, 9 must-hold cases; remote gate: 1 pass, 3 must-hold)")


if __name__ == "__main__":
    if sys.argv[1:2] == ["self-test"]:
        self_test()
    elif sys.argv[1:2] == ["run"]:
        q = Path(sys.argv[sys.argv.index("--queue") + 1]) if "--queue" in sys.argv else QUEUE
        run(q, "--dry-run" in sys.argv)
    else:
        print(__doc__)
