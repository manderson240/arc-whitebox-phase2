"""Gate ledger: one queryable record per G-RB gate parsed from research/R2_GO_NOGO.md (dead ends you must not re-derive).

usage: python research/rebuild/gate_ledger.py build [--no-surreal]    -> research/rebuild/gates.jsonl (+ SurrealDB experiment_runs, fail-open)
       python research/rebuild/gate_ledger.py query <keywords...> [-n 8]
Query = every keyword must match (normalized: Greek -> latin names, punctuation stripped, 4+ char tokens prefix-match), ranked by
where it matches (header > verdict > body). stdlib only.
"""

from __future__ import annotations

import base64
import json
import re
import sys
import unicodedata
import urllib.request
from pathlib import Path


HERE = Path(__file__).resolve().parent
SRC = HERE.parent / "R2_GO_NOGO.md"
OUT = HERE / "gates.jsonl"
GID = re.compile(r"G-RB(\d+)([a-z]?)\b")
GREEK = {
    "κ": "kappa",
    "λ": "lambda",
    "Λ": "lambda",
    "σ": "sigma",
    "Σ": "sigma",
    "μ": "mu",
    "δ": "delta",
    "Δ": "delta",
    "γ": "gamma",
    "β": "beta",
    "α": "alpha",
    "ε": "epsilon",
    "ρ": "rho",
    "τ": "tau",
    "θ": "theta",
    "ω": "omega",
    "χ": "chi",
}
VERDICTS = [  # first match in a verdict line wins; conditional bar language ("KILL if", "STOP rules") is excluded
    ("KILL", r"\bNO-GO\b|\bKILL(?:ED|S)?\b(?! if| rule)|\bCLOSED\b|\bno candidate\b|\bruled out\b"),
    ("STOP", r"\bSTOP\b(?! if| rule)|\bABORT"),
    ("MISS", r"\bMISS(?:ES)?\b|letter[- ]miss|\bMIXED\b|\bWEAK\b"),
    ("FAIL", r"\bFAIL(?:S|ED)?\b(?! if| rule)"),
    ("PASS", r"(?<!not )\bPASS(?:ES|ED)?\b(?! if| rule)|(?<!NO-)\bGO\b(?! if)|\bSUPPORTED\b"),
]
NORM_VERDICT = {
    "KILL": "KILL",
    "FAIL": "KILL",
    "STOP": "STOP",
    "MISS": "MISS",
    "PASS": "PASS",
    "INFO": "INFO",
}  # INFO = analysis-only (no lever bar)
NUM = re.compile(
    r"(?<![\w.])(?:\d+\.\d+e-\d+|0\.9\d{2,4}|1\.\d{2,4}|[×x] ?\d+(?:\.\d+)?|[−+-]\d+(?:\.\d+)? ?%)"
)


def norm_text(s: str) -> str:
    for g, lat in GREEK.items():
        s = s.replace(g, f" {lat} ")
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    s = re.sub(
        r"(?<=[a-z])(?=\d)|(?<=\d)(?=[a-z])", "", s.lower()
    )  # kappa 4 -> kappa4 after the join below
    s = re.sub(r"[^a-z0-9]+", " ", s)
    s = re.sub(
        r"\b(kappa|lambda|sigma|mu|delta|gamma|beta|alpha|rho|tau|theta|omega|chi) (\d)\b",
        r"\1\2",
        s,
    )
    return s.strip()


def tokens(s: str) -> list[str]:
    return norm_text(s).split()


def _match(q: str, toks: set[str]) -> bool:
    if q in toks:
        return True
    return len(q) >= 4 and any(t.startswith(q) for t in toks)


def sections(md: str):
    """Split at markdown headings (## / ###) AND at bold verdict bullets/paragraphs that name a gate ("- **G-RB34b ...", "**G-RB50 RESULT")."""
    lines = md.splitlines()
    cur = None
    head = re.compile(r"^(#{2,3} .*G-RB\d+.*|\s*-?\s*\*\*G-RB\d+[a-z]?\b.*)$")
    for ln in lines:
        if head.match(ln):
            if cur:
                yield cur
            cur = dict(header=ln.strip(), body=[ln])
        elif ln.startswith("## ") or ln.startswith(
            "### "
        ):  # non-gate heading ends the current gate section
            if cur:
                yield cur
            cur = None
        elif cur:
            cur["body"].append(ln)
    if cur:
        yield cur


def classify_line(text: str):
    text = text[:300]  # the verdict is stated up front; later words are evidence, not verdict
    hits = []
    for name, pat in VERDICTS:
        m = re.search(pat, text)
        if m:
            hits.append((m.start(), name))
    return NORM_VERDICT[min(hits)[1]] if hits else "UNKNOWN"


# upper case, or a bare "Verdict:" -- never "Verdict rule:" / "Most likely verdict" (pre-registration text)
VLINE = re.compile(r"VERDICT|RESULT|(?<!likely )\bVerdict\b(?! rule)")


def _strip_paren(t: str) -> str:
    """Drop a leading "( ... )" run note (dates, tags, load) so the verdict words come first."""
    t = t.lstrip(" :*-—")
    if t.startswith("("):
        depth = 0
        for i, ch in enumerate(t):
            depth += ch == "("
            depth -= ch == ")"
            if depth == 0:
                return t[i + 1 :].lstrip(" :*-—")
    return t


def verdict_lines(body: str) -> list[str]:
    """For each RESULT / VERDICT line: the rest of its bullet/paragraph (to the next bullet, blank or heading), run note stripped."""
    lines = body.splitlines()
    out = []
    for i, ln in enumerate(lines):
        m = VLINE.search(ln)
        if not m or ("PRE-REGISTRATION" in ln and "VERDICT" not in ln):
            continue
        para = [ln[m.end() :]]
        for nxt in lines[i + 1 : i + 8]:
            if (
                not nxt.strip()
                or nxt.startswith("#")
                or re.match(r"\s*- ", nxt)
                or nxt.startswith("**G-RB")
            ):
                break
            para.append(nxt.strip())
        out.append(re.sub(r"\s+", " ", _strip_paren(" ".join(para))).strip())
    return out


ORCH = re.compile(r"\*\*G-RB\w*\s+(?:ORCHESTRATOR\s+(?:CHECK|DECISION|NOTE)|VERDICT)\b[^*]*\*\*:?(.*)")


def orchestrator_verdict(body: str):
    """The LAST orchestrator line (an independent re-computation from the raw files) is authoritative.

    Added 2026-10-20: sub-bar wording ("Raw legs PASS") made classify() store KILLed gates
    (G-RB140, G-RB143) as PASS in SurrealDB, which teaches the wrong lesson."""
    hit = None
    for ln in body.splitlines():
        m = ORCH.search(ln)
        if m:
            hit = ln
    if not hit:
        return None
    u = hit.upper()
    if re.search(r"KILL (CONFIRMED|STANDS|ACCEPTED)|: KILL\b|\bKILL\b.*NO RE-REGISTRATION", u):
        return "KILL", hit
    if re.search(r"PASS CONFIRMED|BECOMES #1|REPLACES|HELD-OUT PASS|: PASS\b", u):
        return "PASS", hit
    return None  # no explicit verdict phrase: fall through to the sub-bar parser


def classify(body: str):
    """Orchestrator verdict if present; else PASS if any verdict line passes; else the first decided verdict; else UNKNOWN."""
    vl = verdict_lines(body)
    ov = orchestrator_verdict(body)
    if ov:
        return ov[0], ov[1], vl
    vs = [(classify_line(x), x) for x in vl]
    for v, x in vs:
        if v == "PASS":
            return v, x, vl
    for v, x in vs:
        if v != "UNKNOWN":
            return v, x, vl
    return "UNKNOWN", (vl[0] if vl else ""), vl


def build_records(md: str):
    by = {}
    for sec in sections(md):
        ids = []
        for m in GID.finditer(sec["header"]):
            gid = f"G-RB{m.group(1)}{m.group(2)}"
            if gid not in ids:
                ids.append(gid)
        if not ids:
            continue
        # a bullet like "- **G-RB34b ..." belongs only to its first id; a heading "G-RB30 / G-RB31" to all of its ids
        if not sec["header"].startswith(
            "#"
        ):  # "- **G-RB8 / G-RB7 / G-RB6 — ..." -> the ids before the first dash
            ids = [
                f"G-RB{m.group(1)}{m.group(2)}"
                for m in GID.finditer(sec["header"].split("—", 1)[0])
            ] or ids[:1]
        body = "\n".join(sec["body"])
        for gid in ids:
            r = by.setdefault(gid, dict(id=gid, headers=[], body=[], vbody=[], shared=[]))
            r["headers"].append(sec["header"])
            r["body"].append(body)
            # a verdict paragraph shared by several ids ("G-RB8 / G-RB7 / G-RB6 — VERDICT") cannot be split by regex:
            # it decides only the FIRST-named id; the others keep it as searchable body and record who they share with.
            if gid == ids[0] or sec["header"].startswith("#"):
                r["vbody"].append(body)
            if len(ids) > 1:
                r["shared"] += [x for x in ids if x != gid and x not in r["shared"]]
    recs = []
    for gid, r in sorted(by.items(), key=lambda kv: (int(GID.search(kv[0]).group(1)), kv[0])):
        body = "\n".join(r["body"])
        hdr = r["headers"][0]
        verdict, phrase, vl = classify("\n".join(r["vbody"]))
        # an explicit self-labelled verdict for THIS id ("**G-RB30 KILL (bar <= 0.90).**") outranks the first-300-chars heuristic
        # (INFO = analysis-only; 2026-10-11 B5: the 15 heuristic UNKNOWNs carry such labels in R2 "B5 ledger re-parse")
        lab = re.search(
            r"\*\*" + re.escape(gid) + r"\s+(KILL|PASS(?:ES)?|FAIL|MISS|STOP|INFO)\b[^*]{0,120}",
            body,
        )
        if lab:
            verdict, phrase = (
                NORM_VERDICT[re.sub("ES$", "", lab.group(1))],
                lab.group(0).strip("* "),
            )
        vt = "\n".join(vl)
        date = re.search(r"2026-\d\d-\d\d", "\n".join(r["headers"]) + body)
        lever = re.sub(r"^#+\s*|\*\*", "", hdr)
        lever = re.split(
            r" — (?:PRE-REGISTRATION|RUN|RESULT|STEP|SCREEN|HEAD|CONVENTION|RUNGS|VERDICT)", lever
        )[0]
        lever = re.sub(r"^-?\s*G-RB\d+[a-z]?\s*(?:[—:/-]\s*)?", "", lever).strip(" —-")
        mech = phrase
        recs.append(
            dict(
                id=gid,
                date=date.group(0) if date else None,
                lever=lever[:160],
                verdict=verdict,
                verdict_phrase=phrase[:200],
                key_numbers=list(dict.fromkeys(NUM.findall(vt)))[:8],
                mechanism=re.sub(r"\s+", " ", mech)[:240],
                n_sections=len(r["headers"]),
                shared_verdict_with=r["shared"],
                source="research/R2_GO_NOGO.md",
                _tok_header=" ".join(tokens("\n".join(r["headers"]))),
                _tok_verdict=" ".join(tokens(vt)),
                _tok_body=" ".join(tokens(body)),
            )
        )
    return recs


def query(recs, words, n=8):
    qs = [t for w in words for t in tokens(w)]
    if not qs:
        return []
    out = []
    for r in recs:
        th, tv, tb = (set(r[k].split()) for k in ("_tok_header", "_tok_verdict", "_tok_body"))
        if not all(_match(q, tb | th) for q in qs):
            continue
        score = sum(3 * _match(q, th) + 2 * _match(q, tv) + 1 for q in qs)
        out.append((score, r))
    out.sort(key=lambda x: (-x[0], int(GID.search(x[1]["id"]).group(1))))
    return [r for _, r in out[:n]]


def public(r):
    return {k: v for k, v in r.items() if not k.startswith("_")}


# ---------------------------------------------------------------- SurrealDB (fail-open) --
def surreal(sql: str, url="http://localhost:8001/sql", timeout=5):
    req = urllib.request.Request(
        url,
        data=sql.encode(),
        method="POST",
        headers={
            "surreal-ns": "cohezion",
            "surreal-db": "main",
            "Accept": "application/json",
            "Content-Type": "text/plain",
            "Authorization": "Basic " + base64.b64encode(b"root:root").decode(),
        },
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read())


def write_surreal(recs):
    """UPSERT with deterministic ids; check EVERY statement status (SurrealDB reports errors with HTTP 200); count back."""
    try:
        stmts = []
        for r in recs:
            sid = "arcwb_" + r["id"].lower().replace("-", "_")
            doc = {k: v for k, v in public(r).items() if k != "id"} | dict(
                event="arc_whitebox_gate", gate=r["id"], ts=r["date"]
            )  # record id is the key
            stmts.append(f"UPSERT experiment_runs:{sid} CONTENT {json.dumps(doc)};")
        res = surreal("\n".join(stmts))
        bad = [x for x in res if x.get("status") != "OK"]
        cnt = surreal(
            "SELECT count() FROM experiment_runs WHERE event = 'arc_whitebox_gate' GROUP ALL;"
        )
        n = (
            cnt[0]["result"][0]["count"]
            if cnt and cnt[0].get("status") == "OK" and cnt[0]["result"]
            else 0
        )
        return dict(ok=not bad and n == len(recs), statements=len(res), bad=bad[:3], count_back=n)
    except (OSError, ValueError, KeyError, IndexError) as e:
        return dict(ok=False, error=f"{type(e).__name__}: {e}")


def load():
    """Rebuild from SRC when the cache is missing, older than SRC, or lacks the query tokens (2026-10-16: a
    public-only gates.jsonl made every query crash with KeyError '_tok_header')."""
    recs = [json.loads(l) for l in OUT.read_text().splitlines()] if OUT.exists() else []
    if not recs or OUT.stat().st_mtime < SRC.stat().st_mtime or "_tok_header" not in recs[0]:
        recs = build_records(SRC.read_text())
        OUT.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in recs))
        write_surreal(recs)  # keep Cohezion's experiment_runs in step (fail-open; 2026-10-16: it held 0 ARC gates)
    return recs


def main(argv):
    if not argv or argv[0] not in ("build", "query"):
        print(__doc__)
        return 2
    if argv[0] == "build":
        recs = build_records(SRC.read_text())
        OUT.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in recs))
        nums = sorted(int(GID.search(r["id"]).group(1)) for r in recs)
        missing = [i for i in range(1, max(nums) + 1) if i not in nums]
        from collections import Counter

        print(
            f"{len(recs)} gate records -> {OUT.relative_to(HERE.parent.parent)}; verdicts {dict(Counter(r['verdict'] for r in recs))}; "
            f"missing ids {missing or 'none'}"
        )
        if "--no-surreal" not in argv:
            print("surreal:", json.dumps(write_surreal(recs)))
        return 0
    args = argv[1:]
    n = 8
    if "-n" in args:
        i = args.index("-n")
        n = int(args[i + 1])
        args = args[:i] + args[i + 2 :]
    hits = query(load(), args, n)
    for r in hits:
        print(f"{r['id']:8} {r['date'] or '?':10} {r['verdict']:7} {r['lever'][:70]}")
        print(f"         {r['mechanism'][:170]}")
    if not hits:
        print("no gate matches; nobody has run this yet (or try fewer / shorter keywords)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
