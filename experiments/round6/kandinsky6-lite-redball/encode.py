"""Phase 1 (added by Claude, round 6): read the prompt with Kandinsky 6.0 Lite's text encoders (Qwen2.5-VL-7B + CLIP)
on MPS, save the embeddings to embeds.pt and exit, so the 16.6 GB text encoder is never in memory with the video model."""
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
from diffusers import Kandinsky6TI2VAPipeline
state['phase']='encode';before=snap();t=time.perf_counter()
pipe=Kandinsky6TI2VAPipeline.from_pretrained(MODEL,transformer=None,vae=None,audio_vae=None,vocoder=None,torch_dtype=torch.bfloat16)
pipe.text_encoder.to('mps');pipe.text_encoder_2.to('mps');load=time.perf_counter()-t
t2=time.perf_counter()
with torch.no_grad():
    out=pipe.encode_prompt(POSITIVE,do_classifier_free_guidance=False,device=torch.device('mps'),dtype=torch.bfloat16)
torch.mps.synchronize();enc=time.perf_counter()-t2
pe,ppe,mask=out[0],out[1],out[2]
# The pipeline pads the Qwen tokens to max_sequence_length and passes the mask to the transformer, but __call__ takes no
# mask with prompt_embeds; with right padding, keeping only the real tokens is equivalent, so crop to them.
cropped=False
if mask is not None:
    m=mask[0].bool().cpu();n=int(m.sum());assert bool(m[:n].all()) and not bool(m[n:].any()),'padding is not on the right'
    pe=pe[:,:n].contiguous();cropped=True
torch.save({'prompt':POSITIVE,'prompt_embeds':pe.cpu(),'pooled_prompt_embeds':ppe.cpu(),'mask_is_none':mask is None,'cropped_to_mask':cropped,'valid_tokens':int(pe.shape[1])},ROOT/'embeds.pt')
after=snap()
res={'label':'encode','status':'success','load_s':round(load,3),'encode_s':round(enc,3),'total_s':round(time.perf_counter()-t,3),'mask_is_none':mask is None,
     'embeds_shape':list(pe.shape),'phys_footprint_lifetime_max_bytes':footprint()[1],'phys_footprint_sampled_max_bytes':maxof('phys_footprint_bytes',before['time'],after['time']),
     'mps_driver_sampled_max_bytes':maxof('mps_driver_bytes',before['time'],after['time']),'swap_delta_bytes':after['swap_bytes']-before['swap_bytes'],'before':before,'after':after}
(ROOT/'logs/encode-result.json').write_text(json.dumps(res,indent=2));print('RESULT',json.dumps({k:v for k,v in res.items() if k not in ('before','after')}),flush=True)
print('ENCODE_COMPLETED',flush=True)
