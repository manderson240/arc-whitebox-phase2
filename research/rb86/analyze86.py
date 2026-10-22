"""G-RB86 energy shares from decomp.jsonl (debiased: ee = mean((c-A)(c-B)); <ea,e> uses noise-independent ea). Output -> shares.json + stdout"""
import json, numpy as np
R = [json.loads(l) for l in open('decomp.jsonl')]
arms = {}
for l in open('arms.jsonl'):
    r = json.loads(l); arms[(r['net'], r['mode'])] = r['final']
def stats(rs, sfx):
    ee = sum(r['ee'] for r in rs); ae = sum(r['ea'+sfx+'_e'] if sfx else r['ea_e'] for r in rs)
    aa = sum(r['ea'+sfx+'_ea'+sfx] if sfx else r['ea_ea'] for r in rs)
    eb = ee - 2*ae + aa
    return dict(ee=ee, proj_a=ae/ee, proj_b=1-ae/ee, Ea_over_ee=aa/ee, Eb_over_ee=eb/ee, share_a=aa/(aa+eb), share_b=eb/(aa+eb))
out = {}
for sfx, name in (('', 'carried (post-head) mean'), ('r', 'raw closure (pre-head) mean')):
    print('==', name)
    print('layer | proj a/b (<ea,e>/ee) | E_a/ee  E_b/ee | share_a (E_a/(E_a+E_b))')
    for l in range(8, 16):
        s = stats([r for r in R if r['l'] == l], sfx)
        out[f'{name}|{l}'] = s
        print(f"{l:2d} | {s['proj_a']:+.3f} / {s['proj_b']:.3f} | {s['Ea_over_ee']:.2f} {s['Eb_over_ee']:.2f} | {s['share_a']:.3f}")
    s = stats([r for r in R if r['l'] >= 8], sfx); out[f'{name}|pooled'] = s
    print(f"pooled 8-15 (3 nets): proj a/b {s['proj_a']:+.3f}/{s['proj_b']:.3f}  E_a/ee {s['Ea_over_ee']:.2f} E_b/ee {s['Eb_over_ee']:.2f}  share_a {s['share_a']:.3f}")
    for n in (0, 2, 4):
        s = stats([r for r in R if r['l'] >= 8 and r['net'] == n], sfx)
        print(f"  net {n}: proj_a {s['proj_a']:+.3f} share_a {s['share_a']:.3f}")
ctrl = {n: arms[(n, 'decomp')] for n in (0, 2, 4)}
for mode in ('varmu', 'varmuraw'):
    rat = {n: arms[(n, mode)] / ctrl[n] for n in (0, 2, 4)}
    pooled = sum(arms[(n, mode)] for n in ctrl) / sum(ctrl.values())
    out[f'arm2|{mode}'] = dict(per_net=rat, pooled=pooled)
    print(mode, {n: round(v, 3) for n, v in rat.items()}, 'pooled', round(pooled, 3))
json.dump(out, open('shares.json', 'w'), indent=1)
