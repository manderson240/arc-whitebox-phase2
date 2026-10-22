"""G-RB146: ledger-driven pricing of the DPS-2025 <4x4x4:48> scheme (289 block adds + 26 power-of-2 scalings) replacing the
TOP TWO Strassen-Winograd levels at each site of v112_sb. Inputs: the net-0 op ledger (opledger146.py). Outputs per site:
d_mm = -site_matmul_pt/49 (one of 49 equal products saved), d_glue from the actual call dims (leaf << D), wall bracket.
Billing: add/subtract/stack/multiply 1 per element, matmul 2mkn-mn, transpose 0 (flopscope 0.12.1 default_weights.json).
Wall: add/sub sweep 1.44 ns/element (G-RB137 remote attribution, strided 10-20M-element d6 views) .. 0.7 ns/element [H] for
large top-level slabs; matmul 54.5 GFLOP/s effective (rb142 v112 remote, same leaf shapes). Mapping: Amendment 1,
grader max = 89.4 (1 + 1.32 (r-1)), r = wall/49.40 s (v105 rb142)."""
import json, sys, collections
B = 2**41; PT = 100.0 / B
rows = [json.loads(l) for l in open(sys.argv[1])]
V105_WALL = 49.40
def mmu(m, k, w): return 2 * m * k * w - m * w
def site_D(a, b):
    c, m, k = a[-3], a[-2], a[-1]; w = b[-1]
    if len(a) < 3: return None
    if m == 16 and w == 16 and c == 1: return ("C", 6)            # d5 + fused d6 (all C layers)
    if m == 16 and w == 16 and c == 3: return ("M2", 5)
    if (m, k, w) == (64, 32, 32) and c == 1: return ("T2", 5)
    if (m, k, w) == (128, 32, 32) and c == 1: return ("T2x", 5)   # 4096-row T2-shaped call (first layers)
    if w == 32 and m >= 190 and k <= 32 and c == 1: return ("T", 5)
    if (m, k, w) == (24, 64, 128): return ("E2", 4)
    if (m, k, w) == (32, 12, 64): return ("F1", 5)
    if (m, k, w) == (32, 64, 12): return ("K1", 5)
    if (m, w) == (32, 64) and k == 7: return ("F0", 5)           # d4 + d6
    if (m, w) == (32, 7) and k == 64: return ("K0", 5)
    if m == 128 and k == 128: return ("E1", 3)
    return None
# Winograd glue elements for TWO top levels of a c-batch (m,k)@(k,w): A 4 adds + 3 copies on (m/2,k/2); B 4 adds + 3 copies on (k/2,w/2);
# recomb 5 adds (nested) on (m/2,w/2); level 2 is 7x of the same on halved dims.
def wino2(c, m, k, w):
    def lvl(m, k, w, lead): return lead * c * (7 * (m // 2) * (k // 2) + 7 * (k // 2) * (w // 2) + 5 * (m // 2) * (w // 2))
    return lvl(m, k, w, 1) + lvl(m // 2, k // 2, w // 2, 7)
def dps48(c, m, k, w, aA=104, aB=75, aC=110, smul=26, copies=True):
    bm, bk, bw = m // 4, k // 4, w // 4
    g = c * (aA * bm * bk + aB * bk * bw + aC * bm * bw + smul * max(bm * bk, bk * bw, bm * bw))
    if copies: g += c * 48 * (bm * bk + bk * bw)   # the 48 left/right operand slabs must exist as arrays (billed copies unless pure views)
    return g
agg = collections.defaultdict(lambda: dict(flops=0, glue_base=0.0, glue_new=0.0, glue_new_nocopy=0.0, calls=0.0))
for r in rows:
    if r["op"] != "matmul": continue
    a, b = r["shapes"]
    if len(a) < 3: continue
    s = site_D(a, b)
    if s is None: continue
    name, D = s
    c, m_l, k_l, w_l = a[-3], a[-2], a[-1], b[-1]
    m, k, w = m_l << D, k_l << D, w_l << D
    full = (7 ** D) * c * mmu(m_l, k_l, w_l)        # one full call's matmul units
    eq = r["flops"] / full                          # fraction of a call this row represents
    A = agg[name]; A["flops"] += r["flops"]; A["calls"] += eq
    A["glue_base"] += eq * wino2(c, m, k, w); A["glue_new"] += eq * dps48(c, m, k, w); A["glue_new_nocopy"] += eq * dps48(c, m, k, w, copies=False)
print("| site | matmul pt | calls | d_mm pt (-1/49) | d_glue pt (289 adds+26 smul+48 copies) | d_glue pt (operands as views) | d_util pt | d_util pt (views) | d_wall s/predict [1.44 .. 0.7 ns/el] | d_max s | E pt per max-s |")
tot = collections.Counter()
for name, A in sorted(agg.items(), key=lambda kv: -kv[1]["flops"]):
    d_mm = -A["flops"] / 49 * PT
    dg = (A["glue_new"] - A["glue_base"]) * PT; dgv = (A["glue_new_nocopy"] - A["glue_base"]) * PT
    du, duv = d_mm + dg, d_mm + dgv
    el = (A["glue_new"] - A["glue_base"])
    w_hi = el * 1.44e-9 - (A["flops"] / 49) / 54.5e9; w_lo = el * 0.7e-9 - (A["flops"] / 49) / 54.5e9
    dmax_hi = 89.4 * 1.32 * w_hi / V105_WALL; dmax_lo = 89.4 * 1.32 * w_lo / V105_WALL
    E = -du / dmax_hi if dmax_hi > 0 else float("inf")
    print(f"| {name} | {A['flops']*PT:.4f} | {A['calls']:.1f} | {d_mm:+.4f} | {dg:+.4f} | {dgv:+.4f} | {du:+.4f} | {duv:+.4f} | {w_hi:+.2f} .. {w_lo:+.2f} | {dmax_hi:+.2f} .. {dmax_lo:+.2f} | {E:.4f} |")
    tot.update(dict(d_mm=d_mm, dg=dg, du=du, duv=duv, w_hi=w_hi, w_lo=w_lo, dmax_hi=dmax_hi, dmax_lo=dmax_lo))
print(f"| ALL sites | | | {tot['d_mm']:+.4f} | {tot['dg']:+.4f} | | {tot['du']:+.4f} | {tot['duv']:+.4f} | {tot['w_hi']:+.2f} .. {tot['w_lo']:+.2f} | {tot['dmax_hi']:+.2f} .. {tot['dmax_lo']:+.2f} | {-tot['du']/tot['dmax_hi']:.4f} |")
print("\nControl: Winograd-level glue model vs ledger. Model base glue (top 2 levels only) summed:", round(sum(A['glue_base'] for A in agg.values())*PT,4), "pt; ledger add+subtract+stack =", round(sum(r['flops'] for r in rows if r['op'] in ('add','subtract','stack'))*PT,4), "pt (all levels, all sites).")
# full-depth Winograd glue model check: sum over levels 1..D of lvl(), compare with ledger glue
def winoD(c, m, k, w, D):
    g = 0
    for l in range(D):
        g += (7 ** l) * c * (7 * (m >> (l+1)) * (k >> (l+1)) + 7 * (k >> (l+1)) * (w >> (l+1)) + 5 * (m >> (l+1)) * (w >> (l+1)))
    return g
gtot = 0
for r in rows:
    if r["op"] != "matmul": continue
    a, b = r["shapes"]
    if len(a) < 3: continue
    s = site_D(a, b)
    if s is None: continue
    name, D = s; c, m_l, k_l, w_l = a[-3], a[-2], a[-1], b[-1]
    eq = r["flops"] / ((7 ** D) * c * mmu(m_l, k_l, w_l))
    gtot += eq * winoD(c, m_l << D, k_l << D, w_l << D, D)
print("Full-depth model glue (7+7 operand-side ops incl. 3 copies/side, 5 recomb adds):", round(gtot*PT,4), "pt vs ledger 1.7485 pt (add+sub+stack); concatenate/reshape excluded.")
