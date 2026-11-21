"""A run's SWIO as its runs (L/H and ns), frame by frame (a high over 5 us ends a frame): frame k, its first N runs.
    uv run --project <wireskein> python tools/runs.py <run dir> <frame> [N]"""
import sys
import numpy as np
from wireskein import capture as wc
cap = wc.read(f"{sys.argv[1]}/c0001.wireskein")
ch = cap.parts[0].channel("SWIO")
ns = 1e9 / float(cap.tick_hz)
def changes(ch):
    """(start level, change ticks) of an events channel (wireskein-format 4.4: varint delta k, then the level byte)."""
    out, k, i, d = [], -1, 0, ch.data
    while i < len(d):
        v = sh = 0
        while True:
            b = d[i]; i += 1; v |= (b & 0x7F) << sh; sh += 7
            if not b & 0x80: break
        k += v; i += 1
        out.append(ch.phase + k * ch.step)
    return ch.start_level, out
initial, edges = changes(ch)
lv, last, runs = initial, 0, []
for e in edges:
    runs.append(("L" if lv == 0 else "H", (e - last) * ns)); lv ^= 1; last = e
frames, cur = [], []
for r in runs:
    if r[0] == "H" and r[1] > 5000:
        if cur: frames.append(cur)
        cur = []
    else: cur.append(r)
frames.append(cur)
k, n = int(sys.argv[2]), int(sys.argv[3]) if len(sys.argv) > 3 else 60
print(" ".join(f"{a}{b:.0f}" for a, b in frames[k][:n]))
