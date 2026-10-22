"""G-RB153 arm builder. mkarms.py vse1 -> arms_vse1.json (CTL + 6 grid scalars at layers 11-15)."""
import json, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
A2 = json.load(open(HERE.parent / "rb142" / "arms_142.json"))["A2"]


def scalar_model(tag, cl):
    f = HERE / "models" / f"m_{tag}.json"; f.parent.mkdir(exist_ok=True)
    json.dump(dict(form="scalar", layers={str(l): c for l, c in cl.items()}), open(f, "w"))
    return f"rb153/models/m_{tag}.json"


def arm(model=None, **kw):
    a = dict(A2)
    if model:
        a["vcal"] = dict(file=model, **kw)
    return a


if __name__ == "__main__":
    what = sys.argv[1]
    arms = {"CTL": arm()}
    if what == "vse1":
        for c in (-4e-3, -2e-3, -1e-3, 1e-3, 2e-3, 4e-3):
            arms[f"VSE1_{c:+.0e}"] = arm(scalar_model(f"vse1_{c:+.0e}", {l: c for l in range(11, 16)}))
    json.dump(arms, open(HERE / f"arms_{what}.json", "w"), indent=1)
    print(list(arms))
