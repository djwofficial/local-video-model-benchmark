# LTX-Video local setup and benchmark

Date: 29 October 2026 (Asia/Taipei).

## Locations

- ComfyUI v0.43.0: `/Users/dyn/AI/ComfyUI`
- Python 3.12 virtual environment: `/Users/dyn/AI/venvs/comfyui`
- Checkpoints: `/Users/dyn/AI/models/checkpoints`
- Text encoders: `/Users/dyn/AI/models/text_encoders`
- Outputs, logs, workflows: this directory.
- Double-click launcher: `/Users/dyn/AI/Start-ComfyUI.command`
- Local UI: http://127.0.0.1:8188

## Reproduce

Start the server with the launcher, then run:

```sh
/Users/dyn/AI/venvs/comfyui/bin/python /Users/dyn/AI/ltx-benchmark-2026-10-29/benchmark.py smoke
/Users/dyn/AI/venvs/comfyui/bin/python /Users/dyn/AI/ltx-benchmark-2026-10-29/benchmark.py bench
```

One job runs at a time. The smoke test uses 25 frames and seed 41. Benchmark mode performs a 49-frame warm-up (41) then seeds 42, 43, 44. All use 512×320, batch 1, 25 playback/conditioning FPS, 30 steps, guidance 3, `res_multistep`, and the official scheduler defaults (2.05, 0.95, stretch true, terminal 0.1). The positive prompt is in `benchmark.py`; the original negative prompt is preserved.

## Conditions and measurement

The user currently cannot connect a charger. Battery runs, including any Low Power Mode effect, are nonstandard and must not be presented as the specified AC benchmark. Machine details and initial system swap are recorded in `machine.json`. Initial swap was already in use; report before/after differences, not just the final total.

Time is client submission through server execution success, with no concurrent queued generation. Cold runs include prompt encoding/model loading. Warm runs preserve ComfyUI classic node caching and change sampler seeds; prompt encodings may be cached, while sampler, VAE decode, and both output writes must execute. Model residency/offloading uses ComfyUI defaults. Setup/download time is excluded.

Memory is sampled every second inside the server process: process RSS, PyTorch MPS current/driver allocation, system available memory and total system swap. Report sampled maxima; true allocator peaks are not measured. RSS and MPS counters overlap and must not be added. System swap can also change because of other apps. No MPS memory safety limits are relaxed.

The server uses `--offline`, offline Hugging Face/Transformers environment flags, and a Python socket audit guard allowing only loopback. Paid partner nodes and custom nodes are disabled. This does not turn off macOS networking for other applications.

## Sources

- https://github.com/Comfy-Org/ComfyUI/releases/tag/v0.43.0
- https://docs.comfy.org/installation/desktop/macos
- https://comfyanonymous.github.io/ComfyUI_examples/ltxv/
- https://comfyanonymous.github.io/ComfyUI_examples/ltxv/ltxv_text_to_video_0.9.5.json
- https://huggingface.co/Lightricks/LTX-Video/blob/main/ltx-video-2b-v0.9.5.safetensors
- https://huggingface.co/Comfy-Org/Mochi-Preview/blob/main/split_files/text_encoders/t5xxl_fp16.safetensors

Model licensing is separate from the free local runtime. Check the license applicable to the specific checkpoint before commercial use.

## Status

Completed: both model SHA256 checks passed; smoke test, 49-frame warm-up, seeds 42/43/44, and output decoding checks succeeded. See RESULTS.md and visual-assessment.md for actual measurements and quality limits. All runs were on battery with Low Power Mode on, and substantial system swap was observed.

Best motion example: output/benchmark-49f-seed43_00001_.webm. Mean measured generation time for 49 frames: 78.835 seconds.

Server stopped after tests to release memory and allow idle sleep. Double-click /Users/dyn/AI/Start-ComfyUI.command to start it; close that Terminal session with Ctrl+C when finished. The launcher prevents idle sleep while it runs. Browser visual inspection by the agent was not permitted; backend and media files were verified independently.
