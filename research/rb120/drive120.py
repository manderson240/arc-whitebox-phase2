"""G-RB96 driver: python drive.py <arms.json> <fit12|valid20|fitN:a-b> [out.jsonl]; env NW workers, OMP per worker via OMP.
arms.json = {name: spec}. One task = (arm, net). Resumable: skips (arm,net) already in out.jsonl. Task order is net-major interleaved
so partial runs still give complete nets for a prefix of arms."""
import json, os, sys, time
from concurrent.futures import ProcessPoolExecutor, as_completed
import multiprocessing as mp
from pathlib import Path
HERE = Path(__file__).resolve().parent
SPLIT = json.load(open(HERE.parent / "lc" / "split.json"))
FIT12 = SPLIT["FIT"][:12]
OMP = os.environ.get("OMP", "2")


def init():
    for k in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
        os.environ[k] = OMP
    sys.path.insert(0, str(HERE))


def job(a):
    import w120 as w96
    arm, net, spec = a
    f, s = w96.run(net, spec)
    return arm, net, f, s


def nets_of(tok):
    if tok == "fit12": return FIT12
    if tok == "fit60": return SPLIT["FIT"]
    if tok == "tf80": return SPLIT["FIT"] + SPLIT["VALID"]
    if tok == "valid20": return SPLIT["VALID"]
    if tok.startswith("nets:"): return [int(x) for x in tok[5:].split(",")]
    raise SystemExit(tok)


def main():
    arms = json.load(open(sys.argv[1])); nets = nets_of(sys.argv[2])
    out = Path(sys.argv[3]) if len(sys.argv) > 3 else HERE / "results.jsonl"
    done = set()
    if out.exists():
        for ln in open(out):
            r = json.loads(ln); done.add((r["arm"], r["net"]))
    tasks = [(a, n, sp) for n in nets for a, sp in arms.items() if (a, n) not in done]
    nw = int(os.environ.get("NW", "12"))
    print(f"{len(tasks)} tasks, {nw} workers x OMP {OMP}", flush=True)
    t0 = time.time(); k = 0
    with ProcessPoolExecutor(nw, mp_context=mp.get_context("spawn"), initializer=init) as ex:
        futs = [ex.submit(job, t) for t in tasks]
        for f in as_completed(futs):
            arm, net, fin, secs = f.result(); k += 1
            with open(out, "a") as fh:
                fh.write(json.dumps(dict(arm=arm, net=net, final=fin, secs=secs, spec=arms[arm], utc=time.strftime("%FT%TZ", time.gmtime()))) + "\n")
            if k % 12 == 0:
                print(f"{k}/{len(tasks)} {3600*k/(time.time()-t0):.0f} tasks/h", flush=True)
    print(f"done {k} tasks in {time.time()-t0:.0f}s = {3600*k/max(time.time()-t0,1):.0f} tasks/h", flush=True)


if __name__ == "__main__":
    main()
