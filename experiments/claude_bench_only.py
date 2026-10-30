"""Repeat only the warm benchmark of a ComfyUI candidate (added by Claude).

Usage: python claude_bench_only.py <model_folder>
Same steps as that folder's continue_tests.py without the cold smoke: start run_server.py, run
benchmark.py bench (49-frame warm-up seed 41, then seeds 42/43/44) and verify_outputs.py, then
stop the server. Used when a benchmark was interrupted after its cold smoke had already
succeeded; in the new server session the warm-up absorbs model loading and prompt encoding.
"""
import json,subprocess,sys,time,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parent/sys.argv[1]
statepath=ROOT/'pipeline-state.json'
def state(stage,**extra):
    row={'time':time.time(),'stage':stage,'controller':'claude_bench_only.py',**extra}
    tmp=statepath.with_suffix('.tmp');tmp.write_text(json.dumps(row,indent=2));tmp.replace(statepath)
    print(json.dumps(row),flush=True)
state('starting_local_server')
serverlog=(ROOT/'logs/server.log').open('a')
server=subprocess.Popen([sys.executable,'-u',str(ROOT/'run_server.py')],stdout=serverlog,stderr=subprocess.STDOUT)
for _ in range(90):
    try:
        with urllib.request.urlopen('http://127.0.0.1:8188/system_stats',timeout=2) as response: response.read()
        break
    except OSError: time.sleep(2)
else: state('server_start_failed');server.terminate();sys.exit(1)
try:
    state('running_bench')
    with (ROOT/'logs/bench-run.log').open('w') as log:
        code=subprocess.call([sys.executable,'-u',str(ROOT/'benchmark.py'),'bench'],stdout=log,stderr=subprocess.STDOUT)
    if code: state('bench_failed',exit_code=code);sys.exit(code)
    with (ROOT/'logs/output-verification.log').open('w') as log:
        code=subprocess.call([sys.executable,str(ROOT/'verify_outputs.py')],stdout=log,stderr=subprocess.STDOUT)
    state('complete_pending_visual_review' if not code else 'output_verification_failed')
    if code: sys.exit(code)
finally:
    server.terminate();server.wait(timeout=30);serverlog.close()
