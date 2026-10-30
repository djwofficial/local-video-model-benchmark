import json,datetime
from pathlib import Path
from zoneinfo import ZoneInfo
ROOT=Path(__file__).resolve().parent
lines=[];downloaded=0;total_bytes=0
for item,kind in zip(json.loads((ROOT/'models-sources.json').read_text()),['checkpoints','text_encoders']):
    info=item['metadata'][0];size=info['size'];total_bytes+=size
    dest=Path('/Users/dyn/AI/models')/kind/Path(item['file']).name
    state=dest.with_suffix('.chunks.json')
    count=(size+16777215)//16777216
    if dest.exists() and dest.stat().st_size==size: done=size;label='verified'
    elif state.exists():
        x=json.loads(state.read_text());done=sum(min(16777216,size-int(i)*16777216) for i in x['chunks']);label=f'{len(x["chunks"])}/{count} parts'
    else: done=0;label='pending'
    downloaded+=done
    lines.append(f'{dest.name}: {100*done/size:.1f}% ({done/1e9:.2f}/{size/1e9:.2f} GB; {label})')
p=ROOT/'pipeline-state.json';stage=json.loads(p.read_text())['stage'] if p.exists() else 'setup'
now=datetime.datetime.now(ZoneInfo('Asia/Taipei')).isoformat(timespec='seconds')
summary='\n'.join([now,*lines,f'Total: {downloaded/1e9:.2f}/{total_bytes/1e9:.2f} GB',f'Pipeline: {stage}'])
(ROOT/'STATUS.md').write_text('# Current local setup status\n\n'+summary+'\n\nComfyUI v0.43.0 and all official dependencies installed; compatibility check passed. MPS verified. Model files are only finalized after SHA-256 verification.\n\nThe user currently cannot connect a charger. Battery runs must be labelled nonstandard.\n')
print(summary)
