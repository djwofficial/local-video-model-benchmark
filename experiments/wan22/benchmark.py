import argparse,asyncio,copy,csv,json,subprocess,time,uuid
from pathlib import Path
import aiohttp,psutil
ROOT=Path(__file__).resolve().parent
URL='http://127.0.0.1:8188'
POSITIVE='A single bright red ball rolls slowly from the left side to the right side of a wooden table. The ball remains round and keeps the same size and color throughout the shot. A plain beige wall is visible in the background. Soft daylight enters from a window on the left. The camera stays completely still, showing the entire table surface in one continuous shot.'
ORIGINAL=json.loads((ROOT/'workflows/official-original.json').read_text())
NEGATIVE=next(n['widgets_values'][0] for n in ORIGINAL['nodes'] if n['id']==7)

def graphs(seed,frames,label,clip_device):
    w=copy.deepcopy(ORIGINAL)
    values={6:[POSITIVE],38:['umt5_xxl_fp8_e4m3fn_scaled.safetensors','wan',clip_device],55:[512,320,frames,1],3:[seed,'fixed',30,5,'uni_pc','simple',1],28:[label,25,False,95,'default'],47:[label,'vp9',25,18]}
    for n in w['nodes']:
        if n['id'] in values:n['widgets_values']=values[n['id']]
        if n['id']==47:n['mode']=0
    p={}
    def node(i,t,**inputs):p[str(i)]={'class_type':t,'inputs':inputs}
    node(37,'UNETLoader',unet_name='wan2.2_ti2v_5B_fp16.safetensors',weight_dtype='default')
    node(38,'CLIPLoader',clip_name='umt5_xxl_fp8_e4m3fn_scaled.safetensors',type='wan',device=clip_device)
    node(39,'VAELoader',vae_name='wan2.2_vae.safetensors')
    node(6,'CLIPTextEncode',clip=['38',0],text=POSITIVE)
    node(7,'CLIPTextEncode',clip=['38',0],text=NEGATIVE)
    if 55==40:node(40,'EmptyHunyuanLatentVideo',width=512,height=320,length=frames,batch_size=1)
    else:node(55,'Wan22ImageToVideoLatent',vae=['39',0],width=512,height=320,length=frames,batch_size=1)
    node(48,'ModelSamplingSD3',model=['37',0],shift=8.0)
    node(3,'KSampler',model=['48',0],seed=seed,steps=30,cfg=5,sampler_name='uni_pc',scheduler='simple',positive=['6',0],negative=['7',0],latent_image=[str(55),0],denoise=1.0)
    node(8,'VAEDecode',samples=['3',0],vae=['39',0])
    node(28,'SaveAnimatedWEBP',images=['8',0],filename_prefix=label,fps=25.0,lossless=False,quality=95,method='default')
    node(47,'SaveWEBM',images=['8',0],filename_prefix=label,codec='vp9',fps=25.0,crf=18.0)
    return w,p

def snapshot():
    return {'time':time.time(),'power':subprocess.check_output(['pmset','-g','batt'],text=True).strip(),'power_settings':subprocess.check_output(['pmset','-g','custom'],text=True).strip(),'swap':subprocess.check_output(['sysctl','vm.swapusage'],text=True).strip(),'swap_bytes':psutil.swap_memory().used,'memory_pressure':subprocess.check_output(['memory_pressure','-Q'],text=True).strip()}

def memory_summary(start,end):
    samples=[]
    path=ROOT/'logs/memory-samples.jsonl'
    if path.exists():
        for line in path.read_text().splitlines():
            try: row=json.loads(line)
            except json.JSONDecodeError: continue
            if start<=row['time']<=end: samples.append(row)
    keys=['rss_bytes','mps_allocated_bytes','mps_driver_bytes','system_swap_used_bytes']
    return {'method':'1 Hz samples in ComfyUI server process; sampled maxima, not true allocator peaks. RSS and MPS counters overlap; do not add them.', 'sample_count':len(samples), **{f'sampled_max_{k}':max((r.get(k,0) for r in samples),default=None) for k in keys}}

async def run(label,seed,frames,clip_device):
    workflow,prompt=graphs(seed,frames,label,clip_device)
    (ROOT/f'workflows/{label}.json').write_text(json.dumps(workflow,indent=2))
    (ROOT/f'workflows/{label}-api.json').write_text(json.dumps(prompt,indent=2))
    before=snapshot(); start=time.perf_counter(); cid=str(uuid.uuid4()); events=[]; status='unknown'; cached=[]
    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=None)) as session:
        async with session.get(URL+'/queue') as response:
            queue=await response.json()
        if queue.get('queue_running') or queue.get('queue_pending'): raise RuntimeError('Another job is already queued; refusing parallel generation')
        async with session.ws_connect(URL+'/ws',params={'clientId':cid},max_msg_size=32*1024*1024) as ws:
            async with session.post(URL+'/prompt',json={'prompt':prompt,'client_id':cid,'extra_data':{'extra_pnginfo':{'workflow':workflow}}}) as response:
                submitted=await response.json()
                if response.status!=200:
                    (ROOT/f'logs/{label}-validation.json').write_text(json.dumps(submitted,indent=2)); raise RuntimeError(submitted)
            pid=submitted['prompt_id']; print('QUEUED',label,pid,flush=True)
            low_memory_count=0; last_print=0
            with (ROOT/f'logs/{label}-events.jsonl').open('w',buffering=1) as f:
                while True:
                    try: msg=await ws.receive(timeout=5)
                    except asyncio.TimeoutError:
                        available=psutil.virtual_memory().available
                        low_memory_count=low_memory_count+1 if available<512*1024**2 and psutil.swap_memory().used-before['swap_bytes']>2*1024**3 else 0
                        if low_memory_count>=2:
                            async with session.post(URL+'/interrupt') as response: await response.read()
                            print('INTERRUPTED due to sustained low available memory and swap growth',flush=True)
                        if time.perf_counter()-start>1800:
                            async with session.post(URL+'/interrupt') as response: await response.read()
                            raise TimeoutError('Generation exceeded 30 minutes; interrupt requested')
                        continue
                    if msg.type in (aiohttp.WSMsgType.CLOSED,aiohttp.WSMsgType.ERROR): raise ConnectionError('ComfyUI websocket closed')
                    if msg.type!=aiohttp.WSMsgType.TEXT: continue
                    item=json.loads(msg.data); data=item.get('data',{}); typ=item.get('type')
                    if data.get('prompt_id') not in (None,pid): continue
                    event={'received_time':time.time(),'elapsed_s':time.perf_counter()-start,**item};events.append(event); f.write(json.dumps(event)+'\n')
                    if typ=='execution_cached': cached=data.get('nodes',[])
                    if typ=='executing' and data.get('node'): print(label,'node',data['node'],prompt.get(str(data['node']),{}).get('class_type'),flush=True)
                    if typ=='progress' and time.time()-last_print>10:
                        print(label,'sampling',data.get('value'),'/',data.get('max'),flush=True);last_print=time.time()
                    if typ in ('execution_success','execution_error','execution_interrupted'):
                        status=typ;break
                    if typ=='executing' and data.get('node') is None: status='finished';break
            elapsed=time.perf_counter()-start
            for _ in range(30):
                async with session.get(URL+'/history/'+pid) as response: history=await response.json()
                if pid in history: break
                await asyncio.sleep(0.1)
    after=snapshot();(ROOT/f'logs/{label}-history.json').write_text(json.dumps(history,indent=2))
    h=history.get(pid,{})
    result={'label':label,'model':'Wan 2.2 TI2V 5B','seed':seed,'width':512,'height':320,'frames':frames,'playback_fps':25,'steps':30,'guidance':5,'sampler':'uni_pc','clip_device':clip_device,'status':status,'elapsed_client_s':round(elapsed,3),'generated_frames_per_second':round(frames/elapsed,4),'cached_nodes':cached,'sampler_executed':any(e.get('type')=='executing' and str(e.get('data',{}).get('node'))=='3' for e in events),'prompt_id':pid,'before':before,'after':after,'swap_delta_bytes':after['swap_bytes']-before['swap_bytes'],'memory':memory_summary(before['time'],after['time']),'server_status':h.get('status'),'outputs':h.get('outputs'),'conditions':'AC' if 'AC Power' in before['power'] else 'BATTERY — nonstandard; not the AC benchmark requested in handoff','timing_scope':'Client submit to execution success; includes uncached nodes, sampler, VAE decode, WebP and WebM output writing. Warm runs cache prompt encodings; model residency uses ComfyUI defaults. Downloads/setup excluded.'}
    (ROOT/f'logs/{label}-result.json').write_text(json.dumps(result,indent=2))
    with (ROOT/'results.jsonl').open('a') as f: f.write(json.dumps(result)+'\n')
    print('RESULT',json.dumps(result),flush=True)
    if status not in ('finished','execution_success') or not result['sampler_executed']: raise RuntimeError('Run failed or sampler was cached; inspect logs')
    return result

async def main():
    ap=argparse.ArgumentParser();ap.add_argument('mode',choices=['smoke','bench']);ap.add_argument('--clip-device',choices=['default','cpu'],default='default');a=ap.parse_args()
    async with aiohttp.ClientSession() as session:
        async with session.get(URL+'/object_info') as response: schema=await response.json()
        async with session.get(URL+'/system_stats') as response: stats=await response.json()
    (ROOT/'object_info.json').write_text(json.dumps(schema));(ROOT/'runtime-stats.json').write_text(json.dumps(stats,indent=2))
    w,p=graphs(41,25,'smoke',a.clip_device)
    for n in p.values():
        if n['class_type'] not in schema: raise RuntimeError('Missing node '+n['class_type'])
    if a.mode=='smoke': await run('smoke-25f-seed41'+('-cpu-encoder' if a.clip_device=='cpu' else ''),41,25,a.clip_device)
    else:
        await run('warmup-49f-seed41',41,49,a.clip_device)
        for seed in (42,43,44): await run(f'benchmark-49f-seed{seed}',seed,49,a.clip_device)

if __name__=='__main__': asyncio.run(main())
