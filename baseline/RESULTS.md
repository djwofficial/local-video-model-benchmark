# LTX-Video 2B v0.9.5 — actual local results

Device: MacBook Pro M4 Pro, 16-core GPU, 24 GB unified memory; macOS 27.0.1.

Runtime: ComfyUI 0.43.0; PyTorch 2.15.0; Python 3.12.13; MPS.

Workflow: official v0.9.5 text-to-video workflow; 512×320, batch 1, 25 conditioning/playback FPS, 30 steps, guidance 3, res_multistep. Scheduler: max_shift 2.05, base_shift 0.95, stretch true, terminal 0.1. No interpolation or upscale. WebP and WebM are written by native nodes.

Precision/device logs: diffusion model weights BF16 with no manual cast; VAE BF16 on MPS with CPU offload; T5 encoder FP16 on CPU. Checkpoint storage is also BF16. See logs/server.log.

## Actual runs

| Run | Frames | Seed | Actual time (s) | Generated frames/s | Status | Power | Sampled max RSS (GiB) | Sampled max MPS driver (GiB) | System swap before → after (GiB) |
|---|---:|---:|---:|---:|---|---|---:|---:|---|
| smoke-25f-seed41 | 25 | 41 | 115.428 | 0.2166 | execution_success | BATTERY — nonstandard; not the AC benchmark requested in handoff | 8.97 | 7.11 | 5.06 → 17.31 |
| warmup-49f-seed41 | 49 | 41 | 80.360 | 0.6098 | execution_success | BATTERY — nonstandard; not the AC benchmark requested in handoff | 0.24 | 8.15 | 20.55 → 19.98 |
| benchmark-49f-seed42 | 49 | 42 | 73.578 | 0.6660 | execution_success | BATTERY — nonstandard; not the AC benchmark requested in handoff | 0.54 | 8.15 | 19.98 → 19.94 |
| benchmark-49f-seed43 | 49 | 43 | 79.840 | 0.6137 | execution_success | BATTERY — nonstandard; not the AC benchmark requested in handoff | 0.54 | 8.15 | 19.94 → 20.39 |
| benchmark-49f-seed44 | 49 | 44 | 83.088 | 0.5897 | execution_success | BATTERY — nonstandard; not the AC benchmark requested in handoff | 0.54 | 8.15 | 20.39 → 20.22 |

Mean of seeds 42, 43, 44: **78.835 s** for 49 frames. Aggregate generation speed: 0.6215 frames/s. Playback duration is 1.96 seconds; playback FPS is unrelated to generation speed.

## Conditions and limits

Battery runs are explicitly labelled nonstandard. They do not satisfy the AC-power, Low Power Mode off benchmark conditions in the handoff. Per-run power settings are saved in the result JSON. Other user applications remain running; system swap changes are not attributed exclusively to ComfyUI. Initial system swap was already about 5.4 GiB.

Time is client submission to server execution success. Cold execution includes uncached prompt encoding/model loading. Warm runs use the same classic node cache and default ComfyUI model residency/offloading; cached node IDs and proof of sampler execution are recorded per run. Time includes sampling, VAE decode, and both native output writes, and excludes setup/downloads and later verification.

Memory is sampled at 1 Hz inside the ComfyUI process. Values are sampled maxima, not true allocator peaks. RSS and MPS allocations overlap and must not be added. Unified memory is not separate NVIDIA VRAM.

The server used --offline, offline library flags, disabled paid/custom nodes, and a Python socket audit guard blocking non-loopback connections. This does not disable internet for other applications.

Browser visual inspection was not permitted by the browser access gate. Backend behavior is verified through the local API; output media is verified separately.

## Reproduction and evidence

See README.md for commands and locations. See requirements-lock.txt, machine.json, runtime-versions.json, model-integrity.json, workflows/, logs/, output-verification.json, and output/. Output and benchmark observations are actual local measurements; no M3 Max or RTX 3050 results are substituted.

## Visual assessment

See visual-assessment.md after inspection. This is one prompt and short clips; it is not a general model-quality evaluation.

## Output checks and resource warning

All three benchmark WebM files decode to 49 frames, 512×320, 25 FPS, 1.96 seconds. Some WebP files have fewer stored frames while preserving 1.96 seconds; see visual-assessment.md. Seed43 has the clearest left-to-right movement.

The cold smoke run increased whole-system swap from about 5.06 to 17.31 GiB (+12.25 GiB). Later system swap was about 20 GiB. This is substantial swapping on the 24 GB Mac; successful completion does not mean the full pipeline fits comfortably in physical RAM. Warm-run sampled MPS driver allocation was about 8.15 GiB, which is not total application/system memory.

Offline observation after benchmark: server sockets shown by lsof were loopback only; no blocked outbound requests were recorded. See logs/network-verification.txt.

The benchmark server was stopped after delivery preparation to release model memory and its caffeinate sleep assertion. Start it manually with /Users/dyn/AI/Start-ComfyUI.command when needed.
