"""G-RB146 lever scan, offline analysis of the v112_sb op ledger (research/rb146/opledger146.py output).
Read-only research aid (opt_einsum + flopscope cost formulas), never part of an estimator.

    whest-starterkit/.venv/bin/python research/rb146/analyze146.py <ledger.jsonl> [--adds NAME=aA,aB,aC,smul ...]

Sections: A) matmul sites by leaf shape; B) glue by class + remote wall per class (rb142/wall_v112.jsonl, rb137/wall.jsonl);
C) einsum chains: flopscope-billed cost of the shipped ('auto') path vs every pairwise order (opt_einsum optimal/dp);
D) pricing of alternative bilinear schemes per Winograd site under flopscope billing (adds/stacks count 1 per element,
   matmul 2mkn-mn, transpose 0, reshape 1 per element) and the calibrated wall mapping.
"""

import collections
import itertools
import json
import sys
from pathlib import Path

import opt_einsum as oe
from flopscope._flops import einsum_cost


ROOT = Path(__file__).resolve().parents[2]
B = 2**41
PT = 100.0 / B


def pt(x):
    return x * PT


def load(p):
    return [json.loads(l) for l in open(p)]


# ---------------------------------------------------------------- A) sites
def site_of(shapes):
    """Map a Strassen leaf matmul (lead..., c, m, k) @ (lead..., c, k, w) to a site by leaf shape (SITE_COST_MAP s1 rule, v112 shapes)."""
    a, b = shapes
    if len(a) < 3:
        return "dense"
    c, m, k = a[-3], a[-2], a[-1]
    w = b[-1]
    lead = tuple(a[:-3])
    sevens = sum(1 for x in lead if x == 7)
    if lead == ():
        return "dense"
    if m == 16 and w == 16 and k >= 150 and c == 1:
        return "C(d5+d6,leaf16)"
    if m == 16 and w == 16 and c == 3:
        return "M2(d5,3-batch)"
    if (m, k, w) == (64, 32, 32) and c == 1:
        return "T2(d5)"
    if w == 32 and m >= 190 and k <= 32 and c == 1:
        return "T(d5)"
    if (m, k, w) == (24, 64, 128):
        return "E2(d4)"
    if (m, k, w) == (32, 12, 64):
        return "F1(d5,384)"
    if (m, k, w) == (32, 64, 12):
        return "K1(d5,384)"
    if (m, w) == (32, 64) and k == 7:
        return "F0(d4+d6,224)"
    if (m, w) == (32, 7) and k == 64:
        return "K0(d4+d6,224)"
    if (m, k, w) == (32, 7, 64) or (m, k, w) == (32, 64, 7):
        return "F0/K0"
    if m == 128 and k == 128:
        return "E1(d3)"
    return f"other{sevens}:{(c, m, k, w)}"


def section_a(rows):
    print("## A) matmul by site (net 0, v112_sb)")
    agg = collections.defaultdict(lambda: [0, 0, set()])
    for r in rows:
        if r["op"] != "matmul":
            continue
        s = site_of(r["shapes"])
        agg[s][0] += 1
        agg[s][1] += r["flops"]
        agg[s][2].add(tuple(map(tuple, r["shapes"])))
    tot = sum(v[1] for v in agg.values())
    out = {}
    for s, (c, f, sh) in sorted(agg.items(), key=lambda kv: -kv[1][1]):
        print(
            f"| {s:22} | n={c:5d} | {pt(f):8.4f} pt | {100 * f / tot:5.1f} % | shapes={len(sh)} |"
        )
        out[s] = (c, f, sh)
    print(f"matmul total {pt(tot):.4f} pt")
    return out


# ---------------------------------------------------------------- B) glue + wall
def section_b(rows):
    print("\n## B) glue classes (billed) and remote backend wall per class")
    agg = collections.defaultdict(lambda: [0, 0])
    for r in rows:
        agg[r["op"]][0] += 1
        agg[r["op"]][1] += r["flops"]
    for k in (
        "matmul",
        "add",
        "subtract",
        "stack",
        "concatenate",
        "reshape",
        "multiply",
        "einsum",
        "linalg.solve",
    ):
        c, f = agg[k]
        print(f"| {k:13} | n={c:5d} | {pt(f):8.4f} pt | {f:14d} billed units |")
    walls = {}
    for fn in ("rb142/wall_v112.jsonl", "rb137/wall.jsonl", "rb139/wall2.jsonl"):
        p = ROOT / "research" / fn
        if not p.exists():
            continue
        for l in open(p):
            try:
                r = json.loads(l)
            except json.JSONDecodeError:
                continue
            if not isinstance(r, dict) or "ops" not in r:
                continue
            b = r["build"].split("/")[-1]
            d = walls.setdefault((fn, b), collections.defaultdict(lambda: [0, 0.0, 0.0]))
            d["_predicts"][0] += 1
            d["_wall"][1] += r["wall_s"]
            d["_backend"][1] += r["backend_s"]
            for op, v in r["ops"].items():
                d[op][0] += v["calls"]
                d[op][1] += v["backend_s"]
                d[op][2] += v["overhead_s"]
    for (fn, b), d in walls.items():
        n = d["_predicts"][0]
        print(
            f"\n{fn} {b}: predicts={n} wall/predict={d['_wall'][1] / n:.2f} s backend/predict={d['_backend'][1] / n:.2f} s"
        )
        for op in (
            "matmul",
            "add",
            "subtract",
            "stack",
            "concatenate",
            "multiply",
            "einsum",
            "linalg.solve",
            "reshape",
            "transpose",
        ):
            if op in d:
                print(
                    f"   {op:13} calls/predict={d[op][0] / n:7.1f} backend/predict={d[op][1] / n:7.3f} s overhead={d[op][2] / n:6.3f} s"
                )
    return agg, walls


# ---------------------------------------------------------------- C) einsum paths
def flopscope_path_cost(sub, shapes, path):
    """flopscope-billed cost of a pairwise path: each step billed by einsum_cost on its own subscripts (no symmetry)."""
    ins, out = sub.split("->")
    ins = ins.split(",")
    operands = [(ins[i], tuple(shapes[i])) for i in range(len(ins))]
    total = 0
    for step in path:
        step = sorted(step, reverse=True)
        picked = [operands.pop(i) for i in step]
        labels = set("".join(s for s, _ in picked))
        remaining = set("".join(s for s, _ in operands)) | set(out)
        keep = "".join(sorted(l for l in labels if l in remaining))
        ssub = ",".join(s for s, _ in picked) + "->" + keep
        total += einsum_cost(ssub, [sh for _, sh in picked])
        sizes = {}
        for s, sh in picked:
            for l, d in zip(s, sh):
                sizes[l] = d
        operands.append((keep, tuple(sizes[l] for l in keep)))
    return total


def section_c(rows):
    print(
        "\n## C) multi-operand einsum chains: shipped billed cost vs all pairwise orders (flopscope billing)"
    )
    seen = collections.defaultdict(lambda: [0, 0])
    for r in rows:
        if r["op"] == "einsum" and r.get("sub") and r["sub"].count(",") >= 2:
            seen[(r["sub"], tuple(map(tuple, r["shapes"])))][0] += 1
            seen[(r["sub"], tuple(map(tuple, r["shapes"])))][1] += r["flops"]
    for (sub, shapes), (n, f) in sorted(seen.items(), key=lambda kv: -kv[1][1]):
        k = len(shapes)
        best = None
        allp = []
        # enumerate all pairwise contraction orders (k <= 3 here -> 3 orders; k=4 -> 18)
        for order in itertools.permutations(range(k)):
            pass
        orders = []
        if k == 3:
            orders = [[(0, 1), (0, 1)], [(0, 2), (0, 1)], [(1, 2), (0, 1)]]
        for p in orders:
            c = flopscope_path_cost(sub, shapes, p)
            allp.append((c, p))
        allp.sort()
        import numpy as np

        dummies = [np.empty(s) for s in shapes]
        p_opt, _ = oe.contract_path(sub, *dummies, optimize="optimal")
        p_dp, _ = oe.contract_path(sub, *dummies, optimize="dp")
        c_opt = flopscope_path_cost(sub, shapes, p_opt)
        c_dp = flopscope_path_cost(sub, shapes, p_dp)
        naive = einsum_cost(sub, [tuple(s) for s in shapes])
        shipped = f / n
        print(f"\n{sub} {shapes} x{n}: shipped/call {pt(shipped):.5f} pt ({shipped:,} units)")
        print(
            f"   naive single-pass {pt(naive):.5f} pt | opt_einsum optimal {p_opt} -> {pt(c_opt):.5f} | dp {p_dp} -> {pt(c_dp):.5f}"
        )
        for c, p in allp:
            print(f"   order {p}: {pt(c):.5f} pt {'<-- cheapest' if c == allp[0][0] else ''}")
        gain = shipped - allp[0][0] if allp else shipped - min(c_opt, c_dp, naive)
        print(f"   possible saving vs shipped: {pt(gain) * n:.5f} pt over {n} calls")


# ---------------------------------------------------------------- D) scheme pricing
def winograd_level_elems(m, k, w, c, lead, nested_recomb=5, qa=False):
    """Element-ops billed by ONE Strassen-Winograd level on a (lead*c) batch of (m,k)@(k,w) products: 4 A-adds on (m/2,k/2),
    4 B-adds on (k/2,w/2), 3+3 plain-quadrant stack copies, recomb adds on (m/2,w/2). Returns (adds, stacks) in elements."""
    a = (
        lead
        * c
        * (4 * (m // 2) * (k // 2) + 4 * (k // 2) * (w // 2) + nested_recomb * (m // 2) * (w // 2))
    )
    s = lead * c * ((0 if qa else 3) * (m // 2) * (k // 2) + 3 * (k // 2) * (w // 2))
    return a, s


def mm_units(m, k, w):
    return 2 * m * k * w - m * w


def price_site(name, c, m, k, w, d, ncalls, schemes, rate_ns_elem, mm_gflops):
    """Price replacing the TOP TWO Winograd levels of a depth-d site by a (p,p,p) scheme of rank R with aA/aB/aC block
    additions and smul scalar multiplies, keeping the remaining d-2 Winograd levels under each of the R products.
    Winograd 2 levels: 49 products of (m/4,k/4,w/4) each then d-2 more levels. Scheme: R products of (m/p,k/p,w/p)."""
    out = []
    # shipped: two Winograd levels
    base_mm = 49 * (7 ** (d - 2)) * c * mm_units(m >> d, k >> d, w >> d)
    a1, s1 = winograd_level_elems(m, k, w, c, 1)
    a2, s2 = winograd_level_elems(m // 2, k // 2, w // 2, c, 7)
    base_glue = a1 + s1 + a2 + s2
    for sc in schemes:
        p, R, aA, aB, aC, smul = sc["p"], sc["R"], sc["aA"], sc["aB"], sc["aC"], sc["smul"]
        if m % p or k % p or w % p:
            out.append((sc["name"], "shape not divisible by %d" % p))
            continue
        # the R products inherit the SAME remaining d-2 Winograd levels only if the block dims are those of two halvings (p=4)
        if p == 4:
            new_mm = R * (7 ** (d - 2)) * c * mm_units(m >> d, k >> d, w >> d)
        else:  # p=3 etc: blocks (m/3,...) keep d-2 Winograd levels (needs divisibility by 2^(d-2) too)
            if (m // p) % (2 ** (d - 2)) or (k // p) % (2 ** (d - 2)) or (w // p) % (2 ** (d - 2)):
                out.append((sc["name"], "blocks not divisible by 2^(d-2)"))
                continue
            new_mm = (
                R
                * (7 ** (d - 2))
                * c
                * mm_units((m // p) >> (d - 2), (k // p) >> (d - 2), (w // p) >> (d - 2))
            )
        bm, bk, bw = m // p, k // p, w // p
        new_glue = c * (
            aA * bm * bk + aB * bk * bw + aC * bm * bw + smul * (bm * bk + bk * bw) // 2
        )
        new_glue += c * (
            R * bm * bk + R * bk * bw
        )  # stacking the R left/right operands (billed copies; 0 only if every operand is a view)
        d_util = (new_mm - base_mm) + (new_glue - base_glue)
        d_mm_pt, d_glue_pt = pt(new_mm - base_mm) * ncalls, pt(new_glue - base_glue) * ncalls
        # wall: glue at rate_ns_elem per element; matmul at mm_gflops effective (same leaf shape -> same rate)
        d_wall = ncalls * (
            (new_glue - base_glue) * rate_ns_elem * 1e-9 + (new_mm - base_mm) / (mm_gflops * 1e9)
        )
        out.append(
            (
                sc["name"],
                dict(
                    d_mm_pt=d_mm_pt,
                    d_glue_pt=d_glue_pt,
                    d_util_pt=d_mm_pt + d_glue_pt,
                    d_wall_s=d_wall,
                ),
            )
        )
    return out


def main():
    rows = load(sys.argv[1])
    schemes = [
        # name, block split p, rank R, block additions (A side, B side, C side), scalar multiplies -- filled from the literature fetch
        dict(
            name="Winograd^2 (shipped, 49, 15+7x15 adds, 5-add nested recomb)",
            p=4,
            R=49,
            aA=4 + 7 * 4,
            aB=4 + 7 * 4,
            aC=5 + 7 * 5,
            smul=0,
        ),
        dict(
            name="Strassen^2 (49, 18+7x18 adds)",
            p=4,
            R=49,
            aA=5 + 7 * 5,
            aB=5 + 7 * 5,
            aC=8 + 7 * 8,
            smul=0,
        ),
    ]
    for arg in sys.argv[2:]:
        if arg.startswith("--adds"):
            continue
        nm, vals = arg.split("=")
        p, R, aA, aB, aC, smul = [int(x) for x in vals.split(",")]
        schemes.append(dict(name=nm, p=p, R=R, aA=aA, aB=aB, aC=aC, smul=smul))
    sites = section_a(rows)
    agg, walls = section_b(rows)
    section_c(rows)
    print(
        "\n## D) pricing alternative schemes on the top two levels of each Winograd site (flopscope billing)"
    )
    # wall constants (G-RB137 remote attribution): add+sub +33.5 s over 4 predicts for +5.8e9 add/sub elements/predict
    rate_ns_elem = 33.5 / 4 / 5.8e9 * 1e9
    mm_gflops = 3.46e11 / 6.0 / 1e9  # placeholder, overwritten below from rb142 if present
    for (fn, b), d in walls.items():
        if b == "v112_sb":
            n = d["_predicts"][0]
            mm_s = d["matmul"][1] / n
            mm_flops = agg["matmul"][1]
            mm_gflops = mm_flops / mm_s / 1e9
            print(
                f"wall constants: add/sub sweep {rate_ns_elem:.2f} ns/element (G-RB137); v112 matmul {mm_s:.2f} s/predict for {mm_flops:.3e} billed -> {mm_gflops:.1f} GFLOP/s effective"
            )
    # site specs (c, m, k, w, d, ncalls) from the ledger shapes: top level dims = leaf << d
    specs = {
        "C(d5+d6,leaf16)": (
            1,
            1024,
            10880,
            1024,
            5,
            14,
        ),  # d5 nest + fused d6 level; k = 170*64 at net 0 layer 14 (varies by layer)
        "T(d5)": (1, 8800, 864, 1024, 5, 14),  # m = 275*32, k = 27*32 (varies)
        "T2(d5)": (1, 2048, 1024, 1024, 5, 13),
        "M2(d5,3-batch)": (3, 512, 1024, 512, 5, 15),
        "F1(d5,384)": (2, 1024, 384, 2048, 5, 9),
        "K1(d5,384)": (2, 1024, 2048, 384, 5, 8),
        "F0(d4+d6,224)": (7, 512, 224, 2048, 4, 1),
        "K0(d4+d6,224)": (7, 512, 2048, 224, 4, 1),
        "E2(d4)": (1, 384, 1024, 2048, 4, 10),
    }
    for name, (c, m, k, w, d, nc) in specs.items():
        print(
            f"\n### {name}: c={c} ({m} x {k}) @ ({k} x {w}) depth {d}, ~{nc} calls/net (dims of ONE representative call)"
        )
        for nm, res in price_site(name, c, m, k, w, d, nc, schemes, rate_ns_elem, mm_gflops):
            if isinstance(res, str):
                print(f"   {nm}: {res}")
            else:
                print(
                    f"   {nm}: d_mm {res['d_mm_pt']:+.4f} pt, d_glue {res['d_glue_pt']:+.4f} pt, d_util {res['d_util_pt']:+.4f} pt, d_wall {res['d_wall_s']:+.3f} s/predict"
                )


if __name__ == "__main__":
    main()
