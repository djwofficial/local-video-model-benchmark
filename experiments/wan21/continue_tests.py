import json,subprocess,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parent
statepath=ROOT/'pipeline-state.json'
def state(stage,**extra):
    row={'time':time.time(),'stage':stage,**extra}
    tmp=statepath.with_suffix('.tmp');tmp.write_text(json.dumps(row,indent=2));tmp.replace(statepath)
    print(json.dumps(row),flush=True)
sources=json.loads((ROOT/'models-sources.json').read_text())
expected={str(Path('/Users/dyn/AI/models')/kind/Path(x['file']).name):x['metadata'][0] for x in sources for kind in [x['kind']]}
state('waiting_for_verified_models')
while True:
    p=ROOT/'model-integrity.json'
    try: entries={x['path']:x for x in json.loads(p.read_text())} if p.exists() else {}
    except json.JSONDecodeError: entries={}
    ready=all(path in entries and entries[path].get('verified') and entries[path]['sha256']==info['lfs']['oid'] and Path(path).exists() and Path(path).stat().st_size==info['size'] for path,info in expected.items())
    if ready: break
    time.sleep(10)
state('starting_local_server')
serverlog=(ROOT/'logs/server.log').open('a')
server=subprocess.Popen([sys.executable,'-u',str(ROOT/'run_server.py')],stdout=serverlog,stderr=subprocess.STDOUT)
import urllib.request
for _ in range(90):
    try:
        with urllib.request.urlopen('http://127.0.0.1:8188/system_stats',timeout=2) as response: response.read()
        break
    except OSError: time.sleep(2)
else: state('server_start_failed');server.terminate();sys.exit(1)
try:
    for mode in ['smoke','bench']:
        state('running_'+mode)
        with (ROOT/('logs/'+mode+'-run.log')).open('w') as log:
            code=subprocess.call([sys.executable,'-u',str(ROOT/'benchmark.py'),mode],stdout=log,stderr=subprocess.STDOUT)
        if code: state(mode+'_failed',exit_code=code);sys.exit(code)
    with (ROOT/'logs/output-verification.log').open('w') as log:
        code=subprocess.call([sys.executable,str(ROOT/'verify_outputs.py')],stdout=log,stderr=subprocess.STDOUT)
    state('complete_pending_visual_review' if not code else 'output_verification_failed')
    if code: sys.exit(code)
finally:
    server.terminate();server.wait(timeout=30);serverlog.close()
