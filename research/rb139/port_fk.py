"""G-RB139: port v103_fk's F0/K0 extra level (G-RB126) onto v105 + the inert v100r d6 machinery (v106_1x with _D6_T=False).
python3 port_fk.py <out_dir> <sites: F0,K0 | F0 | K0>"""
import re, shutil, sys
from pathlib import Path

ROOT = Path.home() / "cohezion-labs/arc-whitebox"
out, sites = Path(sys.argv[1]), sys.argv[2].split(",")
src = (ROOT / "submissions/v106_1x/estimator.py").read_text()
v103 = (ROOT / "submissions/v103_fk/estimator.py").read_text()


def rep(s, old, new, n=1):
    assert s.count(old) == n, (old[:80], s.count(old))
    return s.replace(old, new)


s = rep(src, "_D6_T = True  #", "_D6_T = False  #")
if len(sys.argv) > 3:  # optional fused-d6 sites, e.g. T2
    s = rep(s, "_D6_SITES = ()  #", "_D6_SITES = (" + "".join(f'"{x}", ' for x in sys.argv[3].split(",")) + ")  #")
s = rep(s, '        self.maxdims = {}  # role -> max (rows, cols) of its last two axes\n',
        '        self.maxdims = {}  # role -> max (rows, cols) of its last two axes\n'
        '        self.fv, self.full, self.caxis = {}, {}, {}  # v103: F0 / K0 max-shaped views\n')
i0 = v103.index("    def getc(self, role, c):")
getc = v103[i0: v103.index("\n\n\n", i0)] + "\n\n"
s = rep(s, "    def up_view(self, lvl, lead, h2, w2):\n        return self.out\n\n\n",
        "    def up_view(self, lvl, lead, h2, w2):\n        return self.out\n\n" + getc + "\n")
blk = v103[v103.index("_D6_FK = True"): v103.index("def _d6_bside(")]
tup = "(" + ", ".join(f'("{x[0]}", {x[1]})' for x in sites) + ",)"
blk = blk.replace("_D6_FK = True  #", f"_D6_FK = {tup}  # G-RB139: sites taking the extra level;", 1)
s = rep(s, "def _d6_bside(Rg, mini):", blk + "def _d6_bside(Rg, mini, S3=None, T4=None):")
s = rep(s, '    S3 = mini.get("B3", (3,) + Rg.shape[:-2] + (h, w2))\n    T4 = mini.get("T4", Rg.shape[:-2] + (h, w2))\n',
        '    if S3 is None:\n        S3 = mini.get("B3", (3,) + Rg.shape[:-2] + (h, w2))\n        T4 = mini.get("T4", Rg.shape[:-2] + (h, w2))\n')
old = '        if getattr(site, "d6c", False) and L.shape[-2] % 2 == 0 and L.shape[-1] % 2 == 0 and R.shape[-1] % 2 == 0:\n'
s = rep(s, old, '        if getattr(site, "d6fk", False) and L.shape[-2] % 2 == 0 and L.shape[-1] % 2 == 0 and R.shape[-1] % 2 == 0:\n'
        '            _d6_fk(L, R, P, site.mini)  # v103 (G-RB126): F0 / K0 extra level into the plain d4 leaf\n'
        '        el' + old.lstrip())
old = "            if _D6_T:\n                _attach_d6_chunked(S[\"T\"], ar, dt)\n"
s = rep(s, old, old + "            for _fk in _D6_FK:  # G-RB139 (port of G-RB126): the 224 group (depth 4) only\n                _attach_d6_fk(S[_fk], ar, dt)\n")
s = '"""G-RB139 variant: v105_sw + v103_fk\'s exact F0/K0 extra level on sites ' + ",".join(sites) + ' (inert v100r d6 machinery present, _D6_T False, _D6_SITES empty).\n' + s[3:]
out.mkdir(parents=True, exist_ok=True)
for f in ("lc_weights.npz", "weights.npz"):
    shutil.copy2(ROOT / "submissions/v105_sw" / f, out / f)
(out / "estimator.py").write_text(s)
print("wrote", out, tup)
