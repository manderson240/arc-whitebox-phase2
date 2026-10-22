"""G-RB151 table: A2h/A2 pooled + nets improved on VALID-20 and HELD-OUT-40, controls vs G-RB143/144 A2 rows."""
import json, collections, sys
def load(p):
    R = collections.defaultdict(dict)
    for ln in open(p):
        r = json.loads(ln); R[r["arm"]][r["net"]] = r["final"]
    return R
for name, p, refp, bar_p, bar_n in (("VALID-20", "rb151/res_151_valid20.jsonl", "rb142/res_143_valid20.jsonl", 0.990, 12),
                                     ("HELD-OUT-40", "rb151/res_151_heldout.jsonl", "rb142/res_144_heldout.jsonl", 0.995, 22)):
    try: R = load(p)
    except FileNotFoundError: print(name, "missing"); continue
    ref = load(refp)["A2"]; A, H = R["A2"], R["A2h"]
    print(f"{name} control A2 vs {refp}: n={len(A)} bit-identical {all(A[n] == ref[n] for n in A)} max rel {max(abs(A[n]/ref[n]-1) for n in A):.2e}")
    ns = sorted(n for n in H if n in A)
    per = [H[n] / A[n] for n in ns]; pooled = sum(H[n] for n in ns) / sum(A[n] for n in ns); imp = sum(p < 1 for p in per)
    print(f"{name} A2h/A2 n={len(ns)} pooled {pooled:.4f} improve {imp}/{len(ns)} best {min(per):.4f} worst {max(per):.4f} -> bar <= {bar_p} with >= {bar_n}: {'PASS' if pooled <= bar_p and imp >= bar_n else 'FAIL'}")
    print(" ".join(f"{n}:{x:.4f}" for n, x in zip(ns, per)))
