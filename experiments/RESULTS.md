# Local video model comparison

MacBook Pro M4 Pro,24GB unified memory. Conditions per row: battery runs used Low Power Mode, AC runs did not, so times are only comparable within one condition. One prompt (red ball) in rounds 1-3; round 5 adds a second prompt (one blue toy car driving right to left). Three measured seeds42/43/44. Output 49frames,25FPS,1.96s playback, size per row. Cold smoke25frames and warmup excluded from means. Task = exactly one red ball visibly rolls left→right and stays round (visual-task-results.json).

|Model|Weights|Settings|Conditions|Measured runs|Mean s/clip|Memory GiB|Task pass|
|---|---|---|---|---:|---:|---:|---:|
|LTX-Video 2B v0.9.5|BF16|512×320, original prompt|BATTERY|3/3|78.84|8.15|1/3|
|LTX-Video 2B distilled v0.9.6|BF16|512×320, original prompt|BATTERY|3/3|16.55|8.15|0/3|
|Wan 2.1 T2V 1.3B|FP16|512×320, original prompt|BATTERY|3/3|825.73|11.16|0/3|
|LTX-2.3 distilled MLX|MLX 4-bit|512×320, original prompt|AC|3/3|52.67|7.68|1/3|
|Wan 2.2 TI2V 5B|FP16|512×320, original prompt|AC|3/3|274.06|14.94|1/3|
|LTX-Video 2B v0.9.5 (round 2)|BF16|768×512, prompt without "slowly"|AC|3/3|142.91|15.12|0/3|
|LTX-2.3 distilled MLX (round 2)|MLX 4-bit|768×512, prompt without "slowly"|AC|3/3|108.97|9.19|3/3|
|LTX-2.3 distilled MLX (keyframes)|MLX 4-bit|768×512, new prompt, start + end keyframes|AC|3/3|132.22|9.19|9/9|
|LTX-2.3 distilled MLX (blue car)|MLX 4-bit|768×512, blue-car prompt, text only|BATTERY|3/3|109.64|9.19|3/3|
|LTX-2.5 distilled MLX (red ball)|MLX 4-bit|768×512, new red-ball prompt, text only|BATTERY|3/3|175.14|9.19|3/3|
|LTX-2.5 distilled MLX (blue car)|MLX 4-bit|768×512, blue-car prompt, text only|BATTERY|3/3|168.30|9.19|3/3|

Memory counters differ: ComfyUI reports mean per-run1Hz sampled maximum MPS driver allocation; MLX reports the mean of per-run maxima of the sampled MLX peak (cold runs with the Gemma text encoder peak higher, about 14.2 GiB). Neither is total RAM. System swap deltas recorded separately.

Times cover the complete local generation pipeline and output writing, excluding downloads/setup. Warm prompt embeddings cached. Native model residency and output encoders differ. LTX standard30steps/CFG3, LTX distilled8steps/CFG1; Wan official30steps/CFG6 (1.3B) or5 (5B); MLX native8+3step two-stage with spatial2×latent upscale and low-RAM streaming.

See each model folder for source provenance, original and adapted workflows, logs, results.jsonl, output-verification.json, actual movies and visual-assessment.md. Do not infer compatibility merely from runtime installation.

To fit disk, task-created candidate weight caches may be retired after testing. Baseline model/runtime/outputs are retained. Exact retired files and recovery URLs are in retired-candidate-cache.json. To restore a candidate, run its download_ranges.py then its run_server.py (Comfy) or benchmark.py (MLX). Avoid running GPU jobs concurrently.
