import json,time,subprocess,sys,shutil
from pathlib import Path
R=Path(__file__).resolve().parent;M=R/'ltx23-mlx';P='/Users/dyn/AI/venvs/ltx-mlx/bin/python'
def state(stage,**kw):
 row={'time':time.time(),'stage':stage,**kw};(M/'pipeline-state.json').write_text(json.dumps(row,indent=2));print(json.dumps(row),flush=True)
state('waiting_for_comfy_candidates')
while True:
 try:s=json.loads((R/'comparison-state.json').read_text())
 except (OSError,ValueError):s={}
 if s.get('stage')=='comfy_candidates_complete_pending_visual_review':break
 if s.get('stage') in ['needs_review','download_failed']:state('prior_candidate_needs_review',detail=s);sys.exit(1)
 time.sleep(10)
time.sleep(8)
state('releasing_completed_candidate_cache')
code=subprocess.call([sys.executable,str(R/'retire_candidate_weights.py')])
if code:state('cache_cleanup_failed');sys.exit(code)
sources=json.loads((M/'models-sources.json').read_text());needed=sum(x['metadata'][0]['size'] for x in sources if not (M/x['kind']/Path(x['file']).name).exists())
free=shutil.disk_usage(R).free
if free<needed+5*1024**3:state('insufficient_disk',free_bytes=free,download_bytes=needed,reserve_bytes=5*1024**3);sys.exit(1)
state('downloading',download_bytes=needed)
with (M/'logs/download.log').open('a') as out:code=subprocess.call([P,'-u',str(M/'download_ranges.py')],stdout=out,stderr=subprocess.STDOUT)
if code:state('download_failed');sys.exit(code)
state('running_local_benchmark')
with (M/'logs/benchmark.log').open('a') as out:code=subprocess.call([P,'-u',str(M/'benchmark.py')],stdout=out,stderr=subprocess.STDOUT)
if code:state('benchmark_failed',exit_code=code);sys.exit(code)
with (M/'logs/output-verification.log').open('w') as out:code=subprocess.call([P,str(M/'verify_outputs.py')],stdout=out,stderr=subprocess.STDOUT)
state('complete_pending_visual_review' if not code else 'output_verification_failed')
if code:sys.exit(code)
