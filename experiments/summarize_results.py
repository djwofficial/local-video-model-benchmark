import json,statistics
from pathlib import Path
R=Path(__file__).resolve().parent
R1='512×320, original prompt'
models=[('LTX-Video 2B v0.9.5',R.parent/'ltx-benchmark-2026-10-29','BF16',R1),('LTX-Video 2B distilled v0.9.6',R/'ltx-distilled','BF16',R1),('Wan 2.1 T2V 1.3B',R/'wan21','FP16',R1),('LTX-2.3 distilled MLX',R/'ltx23-mlx','MLX 4-bit',R1),('Wan 2.2 TI2V 5B',R/'wan22','FP16',R1),
        ('LTX-Video 2B v0.9.5 (round 2)',R/'round2/ltx095','BF16','768×512, prompt without "slowly"'),('LTX-2.3 distilled MLX (round 2)',R/'round2/ltx23-mlx','MLX 4-bit','768×512, prompt without "slowly"'),
        ('LTX-2.3 distilled MLX (keyframes)',R/'round3/ltx23-mlx-keyframes','MLX 4-bit','768×512, new prompt, start + end keyframes'),
        # Round 5: second prompt (blue toy car, right to left) and LTX-2.5 distilled MLX int4, text only.
        ('LTX-2.3 distilled MLX (blue car)',R/'round5/ltx23-mlx-bluecar','MLX 4-bit','768×512, blue-car prompt, text only'),
        ('LTX-2.5 distilled MLX (red ball)',R/'round5/ltx25-mlx-redball','MLX 4-bit','768×512, new red-ball prompt, text only'),
        ('LTX-2.5 distilled MLX (blue car)',R/'round5/ltx25-mlx-bluecar','MLX 4-bit','768×512, blue-car prompt, text only')]
def mlx_peak(path,x):
 # The pipeline resets MLX's peak counter at the VAE decode, so take the run's maximum of the 1 Hz samples instead of mlx_peak_active_bytes.
 samples=[json.loads(s) for s in (path/'logs/memory-samples.jsonl').read_text().splitlines() if s.strip()]
 return max(s['mlx_peak_bytes'] for s in samples if x['before']['time']<=s['time']<=x['after']['time'])
summary=[]
for name,path,weights,settings in models:
 rows=[json.loads(s) for s in (path/'results.jsonl').read_text().splitlines() if s.strip()] if (path/'results.jsonl').exists() else []
 runs=[next((x for x in reversed(rows) if x['label']==f'benchmark-49f-seed{seed}' and x['status'] in ['success','finished','execution_success'] and x.get('sampler_executed',True)),None) for seed in [42,43,44]]
 complete=all(runs);runs=[x for x in runs if x]
 row={'model':name,'root':str(path),'weights':weights,'settings':settings,'completed_measured_runs':len(runs),'status':'measured' if complete else 'not fully measured'}
 task=path/'visual-task-results.json'
 if task.exists():t=json.loads(task.read_text());row.update(task_passed=t['passed'],task_evaluated=t['evaluated'])
 if complete:
  mean=statistics.mean(x['elapsed_client_s'] for x in runs);row.update(mean_s_per_clip=mean,generated_frames_per_second=49/mean,run_seconds=[x['elapsed_client_s'] for x in runs],conditions=['AC' if 'AC Power' in x['before']['power'] else 'BATTERY' for x in runs])
  if 'memory' in runs[0]:row.update(memory_gib=statistics.mean(x['memory']['sampled_max_mps_driver_bytes'] for x in runs)/1024**3,memory_metric='Mean of per-run 1 Hz sampled maxima of MPS driver allocation; not total RAM or a true peak')
  else:row.update(memory_gib=statistics.mean(mlx_peak(path,x) for x in runs)/1024**3,memory_metric='Mean of per-run maxima of the 1 Hz sampled MLX peak (whole run); differs from MPS driver counter')
  row['swap_delta_gib']=[x['swap_delta_bytes']/1024**3 for x in runs]
 errors=[x for x in rows if x['status'] not in ['success','finished','execution_success']]
 if errors:row['observed_failed_runs']=[{'label':x['label'],'status':x['status'],'error':x.get('error') or x.get('server_status')} for x in errors]
 summary.append(row)
(R/'comparison-results.json').write_text(json.dumps(summary,indent=2));print(json.dumps(summary,indent=2))

lines=['# Local video model comparison','', 'MacBook Pro M4 Pro,24GB unified memory. Conditions per row: battery runs used Low Power Mode, AC runs did not, so times are only comparable within one condition. One prompt (red ball) in rounds 1-3; round 5 adds a second prompt (one blue toy car driving right to left). Three measured seeds42/43/44. Output 49frames,25FPS,1.96s playback, size per row. Cold smoke25frames and warmup excluded from means. Task = exactly one red ball visibly rolls left→right and stays round (visual-task-results.json).','', '|Model|Weights|Settings|Conditions|Measured runs|Mean s/clip|Memory GiB|Task pass|','|---|---|---|---|---:|---:|---:|---:|']
for x in summary:
 lines.append('|'+x['model']+'|'+x['weights']+'|'+x['settings']+'|'+('/'.join(sorted(set(x['conditions']))) if 'conditions' in x else '—')+'|'+str(x['completed_measured_runs'])+'/3|'+(f"{x['mean_s_per_clip']:.2f}" if 'mean_s_per_clip' in x else 'Pending / incomplete')+'|'+(f"{x['memory_gib']:.2f}" if 'memory_gib' in x else '—')+'|'+(f"{x['task_passed']}/{x['task_evaluated']}" if 'task_passed' in x else '—')+'|')
lines+=['','Memory counters differ: ComfyUI reports mean per-run1Hz sampled maximum MPS driver allocation; MLX reports the mean of per-run maxima of the sampled MLX peak (cold runs with the Gemma text encoder peak higher, about 14.2 GiB). Neither is total RAM. System swap deltas recorded separately.','', 'Times cover the complete local generation pipeline and output writing, excluding downloads/setup. Warm prompt embeddings cached. Native model residency and output encoders differ. LTX standard30steps/CFG3, LTX distilled8steps/CFG1; Wan official30steps/CFG6 (1.3B) or5 (5B); MLX native8+3step two-stage with spatial2×latent upscale and low-RAM streaming.','', 'See each model folder for source provenance, original and adapted workflows, logs, results.jsonl, output-verification.json, actual movies and visual-assessment.md. Do not infer compatibility merely from runtime installation.','', 'To fit disk, task-created candidate weight caches may be retired after testing. Baseline model/runtime/outputs are retained. Exact retired files and recovery URLs are in retired-candidate-cache.json. To restore a candidate, run its download_ranges.py then its run_server.py (Comfy) or benchmark.py (MLX). Avoid running GPU jobs concurrently.']
(R/'RESULTS.md').write_text('\n'.join(lines)+'\n')
