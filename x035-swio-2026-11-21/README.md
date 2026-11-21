# x035-swio-2026-11-21

[日本語](README.ja.md)

The Japanese text (`README.ja.md`) is the working text until v1.0.0.

SWIO (the CH32V00x's one-wire debug) as OEP probes drive it, taken by the OEP ESP32-P4 30eda0e31451 at 80 MS/s: for
fitting the SWIO timing of a CH32X035 as an OEP probe.

| run | Driven by | On a CH32V003 |
|---|---|---|
| `p4_ref` | The ESP32-P4's own SWIO (GPIO15, taken on the same channel) | Attaches (the same firmware attaches the resident benches' V003) |
| `x035_late-5-9-10` | A CH32X035F8U6's SWIO (PA0): each step's lateness taken off per step, 5 / 9 / 10 counts | Does not attach |
| `x035_readbit-timeline` | As above, the read bits stepped on deadlines alone, a one not waiting for the rise | Does not attach |
| `x035_half-late-2` | As above, the read's half step less 2 counts | Does not attach |

- No target is on the line taken (the X035's PA0 and the P4's GPIO15 only): the waveform is the probe's own, the read
  bits come back high from the pull-up.
- "On a CH32V003" is the same build on another CH32X035F8U6 (a WeAct board, a V003's SWIO at its PA0, the V003 powered
  from the board's 3V3), attaching; that line is not taken.
- The X035 taken is a WeAct CH32X035F8U6 board (OEP probe 283fbc5cc016abcd, UID c016abcd283fbc5c): PA0-PA7, PB0, PB1,
  PB3, PB11, PB12, PC14 and PC15 reach the P4 (PA0 is GPIO15).

WireSkein's reading (`tools/summary.py`, the medians over each run's frames):

| run | Frames | Short low | Long low | Write high | Read bit pitch | Read high |
|---|---|---|---|---|---|---|
| `p4_ref` | 16, all ok | 312.5 ns | 912.5 ns | 312.5 ns | 850.0 ns | 425.0 ns |
| `x035_late-5-9-10` | 24, all ok | 287.5 ns | 850.0 ns | 350.0 ns | 1387.5 ns | 1012.5 ns |
| `x035_readbit-timeline` | 24, all ok | 287.5 ns | 812.5 ns | 400.0 ns | 950.0 ns | 687.5 ns |
| `x035_half-late-2` | 24, all ok | 287.5 ns | 812.5 ns | 400.0 ns | 950.0 ns | 687.5 ns |

For comparison, a WCH-LinkE's SWIO to a CH32V003 (`../v003-linke-2026-11-17/runs/high/target_info`): short low 250 ns,
long low 875 ns, write high 369 ns, read bit pitch 766 ns, read high 391 ns.

## Tools

- `tools/capture.py`: one run (`p4_ref`, or `x035 <build name>`): one shot of 400k samples (5 ms) cut at SWIO's first
  fall, the attach run while armed.
- `tools/summary.py`: each run read by WireSkein, the medians over its frames.
- `tools/runs.py`: one run's SWIO as L / H lengths, frame by frame.

```sh
uv run --project <wireskein> --with-editable <oep-client-python> python tools/capture.py runs x035 <build name> [note]
uv run --project <wireskein> python tools/summary.py runs/*
```
