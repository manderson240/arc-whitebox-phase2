"""PROOFS.md Theorem 1 -- multilinear cumulant transport through a linear map, checked EXACTLY.

z = h W  (h row vector, W stored (in,out)).  Claim: kappa(z_{j1},...,z_{jk}) = sum_{a1..ak} W_{a1 j1}...W_{ak jk}
kappa(h_{a1},...,h_{ak}) for every k, with NO error term.

Check: h is a DEPENDENT discrete random vector on a handful of rational atoms (so every moment is an exact
Fraction), W has rational entries. Joint cumulants are computed from joint moments by the moment->cumulant
partition formula (exact), on both sides, for k = 1..4. Equality must be EXACT (Fraction == Fraction).

--perturb : replace the exact tensor rule by the "diagonal-only" rule (keep only a1=...=ak terms, i.e. the
            rule that would hold if the h_a were independent) -> must FAIL, since h is dependent here.
"""

from __future__ import annotations

import itertools
import sys
from fractions import Fraction as F


def set_partitions(items):
    if not items:
        yield []
        return
    first, rest = items[0], items[1:]
    for smaller in set_partitions(rest):
        for i, block in enumerate(smaller):
            yield smaller[:i] + [[first] + block] + smaller[i + 1 :]
        yield [[first]] + smaller


def joint_moment(atoms, probs, idx):
    return sum(p * prod(x[i] for i in idx) for x, p in zip(atoms, probs))


def prod(it):
    out = F(1)
    for v in it:
        out *= v
    return out


def joint_cumulant(atoms, probs, idx):
    """kappa(X_{idx[0]},...,X_{idx[k-1]}) = sum_pi (-1)^{|pi|-1} (|pi|-1)! prod_{B in pi} E[prod_{i in B} X_i]."""
    idx = list(idx)
    total = F(0)
    for pi in set_partitions(list(range(len(idx)))):
        m = len(pi)
        sign = (-1) ** (m - 1)
        fact = 1
        for r in range(1, m):
            fact *= r
        term = F(sign * fact)
        for block in pi:
            term *= joint_moment(atoms, probs, [idx[i] for i in block])
        total += term
    return total


def main(perturb: bool) -> int:
    # dependent 3-vector h on 5 rational atoms (probabilities sum to 1)
    atoms_h = [
        (F(1), F(2), F(-1)),
        (F(-1, 2), F(1, 3), F(2)),
        (F(3), F(-1), F(1, 4)),
        (F(0), F(1), F(1)),
        (F(-2), F(-3, 2), F(-1, 3)),
    ]
    probs = [F(1, 5), F(3, 10), F(1, 10), F(1, 4), F(3, 20)]
    assert sum(probs) == 1
    nin, nout = 3, 2
    W = [[F(1, 2), F(-3, 4)], [F(2), F(1, 3)], [F(-1, 5), F(5, 2)]]  # (in, out)
    # z atoms: z_j = sum_a h_a W_aj  (exact, atom by atom -- this is the DEFINITION of z, not the theorem)
    atoms_z = [tuple(sum(h[a] * W[a][j] for a in range(nin)) for j in range(nout)) for h in atoms_h]

    n_checked, n_bad = 0, 0
    for k in range(1, 5):
        for jidx in itertools.product(range(nout), repeat=k):
            lhs = joint_cumulant(atoms_z, probs, jidx)
            rhs = F(0)
            for aidx in itertools.product(range(nin), repeat=k):
                if perturb and len(set(aidx)) != 1:
                    continue  # diagonal-only (independent-h) rule
                w = prod(W[a][j] for a, j in zip(aidx, jidx))
                rhs += w * joint_cumulant(atoms_h, probs, aidx)
            n_checked += 1
            if lhs != rhs:
                n_bad += 1
                if n_bad <= 3:
                    print(f"  MISMATCH k={k} j={jidx}: lhs={lhs} rhs={rhs}")
    tag = "PERTURBED (diagonal-only rule)" if perturb else "exact multilinear rule"
    print(
        f"check1 [{tag}]: {n_checked} joint cumulants (k=1..4), {n_bad} mismatches -> {'FAIL' if n_bad else 'PASS'}"
    )
    return 1 if n_bad else 0


if __name__ == "__main__":
    sys.exit(main("--perturb" in sys.argv))
