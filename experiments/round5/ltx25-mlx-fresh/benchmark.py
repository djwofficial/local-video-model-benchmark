"""Fresh-process memory test for LTX-2.5 distilled MLX int4 (round 5, added by Claude).

Runs fresh_case.py once per video (red ball and blue car, seeds 42-44), each in a new process, so each video includes
loading the text encoder and the models, as the Mac-mini script does. A video's peak memory is its process's lifetime
phys_footprint. Writes fresh-results.json and FRESH.md (per-video time and peak, and per prompt the average of the peaks).
"""
import json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent;GiB=2**30
cases=[(k,s) for k in ('redball','bluecar') for s in (42,43,44)]
failed=[]
for k,s in cases:
    print('CASE',k,s,flush=True)
    with (ROOT/'logs'/f'fresh-{k}-seed{s}.log').open('w') as log:
        code=subprocess.call([sys.executable,'-u',str(ROOT/'fresh_case.py'),k,str(s)],stdout=log,stderr=subprocess.STDOUT)
    if code: failed.append((k,s,code))
rows=[json.loads(x) for x in (ROOT/'results.jsonl').read_text().splitlines() if x.strip()]
out={}
for k in ('redball','bluecar'):
    r=[x for x in rows if x['prompt_key']==k and x['status']=='success']
    out[k]={'videos':{x['seed']:{'seconds':x['elapsed_client_s'],'peak_gib':x['phys_footprint_lifetime_max_bytes']/GiB,'sampled_max_gib':x['phys_footprint_sampled_max_bytes']/GiB,
                                 'mlx_peak_gib':x['mlx_peak_sampled_max_bytes']/GiB,'swap_delta_gib':x['swap_delta_bytes']/GiB,'conditions':x['conditions']} for x in r},
            'avg_peak_gib':sum(x['phys_footprint_lifetime_max_bytes'] for x in r)/len(r)/GiB if r else None,
            'max_peak_gib':max((x['phys_footprint_lifetime_max_bytes'] for x in r),default=0)/GiB,'mean_seconds':sum(x['elapsed_client_s'] for x in r)/len(r) if r else None}
(ROOT/'fresh-results.json').write_text(json.dumps(out,indent=2))
lines=['# LTX-2.5 fresh runs: one video per process','','Each video is its own process (loads the text encoder and models), as the Mac-mini script does. Peak = process lifetime phys_footprint.','',
       '|Prompt|Seed|Seconds (incl. loading)|Peak GiB|','|---|---:|---:|---:|']
for k,v in out.items():
    for s,x in sorted(v['videos'].items()): lines.append(f"|{k}|{s}|{x['seconds']:.1f}|{x['peak_gib']:.2f}|")
    if v['avg_peak_gib']: lines.append(f"|{k}|average|{v['mean_seconds']:.1f}|{v['avg_peak_gib']:.2f}|")
(ROOT/'FRESH.md').write_text('\n'.join(lines)+'\n')
print('FRESH_COMPLETED',json.dumps(out),flush=True)
sys.exit(1 if failed else 0)
