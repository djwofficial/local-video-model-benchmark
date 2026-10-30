# Other open-weight text-to-video models for a 24 GB Apple Silicon Mac (Cosmos 3, LongCat-Video, Helios, and new mid/late-2026 releases)

Research date: 30 October 2026. Target: Mac mini M5 Pro 24 GB (about 17.8 GiB recommended GPU working set; about 15 GiB free disk, up to about 42 GiB if another model is removed). Baseline to beat: LTX-2.5 distilled MLX int4 (M4 Pro 24 GB: peak process memory 15.5 GiB, about 175 s per 2 s 768x512 clip, correct motion 6/6; LTX-2 Community License, free only below US$10M revenue).

Conventions: "Measured" = a number someone reports from an actual run (with hardware named). "Claimed" = vendor or model-card statement without a reproducible run. "Inference" = my own estimate from cited numbers. Download sizes marked "HF API" were computed on 30 Oct 2026 by summing file sizes from `https://huggingface.co/api/models/<repo>/tree/main?recursive=true` (1 GB = 10^9 bytes; GiB in brackets).

## Cosmos 3: variants, sizes, license, Mac path, memory

### Takeaway
Cosmos 3 has no small text-to-video variant: the smallest general checkpoint is Cosmos3-Nano at 16B (8B reasoner + 8B generator, about 35 GB BF16 download), and Super / Super-Image2Video are 64B (about 131 GB). The license (OpenMDW-1.1) is permissive and commercial-friendly, but NVIDIA tests only Linux + NVIDIA GPUs in BF16, there is no MLX port of the generator, and the only GGUF is the reasoning (VLM) branch. Not worth testing on a 24 GB Mac.

### Cited Findings
- Cosmos 3 was announced as an "omni-model" (world generation + physical reasoning + action generation) in a Hugging Face blog published 1 June 2026; it names only two sizes: Nano 16B (8B reasoner + 8B generator) "designed to run on workstation-grade compute like the RTX PRO 6000 GPU", and Super 64B (32B reasoner + 32B generator) for Hopper/Blackwell GPUs — [HF blog, NVIDIA](https://huggingface.co/blog/nvidia/cosmos-3-for-physical-ai)
- Cosmos3-Nano model card: 16B params (BF16), Mixture-of-Transformers ("two complementary transformer towers": autoregressive + diffusion), tasks include text-to-video, image-to-video, text-to-image, video-with-audio, action generation and reasoning; 256p/480p/720p; 5–400 output frames (default 189); T2V examples at 1280x720, 24 fps, 35 steps, guidance 6.0; release date 31 May 2026 — [nvidia/Cosmos3-Nano](https://huggingface.co/nvidia/Cosmos3-Nano)
- Cosmos3-Nano hardware: supported microarchitectures Ampere/Blackwell/Hopper, OS Linux, tested on GB200 and H100; "Only BF16 precision is tested", FP4/FP8/FP16 "not officially supported"; no minimum GPU memory figure is given. The only Apple mention is a Diffusers code comment ("switch to 'mps' for apple devices") — [nvidia/Cosmos3-Nano](https://huggingface.co/nvidia/Cosmos3-Nano)
- Cosmos3-Super: 64B (Hub metadata shows 65B), recommended 8x H200/H100/A100 for vLLM-Omni; 2x H200 works (about 3 minutes per video); 8x H200 about 55 s for 50 steps; names Cosmos3-Super-Image2Video as "the video-specialized checkpoint" — [nvidia/Cosmos3-Super](https://huggingface.co/nvidia/Cosmos3-Super)
- Download sizes (HF API, 30 Oct 2026): Cosmos3-Nano total 34.99 GB [32.58 GiB] (transformer 30.35 GB, sound tokenizer 1.99 GB, VAE 1.41 GB, vision encoder 1.15 GB); Cosmos3-Super-Image2Video total 130.64 GB [121.67 GiB] (transformer 128.00 GB) — [HF API Cosmos3-Nano](https://huggingface.co/api/models/nvidia/Cosmos3-Nano/tree/main?recursive=true); [HF API Super-Image2Video](https://huggingface.co/api/models/nvidia/Cosmos3-Super-Image2Video/tree/main?recursive=true)
- License: model cards state OpenMDW-1.1 and that the model "is ready for commercial and non-commercial use" — [nvidia/Cosmos3-Nano](https://huggingface.co/nvidia/Cosmos3-Nano); OpenMDW-1.1 grants rights "free of charge … without restriction", has no revenue threshold or field-of-use limit, requires keeping the license and notices only when distributing, has a patent-litigation termination clause, and imposes no restrictions on outputs — [OpenMDW 1.1 text](https://openmdw.ai/license/1-1/)
- Derivatives on HF (search API, 30 Oct 2026): the only GGUF, `Hob-forge/Cosmos3-Nano-GGUF` (Q4_K_M 5.03 GB + mmproj 1.16 GB), is explicitly the "understanding branch" (reasoning/VQA via llama.cpp), not the video generator; other quants are GPTQ/W4A16/NVFP4/FP8 (CUDA-oriented). Other NVIDIA Nano repos (Policy-DROID, Transfer-Auto, Sim-*) are robotics/transfer specializations — [HF model search "Cosmos3-Nano"](https://huggingface.co/api/models?search=Cosmos3-Nano&sort=downloads); [Hob-forge/Cosmos3-Nano-GGUF](https://huggingface.co/Hob-forge/Cosmos3-Nano-GGUF)
- Cosmos3-H-Dreams is a narrow surgical-robot world model, not a general video model — [nvidia/Cosmos3-H-Dreams](https://huggingface.co/nvidia/Cosmos3-H-Dreams)
- No Cosmos 3 benchmark numbers (VBench, Artificial Analysis) appear in the model-card text or the launch blog (results are only in images / technical report) — [nvidia/Cosmos3-Nano](https://huggingface.co/nvidia/Cosmos3-Nano); [HF blog](https://huggingface.co/blog/nvidia/cosmos-3-for-physical-ai)

### Inferences
- Nano's 30.35 GB BF16 transformer alone exceeds the 24 GB Mac's total memory; even a hypothetical 4-bit conversion of all 16B (about 8–9 GB) would need a Cosmos-specific MLX/MPS port of a MoT architecture that does not exist. Since both towers share the sequence in MoT, generation likely needs both the 8B reasoner and the 8B generator resident (inference from the architecture description, not confirmed).
- License-wise Cosmos 3 would be fine for a large telecom (OpenMDW-1.1 has no revenue cap), but it is physical-AI oriented (robotics/driving), so its value for general marketing-style T2V is unproven.
- Recommendation: do not test on the 24 GB Mac. If NVIDIA hardware is available later, Nano is the only Cosmos 3 checkpoint worth trying.

### Gaps
- A blog title reportedly mentions "Cosmos 3 Edge"; I found no model card or size for any Edge variant, so it is unconfirmed.
- Cosmos 3's text encoder is not documented in the card text (text appears to go through the AR tower; not confirmed).
- No measured memory/runtime for Nano on any single consumer GPU, and no Mac report of any kind.

## LongCat-Video (Meituan): size, encoder, files, quantization, Mac, license

### Takeaway
LongCat-Video is a 13.6B dense MIT-licensed T2V/I2V/continuation model (Oct 2025) with a UMT5-XXL text encoder; the official repo is 83 GB, there is no MLX port, no Mac report, and no T2V GGUF (only community int8 and GGUFs of the separate Avatar model). The MIT license is excellent, but it is not practical on a 24 GB Mac today.

### Cited Findings
- 13.6B total / 13.6B activated, dense (contrasted with Wan 2.2 MoE); text-to-video, image-to-video and video-continuation in one model; 720p at 30 fps; "within minutes" generation; no GPU memory numbers; official inference via `torchrun`, multi-GPU via `--context_parallel_size`; FlashAttention-2 default — [meituan-longcat/LongCat-Video](https://huggingface.co/meituan-longcat/LongCat-Video)
- License: MIT for the model weights (no trademark/patent grant) — [meituan-longcat/LongCat-Video](https://huggingface.co/meituan-longcat/LongCat-Video)
- Text encoder: acknowledgements credit UMT5-XXL; tech report arXiv 2510.22200 published 25 Oct 2025 — [meituan-longcat/LongCat-Video](https://huggingface.co/meituan-longcat/LongCat-Video)
- Published evals (internal MOS, T2V): Text-Alignment 3.76, Visual Quality 3.25, Motion Quality 3.74, Overall 3.38; I2V: Image-Alignment 4.04, Text-Alignment 3.49, Visual 3.27, Motion 3.59, Overall 3.17; WBench Navi 73.7, Full 69.9; no VBench — [meituan-longcat/LongCat-Video](https://huggingface.co/meituan-longcat/LongCat-Video)
- Download size (HF API): total 83.31 GB [77.59 GiB] — DiT 54.32 GB, text encoder 22.72 GB, LoRA 5.73 GB, VAE 0.51 GB — [HF API LongCat-Video](https://huggingface.co/api/models/meituan-longcat/LongCat-Video/tree/main?recursive=true)
- Derivatives (HF search, 30 Oct 2026): `kwanter/LongCat-Video-dit-int8` (May 2026), FastVideo Diffusers conversions plus a "T2V-Distilled-LoRA" and "Refinement-LoRA", `Kijai/LongCat-Video_comfy`; all GGUFs found are for LongCat-Video-Avatar / Avatar-1.5 (talking-avatar model), not base T2V — [HF model search "LongCat-Video"](https://huggingface.co/api/models?search=LongCat-Video&sort=downloads)
- No MLX port of LongCat-Video surfaced in search; MLX mentions found refer to Meituan's LongCat LLMs, not the video model — [web search summary incl. orcarouter.ai](https://www.orcarouter.ai/de/blog/longcat-2-5); the model card's only Apple reference is a Diffusers "mps" code comment — [meituan-longcat/LongCat-Video](https://huggingface.co/meituan-longcat/LongCat-Video)
- Not listed in Blaizzy/mlx-video (supports only LTX-2/2.3 and Wan2.1/2.2) — [Blaizzy/mlx-video](https://github.com/Blaizzy/mlx-video); not in Draw Things 2026 release notes — [Draw Things downloads](https://drawthings.ai/downloads/)

### Inferences
- The 54.32 GB DiT for 13.6B params implies FP32 storage (about 4 bytes/param); BF16 would be about 27 GB, int8 about 14 GB, 4-bit about 7–8 GB, plus the UMT5-XXL encoder (22.72 GB as stored, roughly 11 GB in BF16 — compare Wan's 11.36 GB UMT5 file in the Wan MLX repo below). A 24 GB Mac would need a 4–8-bit transformer and sequential encoder unloading via an MPS-capable runtime (e.g. ComfyUI + Kijai wrapper), none of which is documented for Mac.
- 13.6B dense at 720p/30 fps would likely be several times slower than Wan2.2 TI2V-5B on Apple Silicon (which already took 274 s for 49 frames at 512x320 on M4 Pro in this project's earlier test). Not worth testing now.

### Gaps
- No measured memory/speed on any consumer GPU or Mac; no VBench/AA Elo; no int4/GGUF for the base T2V model found.

## Helios (PKU-YuanGroup): size, encoder, files, quantization, Mac, license

### Takeaway
Helios is a 14B Apache-2.0 real-time long-video model (Mar 2026; Base/Mid/Distilled) with Diffusers support and a CUDA group-offload mode needing about 6 GB VRAM, but the Distilled repo is 138 GB, quantizations are CUDA-only (int8, bitsandbytes 4-bit), and there is no MLX/MPS port or Mac report. License is ideal; the Mac path does not exist yet.

### Cited Findings
- 14B "Real-Time Long Video Generation Model"; Apache-2.0; variants Base (v-prediction, CFG), Mid (intermediate, "may not meet expected quality"), Distilled (x0-prediction, HeliosDMDScheduler); all support T2V, I2V, V2V and interactive modes — [PKU-YuanGroup/Helios](https://github.com/PKU-YuanGroup/Helios)
- Timeline: code + weights 4 Mar 2026; arXiv 2603.04379 on 5 Mar 2026; group offloading + context parallelism 8 Mar 2026 — [PKU-YuanGroup/Helios](https://github.com/PKU-YuanGroup/Helios)
- Claimed speed/memory: "19.5 FPS on a single H100" end-to-end; about 10 FPS on one Ascend NPU; a user reported up to 20.89 FPS; group offloading needs "~6GB of VRAM" for Helios-Distilled — [PKU-YuanGroup/Helios](https://github.com/PKU-YuanGroup/Helios)
- Generation is autoregressive in 33-frame chunks (num_frames rounded up to a multiple of 33); example resolution 640x384; supported hardware NVIDIA CUDA and Ascend NPU; Mac/MPS not mentioned; no quantized versions in the official README — [PKU-YuanGroup/Helios](https://github.com/PKU-YuanGroup/Helios)
- Diffusers support (HeliosPyramidPipeline), with Distilled at BestWishYsh/Helios-Distilled — [Diffusers Helios docs](https://huggingface.co/docs/diffusers/v0.39.0/api/pipelines/helios)
- Download size (HF API): Helios-Distilled total 137.75 GB [128.29 GiB] — `transformer` 57.25 GB, `transformer_ode` 57.25 GB, text encoder 22.72 GB, VAE 0.51 GB — [HF API Helios-Distilled](https://huggingface.co/api/models/BestWishYsh/Helios-Distilled/tree/main?recursive=true)
- Community quants (HF search): `szwagros/Helios-Distilled-int8` and `szwagros/Helios-Distilled-4bit-bnb` (Mar 2026); no GGUF or MLX found — [HF model search "Helios-Distilled"](https://huggingface.co/api/models?search=Helios-Distilled&sort=downloads)
- No benchmark numbers (VBench or HeliosBench scores) appear in the README — [PKU-YuanGroup/Helios](https://github.com/PKU-YuanGroup/Helios)
- Web search for Helios/LongCat on Mac/MPS returned no relevant reports (only unrelated "Helios" software) — [search result example](https://www.helios.de/news.html)

### Inferences
- The 22.72 GB text-encoder folder is byte-identical in size to LongCat-Video's, and Wan is acknowledged, so Helios very likely uses UMT5-XXL (Wan-2.1-style stack) — inference, not stated.
- 57.25 GB per 14B transformer implies FP32 storage; only one transformer is needed per run, so a BF16 conversion would be about 28 GB, 4-bit about 7–8 GB. bitsandbytes 4-bit does not run on MPS, so a 24 GB Mac would need a new GGUF/MLX conversion.
- The "~6 GB VRAM" figure relies on CUDA host-memory offload; on unified memory, offload does not create extra memory, so it does not transfer to a 24 GB Mac.
- Not worth testing now; revisit if an MLX or GGUF port appears (Apache-2.0 makes it attractive long-term).

### Gaps
- No VBench/AA Elo or prompt-following evidence found; no consumer-GPU or Mac timings; text encoder not confirmed.

## New small open T2V models (about June–October 2026) with MLX ports or Mac support

### Takeaway
The notable new open video release with a small (3B) variant is Kandinsky 6.0 Video Lite (MIT, weights 6 Oct 2026; distilled 10-step checkpoint), but it has no MLX port and no documented Mac run yet. MiniMax H3 (33B, Jul/Aug 2026) is the open-weights quality leader and already has MLX ports and Draw Things support, but it is slow on Macs and its license needs written authorization above US$20M revenue. Other Mac-native options are Wan2.2 TI2V-5B via MLX (Apache-2.0) and the alpha MLX port of ByteDance Lance-3B-Video (Apache-2.0, limited to short clips). No smaller "Lite" LTX-2.5 exists: the distilled checkpoint is still 22B.

### Cited Findings
**Kandinsky 6.0 Video Lite (Kandinsky Lab), MIT**
- Family: Lite 3B and Pro 29B; 5-second clips with synchronized 44 kHz audio (lip-sync); T2AV and TI2AV; separate super-resolution to Full HD; Lite distilled samples in 10 steps with PiFlow scheduler, guidance 1.0; `sample_audio=False` generates video only; example 864x480, 121 frames, 24 fps; Diffusers class `Kandinsky6TI2VAPipeline` with `enable_model_cpu_offload()` — [kandinskylab/Kandinsky-6.0-Lite-distill-5s-Diffusers](https://huggingface.co/kandinskylab/Kandinsky-6.0-Lite-distill-5s-Diffusers)
- Components: Qwen2.5-VL text encoder + CLIP text encoder, HunyuanVideo VAE (`AutoencoderKLHunyuanVideo`), MMAudio VAE + vocoder — [model card](https://huggingface.co/kandinskylab/Kandinsky-6.0-Lite-distill-5s-Diffusers); paper specifies Qwen2.5-VL-7B-Instruct + CLIP ViT-L/14; Lite = 2B video stream + 0.6B audio stream + 0.4B cross-attention — [arXiv 2610.05608 (HTML)](https://arxiv.org/html/2610.05608v1)
- Dates/license: arXiv submitted 4 Oct 2026; code, checkpoints and Diffusers integration released "under the MIT license" — [arXiv 2610.05608](https://arxiv.org/abs/2610.05608); open release reported as 6 Oct 2026 — [Fuser comparison, secondary](https://fuser.studio/articles/best-open-source-video-models); HF repos created 9 Sep 2026 (HF API createdAt) — [HF model search "kandinskylab"](https://huggingface.co/api/models?search=kandinskylab&sort=downloads)
- Download size (HF API): Lite-distill total 26.68 GB [24.85 GiB] — text encoder 16.60 GB, transformer 6.38 GB, audio VAE 1.71 GB, VAE 0.99 GB, CLIP 0.49 GB, vocoder 0.49 GB; non-distilled Lite 27.78 GB [25.87 GiB] (transformer 7.48 GB) — [HF API Lite-distill](https://huggingface.co/api/models/kandinskylab/Kandinsky-6.0-Lite-distill-5s-Diffusers/tree/main?recursive=true); [HF API Lite](https://huggingface.co/api/models/kandinskylab/Kandinsky-6.0-Lite-5s-Diffusers/tree/main?recursive=true)
- Measured timings (paper Table 10, full non-distilled model, after warmup, 5 s clip / 121 frames): Lite SD 437 s on RTX 4090, 309 s on RTX 5090, 239 s on H100; Lite HD 422 s on RTX 4090 — [arXiv 2610.05608 (HTML)](https://arxiv.org/html/2610.05608v1)
- Measured peak memory (paper, CUDA): Lite SD resident 43.5 GiB; with block offload 21.7 GiB; budget presets "32/24 GB" SD 21.7 GiB, "16 GB" SD 7.9 GiB, HD 13.7 GiB — [arXiv 2610.05608 (HTML)](https://arxiv.org/html/2610.05608v1)
- Community quants (HF search): `kabachuha/Kandinsky-6.0-Lite-distill-5s-int8-convrot` (3.25 GB transformer, Apache-2.0 tag), `WaveCut/Kandinsky-6.0-Lite-distill-5s-OrbitQuant-W4A4` (9.33 GB incl. 5.79 GB text encoder); no MLX conversion found ("kandinsky mlx" search empty) — [HF model search "Kandinsky-6"](https://huggingface.co/api/models?search=Kandinsky-6&sort=downloads); [HF API int8](https://huggingface.co/api/models/kabachuha/Kandinsky-6.0-Lite-distill-5s-int8-convrot/tree/main?recursive=true)
- Mac: no Kandinsky 6 Mac/M-series report found; the only Apple-specific guidance is the "mps" code comment — [web search summary](https://huggingface.co/kandinskylab/Kandinsky-6.0-Lite-5s-Diffusers); Kandinsky is absent from Draw Things 2026 release notes — [Draw Things downloads](https://drawthings.ai/downloads/); ComfyUI has a first-party Kandinsky extension — [ComfyUI Wiki Kandinsky](https://comfyui-wiki.com/en/models/kandinsky)
- Older fallback in the same family: Kandinsky 5.0 T2V Lite (MIT; repos dated Sep–Oct 2025, including a "distilled16steps" variant) — [HF model search "kandinskylab"](https://huggingface.co/api/models?search=kandinskylab&sort=downloads)

**MiniMax H3 (MiniMax), MiniMax H3 Community License**
- 33B dense single-stream DiT (about 13B in AdaLN branches), frozen Qwen3-VL-32B encoder (50th-layer hidden states); output 4–15 s, 24 fps, default short side 768 px; the 2K regeneration and the hosted "Context-IR" layer are not part of the local 768p H3-Base — [MiniMaxAI/MiniMax-H3](https://huggingface.co/MiniMaxAI/MiniMax-H3)
- Official repo is 498.47 GB in total (HF API; transformer 66.28 GB BF16, text encoder 66.73 GB) — [HF API MiniMax-H3](https://huggingface.co/api/models/MiniMaxAI/MiniMax-H3/tree/main?recursive=true)
- MLX ports (Aug 2026): `pipenetwork/MiniMax-H3-MLX-4bit` transformer-only 25.28 GB on disk, "resident during generation 11.45 GB" (AdaLN projections precomputed into a 145 MB table for 9 steps); text encoder and VAEs loaded from upstream; measured on M3 Ultra: one denoising step about 8.8 min for a 5 s clip (dense attention, 37,966 rows) and 1.04 h per step for 15 s; quantization gives only about 1.2–1.4x end-to-end — [pipenetwork/MiniMax-H3-MLX-4bit](https://huggingface.co/pipenetwork/MiniMax-H3-MLX-4bit)
- `ddalcu/MiniMax-H3-FL2VA-MLX-Serve-4bit` (mlx-serve): 41.11 GB [38.28 GiB] pack (transformer 18.70 GB, 4-bit text encoder 15.80 GB, video VAE 5.21 GB, Apache-2.0 turbo LoRA 0.78 GB); measured on M4 Max at 960x544, 39 frames: 188 s sampling at 16 steps vs 95 s at 4 steps with the turbo LoRA (about 1.8x faster overall) — [ddalcu/MiniMax-H3-FL2VA-MLX-Serve-4bit](https://huggingface.co/ddalcu/MiniMax-H3-FL2VA-MLX-Serve-4bit)
- Draw Things added MiniMax H3 (incl. LoRAs, TeaCache) on 11 Sep 2026 (26.0910.1), and on 25 Sep 2026 (26.0924.0) added Sol Attention plus a "SpinQuant variant of 4-bit S … for lower RAM usage on low-power devices" — [Draw Things downloads](https://drawthings.ai/downloads/)
- Artificial Analysis open-weights T2V (AA-Video-T2V v2.1): #1 MiniMax H3 (768p) Elo 1161 ±14 (7,005 samples, Jul 2026); LTX-2.5 Fast 947 ±16 and LTX-2.5 Pro 944 ±16 (tied #2–3, Aug 2026); LTX-2.3 Pro 885; LTX-2.3 Fast 838 — [AA open-weights leaderboard](https://artificialanalysis.ai/video/leaderboard/text-to-video/open-weights)

**ByteDance Lance-3B-Video, MLX alpha (Apache-2.0)**
- `mlx-community/Lance-3B-Video-bf16`: MLX port of ByteDance's unified "3B-active" multimodal model (about 6.44B LLM params + 669M ViT); measured about 33 s/clip at 256x256, 17 frames or fewer on M5 Max; "production" T2V up to 768x768 x 25 frames; 768x768 x 49 frames is "structured-but-degraded" (not usable); `relay` memory mode fits validated configs in 16 GB; download 15.64 GB [14.56 GiB] (HF API); "painterly" aesthetic noted — [mlx-community/Lance-3B-Video-bf16](https://huggingface.co/mlx-community/Lance-3B-Video-bf16)

**Wan2.2 TI2V-5B via MLX (Apache-2.0)**
- Blaizzy/mlx-video (MIT) supports Wan2.1 1.3B/14B and Wan2.2 T2V-14B, TI2V-5B, I2V-14B, plus LTX-2/2.3; no Kandinsky, Helios, LongCat, Cosmos or HunyuanVideo listed; no timing or memory numbers on the page — [Blaizzy/mlx-video](https://github.com/Blaizzy/mlx-video)
- `Anes1032/Wan2.2-TI2V-5B-mlx-q8` (Jun 2026): 8-bit transformer about 5 GB, UMT5-XXL bf16 about 11 GB, VAE about 2.6 GB, total 19.58 GB [18.24 GiB] (HF API); card says it runs 1280x704 at 24 fps "comfortably" on a 64 GB Mac (no timing) — [Anes1032/Wan2.2-TI2V-5B-mlx-q8](https://huggingface.co/Anes1032/Wan2.2-TI2V-5B-mlx-q8)
- Wan open weights still stop at Wan 2.2: HF search for "Wan2.7" returned nothing per HowAIWorks, and LocalAIMaster says as of 20 Jul 2026 the official open weights stop at 2.2; claims of an Apache-2.0 Wan 2.7 (wan27.org) look like SEO content and contradict that site's own HF guide — [HowAIWorks](https://howaiworks.ai/blog/alibaba-wan-open-weights-stopped-at-2-2); [LocalAIMaster](https://localaimaster.com/blog/wan-2-7-open-source); [wan27.org](https://www.wan27.org/blog/wan-2-7-open-source-guide)

**LTX variants**
- LTX-2.5 (22B) open weights, ComfyUI article dated 11 Aug 2026: dev and distilled BF16 transformers, int8 convrot and NVFP4 distilled quants, Gemma 4 12B text encoder; spatial upscaler still hosted under LTX-2.3; gated with auto-approval — [ComfyUI Wiki LTX-2.5 news](https://comfyui-wiki.com/en/news/2026-08-11-ltx-2-5-open-weights-release); [Lightricks/LTX-2.5](https://huggingface.co/Lightricks/LTX-2.5)
- MLX conversions exist (mlx-community/ltx-2.5-mlx, -q8, -ditq8; several 4-bit community builds); `mlx-community/ltx-2.5-mlx-q8` is 24.58 GB [22.89 GiB] incl. 13.63 GB Gemma-4-12B encoder and 6.34 GB connector (HF API) — [HF model search "ltx-2.5 mlx"](https://huggingface.co/api/models?search=ltx-2.5%20mlx&sort=downloads); [mlx-community/ltx-2.5-mlx-q8](https://huggingface.co/mlx-community/ltx-2.5-mlx-q8)
- dgrauet/ltx-2-mlx is a pure MLX port of LTX-2.3 and LTX-2.5; one quantized variant reportedly fits in 16 GB — [dgrauet/ltx-2-mlx](https://github.com/dgrauet/ltx-2-mlx)
- No smaller "LTX-2.5 Lite" checkpoint surfaced: the distilled model is 22B (described as "smaller, faster" only in compute terms) — [Lightricks/LTX-2.5](https://huggingface.co/Lightricks/LTX-2.5)

**Draw Things (Mac app) video support in 2026**
- LTX-2 (3 Mar 2026), LTX-2.3 22B series (16 Mar 2026), Wan 2.x previews (Mar 2026), LTX-2.3 distilled 1.1 (20 Apr 2026), MiniMax H3 (11 and 25 Sep 2026); no video additions in the July or October 2026 notes (Oct 22 entry is MOSS Image) — [Draw Things downloads](https://drawthings.ai/downloads/); [draw-things-community releases](https://github.com/drawthingsai/draw-things-community/releases)

### Inferences
- Kandinsky 6.0 Lite is the most interesting new permissive candidate: its DiT is small (about 6.4 GB BF16), but its Qwen2.5-VL-7B encoder (16.6 GB BF16 ≈ 15.5 GiB) alone almost uses up the 17.8 GiB working set, so on 24 GB it needs strict sequential loading (encode → unload → denoise) or a quantized encoder. The paper's CUDA "16 GB preset" peak of 7.9 GiB for Lite SD suggests the denoise phase itself is small. Whether the Diffusers pipeline runs on MPS (HunyuanVideo VAE, PiFlow scheduler, custom attention) is unverified.
- Rough speed expectation (inference only): non-distilled Lite SD took 437 s on an RTX 4090; the distilled checkpoint uses 10 steps with guidance 1.0 (vs the default 50-step, guidance-5 setting), so far fewer forward passes; on an M5 Pro (much less compute than a 4090) a 5 s 864x480 clip could plausibly take several minutes. A 2 s, 768x512-class clip should be shorter; this needs measurement.
- MiniMax H3 is impractical on a 24 GB M5 Pro: an M3 Ultra needed about 8.8 min per denoising step for a 5 s clip with the dense-attention port, and the faster mlx-serve M4 Max run used a much smaller canvas (960x544, 39 frames) and a 41 GB pack that does not fit the 15 GiB free disk. Draw Things' SpinQuant 4-bit and Sol Attention may change this, but no Mac timings were published.
- Lance-3B-Video is Mac-native and fits easily, but its usable envelope (25 frames or fewer at 768², degraded at 49 frames) does not match this project's 49-frame / 2 s protocol, and its style is "painterly"; low priority.
- Wan2.2 TI2V-5B is the only Apache-2.0 model with a mainstream MLX runtime. This project's earlier ComfyUI FP16 run (M4 Pro: 274 s/clip, 14.94 GiB, 1/3 task pass at 512x320) suggests prompt/motion accuracy, not memory, is its weakness; a native MLX q8 run might be faster, but there is no evidence it would follow motion direction better.

### Gaps
- No search hits for mflux, DiffusionKit or mlx-gen adding Kandinsky 6, Helios, LongCat or Cosmos video; mflux/DiffusionKit were not checked in depth (they are image-focused as far as I know, unverified here). mlx-gen lists Wan2.2 and a "Bernini-R" model I did not investigate — [jiangzhenguo/mlx-gen](https://github.com/jiangzhenguo/mlx-gen)
- No r/LocalLLaMA, r/StableDiffusion or r/MacStudio reports were retrieved for Kandinsky 6 or MiniMax H3 on Macs (search returned none).
- LTX-2.3 IC-LoRA details (sizes, licensing, Mac support) were not researched in this pass.
- I did not find a September 2026 open T2V release beyond MiniMax H3 tooling updates; the search coverage of Sep–Oct releases was limited.

## License suitability for a large company (revenue far above US$10M)

### Takeaway
Permissive and commercially usable without revenue caps: Kandinsky 6.0 (MIT), LongCat-Video (MIT), Helios (Apache-2.0), Wan2.2 (Apache-2.0), Lance (Apache-2.0 per MLX card), and Cosmos 3 (OpenMDW-1.1, permissive). Not suitable without a separate agreement: LTX-2.5 (free only below US$10M) and MiniMax H3 (use above US$20M yearly revenue needs prior written authorization and a "MiniMax H3" UI notice).

### Cited Findings
- Kandinsky 6.0: MIT for code, checkpoints and Diffusers integration — [arXiv 2610.05608](https://arxiv.org/abs/2610.05608); model card license: mit — [Lite-distill card](https://huggingface.co/kandinskylab/Kandinsky-6.0-Lite-distill-5s-Diffusers)
- LongCat-Video: MIT for weights; no trademark/patent rights granted — [LongCat-Video card](https://huggingface.co/meituan-longcat/LongCat-Video)
- Helios: "released under the Apache 2.0 license" — [PKU-YuanGroup/Helios](https://github.com/PKU-YuanGroup/Helios)
- Wan2.2 TI2V-5B MLX port: Apache-2.0 — [Anes1032/Wan2.2-TI2V-5B-mlx-q8](https://huggingface.co/Anes1032/Wan2.2-TI2V-5B-mlx-q8)
- Lance-3B-Video MLX: tagged apache-2.0, base `bytedance-research/Lance` — [mlx-community/Lance-3B-Video-bf16](https://huggingface.co/mlx-community/Lance-3B-Video-bf16)
- Cosmos 3: OpenMDW-1.1, "ready for commercial and non-commercial use" — [Cosmos3-Nano card](https://huggingface.co/nvidia/Cosmos3-Nano); OpenMDW-1.1 has no revenue threshold or field-of-use restriction and no output restrictions — [OpenMDW 1.1](https://openmdw.ai/license/1-1/)
- MiniMax H3 Community License: Applicable Territory = worldwide excluding EU, UK, Republic of Korea and USA; Section IV.1 requires "separate, prior written authorization from MiniMax" if commercial products/services "generate more than 20 million US dollars … in yearly revenue"; IV.2 requires prominently displaying "MiniMax H3" in commercial UIs; redistribution needs a "Powered by MiniMax H3" notice — [MiniMax-H3 LICENSE](https://huggingface.co/MiniMaxAI/MiniMax-H3/blob/main/LICENSE)
- Third-party quant/LoRA repos may carry different tags (e.g. kabachuha's Kandinsky int8 tagged Apache-2.0; MiniMax turbo LoRA Apache-2.0), but the base-model license still governs the weights — [HF search Kandinsky-6](https://huggingface.co/api/models?search=Kandinsky-6&sort=downloads); [ddalcu H3 pack](https://huggingface.co/ddalcu/MiniMax-H3-FL2VA-MLX-Serve-4bit)

### Inferences
- For the telecom's production use, Kandinsky 6.0 Lite (MIT) and Wan2.2 TI2V-5B (Apache-2.0) are the realistic permissive replacements for LTX-2.5 on a 24 GB Mac; Helios and LongCat are permissive but not Mac-feasible today; Cosmos 3 is permissive but too large.
- MiniMax H3 should be treated as "evaluation/reference only" unless MiniMax grants written authorization; LTX-2.5 needs a commercial license from Lightricks above US$10M.

### Gaps
- I did not read the full Lance (ByteDance) upstream license file, LTX-2 Community License text, or any Acceptable Use Policies; legal review is still needed before deployment.

## Prompt-following and motion-direction evidence

### Takeaway
Independent, comparable evidence is thin. Artificial Analysis open-weights T2V ranks MiniMax H3 (1161) far above LTX-2.5 (about 945) and LTX-2.3 (838–885); Kandinsky 6, Helios, LongCat and Cosmos 3 do not appear in the visible AA open-weights table. Kandinsky's own paper shows Lite beating LTX-2.5 on VABench text-audio alignment and visual QA, but MiniMax H3 is preferred over Kandinsky Pro on prompt following in human eval. No source gives motion-direction accuracy for any model, so local testing remains necessary.

### Cited Findings
- AA-Video-T2V v2.1 open weights: MiniMax H3 (768p) 1161 ±14; LTX-2.5 Fast 947 ±16; LTX-2.5 Pro 944 ±16; LTX-2.3 Pro 885 ±16; LTX-2.3 Fast 838 ±17 (visible rows only) — [AA open-weights leaderboard](https://artificialanalysis.ai/video/leaderboard/text-to-video/open-weights)
- Kandinsky 6.0 paper VABench (Table 11): Lite ta_align 0.374 vs Pro 0.367 vs LTX 2.5 0.307; visual_qa Lite 0.691 vs Pro 0.652 vs LTX 0.617; Pro beats LTX 2.5 on lipsync (2.072 vs 1.567) and visual_realism (4.485 vs 4.366), LTX 2.5 has better WER (0.099 vs 0.117); in human side-by-side, MiniMax H3 is preferred over Kandinsky Pro "on most criteria with significant margins, including visual quality, motion realism, and prompt following" (no percentages given); no VBench reported — [arXiv 2610.05608 (HTML)](https://arxiv.org/html/2610.05608v1)
- LongCat-Video internal MOS (T2V): Text-Alignment 3.76, Motion Quality 3.74, Overall 3.38 (internal, non-public protocol) — [LongCat-Video card](https://huggingface.co/meituan-longcat/LongCat-Video)
- Helios and Cosmos 3: no numeric prompt-following/motion results in the README/model-card text — [Helios GitHub](https://github.com/PKU-YuanGroup/Helios); [Cosmos3-Nano](https://huggingface.co/nvidia/Cosmos3-Nano)
- This project's own local test (M4 Pro 24 GB, red-ball left-to-right task): Wan 2.2 TI2V 5B FP16 1/3 pass, Wan 2.1 1.3B 0/3, LTX-2.3 distilled MLX 3/3 at 768x512, LTX-2.5 distilled MLX 3/3 (red ball) and 3/3 (blue car) — local file `/Users/dyn/AI/video-model-comparison-2026-10-29/RESULTS.md` (measured in this project)

### Inferences
- Kandinsky's VABench "ta_align" is text-audio alignment, not text-video motion accuracy, so it says little about left-to-right motion; Lite's higher "visual_qa" than LTX 2.5 is a modest positive signal for prompt adherence (vendor-run benchmark).
- Given H3 > Kandinsky Pro on prompt following in Kandinsky's own human eval, and H3 >> LTX-2.5 on AA, H3 is likely the strongest open model for prompt following, but it is the least deployable here (speed + license).

### Gaps
- No VBench or AA Elo for Kandinsky 6 Lite, Helios, LongCat or Cosmos 3; no directional-motion benchmark for any candidate.

## Per-candidate local test requirements and whether to test

### Takeaway
Only one new model is worth a real test on the 24 GB M5 Pro: Kandinsky 6.0 Lite distilled (MIT), as a feasibility-first MPS/ComfyUI experiment after freeing disk. A native MLX re-run of Wan2.2 TI2V-5B (Apache-2.0) is a cheap secondary check. Cosmos 3, LongCat-Video, Helios and MiniMax H3 are not worth testing on this machine now.

### Cited Findings
- Kandinsky 6.0 Lite distilled: 26.68 GB [24.85 GiB] download; CUDA peaks 7.9 GiB (16 GB preset, SD) to 21.7 GiB (24 GB preset/block offload, SD); RTX 4090 non-distilled 437 s per 5 s SD clip — [HF API](https://huggingface.co/api/models/kandinskylab/Kandinsky-6.0-Lite-distill-5s-Diffusers/tree/main?recursive=true); [arXiv 2610.05608 (HTML)](https://arxiv.org/html/2610.05608v1)
- Wan2.2 TI2V-5B MLX q8: 19.58 GB [18.24 GiB] download — [HF API](https://huggingface.co/api/models/Anes1032/Wan2.2-TI2V-5B-mlx-q8/tree/main?recursive=true); prior local ComfyUI FP16 run on M4 Pro: 274.06 s/clip mean, 14.94 GiB MPS peak, 1/3 pass (512x320, 49 frames) — local `RESULTS.md` (measured in this project)
- Lance-3B-Video MLX: 15.64 GB [14.56 GiB]; about 33 s/clip at 256², 17 frames or fewer, on M5 Max; fits 16 GB in relay mode; 49 frames at 768² degraded — [mlx-community/Lance-3B-Video-bf16](https://huggingface.co/mlx-community/Lance-3B-Video-bf16)
- MiniMax H3 MLX 4-bit pack: 41.11 GB [38.28 GiB]; M4 Max 960x544x39f 95–188 s sampling; M3 Ultra dense port about 8.8 min per step for 5 s — [ddalcu pack](https://huggingface.co/ddalcu/MiniMax-H3-FL2VA-MLX-Serve-4bit); [pipenetwork 4-bit](https://huggingface.co/pipenetwork/MiniMax-H3-MLX-4bit)
- Cosmos3-Nano 34.99 GB BF16, Linux/NVIDIA only; LongCat-Video 83.31 GB; Helios-Distilled 137.75 GB — [HF API Cosmos3-Nano](https://huggingface.co/api/models/nvidia/Cosmos3-Nano/tree/main?recursive=true); [HF API LongCat](https://huggingface.co/api/models/meituan-longcat/LongCat-Video/tree/main?recursive=true); [HF API Helios](https://huggingface.co/api/models/BestWishYsh/Helios-Distilled/tree/main?recursive=true)

### Inferences
Summary table (peak memory and runtime on the M5 Pro are my estimates unless marked measured):

| Candidate | License (big-telecom OK?) | Download | Mac path today | Expected peak on 24 GB | Expected runtime (2 s, ~768x512) | Test? |
|---|---|---|---|---|---|---|
| Kandinsky 6.0 Lite distilled (3B, Oct 2026) | MIT (yes) | 26.7 GB / 24.9 GiB (needs freeing disk; about 10 GB less with a quantized encoder) | Diffusers on MPS or ComfyUI extension; untested on Mac; no MLX | Encoder phase about 15.5 GiB BF16 unless quantized; denoise phase likely under 10 GiB (CUDA 16 GB preset: 7.9 GiB) | Unknown; 10-step distilled, CFG 1; plausibly minutes | Yes: priority 1, feasibility-first |
| Wan2.2 TI2V-5B MLX q8 | Apache-2.0 (yes) | 19.6 GB / 18.2 GiB | mlx-video (Blaizzy) | Likely under the 14.9 GiB measured for FP16 ComfyUI | Possibly under 274 s (measured FP16 ComfyUI, 512x320) | Optional: cheap re-check; earlier motion accuracy weak |
| Lance-3B-Video MLX (alpha) | Apache-2.0 (yes, verify upstream) | 15.6 GB / 14.6 GiB (fits) | mlx-community + lance-mlx | Fits 16 GB in relay mode (claimed) | About 33 s at 256²/17f on M5 Max (measured by porter); 768²/25f max usable | Low priority: frame limit breaks 49-frame protocol |
| MiniMax H3 (33B) MLX 4-bit / Draw Things | Community license; written authorization needed above US$20M (no) | 38–41 GiB pack (only after removing a model) | MLX ports, mlx-serve, Draw Things | Transformer about 11.5 GB resident (claimed) + 15.8 GB 4-bit encoder, staged | Likely many minutes to hours (M3 Ultra: 8.8 min per step for 5 s) | No (license + speed); quality reference only |
| Cosmos3-Nano (16B) | OpenMDW-1.1 (yes) | 35.0 GB / 32.6 GiB | None (Linux/NVIDIA BF16 only) | BF16 transformer 30 GB > RAM | n/a | No |
| LongCat-Video (13.6B) | MIT (yes) | 83.3 GB | None found | BF16 about 27 GB > RAM; no T2V GGUF | n/a | No (revisit if GGUF/MLX appears) |
| Helios-Distilled (14B) | Apache-2.0 (yes) | 137.8 GB | None (CUDA/Ascend) | BF16 about 28 GB > RAM; bnb-4bit is CUDA-only | n/a | No (revisit if GGUF/MLX appears) |

- A practical Kandinsky test plan: download only `transformer`, `vae`, `text_encoder_2`, tokenizers and scheduler first, test MPS compatibility with `sample_audio=False`, then add the 16.6 GB Qwen2.5-VL encoder (or swap in a quantized one). Use 49 frames (or the nearest supported count) at about 768x512 to match the LTX baseline, and score with the same red-ball / blue-car tasks.
- Since no candidate here has public motion-direction evidence, the decisive metric will remain the project's own pass/fail on the directional prompts.

### Gaps
- No measured Mac memory or runtime for Kandinsky 6, LongCat, Helios or Cosmos 3; the frame count Kandinsky Lite supports below 121 frames was not confirmed (cards only show 121 frames / 5 s).
- Whether Kandinsky 6's Diffusers pipeline and HunyuanVideo VAE work on MPS without CUDA-only ops (flex attention is required for the SR pipeline, per the card) is unknown.
