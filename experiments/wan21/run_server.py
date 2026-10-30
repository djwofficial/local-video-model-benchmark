import os,sys,time,json,threading,runpy,ipaddress
from pathlib import Path
ROOT=Path(__file__).resolve().parent
os.environ.update(HF_HUB_OFFLINE='1',TRANSFORMERS_OFFLINE='1',HF_HUB_DISABLE_TELEMETRY='1',DO_NOT_TRACK='1')

def audit(event,args):
    if event not in ('socket.connect','socket.getaddrinfo'): return
    address=args[1] if event=='socket.connect' else (args[0],args[1])
    if not isinstance(address,tuple): return
    host=address[0]
    if host in ('localhost',None,''): return
    try: local=ipaddress.ip_address(host).is_loopback
    except ValueError: local=False
    if not local:
        with (ROOT/'logs/network-blocks.jsonl').open('a') as f:
            f.write(json.dumps({'time':time.time(),'event':event,'host':host})+'\n')
        raise OSError('Offline benchmark blocks non-loopback network access')

sys.addaudithook(audit)
import psutil
proc=psutil.Process()

def monitor():
    with (ROOT/'logs/memory-samples.jsonl').open('a',buffering=1) as f:
        while True:
            v=psutil.virtual_memory(); s=psutil.swap_memory()
            row={'time':time.time(),'pid':os.getpid(),'rss_bytes':proc.memory_info().rss,'system_available_bytes':v.available,'system_swap_used_bytes':s.used}
            torch=sys.modules.get('torch')
            manager=sys.modules.get('comfy.model_management')
            if manager is not None and hasattr(manager,'is_device_mps') and torch.backends.mps.is_available():
                row.update(mps_allocated_bytes=torch.mps.current_allocated_memory(),mps_driver_bytes=torch.mps.driver_allocated_memory(),mps_recommended_max_bytes=torch.mps.recommended_max_memory())
            f.write(json.dumps(row)+'\n')
            time.sleep(1)

threading.Thread(target=monitor,daemon=True).start()
(ROOT/'server.pid').write_text(str(os.getpid()))
source=Path('/Users/dyn/AI/ComfyUI')
os.chdir(source);sys.path.insert(0,str(source))
sys.argv=[str(source/'main.py'),'--listen','127.0.0.1','--port','8188','--offline','--disable-all-custom-nodes','--cache-classic','--extra-model-paths-config',str(ROOT/'extra_model_paths.yaml'),'--output-directory',str(ROOT/'output')]
print('Local benchmark arguments:',sys.argv,flush=True)
print('Python outbound network blocked except loopback; MPS memory safety defaults preserved.',flush=True)
runpy.run_path(str(source/'main.py'),run_name='__main__')
