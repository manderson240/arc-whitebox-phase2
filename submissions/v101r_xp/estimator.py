"""v101_xp (G-RB122) = v100_xs + M2's fused extra exact level (_D6_SITES = T2, M2), funded by op-count cuts in _d6_level: the qa
quadrants X12 | X22 (right column half of the level-4 A stack) run as ONE batched pair through a cached row-nested view of that role
(rows split at the fixed m>>5; one reshape per site, built once), X11 alone (27 -> 18 ops per X phase); on T2 / M2 ONE d6 B side for
all 7 leaf slots in A13 behind their Pall (8 -> 4 ops). Same products, same recombination order (G-RB77).
v100_xs (G-RB121) = v99_rm with EXACT extra Strassen-Winograd levels on two more sites (f64 path vs v99: final-layer max|dev|/max|ref|
2.6e-15 / 3.0e-15 on FIT nets 0 / 2): (1) T2 gets v98's fused d6 level (_attach_d6: the C site's scratch placement sized from T2's own roles,
no arena growth); (2) the T site (rows vary per layer) gets a CHUNKED d6 level (_d6_chunked): it runs without the qa trick, B side once for
all 7 depth-5 leaf slots, then two slot groups (4 + 3) of A stack / 7 products / recombination into the plain leaf, scratch in B13 behind
st5B and in st4A's dead home; T's inner dim (prune_K) is rounded to a multiple of 64 and an odd 224-group count adds 32 exact-zero rows
(both exact: zero columns / rows). Net 0: util 20.546734 -> 20.129419 (-2.03 %), ops 14841 -> 15765, in-process residual +28 ms vs v99
(M1/M2 d6 measured and left out: worst util per ms).
v99_rm (G-RB118) = v98_fd with OUTPUT-IDENTICAL op-count / residual cuts (f32 predict bit-identical to v98 on FIT nets 0 and 2):
(1) nested-quadrant up views on the fixed-output-shape Strassen sites (C incl. its d6 level, M1, M2, T2, E1a/E1b/E2, F0/F1, K0/K1): each
role's arena view is built once in a (2,)*e row / col bit-split shape (same element count, same reshape bill), so a quadrant pair is a basic
index and the Winograd recombination runs as 5 adds instead of 7 (same operand pairs, same order); the arithmetic stack slots are permuted
[S2,S3,S1,S4] / [T2,T3,T1] so the paired products are adjacent; (2) nested B stacks on the fixed (k, w) sites: [T1, T3] in one subtract;
(3) _read_stack's LP/LA updates paired on the adjacent Pz/Az arena slots; (4) the closure's six sector matmul+einsum pairs batched in two halves;
(5) carried transposed copies dropped (Ct = C's transposed view, oFPAt = oFPA's), cov_pre's n^2 copy and the TZ _fill copy dropped
(they pay for the level-1 nested reshapes; util below v98); (6) _down / up operand views cached per (level, shape); (7) the T site (rows vary
per layer) nests only its columns: 6 adds. Net 0: ops 16545 -> 14841, util 20.546760 -> 20.546734.
v98_fd (G-RB115) = v97_dl with the extra Winograd level (d6) FUSED across the 7 depth-5 leaf slots (one B side per slot group,
batched matmuls, ONE recombination: ~48 python ops per layer instead of v97's 140) and applied on every layer with a C call.
v97_dl = v95_khs + d6 on the C call of layers 10-14. (i) G-RB77 fsc: with the prune active, the two unprunable row blocks (newest A, Sigma_h) leave opT and run on their own depth-5 site T2 at the full inner n (no complement matmul) -- on top of v77_fuse = v59_p05 with OUTPUT-IDENTICAL residual-time (Python wall) reductions (G-RB77): (A) the Strassen operand stacks' plain quadrants are
written by one stack(out=) instead of concatenate of three [None] views; (B) the four >= 32 MB per-layer temporaries (opT, its warm-column take, the
contraction left factor, the old-tier LPA stacks) are written with out= into two shared persistent buffers (the glibc mmap/munmap path cost
~6 ms per GB of such temporaries freed in predict's frame; 16-21 MB temporaries measured free); (C) exact elementwise fusions: Hermite
recursion coefficients as one (5,n) stack, the closure's U / V operand tensors by one stack + reshape each, and fill_diagonal(X, 0.0) in place
of X - diag(diag(X)) on fresh temporaries. No arithmetic re-association anywhere: f64 twin bit-for-bit vs v59_p05.
v59_p05 = v58_ne + fire-rate pruning of the carried kappa3 legs at p* = _PRUNE (G-RB59/61 arm A1; port G-RB70): the AGED legs
(yP/yA/yT/oQ/oT and the aged-source term of That) use the pruned gate Phi*[Phi >= p*]; the birth keeps the unpruned gate (prototype
srcchain_aug.py: A1 = f1 o C_z with f1 taken before the prune). The merged transport then runs with inner dimension K = warm count rounded
up to 32 (cdf-descending order; padded rows are exact zeros) and the two full-K blocks (newest A, Sigma_h) get their cold-column part from one
plain matmul. _PRUNE = 0 -> v58_ne bit-for-bit (same calls).
v58_ne = v58_qa + ['gram', 'ne', 'nopad'] (G-RB53/57). v58_qa = v57_azs + ['qa'] (G-RB53). v57_azs = v55_y2q3 with memory-safety edits ['az', 'azs'] (G-RB52: grader worker peak 8120 of 8192 MiB). v51_sscf = v49_age6k4 + a FREE-TRANSPORT SSC response closure for kappa4 (G-RB34; Team Puffi #327725 write-up, eqs 2/3/C3, credit theirs; modes {diag(m_i), Sigma_z, Q_free}, Q_free built only from quantities the chain already transports: Tz, mu_pre and three n^2 matvecs -- no extra n^3 work; Lambda (16,3,3) and c (16,4) fitted on our OWN MC nets 9000/9001 only; the MIX2 head refit on this chain; f64 VALID-20 vs lean+shipped head 0.968). v50_ssc = v49_age6k4 + the SSC response closure for kappa4 (Team Puffi #327725 write-up, eqs 2/3/C2/C3, credit theirs; our fit on own MC nets 9000/9001 only; G-RB33): kappa4_z = sum_ab Lam_ab S(B_a,B_b) over modes {diag(m_i), Sigma_z, B4, Q} transported from the previous ReLU; replaces the lean g var^2 / GSM sectors in the closure and the mean readout (f64 VALID-20 vs lean: 0.861, 20/20 improve). v49_age6k4 = v49_age6 + _KH 4 (G-RB24 raw-neutral mini-ratchet). v49_age6 = v48_fk5 with five young sources (_AGE_OLD 6; the 384 group holds ages 6-7) and the old-basis transport back in its own depth-4 call for memory (G-RB24). v48_a3 = v48_a2 + the 384-group formation/contraction sites at depth 5 (G-RB22 A3). v48_a2 = v48_a1 + every transport of the layer (young legs and old bases) in ONE depth-5 call (G-RB22 A2). v48_a1 = v47_fk4 with the merged contraction in ONE depth-5 call (G-RB22 A1; memory bar relaxed to the grader's 8 GB RLIMIT_AS, eval_mem <= 6.3 GB). v47_fk4 = v47_ops + the 224-group formation/contraction sites at Strassen depth 4. v47_ops = v46_y5m with the Strassen operand stacks' plain quadrants written by one concatenate (G-RB20: 17 python ops per level instead of 21, bit-identical). v46_y5m = v44_noI with a COST redesign of the young tier and the arenas (G-RB19, research/R2_GO_NOGO.md; output-identical: f64 copy
rel dev 1.6e-15 vs v44, f32 final rel dev 6e-7). (A) the Hadamard read stack runs on exactly the live sources (no zero padding to 5/10/15);
(B) the read stack keeps seven (S,n,n) buffers instead of twelve and the closure's (K,6,n,n)/(K,5,n,n) temporaries are gone (VmPeak -0.9 GB),
which pays for (D) young transport Strassen depth 5 in the transposed form [P|A]^T @ w (level-5 arena roles, B stack formed before A at level 5);
(C) ONE contraction per layer for every source, young and old ([LP|LA|acc_all] @ [PAh^T; w; Qz_all^T], the old A sites are gone) at depth 5
in two k-halves, ONE transport of every old basis (wT @ [Q_b ...]), 384-group formation/contraction at depth 4, the merged Q transport at depth 4;
and the Strassen-Winograd operand/recombination formulas (15 additions per level). Net 0: util 0.2443 (v44 0.2641), ops 14657 (13639), VmPeak 4.9 GB (5.4).
v44_noI = v43_bud4 with the identity block dropped from the young transport (G-RB17: the newest young source has P = I at
every transport, so its Pz is wT; T operand width (2k-1)n, C right factor [PAh^T; w]). Output-identical up to f32 rounding.
v43_bud4 = v42_g92 with two constants changed (research/rebuild/BUDGET_V41.md): _RK 16 -> 4 (D21 legs + adjustment residual rank), _SW_DEPTH_OLD_G (3,2) -> (3,3). v42_g92 = v41_d3 with the g table x 0.92 (weights.npz) and the MIX2 corrector REFIT on that chain (lc_weights.npz; FIT-only fit, VALID checkpoint; G-RB16, chain src92). v41_d3 = v40_nest with Strassen depth 3 on the four batched sites of the rank-224 old group only (G-RB15); the 384 group stays at d=2.
v40_nest = v31_y4m + a NESTED old tier (G-RB12): sources older than _AGE_OLD2 transports move from their own rank-384 basis into a
rank-_R_OLD2 sub-basis of it (top eigenvectors of the CURRENT legs: Q_b = U R, eigh(R F F^T R^T), Q_b <- U V2, F <- V2^T R F). The prose rank law
(team 504aldo, thread 18218 S2.4: "7n/32 at age 7") measured in our own-basis form on FIT nets 0/2/4 (research/rebuild/results.jsonl tag rb12).
Two batched old groups (384 / _R_OLD2) share the Hadamard assembly; only the Q transport / formation / contraction / basis-read sites are split.
v31_y4m = v29_y4 with the leaf arena aliased onto A13 (valid for every depth except 3: st3 is dead once st4 exists, st1 once st2 exists) and up4 moved to B2u2 (G-RB11 memory trim, -171 MB of arenas, output-identical). v29_y4 = v28_old2 with young Strassen depth 4 (G-RB11). v28_old2 = v26_mem with the old-tier Strassen depth 2 (G-RB9). v26_mem = v25_swlc with the pools shrunk for the worker's 8 GB RLIMIT_AS (G-RB8): ONE read-stack buffer set at S=15 sliced per
layer (was three sets, 5/10/15), and the Strassen scratch (down stacks, leaf, upper recombinations) shared across all six sites through
flat arenas with aliasing by liveness; only each site's result buffer is private. Outputs bit-identical to v25. v25_swlc = v24_swold + corrector strength 1.2 (G-RB5). v24_swold = v21_rb + batched Strassen on EVERY large product via a view-pool kernel (G-RB7): young sites at depth 3 (incl. the
growth layers), old-tier Q transport / leg formation / contraction / basis read at depth 1. v21_rb (2026-10-06, research/R2_GO_NOGO.md "G-RB3"): clean-room rebuild of the public K=3 family, ported to flopscope.

Algorithm (research/rebuild/DESIGN.md; f64 oracle research/rebuild/srcchain.py): ARC's factorized K=3 cumulant propagation
(Wu et al. 2026, arXiv:2605.05179, App. S.4.3 -- factored kappa3 tensor F(A,B,C), eq (16) slice reads, step (d)ii coincident-entry
adjustment) with the three accuracy steps team 504aldo DESCRIBED in forum thread 18218 (memoryless kappa4 core feeding kappa3
through the (2,1,1) vertex; D21 feedback into the birth factors, carried at rank 16; exact final-layer trim), and their cost
structure re-derived from the prose: every source = sum_j Sym(alpha P_j x X_j x Y_j) with legs in {P, A, thin}, so one source
costs 2 transports + 2 contractions per layer ("7 -> 4 units"); sources older than 4 transports live in a per-source rank-384 basis.
Credit: 504aldo (thread 18218) for the accuracy steps and the cost ideas; ARC for the representation. No participant code was read.
Our own: the n x n ReLU closure (bivariate Hermite/Edgeworth series, from v5b..v11), the fitted per-layer kappa4 scale g_l
(16 constants) and the K31 slope kappa_l (16 constants, own nets 9000/9001; sets only the feed amplitude).

Per layer l (W maps h_{l-1} -> z_l = W^T h):
  young sources (age 1..4; stacks (k,n,n)):  Pz = W^T P, Az = W^T A, thin legs W^T [T1 T2 Z u]  (n x 49 per source)
  old sources (age >= 5; own basis Q_b n x 384, static coefficients F_P, F_A 384 x n):  Qz = W^T Q_b, Pz = Qz F_P, Az = Qz F_A
  read (eq 16 regrouped by right factor):  Tz = sum_b LP_b Pz_b^T + LA_b Az_b^T + thin,  LP/LA = sums of Hadamard products of the
     block legs (DESIGN.md S2/S3); old sources contract into the basis: (LP_b F_P^T + LA_b F_A^T) Qz_b^T.
  closure: the v11 n x n ReLU step (mu, Sigma, T_h) with Tz as the kappa3 (2,1)-slice (diag = kappa3 diagonal) and GSM kappa4 sectors.
  age: every carried leg h = Phi o z.   birth: P = I, A = Phi o C_z, D21 ~ U B (rank 16, randomized range finder, Omega = columns
     of W), T1 = Phi o B^T, T2 = f2 o U, u = (kappa_l / 6) f2, adjustment leg Vadj = 3 Delta21^T + diag(Delta3) ~ A d(t) + diag(s) + Z c5.
  last layer: transports + the (3)-diagonal only; mu_out = m1 + kappa3/6 f3 + kappa4/24 f4.
Only flopscope / flopscope.numpy and the standard library are used; no host unwrap of array values in predict(); every branch is on
shapes or host integers (layer index, source ages).
"""

from __future__ import annotations

from pathlib import Path

import flopscope
import flopscope as flops
import flopscope.numpy as fnp
from whestbench import BaseEstimator, SetupContext
from whestbench.domain import MLP


WEIGHTS_FILE = "weights.npz"
LC_FILE = "lc_weights.npz"  # optional frozen learned mean-drift corrector (S4; absent -> chain unchanged)
_LC_L0 = 4  # first corrected layer (M2 trained on layers 4..14); layer 15 uses the LITE head
_LC_SCALE = 1.2  # corrector strength: G-RB5 VALID scan (20 nets, paired) 0.9/1.0/1.1/1.2/1.3 -> 1.0105/1/0.9939/0.9929/0.9968, s* = 1.17
_CAL_WIDTH, _CAL_DEPTH = 1024, 16
_PRUNE = 0.02  # G-RB59/61: kappa3 legs of neurons with gate probability Phi < _PRUNE are dropped at the ageing step (0 = off)
_RK = 2  # BUDGET_V41.md: was 16; rank of the D21 feedback legs and of the adjustment residual
_OS = 8  # range-finder oversampling
_R_OLD = 384  # per-source basis rank for sources older than _AGE_OLD transports
_AGE_OLD = 6  # G-RB24: five young sources (f64 ablation age6 -2.4 % raw; port screen -5.1 % raw for +0.68 pt)
_R_OLD2 = 224  # G-RB12: nested sub-basis rank for sources older than _AGE_OLD2 transports (prose law 7n/32)
_AGE_OLD2 = 8  # G-RB12 f64 rows: 8:224 -0.5/-1.1/+1.9 % raw on nets 0/2/4 (7:224 +3.0/+2.6/+4.6; 7:192 +6.7/+9.0/+8.7)
_KH = 4  # G-RB24: Hermite orders 8 -> 4 (port screen raw +0.01 %, util -0.13 pt, ops -300; the series is converged at 4 for these correlations); bivariate Hermite orders kept (v5b..v11)
_KGC = _KH + 4
_NS = 6
_K1 = (0, 1, 3)
_DTYPE = fnp.float32
_ZERO_MASK_TABLE = [
    [0.0 if (k == 0 and s in _K1) else 1.0 for s in range(_NS)] for k in range(_KH + 1)
]


class Weights(flopscope.Module):
    """g: per-layer excess-kurtosis scale (kappa4 = g var^2, our v5b..v11 table); kappa: per-layer K31/C slope (feed amplitude)."""

    def __init__(self) -> None:
        self.g = fnp.zeros((_CAL_DEPTH,), dtype=fnp.float32)
        self.kappa = fnp.zeros((_CAL_DEPTH,), dtype=fnp.float32)
        # G-RB33 (v50): SSC response closure (Team Puffi, submission #327725 write-up, eqs 2/3/C2/C3; credit theirs). kappa4 of z is regenerated
        # every layer as sum_ab Lam_ab S(B_a, B_b) over four live modes B = {diag(m_i), Sigma_z, B4 = gate-response, Q = fitted quadratic form}
        # transported from the previous ReLU. lam (16,4,4) and qc (16,6) were fitted by ridge on our OWN MC nets 9000/9001 only (never FIT/VALID/TEST).
        self.lam = fnp.zeros((_CAL_DEPTH, 3, 3), dtype=fnp.float32)  # v51: modes {diag(m_i), Sigma_z, Q_free}
        self.qc = fnp.zeros((_CAL_DEPTH, 4), dtype=fnp.float32)  # v51: Q_free = P_off[c0/2 mbar (Tz+Tz^T) + c1 (tz mu^T + mu tz^T) + c2 vz vz^T + c3 (w^T 1)(w^T 1)^T] / vbar


class LCWeights(flopscope.Module):
    """MIX2 corrector in the v10/v11 layout (research/lc/export_v21.py): M2 on layers 4..14 (21 raw per-neuron columns -> 32 -> 32 -> 1)
    and a 7-column LITE head at layer 15 (-> 16 -> 1); per-layer constants (g_l, l/15) folded into `bias` (16, 32) / `hbias` (16,);
    the per-layer neuron-means of five columns enter through `wm`; standardisation and the output scale are folded."""

    def __init__(self) -> None:
        self.wr = fnp.zeros((21, 32), dtype=fnp.float32)
        self.wm = fnp.zeros((21, 32), dtype=fnp.float32)
        self.bias = fnp.zeros((_CAL_DEPTH, 32), dtype=fnp.float32)
        self.w1 = fnp.zeros((32, 32), dtype=fnp.float32)
        self.b1 = fnp.zeros((32,), dtype=fnp.float32)
        self.w2 = fnp.zeros((32,), dtype=fnp.float32)
        self.b2 = fnp.zeros((1,), dtype=fnp.float32)
        self.hw = fnp.zeros((7, 16), dtype=fnp.float32)
        self.hbias = fnp.zeros((16,), dtype=fnp.float32)
        self.hw1 = fnp.zeros((16,), dtype=fnp.float32)
        self.hb1 = fnp.zeros((1,), dtype=fnp.float32)


# Batched classic Strassen (7 products) with pooled out= buffers (our v11_sw kernel; must be self-contained)
def _buf(pool, shape, dt):
    key = (shape, str(dt))
    b = pool.get(key)
    if b is None:
        b = pool[key] = fnp.empty(tuple(x for x in shape if isinstance(x, int)), dtype=dt)
    return b


# ---- v24 kernel (research/rebuild/sw4.py, G-RB7): batched classic Strassen with per-site max-shape pools; every write is
# out= into a slice view, so one buffer set serves all batch sizes / widths (no per-shape pools -> no 8 GB OOM, no padding FLOPs).


_SW_GROUP = {  # scratch roles that are never live at the same time share one flat arena (st1 dead before st3 is written, st2 dead
    ("st", "A", 1): "A13", ("st", "A", 3): "A13", ("st", "B", 1): "B13", ("st", "B", 3): "B13",  # before up3, ...)
    ("st", "A", 2): "A2u3", ("up", 3): "A2u3", ("st", "B", 2): "B2u2", ("up", 2): "B2u2", ("leaf",): "leaf",
    ("st", "A", 4): "A2u3", ("st", "B", 4): "B2u2", ("up", 4): "B2u2",  # depth 4: st4 is written after st2 died; up4 after st4B died (leaf lives in A13, see _group)
    # v46 (G-RB19 D), depth 5 with the B stack formed BEFORE the A stack at level 5 (sw_matmul): st5B -> B13 (st1B/st3B dead), then st5A -> B2u2
    # (st4B just died, up2/up4 not yet written), leaf -> A13 (st3A dead; st5A/st5B live elsewhere), up5 -> A2u3 (st4A dead), up4 -> B2u2 (st5A dead)
    ("st", "A", 5): "B2u2", ("st", "B", 5): "B13", ("up", 5): "A2u3",
}


class SWArenas:
    """Flat per-group scratch arenas sized to the largest requester; each (site, role) gets a cached reshaped view (reshape once)."""

    def __init__(self, dt):
        self.dt, self.cap, self.buf, self.views = dt, {}, {}, {}

    def reserve(self, group, nelems):
        self.cap[group] = max(self.cap.get(group, 0), nelems)

    def view(self, group, key, shape):
        v = self.views.get((group, key))
        if v is None:
            b = self.buf.get(group)
            if b is None:
                b = self.buf[group] = fnp.empty((self.cap[group],), dtype=self.dt)
            n = 1
            for x in shape:
                n *= x
            v = self.views[(group, key)] = b[:n].reshape(shape)
        return v


class SWSite:
    """One Strassen call site: max shapes (ca, m, k) x (cb, k, w) at depth d; scratch comes from the shared arenas, the result
    buffer (level-1 recombination) is private so it survives until the site's next call."""

    def __init__(self, name, ca, cb, m, k, w, d, dt, arenas, nest=False):
        self.name, self.d, self.dt, self.arenas = name, d, dt, arenas
        self.max = (ca, cb, m, k, w)
        self.bufs = {}
        self.nest, self.nv = nest, {}  # v99 (G-RB118): nested-quadrant up views (fixed (m, w) sites only), cached per (level, c)
        self.nestB = False
        self.d6nest = False  # v99: set on the C site (d6 always runs there)
        self.colnest = False  # v99: T site -- rows vary per layer, so only the COLUMNS are nested (6-add recombination)
        self.dc = {}  # v99: _down operand views per (side, level >= 2, input shape) -- the input is then this site's own stack view  # v99 (G-RB118): nested B stacks (fixed (k, w) sites): T1/T3 in one subtract at levels with a nested input
        self.roles = self._roles()  # v46: computed once (was rebuilt on every stack/leaf/up view)
        for key, smax in self.roles.items():
            if key != ("up", 1):
                n = 1
                for x in smax:
                    n *= x
                arenas.reserve(self._group(key), n)

    def _roles(self):
        ca, cb, m, k, w, d = self.max + (self.d,)
        r = {}
        for lvl in range(1, d + 1):
            r[("st", "A", lvl)] = (7,) * lvl + (ca, m >> lvl, k >> lvl)
            r[("st", "B", lvl)] = (7,) * lvl + (cb, k >> lvl, w >> lvl)
            r[("up", lvl)] = (7,) * (lvl - 1) + (max(ca, cb), m >> (lvl - 1), w >> (lvl - 1))
        r[("leaf",)] = (7,) * d + (max(ca, cb), m >> d, w >> d)
        return r

    def _group(self, key):
        # v31: the leaf is computed from st_d, so st_{d-1} is dead -> alias A13 (st1/st3) unless d == 3 (st3 live while the leaf is written)
        if key == ("leaf",):
            # v41 (G-RB15): at d == 3 the leaf is computed from st3 (A13/B13 live) but st2B is dead and up2 is not yet written -> B2u2 is free
            return "A13" if self.d != 3 else "B2u2"
        return _SW_GROUP[key]

    def _buf(self, key, shape_max):
        if key == ("up", 1):
            b = self.bufs.get(key)
            if b is None:
                b = self.bufs[key] = fnp.empty(shape_max, dtype=self.dt)
            return b
        return self.arenas.view(self._group(key), (self.name,) + key, shape_max)

    def stack_view(self, side, lvl, lead, h, kk):
        b = self._buf(("st", side, lvl), self.roles[("st", side, lvl)])
        return b[(slice(None),) * lvl + (slice(0, lead[-1]), slice(0, h), slice(0, kk))]

    def leaf_view(self, lead, h, w):
        d = self.d
        b = self._buf(("leaf",), self.roles[("leaf",)])
        return b[(slice(None),) * d + (slice(0, lead[-1]), slice(0, h), slice(0, w))]

    def up_view(self, lvl, lead, h2, w2):
        b = self._buf(("up", lvl), self.roles[("up", lvl)])
        return b[(slice(None),) * (lvl - 1) + (slice(0, lead[-1]), slice(0, h2), slice(0, w2))]

    def xpair(self, c, k5):
        """v101 (G-RB122): [X12, X22] of the level-(d-1) A stack (the qa quadrants of slots 5 / 6) as ONE (2,) + lead + (m>>d, k5) view:
        the role's arena memory viewed with its rows split at the fixed m>>d (one reshape per site, cached; the plain role view is
        unchanged), then the right column half of the CALL (k5 = this call's level-d inner width) and the row-pair axis moved to the front."""
        key = ("xp", c, k5)
        v = self.nv.get(key)
        if v is None:
            ca, cb, m, k, w = self.max
            d = self.d
            role = self.roles[("st", "A", d - 1)]
            assert role[-2] == m >> (d - 1), (self.name, role)
            N = self.arenas.view(self._group(("st", "A", d - 1)), (self.name, "stAr", d - 1), role[:-2] + (2, m >> d, role[-1]))
            v = self.nv[key] = fnp.moveaxis(N[(slice(None),) * (d - 1) + (slice(0, c), slice(None), slice(None), slice(k5, 2 * k5))], -3, 0)
        return v

    def stBn(self, lvl):
        """v99: the level-lvl B stack viewed nested, (7,)*lvl + (cb,) + (2,)*e + (k>>d,) + (2,)*e + (w>>d,), e = d - lvl (replaces the plain
        view of the role; same element count, same reshape bill). Its quadrants have exactly the shape of the next level's slots."""
        ca, cb, m, k, w = self.max
        d, e = self.d, self.d - lvl
        shp = (7,) * lvl + (cb,) + (2,) * e + (k >> d,) + (2,) * e + (w >> d,)
        return self.arenas.view(self._group(("st", "B", lvl)), (self.name, "stBn", lvl), shp)

    def nest_down_B(self, lvl, c, Xn=None):
        """v99: cached operand views of the B side of level lvl on a nested input X (the level-(lvl-1) nested stack, or at level 1 a
        persistent nested input Xn): [T1, T3] = [B12, B22] - [B11, B12] in ONE subtract, then T2, T4 and the plain-quadrant stack."""
        key = ("dB", lvl, c)
        v = self.nv.get(key)
        if v is None:
            e = self.d - lvl
            X = Xn[:c] if lvl == 1 else self.stBn(lvl - 1)[(slice(None),) * (lvl - 1) + (slice(0, c),)]
            S = self.stBn(lvl)[(slice(None),) * lvl + (slice(0, c),)]
            ra, cax = lvl, lvl + e + 2

            def ix(i, j):
                t = [slice(None)] * X.ndim
                t[ra], t[cax] = i, j
                return tuple(t)

            X11, X21, X22 = X[ix(0, 0)], X[ix(1, 0)], X[ix(1, 1)]
            colR, rowT = X[ix(slice(None), 1)], X[ix(0, slice(None))]  # [B12, B22] (pair axis ra), [B11, B12] (pair axis cax - 1)
            nd = colR.ndim
            pc = (ra,) + tuple(i for i in range(nd) if i != ra)
            pr = (cax - 1,) + tuple(i for i in range(nd) if i != cax - 1)
            v = self.nv[key] = (S, colR.transpose(*pc), rowT.transpose(*pr), S[2:0:-1], S[0], S[2], S[6], S[3:6], X22, X21, [X22, X11, X21])
        return v

    def colnest_up(self, lvl, c, M):
        """v99 (G-RB118): T-site operand views of the 6-add recombination at level lvl for M output rows (cached per (level, c, M)).
        Rows stay plain (M varies per layer); columns are nested (2,)*e + (w>>d,), e = d - lvl + 1, so the row-2 quadrant pair
        (Q21, Q22) is a basic index. Same element count per role view; the private level-1 result adds one reshape (Mmax*w) per worker."""
        key = ("col", lvl, c, M)
        v = self.nv.get(key)
        if v is None:
            d = self.d
            e = d - lvl + 1
            ca, cb, m, k, w = self.max
            cm = max(ca, cb)
            wd = w >> d
            shp = (7,) * (lvl - 1) + (cm, m >> (lvl - 1)) + (2,) * e + (wd,)
            if lvl == 1:
                plain = self.bufs.get(("up", 1))
                if plain is None:
                    plain = self.bufs[("up", 1)] = fnp.empty((cm, m, w), dtype=self.dt)
                O = self.bufs.get(("up", 1, "col"))
                if O is None:
                    O = self.bufs[("up", 1, "col")] = plain.reshape(shp)
            else:
                O = self.arenas.view(self._group(("up", lvl)), (self.name, "upc", lvl), shp)
            ml = M >> (lvl - 1)
            O = O[(slice(None),) * (lvl - 1) + (slice(0, c), slice(0, ml))]
            h = ml // 2
            P = self.colnest_up(lvl + 1, c, M)[0] if lvl < d else self.leaf_view((7,) * d + (c,), M >> d, wd)
            lead = (slice(None),) * lvl
            Q11, Q12, Q21, Q22 = O[lead + (slice(0, h), 0)], O[lead + (slice(0, h), 1)], O[lead + (slice(h, 2 * h), 0)], O[lead + (slice(h, 2 * h), 1)]
            row2 = O[lead + (slice(h, 2 * h),)]  # (Q21, Q22), pair axis at lvl + 1
            perm = tuple(range(1, lvl + 2)) + (0,) + tuple(range(lvl + 2, P.ndim))
            v = self.nv[key] = (O, P[4], P[5], P[0], P[2], P[3], P[6], Q11, Q12, Q21, Q22, row2, Q12[lead + (slice(None), None)], P[1:3].transpose(*perm))
        return v

    def nest_up(self, lvl, c):
        """v99 (G-RB118): operand views of the 5-add recombination at level lvl for batch c (cached; only fixed (m, w) sites).
        The level-lvl up buffer is viewed NESTED: lead + (2,)*e + (m>>d,) + (2,)*e + (w>>d,), e = d - lvl + 1 (row bits then col bits,
        top level first; C order, so it is the plain (m_l, w_l) matrix), so its quadrant (i, j) is a basic index and has exactly the
        shape of a slot of the level lvl+1 buffer. Each role's arena view is built ONCE in this shape (same element count as v98's plain
        view, same reshape bill); only the private level-1 result adds one reshape (c*m*w) per worker."""
        key = (lvl, c)
        v = self.nv.get(key)
        if v is None:
            d = self.d
            D = d + (1 if self.d6nest else 0)  # the d6 site recombines its extra level into a NESTED depth-5 leaf (level d + 1)
            e = D - lvl + 1
            ca, cb, m, k, w = self.max
            cm = max(ca, cb)
            hd, wd = m >> D, w >> D
            shp = (7,) * (lvl - 1) + (cm,) + (2,) * e + (hd,) + (2,) * e + (wd,)
            if lvl == 1:
                plain = self.bufs.get(("up", 1))
                if plain is None:
                    plain = self.bufs[("up", 1)] = fnp.empty((cm, m, w), dtype=self.dt)
                O = self.bufs.get(("up", 1, "nest"))
                if O is None:
                    O = self.bufs[("up", 1, "nest")] = plain.reshape(shp)
            elif lvl <= d:
                O = self.arenas.view(self._group(("up", lvl)), (self.name, "up", lvl), shp)
            else:  # lvl == d + 1: the depth-5 leaf itself, nested once (replaces its plain view; same reshape bill)
                O = self.arenas.view(self._group(("leaf",)), (self.name, "leafn"), shp)
            O = O[(slice(None),) * (lvl - 1) + (slice(0, c),)]
            if lvl < D:
                P = self.nest_up(lvl + 1, c)[0]
            elif self.d6nest:  # the d6 leaf Pall (7, 7) + (7,)*(d-1) + (c, hd, wd), same view _d6_level writes
                P = self.mini.get("leaf", (7,) * (d + 1) + (c, hd, wd), kind="*")
            else:
                P = self.leaf_view((7,) * d + (c,), hd, wd)
            ra, cax = lvl, lvl + e + 1

            def ix(i, j):
                t = [slice(None)] * O.ndim
                t[ra], t[cax] = i, j
                return tuple(t)

            perm = tuple(range(1, lvl + 1)) + (0,) + tuple(range(lvl + 1, P.ndim))
            Q21 = O[ix(1, 0)]
            v = self.nv[key] = (
                O, P[4], P[5], P[0], P[6], O[ix(0, 0)], Q21, O[ix(1, 1)], O[ix(slice(None), 1)], O[ix(slice(None, None, -1), 1)],
                Q21[(slice(None),) * lvl + (None,)], P[1:3].transpose(*perm), P[3:1:-1].transpose(*perm),
            )
        return v


def _down(X, side, lvl, site, sums_only=False):
    """X: lead + (m, k) -> (7,) + lead + (m/2, k/2), written straight into the stacked buffer (7 ops)."""
    # v99 (G-RB118): at level >= 2 X is this site's previous stack view (same slice for the same shape), so every operand view is cached
    key = (side, lvl, X.shape) if lvl > 1 else None
    v = site.dc.get(key) if key is not None else None
    if v is None:
        h, kk = X.shape[-2] // 2, X.shape[-1] // 2
        X11, X12, X21, X22 = X[..., :h, :kk], X[..., :h, kk:], X[..., h:, :kk], X[..., h:, kk:]
        S = site.stack_view(side, lvl, X.shape[:-2], h, kk)
        # v99 (G-RB118): on nest sites the arithmetic slots are permuted to [S2, S3, S1, S4] / [T2, T3, T1, ., ., ., T4] so the products the
        # 5-add recombination pairs (P7|P5, P3|P5) sit in adjacent slots; plain-quadrant slots and every product are unchanged
        i1, i2, i3 = (2, 0, 1) if (site.nest or site.colnest) else (0, 1, 2)
        if side == "A":
            v = (S, X11, X12, X21, X22, S[i1], S[i2], S[i3], S[3], S[4:7], [X11, X12, X22])
        else:
            v = (S, X11, X12, X21, X22, S[i1], S[i2], S[i3], S[6], S[3:6], [X22, X11, X21])
        if key is not None:
            site.dc[key] = v
    S, X11, X12, X21, X22, s1, s2, s3, s4, s3x, plain3 = v
    add, sub = fnp.add, fnp.subtract
    # v46 (G-RB19): Strassen-Winograd operand stacks (15 additions per level instead of 18; the 7 products are unchanged in count).
    # v47 (G-RB20): the three plain quadrants sit in adjacent slots and are written by ONE concatenate (5 python ops per side, not 7)
    if side == "A":  # [S1, S2, S3, S4, A11, A12, A22]; S1 = A21+A22, S2 = S1-A11, S3 = A11-A21, S4 = A12-S2
        add(X21, X22, out=s1)
        sub(s1, X11, out=s2)
        sub(X11, X21, out=s3)
        sub(X12, s2, out=s4)
        if sums_only:  # G-RB53 qa: the caller reads A11 / A12 / A22 as views; slots 4-6 stay unwritten (never read)
            return S, (X11, X12, X22)
        fnp.stack(plain3, axis=0, out=s3x)  # v77 (G-RB77 A): stack(out=) = concatenate of three [None] views, ~11 us less untimed overhead
    else:  # [T1, T2, T3, B22, B11, B21, T4] (pairs S4 with B22 and A22 with T4); T1 = B12-B11, T2 = B22-T1, T3 = B22-B12, T4 = T2-B21
        sub(X12, X11, out=s1)
        sub(X22, s1, out=s2)
        sub(X22, X12, out=s3)
        sub(s2, X21, out=s4)
        fnp.stack(plain3, axis=0, out=s3x)
    return S


def _up(P, lvl, site):
    """P: (7,) + lead + (h, w) -> lead + (2h, 2w), quadrants written in place (7 ops, Strassen-Winograd recombination).
    Product order follows the v47 stacks: P[0]=S1 T1, P[1]=S2 T2, P[2]=S3 T3, P[3]=S4 B22, P[4]=A11 B11, P[5]=A12 B21, P[6]=A22 T4.
    C11 = P1+P2; U2 = P1+P6; U3 = U2+P7; U4 = U2+P5; C12 = U4+P3; C21 = U3-P4; C22 = U3+P5  (Winograd numbering: P1=A11B11, P2=A12B21,
    P3=S4B22, P4=A22T4, P5=S1T1, P6=S2T2, P7=S3T3)."""
    h, w = P.shape[-2], P.shape[-1]
    O = site.up_view(lvl, P.shape[1:-2], 2 * h, 2 * w)
    C11, C12, C21, C22 = O[..., :h, :w], O[..., :h, w:], O[..., h:, :w], O[..., h:, w:]
    add, sub = fnp.add, fnp.subtract
    add(P[4], P[5], out=C11)  # P1 + P2
    add(P[4], P[1], out=C12)  # U2 = P1 + P6
    add(C12, P[2], out=C21)  # U3 = U2 + P7
    add(C12, P[0], out=C12)  # U4 = U2 + P5
    add(C12, P[3], out=C12)  # C12 = U4 + P3
    add(C21, P[0], out=C22)  # C22 = U3 + P5
    sub(C21, P[6], out=C21)  # C21 = U3 - P4
    return O


class _MiniSite:
    """v98 (G-RB115): scratch for the extra Strassen-Winograd level on the C site's depth-5 leaf batch (see _d6_level). Each role
    has a fixed placement in memory that is provably dead while it is live: the d6 leaf Pall and the X-phase B side in the A13 tail
    behind the depth-5 leaf P (st1A/st3A are dead at the leaf); the X-phase A stack in the never-written qa slots 4-6 of st5A;
    the L-phase A stack in st4A's home (A2u3) and its B stack in st5B slots 4-6 (R[4:7]), both dead once the X phase ran.
    One max-shaped view per (role, lead), built once and sliced (reshape is metered per element)."""

    def __init__(self, dt):
        self.dt, self.cap, self.views, self.out, self.kind = dt, {}, {}, None, "X"
        self.ar = self.place = None
        self.maxdims = {}  # role -> max (rows, cols) of its last two axes
        self.ball = False  # v101 (G-RB122): ONE d6 B side for all 7 leaf slots (roles ("*", "B3") / ("*", "T4"))

    def reserve(self, role, nelems):
        self.cap[role] = max(self.cap.get(role, 0), nelems)

    def bind(self, ar, place):
        self.ar, self.place = ar, place
        for role, (group, o) in place.items():
            assert o + self.cap[role] <= ar.cap[group], (role, group, o, ar.cap[group])

    def get(self, role, shape, kind=None):
        """View for (kind, role) at `shape`: ONE max-shaped view per (role, lead) built once (reshape is metered per element), then
        sliced on the last two axes like SWSite.stack_view."""
        role = (self.kind if kind is None else kind, role)
        lead = shape[:-2]
        v = self.views.get((role, lead))
        if v is None:
            group, o = self.place[role]
            b = self.ar.buf.get(group)
            if b is None:
                b = self.ar.buf[group] = fnp.empty((self.ar.cap[group],), dtype=self.dt)
            full = lead + self.maxdims[role[1]]
            n = 1
            for x in full:
                n *= x
            assert n <= self.cap[role], (role, full)
            v = self.views[(role, lead)] = b[o : o + n].reshape(full)
        return v[..., : shape[-2], : shape[-1]]

    def up_view(self, lvl, lead, h2, w2):
        return self.out


_D6_LAYERS = frozenset(range(16))  # v98: EVERY layer whose C-site call runs (14 of 16) takes the extra d6 level (v97: {10..14})
_D6_SITES = ("T2", "M2")  # v101 (G-RB122): + M2, funded by the X-phase pair / single B side  # v100 (G-RB121): the same fused extra level on these depth-5 nest sites, every call (M1: one call, its one-time views cost more than it saves; M2: 0.056 pt for +13 ms residual, the worst util per ms)


def _attach_d6(site, ar, dt):
    """v100 (G-RB121): give a depth-5 qa nest site (not C) v98's fused extra Winograd level, with its scratch placed exactly like the C
    site's (_MiniSite docstring) but sized from THIS site's own roles, and WITHOUT reserving: every placement must fit the arena caps the
    sites already set (asserted in bind), so the arenas -- and VmPeak -- do not grow. Liveness at this site's leaf is the C site's:
    st1A/st3A dead (A13 behind the depth-5 leaf), st5A slots 4-6 never written (qa), st4A dead after the X phase, st5B slots 4-6 dead
    after the X phase; every one of them is scratch of the running call only."""
    ca, cb, m, k, w = site.max
    assert site.d == 5 and site.nest and ca == cb and m % 64 == 0 and k % 64 == 0 and w % 64 == 0, (
        site.name,
        site.max,
    )
    mini = site.mini = _MiniSite(dt)
    site.d6, site.d6nest = True, True
    site.xpair_on, mini.ball = _D6_XPAIR, True  # v101 (G-RB122)
    h, kA, wA = m >> 6, k >> 6, w >> 6
    mini.maxdims = {"stA": (h, kA), "B3": (kA, wA), "T4": (kA, wA), "leaf": (h, wA)}
    l4 = 7**4 * ca  # lead of one depth-5 leaf slot (incl. the batch)
    mini.reserve(("*", "leaf"), 49 * l4 * h * wA)
    mini.reserve(("*", "B3"), 3 * 7 * l4 * kA * wA)  # v101: one B side for all 7 slots
    mini.reserve(("*", "T4"), 7 * l4 * kA * wA)
    mini.reserve(("X", "stA"), 4 * (2 if _D6_XPAIR else 1) * l4 * h * kA)  # v101: the X12 | X22 pair at once
    mini.reserve(("L", "stA"), 4 * 4 * l4 * h * kA)

    def prod(t):
        r = 1
        for x in t:
            r *= x
        return r

    n5a, n5b, nleaf = (
        prod(site.roles[("st", "A", 5)]),
        prod(site.roles[("st", "B", 5)]),
        prod(site.roles[("leaf",)]),
    )
    cp = mini.cap
    lf = nleaf + cp[("*", "leaf")]
    assert lf + cp[("*", "B3")] + cp[("*", "T4")] <= ar.cap["A13"], (site.name, ar.cap["A13"])
    mini.bind(
        ar,
        {
            ("*", "leaf"): ("A13", nleaf),
            ("X", "stA"): ("B2u2", 4 * n5a // 7),
            ("*", "B3"): ("A13", lf),  # v101: the whole B side in the A13 tail behind Pall (st1A/st3A dead at the leaf)
            ("*", "T4"): ("A13", lf + cp[("*", "B3")]),
            ("L", "stA"): ("A2u3", 0),
        },
    )
    # the X-phase A stack must stay inside st5A's unwritten qa slots 4-6 (n5b unused since v101)
    assert cp[("X", "stA")] <= 3 * n5a // 7 and n5b > 0, site.name




_D6_XPAIR = True  # v101 (G-RB122): X12 | X22 of the d6 X phase as one batched pair (row-nested level-4 A view)
_D6_T = True  # v100 (G-RB121): chunked extra level on the T site (leaf slot by slot), every call


def _attach_d6_chunked(site, ar, dt):
    """v100 (G-RB121): scratch for _d6_chunked on a depth-5 site whose fused d6 leaf would not fit (T: 49 x 7^4 x 200 x 16 = 376M) and
    that runs WITHOUT the qa trick (st5A has all 7 slots). Placements (no reserve; bind asserts the existing caps): the B side of all 7
    slots and the product chunk in B13 behind st5B (st1B/st3B dead; st5B = R is read to the end); the per-group A stack in st4A's home
    (A2u3: st4A is dead once st5A is complete). The 4-slot chunk Pc4 is sized to what B13 has left (rows <= 168, i.e. M <= 10752, which
    covers every realized T call); taller calls use the 3-slot chunk Pc (same region)."""
    ca, cb, m, k, w = site.max
    assert site.d == 5 and ca == cb == 1 and m % 64 == 0 and k % 64 == 0 and w % 64 == 0, (site.name, site.max)
    mini = site.mini = _MiniSite(dt)
    site.d6c = True

    def prod(t):
        r = 1
        for x in t:
            r *= x
        return r

    h, kA, wA = m >> 6, k >> 6, w >> 6
    l4 = 7**4
    n5b = prod(site.roles[("st", "B", 5)])
    nB3, nT4 = 21 * l4 * kA * wA, 7 * l4 * kA * wA
    left = ar.cap["B13"] - n5b - nB3 - nT4
    h4 = min(h, left // (28 * l4 * wA))
    mini.maxdims = {"stA4": (h, kA), "B3": (kA, wA), "T4": (kA, wA), "Pc": (h, wA), "Pc4": (h4, wA)}
    for role, nel in (("B3", nB3), ("T4", nT4), ("Pc", 21 * l4 * h * wA), ("Pc4", 28 * l4 * h4 * wA), ("stA4", 16 * l4 * h * kA)):
        mini.reserve(("*", role), nel)
    cp = mini.cap
    oP = n5b + nB3 + nT4
    mini.bind(ar, {
        ("*", "B3"): ("B13", n5b),
        ("*", "T4"): ("B13", n5b + nB3),
        ("*", "Pc"): ("B13", oP),
        ("*", "Pc4"): ("B13", oP),
        ("*", "stA4"): ("A2u3", 0),
    })
    assert cp[("*", "stA4")] <= prod(site.roles[("st", "A", 4)]), site.name


def _d6_recomb(Pc, O):
    """Winograd recombination of one chunk Pc (slots [S2T2, S3T3, S1T1, S4B22, A11B11, A12B21, A22T4]) into O (7 adds, _up's order)."""
    h, w = Pc.shape[-2], Pc.shape[-1]
    C11, C12, C21, C22 = O[..., :h, :w], O[..., :h, w:], O[..., h:, :w], O[..., h:, w:]
    add, sub = fnp.add, fnp.subtract
    add(Pc[4], Pc[5], out=C11)  # P1 + P2
    add(Pc[4], Pc[0], out=C12)  # U2 = P1 + P6
    add(C12, Pc[1], out=C21)  # U3 = U2 + P7
    add(C12, Pc[2], out=C12)  # U4 = U2 + P5
    add(C12, Pc[3], out=C12)  # C12 = U4 + P3
    add(C21, Pc[2], out=C22)  # C22 = U3 + P5
    sub(C21, Pc[6], out=C21)  # C21 = U3 - P4


def _d6_chunked(L, R, P, mini):
    """v100 (G-RB121): one extra Strassen-Winograd level on a depth-5 leaf whose A stack L has all 7 slots written (the T site runs
    without the qa trick), into the plain leaf P a group of depth-5 leaf slots at a time: B side once for all 7 slots, then per group the
    A stack (st4A's dead home), the 7 products into the chunk Pc and the recombination into P[group]. Products as _d6_level's."""
    lead = R.shape[1:-2]
    hA, kA2, w2 = L.shape[-2] // 2, L.shape[-1] // 2, R.shape[-1] // 2
    mm = fnp.matmul
    mini.kind = "*"
    S3, T4, B11, B21, B22 = _d6_bside(R, mini)  # (3, 7) + lead, (7,) + lead, views (7,) + lead
    if hA <= mini.maxdims["Pc4"][0]:
        groups, Pc = ((0, 4), (4, 7)), mini.get("Pc4", (7, 4) + lead + (hA, w2))
    else:  # rows above every realized T call (M > 10752): the chunk holds 3 slots
        groups, Pc = ((0, 3), (3, 6), (6, 7)), mini.get("Pc", (7, 3) + lead + (hA, w2))
    SA4 = mini.get("stA4", (4, 4) + lead + (hA, kA2))
    for g0, g1 in groups:
        g, SA, pc = slice(g0, g1), SA4[:, : g1 - g0], Pc[:, : g1 - g0]
        a11, a12, a22 = _d6_aside(L[g], SA)
        mm(SA[0:3], S3[:, g], out=pc[0:3])
        mm(SA[3], B22[g], out=pc[3])
        mm(a11, B11[g], out=pc[4])
        mm(a12, B21[g], out=pc[5])
        mm(a22, T4[g], out=pc[6])
        _d6_recomb(pc, P[g])


def _d6_bside(Rg, mini):
    """qb B side of one extra Winograd level for a group of leaf slots Rg: (g,) + lead + (k, w): T1..T3 into ONE 3-slot stack, T4
    alone; the plain quadrants B11 / B21 / B22 stay views (4 ops for the whole group)."""
    h, w2 = Rg.shape[-2] // 2, Rg.shape[-1] // 2
    B11, B12, B21, B22 = Rg[..., :h, :w2], Rg[..., :h, w2:], Rg[..., h:, :w2], Rg[..., h:, w2:]
    S3 = mini.get("B3", (3,) + Rg.shape[:-2] + (h, w2))
    T4 = mini.get("T4", Rg.shape[:-2] + (h, w2))
    sub = fnp.subtract
    # v99 (G-RB118): slots [T2, T3, T1] (was [T1, T2, T3]) so the 49 products land in the nested recombination's order
    sub(B12, B11, out=S3[2])  # T1
    sub(B22, S3[2], out=S3[0])  # T2
    sub(B22, B12, out=S3[1])  # T3
    sub(S3[0], B21, out=T4)  # T4
    return S3, T4, B11, B21, B22


def _d6_aside(X, SA):
    """qa A side: S1..S4 of X (lead + (m, k)) into the 4-slot stack view SA; returns the plain quadrants A11 / A12 / A22 as views."""
    h, kk = X.shape[-2] // 2, X.shape[-1] // 2
    X11, X12, X21, X22 = X[..., :h, :kk], X[..., :h, kk:], X[..., h:, :kk], X[..., h:, kk:]
    add, sub = fnp.add, fnp.subtract
    add(X21, X22, out=SA[2])  # S1  (v99: slots [S2, S3, S1, S4])
    sub(SA[2], X11, out=SA[0])  # S2
    sub(X11, X21, out=SA[1])  # S3
    sub(X12, SA[0], out=SA[3])  # S4
    return X11, X12, X22


def _d6_level(L, XA, R, P, mini, XR=None):
    """v98 (G-RB115): one extra Strassen-Winograd level on the WHOLE depth-5 leaf batch of the C site, fused across its 7 slots:
    L[0:4] (the written stack slots) are one batch; the three qa quadrant slots XA = (A11, A12, A22) of the level-4 stack run
    one at a time (A stack kept inside v97's footprint) against ONE shared B side for R[4:7]. All 49 d6 products land in one leaf Pall
    (7, 7, lead, h, w) and ONE _up writes the depth-5 leaf P. Products / recombination exactly as v97's per-slot level
    (P[0..2] = S_i T_i, P[3] = S4 B22, P[4] = A11 B11, P[5] = A12 B21, P[6] = A22 T4)."""
    lead = R.shape[1:-2]
    X11 = XA[0]
    hA, kA2, w2 = X11.shape[-2] // 2, X11.shape[-1] // 2, R.shape[-1] // 2
    mm = fnp.matmul
    Pall = mini.get("leaf", (7, 7) + lead + (hA, w2), kind="*")
    if mini.ball:  # v101 (G-RB122): ONE B side for all 7 slots (small fixed sites: room in the A13 tail)
        mini.kind = "*"
        bs = _d6_bside(R, mini)
        S3, T4, B11, B21, B22 = bs[0][:, 4:7], bs[1][4:7], bs[2][4:7], bs[3][4:7], bs[4][4:7]
        mini.kind = "X"
    else:
        mini.kind = "X"  # the qa slots first: they read st4A and R[4:7], whose memory the L phase then reuses
        S3, T4, B11, B21, B22 = _d6_bside(R[4:7], mini)
    PX = Pall[:, 4:7]
    if XR is None:
        SA = mini.get("stA", (4,) + lead + (hA, kA2))  # one qa slot at a time (keeps the X A stack inside v97's footprint)
        for j, Xc in enumerate(XA):
            a11, a12, a22 = _d6_aside(Xc, SA)
            mm(SA[0:3], S3[:, j], out=PX[0:3, j])
            mm(SA[3], B22[j], out=PX[3, j])
            mm(a11, B11[j], out=PX[4, j])
            mm(a12, B21[j], out=PX[5, j])
            mm(a22, T4[j], out=PX[6, j])
    else:  # v101 (G-RB122): slots 5 / 6 (X12 | X22, one batched pair view), then slot 4 (X11) in the pair stack's first half
        SA2 = mini.get("stA", (4, 2) + lead + (hA, kA2))
        a11, a12, a22 = _d6_aside(XR, SA2)
        mm(SA2[0:3], S3[:, 1:3], out=PX[0:3, 1:3])
        mm(SA2[3], B22[1:3], out=PX[3, 1:3])
        mm(a11, B11[1:3], out=PX[4, 1:3])
        mm(a12, B21[1:3], out=PX[5, 1:3])
        mm(a22, T4[1:3], out=PX[6, 1:3])
        SA = SA2[:, 0]
        a11, a12, a22 = _d6_aside(X11, SA)
        mm(SA[0:3], S3[:, 0], out=PX[0:3, 0])
        mm(SA[3], B22[0], out=PX[3, 0])
        mm(a11, B11[0], out=PX[4, 0])
        mm(a12, B21[0], out=PX[5, 0])
        mm(a22, T4[0], out=PX[6, 0])
    mini.kind = "L"
    if mini.ball:
        S3, T4, B11, B21, B22 = bs[0][:, 0:4], bs[1][0:4], bs[2][0:4], bs[3][0:4], bs[4][0:4]
    else:
        S3, T4, B11, B21, B22 = _d6_bside(R[0:4], mini)
    SA = mini.get("stA", (4, 4) + lead + (hA, kA2))
    a11, a12, a22 = _d6_aside(L[0:4], SA)
    PL = Pall[:, 0:4]
    mm(SA[0:3], S3, out=PL[0:3])
    mm(SA[3], B22, out=PL[3])
    mm(a11, B11, out=PL[4])
    mm(a12, B21, out=PL[5])
    mm(a22, T4, out=PL[6])
    # v99 (G-RB118): the recombination into the depth-5 leaf is level 6 of the C site's nested 5-add up (sw_matmul)


def _down_Bn(site, lvl, cb, Bn):
    """v99 (G-RB118): nested B side (4 ops: v98 order T1, T3, T2, T4, stack; [T1, T3] fused)."""
    S, cr, rt, o13, s0, s2, s6, s36, x22, x21, plain3 = site.nest_down_B(lvl, cb, Bn)
    fnp.subtract(cr, rt, out=o13)  # [T1, T3] = [B12 - B11, B22 - B12]
    fnp.subtract(x22, s2, out=s0)  # T2 = B22 - T1
    fnp.subtract(s0, x21, out=s6)  # T4 = T2 - B21
    fnp.stack(plain3, axis=0, out=s36)
    return S


def sw_matmul(A, B, site, Bn=None):
    """A (ca, m, k) @ B (cb, k, w) -> (max(ca,cb), m, w) view into the site's result buffer (valid until the site's next call).
    v99: Bn = an optional PERSISTENT nested view of B (site.nestB only), used at level 1 instead of B."""
    d = site.d
    if d == 0:
        return fnp.matmul(A, B)
    L, R = A, B
    XA = None
    qa = d in (3, 5) and not getattr(site, "d6c", False)  # v100: the d6c (T) site keeps all 7 level-5 A slots for its chunked level  # G-RB53 qa: deepest-level A-side plain quadrants as views (d = 2 / 4 leaves alias the previous A stack)
    nb, cb = site.nestB, B.shape[0]
    if site.nest:  # v99: nested views assume the site's max (m, w) (and (k, w) for nestB); host-int shape checks only
        assert A.shape[-2] == site.max[2] and B.shape[-1] == site.max[4], (site.name, A.shape, B.shape)
        assert not nb or B.shape[-2] == site.max[3], (site.name, B.shape)

    def downB(R, lvl):
        if nb and (lvl > 1 or Bn is not None):
            return _down_Bn(site, lvl, cb, Bn)
        return _down(R, "B", lvl, site)

    for lvl in range(1, d + 1):
        last = qa and lvl == d
        if lvl == 5:  # v46: the level-5 B stack first, so st5A may alias the (then dead) st4B arena (see _SW_GROUP)
            R = downB(R, lvl)
            L, XA = _down(L, "A", lvl, site, last) if last else (_down(L, "A", lvl, site), None)
        else:
            if last:
                L, XA = _down(L, "A", lvl, site, True)
                R = downB(R, lvl)
            else:
                L, R = _down(L, "A", lvl, site), downB(R, lvl)
    lead = R.shape[:-2] if R.shape[-3] >= L.shape[-3] else L.shape[:-2]
    if XA is None:
        P = site.leaf_view(lead, L.shape[-2], R.shape[-1])
        if getattr(site, "d6c", False) and L.shape[-2] % 2 == 0 and L.shape[-1] % 2 == 0 and R.shape[-1] % 2 == 0:
            _d6_chunked(L, R, P, site.mini)  # v100 (G-RB121): chunked extra level into the plain leaf
        else:
            fnp.matmul(L, R, out=P)
    else:  # G-RB53 qa: slots 4-6 of the A stack were never written; read the quadrants of the previous A stack instead
        X11, X12, X22 = XA
        if getattr(site, "d6", False) and L.shape[-2] % 2 == 0 and L.shape[-1] % 2 == 0 and R.shape[-1] % 2 == 0:
            assert site.d6nest
            XR = site.xpair(lead[-1], XA[1].shape[-1]) if getattr(site, "xpair_on", False) else None  # v101 (G-RB122)
            _d6_level(L, XA, R, None, site.mini, XR)
        else:
            assert not site.d6nest
            P = site.leaf_view(lead, L.shape[-2], R.shape[-1])
            fnp.matmul(L[0:4], R[0:4], out=P[0:4])
            fnp.matmul(X11, R[4], out=P[4])
            fnp.matmul(X12, R[5], out=P[5])
            fnp.matmul(X22, R[6], out=P[6])
    if site.nest:  # v99 (G-RB118): 5 adds per level on cached nested views (same operand pairs as _up -> bit-identical)
        c = lead[-1]
        add, sub = fnp.add, fnp.subtract
        for lvl in range(d + (1 if site.d6nest else 0), 0, -1):
            _, p1, p2, p6, p4, q11, q21, q22, col1, col1r, u2b, p75, p35 = site.nest_up(lvl, c)
            add(p1, p2, out=q11)  # C11 = P1 + P2
            add(p1, p6, out=q21)  # U2 = P1 + P6
            add(u2b, p75, out=col1r)  # [U3 -> Q22, U4 -> Q12] = U2 + [P7, P5]
            sub(q22, p4, out=q21)  # C21 = U3 - P4
            add(col1, p35, out=col1)  # [C12, C22] = [U4, U3] + [P3, P5]  (in place)
        return site.bufs[("up", 1)][:c]
    if site.colnest:  # v99 (G-RB118): 6 adds per level (same operand pairs as _up -> bit-identical)
        c, M = lead[-1], A.shape[-2]
        add, sub = fnp.add, fnp.subtract
        for lvl in range(d, 0, -1):
            _, p1, p2, p6, p5, p3, p4, q11, q12, q21, q22, row2, u2b, p75 = site.colnest_up(lvl, c, M)
            add(p1, p2, out=q11)  # C11 = P1 + P2
            add(p1, p6, out=q12)  # U2 = P1 + P6  (in Q12)
            add(u2b, p75, out=row2)  # [U3 -> Q21, U4 -> Q22] = U2 + [P7, P5]
            add(q22, p3, out=q12)  # C12 = U4 + P3
            add(q21, p5, out=q22)  # C22 = U3 + P5
            sub(q21, p4, out=q21)  # C21 = U3 - P4  (in place)
        return site.bufs[("up", 1)][:c, :M]
    for lvl in range(d, 0, -1):
        P = _up(P, lvl, site)
    return P

_SW_DEPTH = 5  # Strassen depth on the (merged) contraction site, ONE call per layer (v48); v29: 3 -> 4 (G-RB11); v46: 5 (G-RB19)
_SW_DEPTH_T = 5  # Strassen depth on the young transport site (all layers); v29: 3 -> 4 (G-RB11); v46: 5 in the transposed form [P|A]^T @ w (G-RB19 D)
_SW_DEPTH_OLD = 3  # Strassen depth on the four old-tier sites (batched over the old sources); v28: 1 -> 2 (G-RB9)
_SW_DEPTH_FK = (4, 5)  # v48_a3 (G-RB22 A3): 384 group at depth 5 (384/32 = 12); v47_fk4 (G-RB20 b): both old groups at depth 4 (224/16 = 14 divides); the 224 group's d=4 leaf / st4 arenas are 600 MB each -- affordable after the G-RB19 memory trims
_E_PAD = 384  # G-RB57: r = 384 = 12 * 32 needs no pad (was 416 for 392 = r + os)
_E_PAD_OLD = 416  # v54 (G-RB41 E): old-tier entry sketch (392 = _R_OLD + _OS) zero-padded to 13 * 32
_E_DEPTH_Y = 3  # v55 (G-RB42): Strassen depth of the two Y-chain entry calls (n x n x 416)
_E_DEPTH_Q = 4  # depth of the QP|QA call (416 x n x 2n); d3 on BOTH chains gave a +45 ms worker-only excursion on mlp 1 (G-RB41/42)
_SW_DEPTH_Q = 4  # v46: the merged old-tier Q transport (n x sum of basis ranks; every rank is a multiple of 32)
_K_STEADY = _AGE_OLD - 1  # young sources alive at steady state (4)



def _rank_rf(M, Om, r):
    """M ~ U @ B with U (n x r) orthonormal: randomized range finder (Om = n x (r+os) Gaussian), small SVD of the sketch."""
    Q1, _ = fnp.linalg.qr(M @ Om)
    Q1, _ = fnp.linalg.qr(M @ (M.T @ Q1))  # one power iteration (a 0-power sketch costs +52 % e2e in the f64 prototype)
    U2, s2, Vt = fnp.linalg.svd(Q1.T @ M, full_matrices=False)
    return Q1 @ U2[:, :r], s2[:r, None] * Vt[:r]


def _zbuf(pool, shape, dt):
    key = (shape, str(dt), "Z")
    b = pool.get(key)
    if b is None:
        b = pool[key] = fnp.zeros(tuple(x for x in shape if isinstance(x, int)), dtype=dt)
    return b


def _big_view(pool, name, key, shape, dt):
    """G-RB77 (B): a cached reshaped view of one of the two shared >= 32 MB scratch buffers (BUF1: opT then the contraction left factor;
    BUF2: the warm-column take of opT then each old group's LPA stack -- the pairs are never live at the same time). The buffer is sized at
    the first (largest) reservation under `pool[("__bigcap__", name)]`; reshape once per (name, key) like SWArenas.view."""
    k = ("__big__", name, key)
    v = pool.get(k)
    if v is None:
        bk = ("__bigbuf__", name)
        b = pool.get(bk)
        if b is None:
            b = pool[bk] = fnp.empty((pool[("__bigcap__", name)],), dtype=dt)
        n_el = 1
        for x in shape:
            n_el *= x
        assert n_el <= b.shape[0], (name, key, shape, b.shape)
        v = pool[k] = b[:n_el].reshape(shape)
    return v


_RS_ALIAS = {"STPz": ("A2u3", 0), "STAz": ("A2u3", 1), "PP": ("A13", 0), "PA": ("A13", 1), "W": ("B13", 0), "tmp": ("B13", 1), "tmp2": ("B2u2", 0)}


def _arena_slot(pool, tag, shape, dt):
    """G-RB52: a _read_stack temporary as a view into an SW arena (group, slot). Arenas are scratch only DURING an sw_matmul call
    and no call runs inside _read_stack, so its temporaries can live there; LP / LA (read by later calls) stay private."""
    if tag in ("STPz", "STAz"):  # v99 (G-RB118): A2u3 slots 0/1 as ONE (2,) + shape view (same reshape bill as two), so _read_stack can pair Pz/Az
        key = ("__slot__", "STPA2")
        v = pool.get(key)
        if v is None:
            ar = pool["__ar__"]
            n_el = 1
            for x in shape:
                n_el *= x
            assert ar.cap["A2u3"] >= 2 * n_el, (ar.cap["A2u3"], n_el)
            b = ar.buf.get("A2u3")
            if b is None:
                b = ar.buf["A2u3"] = fnp.empty((ar.cap["A2u3"],), dtype=ar.dt)
            v = pool[key] = b[: 2 * n_el].reshape((2,) + tuple(shape))
        return v[0 if tag == "STPz" else 1]
    key = ("__slot__", tag)
    v = pool.get(key)
    if v is None:
        ar = pool["__ar__"]
        group, slot = _RS_ALIAS[tag]
        n_el = 1
        for x in shape:
            n_el *= x
        assert ar.cap[group] >= (slot + 1) * n_el, (group, ar.cap[group], n_el)
        b = ar.buf.get(group)
        if b is None:
            b = ar.buf[group] = fnp.empty((ar.cap[group],), dtype=ar.dt)
        v = pool[key] = b[slot * n_el : (slot + 1) * n_el].reshape(shape)
    return v


def _read_stack(Pz, Az, TZ, F, Cc, Ct, pool):
    """Hadamard assembly for a stack of sources (S,n,n): returns LP, LA (S,n,n) and the thin part of the read (n,n).
    Tz_b = LP_b Pz_b^T + LA_b Az_b^T + thin_b (eq 16 for the five birth blocks; DESIGN.md S2/S3).
    Every intermediate is written with out= into a persistent pooled buffer (the residual-time cost of this section is malloc/munmap
    churn, not FLOPs). v46 (G-RB19 B): the terms are accumulated in an order that keeps only SEVEN (S,n,n) buffers live
    (PP, PA, LP, LA, one X/Y scratch, two temporaries) instead of twelve; same FLOPs, f32 rounding-level reordering."""
    dt = Pz.dtype
    S_, n = Pz.shape[0], Pz.shape[1]
    mul, add, mm = fnp.multiply, fnp.add, fnp.matmul

    SM = _STACK_SIZES[-1]

    def B(tag):  # ONE buffer set at the largest stack width, sliced on the leading axis (contiguous view)
        if tag in _RS_ALIAS and "__ar__" in pool:  # G-RB52: dead-between-calls arena memory
            return _arena_slot(pool, tag, (SM, n, n), dt)[:S_]
        return _buf(pool, (SM, n, n) + ("RS", tag), dt)[:S_]

    f1, f2, f3, t, s = (F[:, i : i + 1, :] for i in range(5))  # (S,1,n): per-hub (column) statics
    c1, c2, c3, c4, c5 = (Cc[:, i] for i in range(5))  # (S,RK,n)
    c1t, c2t, c3t, c4t, c5t = (Ct[:, i] for i in range(5))  # (S,n,RK)
    T1z, T2z, Zz, uz = TZ[:, :, :_RK], TZ[:, :, _RK : 2 * _RK], TZ[:, :, 2 * _RK : 3 * _RK], TZ[:, :, 3 * _RK :]
    sht = (SM, n, _RK)
    L1b = _buf(pool, sht + ("RS", "L1"), dt)[:S_]
    L2b = _buf(pool, sht + ("RS", "L2"), dt)[:S_]
    # v99 (G-RB118): LP/LA share one (2, S, n, n) buffer and every pair of updates "LP += a*Az..., LA += b*Pz..." runs as ONE op on the
    # [Az, Pz] pair view (Pz/Az live in adjacent arena slots); each element sees exactly v98's operations in v98's order.
    PZA = pool[("__slot__", "STPA2")][:, :S_]  # [Pz, Az] (the _fill targets)
    AZP = PZA[::-1]  # [Az, Pz]
    LPAj = _buf(pool, (2, SM, n, n) + ("RS", "LPA2"), dt)[:, :S_]
    LP, LA = LPAj[0], LPAj[1]
    PT = _buf(pool, (2, SM, n, n) + ("RS", "PT"), dt)[:, :S_]  # private pair temporary (empty is free; its slot 0 replaces v98's tmp2 arena view)
    tmp2 = PT[0]
    PP = mul(Pz, Pz, out=B("PP"))
    PA = mul(Pz, Az, out=B("PA"))
    tmp = B("tmp")
    # adjustment leg: Yadj = Zz c5 + Az*t + Pz*s;  LP = (2/3) Pz*Yadj + (1/3) PP*s;  LA = (1/3) PP*t
    W = mm(Zz, c5, out=B("W"))
    tmp = mul(Az, t, out=tmp)
    W = add(W, tmp, out=W)
    tmp = mul(Pz, s, out=tmp)
    W = add(W, tmp, out=W)
    mul(PP[None], F[:, 4:2:-1, :].transpose(1, 0, 2)[:, :, None, :], out=LPAj)  # [PP*s, PP*t]
    mul(LPAj, 1.0 / 3.0, out=LPAj)
    tmp = mul(Pz, W, out=tmp)
    tmp = mul(tmp, 2.0 / 3.0, out=tmp)
    LP = add(LP, tmp, out=LP)
    # Y11 = T1z c1 + T2z c2 + Az*f2;  LP += Az*Y11;  LA += Pz*Y11   (tmp keeps Af2 = Az*f2)
    W = mm(T1z, c1, out=W)
    tmp2 = mm(T2z, c2, out=tmp2)
    W = add(W, tmp2, out=W)
    tmp = mul(Az, f2, out=tmp)
    W = add(W, tmp, out=W)
    mul(AZP, W[None], out=PT)
    add(LPAj, PT, out=LPAj)
    # X12 = T2z c3;  LP += X12*Af2;  LA += (Pz*X12)*f2;  thin T2: PA c2^T + (Pz o Af2) c3^T
    W = mm(T2z, c3, out=W)
    mul(W, tmp, out=PT[0])
    mul(Pz, W, out=PT[1])
    mul(PT[1], f2, out=PT[1])
    add(LPAj, PT, out=LPAj)
    tmp = mul(Pz, tmp, out=tmp)
    L2 = mm(tmp, c3t, out=L2b)
    L1 = mm(PA, c2t, out=L1b)
    L1 = add(L1, L2, out=L1)
    th = fnp.einsum("kir,kjr->ij", L1, T2z)
    # X21 = T1z c4;  LP += 0.5 X21*Af3;  LA += 0.5 (Pz*X21)*f3;  thin T1: PA c1^T + 0.5 (Pz o Af3) c4^T
    W = mm(T1z, c4, out=W)
    tmp = mul(Az, f3, out=tmp)
    mul(W, tmp, out=PT[0])
    mul(Pz, W, out=PT[1])
    mul(PT[1], f3, out=PT[1])
    mul(PT, 0.5, out=PT)
    add(LPAj, PT, out=LPAj)
    tmp = mul(Pz, tmp, out=tmp)
    L2 = mm(tmp, c4t, out=L2)
    L2 = mul(L2, 0.5, out=L2)
    L1 = mm(PA, c1t, out=L1)
    L1 = add(L1, L2, out=L1)
    th = th + fnp.einsum("kir,kjr->ij", L1, T1z)
    # kappa4 feed: LP += uz*(Az*f1);  LA += uz*(Pz*f1);  thin: sum_j (PA*f1)_ij  x  uz
    mul(AZP, f1, out=PT)
    mul(PT, uz, out=PT)
    add(LPAj, PT, out=LPAj)
    tmp = mul(PA, f1, out=tmp)
    th = th + fnp.einsum("ki,kj->ij", fnp.sum(tmp, axis=2), uz[:, :, 0])
    # LA += PA*f2;  thin Z: PP c5^T / 3
    tmp = mul(PA, f2, out=tmp)
    LA = add(LA, tmp, out=LA)
    L1 = mm(PP, c5t, out=L1)
    th = th + (1.0 / 3.0) * fnp.einsum("kir,kjr->ij", L1, Zz)
    return LP, LA, th


def _read_stack_diag(Pz, Az, TZ, F, Cc, Ct, pool):
    """(3)-diagonal only (last layer): diag of LP Pz^T + LA Az^T + thin."""
    LP, LA, th = _read_stack(Pz, Az, TZ, F, Cc, Ct, pool)
    return fnp.einsum("kij,kij->i", LP, Pz) + fnp.einsum("kij,kij->i", LA, Az) + fnp.diag(th)


_STACK_SIZES = (15,)  # v46: one pooled buffer set at the largest stack (all sources at the last layer), sliced to the exact source count per layer


class Estimator(BaseEstimator):
    def __init__(self) -> None:
        self._g = None
        self._kap = None
        self._pool = None
        self._sites = None
        self._lc = None
        self._lc_bias = None
        self._lam = None
        self._qc = None

    def setup(self, context: SetupContext) -> None:
        self._g = None
        self._kap = None
        self._pool = {}
        self._sites = {}
        if context.submission_dir is not None:
            path = Path(context.submission_dir) / WEIGHTS_FILE
            if path.exists():
                w = Weights.from_file(str(path))
                # length-1 slices: integer indexing would unwrap to a host scalar (G-V5-RES)
                self._g = [w.g[i : i + 1] for i in range(_CAL_DEPTH)]
                self._kap = [w.kappa[i : i + 1] for i in range(_CAL_DEPTH)]
                self._lam = [w.lam[i] for i in range(_CAL_DEPTH)]  # (4,4) per transport layer
                self._qc = [w.qc[i] for i in range(_CAL_DEPTH)]  # (6,) per ReLU layer (forms Q for the next transport)
            lc_path = Path(context.submission_dir) / LC_FILE
            if lc_path.exists():
                self._lc = LCWeights.from_file(str(lc_path))
                self._lc_bias = [self._lc.bias[i : i + 1] for i in range(_CAL_DEPTH)]

    def predict(self, mlp: MLP, budget: int) -> fnp.ndarray:
        _ = budget
        dt = _DTYPE
        n, depth = mlp.width, mlp.depth
        use_fit = self._g is not None and n == _CAL_WIDTH and depth == _CAL_DEPTH
        use_stack = (
            n == _CAL_WIDTH and depth == _CAL_DEPTH
        )  # off the calibration shape: plain two-index chain (cost insurance)
        use_lc = use_fit and self._lc is not None  # learned corrector: calibration shape only, needs its weights (host booleans)
        lc = self._lc
        norm = flops.stats.norm

        karr = fnp.arange(1, _KH + 1, dtype=dt)
        kcoef = fnp.arange(1, _KGC - 2, dtype=dt)[:, None]  # G-RB77 (C): Hermite recursion coefficients k-2 for k = 3.._KGC-1
        inv_fact_d22 = fnp.concatenate([fnp.ones(1, dtype=dt), 1.0 / fnp.cumprod(karr)])
        zero_mask = fnp.array(_ZERO_MASK_TABLE, dtype=dt)
        coef = (inv_fact_d22[:, None] * zero_mask)[:, :, None, None]
        I_n = fnp.eye(n, dtype=dt)

        mu = fnp.zeros(n, dtype=dt)
        cov = flops.as_symmetric(fnp.eye(n, dtype=dt), symmetry=(0, 1))
        ssc_modes = None  # v51: (t = kappa_iii(h), v = diag Sigma_h, mbar, vbar) from the previous ReLU; None at layer 0 (input Gaussian -> lean path with g_0)
        ones_n = fnp.ones(n, dtype=dt)
        use_ssc = use_fit and self._lam is not None
        T = None  # two-index sector transport (only when the source machinery is off)
        # young sources: stacks over sources (k, ...)
        yP = yA = yT = yF = yC = yCt = None  # (k,n,n), (k,n,n), (k,n,49), (k,5,n), (k,5,16,n), (k,5,n,16)
        y_birth = []  # birth layers (host ints) of the young stack, oldest first
        # old sources: per-source basis
        # two batched groups by basis rank, G = 0: r = _R_OLD2 (the oldest), G = 1: r = _R_OLD; all-old thin stacks oT/oF/oC/oCt are oldest-first
        oQ, oFPA, oFPAt = [None, None], [None, None], [None, None]  # per group: (m,n,r), (m,r,2n) [F_P|F_A], (m,2n,r)
        oT = oF = oC = oCt = None  # (m,n,49), (m,5,n), (m,5,16,n), (m,5,n,16) over ALL old sources, oldest first
        o_birth = [[], []]  # birth layers per group (host ints), oldest first
        r_ = _R_OLD
        R_G = (_R_OLD2, _R_OLD)
        kmax = max(depth - _AGE_OLD, 1)  # most old sources alive at once (m_o = l - 4 at layer l: 11 at depth 16)
        kmax_g = (max(depth - _AGE_OLD2, 1), max(_AGE_OLD2 - _AGE_OLD, 1))  # group sizes: oldest group grows to depth - _AGE_OLD2; the 384 group holds ages 5.._AGE_OLD2-1
        r_all = kmax_g[0] * R_G[0] + kmax_g[1] * R_G[1]  # every old source's basis rank, summed (the merged Q transport's width / the merged contraction's extra k)
        if use_stack and self._sites is not None and not self._sites:
            S = self._sites
            ar = SWArenas(dt)
            self._pool["__ar__"] = ar  # G-RB52: _read_stack temporaries alias the arenas
            S["T"] = SWSite("T", 1, 1, (2 * _K_STEADY - 1) * n + r_all + n, n, n, _SW_DEPTH_T, dt, ar)  # v54 (G-RB41 T): + the Sigma_h row block (Sigma_h w rides the transport call)  # v52 (G-RB39, 7.0 GB bar): v48's merged form at age 6 -- EVERY transport of the layer in ONE transposed depth-5 call [P_1..P_{k-1} A_1..A_k Q_1..Q_m]^T @ w (v49 split it to stay under 6.3 GB)
            _kkC = -(-(2 * n * _K_STEADY + r_all + 32) // 64) * 64  # v96: kk padded to a multiple of 64 (one extra Strassen level on C)
            S["C"] = SWSite("C", 1, 1, n, _kkC, n, _SW_DEPTH, dt, ar, nest=True)
            S["C"].d6, S["C"].mini = False, _MiniSite(dt)
            S["C"].xpair_on = _D6_XPAIR  # v101 (G-RB122)
            # (nestB is set below, after every site exists)
            _mini = S["C"].mini
            _h, _kA = n >> 6, _kkC >> 6  # d6 chunk A rows / B rows (half the depth-5 leaf dims)
            _mini.maxdims = {"stA": (_h, _kA), "B3": (_kA, _h), "T4": (_kA, _h), "leaf": (_h, _h)}
            _l4 = 7 ** 4  # lead of one depth-5 leaf slot (ca = 1)
            _mini.reserve(("*", "leaf"), 49 * _l4 * _h * _h)
            for _kd, _g in (("X", 3), ("L", 4)):  # X = the three qa slots, L = the four written slots
                _mini.reserve((_kd, "stA"), 4 * (_g if _kd == "L" else (2 if _D6_XPAIR else 1)) * _l4 * _h * _kA)  # v101: X pair
                _mini.reserve((_kd, "B3"), 3 * _g * _l4 * _kA * _h)
                _mini.reserve((_kd, "T4"), _g * _l4 * _kA * _h)
            _n5a = 1
            for _x in S["C"].roles[("st", "A", 5)]:
                _n5a *= _x
            _n5b = 1
            for _x in S["C"].roles[("st", "B", 5)]:
                _n5b *= _x
            _nleaf = 1
            for _x in S["C"].roles[("leaf",)]:
                _nleaf *= _x
            _cp = _mini.cap
            _lf = _nleaf + _cp[("*", "leaf")]  # A13: [leaf P | Pall | phase scratch]
            ar.reserve("A13", _lf + max(_cp[("X", "B3")] + _cp[("X", "T4")], _cp[("L", "T4")]))
            _o = 4 * _n5a // 7
            _mini.bind(ar, {
                ("*", "leaf"): ("A13", _nleaf),  # A13 tail behind the depth-5 leaf P (st1A/st3A dead at the leaf)
                ("X", "stA"): ("B2u2", _o),  # the never-written qa slots 4-6 of st5A (exactly 4*3 d6 slots)
                ("X", "B3"): ("A13", _lf), ("X", "T4"): ("A13", _lf + _cp[("X", "B3")]),
                ("L", "stA"): ("A2u3", 0),  # st4A's home (dead once the X phase read the qa quadrants)
                ("L", "B3"): ("B13", 4 * _n5b // 7),  # st5B slots 4-6 = R[4:7] (dead after the X phase)
                ("L", "T4"): ("A13", _lf),
            })
            # G-RB77 (B): BUF1 holds opT ((2k-1)n + r_all + n rows) then the (n, kk) contraction left factor; BUF2 the warm-column take of opT
            # then the LPA stacks (kg, n, 2n) of the two old groups
            _m_opT = (2 * _K_STEADY - 1) * n + r_all + n
            self._pool[("__bigcap__", "B1")] = max(_m_opT * n, n * _kkC)
            self._pool[("__bigcap__", "B2")] = max(_m_opT * n, max(kmax_g) * n * 2 * n)
            S["T2"] = SWSite("T2", 1, 1, 2 * n, n, n, _SW_DEPTH_T, dt, ar, nest=True)  # G-RB77 (i): [A_new^T; Sigma_h] @ w at full inner n when the prune splits the T call
            S["M1"] = SWSite("M1", 1, 1, n, n, n, _SW_DEPTH, dt, ar, nest=True)  # v53 (G-RB40 A): Sigma_z = w^T (Sigma_h w) as two depth-5 products (the einsum billed 3 n^3/layer)
            S["M2"] = SWSite("M2", 1, 1, n, n, n, _SW_DEPTH, dt, ar, nest=True)
            S["E1a"] = SWSite("E1a", 1, 1, n, n, _E_PAD, _E_DEPTH_Y, dt, ar, nest=True)  # v55 (G-RB42): P0^T @ [Om2|0]
            S["E1b"] = SWSite("E1b", 1, 1, n, n, _E_PAD, _E_DEPTH_Y, dt, ar, nest=True)  # P0 @ (.)
            S["E2"] = SWSite("E2", 1, 1, _E_PAD, n, 2 * n, _E_DEPTH_Q, dt, ar, nest=True)  # [Q1^T; 0] @ [P0 | A0] in ONE call  # second product on its own site: a site's result buffer is overwritten by its next call  # v48 (G-RB22 A1): [LP|LA|acc_all] @ [PAh^T; w; Qz_all^T] in ONE call at depth 5 (the two k-halves of v46/v47 only served the 5.5 GB bar)
            for G in (0, 1):
                rg, kg = R_G[G], kmax_g[G]
                S[("F", G)] = SWSite(f"F{G}", kg, kg, n, rg, 2 * n, _SW_DEPTH_FK[G], dt, ar, nest=True)  # Qz_b @ [F_P|F_A]_b
                S[("K", G)] = SWSite(f"K{G}", kg, kg, n, 2 * n, rg, _SW_DEPTH_FK[G], dt, ar, nest=True)  # [LP|LA]_b @ [F_P^T; F_A^T]_b
            for _nm in ("T2", "M2", "E1a", "E1b", "E2", ("F", 0), ("F", 1), ("K", 0), ("K", 1)):  # v99 (G-RB118): fixed (k, w) sites get nested B stacks
                S[_nm].nestB = True
            S["C"].d6nest = True
            S["T"].colnest = True  # v99: T's output rows vary per layer -> column nesting only  # v99: d6 runs on every C call (_D6_LAYERS = all, k padded to a multiple of 64)
            for _nm in _D6_SITES:  # v100 (G-RB121): fused extra level on these sites (after every site exists: the arena caps are final)
                _attach_d6(S[_nm], ar, dt)
            if _D6_T:
                _attach_d6_chunked(S["T"], ar, dt)
        sites = self._sites
        rows = []
        prune_ord = None  # G-RB70: (warm-first order[:K], order[K:]) from the previous ageing step; None -> unsplit transport
        prune_ord_all, prune_K = None, n
        for l, w in enumerate(mlp.weights):
            if w.dtype != dt:  # never taken on the grader (weights are float32)
                w = w.astype(dt)
            last = l == depth - 1
            wT = w.T
            mu_pre = wT @ mu
            g_l = self._g[l] if use_fit else 0.0
            kap_l = self._kap[l] if use_fit else 0.0

            # --- kappa3 read: transport legs and contract (sources on) / two-index transport (sources off)
            k_y = 0 if yP is None else yP.shape[0]
            m_g = [0 if oQ[G] is None else oQ[G].shape[0] for G in (0, 1)]
            m_o = m_g[0] + m_g[1]
            Tz = None
            k3z = None
            cw_T = None  # v54 (G-RB41 T): Sigma_h w from the merged transport call, when one ran
            if use_stack and (k_y + m_o) > 0:
                # transports
                # v52 (G-RB39): v48's merged form (G-RB22 A2) -- EVERY transport of the layer in one transposed Strassen call: [P_1..P_{k-1} A_1..A_k Q_1..Q_m]^T @ w.
                # Row blocks: Pz_b^T / Az_b^T then Qz_b^T; the (n,n) / (n,r) legs are read back as transposed views. (The newest young source has P = I: its block is wT itself.)
                ny = (2 * k_y - 1) * n if k_y else 0
                split = prune_ord is not None  # G-RB77 (i): the unprunable blocks (newest A, Sigma_h) run on T2 at full n
                _zp = 32 if (_D6_T and m_g[0] % 2) else 0  # v100 (G-RB121): 224 m_0 = 32 mod 64 -> 32 exact-zero rows (zero output rows, read by nobody)
                _opT_rows = ny + sum(m_g[G] * R_G[G] for G in (0, 1)) + n - (2 * n if split else 0) + _zp
                _m_opT = (2 * _K_STEADY - 1) * n + r_all + n
                opT = fnp.concatenate(
                    ([yP[i].T for i in range(k_y - 1)] + [yA[i].T for i in range(k_y - (1 if split else 0))] if k_y else [])
                    + [oQ[G][i].T for G in (0, 1) if m_g[G] for i in range(m_g[G])]
                    + ([_zbuf(self._pool, (32, n, "ZT"), dt)] if _zp else [])
                    + ([] if split else [cov]),  # v54 (G-RB41 T): Sigma_h (symmetric) as the last row block -> its rows of AllT are Sigma_h w
                    axis=0,
                    out=_big_view(self._pool, "B1", ("opT", n), (_m_opT, n), dt)[:_opT_rows],  # G-RB77 (B): no 44 MB temporary
                )
                if prune_ord is None:
                    AllT = sw_matmul(opT[None], w[None], sites["T"])[0]
                else:  # G-RB70: every row block except the newest A and Sigma_h has exact-zero columns at the cold neurons
                    ordK, ordC = prune_ord
                    M_ = opT.shape[0]
                    wP = fnp.take(w, prune_ord_all, axis=0)  # rows of w in cdf-descending order: [warm (K) | cold]
                    opTK = fnp.take(opT, ordK, axis=1, out=_big_view(self._pool, "B2", ("opTK", n), (_m_opT, n), dt)[:M_, :prune_K])  # G-RB77 (B)
                    AllT = sw_matmul(opTK[None], wP[None, :prune_K], sites["T"])[0]
                    # G-RB77 (i): the two full-K blocks on their own depth-5 site, [A_new^T; Sigma_h] @ w (rows 0..n-1: Az_new^T, n..2n-1: Sigma_h w)
                    AllT2 = sw_matmul(fnp.concatenate([yA[k_y - 1].T, cov], axis=0)[None], w[None], sites["T2"])[0]
                cw_T = AllT2[n:] if split else AllT[opT.shape[0] - n :]
                if k_y:
                    PAhT = AllT[: ny - n] if split else AllT[:ny]  # split: P_0..P_{k-2}, A_0..A_{k-2}; the newest A block is AllT2[:n]
                    Pzy = fnp.stack([PAhT[i * n : (i + 1) * n].T for i in range(k_y - 1)] + [wT], axis=0)
                    Azy = fnp.stack(
                        [PAhT[(k_y - 1 + i) * n : (k_y + i) * n].T for i in range(k_y - (1 if split else 0))] + ([AllT2[:n].T] if split else []),
                        axis=0,
                    )
                    _TZb = _buf(self._pool, (_STACK_SIZES[-1], n, 3 * _RK + 1) + ("ST", "TZ"), dt)  # v99: written in place (no _fill copy)
                    TZy = fnp.matmul(wT, yT, out=_TZb[:k_y])
                if m_o:
                    Qz = [None, None]
                    PAo = [None, None]
                    off_q = ny - (n if split else 0)
                    for G in (0, 1):
                        if m_g[G]:
                            rg = R_G[G]
                            Qz[G] = fnp.stack([AllT[off_q + i * rg : off_q + (i + 1) * rg].T for i in range(m_g[G])], axis=0)  # (m,n,r)
                            off_q += m_g[G] * rg
                            PAo[G] = sw_matmul(Qz[G], oFPA[G], sites[("F", G)])  # (m,n,2n) = [Pz_b | Az_b]
                    Pzo = [PAo[G][:, :, :n] for G in (0, 1) if m_g[G]]  # oldest group first = the oT/oF/oC/oCt order
                    Azo = [PAo[G][:, :, n:] for G in (0, 1) if m_g[G]]
                    TZo = fnp.matmul(wT, oT, out=_buf(self._pool, (_STACK_SIZES[-1], n, 3 * _RK + 1) + ("ST", "TZ"), dt)[k_y : k_y + m_o])
                # ONE Hadamard assembly over young + old on a fixed-size zero-padded stack (pooled out= buffers, no churn)
                tot = k_y + m_o
                S_ = tot  # v46 (G-RB19 A): exact stack width, no zero padding (read-stack flops are proportional to S_)
                # persistent out= targets; padding slots are views of persistent zero stacks (flopscope arrays are immutable)
                def _fill(parts, shape_tail, tag):
                    if "ST" + tag in _RS_ALIAS and "__ar__" in self._pool:  # G-RB52: dead before the layer's next call
                        buf = _arena_slot(self._pool, "ST" + tag, (_STACK_SIZES[-1],) + shape_tail, dt)[:S_]
                    else:
                        buf = _buf(self._pool, (_STACK_SIZES[-1],) + shape_tail + ("ST", tag), dt)[:S_]
                    pieces = [p for p in parts if p is not None]
                    if tot < S_:  # G-RB52: zero stack only if padding is used (S_ == tot: never)
                        zero = _zbuf(self._pool, (_STACK_SIZES[-1],) + shape_tail + ("ST0", tag), dt)
                        pieces.append(zero[: S_ - tot])
                    return fnp.concatenate(pieces, axis=0, out=buf)

                Pz_all = _fill([Pzy if k_y else None] + (Pzo if m_o else []), (n, n), "Pz")
                Az_all = _fill([Azy if k_y else None] + (Azo if m_o else []), (n, n), "Az")
                TZ_all = _buf(self._pool, (_STACK_SIZES[-1], n, 3 * _RK + 1) + ("ST", "TZ"), dt)[:S_]  # v99: TZy / TZo were written here by out=
                F_all = _fill([yF if k_y else None, oF if m_o else None], (5, n), "F")
                C_all = _fill([yC if k_y else None, oC if m_o else None], (5, _RK, n), "C")
                Ct_all = C_all.transpose(0, 1, 3, 2)  # v99 (G-RB118): the Ct stack is C's transposed VIEW (no carried copy, no _fill)
                if last:
                    k3z = _read_stack_diag(Pz_all, Az_all, TZ_all, F_all, C_all, Ct_all, self._pool)
                else:
                    LP, LA, th = _read_stack(Pz_all, Az_all, TZ_all, F_all, C_all, Ct_all, self._pool)
                    Tz = th
                    # v46 (G-RB19 C): ONE contraction for every source. Young (G-RB17 order): [LP_0..LP_{k-2} | LA_0..LA_{k-1} | LP_{k-1}] against
                    # [PAh^T ; w] (the newest source's Pz^T = w); old: acc_b = LP_b F_P^T + LA_b F_A^T (K site, in the basis) against Qz_b^T.
                    # sum_b (LP_b Pz_b^T + LA_b Az_b^T) = [young blocks | acc_0 .. acc_m] @ [PAh^T; w; Qz_0^T; ..; Qz_m^T]  (a block row times a block column)
                    lefts = [LP[i] for i in range(k_y - 1)] + [LA[i] for i in range(k_y)] + [LP[k_y - 1]] if k_y else []
                    rights = ([PAhT, AllT2[:n], w] if split else [PAhT, w]) if k_y else []  # [PAh^T; w]: the newest A^T block comes from T2 when split
                    kk = 2 * n * k_y
                    if m_o:
                        off = k_y
                        for G in (0, 1):
                            if m_g[G]:
                                LPA = fnp.concatenate(
                                    [LP[off : off + m_g[G]], LA[off : off + m_g[G]]], axis=2,
                                    out=_big_view(self._pool, "B2", ("LPA", G, n), (kmax_g[G], n, 2 * n), dt)[: m_g[G]],
                                )  # (m,n,2n); G-RB77 (B): shared BUF2 (opTK is dead by now)
                                acc = sw_matmul(LPA, oFPA[G].transpose(0, 2, 1), sites[("K", G)])  # v99: [F_P|F_A]^T as a VIEW (no carried transposed copy)  # (m,n,r) = LP_b F_P^T + LA_b F_A^T  (view, valid until this site's next call)
                                for i in range(m_g[G]):
                                    lefts.append(acc[i])
                                    rights.append(Qz[G][i].T)
                                kk += m_g[G] * R_G[G]
                                off += m_g[G]
                    sites["C"].d6 = l in _D6_LAYERS  # v97: d6 only on the chosen layers
                    if sites["C"].d6 and (kk // 32) % 2:  # v96: zero block pads k to a multiple of 64 (exact: adds 0)
                        lefts.append(_zbuf(self._pool, (n, 32, "ZL"), dt))
                        rights.append(_zbuf(self._pool, (32, n, "ZR"), dt))
                        kk += 32
                    left = fnp.concatenate(
                        lefts, axis=1, out=_big_view(self._pool, "B1", ("left", n), (n, 2 * n * _K_STEADY + r_all + 64), dt)[:, :kk]
                    )  # (n, kk); G-RB77 (B): shared BUF1 (opT is dead by now)
                    rbuf = _buf(self._pool, (2 * n * _K_STEADY + r_all + 64, n) + ("CR",), dt)[:kk]
                    right = fnp.concatenate(rights, axis=0, out=rbuf)
                    Tz = Tz + sw_matmul(left[None], right[None], sites["C"])[0]
                    k3z = fnp.diag(Tz)
            elif T is not None:  # off-shape fallback: v11's exact two-index transport of T
                w2 = w * w
                dT = fnp.diag(T)
                M = w2.T @ T
                if last:
                    k3z = 3.0 * fnp.sum(M * wT, axis=1) - 2.0 * ((w2 * w).T @ dT)
                else:
                    Tz = (M + 2.0 * (w * (T @ w)).T - 2.0 * (w2 * dT[:, None]).T) @ w
                    k3z = fnp.diag(Tz)
            else:
                k3z = fnp.zeros(n, dtype=dt)
                Tz = fnp.zeros((n, n), dtype=dt)

            # --- Gaussian marginals of the pre-activation
            _M1 = sites.get("M1") if (use_stack and sites) else None  # v53 (G-RB40 A)
            if last:
                cw = cw_T if cw_T is not None else (sw_matmul(cov[None], w[None], _M1)[0] if _M1 is not None else cov @ w)
                var_pre = fnp.maximum(fnp.sum(w * cw, axis=0), 1e-12)
            else:
                if _M1 is not None:
                    cw = cw_T if cw_T is not None else sw_matmul(cov[None], w[None], _M1)[0]  # v54: layer 0 only on M1
                    _Bn = None
                    if cw_T is not None and split:  # v99: cw = rows n:2n of T2's level-1 result (persistent) -> nested level-1 B for M2
                        _Bn = sites["T2"].nv.get("cwn")
                        if _Bn is None:
                            _d2 = sites["M2"].d
                            _Bn = sites["T2"].nv["cwn"] = sites["T2"].bufs[("up", 1)][:, n:].reshape(
                                (1,) + (2,) * _d2 + (n >> _d2,) + (2,) * _d2 + (n >> _d2,)
                            )
                    cov_pre = sw_matmul(wT[None], cw[None], sites["M2"], _Bn)[0]
                    cov_pre = 0.5 * (cov_pre + cov_pre.T)  # Strassen f32 rounding breaks exact symmetry (2.7e-6 > as_symmetric's atol 1e-6 downstream): symmetrise (2 n^2 ops)
                else:
                    cov_pre = fnp.einsum("ij,ia,jb->ab", cov, w, w)
                var_pre = fnp.maximum(fnp.diag(cov_pre), 1e-12)
            # --- v50 SSC kappa4 sectors from the transported modes (replaces the lean g var^2 / GSM sectors when modes exist)
            ssc_k4 = None
            if use_ssc and ssc_modes is not None:
                # v51 (G-RB34): FREE-TRANSPORT SSC -- every mode is built from quantities the chain already transports (no n^3 work):
                # I = diag(m_i), C = Sigma_z (cov_pre), Q_free from Tz (the kappa3 read), mu_pre and three n^2 matvecs (w^T t, w^T v, w^T 1).
                lam_l = self._lam[l]
                m_i = fnp.sum(w * w, axis=0)
                if last:
                    # Q is off at the last layer (Tz is diagonal-only there; lam[15] has zero Q rows): the (4) slice needs only d_I, d_C
                    Dl = fnp.stack([m_i, var_pre], axis=0)
                    ssc_k4 = 3.0 * fnp.einsum("ab,ai,bi->i", lam_l[:2, :2], Dl, Dl)
                else:
                    t_h, v_h, mbar, vbar = ssc_modes
                    qc_l = self._qc[l - 1]
                    tz = wT @ t_h
                    vz = wT @ v_h
                    oz = wT @ ones_n
                    Qf = (
                        (0.5 * qc_l[0:1] * mbar) * (Tz + Tz.T)
                        + qc_l[1:2] * (fnp.outer(tz, mu_pre) + fnp.outer(mu_pre, tz))
                        + qc_l[2:3] * fnp.outer(vz, vz)
                        + qc_l[3:4] * fnp.outer(oz, oz)
                    ) / vbar
                    fnp.fill_diagonal(Qf, 0.0)  # G-RB77 (C): was Qf - diag(diag(Qf)) (3 ops)
                    Bst = fnp.stack([fnp.diag(m_i), cov_pre, Qf], axis=0)  # (3,n,n)
                    Dl = fnp.stack([m_i, var_pre, fnp.diag(Qf)], axis=0)  # (3,n)  (diag(Qf) = 0 by construction)
                    ssc_k4 = 3.0 * fnp.einsum("ab,ai,bi->i", lam_l, Dl, Dl)
                    ssc_q22 = fnp.einsum("ab,ai,bj->ij", lam_l, Dl, Dl) + 2.0 * fnp.einsum("ab,aij,bij->ij", lam_l, Bst, Bst)
                    ssc_k31 = 2.0 * fnp.einsum("ab,ai,bij->ij", lam_l, Dl, Bst) + fnp.einsum("ab,aij,bi->ij", lam_l, Bst, Dl)
            sig = fnp.sqrt(var_pre)
            inv_sig = 1.0 / sig
            inv_var = inv_sig * inv_sig
            a = mu_pre * inv_sig
            pdf = norm.pdf(a).astype(dt)
            cdf = norm.cdf(a).astype(dt)
            sp = sig * pdf
            m1 = mu_pre * cdf + sp
            fh2 = pdf * inv_sig
            y = -a * inv_sig
            fh3 = y * fh2
            fh4 = y * fh3 - inv_var * fh2
            k6 = k3z * (1.0 / 6.0)
            k24 = ssc_k4 * (1.0 / 24.0) if ssc_k4 is not None else (g_l * (1.0 / 24.0)) * (var_pre * var_pre)
            g3 = k6 * fh3
            g4 = k24 * fh4
            g = g3 + g4
            m1c = m1 + g
            if last:
                if use_lc:
                    lc_xh = fnp.stack([mu_pre, sig, a, pdf, cdf, m1c, k3z], axis=-1)
                    lc_hh = fnp.maximum(lc_xh @ lc.hw + lc.hbias, 0.0)
                    m1c = m1c + _LC_SCALE * (lc_hh @ lc.hw1 + lc.hb1)
                rows.append(m1c)
                break

            # --- n x n ReLU closure (v11 verbatim): Sig (post-ReLU covariance), Tn (kappa3 (2,1)-slice of h, diag exact)
            mu2 = mu_pre * mu_pre
            m2 = (mu2 + var_pre) * cdf + mu_pre * sp
            m3 = (mu2 * mu_pre + 3.0 * mu_pre * var_pre) * cdf + (mu2 + 2.0 * var_pre) * sp
            fh = [m1, cdf, fh2, fh3]
            kinv = kcoef * inv_var  # G-RB77 (C): (k-2) inv_var for k = 3.._KGC-1 in one op (exact: small integers x inv_var)
            for k in range(3, _KGC):
                fh.append(y * fh[k] - kinv[k - 3] * fh[k - 1])
            Fh = fnp.stack(fh, axis=0)
            F2h = fnp.concatenate([m2[None, :], 2.0 * Fh[:_KGC]], axis=0)
            KF = k6 * Fh
            KF2 = k6 * F2h
            K24 = k24 * Fh
            K24_2 = k24 * F2h
            K = _KH + 1
            KFc = KF[3 : K + 3] + K24[4 : K + 4]
            KF2c = KF2[3 : K + 3] + K24_2[4 : K + 4]
            f0, f1_, f2_ = Fh[0:K], Fh[1 : K + 1], Fh[2 : K + 2]
            f3_ = Fh[3 : K + 3]
            f2h1 = F2h[1 : K + 1]
            f2h2 = F2h[2 : K + 2]
            f2h3 = F2h[3 : K + 3]
            zero = fnp.zeros((K, n), dtype=dt)
            # G-RB77 (C): U (K,6,n,2) and V (K,6,2,n) by ONE stack + reshape each (was 7 stacks each): U[k,c,i,t] = u_list[2c+t][k,i],
            # V[k,c,t,j] = v_list[2c+t][k,j]. V's reshape is contiguous (same layout as the nested stacks); U is a transposed view, consumed
            # only by the elementwise `U * coef` (contiguous result), so every matmul below sees the operand layouts of v59_p05.
            U = fnp.stack([f0, zero, KFc, zero, f2_, zero, F2h[0:K], KF2c, f1_, zero, f0, zero], axis=1).reshape((K, 6, 2, n)).transpose(0, 1, 3, 2)
            V = fnp.stack([f0, zero, f0, zero, f1_, zero, f0 + KFc, f0, f1_, zero, f2_, zero], axis=1).reshape((K, 6, 2, n))
            Uc = U * coef  # (K,6,n,2)
            C = cov_pre  # v99 (G-RB118): cov_pre is dead from here (var_pre / Bst already copied out), so zero its diagonal in place (no n^2 copy)
            fnp.fill_diagonal(C, 0.0)
            # power stack C^0..C^KH (op count: the two Horner loops of v11 were 36 ops; here 8 + 2 einsums, same FLOPs)
            cp = [fnp.ones((n, n), dtype=dt), C]
            for k in range(2, _KH + 1):
                cp.append(cp[-1] * C)
            Cpow = fnp.stack(cp, axis=0)
            # v46 (G-RB19 B): per-sector products, so the (K,6,n,n) / (K,5,n,n) temporaries (216 / 180 MB, ~450 MB of VmPeak with the einsum's
            # own copy) never exist; same contraction FLOPs, the 1/k! of the five Hadamard-series sectors folded into the left vector (+10 ops/layer)
            # v99 (G-RB118): the six sector matmul+einsum pairs batched in two halves (bit-identical per sector, same FLOPs; a 63 MB transient --
            # the one-shot batch held 126 MB and moved in-process VmPeak +87 MB more)
            _SVg = [fnp.einsum("kcij,kij->cij", fnp.matmul(Uc[:, c0 : c0 + 3], V[:, c0 : c0 + 3]), Cpow) for c0 in (0, 3)]
            S_ff, Zs, S21, A21, Pser, Qser = (_SVg[c // 3][c % 3] for c in range(6))
            A5 = fnp.stack([f2_, f2h2, f3_, f2h3, f2h1], axis=0) * inv_fact_d22[None, :, None]
            B5 = fnp.stack([f2_, f2_, f1_, f1_, f3_], axis=0)
            acc_sig, acc_t, acc_sig31, acc_t31a, acc_t31b = (
                fnp.einsum("ki,kij,kj->ij", A5[r], Cpow, B5[r]) for r in range(5)
            )
            if ssc_k4 is not None:
                Qcoef = ssc_q22 * (0.25 * (0.96 if l >= 8 else 1.0))  # G-RB96: deep-layer (l>=8) Q22 sector x0.96
                fnp.fill_diagonal(Qcoef, 0.0)  # G-RB77 (C)
                K31_row = ssc_k31 * ((0.72 * (0.8 if l >= 8 else 1.0)) / 6.0)  # G-RB91 K31 x0.9 -> G-RB103 x0.72 (radial share of the two-term law); G-RB96 deep x0.8
                # G-RB103: al07 two-term (3,1) law, second term kappa3_a T_aab / v_a (kai_leal_gonzalez forum #18246 prose; credit theirs), 3 n^2 ops
                K31_row = K31_row + (1.0 / 6.0) * (k3z / var_pre)[:, None] * Tz
                fnp.fill_diagonal(K31_row, 0.0)
                K31_col = K31_row.T
            else:
                Qcoef = (g_l * (1.0 / 12.0)) * (fnp.outer(var_pre, var_pre) + 2.0 * C * C)
                fnp.fill_diagonal(Qcoef, 0.0)  # G-RB77 (C)
                K31_row = (g_l * (1.0 / 6.0)) * (var_pre[:, None] * C)
                K31_col = (g_l * (1.0 / 6.0)) * (var_pre[None, :] * C)
            X = Zs + (Tz * 0.5) * S21
            Sig = (
                (S_ff + (X + X.T))
                - fnp.outer(g, g)
                + Qcoef * acc_sig
                + K31_row * acc_sig31
                + K31_col * acc_sig31.T
            )
            g2 = k6 * F2h[3] + k24 * F2h[4]
            m2c = m2 + g2
            m3c = m3 + k3z * cdf + (6.0 * k24) * fh2
            Tn = (
                (A21 + Tz * Pser + Tz.T * Qser - fnp.outer(g2, g))
                - 2.0 * m1c[:, None] * Sig
                + Qcoef * acc_t
                + K31_row * acc_t31a
                + K31_col * acc_t31b
            )
            kh = m3c - 3.0 * m2c * m1c + 2.0 * m1c * m1c * m1c
            vh = fnp.maximum(m2c - m1c * m1c, 0.0)
            fnp.fill_diagonal(Tn, kh)
            fnp.fill_diagonal(Sig, vh)
            if use_ssc:
                # --- v51: the h-side quantities the next transport needs (uncorrected m1c; exact-diagonal Sig / Tn)
                ssc_modes = (kh, vh, fnp.mean(m1c), fnp.mean(vh))
            mu_carry = m1c  # UNCORRECTED m1c stays the input of Sig / Tn / birth (prototype hook point)
            if use_lc and l >= _LC_L0:
                # the 21 raw per-neuron columns of research/lc/lcfeat.NAMES (G-LC / v10 plumbing); Tz's diagonal is kept (the birth needs it)
                lc_isg3 = inv_sig * inv_var
                lc_skew = k3z * lc_isg3
                lc_rs = fnp.sum(C, axis=1) * inv_sig
                lc_rq = fnp.sqrt(fnp.einsum("ij,ij->i", C, C)) * inv_sig
                lc_rt = fnp.sum(Tz, axis=1) - k3z
                lc_rt2 = fnp.einsum("ij,ij->i", Tz, Tz) - k3z * k3z
                lc_x = fnp.stack(
                    [
                        mu_pre,  # mu_z
                        sig,  # sz
                        a,  # alpha
                        pdf,
                        cdf,
                        sp,  # sz_pdf
                        m1c,  # feature "mu_pre" (post-ReLU, pre-hook)
                        g,  # corr_marg = m1c - m1
                        lc_skew,
                        lc_rs,  # rs_z
                        lc_rq,  # rq_z
                        lc_rt * lc_isg3,  # trs_z
                        fnp.sqrt(fnp.maximum(lc_rt2, 0.0)) * lc_isg3,  # trq_z
                        vh,  # var_h
                        fnp.sum(Sig, axis=1) - vh,  # rs_h
                        fnp.sum(Tn, axis=1) - kh,  # ts_h
                        kh,  # k3_h
                        a * a,  # alpha2
                        fh2,  # pdf_over_sz
                        k3z,  # k3
                        fnp.abs(lc_skew),  # (weight 0; only its neuron-mean is a feature)
                    ],
                    axis=-1,
                )
                lc_c = fnp.mean(lc_x, axis=0) @ lc.wm + self._lc_bias[l]
                lc_h1 = fnp.maximum(lc_x @ lc.wr + lc_c, 0.0)
                lc_h2 = fnp.maximum(lc_h1 @ lc.w1 + lc.b1, 0.0)
                mu_carry = m1c + (_LC_SCALE * (0.9 if l >= 8 else 1.0)) * (lc_h2 @ lc.w2 + lc.b2)  # G-RB109: deep-layer corrector strength x0.9 (twin hsD0.9; last layer unchanged)
            cov = flops.as_symmetric(Sig, symmetry=(0, 1))
            mu = mu_carry
            rows.append(mu)

            if not use_stack:
                T = Tn
                continue

            # --- age the carried legs (h = Phi o z); G-RB70: with the PRUNED gate (cold neurons' legs dropped); the birth below keeps Phi
            Phi = cdf[:, None]
            prune_ord = None
            if _PRUNE > 0.0:
                cdfp = fnp.where(cdf >= _PRUNE, cdf, fnp.zeros_like(cdf))
                n_warm = fnp.flatnonzero(cdf >= _PRUNE).shape[0]
                prune_K = min(n, -(-n_warm // 64) * 64) if _D6_T else min(n, -(-n_warm // 32) * 32)  # v100 (G-RB121): T's inner dim even at depth 6
                if prune_K < n:
                    prune_ord_all = fnp.argsort(-cdf)
                    prune_ord = (prune_ord_all[:prune_K], prune_ord_all[prune_K:])
            else:
                cdfp = cdf
            Phip = cdfp[:, None]
            if k_y:
                yP, yA, yT = Phip * Pzy, Phip * Azy, Phip * TZy
            if m_o:
                oQ = [Phip * Qz[G] if m_g[G] else None for G in (0, 1)]
                oT = Phip * TZo

            # --- birth of the layer-l source (P = I, A = Phi o C_z, rank-16 D21 legs, kappa4 feed, adjustment leg)
            A1 = Phi * C
            Om = w[
                :, : _RK + _OS
            ]  # Gaussian columns of this layer's weights: the range-finder test matrix
            if Tz is not None and (k_y + m_o) > 0:
                D21 = Tz - fnp.diag(k3z)
                Ud, Bd = _rank_rf(D21, Om, _RK)
            else:
                Ud, Bd = fnp.zeros((n, _RK), dtype=dt), fnp.zeros((_RK, n), dtype=dt)
            T1 = Phi * Bd.T
            T2 = fh2[:, None] * Ud
            c1 = Ud.T * (0.5 * fh3)[None, :]
            c2 = Bd * (0.5 * fh2)[None, :]
            c3 = 0.5 * Bd
            c4 = Ud.T
            u = (kap_l * (1.0 / 6.0)) * fh2
            # coincident entries already in the live factored tensor: aged sources = Phi^2 Phi o their z-read; newborn at P = I
            That = (
                ((cdfp * cdfp)[:, None] * cdfp[None, :]) * Tz
                if (Tz is not None and (k_y + m_o) > 0)
                else fnp.zeros((n, n), dtype=dt)
            )
            A1f2 = A1 * fh2[None, :]
            Y11 = A1f2 + T1 @ c1 + T2 @ c2
            X12 = T2 @ c3
            X21 = T1 @ c4
            # newborn blocks at P = I (read_block_identity): every X leg and the Y legs of G12/G21 are zero-diagonal (C_z, D21 are),
            # so only the Hadamard terms survive plus diag(Y11) X11^T and the feed's 3u (A1 f1)^T
            A1f1 = A1 * cdf[None, :]
            That = That + (A1 * Y11 + X12 * A1f2 + 0.5 * (X21 * (A1 * fh3[None, :])) + u[:, None] * A1f1)
            That = That + fnp.diag(Y11)[:, None] * A1.T + u[:, None] * A1f1.T
            Dadj = Tn - That
            d3 = fnp.diag(Dadj)  # a VIEW of Dadj's diagonal (numpy diagonal semantics): Dadj must not be zeroed in place (d3 is read by s_adj)
            Voff = 3.0 * (Dadj - fnp.diag(d3)).T
            tfit = fnp.einsum("ij,ij->j", Voff, A1) / fnp.maximum(
                fnp.einsum("ij,ij->j", A1, A1), 1e-30
            )
            Rres = Voff - A1 * tfit[None, :]
            Zn, c5 = _rank_rf(Rres, Om, _RK)
            s_adj = d3 - fnp.einsum("ij,ji->i", Zn, c5)
            newT = fnp.concatenate([T1, T2, Zn, u[:, None]], axis=1)[None]  # (1,n,49)
            newF = fnp.stack([cdf, fh2, fh3, tfit, s_adj], axis=0)[None]  # (1,5,n)
            newC = fnp.stack([c1, c2, c3, c4, c5], axis=0)[None]  # (1,5,16,n)
            # v99 (G-RB118): no newCt -- the read takes Ct as C's transposed view
            if k_y:
                yP = fnp.concatenate([yP, I_n[None]], axis=0)
                yA = fnp.concatenate([yA, A1[None]], axis=0)
                yT = fnp.concatenate([yT, newT], axis=0)
                yF = fnp.concatenate([yF, newF], axis=0)
                yC = fnp.concatenate([yC, newC], axis=0)
            else:
                yP, yA, yT, yF, yC = I_n[None], A1[None], newT, newF, newC
            y_birth.append(l)

            # --- old tier: the oldest young source reaches age _AGE_OLD at the next transport -> own rank-384 basis
            if l + 1 - y_birth[0] >= _AGE_OLD:
                P0, A0 = yP[0], yA[0]
                Om2 = w[:, :_R_OLD]  # G-RB57 (Lens D): no oversampling
                _E = sites.get("E1a") if (use_stack and sites) else None  # v54 (G-RB41 E): the entry's n x n x 392 products at depth _E_DEPTH on a 416 zero pad
                if _E is not None:
                    _ros = _R_OLD
                    Om2p = Om2 if _E_PAD == _ros else fnp.concatenate([Om2, _zbuf(self._pool, (n, _E_PAD - _ros), dt)], axis=1)  # (n, 416): 24 exact zero columns
                    _Y1 = sw_matmul(P0.T[None], Om2p[None], _E)  # v99: E1a's nested level-1 result has exactly E1b's nested B shape (n x 384, d 3)
                    Y = sw_matmul(P0[None], _Y1, sites["E1b"], _E.bufs[("up", 1, "nest")])[0][:, :_ros]  # zero columns in -> zero columns out
                    Q1, _ = fnp.linalg.qr(Y)  # (n, r+os)
                    Q1Tp = Q1.T if _E_PAD == _ros else fnp.concatenate([Q1.T, _zbuf(self._pool, (_E_PAD - _ros, n), dt)], axis=0)  # (416, n)
                    QPA = sw_matmul(Q1Tp[None], fnp.concatenate([P0, A0], axis=1)[None], sites["E2"])[0]  # (416, 2n): QP | QA in one product
                    QP, QA = QPA[:_ros, :n], QPA[:_ros, n:]
                else:
                    Y = P0 @ (P0.T @ Om2)  # A0 lies in P0's range (same linear transport of a different birth leg): sketch P0 only
                    Q1, _ = fnp.linalg.qr(Y)  # (n, r+os); no power iteration here (f64: +1.4 % e2e, 4 n^2 r matmuls saved per entry)
                    QP, QA = Q1.T @ P0, Q1.T @ A0  # (r+os, n)
                Qb = Q1  # G-RB57 (Lens D): the QR range of the r-column sketch is the basis (no S / eigh / rotation)
                FP, FA = QP, QA  # (r, n)
                FPA = fnp.concatenate([FP, FA], axis=1)  # (r, 2n): the two static coefficient blocks of this source
                if oQ[1] is not None:
                    oQ[1] = fnp.concatenate([oQ[1], Qb[None]], axis=0)
                    oFPA[1] = fnp.concatenate([oFPA[1], FPA[None]], axis=0)
                else:
                    oQ[1], oFPA[1], oFPAt[1] = Qb[None], FPA[None], FPA.T[None]
                if oT is not None:
                    oT = fnp.concatenate([oT, yT[:1]], axis=0)
                    oF = fnp.concatenate([oF, yF[:1]], axis=0)
                    oC = fnp.concatenate([oC, yC[:1]], axis=0)
                else:
                    oT, oF, oC = yT[:1], yF[:1], yC[:1]
                o_birth[1].append(y_birth[0])
                yP, yA, yT, yF, yC = yP[1:], yA[1:], yT[1:], yF[1:], yC[1:]
                y_birth = y_birth[1:]

            # --- G-RB12 nested tier: the oldest rank-384 source reaches age _AGE_OLD2 at the next transport -> rank-_R_OLD2 sub-basis of
            # its CURRENT legs L = Q_b F (Q_b is transported, no longer orthonormal): Q_b = U R, eigh(R F F^T R^T) -> V2, Q_b <- U V2, F <- V2^T R F
            if o_birth[1] and l + 1 - o_birth[1][0] >= _AGE_OLD2:
                Qb0, FPA0 = oQ[1][0], oFPA[1][0]  # (n, 384), (384, 2n)
                U_, R_ = fnp.linalg.qr(Qb0)
                Gm = R_ @ (fnp.einsum("ik,jk->ij", FPA0, FPA0) @ R_.T)  # G-RB57: self-Gram einsum (0.5x billed; no as_symmetric tag added)
                _ev2, V_ = fnp.linalg.eigh(Gm)  # ascending: keep the LAST _R_OLD2 eigenvectors
                V2 = V_[:, _R_OLD - _R_OLD2 :]
                Qn = U_ @ V2  # (n, r2)
                FPAn = (V2.T @ R_) @ FPA0  # (r2, 2n)
                if oQ[0] is not None:
                    oQ[0] = fnp.concatenate([oQ[0], Qn[None]], axis=0)
                    oFPA[0] = fnp.concatenate([oFPA[0], FPAn[None]], axis=0)
                else:
                    oQ[0], oFPA[0], oFPAt[0] = Qn[None], FPAn[None], FPAn.T[None]
                o_birth[0].append(o_birth[1][0])
                if oQ[1].shape[0] > 1:
                    oQ[1], oFPA[1], oFPAt[1] = oQ[1][1:], oFPA[1][1:], oFPAt[1][1:]
                else:
                    oQ[1] = oFPA[1] = oFPAt[1] = None
                o_birth[1] = o_birth[1][1:]

        return fnp.stack(rows, axis=0)
