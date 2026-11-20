"""Capture SWIO / SWCLK while sending raw WCH-Link commands in one USB session.

    RAWCMD=<wch-protocols>/experiments/e165_linke_x035_v103_wire/rawcmd.py \
    uv run --project <wireskein> python tools/run_raw.py <out.wireskein> <rate> <duration> <lead s> <hex|sleep:s> ...

Runs `wireskein` from PATH; RAWCMD names wch-protocols' rawcmd.py."""
import subprocess, sys, time, os
out, rate, dur, lead = sys.argv[1], sys.argv[2], sys.argv[3], float(sys.argv[4])
cmds = sys.argv[5:]
cap = subprocess.Popen(["wireskein","capture","--source","oep:oep://e8f60ae84dd7",
    "--channels","SWIO=GPIO16,SWCLK=GPIO21","--mode","stream","--rate",rate,"--duration",dur,"-o",out],
    stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
time.sleep(lead)
t0=time.monotonic_ns()
p = subprocess.run([os.environ["RAWCMD"],"--probe","serial:FBC18F0680B0",*cmds],capture_output=True,text=True)
print(p.stdout, p.stderr, flush=True)
o,_ = cap.communicate(timeout=120)
print("capture rc", cap.returncode, o.strip()[-400:])
