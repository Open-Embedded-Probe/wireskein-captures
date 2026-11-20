"""WireSkein's rvswd (clk / dio) and swio (dio) readings of a capture, in time order.

    uv run --project <wireskein> python tools/dec.py <capture> [max rows]   (runs `wireskein` from PATH)"""
import json, subprocess, sys
f=sys.argv[1]; lim=int(sys.argv[2]) if len(sys.argv)>2 else 60
W=["wireskein"]
specs={"rvswd":'{"buses":[{"protocol":"rvswd","pins":{"clk":"SWCLK","dio":"SWIO"}}]}',"swio":'{"buses":[{"protocol":"swio","pins":{"dio":"SWIO"}}]}'}
rows=[]
for P,s in specs.items():
    d=json.loads(subprocess.run(W+["decode",f,"--spec",s],capture_output=True,text=True).stdout)
    for part in d.get("parts",[d]):
        for b in part.get("buses",[]):
            for r in (b.get("dmi") or (b.get("result") or {}).get("dmi") or []):
                r["P"]=P; rows.append(r)
rows.sort(key=lambda r:r.get("s",0))
prev=None; n=0
for r in rows:
    t=r.get("s",0)/5e7
    if prev is not None and t-prev>0.02: print("   ...gap %.1f ms"%((t-prev)*1e3))
    prev=t
    dv=r.get("data"); dv=hex(dv) if isinstance(dv,int) else dv
    print(f"{t:9.4f} {r['P']:5s} {r['op']:5s} {hex(r['addr']):5s} {dv} {'ok' if r.get('ok',True) else 'BAD'}{'' if r.get('answered',True) else ' noans'}")
    n+=1
    if n>=lim: break
