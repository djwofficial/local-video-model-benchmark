"""Battery guard for serial candidate tests (added by Claude at handoff).

Usage: python claude_battery_guard.py <watched_pid> [stop_percent]
Polls pmset every 30 s while the watched controller PID is alive and logs each
reading to logs/battery-guard.jsonl. On battery power at or below stop_percent it
asks the loopback ComfyUI server to interrupt the current job (benchmark.py then
records an execution_interrupted result and continue_tests.py stops the server) and
terminates a running LTX-2.3 MLX benchmark.py, which has no interrupt endpoint.
This repeats every poll, so a job started between polls is also stopped. Downloads
are left running. It never changes power settings and only contacts 127.0.0.1.
"""
import json,os,re,subprocess,sys,time,urllib.request
from pathlib import Path
R=Path(__file__).resolve().parent
pid=int(sys.argv[1]);stop=int(sys.argv[2]) if len(sys.argv)>2 else 15
log=R/'logs/battery-guard.jsonl'
def alive(p):
    try: os.kill(p,0); return True
    except OSError: return False
while alive(pid):
    out=subprocess.check_output(['pmset','-g','batt'],text=True)
    m=re.search(r'(\d+)%;\s*([^;]+);',out)
    pct=int(m.group(1)) if m else None
    row={'time':time.time(),'percent':pct,'state':m.group(2) if m else None,'battery_power':"'Battery Power'" in out,'watched_pid':pid,'stop_percent':stop}
    if row['battery_power'] and pct is not None and pct<=stop:
        actions=[]
        try:
            with urllib.request.urlopen(urllib.request.Request('http://127.0.0.1:8188/interrupt',method='POST'),timeout=5) as r: r.read()
            actions.append('comfy_interrupt_requested')
        except OSError as e: actions.append('comfy_not_interrupted: '+str(e))
        if subprocess.run(['pkill','-TERM','-f','ltx23-mlx/benchmark.py']).returncode==0: actions.append('mlx_benchmark_terminated')
        row['action']=actions
    with log.open('a') as f: f.write(json.dumps(row)+'\n')
    time.sleep(30)
