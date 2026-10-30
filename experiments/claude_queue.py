"""Serial queue for further candidate stages (added by Claude).

Usage: python claude_queue.py <stage> [<stage> ...]
  download:<folder>         <folder>/download_ranges.py (MLX Python for ltx23-mlx, Comfy Python otherwise)
  comfy:<folder>:<modes>    claude_comfy_tests.py <folder> <modes>; skipped when already complete
  retire:<model>[,<model>]  retire_candidate_weights.py for completed Comfy candidates
  mlx:<folder>              <folder>/benchmark.py then verify_outputs.py with the MLX Python, as continue_mlx.py;
                            skipped when already complete
Runs the stages in order, one job at a time, writes each step to comparison-state.json and stops at
the first failure. Every stage first waits for a download, ComfyUI server or benchmark left running by
an earlier controller; a comfy stage whose folder that run completed is skipped, and one it failed stops
the queue for review instead of being repeated. On battery, downloads start only at DL_START percent and GPU stages at START
percent, otherwise the queue waits for a charger. A GPU stage stopped by claude_battery_guard.py
(run it with the same STOP percent) has its logs copied to <folder>/logs/battery-stop-<time>/ and is
repeated after charging. Run under claude_battery_guard.py like claude_continue_remaining.py.
"""
import json,re,shutil,subprocess,sys,time
from pathlib import Path
R=Path(__file__).resolve().parent
COMFY='/Users/dyn/AI/venvs/comfyui/bin/python';MLX='/Users/dyn/AI/venvs/ltx-mlx/bin/python'
STOP,START,DL_START=6,30,10
T0=time.time()

def state(stage,**extra):
    row={'time':time.time(),'stage':stage,'controller':'claude_queue.py',**extra}
    tmp=R/'comparison-state.tmp';tmp.write_text(json.dumps(row,indent=2));tmp.replace(R/'comparison-state.json');print(json.dumps(row),flush=True)
def write_state(folder,stage,**extra):
    row={'time':time.time(),'stage':stage,'controller':'claude_queue.py',**extra}
    tmp=folder/'pipeline-state.tmp';tmp.write_text(json.dumps(row,indent=2));tmp.replace(folder/'pipeline-state.json')
def pstate(folder):
    try: return json.loads((folder/'pipeline-state.json').read_text())
    except (OSError,ValueError): return {}
def power():
    out=subprocess.check_output(['pmset','-g','batt'],text=True);m=re.search(r'(\d+)%',out)
    return "'AC Power'" in out,int(m.group(1)) if m else None
def wait_for_charger(reason):
    state('waiting_for_charger',reason=reason,battery_percent=power()[1])
    while not power()[0]: time.sleep(60)
    state('charger_connected_resuming',reason=reason,battery_percent=power()[1])
def need_charge(name,minimum):
    ac,pct=power()
    if not ac and pct is not None and pct<minimum: wait_for_charger(f'{name}: battery {pct}% is below the {minimum}% needed to start')
def wait_idle():
    while subprocess.run(['pgrep','-f',r'download_ranges\.py|run_server\.py|/benchmark\.py'],capture_output=True).returncode==0: time.sleep(10)
def guard_acted(since):
    p=R/'logs/battery-guard.jsonl'
    rows=[json.loads(x) for x in p.read_text().splitlines() if x.strip()] if p.exists() else []
    return any(x.get('action') and x['time']>=since for x in rows)
def run(cmd,log):
    with log.open('a') as out:
        child=subprocess.Popen(cmd,stdout=out,stderr=subprocess.STDOUT)
        awake=subprocess.Popen(['caffeinate','-i','-w',str(child.pid)])
        code=child.wait();awake.wait()
    return code
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

for spec in sys.argv[1:]:
    kind,_,rest=spec.partition(':');wait_idle()
    if kind=='download':
        folder=R/rest;(folder/'logs').mkdir(exist_ok=True)
        if rest=='ltx23-mlx':  # same disk check as continue_mlx.py: missing files plus a 5 GiB reserve for swap
            needed=sum(x['metadata'][0]['size'] for x in json.loads((folder/'models-sources.json').read_text()) if not (folder/x['kind']/Path(x['file']).name).exists())
            if (free:=shutil.disk_usage(R).free)<needed+5*1024**3: state('insufficient_disk',model=rest,free_bytes=free,download_bytes=needed);sys.exit(1)
        need_charge(spec,DL_START);state('downloading',model=rest)
        code=run([MLX if rest=='ltx23-mlx' else COMFY,'-u',str(folder/'download_ranges.py')],folder/'logs/download.log')
        if code: state('download_failed',model=rest,exit_code=code);sys.exit(code)
    elif kind=='comfy':
        name,_,modes=rest.partition(':');folder=R/name;st=pstate(folder)
        if st.get('stage')=='complete_pending_visual_review': print('skip completed',name,flush=True);continue
        if str(st.get('stage','')).endswith('failed') and st.get('time',0)>=T0: state('needs_review',model=name,detail='run left by an earlier controller failed: '+st['stage']);sys.exit(1)
        state('testing',model=name,modes=modes)
        code=gpu_stage(spec,folder,[COMFY,'-u',str(R/'claude_comfy_tests.py'),name,modes],folder/'logs/controller.log')
        if code: state('needs_review',model=name,exit_code=code);sys.exit(code)
    elif kind=='retire':
        state('retiring_completed_candidate_caches',models=rest)
        if code:=subprocess.call([COMFY,str(R/'retire_candidate_weights.py'),*rest.split(',')]): state('needs_review',detail='retire failed',exit_code=code);sys.exit(code)
    elif kind=='mlx':
        folder=R/rest;(folder/'logs').mkdir(exist_ok=True)
        if pstate(folder).get('stage')=='complete_pending_visual_review': print('skip completed',rest,flush=True);continue
        state('testing',model=rest);write_state(folder,'running_local_benchmark')
        if code:=gpu_stage(spec,folder,[MLX,'-u',str(folder/'benchmark.py')],folder/'logs/benchmark.log'):
            write_state(folder,'benchmark_failed',exit_code=code);state('needs_review',model=rest,exit_code=code);sys.exit(code)
        code=run([MLX,str(folder/'verify_outputs.py')],folder/'logs/output-verification.log')
        write_state(folder,'complete_pending_visual_review' if not code else 'output_verification_failed')
        if code: state('needs_review',model=rest,detail='output verification failed');sys.exit(code)
    else: raise SystemExit('unknown stage '+spec)
state('queue_complete_pending_review',stages=sys.argv[1:])
