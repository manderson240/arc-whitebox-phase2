# Rebuild S1 — ARC factorized K=3 + 504aldo's prose additions, in our notation (2026-10-06)

Sources (public prose only): Wu et al. 2026, arXiv:2605.05179 App. S.4.3 (eqs 15–20, step (d)ii); forum thread 18218
(team 504aldo, posts 1, 3, 5 — §2.1–2.5, §4 rows 2–3, §5; AndreasHad04 post 4 for the pre/post C question). No participant
code was opened. Credit: the three accuracy steps (memoryless κ4 core `G_off = λ_l C_pre_off` with exact diagonal, D21 feedback
into the birth factors, exact final-layer trim) are 504aldo's; the factorized representation and the diagonal adjustment are ARC's.

Conventions. Weights stored (in, out): z_l = W_lᵀ h_{l-1}, Σ_z = Wᵀ Σ_h W. F(A,B,C) := Σ_j Sym(A_j⊗B_j⊗C_j) with Sym the AVERAGE over
the 6 permutations (paper eq 15). Slices (paper eq 16): D3_i = Σ_j (A∘B∘C)_{ij}; D21_{ik} = κ3(i,i,k) = ⅓Σ_j[(B∘C)_{ij}A_{kj} +
(A∘C)_{ij}B_{kj} + (A∘B)_{ij}C_{kj}] — as a matrix its diagonal is D3 automatically, so the whole read is ONE n×n matrix `Tz`
(our proto_cov4 convention: Tz[a,b] = κ3(z_a,z_a,z_b), diag = κ3(a,a,a)). Our hub term w·(aae+aea+eaa) is F(a, a, 3w·e).
f_k := Hermite coefficient E[φ^{(k)}(z)] of ReLU under N(μ_z,σ_z²): f_1 = Φ(α), f_2 = φ(α)/σ, f_3 = −α φ/σ², f_4 = He₂(−α)φ/σ³
(proto_r2.coeffs_relu, index k).

## Per layer
1. Linear: μ_z, Σ_z, and the κ3 read Tz from the transported legs P_X = Wᵀ X (X ∈ {A,B,C}).
2. κ4 (z side). `k4exact`: κ4_z,i = m_i (Wᵀ K̃ W)_ii with m_i = Σ_a W_ai², K̃ = diag(κ4_h) + off-diag 2·K31_h — the exact
   W^{⊗4} transport of the core model κ4_h = Sym(G_h ⊗ c_h I) (all 4!/(2!2!) multinomial terms; c_h cancels; derivation: the
   (4)-slice of Sym(G⊗cI) is c·G_ii, (2,2) is (c/6)(G_ii+G_jj), (3,1) is (c/2)G_ij, (2,1,1) is (c/6)G_jk, (1,1,1,1) is 0).
   K31_h,ab is modelled to first order as Φ_a²·κ_l·C_h,ab (κ4(h_a,h_a,h_a,h_b) ≈ Φ_a³Φ_b κ_l C_z,ab and C_h ≈ Φ_aΦ_b C_z);
   symmetrised: K̃_ab = κ_l(Φ_a²+Φ_b²)C_h,ab. The z-side sectors fed to the ReLU closure: K31_z = κ_l C_z,off (504aldo's law in
   our normalisation: κ_l = (c/2)λ_l; fitted per layer on own nets 9000/9001 MC, `fit_kappa.py` → κ ≈ g·var within ±15 %, i.e.
   the GSM model's K31 was already right), Q22_z = (κ4_i+κ4_j)/6. `lean`: κ4 = g_l var², Q/K31 = GSM (our exact chain).
3. ReLU n×n closure: `proto_cov4.relu_step_ext(μ_z, Σ_z, Tz, κ4, Q22, K31)` → μ_h, Σ_h (exact diag), T_h (κ3_h (2,1)-slice,
   exact (3)-diag). Per-neuron κ4_h from the first-order Edgeworth marginal: E[h⁴] = m4_G + 4κ3 m1_G + κ4 Φ
   (f=relu⁴: f''' = 24 relu, f'''' = 24·1_{z>0}), m4_G = (μ⁴+6μ²σ²+3σ⁴)Φ + (μ³+5μσ²)σφ; κ4_h = m4 − 4m3m1 − 3m2² + 12m2m1² − 6m1⁴
   with the corrected m1,m2,m3 of the closure.
4. New (1,1,1) factors (hub form, one column per neuron j; the hub is the middle vertex of the two-legged diagrams):
   - transported (eq 19): (f_1∘P_A, f_1∘P_B, f_1∘P_C)  [J columns]
   - two-legged, k2 = 1 (eq 18; hub j carries f_{1+k3}): A = 3I, B[:,j] = f_1∘C_z[:,j] + ½ f_2∘D21[:,j],
     C[:,j] = f_2(j) f_1∘C_z[:,j] + ½ f_3(j) f_1∘D21[j,:] + ½ f_2(j) f_2∘D21[:,j] + ¼ f_3(j) f_2∘Q22[j,:]
     (Q_{(2,1)}(i,j) = κ3(i,i,j) = D21[i,j]; Q_{(1,2)}(i,j) = D21[j,i]; Q_{(1,1)} = C_z; Q_{(2,2)} = Q22, all zero-diagonal.)
     The k=(1,1,1,1) term alone (B = f_1∘C_z, C = f_2(j) f_1∘C_z[:,j]) is our chain's newborn; the D21/Q22 terms are the
     "D21 feedback into the birth factors" (504aldo §2.3), full rank here (their rank-16 is a cost version).
   - two-legged, k2 = 2: A = 1.5I, B[:,j] = f_1∘D21[j,:] + ½ f_2∘Q22[:,j],
     C[:,j] = f_3(j) f_1∘C_z[:,j] + ½ f_4(j) f_1∘D21[j,:] + ½ f_3(j) f_2∘D21[:,j] + ¼ f_4(j) f_2∘Q22[j,:]
   - κ4 (2,1,1) feed (eq 20 with the core model, = G-B1's vertex): κ4_z(i,i,j,k) = (κ_l/3) C_z,jk ⇒ Σ_{A3} ½f_2 f_1 f_1 κ4 =
     3 Sym(u⊗M′), u = (κ_l/6) f_2, M′ = f_1 C_z f_1 ⇒ A = I, B = M′, C[:,j] = 3u (= ½κ_l f_2, the same vector for every hub).
   Paper eq (18) as typeset puts diag(f_{k2+k3}) on the outer leg; the diagram (middle vertex has k2+k3 Hermite legs) fixes it on
   the hub, which is what is implemented.
5. Coincident-entry adjustment (paper step (d)ii): read D3̂, D21̂ of the assembled h-side factors F̂ with eq (16); Δ21 = T_h,off −
   D21̂_off, Δ3 = diag T_h − D3̂; append ONE n-column block (e_j, e_j, v_j), v_j = 3·Δ21[j,:] + Δ3_j e_j. Check: F(e_j,e_j,v_j)_{iik}
   = (2/6)·v_i[k] = Δ21[i,k] for i≠k (the two identity legs must sit on the equal indices, 2 of 6 permutations), _{iii} = v_i[i] = Δ3_i,
   and zero on the (1,1,1) slice. (The paper's eq 17 as typeset, F(D3·1ᵀ, I, I), has a (2,1) spill of D3_k/3; the combined block
   above is exact for both slices at once and is the same object after transport as our Thm-8 / "sect" correction.)
   J grows by 4n per layer (ARC: 6n, with a general metric and two separate adjustment blocks).
6. Last layer (`trim`): mean only, μ_out = m1 + κ3/6 f_3 + κ4/24 f_4 with κ3 = D3_z (elementwise read of the transported legs,
   no n×n slice) — identical to the closure's m1c by construction.

Ladder: R0 lean (control vs our exact SBk1 chain) → R1 +d21 (the D21/Q22 legs and the k2=2 block) → R2 +k4exact (κ4 diag transport,
K31 = κC, Q22 from κ4) → R3 +feed → R4 trim. Each: e2e raw final MSE vs the 1e9 truth, FIT nets 0/2/4.

## S2/S3 — cost structure (per-source {P, A, thin} form; 504aldo's "7 → 4 units per source-layer" re-derived)
Measured (G-RB2, net 0): rank-16 D21 legs are better than full (−1.7 %); adjustment leg = A·d(t) + diag(s) + rank-16 residual
costs +1.3 % (dropping the residual: 19×); shared basis r=384 (age ≥ 4) / 224 (age ≥ 7) holds ≥ 0.995 of the old-source energy.

Every birth block of source b is Σ_j Sym(α P_j ⊗ X_j ⊗ Y_j) with P = I at birth and X, Y ∈ {P·d(·), A·d(·), thin}:
  G11 (α=3): X = A, Y = A d(f2) + T1 c1 + T2 c2        [D21 ≈ U B (range finder, rank 16): T1 = f1∘Bᵀ, T2 = f2∘U (n×16, transported);
  G12 (α=3): X = T2 c3, Y = A d(f2)                     c1 = Uᵀ d(½f3), c2 = B d(½f2), c3 = ½B, c4 = Uᵀ (16×n, static)]
  G21 (α=1.5): X = T1 c4, Y = A d(f3)
  feed (α=1): X = A d(f1), Y = 3u 1ᵀ (u = (κ_l/6) f2, transported vector)
  adj (α=1): X = P, Y = A d(t) + P d(s) + Z c5         [R = Vadj_off − A d(t); Z = range finder(R) n×16; c5 = Zᵀ R; s = diag Vadj]
Transport (h→z): P, A dense (2 units), T1, T2, Z, u thin. Read (eq 16) of Σ_j Sym(αP_j⊗X_j⊗Y_j) = (α/3)[(X∘Y)Pᵀ + (P∘Y)Xᵀ + (P∘X)Yᵀ]:
thin legs are FORMED as dense n×n (n²·16 flops) and enter the Hadamards; the right factor is P or A (→ accumulate LP, LA) or thin
(→ (n×n)@(n×16)@(16×n)). Per source-layer: 2 transports + 2 dense contractions (LP Pᵀ + LA Aᵀ, one batched matmul) = 4 units + O(n²).
(3)-diagonal: Σ_j α (P∘X∘Y)_ij, O(n²) per block. Last layer: transports + (3)-read only (trim).
Old tier (age ≥ 5): legs confined to Q (n×r): P_b = Q F_P,b, A_b = Q F_A,b with STATIC F (transport is linear: Wᵀ Q F = (WᵀQ) F; Φ∘ acts
on rows → also linear), so only Q is transported (r/n units per layer, shared). Read: form dense P_b, A_b (2·r/n units), contract
LP_b F_Pᵀ + LA_b F_Aᵀ (2·r/n) into an n×r accumulator, ONE trailing (·)Qᵀ per layer (r/n). Per old source ≈ 1.5 units (r=384) /
0.875 (r=224). Entering the tier: Q_new = range finder on [Q_old (F Fᵀ)^{1/2} | P_new | A_new] (≈ 2 units/layer); old F re-expressed
by Q_newᵀ Q_old (r×r×n, cheap). The newcomer's coefficients F = Q_newᵀ P_new (committed truncation).
Hand ledger (units of 2n³; budget 1024): layers 1–14 young 3 (age 1: P = Wᵀ free) + 4·min(l−1,3) ; old 1.5 × (ages 5–7) + 0.875 × (age ≥ 8)
+ 0.75 shared; base ≈ 3.5 (Σ transport 3 symmetric + closure); last layer ≈ 15.5 → ≈ 323 units ≈ 31.5 % before Strassen, elementwise and
thin products ≈ +2–3 pts → **≈ 34 % pre-Strassen; ≈ 28 % at Strassen d=3 on the dense products** (v11 kernel). 504aldo V24: 36.7 %.
Range finders: `fnp.linalg.qr` on n×24 bills 0.001 units; a rank-16 range finder on an n×n matrix bills 0.048 units (measured).
Never `eigh`/`svd` on n×n in the port (9 / 20 units). Ω for the range finders = 24 columns of W_l (Gaussian, free, deterministic).
