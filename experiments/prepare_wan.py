import json,shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parent
source=ROOT/'ltx-distilled'
all_models=json.loads((ROOT/'sources/wan-models-sources.json').read_text())
for version,name,cfg,latent in [('21','Wan 2.1 T2V 1.3B',6,40),('22','Wan 2.2 TI2V 5B',5,55)]:
 r=ROOT/('wan'+version);r.mkdir(exist_ok=True)
 for d in ['logs','workflows','output']:(r/d).mkdir(exist_ok=True)
 for fn in ['run_server.py','verify_outputs.py']:shutil.copy2(source/fn,r/fn)
 (r/'extra_model_paths.yaml').write_text('local_ai:\n  base_path: /Users/dyn/AI/models\n  checkpoints: checkpoints\n  text_encoders: text_encoders\n  diffusion_models: diffusion_models\n  vae: vae\n')
 shutil.copy2(ROOT/f'sources/wan{version}-workflow.json',r/'workflows/official-original.json')
 model='wan2.1_t2v_1.3B_fp16.safetensors' if version=='21' else 'wan2.2_ti2v_5B_fp16.safetensors'
 vae='wan_2.1_vae.safetensors' if version=='21' else 'wan2.2_vae.safetensors'
 sources=[x for x in all_models if Path(x['file']).name in [model,vae,'umt5_xxl_fp8_e4m3fn_scaled.safetensors']]
 (r/'models-sources.json').write_text(json.dumps(sources,indent=2))
 text=(ROOT/'download_ranges.py').read_text().replace("for item,kind in zip(json.loads((ROOT/'models-sources.json').read_text()),['checkpoints','text_encoders']):","for item in json.loads((ROOT/'models-sources.json').read_text()):\n    kind=item['kind']")
 (r/'download_ranges.py').write_text(text)
 text=(source/'benchmark.py').read_text();a=text.index('def graphs(');b=text.index('\ndef snapshot():')
 graph='''def graphs(seed,frames,label,clip_device):
    w=copy.deepcopy(ORIGINAL)
    values={6:[POSITIVE],38:['umt5_xxl_fp8_e4m3fn_scaled.safetensors','wan',clip_device],LATENT:[512,320,frames,1],3:[seed,'fixed',30,CFG,'uni_pc','simple',1],28:[label,25,False,95,'default'],47:[label,'vp9',25,18]}
    for n in w['nodes']:
        if n['id'] in values:n['widgets_values']=values[n['id']]
        if n['id']==47:n['mode']=0
    p={}
    def node(i,t,**inputs):p[str(i)]={'class_type':t,'inputs':inputs}
    node(37,'UNETLoader',unet_name=MODEL,weight_dtype='default')
    node(38,'CLIPLoader',clip_name='umt5_xxl_fp8_e4m3fn_scaled.safetensors',type='wan',device=clip_device)
    node(39,'VAELoader',vae_name=VAE)
    node(6,'CLIPTextEncode',clip=['38',0],text=POSITIVE)
    node(7,'CLIPTextEncode',clip=['38',0],text=NEGATIVE)
    if LATENT==40:node(40,'EmptyHunyuanLatentVideo',width=512,height=320,length=frames,batch_size=1)
    else:node(55,'Wan22ImageToVideoLatent',vae=['39',0],width=512,height=320,length=frames,batch_size=1)
    node(48,'ModelSamplingSD3',model=['37',0],shift=8.0)
    node(3,'KSampler',model=['48',0],seed=seed,steps=30,cfg=CFG,sampler_name='uni_pc',scheduler='simple',positive=['6',0],negative=['7',0],latent_image=[str(LATENT),0],denoise=1.0)
    node(8,'VAEDecode',samples=['3',0],vae=['39',0])
    node(28,'SaveAnimatedWEBP',images=['8',0],filename_prefix=label,fps=25.0,lossless=False,quality=95,method='default')
    node(47,'SaveWEBM',images=['8',0],filename_prefix=label,codec='vp9',fps=25.0,crf=18.0)
    return w,p
'''.replace('MODEL',repr(model)).replace('VAE)',repr(vae)+')').replace('LATENT',str(latent)).replace('CFG',str(cfg))
 # Preserve VAEDecode class text; replace only VAE variable left in loader.
 graph=graph.replace('vae_name=VAE','vae_name='+repr(vae))
 text=text[:a]+graph+text[b:]
 text=text.replace("'model':'LTX-Video 2B distilled v0.9.6'", "'model':"+repr(name)).replace("'steps':8,'guidance':1,'sampler':'euler_ancestral'",f"'steps':30,'guidance':{cfg},'sampler':'uni_pc'").replace("get('node'))=='72'","get('node'))=='3'")
 compile(text,str(r/'benchmark.py'),'exec');(r/'benchmark.py').write_text(text)
 (r/'PROVENANCE.md').write_text(f'# {name}\n\nOfficial ComfyUI example: https://comfyanonymous.github.io/ComfyUI_examples/wan'+('22' if version=='22' else '')+'/\n\nAdapted only prompt, seed, resolution 512×320, frames25/49, output25FPS and output encoding quality to benchmark. Official sampling retained:30steps, CFG'+str(cfg)+', uni_pc, simple scheduler, model sampling shift8. Text encoder FP8 scaled, diffusion FP16. Original workflow saved. All are text-to-video; no start image supplied.\n')
 print(r)
