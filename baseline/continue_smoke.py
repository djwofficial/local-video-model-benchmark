import json,subprocess,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parent
statepath=ROOT/'pipeline-state.json'
def state(stage,**extra):
    row={'time':time.time(),'stage':stage,**extra}
    tmp=statepath.with_suffix('.tmp');tmp.write_text(json.dumps(row,indent=2));tmp.replace(statepath)
    print(json.dumps(row),flush=True)
sources=json.loads((ROOT/'models-sources.json').read_text())
expected={str(Path('/Users/dyn/AI/models')/kind/Path(x['file']).name):x['metadata'][0] for x,kind in zip(sources,['checkpoints','text_encoders'])}
state('waiting_for_verified_models')
while True:
    p=ROOT/'model-integrity.json'
    try: entries={x['path']:x for x in json.loads(p.read_text())} if p.exists() else {}
    except json.JSONDecodeError: entries={}
    ready=all(path in entries and entries[path].get('verified') and entries[path]['sha256']==info['lfs']['oid'] and Path(path).exists() and Path(path).stat().st_size==info['size'] for path,info in expected.items())
    if ready: break
    time.sleep(10)
state('running_smoke_25_frames_seed41')
with (ROOT/'logs/smoke-run.log').open('w',buffering=1) as log:
    code=subprocess.call([sys.executable,'-u',str(ROOT/'benchmark.py'),'smoke'],stdout=log,stderr=subprocess.STDOUT)
if code:
    state('smoke_failed',exit_code=code);sys.exit(code)
state('verifying_smoke_output')
with (ROOT/'logs/verification-smoke.log').open('w') as log:
    code=subprocess.call([sys.executable,str(ROOT/'verify_outputs.py')],stdout=log,stderr=subprocess.STDOUT)
if code:
    state('smoke_verification_failed',exit_code=code);sys.exit(code)
state('smoke_ready_for_visual_inspection')
