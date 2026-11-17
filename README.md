# wireskein-captures

Real captures for measuring [WireSkein](https://github.com/Open-Embedded-Probe/wireskein)'s analysis, each with a truth
taken outside WireSkein (the debugger's or the firmware's own record, what was read or written).

These are the raw streams. WireSkein's algorithm bench (`bench/` of wireskein) reads its own copies under
`bench/data/`: each capture cut to the operation it holds, with the truth beside it; the copy's `SOURCE.json` names
this repository's commit and each file it came from. The tools that took and cut them are in that copy's `tools/`.

| Directory | What |
|---|---|
| `l103-linke-2026-11-17/` | A WCH-LinkE's RVSWD to a CH32L103C8T6, taken by an OEP ESP32-P4X at the LinkE's pins at 160 MS/s: 103 ch32rv operations (the LinkE's speeds high / medium / low, and more), and 4 operations at 26 capture rates (160 MHz to 627 kHz, whole and fractional dividers). Truth: ch32rv's USB record (its DMI operations) and what it read |

Each run is wireskein-run/1 (`run.json`, `c0001.wireskein`) with `take.json` (how it was taken), `truth.json`
(the truth), `reading.json` (WireSkein's reading at the time: not truth), and the debugger's own files.

MIT License (see `LICENSE`).
