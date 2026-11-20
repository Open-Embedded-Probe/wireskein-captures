# wireskein-captures

Real captures for measuring [WireSkein](https://github.com/Open-Embedded-Probe/wireskein)'s analysis, each with a truth
taken outside WireSkein (the debugger's or the firmware's own record, what was read or written).

These are the raw streams. WireSkein's algorithm bench (`bench/` of wireskein) reads its own copies under
`bench/data/`: each capture cut to the operation it holds, with the truth beside it; the copy's `SOURCE.json` names
this repository's commit and each file it came from.

Captures are taken here: each directory's `tools/` takes them (`capture.py`), checks the truth (`truth.py`) and cuts them for the bench (`publish.py`). Only what is taken and settled is copied into wireskein's `bench/data/` by `publish.py` (nothing is taken in wireskein's working tree).

| Directory | What |
|---|---|
| `l103-linke-2026-11-17/` | A WCH-LinkE's RVSWD to a CH32L103C8T6, taken by an OEP ESP32-P4X at the LinkE's pins at 160 MS/s: 103 ch32rv operations (the LinkE's speeds high / medium / low, and more), and 4 operations at 26 capture rates (160 MHz to 627 kHz, whole and fractional dividers). Truth: ch32rv's USB record (its DMI operations) and what it read |
| `v003-linke-2026-11-17/` | A WCH-LinkE's SWIO to a CH32V003F4P6, taken by the same P4X on the one SWIO line at 160 MS/s (the LinkE's two-line RVSWD try on attach in 3 runs of their own). The operations of the L103 set, and 5 capture rates. Truth: ch32rv's USB record and what it read |
| `v203-linke-2026-11-17/` | A WCH-LinkE's RVSWD to a CH32V203C8T6, taken by the same P4X on both lines at 160 MS/s (the fast transfers' SWCLK high some 19 ns). The 14 operations at the LinkE's speeds high and low and 9 more (not all: the wiring was loose). Truth: ch32rv's USB record and what it read |
| `x315-linke-tap-2026-11-20/` | A WCH-LinkE's target info to a CH32X315MCU6, taken by the same P4X on both lines (SWCLK, SWDIO) at 80 / 160 MS/s: 3 runs, 2 with the GPIO16 tap floating (not reaching the LinkE's SWDIO), 1 after it was fixed (the one-line SWIO shaped as the V003's). A pair for telling a floating input. Truth: ch32rv's USB record |

Each run is wireskein-run/1 (`run.json`, `c0001.wireskein`) with `take.json` (how it was taken), `truth.json`
(the truth), `reading.json` (WireSkein's reading at the time: not truth), and the debugger's own files.

MIT License (see `LICENSE`).
