"""Retire only task-downloaded Comfy candidate weights after completed tests.
Preserve baseline, outputs, workflows, logs and model source/checksum manifests.
"""
import json,hashlib,time,subprocess,sys
from pathlib import Path
R=Path(__file__).resolve().parent
assert subprocess.run(['pgrep','-f','run_server.py'],capture_output=True).returncode!=0, 'ComfyUI server is still running'
sources=[]
for model in (sys.argv[1:] or ['ltx-distilled','wan21','wan22']):
 assert model in ['ltx-distilled','wan21','wan22']
 p=R/model
 state=json.loads((p/'pipeline-state.json').read_text())['stage'];assert state=='complete_pending_visual_review',(model,state)
 rows=[json.loads(x) for x in (p/'results.jsonl').read_text().splitlines()]
 assert all(any(x['label']==f'benchmark-49f-seed{seed}' and x['status'] in ['finished','execution_success'] for x in rows) for seed in [42,43,44]),model
 for x in json.loads((p/'models-sources.json').read_text()):
  kind=x.get('kind','checkpoints');dest=Path('/Users/dyn/AI/models')/kind/Path(x['file']).name
  assert dest.name not in ['ltx-video-2b-v0.9.5.safetensors','t5xxl_fp16.safetensors']
  sources.append((x,dest))
record=json.loads((R/'retired-candidate-cache.json').read_text()) if (R/'retired-candidate-cache.json').exists() else [];seen=set()
for item,dest in sources:
 if str(dest) in seen:continue
 seen.add(str(dest));info=item['metadata'][0]
 if not dest.exists():continue
 if dest.name=='umt5_xxl_fp8_e4m3fn_scaled.safetensors' and (not (R/'wan22/pipeline-state.json').exists() or json.loads((R/'wan22/pipeline-state.json').read_text())['stage']!='complete_pending_visual_review'):
  print('Retained shared Wan encoder:',dest,flush=True);continue
 assert dest.stat().st_size==info['size'];assert hashlib.file_digest(dest.open('rb'),'sha256').hexdigest()==info['lfs']['oid']
 record.append({'path':str(dest),'bytes':dest.stat().st_size,'sha256':info['lfs']['oid'],'recovery_url':'https://huggingface.co/'+item['repo']+'/resolve/main/'+item['file'],'reason':'task-created candidate cache retired after completed benchmark to fit next 28.14GB MLX candidate','time':time.time()});dest.unlink()
 print('Retired completed-test cache:',dest,flush=True)
(R/'retired-candidate-cache.json').write_text(json.dumps(record,indent=2))
