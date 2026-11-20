"""Capture WCH-LinkE -> CH32X315MCU6 (a short RVSWD try on attach, then SWIO on SWDIO) at 160 MS/s while ch32rv runs one operation, one run directory per scenario.

    uv run --project <wireskein> python tools/capture.py <out dir> [name-glob ...]

Each run (wireskein-run/1, wireskein.runlog.Recorder): run.json (the heading "# <scenario>", the ch32rv command and
its exit code / output), c0001.wireskein (SWCLK, SWDIO as tapped at the LinkE's pins: OEP ESP32-P4X e8f60ae84dd7,
GPIO16 = SWIO (the LinkE's SWDIO; its SWCLK, moving only while it tries RVSWD on attach, not taken), stream mode, no glitch filter), and the truth beside it, taken outside WireSkein:
ch32rv.ndjson (ch32rv --capture: every USB round trip with the LinkE), ch32rv.json (its --json stdout),
ch32rv.stderr, and read.bin for a read. The capture is checked to hold the whole command (host clock of the
first sample from meta.probe.clock, against time.monotonic_ns() around ch32rv); a capture that lost data or
missed the command is taken again with a longer stream. Scenarios already in <out dir> are skipped."""
from __future__ import annotations

import fnmatch
import hashlib
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

from wireskein import _fileformat as fileformat
from wireskein.runlog import Recorder

CH32RV = os.environ.get("CH32RV", "ch32rv")     # the ch32rv to run (a build of ch32-riscv-ug/ch32rv)
LINKE = "FBC18F0680B0"
PROBE = "oep:oep://e8f60ae84dd7"
CHANNELS = "SWIO=GPIO16"     # SWIO alone: 20 MB/s at 160 MS/s (the LinkE's RVSWD try on attach, on GPIO21 too, is left out)
RATE = "160M"
TOOLS = Path(__file__).resolve().parent
TRIES = int(os.environ.get("TRIES", "4"))   # attempts per scenario (a busy host may lose a 40 MB/s stream now and then)
LEAD_S = 3.0          # the stream starts 0.8-2.1 s after the capture process (more when the link opens slowly)
TAIL_S = 0.6
WRONG_CHIP = "CH32V003F4P6"
TARGET = "CH32X315MCU6"
TARGET_UID = "36a0abcd9eb5bc48"


def scenarios() -> list[tuple[str, list[str]]]:
    """(name, ch32rv args); "{read}" becomes this run's read.bin."""
    # img: ch32rv tests/fixtures/debug-smoke dmdata.bin (X315 and V205; DMDATA "OK\n", results at 0x20001000)
    pat, img, ram = (str(TOOLS / f) for f in ("pattern-4k.bin", "x315_smoke.bin", "ram-256.bin"))
    out: list[tuple[str, list[str]]] = []
    base = [
        ("target_info", ["target", "info"]),
        ("read_ram_256", ["read", "--range", "0x20000000+256", "-o", "{read}"]),
        ("read_flash_4k", ["read", "--range", "0x08000000+4096", "-o", "{read}"]),
        ("flash_pattern4k", ["flash", pat, "--yes"]),
        ("verify_pattern4k", ["verify", pat]),
        ("read_pattern4k", ["read", "--range", "0x08000000+4096", "-o", "{read}"]),
        ("dbg_halt", ["dbg", "halt"]),
        ("dbg_regs", ["dbg", "regs"]),
        ("dbg_step", ["dbg", "step"]),
        ("dbg_resume", ["dbg", "resume"]),
        ("reset", ["reset"]),
        ("erase_all", ["erase", "--all", "--yes"]),
        ("read_erased_1k", ["read", "--range", "0x08000000+1024", "-o", "{read}"]),
        ("flash_sketch", ["flash", img, "--yes"]),
    ]
    for speed in ("high", "medium", "low"):
        out += [(f"{speed}/{n}", ["--speed", speed, *a]) for n, a in base]
    hi = "high/x_"
    out += [(f"{hi}target_info_{k}", ["target", "info"]) for k in range(2, 6)]
    out += [(f"{hi}read_flash_4k_{k}", ["read", "--range", "0x08000000+4096", "-o", "{read}"]) for k in range(2, 4)]
    out += [
        (f"{hi}read_flash_16k", ["read", "--range", "0x08000000+16384", "-o", "{read}"]),
        (f"{hi}read_flash_64k", ["read", "--range", "0x08000000+65536", "-o", "{read}"]),
        (f"{hi}read_ram_2k", ["read", "--range", "0x20000000+2048", "-o", "{read}"]),
        (f"{hi}read_esig", ["read", "--range", "0x1ffff7e0+20", "-o", "{read}"]),
        (f"{hi}read_optbytes", ["read", "--range", "0x1ffff800+16", "-o", "{read}"]),
        (f"{hi}read_unaligned_odd", ["read", "--range", "0x08000003+13", "-o", "{read}"]),
        (f"{hi}dbg_halt_w", ["dbg", "halt"]),
        (f"{hi}write_ram_256", ["write", "--at", "0x20000400", ram]),
        (f"{hi}read_ram_written", ["read", "--range", "0x20000400+256", "-o", "{read}"]),
        (f"{hi}write_ram_word", ["write", "--at", "0x20000500", "word:0xa5c3e10f"]),
        (f"{hi}read_ram_word", ["read", "--range", "0x20000500+4", "-o", "{read}"]),
        (f"{hi}dbg_reg_pc", ["dbg", "reg", "read", "pc"]),
        (f"{hi}dbg_reg_sp", ["dbg", "reg", "read", "x2"]),
        (f"{hi}dbg_reg_misa", ["dbg", "reg", "read", "csr:0x301"]),
        (f"{hi}dbg_reg_write_t0", ["dbg", "reg", "write", "x5", "0x12345678"]),
        (f"{hi}dbg_reg_t0", ["dbg", "reg", "read", "x5"]),
        (f"{hi}dbg_step_1", ["dbg", "step"]),
        (f"{hi}dbg_step_2", ["dbg", "step"]),
        (f"{hi}dbg_step_3", ["dbg", "step"]),
        (f"{hi}dbg_regs_after_step", ["dbg", "regs"]),
        (f"{hi}dbg_resume_w", ["dbg", "resume"]),
        (f"{hi}dmi_write_dmcontrol_01", ["dbg", "dmi", "write", "0x10", "0x00000001"]),
        (f"{hi}dmi_read_dmcontrol", ["dbg", "dmi", "read", "0x10"]),
        (f"{hi}dmi_read_dmstatus", ["dbg", "dmi", "read", "0x11"]),
        (f"{hi}dmi_read_hartinfo", ["dbg", "dmi", "read", "0x12"]),
        (f"{hi}dmi_read_abstractcs", ["dbg", "dmi", "read", "0x16"]),
        (f"{hi}dmi_read_data0", ["dbg", "dmi", "read", "0x04"]),
        (f"{hi}dmi_write_data0", ["dbg", "dmi", "write", "0x04", "0xdeadbeef"]),
        (f"{hi}dmi_read_data0_after", ["dbg", "dmi", "read", "0x04"]),
        (f"{hi}reset_halt", ["reset", "--halt"]),
        (f"{hi}reset_dm", ["reset", "--dm"]),
        (f"{hi}reset_confirm_pc", ["reset", "--confirm-run", "pc"]),
        (f"{hi}release_dm_info", ["--release-dm", "target", "info"]),
        (f"{hi}connect_under_reset", ["--connect-under-reset", "target", "info"]),
        (f"{hi}err_read_unmapped", ["read", "--range", "0x60000000+16", "-o", "{read}"]),
        (f"{hi}err_wrong_chip", ["--chip", WRONG_CHIP, "target", "info"]),
        (f"{hi}err_verify_mismatch", ["verify", pat]),
        (f"{hi}option_get", ["target", "option", "get"]),
        (f"{hi}option_set_data", ["target", "option", "set", "data0=0x5a", "data1=0xc3", "--yes"]),
        (f"{hi}option_get_after_set", ["target", "option", "get"]),
        (f"{hi}read_obr_after_set", ["read", "--range", "0x4002201c+4", "-o", "{read}"]),
        (f"{hi}option_reset", ["target", "option", "reset", "--yes"]),
        (f"{hi}option_get_after_reset", ["target", "option", "get"]),
        (f"{hi}flash_sketch_end", ["flash", img, "--yes"]),
    ]
    return out


# the capture rates swept (MHz): whole dividers of 160 MHz (evenly spaced samples) and fractional ones (samples on
# the 6.25 ns grid, unevenly spaced: oep-probe-arduino docs/guide/capture), down to the probe's lowest
WHOLE = ["160", "10", "5"]
FRACTIONAL = ["133.333333", "50"]


def rate_scenarios() -> list[tuple[str, list[str], str]]:
    """The same operations at every rate swept: rate/<MHz>/<op>."""
    pat = str(TOOLS / "pattern-4k.bin")
    ops = [("target_info", ["--speed", "high", "target", "info"]),
           ("read_flash_4k", ["--speed", "high", "read", "--range", "0x08000000+4096", "-o", "{read}"]),
           ("flash_pattern4k", ["--speed", "high", "flash", pat, "--yes"]),
           ("low_read_ram_256", ["--speed", "low", "read", "--range", "0x20000000+256", "-o", "{read}"])]
    out = []
    for r in WHOLE + FRACTIONAL:
        tag = f"{float(r):g}".replace(".", "p")
        out += [(f"rate/{tag}M/{n}", a, f"{float(r) * 1e6:.0f}") for n, a in ops]
    return out


def holdout(name: str) -> bool:
    """Half the scenarios set aside for checking, by the hash of the name (data-requests §0); a rate sweep's by its
    operation's name, so that one operation is on one side at every rate."""
    if name.startswith("rate/"):
        name = "rate/" + name.split("/", 2)[2]
    return hashlib.sha256(name.encode()).digest()[0] & 1 == 1


def first_sample_host_ns(path: Path) -> tuple[int, float] | None:
    """(host ns of the first sample, seconds taken) from the capture's clock record."""
    head = fileformat.read_header(path)
    num, den = head["tick_hz"]
    before = ((head.get("meta") or {}).get("probe") or {}).get("clock", {}).get("before")
    part = (head.get("parts") or [{}])[0]
    start = (part.get("meta") or {}).get("start_ns")
    if not before or start is None or len(head.get("parts") or []) != 1:
        return None
    return before["host_ns"] + (start - before["uptime_ns"]), part["ticks"] * den / num


TWO_LINES = "SWIO=GPIO16,SWCLK=GPIO21"
# the LinkE's RVSWD try on attach, both lines, kept short: a one-shot into the probe's memory from SWCLK's first fall,
# 0.15 s at 160 MS/s (the RVSWD try takes some 100 ms; a triggered one-shot of two lines at 160 MS/s that waits for
# its trigger longer than the probe's ring needs its firmware from b9b46df on: before, the trigger search fell behind
# and the segment lost data); no stream, so a busy host cannot lose it
ATTACH_RATE = "160M"
ONESHOT = ["--mode", "oneshot", "--samples", "24M", "--trigger", "SWCLK:fall", "--pretrigger", "100000", "--timeout", "30"]


def take(root: Path, name: str, args: list[str], log, rate: str = RATE, two: bool = False) -> dict:
    run = root / name
    tmp = root / (name.replace("/", "__") + ".tmp")
    duration = 5.0
    for attempt in range(TRIES):
        shutil.rmtree(run, ignore_errors=True); shutil.rmtree(tmp, ignore_errors=True)
        tmp.mkdir(parents=True)
        cap_path = tmp / "c.wireskein"
        read_bin = tmp / "read.bin"
        a = [x.replace("{read}", str(read_bin)) for x in args]
        cmd = [CH32RV, "--probe", f"serial:{LINKE}", "--json", "--non-interactive", "--progress", "none",
               "--capture", str(tmp / "ch32rv.ndjson"), *a]
        rec = Recorder(tmp / "run", target=TARGET, target_uid=TARGET_UID, linke=LINKE,
                       tap="LinkE side", probe=PROBE, scenario=name, holdout=holdout(name))
        rec.heading(1, name)
        armed = rec.armed()
        how = (["--channels", TWO_LINES, "--rate", ATTACH_RATE, *ONESHOT] if two else
               ["--channels", CHANNELS, "--mode", "stream", "--rate", rate, "--duration", f"{duration:g}s"])
        cap = subprocess.Popen(["wireskein", "capture", "--source", PROBE, *how, "-o", str(cap_path)],
                               stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        time.sleep(LEAD_S)
        shown = " ".join(["ch32rv", *cmd[1:]]).replace(str(tmp) + "/", "").replace(str(TOOLS) + "/", "tools/")
        rec.command(shown)
        t0 = time.monotonic_ns()
        p = subprocess.run(cmd, capture_output=True, text=True, stdin=subprocess.DEVNULL, timeout=300)
        t1 = time.monotonic_ns()
        rec.reply(f"exit {p.returncode} in {(t1 - t0) / 1e9:.3f} s")
        rec.heading(1)
        cap_out, _ = cap.communicate(timeout=duration + 120)
        took = (t1 - t0) / 1e9
        ok, why = cap.returncode == 0 and cap_path.exists(), ""
        if not ok:
            why = f"capture rc {cap.returncode}: {cap_out.strip()[-300:]}"
        else:
            fs = first_sample_host_ns(cap_path)
            if fs is None:
                ok, why = False, "no clock record"
            else:
                start, span_s = fs
                end = start + span_s * 1e9
                if two:
                    if not (t0 - 0.1e9 <= start + 1e9 * 100_000 / 160e6 <= t1 + 0.1e9):   # the trigger inside the command
                        ok, why = False, f"one-shot triggered {(start - t0) / 1e9:+.3f} s from the command"
                elif t0 - 0.1e9 < start or t1 + 0.2e9 > end:
                    ok, why = False, f"window {(start - t0) / 1e9:+.3f}..{(end - t1) / 1e9:+.3f} s around the command ({took:.2f} s)"
        if not ok:
            print(f"  retry {name} ({why})", flush=True)
            log.write(json.dumps({"scenario": name, "attempt": attempt + 1, "why": why, "host_ns": t0}) + "\n"); log.flush()
            duration = max(duration, took + LEAD_S + TAIL_S + 1.0) * 1.5
            # the probe's HS link dropped and came back: ModemManager probes a new CDC port for 15-20 s ([oep]),
            # a capture then opens slowly and loses data
            time.sleep(25.0 if "NoDevice" in why or "NO_DEVICE" in why else 10.0 if "capture rc" in why else 2.0)
            continue
        rec.add(armed, cap_path)
        rec.close()
        run.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(tmp / "run", run)
        for f in ("ch32rv.ndjson", "read.bin"):
            if (tmp / f).exists():
                shutil.move(tmp / f, run / f)
        (run / "ch32rv.json").write_text(p.stdout)
        (run / "ch32rv.stderr").write_text(p.stderr)
        shown_args = [x.replace(str(tmp) + "/", "").replace(str(TOOLS) + "/", "tools/") for x in a]
        info = {"scenario": name, "args": shown_args, "rc": p.returncode, "seconds": round(took, 4),
                "t0_host_ns": t0, "t1_host_ns": t1, "stream_s": duration, "attempts": attempt + 1,
                "holdout": holdout(name), "rate_requested": ATTACH_RATE if two else rate, "lines": TWO_LINES if two else CHANNELS, "capture_log": cap_out.strip().splitlines()}
        (run / "take.json").write_text(json.dumps(info, indent=1))
        shutil.rmtree(tmp, ignore_errors=True)
        return info
    shutil.rmtree(tmp, ignore_errors=True)
    return None


def main() -> None:
    root = Path(sys.argv[1])
    pats = sys.argv[2:] or ["*"]
    root.mkdir(parents=True, exist_ok=True)
    log = open(root / "retries.jsonl", "a")
    todo = [(n, a, RATE, False) for n, a in scenarios()] + [(n, a, r, False) for n, a, r in rate_scenarios()]
    todo += [(f"attach2/{sp}/target_info", ["--speed", sp, "target", "info"], RATE, True)
             for sp in ("high", "medium", "low")]
    for name, args, rate, two in todo:
        if not any(fnmatch.fnmatch(name, p) for p in pats):
            continue
        if (root / name / "take.json").exists():
            continue
        info = take(root, name, args, log, rate, two)
        if info is None:
            print(f"{name}: FAILED (no good capture in {TRIES} tries; retries.jsonl)", flush=True)
            continue
        size = sum(f.stat().st_size for f in (root / name).iterdir())
        print(f"{name}: rc {info['rc']} {info['seconds']:.2f} s, {size / 1e6:.2f} MB, try {info['attempts']}"
              f"{' holdout' if info['holdout'] else ''}", flush=True)


if __name__ == "__main__":
    main()
