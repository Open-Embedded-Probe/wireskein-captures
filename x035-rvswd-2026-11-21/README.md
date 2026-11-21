# x035-rvswd-2026-11-21

[日本語](README.ja.md)

The Japanese text (`README.ja.md`) is the working text until v1.0.0.

RVSWD (two lines) attaches as OEP probes drive them, taken by the OEP ESP32-P4 30eda0e31451 at 80 MS/s, with no target
on the lines: a first look at the timing of a CH32X035 as an RVSWD probe.

| run | Driven by |
|---|---|
| `p4_ref` | The ESP32-P4's own RVSWD (GPIO15 SWDIO, GPIO14 SWCLK, taken on the same channels) |
| `x035_a7adace` | A CH32X035F8U6's RVSWD (WeAct board, OEP probe 283fbc5cc016abcd, the distributed build 0.0.60+a7adace; PA0 SWDIO, PA1 SWCLK, at the P4's GPIO15 / GPIO14) |

- With no target, both show only the attach's search (the slow speed that waits for an answer). RVSWD speeds up once
  the target answers, so the usual speed shows only on a line with a target.
- SWCLK (raw lengths read by `tools/runs.py`): `p4_ref` low 560-720 ns, high 620-840 ns (a period of some 1.2-1.5 us);
  `x035_a7adace` low 1.3-1.5 us, high 2.0-2.2 us (some 3.3 us).
- WireSkein reads neither as RVSWD (no target answers).

## Tools

- `tools/capture.py`: one run (`p4_ref`, or `x035 <build name>`): one shot of 400k samples (5 ms) cut at SWDIO's first
  fall, the attach run while armed.
- `tools/runs.py`: one line of one run as L / H lengths (`tools/runs.py runs/<run> 0 40 SWCLK`).
- `tools/summary.py`: for SWIO (as in `../x035-swio-2026-11-21`); not for these RVSWD runs.
