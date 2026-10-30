# HANDOFF TO CLAUDE AT USER REQUEST

Codex serial controllers stopped to conserve Codex usage. Read latest checkpoint in `/Users/dyn/Documents/ChatGPT/Taiwan Mobile Internship/Claude-video-benchmark-handoff.md`. No generation currently running; Wan VAE downloader may finish independently.

# Local video model comparison

User explicitly requested testing the model candidates in the original handoff and revising the PPT as a model comparison.

- Baseline LTX-Video 2B v0.9.5: completed. Evidence at ../ltx-benchmark-2026-10-29.
- LTX-Video 2B distilled v0.9.6: completed and visually inspected. Mean16.5493s/clip, MPS driver sampled maximum mean8.153GiB. Seed42 duplicates ball;43/44 nearly static. Temporary checkpoint retired after tests to fit later models; baseline preserved. ltx-distilled/pipeline-state.json.
- Wan 2.1 T2V 1.3B and Wan 2.2 TI2V 5B: official workflows adapted, serial controller active: Wan2.1 checkpoint verified, downloading shared UMT5 encoder; Wan2.2 queued. comparison-state.json.
- LTX-2.3 distilled MLX q4: isolated runtime installed and Metal calculation passed. Selected required weights 28,143,152,956 bytes including Gemma, connector, VAE encoder/decoder and spatial upscaler. No model generation tested yet. continue_mlx.py waits for successful completion of both Wan pipelines, frees only task-created candidate caches then downloads/tests MLX. PID67845 with caffeinate. Continue-comparison PID65401 with caffeinate.

Same prompt, 512×320, 25-frame cold smoke; 49-frame warmup plus measured seeds42/43/44;25FPS;batch1. Preserve model-specific sampling. Conditions battery/Low Power Mode unless runtime snapshots show otherwise. Native runtime memory counters differ; never call them total RAM. Failed tests must preserve errors, never fabricate performance numbers.

Model downloads are serialized, not concurrent with one another. Preserve all baseline files. All generation local and offline. Browser access localhost8188 was denied; do not retry via other UI paths. Local backend API remains usable.

Next: review results and contact sheets, finish MLX generation, revise the PPT using actual multi-model rows and clearly disclose conditions and metrics.
