"""Each run's SWIO frames as WireSkein reads them: per run, the medians over its frames (short / long low, high,
the read bits' pitch), and how many frames read ok.    uv run --project <wireskein> python tools/summary.py runs/*"""
import json, statistics, subprocess, sys
for run in sys.argv[1:]:
    r = subprocess.run(["wireskein", "analyze", f"{run}/c0001.wireskein"], capture_output=True, text=True)
    doc = json.loads(r.stdout[r.stdout.index("{"):])
    claims = doc["parts"][0]["claims"]
    if not claims:
        print(f"{run}: nothing read as SWIO"); continue
    rows = claims[0]["result"]["dmi"]
    w = [x for x in rows if x["op"] == "W"]; rd = [x for x in rows if x["op"] == "R"]
    med = lambda rs, k: round(statistics.median(x[k] for x in rs), 1) if rs else None
    print(f"{run}: {len(rows)} frames, {sum(x['ok'] for x in rows)} ok; writes short {med(w,'short_median_ns')} "
          f"long {med(w,'long_median_ns')} high {med(w,'space_ns')}; reads pitch(1) {med(rd,'pitch_1_ns')} "
          f"high {med(rd,'space_ns')}")
