# Kandinsky 6.0 (Pro / Pro Distill / Lite), HunyuanVideo 1.5 and Wan 2.2 (TI2V-5B, A14B) for local T2V on a 24 GB Apple Silicon Mac

Research date: 30 Oct 2026. Target machine: Mac mini M5 Pro, 24 GB unified memory (macOS recommended GPU working set about 17.8 GiB), about 15 GiB free disk (up to about 42 GiB if another model is removed).
Baseline: LTX-2.5 distilled MLX int4 on M4 Pro 24 GB. Peak process memory 15.5 GiB, about 175 s per 2 s 768x512 clip, correct motion 6/6.
Existing in-house evidence: Wan 2.2 TI2V-5B via ComfyUI FP16 on this Mac gave 1/3 correct, 274 s/clip and 14.9 GiB MPS memory.

File sizes come from the Hugging Face tree API (`/api/models/<repo>/tree/main?recursive=true`), queried 30 Oct 2026. Sizes are in decimal GB unless marked GiB. **[M]** marks a measured number, **[C]** a developer or vendor claim, and **[E]** my own estimate or derivation.

---

## Q1. Kandinsky 6.0 Lite: does it exist, what is it, and is it small enough for 24 GB?

### Takeaway
Yes. Kandinsky 6.0 Lite (3B parameters, MIT license) has official downloadable Diffusers checkpoints: Lite 5s, Lite distill 5s (10 PiFlow steps) and Lite pretrain 5s. **There is no 10s variant in 6.0.** The 10s checkpoints are Kandinsky 5.0. The Lite transformer is small (6.38 GB bf16 for distill). The problem is the bundled Qwen2.5-VL-7B text encoder (16.6 GB bf16). The full repo is 26.7 GB, which does not fit 24 GB unified memory if everything is resident and exceeds the 15 GiB of free disk. Lite is feasible only if the text encoder is run first and freed, or quantized. **No Mac/MPS run has been reported anywhere.**

### Cited Findings
- **Family and specs [C].** Kandinsky 6.0 Video is a "family of foundation diffusion models for synchronized text-to-audio-video generation". It has Lite (3B) and Pro (29B). Both generate 5-second clips with synchronized 44 kHz audio (lip-sync), in T2AV and TI2AV modes. A plug-in SR model upscales to 1920×1080. — [HF model card, Lite distill](https://huggingface.co/kandinskylab/Kandinsky-6.0-Lite-distill-5s-Diffusers); [GitHub kandinsky-6](https://github.com/kandinskylab/kandinsky-6)
- **Release dates.** Open-sourced 2026-10-06; Diffusers, ComfyUI, vLLM-omni, SGLang and FastVideo support announced the same day. The HF repos were created 2026-09-09; the pretrain repos on 2026-09-29. Paper arXiv 2610.05608 v1 is dated 4 Oct 2026. — [GitHub](https://github.com/kandinskylab/kandinsky-6); [HF API listing](https://huggingface.co/api/models?author=kandinskylab); [arXiv](https://arxiv.org/abs/2610.05608)
- **Official Lite checkpoints on HF.** `kandinskylab/Kandinsky-6.0-Lite-5s-Diffusers` (50 steps, CFG 5), `Kandinsky-6.0-Lite-distill-5s-Diffusers` (10 steps, guidance 1.0, PiflowScheduler, shift 5.0) and `Kandinsky-6.0-Lite-pretrain-5s-Diffusers`. — [Diffusers K6 docs](https://github.com/huggingface/diffusers/blob/main/docs/source/en/api/pipelines/kandinsky6.md); [Lite distill card](https://huggingface.co/kandinskylab/Kandinsky-6.0-Lite-distill-5s-Diffusers)
- **License.** The HF metadata says `license: mit` for the Lite distill repo (checked via the API, lastModified 2026-10-12). The realrebelai GGUF repo also states MIT. — [HF API](https://huggingface.co/api/models/kandinskylab/Kandinsky-6.0-Lite-distill-5s-Diffusers); [Lite distill card](https://huggingface.co/kandinskylab/Kandinsky-6.0-Lite-distill-5s-Diffusers)
- **Lite architecture [C].** 3B in total: video stream 2B, audio stream 0.6B, cross-attention 0.4B. Dual-stream CrossDiT with 32 visual blocks plus 32 audio blocks, video dim 1792 and audio dim 896. Video VAE is the Hunyuan VAE, audio is MMAudio at 44 kHz. Text encoders are Qwen2.5-VL-7B-Instruct (max 1024 tokens, dim 3584) and CLIP ViT-L/14. — [arXiv HTML](https://arxiv.org/html/2610.05608)
- **Transformer config (Lite distill).** `model_dim` 1792, `num_visual_blocks` 32, `ff_dim` 7168, `in_visual_dim` 16, `patch_size` [1,2,2]. — [config.json](https://huggingface.co/kandinskylab/Kandinsky-6.0-Lite-distill-5s-Diffusers/blob/main/transformer/config.json)
- **File sizes, Lite distill repo [M] (26.68 GB / 24.85 GiB total).**

  | Component | Size |
  |---|---:|
  | transformer | 6.38 GB |
  | text_encoder (Qwen2.5-VL, 5 shards) | 16.60 GB |
  | text_encoder_2 (CLIP-L) | 0.49 GB |
  | vae (HunyuanVideo VAE) | 0.99 GB |
  | audio_vae | 1.71 GB |
  | vocoder | 0.49 GB |

  The Lite non-distill repo is 27.78 GB (transformer 7.48 GB). — [HF tree API](https://huggingface.co/api/models/kandinskylab/Kandinsky-6.0-Lite-distill-5s-Diffusers/tree/main?recursive=true)
- **Default generation [C].** 480×864, 121 frames, 24 fps, 10 steps, guidance 1.0 for distill. The usage example calls `pipe.enable_model_cpu_offload()`. `sample_audio=False` gives video only. `expand_prompts=True` lets Qwen rewrite the prompt with no extra weights. — [Lite distill card](https://huggingface.co/kandinskylab/Kandinsky-6.0-Lite-distill-5s-Diffusers)
- **Official timings for a 5 s clip with audio at 480×864, excluding load and encode [C/M by developer].**
  - Lite Distill SD: RTX 4090 68.0 s, RTX 5060 Ti 16 GB 173.7 s, RTX 5090 44.2 s, H100 31.2 s.
  - Lite (50 steps + MagCache): 4090 267.9 s, 5060 Ti 834.9 s.

  — [GitHub README Performance](https://github.com/kandinskylab/kandinsky-6)
- **Conflicting timings in the paper.** Table 10 ("full model") gives Lite SD as 437 s on the 4090 and 1310 s on the 5060 Ti. This does not match the README's 267.9 s, probably because of different settings such as MagCache. — [arXiv HTML](https://arxiv.org/html/2610.05608) vs [GitHub](https://github.com/kandinskylab/kandinsky-6)
- **Where the time goes on the RTX 5060 Ti 16 GB (Lite distill SD, 173.7 s, "Lite stays resident", Qwen in NF4, SageAttention, torch compile) [M by developer].** DiT 53.5%, **VAE decoder 36.2%**, text encoder 5.9%. — [rtx-5060-ti.md](https://github.com/kandinskylab/kandinsky-6/blob/main/docs/performance/rtx-5060-ti.md)
- **Memory figures from the paper [M by developer, CUDA VRAM].**
  - Lite SD peak allocated, fully resident: 43.5 GiB.
  - Lite SD with block offloading: 21.7 GiB.
  - 16 GB preset: SD 7.9 GiB, HD 13.7 GiB, Full HD 12.3 GiB.

  — [arXiv HTML](https://arxiv.org/html/2610.05608)
- **Independent measurement on RTX 3090 24 GB, 864×480 × 121 frames, 10 PiFlow steps, with audio [M, third party].**
  - Original BF16: 184.60 s, torch allocated 16.13 GiB.
  - OrbitQuant W4A4 DiT plus W4A6 Qwen: 94.38 s; 100.24 s at 7.61 GiB total VRAM in low-memory mode.
  - Host RAM reached 14.6–14.9 GiB.
  - Quantized components total 9.33 GB: DiT 3.54 GB, Qwen 5.79 GB. CUDA-only setup (PyTorch 2.12.1 / CUDA 13.0).

  — [WaveCut OrbitQuant card](https://huggingface.co/WaveCut/Kandinsky-6.0-Lite-distill-5s-OrbitQuant-W4A4)
- **Community Lite quants (all aimed at CUDA ComfyUI).**
  - kabachuha Lite distill INT8 ConvRot: 3.25 GB. It needs the native ComfyUI PR, and the card says it "may NOT work" with the official node pack. — [HF](https://huggingface.co/kabachuha/Kandinsky-6.0-Lite-distill-5s-int8-convrot)
  - shadwosii Lite: bf16 7.48 GB or int8 5.26 GB. Lite distill: bf16 6.38 GB or int8 4.17 GB. — [HF tree](https://huggingface.co/shadwosii/Kandinsky-6.0)
  - DeepBeepMeep (Wan2GP) Lite distill: bf16 6.38 GB or int8 3.35 GB. — [HF tree](https://huggingface.co/DeepBeepMeep/Kandinsky6)
  - **No Lite GGUF was found** (HF search "kandinsky gguf", 30 Oct 2026).
- **Official pipeline is NVIDIA-only.** The quick start requires "An NVIDIA GPU and Python 3.13 or 3.14". `just setup` installs CUDA 13.0 PyTorch plus FlashAttention 3 or SageAttention, and `--device` defaults to `cuda`. — [quick_start.md](https://github.com/kandinskylab/kandinsky-6/blob/main/docs/quickstart/quick_start.md)

### Inferences
- **[E] Fit in 24 GB.** All Lite distill weights resident at once come to about 24.9 GiB, more than 24 GB of RAM. The text encoder alone (16.6 GB, about 15.5 GiB) is close to the 17.8 GiB working-set guidance. A workable Mac recipe has two phases:
  1. Encode the prompts with Qwen, save the embeddings, and free Qwen.
  2. Load the transformer, CLIP and VAE, about 7.9 GB of weights without the audio parts, and run the DiT and VAE decode.

  `enable_model_cpu_offload()` saves nothing on unified memory, because the "CPU" copy lives in the same RAM pool.
- **[E] Token count.** The VAE has 16 channels, 8× spatial and 4× temporal compression, and the patch is 1×2×2. A 2 s 768×512 test clip (49 frames) is then 13 × 32 × 48 ≈ 20k tokens, against ≈ 50k for the default 480×864×121. That makes it a much lighter attention load than the developer benchmarks.
- **[E] Disk.** A minimal Lite distill test (transformer, Qwen bf16, CLIP, VAE, no audio) is about 24.5 GB (22.8 GiB). It does not fit the current 15 GiB free, so another model must be removed. The audio VAE and vocoder add 2.2 GB.

### Gaps
- No measured Mac/MPS run of any Kandinsky 6 variant was found on GitHub issues (searched "mps/mac/apple" in kandinskylab/kandinsky-6: no relevant hits), on HF or on the web.
- There is no SBS or benchmark for the **Lite distill** model specifically. Only Pro distilled vs Pro full is reported.
- No Apple-compatible quantized Qwen2.5-VL that drops into the Kandinsky pipeline was found. A generic GGUF Qwen2.5-VL-7B exists (Q4_K_M 4.68 GB, Q8_0 8.1 GB, [unsloth](https://huggingface.co/unsloth/Qwen2.5-VL-7B-Instruct-GGUF)), but nobody has verified it with Kandinsky.

---

## Q2. Kandinsky 6.0 Pro and Pro Distill: quants, sizes, Mac reports, and Diffusers on MPS

### Takeaway
Pro and Pro Distill are 29B models: 69.73 GB bf16 for Pro and 60.34 GB for Pro distill (transformer only). The smallest quant is 17.13 GB (W4A8, CUDA-oriented). The smallest GGUF is 20.35 GB (Q3_K_S, non-distilled Pro only; distilled GGUF is still "Coming"). On top of that comes the 7B text encoder. **Not feasible on a 24 GB Mac.** No Mac report exists. The Diffusers base pipeline itself shows no hard CUDA-only ops in the main transformer: it uses default SDPA dispatch and fp32 RoPE. Flex attention and torch.compile are required only by the SR pipeline.

### Cited Findings
- **Pro sizes [M].** Pro transformer 69.73 GB (repo 90.04 GB). Pro distill transformer 60.34 GB (repo 80.65 GB). Pro distill config: `model_dim` 4096, 60 visual blocks, `ff_dim` 16384. — [HF tree API Pro distill](https://huggingface.co/api/models/kandinskylab/Kandinsky-6.0-Pro-distill-5s-Diffusers/tree/main?recursive=true); [config](https://huggingface.co/kandinskylab/Kandinsky-6.0-Pro-distill-5s-Diffusers/blob/main/transformer/config.json)
- **realrebelai/Kandinsky-6.0-Pro-5s_GGUFs (created 2026-10-08; "Experimental / Not Fully Tested").**
  - Pro full: Q3_K_S 20.35 GB, Q4_K_S 23.73 GB, W4A8 17.13 GB.
  - Pro distill: W4A8 17.13 GB. Distill GGUF Q3_K_S and Q4_K_S are listed as "Coming".
  - Qwen2.5-VL-7B W4A8: 5.58 GB. VAE: 0.99 GB.
  - GGUF needs two forks (RealRebelAI/Kandinsky6_GGUF and ComfyUI-GGUF-Rebel).
  - The card recommends first tests at 240×240 × 21 frames because Pro "is still a very large model even after quantization".

  — [HF card](https://huggingface.co/realrebelai/Kandinsky-6.0-Pro-5s_GGUFs)
- **DmitryDB/Kandinsky-6-Pro-Distill-5s-ComfyUI-Quants (experimental).**
  - Transformers: INT8 ConvRot 34.91 GB; variants INT8 30.24 GB and NVFP4 17.10 GB.
  - Qwen: INT8 9.58 GB; text-only INT8 7.62 GB; NVFP4 4.76 GB.
  - Smoke test on an RTX 4090 24 GB with ComfyUI dynamic CPU offload: I2V 384×608, 49 frames, 10 steps, 81.90 s [M].

  — [HF card](https://huggingface.co/DmitryDB/Kandinsky-6-Pro-Distill-5s-ComfyUI-Quants)
- **Other Pro quants.** shadwosii: Pro int8 48.21 GB, Pro distill int8 38.82 GB. DeepBeepMeep: Pro distill int8 31.45 GB. — [shadwosii](https://huggingface.co/shadwosii/Kandinsky-6.0); [DeepBeepMeep](https://huggingface.co/DeepBeepMeep/Kandinsky6)
- **Host memory [C].** The paper says Pro under the 16 GB preset "needs about 58 GiB of host RSS". With block offloading, Pro SD peaks at 21.7 GiB VRAM. — [arXiv HTML](https://arxiv.org/html/2610.05608)
- **Official Pro distill timings, 5 s SD.** RTX 4090 235.0 s, RTX 5060 Ti 717.6 s (block offload), H100 87.8 s. — [GitHub](https://github.com/kandinskylab/kandinsky-6)
- **Diffusers transformer source.** `transformer_kandinsky6.py` routes attention through `dispatch_attention_fn` with a configurable backend (default native). RoPE tables and sinusoidal embeddings are kept in fp32. A grep found no float64, complex, triton or CUDA-specific calls. — [diffusers source](https://github.com/huggingface/diffusers/blob/main/src/diffusers/models/transformers/transformer_kandinsky6.py)
- **SR pipeline only.** The docs say the SR transformer "always runs NABLA sparse attention on the `flex` backend" and must be compiled; otherwise flex "falls back to an eager implementation that needs far more memory". — [Diffusers K6 docs](https://github.com/huggingface/diffusers/blob/main/docs/source/en/api/pipelines/kandinsky6.md)
- **ComfyUI.**
  - The official extension needs ComfyUI ≥ 0.38.0. SageAttention is recommended (NVIDIA). Its one-click download bundle includes an optional Qwen3.5-9B prompt beautifier (about 19.3 GB). — [kandinsky-6 comfyui README](https://github.com/kandinskylab/kandinsky-6/blob/main/comfyui/README.md)
  - The native ComfyUI PR #16825 (kabachuha) was still **open, not merged** at the 30 Oct 2026 API check. Per its description, all variants were tested in 8-bit and vanilla Lite, and PiFlow distilled is supported via a Guider. — [PR #16825](https://github.com/Comfy-Org/ComfyUI/pull/16825)
- **Pro quality [C].** Pro distilled vs Pro full (I2AV) mean preference was 51% vs 49%, with no criterion significant. — [arXiv HTML](https://arxiv.org/html/2610.05608)

### Inferences
- **[E]** Even Pro distill W4A8 (17.13 GB) plus Qwen W4A8 (5.58 GB) is 22.7 GB of weights before activations, VAE and audio. W4A8 relies on ComfyUI's `asym_w4a8_int8` kernels, which are unlikely to have MPS paths. **Skip Pro and Pro Distill on this Mac.**
- **[E]** The Diffusers base pipeline is the most plausible MPS route for **Lite**. ComfyUI quant formats (INT8 ConvRot, NVFP4, W4A8, fp8) are CUDA-centric. An older ComfyUI issue reports that Float8_e4m3fn is unsupported on MPS ([#5533](https://github.com/Comfy-Org/ComfyUI/issues/5533), 2024; may be outdated).

### Gaps
- No Mac/MPS report exists for Pro, Pro Distill or their quants.
- Whether ComfyUI-GGUF dequantization works on MPS for Kandinsky's "FP32 Linear" path (the fix in the Rebel fork) is untested.

---

## Q3. HunyuanVideo 1.5: MLX ports, Mac/MPS reports, quant sizes, text encoder, distilled variants, license

### Takeaway
HunyuanVideo 1.5 has an 8.3B DiT. Its text encoder is Qwen2.5-VL-7B (16.58 GB bf16 / 9.38 GB fp8) plus a 0.44 GB Glyph-ByT5, and its VAE is 2.52 GB fp16. Small GGUFs exist: the 480p T2V cfg-distilled Q4_K_M is 5.09 GB. Step-distilled options:
- an official 480p I2V step-distill (8 or 12 steps);
- the LightX2V 4-step **T2V** 480p distill;
- a 4-step LoRA (0.34 GB).

One **MLX port** exists: `PocketAiHub/HunyuanVideo-1.5-Distilled-MLX` (21.08 GB, July 2026). It is **gated and territory-restricted**; its README and benchmark were not readable without login. **No measured Mac speed or memory numbers were found.** A Tencent engineer says macOS works without the advanced features. The license excludes the EU, the UK and South Korea, **not Taiwan**. It also has a 100M-MAU threshold and a ban on using outputs to improve other AI models.

### Cited Findings
- **Specs [C].** 8.3B-parameter DiT. 3D causal VAE with 16× spatial and 4× temporal compression and 32 latent channels. 54 dual-stream blocks, dim 2048. "Minimum GPU Memory: 14 GB (with model offloading enabled)". The official requirements say NVIDIA GPU with CUDA, Linux. — [HF card](https://huggingface.co/tencent/HunyuanVideo-1.5); [tech report](https://arxiv.org/html/2511.18870v2)
- **Release.** The license release date is November 21, 2025. The HF repo was last modified 2025-12-25. — [LICENSE](https://huggingface.co/tencent/HunyuanVideo-1.5/blob/main/LICENSE); [HF API](https://huggingface.co/api/models/tencent/HunyuanVideo-1.5)
- **Paper memory [M by developer].** Peak 13.6 GB for 720p, 121 frames, single GPU, with pipeline offloading, group offloading and VAE tiling. — [tech report](https://arxiv.org/html/2511.18870v2)
- **Official variants.**
  - 480p T2V/I2V, cfg-distilled 480p T2V/I2V, 480p I2V step-distilled (8 or 12 steps, recommended), 720p T2V/I2V, 720p I2V cfg-distilled (plus sparse), and 720p and 1080p SR step-distilled.
  - 720p T2V cfg-distill was still "Comming soon" on the card.
  - The cfg-distilled model "must use 50 steps".

  — [HF card](https://huggingface.co/tencent/HunyuanVideo-1.5)
- **Diffusers-format sizes [M].**
  - Official transformer folders: 33.31 GB each (fp32 storage).
  - Diffusers community 480p T2V distilled repo: 53.38 GB in total (transformer 33.31, text_encoder 14.14, text_encoder_2 0.88, vae 5.04).

  — [tencent tree](https://huggingface.co/api/models/tencent/HunyuanVideo-1.5/tree/main?recursive=true); [hunyuanvideo-community](https://huggingface.co/hunyuanvideo-community/HunyuanVideo-1.5-Diffusers-480p_t2v_distilled)
- **ComfyUI repackaged sizes (Comfy-Org) [M].**

  | File | Size |
  |---|---:|
  | 480p T2V fp16 | 16.65 GB |
  | 480p T2V cfg-distilled fp16 | 16.65 GB |
  | 480p T2V cfg-distilled fp8_scaled | 8.33 GB |
  | 480p I2V step-distilled fp16 | 16.66 GB |
  | 480p I2V step-distilled fp8 | 8.34 GB |
  | qwen_2.5_vl_7b | 16.58 GB |
  | qwen_2.5_vl_7b_fp8_scaled | 9.38 GB |
  | byt5_small_glyphxl_fp16 | 0.44 GB |
  | hunyuanvideo15_vae_fp16 | 2.52 GB |
  | `hunyuanvideo1.5_t2v_480p_lightx2v_4step_lora_rank_32_bf16` | 0.34 GB |

  — [Comfy-Org/Hunyuan-Video-1.5 tree](https://huggingface.co/Comfy-Org/Hunyuan-Video-1.5)
- **GGUF (jayn7, 2025-11-21), 480p T2V and 480p T2V cfg-distilled, same sizes for both [M].** Q4_K_S 4.92, Q4_K_M 5.09, Q5_K_S 5.94, Q5_K_M 6.12, Q6_K 7.02, Q8_0 9.00 GB. 720p and I2V GGUF repos also exist. — [jayn7 T2V 480p GGUF](https://huggingface.co/jayn7/HunyuanVideo-1.5_T2V_480p-GGUF)
- **LightX2V 4-step distill [C].** `hy1.5_t2v_480p_lightx2v_4step.safetensors` is 16.7 GB; the FP8 version is 8.85 GB. Settings: 4 steps, guidance 1, `denoising_step_list=[1000,750,500,250]`. Apache-2.0 on the distill repo, though the base model license still applies. — [lightx2v/Hy1.5-Distill-Models](https://huggingface.co/lightx2v/Hy1.5-Distill-Models)
- **MLX port: PocketAiHub/HunyuanVideo-1.5-Distilled-MLX (created 2026-07-25) [M sizes].**
  - Total 21.08 GB (19.63 GiB): transformer 11.90 GB (6 shards), Qwen text-only encoder 7.44 GB, VAE decoder 1.74 GB.
  - Ships its own `pocketai_video` runtime and a benchmark file `benchmark/horse-512x320-81f-50step.json`.
  - Gated. Gate text: "Access is available only in the licensed Territory", with a checkbox "I am not located in the European Union, United Kingdom, or South Korea". README and benchmark returned "restricted" without login.

  — [HF API tree](https://huggingface.co/api/models/PocketAiHub/HunyuanVideo-1.5-Distilled-MLX/tree/main?recursive=true); [HF API metadata](https://huggingface.co/api/models/PocketAiHub/HunyuanVideo-1.5-Distilled-MLX)
- **Other MLX ports.** `gaurav-nelson/HunyuanVideo_MLX` is a port of the *original* HunyuanVideo (Dec 2024), not 1.5. mlx-video (Blaizzy) supports only LTX-2/2.3/2.5 and Wan 2.1/2.2, not HunyuanVideo. No HunyuanVideo support was found in mflux or DiffusionKit. — [GitHub search](https://github.com/gaurav-nelson/HunyuanVideo_MLX); [mlx-video README](https://github.com/Blaizzy/mlx-video)
- **macOS via the official repo.** Issue #18 ("Is MacOS supported?", 2025-11-26) shows the CUDA device-mesh init failing on Mac. Reply from KimbingNg: "Yes, macOS is supported (without enabling advanced features like sparse attention)". The workaround is `init_process_group(backend='gloo')` or a newer PyTorch. No timings were given. — [issue #18](https://github.com/Tencent-Hunyuan/HunyuanVideo-1.5/issues/18)
- **ComfyUI has native HunyuanVideo 1.5 support** (blog, late Nov 2025). No Apple Silicon timing report was found; web searches only turned up Mac reports for the *original* HunyuanVideo, which were very slow or crashed. — [Comfy blog](https://blog.comfy.org/p/hunyuanvideo-15-native-support); [HF discussion on HunyuanVideo v1](https://huggingface.co/tencent/HunyuanVideo/discussions/13)
- **License: Tencent Hunyuan Community License [M, text].**
  - "THIS LICENSE AGREEMENT DOES NOT APPLY IN THE EUROPEAN UNION, UNITED KINGDOM AND SOUTH KOREA". Territory = worldwide excluding the EU, UK and South Korea.
  - Over 100 million MAU on the release date means a separate license is required.
  - "You must not use … any Output or results … to improve any other AI model".
  - No use outside the Territory. An Acceptable Use Policy applies.
  - Taiwan is **not** among the excluded territories.

  — [LICENSE](https://huggingface.co/tencent/HunyuanVideo-1.5/blob/main/LICENSE)

### Inferences
- **[E] Lightest ComfyUI-on-MPS recipe**, about 12.7 GB of downloads, which fits the 15 GiB free:
  - 480p T2V cfg-distilled GGUF Q5_K_M (6.12 GB) or Q4_K_M (5.09 GB);
  - Qwen2.5-VL-7B as GGUF Q4_K_M (4.68 GB), if ComfyUI-GGUF loads it for HunyuanVideo. Otherwise fp16 (16.58 GB), because fp8 on MPS is doubtful;
  - ByT5 0.44 GB and VAE 2.52 GB;
  - the 4-step LightX2V LoRA (0.34 GB).

  With the bf16 Qwen it is about 25.7 GB.
- **[E] Steps.** The cfg-distilled model at 50 steps would likely be far slower on an M5 Pro than the LTX baseline. The **4-step LoRA or LightX2V distill** is the only realistic T2V setting for parity with LTX-2.5 distilled.
- **[E] MLX port.** It is the only Apple-native path. At 19.6 GiB on disk, it requires removing another model. Reading its README and benchmark requires accepting the gate. Since the gate is territory-based, a user in Taiwan should be eligible, but legal or corporate policy should confirm.

### Gaps
- No measured Mac (MPS or MLX) speed or peak memory for HunyuanVideo 1.5 was found. The PocketAI benchmark JSON exists but is gated.
- It is unverified whether ComfyUI's HunyuanVideo 1.5 nodes accept a GGUF Qwen2.5-VL text encoder on MPS.
- The step-distilled 480p model is **I2V** only from Tencent. For T2V, only LightX2V's 4-step distill/LoRA exists, and no independent quality evaluation was found.
- It is unclear whether the Qwen2.5-VL-7B file can be shared between Kandinsky 6 and HunyuanVideo 1.5, which would save disk. Both use Qwen2.5-VL-7B, but this is not verified.

---

## Q4. Wan 2.2: MLX ports, GGUF sizes, Mac reports, A14B feasibility

### Takeaway
Wan 2.2 has the **most mature Apple Silicon tooling** of the three: mlx-video, SceneWorks/PocketAI MLX packs and FastWan MLX, plus GGUF. TI2V-5B (already tested in-house at 1/3 correct) can be made much faster with the 3-step FastWan distill on MLX, but prompt adherence is the weak point. A14B Q4 MLX has a real measured Mac run on an M5 Max 128 GB: max RSS 16.37 GiB, 10:25 for a 512×320 81-frame clip. That is borderline on a 24 GB machine, slow, and affected by open bugs: black output with quantized weights + CFG + long clips, and a T5 fp32-upcast timeout on 24 GB.

### Cited Findings
- **Official specs [C].**
  - A14B uses a MoE with two experts ("total of 27B parameters but only 14B active parameters per step").
  - TI2V-5B is a dense 5B model with a 16×16×4 VAE, 720P at 24 fps. It "can generate a 5-second 720P video in under 9 minutes on a single consumer-grade GPU"; the 5B command needs ≥24 GB VRAM with offload, and A14B needs ≥80 GB without heavy offload.
  - License Apache-2.0.

  — [Wan2.2 GitHub](https://github.com/Wan-Video/Wan2.2); [HF API](https://huggingface.co/api/models/Wan-AI/Wan2.2-TI2V-5B)
- **mlx-video (Blaizzy) [C].** Supports Wan2.2 T2V-14B, TI2V-5B and I2V-14B. Quantizes the transformer to 4 or 8 bits ("14B: ~28 GB → ~8 GB", "Enables running on 16GB devices"). Supports Lightning LoRA (`--lora-high/--lora-low`, 4 steps, CFG 1). Notes "10 steps often produces satisfying results for 14B" with UniPC. — [mlx-video README](https://github.com/Blaizzy/mlx-video); [wan_2 README](https://github.com/Blaizzy/mlx-video/blob/main/mlx_video/models/wan_2/README.md)
- **MLX weight sizes [M].**
  - TI2V-5B (SceneWorks): transformer bf16 10.00 GB, q8 5.40 GB, q4 2.95 GB. UMT5 encoder 11.36 GB bf16 (not quantized). VAE 2.82 GB. — [SceneWorks TI2V-5B](https://huggingface.co/SceneWorks/wan2.2-ti2v-5b-mlx)
  - TI2V-5B (Anes1032 q8): 19.58 GB total. — [Anes1032](https://huggingface.co/Anes1032/Wan2.2-TI2V-5B-mlx-q8)
  - A14B (SceneWorks/PocketAI): each expert bf16 28.58 GB, q8 15.40 GB, q4 8.38 GB; T5 11.36 GB; VAE 0.51 GB. The PocketAI Q4 pack is 28.66 GB (26.68 GiB). — [SceneWorks A14B](https://huggingface.co/SceneWorks/wan2.2-t2v-a14b-mlx); [PocketAI](https://huggingface.co/PocketAiHub/Wan2.2-T2V-A14B-MLX)
- **A14B on Apple M5 Max 128 GB, 512×320, 81 frames, 10 UniPC steps, guidance 3/4 [M, PocketAI].**

  | Weights | End-to-end | Max RSS | Note |
  |---|---:|---:|---|
  | Q4 | 10:25 | 16.37 GiB | "good prompt adherence" |
  | Q8 | 11:17 | 29.46 GiB | |
  | BF16 | 11:03 | 41.48 GiB | |

  - A 768×512 Q4 run took **36:53**.
  - Requirement line: "24 GB unified memory for short low-guidance tests; 128 GB was used for the validated 81-frame CFG benchmark".

  — [PocketAiHub/Wan2.2-T2V-A14B-MLX](https://huggingface.co/PocketAiHub/Wan2.2-T2V-A14B-MLX)
- **Bug: black frames (mlx-video #40, opened 2026-07-05, still open).** Quantized Wan2.2 A14B with CFG at 81 frames (832×480, M5 Pro 48 GB) gives **fully black video**. 17 frames, CFG off (guide 1, as with Lightning) or bf16 are fine. — [mlx-video #40](https://github.com/Blaizzy/mlx-video/issues/40)
- **Relay mode (PR #41, not merged at check).** `memory_mode=relay` keeps one expert resident at a time. A14B bf16 peaked at 36.8 GB (832×480, 81 frames, Lightning) or 44.3 GB with CFG on a 48 GB Mac, about 27.9 min at 20 steps. — [mlx-video PR #41](https://github.com/Blaizzy/mlx-video/pull/41)
- **Bug: T5 load timeout on 24 GB (issue #54, 2026-09-16, open, on an Apple M5 Pro 24 GB).**
  - `load_t5_encoder` upcasts the 11.36 GB bf16 T5 to fp32 (about 22.7 GB), which is "past `recommendedMaxWorkingSetSize` (17.76 GB)". This causes a Metal GPU timeout.
  - With the posted patch, a Wan2.1-1.3B 480×480 17-frame run took 165 s, of which T5 encoding was **128.5 s (78%)**.

  — [mlx-video #54](https://github.com/Blaizzy/mlx-video/issues/54)
- **FastWan2.2-TI2V-5B (DMD 3-step distill by FastVideo; Apache-2.0)** is available in MLX.
  - `lBroth/FastWan2.2-TI2V-5B-MLX`: 24.2 GB with bf16 DiT.
  - `jboone100/FastWan2.2-TI2V-5B-MLX-q8`: 8-bit T5 at 6.0 GB, 18.8 GB total.
  - Measured on an M2 Max 32 GB at 832×480 [M]:

    | Clip | Total | Peak memory |
    |---|---:|---:|
    | 1 s (25 frames) | **43 s** | 17.0 GB |
    | 5 s (121 frames) | 311 s (VAE decode 221 s) | 15.0 GB |

  - 4-bit T5 "breaks the prompt" (cosine 0.911).

  — [jboone100 card](https://huggingface.co/jboone100/FastWan2.2-TI2V-5B-MLX-q8); [lBroth card](https://huggingface.co/lBroth/FastWan2.2-TI2V-5B-MLX); [FastVideo card](https://huggingface.co/FastVideo/FastWan2.2-TI2V-5B-FullAttn-Diffusers)
- **GGUF sizes (QuantStack) [M].**
  - TI2V-5B: Q4_K_M 3.43, Q5_K_M 3.81, Q6_K 4.21, Q8_0 5.40 GB; Wan2.2 VAE 1.41 GB. — [QuantStack TI2V-5B GGUF](https://huggingface.co/QuantStack/Wan2.2-TI2V-5B-GGUF)
  - A14B, *per expert* (×2 needed): Q2_K 5.30, Q3_K_M 7.17, Q4_K_M 9.65, Q5_K_M 10.79, Q8_0 15.40 GB. — [QuantStack A14B GGUF](https://huggingface.co/QuantStack/Wan2.2-T2V-A14B-GGUF)
  - UMT5-XXL encoder GGUF: Q5_K_M 4.15, Q8_0 6.04, F16 11.37 GB. — [city96 umt5 GGUF](https://huggingface.co/city96/umt5-xxl-encoder-gguf)
- **Lightning LoRAs.** Lightning LoRAs exist for A14B T2V/I2V (rank-64 Seko LoRAs about 1.23 GB per expert). **None exists for TI2V-5B** in that repo; for 5B the step-reducers are FastWan (3-step) and "TI2V-5B-Turbo". — [lightx2v/Wan2.2-Lightning](https://huggingface.co/lightx2v/Wan2.2-Lightning)

### Inferences
- **[E] A14B on 24 GB.** Q4 with both experts resident is 15.6 GiB of weights, plus T5 unless it is freed or quantized, plus activations. PocketAI's 16.37 GiB RSS at 512×320 was measured on a 128 GB machine, where memory pressure is absent. On 24 GB it is borderline.
  - Use Lightning LoRA (4 steps, CFG 1) and 2 s clips. This also sidesteps bug #40.
  - Even so, the 768×512 Q4 CFG run of 36:53 on an M5 Max suggests **minutes per clip**, not seconds, on an M5 Pro.
  - Download is 28.7 GB, so another model must be removed.
- **[E] TI2V-5B.** FastWan q8 MLX would likely be **faster than the in-house ComfyUI FP16 test** (274 s/clip). The prompt-following weakness (1/3 in-house) is a property of the base model and is not fixed by distillation. **Low priority.**

### Gaps
- No measured Wan 2.2 A14B run on a **24 GB** Mac was found; PocketAI only states it is possible for "short low-guidance tests".
- No independent prompt-following evaluation of FastWan 3-step vs base TI2V-5B was found.

---

## Q5. Prompt-following and motion-direction evidence

### Takeaway
None of the three appears in the visible top of Artificial Analysis's open-weights T2V leaderboard, where LTX-2.5 Fast and Pro sit at about 947/944 Elo behind MiniMax H3. The evidence that exists is mostly developer-run:
- HunyuanVideo 1.5 leads Wan 2.2 on instruction following in Tencent's own eval (61.57 vs 44.07 T2V) and on LMArena (T2V 1169 vs 1132).
- Kandinsky 6 Lite and Pro beat LTX-2.5 on VABench text-video alignment (tv_align 0.227/0.229 vs 0.185). However, Pro loses prompt-following to Veo 3.1 Fast and is beaten by MiniMax H3 on most criteria.

No source tests **motion direction** (left vs right, push-in vs pull-out) specifically. The in-house 6-prompt test remains the only direct evidence.

### Cited Findings
- **Artificial Analysis AA-Video-T2V v2.1, open weights (snapshot with releases up to Aug 2026).** MiniMax H3 (768p) 1161, LTX-2.5 Fast 947, LTX-2.5 Pro 944, LTX-2.3 Pro 885, LTX-2.3 Fast 838. Kandinsky 6, HunyuanVideo 1.5 and Wan 2.2 were not in the visible portion; the page was truncated. — [AA open-weights leaderboard](https://artificialanalysis.ai/video/leaderboard/text-to-video/open-weights)
- **Kandinsky 6 paper, VABench (Table 11) [developer-run].**

  | Metric | LTX 2.5 | K6 Lite | K6 Pro |
  |---|---:|---:|---:|
  | tv_align (text-video) | 0.185 | 0.227 | 0.229 |
  | visual_realism | 4.366 | 4.459 | 4.485 |
  | visual_qa | 0.617 | 0.691 | 0.652 |
  | "alignment" | 4.527 | 4.351 | 4.329 |
  | "expressiveness" | 4.360 | 4.334 | 4.312 |

  On "alignment" and "expressiveness" LTX 2.5 is higher; the definitions were not extracted. — [arXiv HTML](https://arxiv.org/html/2610.05608)
- **Kandinsky 6 Pro SBS human eval (about 200 or more pairs per criterion; percentages only shown in figures) [developer-run].**
  - Pro vs LTX 2.5: Pro "leads visually".
  - Pro vs Veo 3.1 Fast: Veo wins on prompt following; Pro wins on artifacts and camera motion.
  - Pro vs MiniMax H3: H3 preferred on most criteria (visual quality, artifacts, motion realism significant).
  - **No SBS for Lite** vs other models.

  — [arXiv HTML](https://arxiv.org/html/2610.05608)
- **HunyuanVideo 1.5 tech report, T2V per-dimension scores [developer-run].**

  | Dimension | HY1.5 720p | Wan2.2 | Veo3 |
  |---|---:|---:|---:|
  | Instruction following | 61.57 | 44.07 | 73.77 |
  | Motion effects | 57.67 | 53.08 | 60.81 |
  | Structural stability | 79.75 | 73.75 | 75.62 |

  - T2V GSB vs Wan2.2: HY better 34.90%, Wan better 17.78% (net +17.12%). Vs Veo3: net −10.32%.
  - 300 prompts, over 100 professional assessors.

  — [tech report](https://arxiv.org/html/2511.18870v2)
- **LMArena via gradually.ai (data 2026-09-22, checked 2026-10-27).** T2V: HunyuanVideo 1.5 1169 (rank 38, 4,292 votes) vs Wan 2.2 A14B 1132 (rank 42, 10,458 votes); the confidence intervals do not overlap. I2V: 1198 vs 1170. This is a third-party aggregator page. — [gradually.ai](https://www.gradually.ai/en/ai-video-model-comparison/wan-2-2-a14b-vs-hunyuan-video-1-5/)
- **In-house baselines (from the assignment).** Wan 2.2 TI2V-5B: 1/3 correct. LTX-2.5 distilled MLX int4: 6/6 correct motion.
- **PocketAI's qualitative note** on Wan A14B Q4: "good prompt adherence" (single seed, no scoring). — [PocketAI card](https://huggingface.co/PocketAiHub/Wan2.2-T2V-A14B-MLX)

### Inferences
- **[E] HunyuanVideo 1.5.** It has the strongest documented instruction-following signal of the three against Wan 2.2. Whether it beats LTX-2.5 is unknown: no shared benchmark was found.
- **[E] Kandinsky Lite.** The VABench tv_align advantage over LTX 2.5 is the only Lite-vs-LTX signal. It is developer-run and audio-video oriented, and it does not test camera or motion direction.
- **[E] Wan 2.2 A14B** is the weakest documented instruction follower of the three per Tencent (44.07). The 5B model was already weak in-house.

### Gaps
- There is no independent benchmark (VBench-2.0, Artificial Analysis or other neutral human eval) covering Kandinsky 6 Lite, HunyuanVideo 1.5 and LTX-2.5 together.
- There is no motion-direction-specific benchmark for any of these models.
- Exact Elo for Kandinsky 6, HunyuanVideo 1.5 or Wan 2.2 on Artificial Analysis was not found.

---

## Q6. What a local test needs, and whether it is worth it

### Takeaway
Priority on a 24 GB M5 Pro:
1. **Kandinsky 6.0 Lite distill** via Diffusers on MPS, with a two-phase script: text encoder first, then DiT. This is a moderate risk with possible upside: a small 3B DiT, MIT license, 10 steps and a good tv_align score.
2. **HunyuanVideo 1.5 480p T2V** with a 4-step distill, via ComfyUI-GGUF on MPS or the gated PocketAI MLX pack. This has the best prompt-following evidence, but there is no Mac data and the license is restrictive.
3. **Wan 2.2 A14B Q4 MLX + Lightning** only if disk and time allow. It is slow, borderline on memory and has known bugs.

**Skip** Kandinsky Pro and Pro Distill (29B; not feasible). **Skip or deprioritize** Wan 2.2 TI2V-5B, which is already tested at 1/3; FastWan MLX would speed it up but is unlikely to fix prompt following.

### Test-requirement table
GB is decimal. "Peak" is measured only where marked [M]; otherwise it is an estimate [E].

| Candidate | Route | Download | Fits 15 GiB free? | Expected peak memory | Runtime evidence | Worth testing? |
|---|---|---|---|---|---|---|
| **K6 Lite distill** (3B, 10 steps, MIT) | Diffusers `Kandinsky6TI2VAPipeline` on MPS; phase 1 Qwen encode → free; phase 2 DiT+VAE; `sample_audio=False` | 24.5 GB (no audio) / 26.7 GB full | **No**, needs another model removed | [E] about 15.5 GiB during Qwen bf16 encode; about 8–12 GiB DiT+VAE phase (CUDA reference: 16.13 GiB torch-allocated BF16 on 3090 [M]; 7.9 GiB in the 16 GB preset [M]) | No Mac data. CUDA: 68 s (4090) / 173.7 s (5060 Ti) / 184.6 s (3090) per 5 s 480×864 clip [M] | **Yes, first.** Risks: MPS SDPA memory, heavy HunyuanVideo-VAE decode (36% of time on the 5060 Ti) |
| **K6 Pro / Pro Distill** (29B) | ComfyUI GGUF/W4A8 (CUDA-oriented) | ≥ 17.13 GB DiT + 5.6–16.6 GB TE + extras | No | Exceeds 24 GB [E]; paper: about 58 GiB host RSS [C] | 235 s Pro distill on a 4090 [M by developer] | **No** |
| **HunyuanVideo 1.5** 480p T2V + 4-step | ComfyUI-GGUF (Q5_K_M 6.12 GB) + Qwen2.5-VL (GGUF 4.68 or bf16 16.58) + ByT5 0.44 + VAE 2.52 + LoRA 0.34 | about 14 GB (GGUF TE) to about 26 GB (bf16 TE) | Only with a GGUF text encoder | [E] about 8–12 GiB DiT+VAE; text encoder phase up to 15.5 GiB if bf16 | No Mac data. Paper: 13.9 s for 50 steps at 480p on 8× H800 with acceleration [M by developer] | **Yes, second.** License: no EU/UK/KR use; outputs cannot improve other models |
| HunyuanVideo 1.5 (MLX) | PocketAiHub/HunyuanVideo-1.5-Distilled-MLX (gated) | 21.08 GB | No | Unknown (benchmark gated) | Unknown | Alternative to ComfyUI if the gate is accepted |
| **Wan 2.2 A14B** Q4 | mlx-video / PocketAI Q4 + Lightning LoRA (4 steps, CFG 1), 2 s clips | 28.7 GB (+2.5 GB LoRA) | No | [M] 16.37 GiB RSS at 512×320×81 on 128 GB M5 Max | [M] 10:25 at 512×320×81 (10 steps, CFG); 36:53 at 768×512 on M5 Max | **Maybe, third**. Bugs #40 and #54 |
| **Wan 2.2 TI2V-5B** (FastWan 3-step) | jboone100 FastWan q8-T5 MLX | 18.8 GB | No (unless the existing ComfyUI TI2V files are removed) | [M] 15.0–17.0 GB peak on M2 Max 32 GB | [M] 43 s for 1 s 832×480; 311 s for 5 s | **Low**; base model already 1/3 in-house |

### Cited Findings
- All sizes, timings and memory figures in the table are cited in Q1–Q4 above. Key sources:
  - [Kandinsky GitHub perf table](https://github.com/kandinskylab/kandinsky-6) and [WaveCut 3090 measurements](https://huggingface.co/WaveCut/Kandinsky-6.0-Lite-distill-5s-OrbitQuant-W4A4)
  - [jayn7 GGUF](https://huggingface.co/jayn7/HunyuanVideo-1.5_T2V_480p-GGUF) and [Comfy-Org HY1.5 files](https://huggingface.co/Comfy-Org/Hunyuan-Video-1.5)
  - [PocketAI Wan A14B benchmark](https://huggingface.co/PocketAiHub/Wan2.2-T2V-A14B-MLX) and [FastWan q8 M2 Max benchmark](https://huggingface.co/jboone100/FastWan2.2-TI2V-5B-MLX-q8)
  - [mlx-video #54 (M5 Pro 24 GB working set 17.76 GB)](https://github.com/Blaizzy/mlx-video/issues/54)

### Inferences
- **[E] Text encoders dominate memory** for all three families: Qwen2.5-VL-7B (16.6 GB bf16) for Kandinsky and HunyuanVideo, and UMT5-XXL (11.36 GB bf16) for Wan. On 24 GB unified memory, every test should:
  1. encode the prompt, then free or unload the text encoder before loading the DiT; or
  2. use an 8-bit text encoder. 4-bit UMT5 was shown to break prompts.

  This mirrors the T5 issue on M5 Pro 24 GB in mlx-video #54.
- **[E] Disk strategy.** Within 15 GiB free, only the HunyuanVideo 1.5 GGUF route with a GGUF text encoder (about 14 GB) fits. Kandinsky Lite needs the "42 GiB if another model is removed" budget.
- **[E] Fair comparison with LTX-2.5.** Use the same 2 s 768×512 prompts, measure peak process memory (as in the LTX baseline), and score motion direction on the same 6 prompts. Kandinsky outputs 24 fps natively (49 frames ≈ 2 s). HunyuanVideo 1.5 also defaults to 24 fps-class 121-frame clips. Frame counts must follow each model's 4n+1 rule.

### Gaps
- There is no Apple Silicon measurement for Kandinsky 6 (any variant) or HunyuanVideo 1.5. Speed relative to the LTX-2.5 baseline (175 s per 2 s clip) cannot be estimated from sources without guessing.
- The M5 Pro Mac mini GPU core count was not verified. The issue #54 machine (a MacBook Pro) reported 20 GPU cores.
- It was not verified whether the Diffusers HunyuanVideo-VAE decode and the Kandinsky audio path run correctly on MPS.
