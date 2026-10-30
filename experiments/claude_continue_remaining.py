"""Serial controller for the remaining candidates (added by Claude at the user's request).

Runs one job at a time:
  Wan 2.1: claude_bench_only.py wan21 (warm-up + seeds 42/43/44 + verify; its cold smoke already passed)
  Wan 2.2: download_ranges.py -> continue_tests.py (server, smoke, bench, verify)
  LTX-2.3 MLX: retire_candidate_weights.py -> disk check -> download_ranges.py -> benchmark.py -> verify_outputs.py
This mirrors continue_comparison.py and continue_mlx.py. Additions: each active stage runs under
`caffeinate -i`; when claude_battery_guard.py stops a GPU stage on low battery, the stage's
logs are copied to logs/battery-stop-<time>/, the controller waits for a charger and repeats the
whole stage (cold smoke included). On battery, a GPU test stage starts only at or above START
percent and a download at or above DL_START percent; below that the controller waits for a
charger, so the last few percent are not spent on a run the guard would stop anyway. Any other
failure stops the chain for review.

Usage: python claude_continue_remaining.py [guard_stop_percent=6] [gpu_start_percent=30]
"""
import json,re,shutil,subprocess,sys,time
from pathlib import Path
R=Path(__file__).resolve().parent;M=R/'ltx23-mlx';W=R/'wan22'
COMFY='/Users/dyn/AI/venvs/comfyui/bin/python';MLX='/Users/dyn/AI/venvs/ltx-mlx/bin/python'
STOP=int(sys.argv[1]) if len(sys.argv)>1 else 6  # must match the battery guard's stop percent
START=int(sys.argv[2]) if len(sys.argv)>2 else 30  # on battery, a GPU test stage starts only at or above this charge
DL_START=10  # on battery, a download starts only at or above this charge

def write(path,stage,**extra):
    row={'time':time.time(),'stage':stage,'controller':'claude_continue_remaining.py',**extra}
    tmp=path.with_suffix('.tmp');tmp.write_text(json.dumps(row,indent=2));tmp.replace(path);print(json.dumps(row),flush=True)
def state(stage,**extra): write(R/'comparison-state.json',stage,**extra)
def mlx_state(stage,**extra): write(M/'pipeline-state.json',stage,**extra)
def stage_of(folder):
    try: return json.loads((folder/'pipeline-state.json').read_text())['stage']
    except (OSError,ValueError,KeyError): return None
def power():
    out=subprocess.check_output(['pmset','-g','batt'],text=True);m=re.search(r'(\d+)%',out)
    return "'AC Power'" in out,int(m.group(1)) if m else None
def wait_for_charger(reason):
    state('waiting_for_charger',reason=reason,battery_percent=power()[1])
    while not power()[0]: time.sleep(60)
    state('charger_connected_resuming',reason=reason,battery_percent=power()[1])
def guard_acted(since):
    p=R/'logs/battery-guard.jsonl'
    rows=[json.loads(x) for x in p.read_text().splitlines() if x.strip()] if p.exists() else []
    return any(x.get('action') and x['time']>=since for x in rows)
def run(cmd,log,mode='a'):
    with log.open(mode) as out:
        child=subprocess.Popen(cmd,stdout=out,stderr=subprocess.STDOUT)
        awake=subprocess.Popen(['caffeinate','-i','-w',str(child.pid)])
        code=child.wait();awake.wait()
    return code
def need_charge(name,minimum):
    ac,pct=power()
    if not ac and pct is not None and pct<minimum: wait_for_charger(f'{name}: battery {pct}% is below the {minimum}% needed to start')
def gpu_stage(name,folder,cmd,log):
    for attempt in range(1,4):
        need_charge(name,START)
        start=time.time();code=run(cmd,log)
        if not code or not guard_acted(start): return code
        keep=folder/'logs'/f'battery-stop-{int(start)}';keep.mkdir(parents=True,exist_ok=True)
        for p in [*(folder/'logs').glob('*.*'),folder/'pipeline-state.json']:
            if p.is_file(): shutil.copy2(p,keep/p.name)
        wait_for_charger(f'{name} stopped by battery guard on attempt {attempt}; logs copied to {keep.name}')
    return code

if subprocess.run(['pgrep','-f','claude_bench_only.py wan21'],capture_output=True).returncode==0:
    # Restarted controller: the Wan 2.1 bench rerun launched by the previous instance is still running.
    state('waiting_for_wan21',detail='bench rerun already running')
    while (s:=stage_of(R/'wan21'))!='complete_pending_visual_review':
        if s and s.endswith('failed'): state('needs_review',model='wan21',detail=s);sys.exit(1)
        time.sleep(15)
elif subprocess.run(['pgrep','-f','run_server.py'],capture_output=True).returncode==0: state('needs_review',detail='a ComfyUI server is already running');sys.exit(1)
if stage_of(R/'wan21')!='complete_pending_visual_review':
    # Cold smoke already succeeded; Claude interrupted seed 42 for a colour check, so only bench + verify repeat.
    state('testing',model='wan21',detail='bench rerun after manual interrupt; cold smoke kept')
    if code:=gpu_stage('wan21 bench',R/'wan21',[COMFY,'-u',str(R/'claude_bench_only.py'),'wan21'],R/'wan21/logs/controller.log'): state('needs_review',model='wan21',exit_code=code);sys.exit(code)
while subprocess.run(['pgrep','-f','run_server.py'],capture_output=True).returncode==0: time.sleep(5)
time.sleep(8)

need_charge('wan22 download',DL_START)
state('downloading',model='wan22')
if code:=run([COMFY,'-u',str(W/'download_ranges.py')],W/'logs/download.log'): state('download_failed',model='wan22',exit_code=code);sys.exit(code)
state('testing',model='wan22')
if code:=gpu_stage('wan22 tests',W,[COMFY,'-u',str(W/'continue_tests.py')],W/'logs/controller.log'): state('needs_review',model='wan22',exit_code=code);sys.exit(code)
state('comfy_candidates_complete_pending_visual_review')
time.sleep(8)

mlx_state('releasing_completed_candidate_cache')
if code:=subprocess.call([COMFY,str(R/'retire_candidate_weights.py')]): mlx_state('cache_cleanup_failed');state('needs_review',model='ltx23-mlx',detail='cache_cleanup_failed');sys.exit(code)
sources=json.loads((M/'models-sources.json').read_text())
needed=sum(x['metadata'][0]['size'] for x in sources if not (M/x['kind']/Path(x['file']).name).exists())
free=shutil.disk_usage(R).free
if free<needed+5*1024**3: mlx_state('insufficient_disk',free_bytes=free,download_bytes=needed,reserve_bytes=5*1024**3);state('needs_review',model='ltx23-mlx',detail='insufficient_disk');sys.exit(1)
need_charge('ltx23-mlx download',DL_START)
state('downloading',model='ltx23-mlx');mlx_state('downloading',download_bytes=needed)
if code:=run([MLX,'-u',str(M/'download_ranges.py')],M/'logs/download.log'): mlx_state('download_failed');state('download_failed',model='ltx23-mlx',exit_code=code);sys.exit(code)
state('testing',model='ltx23-mlx');mlx_state('running_local_benchmark')
if code:=gpu_stage('ltx23-mlx benchmark',M,[MLX,'-u',str(M/'benchmark.py')],M/'logs/benchmark.log'): mlx_state('benchmark_failed',exit_code=code);state('needs_review',model='ltx23-mlx',exit_code=code);sys.exit(code)
code=run([MLX,str(M/'verify_outputs.py')],M/'logs/output-verification.log','w')
mlx_state('complete_pending_visual_review' if not code else 'output_verification_failed')
state('all_candidates_complete_pending_visual_review' if not code else 'needs_review',model='ltx23-mlx')
sys.exit(code)
