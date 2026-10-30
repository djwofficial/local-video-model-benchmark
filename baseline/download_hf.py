import json,hashlib,os,time
from pathlib import Path
os.environ['HF_HUB_DISABLE_TELEMETRY']='1'
from huggingface_hub import hf_hub_download
root=Path('/Users/dyn/AI/ltx-benchmark-2026-10-29')
models=json.loads((root/'models-sources.json').read_text())
results=[]
for item,kind in zip(models,['checkpoints','text_encoders']):
 info=item['metadata'][0]
 dest=Path('/Users/dyn/AI/models')/kind/Path(item['file']).name
 dest.parent.mkdir(parents=True,exist_ok=True)
 print('START',dest.name,'bytes',info['size'],flush=True)
 if not dest.exists():
  target=Path(hf_hub_download(item['repo'],item['file'],local_dir='/Users/dyn/AI/models/.downloads'))
 else: target=dest
 assert target.stat().st_size==info['size'], 'size mismatch'
 h=hashlib.file_digest(target.open('rb'),'sha256').hexdigest()
 assert h==info['lfs']['oid'], 'hash mismatch'
 if target!=dest: target.rename(dest)
 results.append({'path':str(dest),'bytes':info['size'],'sha256':h,'verified':True})
 (root/'model-integrity.json').write_text(json.dumps(results,indent=2))
 print('VERIFIED',dest.name,h,flush=True)
