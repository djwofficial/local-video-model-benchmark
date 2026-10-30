"""Run a ComfyUI candidate folder's tests in one server session (added by Claude).

Usage: python claude_comfy_tests.py <folder> <mode>[,<mode>...]     e.g. round2/ltx095 smoke,bench
Same steps as a model folder's continue_tests.py, for folders whose weights are already verified:
start <folder>/run_server.py, run <folder>/benchmark.py once per mode in order, then
verify_outputs.py, and stop the server. Writes <folder>/pipeline-state.json the same way.
"""
import json,subprocess,sys,time,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parent/sys.argv[1];MODES=sys.argv[2].split(',')
statepath=ROOT/'pipeline-state.json'
def state(stage,**extra):
    row={'time':time.time(),'stage':stage,'controller':'claude_comfy_tests.py',**extra}
    tmp=statepath.with_suffix('.tmp');tmp.write_text(json.dumps(row,indent=2));tmp.replace(statepath)
    print(json.dumps(row),flush=True)
(ROOT/'logs').mkdir(exist_ok=True)
state('starting_local_server',modes=MODES)
serverlog=(ROOT/'logs/server.log').open('a')
server=subprocess.Popen([sys.executable,'-u',str(ROOT/'run_server.py')],stdout=serverlog,stderr=subprocess.STDOUT)
for _ in range(90):
    try:
        with urllib.request.urlopen('http://127.0.0.1:8188/system_stats',timeout=2) as response: response.read()
        break
    except OSError: time.sleep(2)
else: state('server_start_failed');server.terminate();sys.exit(1)
try:
    for mode in MODES:
        state('running_'+mode)
        with (ROOT/f'logs/{mode}-run.log').open('w') as log:
            code=subprocess.call([sys.executable,'-u',str(ROOT/'benchmark.py'),mode],stdout=log,stderr=subprocess.STDOUT)
        if code: state(mode+'_failed',exit_code=code);sys.exit(code)
    with (ROOT/'logs/output-verification.log').open('w') as log:
        code=subprocess.call([sys.executable,str(ROOT/'verify_outputs.py')],stdout=log,stderr=subprocess.STDOUT)
    state('complete_pending_visual_review' if not code else 'output_verification_failed')
    if code: sys.exit(code)
finally:
    server.terminate();server.wait(timeout=30);serverlog.close()
