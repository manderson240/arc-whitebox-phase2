# G-RB136 — the non-tree C_jk κ3_ijk birth at a ReLU (derivation and MC check)

Credit: the term's existence and its ablation value (1.56x in a K = 4 research chain) are Susupro's (forum 18254, prose only,
`research/forum/MINING_20261018.md` §3). The derivation below is ours, from textbook Edgeworth / Price / Stein identities.

## 1. Setting and notation

Pre-activation z ∈ R^n with mean μ, covariance Σ (off-diagonal part C, diagonal σ²) and third cumulant κ3_z (no higher
cumulants at the order considered). h = φ(z), φ = ReLU, applied per neuron. Price coefficients
f_m(i) = E_G[φ^(m)(z_i)] under the Gaussian marginal N(μ_i, σ_i²): f1 = Φ(μ/σ), f2 = φ_N(μ/σ)/σ, f3 = −(μ/σ²) f2
(these are `R.coeffs_relu` fh[1..3], the same coefficients the chain's births use).

## 2. First order in κ3 (Edgeworth / Stein)

For a smooth test function F, to first order in κ3_z

    E[F(z)] = E_G[F] + (1/6) Σ_{p,q,r} κ3_z[p,q,r] E_G[∂_p ∂_q ∂_r F]        (1)

(E_G: Gaussian with the same μ, Σ). Take the joint cumulant κ3[h_i, h_j, h_k] for **distinct** i, j, k and collect the part
linear in the **all-distinct** entry κ3_z[i,j,k]:

- κ3[h_i,h_j,h_k] = E[h_i h_j h_k] − E[h_i]E[h_j h_k] − (2 perms) + 2E[h_i]E[h_j]E[h_k].
- ∂_p of a product of h's vanishes unless p indexes one of its factors, so κ3_z[i,j,k] with i, j, k all distinct enters
  ONLY E[h_i h_j h_k] (the lower moments involve at most two of the three indices). In (1) the 3! orderings of (i,j,k) give
  6 x (1/6) = 1, so

      δκ3[h_i,h_j,h_k] = κ3_z[i,j,k] · E_G[φ'(z_i) φ'(z_j) φ'(z_k)].                                      (2)

The repeated-index entries κ3_z[i,i,j] give the TREE births already in the chain (D21 legs, see Step 0 in the ledger).

## 3. Expansion of the Gaussian 3-point function in C (Price / Mehler)

For jointly Gaussian (z_i, z_j, z_k) with off-diagonal covariances C_ij, C_ik, C_jk,

    E_G[g_i g_j g_k] = Σ_{a,b,c ≥ 0} C_ij^a C_ik^b C_jk^c / (a! b! c!) · E[g_i^(a+b)] E[g_j^(a+c)] E[g_k^(b+c)].

With g = φ' (so E[g^(m)] = f_{m+1}):

- order C^0: f1_i f1_j f1_k — the chain's ageing of carried κ3 by the gate (present);
- **order C^1 (the registered term):**

      Δ_ijk = κ3_z[i,j,k] · ( f1_i f2_j f2_k C_jk + f2_i f1_j f2_k C_ik + f2_i f2_j f1_k C_ij ),   i ≠ j ≠ k ≠ i.   (3)

This is first order in κ3 and first order in C, the same order as the chain's existing D21 tree births (which are linear in C).
Order C^2 and higher (e.g. C_ij C_jk, C_jk^2) are not included.

Graph picture: in (3) the κ3 hyperedge {i,j,k} and the covariance edge {j,k} close a loop, so (3) is the non-tree birth; the
tree births use κ3_z[i,i,j] with C on a different leg.

## 4. How the term enters the chain (rb136/s136.py, switch SW['nt'])

- Carrier: one dense n×n×n f64 tensor E (unsymmetrised; the cumulant it represents is Sym(E)), holding all non-tree births and
  their descendants. Per layer: E is transported to z like every leg (E ×1 W ×2 W ×3 W, in place); its Sym (2,1) slice and (3)
  diagonal are added to T_z exactly as a source's read (and to the coincident-entry bookkeeping `That` through `per_src_T`, as
  aged sources are).
- Birth at the ReLU of layer l ≥ 1: κ3_z[i,j,k] = Sym(K + E), where K is the unsymmetrised tensor of the factored sources
  (K_ijk = Σ_sources Σ_blocks α P_im X_jm Y_km, built densely from the same z legs the chain reads), so the input is the chain's
  FULL current z-side κ3, not a truncation of it. Then E ← Φ⊗Φ⊗Φ ∘ E + mult · mask_distinct ∘ S ∘ (K + E), with
  S_ijk = f1_i G_jk + f1_j G_ik + f1_k G_ij, G = (f2 f2ᵀ) ∘ C. Φ is the pruned gate the chain ages its legs with; f1, f2 are
  the unpruned coefficients its births use.
- Double counting: the new term is masked to i ≠ j ≠ k ≠ i. The (2,1) and (3) h-slices are fixed by the bivariate pair step
  plus the adjustment leg (Dadj = T_h − That), which already carry C × κ3_iij to all orders; the carried part of E enters
  `That` like an aged source, so the adjustment absorbs its coincident entries. (Hadamard with symmetric S, the mask, the gate
  and the transport all commute with Sym, so E never has to be symmetrised.)
- Exactness check of K (switch `ntcheck`): the Sym (2,1) read of K on a 32×32 block must equal the sum of the sources' own
  reads (`per_src_T`) at every layer; logged per layer in results_chk.jsonl.
- Arms: mult = +1 (arm), −1 (mutant), placebo = mult +1 with C replaced, per layer, by a random symmetric zero-diagonal
  matrix with the same Frobenius norm (seed 136000 + l). Default (no 'nt'): code path untouched, control bit-identical.

## 5. Monte-Carlo check (rb136/mc_check.py; n = 64, N = 1e6, before any arm was read)

Construction in which, at O(ε), the ONLY non-Gaussian cumulant is the all-distinct κ3:
z(ε) = μ + L g + M y + ε Q(y), g, y independent standard normals; 16 'product' neurons load no y linearly and each receive
3 products y_p y_q (p ≠ q); the 48 'y' neurons each load exactly one y. Then κ3_z[a,b,c] = ε(m_b m_c + …) only for
(product, y, y) triples, κ3_z[i,i,j] = 0, and by Stein's lemma the O(ε) change of κ3[h] on distinct triples is EXACTLY (2).
Common random numbers and a central difference D = (κ̂3_h(+ε) − κ̂3_h(−ε)) / 2ε remove the Gaussian births and all even
orders in ε. Off-diagonal |ρ| mean 0.354 (max 0.96). Regression over the 1152 signal triples:

| ε | β_tree (f1³κ3) | β_nt (term (3)) | rms resid: tree only | tree + nt | tree − nt (mutant) | exact E_G[1·1·1] | rms D on 248,832 null triples |
|---|---|---|---|---|---|---|---|
| 0.30 | 0.953 ± 0.003 | **1.021 ± 0.004** | 0.0512 | **0.0052** | 0.1044 | 0.0064 | 0.0015 |
| 0.15 | 0.977 ± 0.002 | **1.052 ± 0.003** | 0.0545 | **0.0034** | 0.1077 | 0.0029 | 0.0016 |

(rms D = 0.13; rms of term (3) = 0.053.) The term has the right sign and unit coefficient; adding it cuts the residual
~10-16x, negating it doubles the residual, and the remainder (≈ 3-5 % of D) is the C² truncation (the exact Gaussian
3-point function closes it). This also confirms fh[2] is the Price coefficient E[φ''] and not a Hermite-normalised one.
**PASS.** Raw outputs: mc_check_N1000000_e0.3.json, mc_check_N1000000_e0.15.json.
