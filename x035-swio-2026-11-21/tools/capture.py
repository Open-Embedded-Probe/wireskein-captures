"""Capture an OEP probe's SWIO frames (its attach to a CH32V00x) on the line, by the ESP32-P4 30eda0e31451 at 80 MS/s.

    uv run --project <wireskein> --with-editable <oep-client-python> python tools/capture.py <out dir> p4_ref [note]
    uv run ... python tools/capture.py <out dir> x035 <label> [note]

p4_ref  the ESP32-P4's own SWIO on its GPIO15, taken on the same channel (the capture only listens): the frames that
        attach a CH32V003 on the benches (its timing is the reference).
x035    a CH32X035F8U6 (WeAct board, OEP probe 283fbc5cc016abcd, UID c016abcd283fbc5c) running the OEP firmware with
        SWIO, its PA0 wired to the P4's GPIO15: its frames as it attaches. <label> names the firmware build.
No target is on this line (the X035's PA0 and the P4's GPIO15 only): the waveform is the probe's own, the reads come
back high from the pull-up. Whether the same frames attach a CH32V003 is recorded beside it (the note and README).

One shot of 400k samples (5 ms) armed on SWIO's first fall (2000 samples before it), the attach run while armed, on
the session that holds the capture (one session: a stream read beside an attach on another thread lost the session).
Each run (wireskein-run/1, wireskein.runlog.Recorder): run.json (the heading "# <name>", notes: the probes' firmware,
the attach's outcome) and c0001.wireskein (SWIO)."""
from __future__ import annotations

import sys
import time
from pathlib import Path

from oep_client import acquire, capture, core, link, pins
from wireskein import capture as wc
from wireskein.runlog import Recorder

P4 = "oep://30eda0e31451"
X035 = "oep://283fbc5cc016abcd"
P4_LINE, P4_CH, X035_CH = "GPIO15", 15, 0     # the P4's channel on the line; the X035's (PA0)
RATE, SAMPLES, PRE = 80_000_000, 400_000, 2000


def firmware(hst) -> str:
    """What the probe's describe says it runs (oep_client.acquire's own reading of fn 0's describe)."""
    info = acquire._probe_info(core, hst, None)
    return f"{info.get('model', '?')} {info.get('unit_id', '?')} firmware {info.get('firmware', '?')}"


def attach(hst, ch: int) -> str:
    f = pins.PinFinder(hst, wire="swio", say=lambda *a: None)
    try:
        f.wire.attach(halt=False, pins=(ch, 0xFFFF))
        return "attached"
    except Exception as e:     # no target here: the attach fails, its frames are what is taken
        return f"{type(e).__name__}: {e}"


def main() -> int:
    out, kind = Path(sys.argv[1]), sys.argv[2]
    rest = sys.argv[3:]
    label = rest.pop(0) if kind == "x035" else ""
    note = rest[0] if rest else ""
    name = "p4_ref" if kind == "p4_ref" else f"x035_{label}"
    p4 = link.open_host(P4)
    core.take(p4, 30000, owner="wireskein-captures x035-swio")
    src = p4 if kind == "p4_ref" else link.open_host(X035)
    if src is not p4:
        core.take(src, 30000, owner="wireskein-captures x035-swio")
    rec = Recorder(out / name, probe=P4, line=P4_LINE)
    rec.note(f"capture: {firmware(p4)}, {P4_LINE} at {RATE} S/s, {SAMPLES} samples from {PRE} before SWIO's first fall")
    rec.note(f"SWIO from {firmware(src)}, channel {P4_CH if src is p4 else X035_CH}")
    if note:
        rec.note(note)
    lc = capture.LogicCapture(p4)
    core.plan_apply(p4, [(lc.fn, 0, P4_CH)])
    try:
        cfg = lc.configure(rate=RATE, samples=SAMPLES, trigger=(capture.EDGE, 0, 1), pretrigger=PRE)
        with rec.section(1, name):
            lc.start()
            armed = rec.armed()
            time.sleep(0.05)
            outcome = attach(src, P4_CH if src is p4 else X035_CH)
            (seg,) = lc.wait(timeout=10.0)
        bits = lc.channel(lc.read_segment(seg), 0, seg.samples)
    finally:
        core.plan_release(p4, [lc.fn])
    edges = [k for k in range(1, len(bits)) if bits[k] != bits[k - 1]]
    meta = {"start_ns": seg.start_ns, "start_uncertainty_ns": seg.start_uncertainty_ns}
    part = wc.Part(len(bits), [wc.logic("SWIO", int(bits[0]), edges, len(bits))], meta, 0)
    rec.note(f"attach: {outcome}")
    rec.add(armed, wc.Capture(cfg.rate, [part]))
    print(rec.close(), outcome)
    return 0


if __name__ == "__main__":
    sys.exit(main())
