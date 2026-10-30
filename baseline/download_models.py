import json,hashlib,subprocess,time
from pathlib import Path
root=Path('/Users/dyn/AI/ltx-benchmark-2026-10-29')
models=json.loads((root/'models-sources.json').read_text())
results=[]
for item,kind in zip(models,['checkpoints','text_encoders']):
 info=item['metadata'][0]
 dest=Path('/Users/dyn/AI/models')/kind/Path(item['file']).name
 dest.parent.mkdir(parents=True,exist_ok=True)
 part=dest.with_suffix(dest.suffix+'.partial')
 if not dest.exists():
  url='https://huggingface.co/'+item['repo']+'/resolve/main/'+item['file']
  print('Downloading',dest.name,'expected bytes',info['size'],flush=True)
  with (root/'logs'/('download-'+kind+'.log')).open('a') as log:
   subprocess.run(['curl','--fail','--location','--retry','6','--retry-delay','5','--continue-at','-','--output',str(part),url],stdout=log,stderr=log,check=True)
  target=part
 else: target=dest
 assert target.stat().st_size==info['size'], (str(target),'size mismatch')
 h=hashlib.file_digest(target.open('rb'),'sha256').hexdigest()
 assert h==info['lfs']['oid'], (str(target),'hash mismatch')
 if target==part: part.rename(dest)
 results.append({'path':str(dest),'bytes':info['size'],'sha256':h,'verified':True})
 (root/'model-integrity.json').write_text(json.dumps(results,indent=2))
 print('VERIFIED',dest.name,h,flush=True)
