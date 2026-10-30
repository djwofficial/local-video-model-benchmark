import os,sys,json,time,threading,subprocess,traceback,ipaddress
from pathlib import Path
ROOT=Path(__file__).resolve().parent
MODEL_ROOT=ROOT.parent.parent/'ltx25-mlx'  # LTX-2.5 MLX int4 distilled files (ltx25-mlx/download_ltx25.py)
os.environ.update(HF_HUB_OFFLINE='1',TRANSFORMERS_OFFLINE='1',HF_HUB_DISABLE_TELEMETRY='1',DO_NOT_TRACK='1')
os.environ['PATH']='/Users/dyn/AI/venvs/ltx-mlx/bin:'+os.environ['PATH']
def audit(event,args):
 if event not in ('socket.connect','socket.getaddrinfo'):return
 address=args[1] if event=='socket.connect' else (args[0],args[1])
 if not isinstance(address,tuple):return
 host=address[0]
 try:local=host in ('localhost',None,'') or ipaddress.ip_address(host).is_loopback
 except ValueError:local=False
 if not local:raise OSError('Offline benchmark blocks outbound network access: '+str(host))
sys.addaudithook(audit)
import psutil,mlx.core as mx
sys.path.insert(0,str(ROOT.parent.parent))
from claude_memprobe import footprint
from ltx_pipelines_mlx.distilled import DistilledPipeline
POSITIVE='A small blue toy car drives from the right side to the left side of a white desk, moving steadily across the whole desk until it reaches the left edge. The car keeps the same shape, size and color throughout the shot. A plain light-grey wall is visible in the background. Soft daylight comes from above. The camera stays completely still, showing the entire desk surface in one continuous shot.'
proc=psutil.Process();run_state={};samples=[]
def snap():return {'time':time.time(),'power':subprocess.check_output(['pmset','-g','batt'],text=True).strip(),'swap_bytes':psutil.swap_memory().used,'available_bytes':psutil.virtual_memory().available,'free_disk_bytes':psutil.disk_usage(ROOT).free}
def monitor():
 low=0
 with (ROOT/'logs/memory-samples.jsonl').open('a',buffering=1) as f:
  while True:
   v=psutil.virtual_memory();s=psutil.swap_memory();row={'time':time.time(),'rss_bytes':proc.memory_info().rss,'mlx_active_bytes':mx.get_active_memory(),'mlx_peak_bytes':mx.get_peak_memory(),'phys_footprint_bytes':footprint()[0],'mlx_cache_bytes':mx.get_cache_memory(),'system_available_bytes':v.available,'system_swap_used_bytes':s.used,'label':run_state.get('label')};samples.append(row);f.write(json.dumps(row)+'\n')
   if run_state.get('start'):
    low=low+1 if v.available<512*1024**2 and s.used-run_state['swap_start']>2*1024**3 else 0
    reason='sustained low available memory and swap growth' if low>=10 else 'run exceeded 60 minutes' if time.time()-run_state['start']>3600 else 'free disk below 4 GiB' if psutil.disk_usage(ROOT).free<4*1024**3 else None
    if reason:
     (ROOT/'logs/safety-stop.json').write_text(json.dumps({'time':time.time(),'reason':reason,'label':run_state['label']}));os._exit(70)
   time.sleep(1)
threading.Thread(target=monitor,daemon=True).start()
class BenchmarkDistilled(DistilledPipeline):
 def _load_text_encoder(self):
  if not getattr(self,'_benchmark_prompt_cache',None):super()._load_text_encoder()
 def _encode_text(self,prompt):
  cache=getattr(self,'_benchmark_prompt_cache',None)
  if cache and cache[0]==prompt:return cache[1]
  value=super()._encode_text(prompt);mx.eval(*value);self._benchmark_prompt_cache=(prompt,value);return value
pipe=BenchmarkDistilled(model_dir=str(MODEL_ROOT/'model'),low_memory=True,low_ram_streaming=True)  # the 2.5 pack carries its own Gemma-4 text encoder
pipe.generate_audio=False
# Use native defaults: distilled 8-step half resolution + 3-step upscale/refine.
# Cache the repeated prompt embeddings after the cold smoke, matching ComfyUI warm runs.
# Round 5 (added by Claude): LTX-2.5 distilled MLX int4 with round-2 settings and the second prompt (blue toy car, right to left), text only.
# The pack is detected as LTX-2.5 (ancestral Euler, 2.5 sigmas). Warm-up seed 41 absorbs the cold start; seeds 42-44 are measured.
for label,seed,frames in [('warmup-49f-seed41',41,49)]+[(f'benchmark-49f-seed{s}',s,49) for s in (42,43,44)]:
 before=snap();mx.reset_peak_memory();start=time.perf_counter();run_state.update(label=label,start=time.time(),swap_start=before['swap_bytes']);status='success';error=None
 print('START',label,flush=True)
 try:pipe.generate_and_save(prompt=POSITIVE,output_path=str(ROOT/'output'/f'{label}.mp4'),width=768,height=512,num_frames=frames,frame_rate=25,seed=seed)
 except Exception:status='error';error=traceback.format_exc();print(error,flush=True)
 elapsed=time.perf_counter()-start;after=snap();run_state.clear();rows=[x for x in samples if before['time']<=x['time']<=after['time']]
 result={'label':label,'model':'LTX-2.5 distilled MLX 4-bit','round':5,'prompt_key':'bluecar','prompt':POSITIVE,'status':status,'error':error,'seed':seed,'width':768,'height':512,'frames':frames,'playback_fps':25,'elapsed_client_s':round(elapsed,3),'before':before,'after':after,'mlx_peak_active_bytes':mx.get_peak_memory(),'mlx_peak_sampled_max_bytes':max((x['mlx_peak_bytes'] for x in rows),default=0),'phys_footprint_sampled_max_bytes':max((x['phys_footprint_bytes'] for x in rows),default=0),'phys_footprint_lifetime_max_bytes':footprint()[1],'conditions':'AC' if 'AC Power' in before['power'] else 'BATTERY','sampled_max_rss_bytes':max((x['rss_bytes'] for x in rows),default=0),'swap_delta_bytes':after['swap_bytes']-before['swap_bytes'],'low_ram_streaming':True,'audio':False,'pipeline':'DistilledPipeline (LTX-2.5 pack, ancestral Euler) two-stage:384x256 8steps +2x spatial upscale +768x512 3steps','timing_scope':'Native pipeline generation through MP4 saving; includes uncached text encoding and native model load/free lifecycle. Warm runs reuse cached prompt embeddings, matching ComfyUI prompt caching; model residency differs by runtime. Setup and downloads excluded.'}
 (ROOT/'logs'/f'{label}-result.json').write_text(json.dumps(result,indent=2))
 with (ROOT/'results.jsonl').open('a') as f:f.write(json.dumps(result)+'\n')
 print('RESULT',json.dumps(result),flush=True)
 if status!='success':sys.exit(1)
print('ALL_RUNS_COMPLETED',flush=True)
