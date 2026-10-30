"""Retire the task-downloaded LTX-2.3 MLX weights to make room for LTX-2.5 (added by Claude, user-approved 30 Oct 2026).

Usage: python claude_retire_mlx_weights.py
Deletes only the weight files listed in ltx23-mlx/models-sources.json (transformer, connector, upscaler, VAEs, Gemma 3
shards) after checking each file's size and SHA-256 against that manifest, and records path, size, SHA-256, recovery URL
and reason in retired-candidate-cache.json. Small config and tokenizer files, outputs, logs and manifests stay.
Refuses to run while a benchmark is running or before the round-5 LTX-2.3 comparison run has completed.
"""
import hashlib,json,subprocess,time
from pathlib import Path
R=Path(__file__).resolve().parent
M=R/'ltx23-mlx'
assert subprocess.run(['pgrep','-f',r'/benchmark\.py'],capture_output=True).returncode!=0,'a benchmark is still running'
state=json.loads((R/'round5/ltx23-mlx-bluecar/pipeline-state.json').read_text())['stage']
assert state=='complete_pending_visual_review',('round-5 LTX-2.3 comparison not complete',state)
record=json.loads((R/'retired-candidate-cache.json').read_text())
for item in json.loads((M/'models-sources.json').read_text()):
    info=item['metadata'][0];dest=M/item['kind']/Path(item['file']).name
    if not dest.exists(): print('Already absent:',dest,flush=True);continue
    assert dest.stat().st_size==info['size'],(dest,dest.stat().st_size,info['size'])
    with dest.open('rb') as f: digest=hashlib.file_digest(f,'sha256').hexdigest()
    assert digest==info['lfs']['oid'],(dest,digest)
    record.append({'path':str(dest),'bytes':info['size'],'sha256':digest,'recovery_url':f"https://huggingface.co/{item['repo']}/resolve/main/{item['file']}",
                   'reason':'task-created LTX-2.3 MLX weights retired with user approval to fit the LTX-2.5 MLX q4 download (round 5)','time':time.time()})
    (R/'retired-candidate-cache.json').write_text(json.dumps(record,indent=2))
    dest.unlink();print('Retired:',dest,f"{info['size']/2**30:.2f} GiB",flush=True)
print('RETIRE_COMPLETED',flush=True)
