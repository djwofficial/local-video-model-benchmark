"""Download the LTX-2.5 MLX int4 files needed for distilled text-to-video (added by Claude, round 5).

Usage: /Users/dyn/AI/venvs/ltx-mlx/bin/python download_ltx25.py
The repo dgrauet/ltx-2.5-mlx-q4 is gated: the user accepts its conditions on Hugging Face and logs in with
`hf auth login` first; huggingface_hub reads that login itself (this script never sees or prints the token).
Only the distilled pipeline's files are fetched (no dev transformer, distilled LoRA, _av VAEs or temporal upscaler).
Writes models-sources.json (Hugging Face file metadata) before downloading and model-integrity.json (SHA-256 of every
LFS file checked against the repo's LFS id) after. Stops if free disk would fall below 5 GiB.
"""
import hashlib,json,shutil,time
from pathlib import Path
from huggingface_hub import HfApi,hf_hub_download

ROOT=Path(__file__).resolve().parent;MODEL=ROOT/'model';REPO='dgrauet/ltx-2.5-mlx-q4'
FILES=['transformer-distilled.safetensors','text_encoder.safetensors','text_encoder_config.json','connector.safetensors',
       'spatial_upscaler_x2_v1_0.safetensors','spatial_upscaler_x2_v1_0_config.json','vae_decoder_conv.safetensors','vae_encoder_conv.safetensors',
       'duration_head.safetensors','audio_vae.safetensors','vocoder.safetensors','tokenizer.json','tokenizer_config.json','chat_template.jinja',
       'processor_config.json','embedded_config.json','generation_config.json','quantize_config.json','split_model.json','LICENSE','README.md']
GiB=2**30

info=HfApi().model_info(REPO,files_metadata=True)
meta={s.rfilename:s for s in info.siblings}
missing=[f for f in FILES if f not in meta];assert not missing,('not in repo',missing)
sources=[{'repo':REPO,'revision':info.sha,'file':f,'kind':'model','size':meta[f].size,
          'sha256':(meta[f].lfs.sha256 if meta[f].lfs else None)} for f in FILES]
(ROOT/'models-sources.json').write_text(json.dumps(sources,indent=2))
MODEL.mkdir(parents=True,exist_ok=True)
todo=[s for s in sources if not ((MODEL/s['file']).exists() and (MODEL/s['file']).stat().st_size==s['size'])]
need=sum(s['size'] for s in todo);free=shutil.disk_usage(ROOT).free
print(f'revision {info.sha}; {len(todo)} files to fetch, {need/GiB:.2f} GiB; free {free/GiB:.2f} GiB',flush=True)
assert free>=need+5*GiB,f'not enough disk: need {need/GiB:.2f} GiB plus 5 GiB reserve, have {free/GiB:.2f} GiB'
for s in todo:
    t=time.time();hf_hub_download(REPO,s['file'],revision=info.sha,local_dir=MODEL)
    print(f"downloaded {s['file']} ({s['size']/GiB:.2f} GiB) in {time.time()-t:.0f} s",flush=True)
checks=[]
for s in sources:
    p=MODEL/s['file'];assert p.stat().st_size==s['size'],(p,p.stat().st_size,s['size'])
    if s['sha256']:
        with p.open('rb') as f: digest=hashlib.file_digest(f,'sha256').hexdigest()
        assert digest==s['sha256'],(p,digest);checks.append({'file':s['file'],'bytes':s['size'],'sha256':digest,'verified':True})
(ROOT/'model-integrity.json').write_text(json.dumps({'repo':REPO,'revision':info.sha,'time':time.time(),'files':checks},indent=2))
print('DOWNLOAD_VERIFIED',len(checks),'LFS files',flush=True)
