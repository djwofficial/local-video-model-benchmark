"""Memory / size ladder for the LTX-2.3 + keyframes setup (round 4, added by Claude).

Runs ladder_case.py once per configuration, each in its own process so its lifetime peak memory is
its own: resolution at 49 frames (768×512 → 1536×1024, 3:2 like the anchors), length at 768×512
(97 → 145 frames), then the largest passing resolution at 97 frames. Each case renders seed 42 (cold,
with text encoding) and seed 43 (warm). An axis stops at the first case that fails, exceeds LIMIT GiB of
sampled process phys_footprint, or grows swap by more than 2 GiB during the warm run.
Writes ladder-results.json and LADDER.md. Exit code is 0 when the ladder ran, even if it stopped early.
"""
import json,subprocess,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parent
LIMIT=19.0  # GiB; macOS recommends at most 19.07 GB of GPU working set on a 24 GB Mac
GiB=2**30

def case(w,h,f):
    cfg=f'{w}x{h}x{f}';print('CASE',cfg,flush=True)
    with (ROOT/'logs'/f'ladder-{cfg}.log').open('w') as log:
        code=subprocess.call([sys.executable,'-u',str(ROOT/'ladder_case.py'),str(w),str(h),str(f)],stdout=log,stderr=subprocess.STDOUT)
    rows=[json.loads(x) for x in (ROOT/'results.jsonl').read_text().splitlines() if x.strip()] if (ROOT/'results.jsonl').exists() else []
    rows=[x for x in rows if x['config']==cfg]
    stop=(ROOT/'logs/safety-stop.json')
    r={'config':cfg,'width':w,'height':h,'frames':f,'exit_code':code,'runs':len(rows),
       'ok':code==0 and len(rows)==2 and all(x['status']=='success' for x in rows),
       'peak_footprint_gib':max((x['phys_footprint_lifetime_max_bytes'] for x in rows),default=0)/GiB,
       'warm_footprint_gib':max((x['phys_footprint_sampled_max_bytes'] for x in rows if not x['cold']),default=0)/GiB,
       'mlx_peak_gib':max((x['mlx_peak_sampled_max_bytes'] for x in rows),default=0)/GiB,
       'warm_swap_delta_gib':max((x['swap_delta_bytes'] for x in rows if not x['cold']),default=0)/GiB,
       'warm_seconds':next((x['elapsed_client_s'] for x in rows if not x['cold']),None),
       'cold_seconds':next((x['elapsed_client_s'] for x in rows if x['cold']),None)}
    if stop.exists() and stop.stat().st_mtime>time.time()-7200 and code: r['safety_stop']=json.loads(stop.read_text())
    sampled=max([r['peak_footprint_gib']]+[x['phys_footprint_sampled_max_bytes']/GiB for x in rows])
    r['fits']=r['ok'] and sampled<=LIMIT and r['warm_swap_delta_gib']<=2
    results.append(r);(ROOT/'ladder-results.json').write_text(json.dumps(results,indent=2))
    print('RESULT',json.dumps(r),flush=True)
    return r['fits']

results=[]
best=None
for w,h in [(768,512),(960,640),(1152,768),(1344,896),(1536,1024)]:
    if not case(w,h,49): break
    best=(w,h)
for f in (97,121,145):
    if not case(768,512,f): break
if best and best!=(768,512): case(*best,97)

lines=['# LTX-2.3 + keyframes: memory / size ladder','',f'Limit for "fits": sampled process phys_footprint ≤ {LIMIT} GiB and warm-run swap growth ≤ 2 GiB. Seed 42 cold (includes text encoding), seed 43 warm. AC power, M4 Pro 24 GB.','',
       '|Config (W×H×frames)|Runs OK|Peak process GiB|Warm-run process GiB|MLX peak GiB|Warm swap Δ GiB|Warm s/video|Fits 24 GB|','|---|---|---:|---:|---:|---:|---:|---|']
for r in results:
    lines.append(f"|{r['config']}|{'yes' if r['ok'] else 'no'}|{r['peak_footprint_gib']:.2f}|{r['warm_footprint_gib']:.2f}|{r['mlx_peak_gib']:.2f}|{r['warm_swap_delta_gib']:.2f}|{r['warm_seconds'] or '—'}|{'yes' if r['fits'] else 'no'}|")
(ROOT/'LADDER.md').write_text('\n'.join(lines)+'\n')
print('LADDER_COMPLETED',flush=True)
