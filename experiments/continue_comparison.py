import json,time,subprocess,sys
from pathlib import Path
R=Path(__file__).resolve().parent
P='/Users/dyn/AI/venvs/comfyui/bin/python'
def state(stage,**extra):
 row={'time':time.time(),'stage':stage,**extra};(R/'comparison-state.json').write_text(json.dumps(row,indent=2));print(json.dumps(row),flush=True)
state('waiting_for_ltx_distilled')
while True:
 try:s=json.loads((R/'ltx-distilled/pipeline-state.json').read_text())['stage']
 except (OSError,ValueError):s='waiting'
 if s=='complete_pending_visual_review':break
 if s.endswith('_failed'):state('needs_review',model='ltx-distilled',detail=s);sys.exit(1)
 time.sleep(10)
time.sleep(8)
for model in ['wan21','wan22']:
 r=R/model
 state('downloading',model=model)
 with (r/'logs/download.log').open('a') as out:
  code=subprocess.call([P,'-u',str(r/'download_ranges.py')],stdout=out,stderr=subprocess.STDOUT)
 if code:state('download_failed',model=model);sys.exit(code)
 state('testing',model=model)
 with (r/'logs/controller.log').open('a') as out:
  code=subprocess.call([P,'-u',str(r/'continue_tests.py')],stdout=out,stderr=subprocess.STDOUT)
 if code:state('needs_review',model=model);sys.exit(code)
 time.sleep(8)
state('comfy_candidates_complete_pending_visual_review')
