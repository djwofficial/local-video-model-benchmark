"""Phase 2 (added by Claude, round 6): Kandinsky 6.0 Lite distill (3B, MIT) text-to-video on MPS from the saved prompt
embeddings: 768x512, 49 frames, frame_rate 24, 10 PiFlow steps, guidance 1.0, no audio, VAE tiling. Warm-up seed 41 (excluded),
then seeds 42-44. Each video's time, sampled peak memory (phys_footprint, MPS driver) and swap change go to results.jsonl.
Runs encode.py first if embeds.pt is missing."""
import os,sys,json,time,threading,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parent
MODEL='/Users/dyn/AI/kandinsky6-lite/model'  # kandinskylab/Kandinsky-6.0-Lite-distill-5s-Diffusers @4c487e8b, audio parts not downloaded
os.environ.update(HF_HUB_OFFLINE='1',TRANSFORMERS_OFFLINE='1',HF_HUB_DISABLE_TELEMETRY='1',DO_NOT_TRACK='1')
sys.path.insert(0,str(ROOT.parent.parent))
import psutil,torch
from claude_memprobe import footprint
POSITIVE='A single bright red ball rolls from the left side to the right side of a wooden table, moving steadily across the whole table until it reaches the right edge. The ball remains round and keeps the same size and color throughout the shot. A plain beige wall is visible in the background. Soft daylight enters from a window on the left. The camera stays completely still, showing the entire table surface in one continuous shot.'
GiB=2**30;samples=[];state={}
def snap(): return {'time':time.time(),'power':subprocess.check_output(['pmset','-g','batt'],text=True).strip(),'swap_bytes':psutil.swap_memory().used,'available_bytes':psutil.virtual_memory().available}
def monitor():
    with (ROOT/'logs/memory-samples.jsonl').open('a',buffering=1) as f:
        while True:
            v=psutil.virtual_memory();row={'time':time.time(),'phase':state.get('phase'),'label':state.get('label'),'phys_footprint_bytes':footprint()[0],
                 'mps_allocated_bytes':torch.mps.current_allocated_memory(),'mps_driver_bytes':torch.mps.driver_allocated_memory(),
                 'available_bytes':v.available,'swap_used_bytes':psutil.swap_memory().used}
            samples.append(row);f.write(json.dumps(row)+'\n')
            if state.get('start') and time.time()-state['start']>3600:
                (ROOT/'logs/safety-stop.json').write_text(json.dumps({'reason':'run exceeded 60 minutes','label':state.get('label')}));os._exit(70)
            time.sleep(1)
threading.Thread(target=monitor,daemon=True).start()
def maxof(key,t0,t1): return max((x[key] for x in samples if t0<=x['time']<=t1),default=0)
import av,numpy as np
if not (ROOT/'embeds.pt').exists():
    assert subprocess.call([sys.executable,'-u',str(ROOT/'encode.py')],stdout=open(ROOT/'logs/encode.log','w'),stderr=subprocess.STDOUT)==0,'encode failed'
E=torch.load(ROOT/'embeds.pt');assert E['prompt']==POSITIVE and (E['mask_is_none'] or E.get('cropped_to_mask'))  # padded tokens removed in encode.py
from diffusers import Kandinsky6TI2VAPipeline
state['phase']='load';t=time.perf_counter()
pipe=Kandinsky6TI2VAPipeline.from_pretrained(MODEL,text_encoder=None,tokenizer=None,text_encoder_2=None,tokenizer_2=None,audio_vae=None,vocoder=None,torch_dtype=torch.bfloat16)
pipe.to('mps')
# Smaller VAE tiles; run 1 showed the decode drives the MPS allocator to ~27 GiB.
pipe.vae.enable_tiling(tile_sample_min_height=192,tile_sample_min_width=192,tile_sample_stride_height=144,tile_sample_stride_width=144);load_s=time.perf_counter()-t;print('loaded in',round(load_s,1),'s',flush=True)
pe=E['prompt_embeds'].to('mps',torch.bfloat16);ppe=E['pooled_prompt_embeds'].to('mps',torch.bfloat16)
def save(frames,path,fps=24):
    arr=(np.clip(frames,0,1)*255).round().astype(np.uint8)
    with av.open(str(path),'w') as c:
        s=c.add_stream('libx264',rate=fps);s.width,s.height=arr.shape[2],arr.shape[1];s.pix_fmt='yuv420p';s.options={'crf':'18'}
        for f in arr:
            for p in s.encode(av.VideoFrame.from_ndarray(f,format='rgb24')): c.mux(p)
        for p in s.encode(): c.mux(p)
for label,seed in [('warmup-49f-seed41',41)]+[(f'benchmark-49f-seed{s}',s) for s in (42,43,44)]:
    state.update(phase='generate',label=label,start=time.time());before=snap();t=time.perf_counter();status,error='success',None;print('START',label,flush=True)
    try:
        # Denoise to latents, release the MPS cache, then decode (same steps as the pipeline's own decode).
        with torch.no_grad():
            lat=pipe(prompt_embeds=pe,pooled_prompt_embeds=ppe,height=512,width=768,num_frames=49,frame_rate=24.0,num_inference_steps=10,guidance_scale=1.0,
                     sample_audio=False,output_type='latent',generator=torch.Generator('cpu').manual_seed(seed)).frames
            torch.mps.synchronize();denoise_s=time.perf_counter()-t;torch.mps.empty_cache();state['phase']='decode'
            video=pipe.vae.decode(lat.to(pipe.vae.dtype)/pipe.vae.config.scaling_factor,return_dict=False)[0]
            frames=pipe.video_processor.postprocess_video(video,output_type='np')
        del lat,video;torch.mps.synchronize();torch.mps.empty_cache();state['phase']='generate'
        save(np.asarray(frames[0]),ROOT/'output'/f'{label}.mp4')
    except Exception as e:
        import traceback;status,error='error',traceback.format_exc();print(error,flush=True)
    el=time.perf_counter()-t;after=snap();state['start']=None
    res={'label':label,'model':'Kandinsky 6.0 Lite distill (Diffusers, MPS, bf16)','round':6,'prompt_key':'redball','prompt':POSITIVE,'status':status,'error':error,'seed':seed,
         'width':768,'height':512,'frames':49,'playback_fps':24,'steps':10,'run':2,'cache_release':True,'vae_tiles':'192/144','guidance':1.0,'elapsed_client_s':round(el,3),'denoise_s':round(denoise_s,3) if status=='success' else None,'load_s':round(load_s,3),
         'phys_footprint_sampled_max_bytes':maxof('phys_footprint_bytes',before['time'],after['time']),'phys_footprint_lifetime_max_bytes':footprint()[1],
         'mps_driver_sampled_max_bytes':maxof('mps_driver_bytes',before['time'],after['time']),'swap_delta_bytes':after['swap_bytes']-before['swap_bytes'],
         'conditions':'AC' if 'AC Power' in before['power'] else 'BATTERY','before':before,'after':after}
    with (ROOT/'results.jsonl').open('a') as f: f.write(json.dumps(res)+'\n')
    print('RESULT',json.dumps({k:v for k,v in res.items() if k not in ('before','after','prompt','error')}),flush=True)
    if status!='success': sys.exit(1)
print('ALL_RUNS_COMPLETED',flush=True)
