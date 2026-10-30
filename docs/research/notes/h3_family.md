# MiniMax H3 video model family (H3 base, FastH3 Omni, Pika H3 Flex): can it run locally on a 24 GB Apple Silicon Mac?

Research date: 30 Oct 2026. Target machine: Mac mini M5 Pro, 24 GB unified memory (macOS recommends at most ~17.8 GiB, about 19.1 GB, as GPU working set), ~15 GiB (~16.1 GB) free disk, up to ~42 GiB (~45.1 GB) if another model is removed. Baseline to beat: LTX-2.5 distilled MLX int4 on an M4 Pro 24 GB, with 15.5 GiB peak, ~175 s per 2 s 768x512 clip, and correct motion on 6/6 tests.

Labels used below: **[MEASURED]** means a run reported by the people who did it. **[CLAIM]** means a vendor or author statement with no run behind it. **[EST]** means my own estimate. Most figures come from page extractions made with a fetch tool. Exact strings should be rechecked on the page before they go into a final report.

Background (not one of the key questions):
- MiniMax announced H3 on 31 Jul 2026. The weights went up on Hugging Face as `MiniMaxAI/MiniMax-H3` on 3 Aug 2026. — [Runpod blog, 3 Aug 2026, updated 25 Aug 2026](https://www.runpod.io/blog/minimax-h3-the-open-weight-omni-modal-video-model-and-what-it-takes-to-run-it)
- **Architecture** — [HF model card](https://huggingface.co/MiniMaxAI/MiniMax-H3)
  - A 33B dense single-stream "H3-Omni-Transformer". About 13B of its parameters sit in AdaLN branches that can be precomputed and cached for inference.
  - The text encoder is the full Qwen3-VL-32B, which uses hidden states from layer 50.
  - The video VAE compresses 16x in space and 4x in time, with 24 channels.
  - The audio VAE works at 32 kHz stereo.
  - The model outputs 4–15 s at 24 fps, with a 768 px default short side.
  - The open release supports full (dense) attention only. Sparse attention is "planned".
  - H3-Context-IR (a hosted multi-model pipeline) and H3-Regenerate-2K are **not** open-sourced.
- **Open checkpoints** — [HF model card](https://huggingface.co/MiniMaxAI/MiniMax-H3)
  - `Base FL2VA` covers text-to-audio-video (t2va) and first/last-frame (fl2va).
  - `Base Ref2VA` covers reference-to-audio-video.
  - Both are BF16 and CFG-distilled.
  - Frame counts follow a 17n+5 grid (22, 39, 56, 73, ... 124 frames). 56 frames is about 2.3 s and 124 frames is about 5.2 s. — [mlx-h3 PyPI](https://pypi.org/project/mlx-h3/); [ComfyUI FastH3 docs](https://docs.comfy.org/tutorials/video/minimax/minimax-h3-fastvideo)

---

## Q1. Which Apple Silicon ports exist, how mature are they, what hardware were they tested on, which variants do they offer, and how large are the DiT and the Qwen3-VL-32B text encoder?

### Takeaway
At least six community routes exist. All are community-built, pre-alpha or "vertical-slice" quality, from Aug–Oct 2026, and none is endorsed by MiniMax. Only two routes keep the text encoder small enough for a 24 GB Mac:
- **Quantized Qwen3-VL-32B GGUF in ComfyUI:** 14.6–18.2 GB on disk.
- **Layer-by-layer streaming of the text encoder (Argus MLX route):** a 4-bit text encoder built locally, or BF16 streamed one layer at a time.

The upstream BF16 text encoder alone is ~67 GB on disk.

### Cited Findings

**Component sizes (upstream)**
- Full Qwen3-VL-32B is **66.7 GB**. Truncated to layers 0–49 (no lm_head, no vision tower), it is **50.3 GB / 25.16B params**. — [PipeNetwork/minimax-h3-mlx README](https://github.com/PipeNetwork/minimax-h3-mlx)
- The video VAE is **10.4 GB (2.60B params)** and the audio VAE is **0.6 GB (151.3M params)**. — [PipeNetwork/minimax-h3-mlx README](https://github.com/PipeNetwork/minimax-h3-mlx)
- After the AdaLN drop, the DiT falls from **33.12B to 20.11B** resident params. The AdaLN cache is **745 MB** [MEASURED]. — [PipeNetwork/minimax-h3-mlx README](https://github.com/PipeNetwork/minimax-h3-mlx)
- The original BF16 DiT is "~62 GiB" and one BF16 DiT block is about 1.29 GB. — [Argus-AiTeam/minimax-h3-mac README](https://github.com/Argus-AiTeam/minimax-h3-mac)
- ModelFit lists the official BF16 build at **144.02 GB** in total. — [ModelFit, files read 24 Oct 2026](https://modelfit.io/video/minimax-h3/)
- The Comfy-Org repackage has a video VAE fp16 of **5.21 GB** and an audio VAE fp32 of **0.61 GB**. — [ModelFit GGUF page, 24 Oct 2026](https://modelfit.io/video/minimax-h3/gguf/)

**1. PipeNetwork/minimax-h3-mlx (MLX, Apache-2.0 code)**
- **Status:** DiT, both VAEs, the text encoder, AdaLN precompute, the scheduler and the pipeline are all done. Only the t2va path has run end to end. The fl2va path is implemented but untested end to end. 88 stars and 28 commits; no date shown on the page.
- **Tested hardware:** **Apple M3 Ultra with 550 GB** only. No 24/32/36 GB results.
- **Builds (transformer only):**

  | Build | Disk | Resident (parameter-based, not RSS) |
  |---|---|---|
  | f32 | 132.5 GB | 80.5 GB |
  | bf16 | 66.3 GB | 40.3 GB |
  | 8-bit | 35.3 GB | 21.5 GB |
  | 6-bit | 30.3 GB | 16.5 GB |
  | 4-bit | 25.3 GB | 11.5 GB |

  A 3-bit build exists but is withheld.
- **Text encoder:** no quantized text encoder. The quant builds cover the transformer only, and the VAEs and text encoder come from upstream FL2VA.
- **Activation peak (bf16, M3 Ultra):** 9.3 GB for 5 s at 1344x768, and 24.4 GB for 15 s.

  — [GitHub README](https://github.com/PipeNetwork/minimax-h3-mlx); HF repos [pipenetwork/MiniMax-H3-MLX-4bit](https://huggingface.co/pipenetwork/MiniMax-H3-MLX-4bit) and [-bf16](https://huggingface.co/pipenetwork/MiniMax-H3-MLX-bf16)

**2. mlx-h3 on PyPI (appautomaton, pure MLX)**
- **Version:** 0.0.1a3, released 6 Aug 2026 (a1 on 4 Aug, a2 on 5 Aug). Classified "2 - Pre-Alpha".
- **Requirements:** Python ≥3.13 and ffmpeg.
- **Variants:** 8-bit DiT (`dit_fl2va_a8g32`, `dit_ref2va_a8g32`) and an **8-bit text encoder (`te_qwen3vl_a8g32`)**. Video VAE in fp16, audio VAE in fp32. No 6-bit, 4-bit or NF4.
- **Memory:** the default runtime memory budget is **70 GiB**, described as "a guardrail, not a promise". The pipeline keeps one phase resident at a time.
- **Not published:** tested hardware, measured memory, timings and checkpoint sizes.
- **Limits:** canvas ≤768x1344 in multiples of 32. Context-IR and 2K regeneration are "not available locally".

  — [PyPI mlx-h3](https://pypi.org/project/mlx-h3/)

**3. antirez/h3.c (native C/Objective-C/Metal, not MLX)**
- **Status [CLAIM]:** prompt-to-video/audio, FL2VA and Ref2VA "work end to end". Active work targets M3 Max and M5 Max. 122 commits.
- **Precision:** native BF16. On **M5 / Metal 4** there is a default int8 MLP engine plus int8 QKV and attention-output projections.
- **Streaming:** `--ssd-streaming` keeps 2 DiT blocks resident and prefetches the next block from SSD. On M5, weights are mmapped from the safetensor shards. The Qwen text encoder is streamed layer by layer with I/O prefetch.
- **Measured memory:**
  - DiT tracked tensor storage fell from ~36.5 GiB to **2.0 GiB at 512² and 2.1 GiB at 864x480** with SSD streaming.
  - Peak live tensors are 25.9 GiB with int8 MLP and 36.4 GiB with BF16.
  - End-to-end renders on a **128 GB M5 Max** had a "~40.1 GB peak physical footprint, zero swaps".
- **Model file:** stated as "37 GiB".
- **Tested Macs:** none at 24/32/36/64 GB in the README.

  — [antirez/h3.c](https://github.com/antirez/h3.c); [ComfyUI-Wiki news, 9 Aug 2026](https://comfyui-wiki.com/en/news/2026-08-09-h3-c-apple-silicon-inference)

**4. Argus-AiTeam/minimax-h3-mac (MLX streaming route, Apache-2.0 code)**
- Tested **only on a 24 GB M4 Pro MacBook Pro (Mac16,8)**.
- **Text encoder:** runs only the first 50 layers, one layer at a time in a single reusable slot. A 4-bit text encoder is **built locally** with `scripts/quantize_text_encoder.py` from the FL2VA `text_encoder`. No HF repo is given for it.
- **DiT:** 2 BF16 DiT blocks resident at a time.
- **Files:**
  - Calibrated INT8 DiT: `water1234/MiniMax-H3-MLX-Argus-Calibrated-INT8`, about **37.8 GB**.
  - Native MLX BF16 Turbo: `water1234/MiniMax-H3-Turbo-v4-step600-EMA-MLX`, 53 shards, size not stated.
  - LightX2V 768p Turbo LoRA: `lightx2v/Minimax-h3-Turbo`, **1.38 GB**.
- 48 stars and 22 commits.

  — [Argus GitHub](https://github.com/Argus-AiTeam/minimax-h3-mac); [Argus README_EN revision dated 11 Aug 2026](https://raw.githubusercontent.com/Argus-AiTeam/minimax-h3-mac/7d2d00d81a51a38031adaac8bf4c2aabc307c6d2/README_EN.md)
- ModelFit lists the Argus INT8 build at **115.53 GB** total download. — [ModelFit](https://modelfit.io/video/minimax-h3/)

**5. ComfyUI GGUF on MPS (Bambushu/minimax-h3-mac "MacMax" workflow)**
- **Required files:**

  | File | Size |
  |---|---|
  | `MiniMax-H3-FL2VA-Pruned-Q5_K_M.gguf` | 14.1 GB |
  | `H3-PK-Parasyte-Turbo.safetensors` LoRA | 2.1 GB |
  | `qwen3vl-32B-MiniMax-H3-Q4_K_M.gguf` text encoder | 14.6 GB |
  | Video VAE fp16 | 5.2 GB |
  | Audio VAE fp32 | 0.6 GB |
  | **Total** | **~37 GB** (listed sizes sum to ~36.6 GB) |

- A smaller Q3_K_M DiT of **8.8 GB** is offered for small Macs.
- A `qwen3vl_4b_fp8_scaled` encoder is mentioned as a smaller-encoder alternative; its size is not listed.
- **Software:** ComfyUI v0.34.0 with PyTorch 2.13/2.14. The page is inconsistent on the PyTorch version.
- **Flags:** `--reserve-vram 1` is recommended below 32 GB.

  — [Bambushu/minimax-h3-mac](https://github.com/Bambushu/minimax-h3-mac)
- **Other GGUF builds:**
  - Unsloth DiT `minimax_h3_fl2va_pruned-Q4_K.gguf` is **11.42 GB**.
  - Unsloth Qwen3-VL-32B Q4_K_M is **18.22 GB**.
  - The full Unsloth Q4_K set is **35.45 GB**.

  — [ModelFit GGUF page](https://modelfit.io/video/minimax-h3/gguf/); repos [unsloth/MiniMax-H3-GGUF](https://huggingface.co/unsloth/MiniMax-H3-GGUF), [Abiray/MiniMax-H3-Pruned-GGUF](https://huggingface.co/Abiray/MiniMax-H3-Pruned-GGUF), [realrebelai/MiniMax-H3_GGUFs](https://huggingface.co/realrebelai/MiniMax-H3_GGUFs)

**6. ddalcu/mlx-serve 4-bit pack**
- **41.10 GB** total.
- Measured only on a 128 GB M4 Max, with peaks of 66.5–76.6 GB (see Q2).

  — [ModelFit](https://modelfit.io/video/minimax-h3/); HF [ddalcu/MiniMax-H3-FL2VA-MLX-Serve-4bit](https://huggingface.co/ddalcu/MiniMax-H3-FL2VA-MLX-Serve-4bit)

**Other repos and quality notes**
- A Sawfwair 4-bit FL2VA MLX repo also exists. — [HF Sawfwair/MiniMax-H3-FL2VA-MLX-4bit](https://huggingface.co/Sawfwair/MiniMax-H3-FL2VA-MLX-4bit/discussions)
- **Quantization quality (PipeNetwork, teacher-forced velocity error vs bf16):**

  | Bits | Video rel-L2 | Audio rel-L2 | Note |
  |---|---|---|---|
  | 8-bit | 0.0329 | 0.0130 | 27.6 dB PSNR |
  | 6-bit | 0.0611 | 0.0274 | |
  | 4-bit | 0.1649 | 0.1016 | 22.0 dB PSNR, measured at 256x256 only |
  | 3-bit | 0.2842 | — | 16.3 dB PSNR |

  The README says 4-bit looks clean at 1344x768. Audio degrades faster than video. — [PipeNetwork README](https://github.com/PipeNetwork/minimax-h3-mlx)

### Inferences
- The "pruned" GGUF DiTs are probably the AdaLN-dropped ~20B-parameter trunk. That fits the file sizes: ~20.1B params at ~5.5 bits/weight is about 14 GB for Q5_K_M.
- h3.c's "37 GiB" model file matches a pruned BF16 trunk (20.11B params × 2 bytes ≈ 37.5 GiB). [EST]
- The text encoder, not the DiT, sets the floor for 24 GB Macs. A Q4 GGUF encoder (14.6–18.2 GB) fits the GPU working set but not alongside the DiT, so stages must run one after another. The ComfyUI and Argus routes both do that.
- For the target machine, **disk is the binding constraint** more than RAM:
  - Every MLX/Metal route that uses upstream weights (Argus, h3.c, PipeNetwork, mlx-h3) needs the upstream BF16 text encoder (~50–67 GB) on disk at least during setup. That exceeds 42 GiB.
  - Only the ComfyUI GGUF set (~31–37 GB) fits in 42 GiB.
  - Nothing fits in 15 GiB.

### Gaps
- Sizes not found for: the Argus 4-bit text encoder, the mlx-h3 8-bit text encoder, and the `water1234` Turbo MLX repo.
- h3.c's exact total on-disk footprint was not confirmed.
- No port documents a test on an **M5 Pro 24 GB**. The M5-specific int8/Metal 4 paths in h3.c were tested on M5 Max and on M5 Pro 64 GB (see Q2).
- No NF4 variant for Mac was found.

---

## Q2. What memory and speed have been MEASURED on 24/32/36/48/64 GB Macs, what is the smallest Mac shown working, and how long does a clip take at small resolution?

### Takeaway
**H3 has a measured run on a 24 GB Mac:** an M4 Pro 24 GB, the same chip class as the LTX baseline, using the Argus MLX streaming route. It is roughly an order of magnitude slower than the LTX-2.5 baseline:
- **768x448, 5.17 s, 8 NFE: 1,378 s (~23 min)**, max RSS ~12.0 GB.
- **1344x768, 5.17 s, 4 NFE: 2,879 s (~48 min)**, ~15.8 GB peak footprint.

The smallest Mac shown working is a **16 GB M1 MacBook Air**. It only managed ~1 s (22-frame) clips at 352x608, taking 17–36 min.

### Cited Findings

**M4 Pro 24 GB (Mac16,8), Argus MLX streaming** — [Argus GitHub](https://github.com/Argus-AiTeam/minimax-h3-mac); [Argus README rev. 11 Aug 2026](https://raw.githubusercontent.com/Argus-AiTeam/minimax-h3-mac/7d2d00d81a51a38031adaac8bf4c2aabc307c6d2/README_EN.md)

| | Run A [MEASURED] | Run B [MEASURED] | Run C |
|---|---|---|---|
| DiT | BF16 | Calibrated INT8 | Argus INT8 |
| Text encoder | BF16, streamed | MLX 4-bit | Full BF16 |
| Turbo | LightX2V 768p 4-step | Native MLX BF16 Turbo | Native MLX BF16 Turbo |
| Output | 1344x768, 124 frames (5.17 s), stereo audio | 768x448, 124 frames | 480x864 portrait, 6.575 s |
| Steps | 5 sigma points = 4 NFE | `--steps 9` = 8 NFE | 4 NFE |
| End-to-end | **2,878.7 s** | **1,378.0 s** | Not reported |
| Breakdown | TE 30.5 s; DiT ~601 s per NFE; video VAE decode **427.4 s**; audio VAE 1.8 s | TE 23.4 s; DiT avg **154.3 s per NFE** | — |
| Memory | Peak footprint **~15.8 GB** (approx.); max RSS ~6.9 GB | Max RSS **~12.0 GB**; peak footprint not reported | — |
| Swap | Not reported | Not reported | Not reported |

- Other Run A settings: 2 blocks streamed, no block cache, `--memory-limit-gb 24`.
- Profile for Run A: attention is ~50.1% of time and linear layers ~29.6%.
- The README notes that RSS and Metal/IOSurface memory are counted differently.

**M5 Pro 48 GB, ComfyUI GGUF** — [Bambushu README](https://github.com/Bambushu/minimax-h3-mac); dated 14 Sep 2026 per [ModelFit](https://modelfit.io/video/minimax-h3/)
- Setup: Q5_K_M DiT, Qwen3-VL-32B Q4_K_M encoder, Parasyte Turbo LoRA, 8 steps, audio included.
- **352x608, 124 frames: 6 min 54 s** [MEASURED].
- **480x864, 124 frames: 12 min 52 s** [MEASURED].
- Peak memory was not reported. These are single runs, excluding download and queue time.

**M5 Pro 64 GB** — rznotes articles, 13 Aug 2026, via [ModelFit](https://modelfit.io/video/minimax-h3/) (primary article not fetched)
- ComfyUI INT8 convrot, FL2V, 352x608, 124 frames, 10 steps: **501.6 s**.
- h3.c BF16 checkpoint, 576x1024, 124 frames: **1,859.1 s**.
- h3.c with int8 at load, same settings: **1,440 s** (ModelFit grade B).

**M1 MacBook Air 16 GB, ComfyUI "light" setup** — [Bambushu README](https://github.com/Bambushu/minimax-h3-mac)
- Turbo LoRA merged with `low_vram`, 352x608, 22 frames (~1 s), 4 steps: **17 min**.
- Parasyte LoRA, 8 steps: **36 min**.
- **56 frames and up: "ran out of GPU memory"**.
- 24 GB is untested in this repo. Its estimate ("a 24 GB Mac has about 6 GB more room, which should cover 3-5 s clips at this size") is an estimate, not a run.

**M4 Max 128 GB, ddalcu/mlx-serve 4-bit pack with Turbo LoRA and audio, 4 steps** — Zenn article, 12 Aug 2026, via [ModelFit](https://modelfit.io/video/minimax-h3/)

| Resolution | Frames | Time [MEASURED] | Peak memory |
|---|---|---|---|
| 384x224 | 56 | 31.2 s | 66.7 GB |
| 512x288 | 56 | 53.8 s | 68.6 GB |
| 768x448 | 56 | 114.3 s | 72.8 GB |
| 960x544 | 56 | 203.3 s | 75.6 GB |
| 608x352 | 124 | 310.1 s | 70.4 GB |
| 608x352 | 362 | Failed (first step alone took 79 min) | Swapping under memory pressure |

**Other reports**
- h3.c on a 128 GB M5 Max: end-to-end image+audio render **74.58 s** and embedded-video+audio render **76.99 s** [MEASURED]. The resolution and frame count were not stated. The 512x512, 22-frame DiT denoise took 12.6–36.3 s depending on the int8 and token-reduction options. — [antirez/h3.c](https://github.com/antirez/h3.c)
- PipeNetwork on the M3 Ultra: one full bf16 step at 5 s 1344x768 took **531.6 s**. A full 15 s 4-bit render (8 steps) took **426 min** [MEASURED]. — [PipeNetwork README](https://github.com/PipeNetwork/minimax-h3-mlx)
- A secondary review claims a 256 GB M5 Ultra makes 768p 5 s clips in "~2 min 22 s when optimized" and is "45x slower than RTX 4090". This is unverified and secondary. — [besthub.dev](https://www.besthub.dev/articles/minimax-h3-on-mac-studio-m5-ultra-256gb-ram-fits-33b-model-but-45x-slower-than-rtx-4090-9d9a6e15cc66)
- ModelFit's RAM-fit table is internally inconsistent: its 32 GB row cites the 24 GB run, and it pairs the BF16 24 GB run with the INT8 download size. It lists no 32 GB or 36 GB Mac runs. — [ModelFit](https://modelfit.io/video/minimax-h3/)

### Inferences
- **Per second of video on the same M4 Pro 24 GB class:**
  - LTX-2.5 baseline: ~87 s per video-second (175 s ÷ 2 s at 768x512).
  - H3 Argus INT8 Run B: ~267 s per video-second (1,378 s ÷ 5.17 s at the smaller 768x448), with stereo audio included. That is roughly **3x slower per video-second at lower resolution**. [EST]
  - A 56-frame (2.3 s) H3 clip at 768x448 would likely take ~8–12 min rather than 175 s. This is an estimate: there are fewer tokens, attention is ~50% of time, and the TE/VAE overhead is fixed. [EST]
- An M5 Pro should be faster than the M4 Pro for matmul-heavy DiT work. The h3.c M5 int8 paths and MLX on M5 neural accelerators both point that way. No M5 Pro 24 GB run exists to size the gain.
- The 128 GB ddalcu numbers (e.g. 768x448, 56 frames, 4 steps in 114 s) show that H3 can be fast when everything stays resident. On 24 GB, streaming from SSD and staging models one at a time cost roughly an order of magnitude. [EST from comparing Run B with the Zenn run]
- The Run A video VAE decode (427 s at 1344x768) is a large fixed cost. Smaller canvases should cut it sharply. [EST]

### Gaps
- No measured run on any **M5 Pro 24 GB**, or on any 32 GB or 36 GB Mac.
- No peak-memory figure for the ComfyUI GGUF route at any RAM size.
- No swap figures for the 24 GB Argus runs.
- No 24 GB run at 2 s / 480p to compare directly with the LTX baseline.
- The rznotes and Zenn primary articles were seen only through ModelFit's tables.

---

## Q3. What are FastH3 Omni and Pika H3 Flex (checkpoints, distillation, adapters, resolution, hardware), and does either have a Mac path?

### Takeaway
Neither has a documented Mac, MPS or MLX path. The only Apple mention on either card is a generic "switch to 'mps'" comment in the Diffusers snippet.
- **FastH3 Omni** (FastVideo, released 20 Oct 2026) is an 8-step distillation for **reference-to-video only**. It needs at least one image or video, so it is not pure text-to-video. Its local profiles are NVIDIA-only (RTX 5090 32 GB, DGX Spark).
- **Pika H3 Flex** is a set of rank-128 LoRA adapters on top of the full H3 base, with 6-step sampling. It was validated on an H100 80 GB.

### Cited Findings

**FastH3 Omni**
- `FastVideo/FastVideo-FastH3-Omni-8-Step-V1` is the "final BF16 release checkpoint". It contains the BF16 reference transformer, schedulers and config. It loads the text encoder and VAEs from MiniMax-H3. — [HF model card](https://huggingface.co/FastVideo/FastVideo-FastH3-Omni-8-Step-V1)
- **Precisions:** separate FP8 weights (`FastH3-OmniRef-FP8`) and NVFP4 quantization-aware-distilled weights (`FastH3-OmniRef-NVFP4-QAD`), plus optional NVFP4 VAE decoders in 36-layer and 8-layer variants. NVFP4 requires Blackwell. — [HF model card](https://huggingface.co/FastVideo/FastVideo-FastH3-Omni-8-Step-V1)
- **Inference:** "eight transformer evaluations, guidance 1.0". — [HF model card](https://huggingface.co/FastVideo/FastVideo-FastH3-Omni-8-Step-V1)
- **Inputs and outputs:** a text prompt plus up to 9 images, 3 videos and 3 audio clips, with at least one image or video required. Output is 24 fps video with 32 kHz stereo audio. — [HF model card](https://huggingface.co/FastVideo/FastVideo-FastH3-Omni-8-Step-V1)
- **Supported runtimes:** GB200/B200, RTX PRO 6000 Blackwell, H100/H200, DGX Spark (GB10, 128 GB) and RTX 5090 (32 GB). The card lists them as supported, not as tested.
  - The RTX 5090 profile offloads the text encoder and needs a precomputed AdaLN table.
  - Both local profiles default to **480p**.
  - Checkpoint file sizes are not stated.

  — [HF model card](https://huggingface.co/FastVideo/FastVideo-FastH3-Omni-8-Step-V1)
- **Speed [CLAIM, team-reported]:** 5.6x–11.9x lower end-to-end latency than base H3 across 27 workloads on 8×GB200. — [ComfyUI-Wiki news, 20 Oct 2026](https://comfyui-wiki.com/en/news/2026-10-20-fasth3-omni)
- **FastH3 8-Step V2 (ComfyUI template, ~16 Sep 2026)** is the sibling that does **text-to-video and first/last-frame**; it does not do Ref2VA.
  - Files: `fastvideo_fasth3_8step_v2_pruned_int8_convrot.safetensors` DiT, `qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors` text encoder, `minimax_h3_video_vae_int8_convrot`, and audio VAE fp32.
  - Steps are fixed at 8.
  - The docs say: "FastH3 trades some motion and audio fidelity for speed."
  - No Mac or MPS notes. Sizes not listed.

  — [ComfyUI docs](https://docs.comfy.org/tutorials/video/minimax/minimax-h3-fastvideo); [ComfyUI-Wiki zh, 16 Sep 2026](https://comfyui-wiki.com/zh/news/2026-09-16-fasth3-comfyui-templates)

**Pika H3 Flex**
- `Pika-Labs/Pika-H3-Flex` is post-trained on MiniMax-H3 and generates video with stereo audio in **six sampling steps**. Its adapters are "Model Derivatives of MiniMax H3". — [HF model card](https://huggingface.co/Pika-Labs/Pika-H3-Flex)
- **Files:**
  - `fl2va/`: FP32 LoRA, rank/alpha 128.
  - `ref2va/`: FP32 LoRA, rank/alpha 128.
  - `comfy/loras/`: BF16 LoRAs in Comfy format.
  - Per-file sizes are not stated. The base components total "approximately 210 GB".

  — [HF model card](https://huggingface.co/Pika-Labs/Pika-H3-Flex)
- **Output:** native 480p and 768p across 11 aspect ratios, 5–15 s at 24 fps. Text-to-video uses the FL2VA adapter with the `t2va` task. — [HF model card](https://huggingface.co/Pika-Labs/Pika-H3-Flex)
- **Tested hardware:** "Representative 480p and 768p CLI requests passed on H100 80GB". Larger requests may need `--cpu-offload`. No speed numbers. — [HF model card](https://huggingface.co/Pika-Labs/Pika-H3-Flex)
- **Licenses:** the adapters fall under the MiniMax H3 Community License. The example code and the Qwen encoder/tokenizer assets are Apache 2.0. — [HF model card](https://huggingface.co/Pika-Labs/Pika-H3-Flex)

### Inferences
- FastH3 Omni BF16 is likely about the base DiT size: 33B × 2 bytes ≈ 66 GB, or ~40 GB if pruned. That alone exceeds the 42 GiB disk budget. Its fast formats (FP8/NVFP4) target NVIDIA tensor cores. [EST]
- Being ref2v-only, FastH3 Omni is a poor fit for a pure text-to-video comparison against LTX.
- Pika H3 Flex's Comfy BF16 LoRA could in principle be loaded onto the GGUF base in the ComfyUI MPS workflow, like the Parasyte/LightX2V Turbo LoRAs. That would give 6-step sampling. This is unverified. The Bambushu README warns that "A LoRA held on MPS runs out of memory at 16 GB", so the LoRA should stay off the GPU or be merged.
- The FastH3 V2 int8-convrot DiT might load in ComfyUI on a Mac, since a Comfy INT8 convrot base-H3 setup ran on an M5 Pro 64 GB. Its NVFP4-AWQ text encoder would likely need replacing with the GGUF Q4 encoder. This is unverified. [EST]

### Gaps
- Checkpoint byte sizes for FastH3 Omni BF16/FP8/NVFP4 and for the Pika LoRAs.
- Any community Mac run of FastH3 (V2 or Omni) or Pika H3 Flex.
- No quality comparison of Pika Flex against base H3.

---

## Q4. What evidence exists on text-to-video prompt-following and motion direction (VBench, Artificial Analysis Elo, physics/motion tests)?

### Takeaway
There are no published VBench numbers and no independent motion-direction test. Secondary sources say H3 is the top open-weight model on Artificial Analysis boards, but the Elo figures vary by board and date. Third-party hands-on tests rate its motion physics below Seedance 2.5.

Two caveats matter for a local test:
- The leaderboard/API model includes H3-Context-IR and 2K regeneration, which are not open.
- Local runs use quantization and Turbo LoRAs that trade away fidelity.

So local prompt-following may fall below what the leaderboards suggest.

### Cited Findings
- **No standard benchmarks:** MiniMax has not published VBench, MovieGenBench or EvalCrafter-type results. The HF model card lists no benchmarks. — [HF model card](https://huggingface.co/MiniMaxAI/MiniMax-H3); summary of reviews via [autoae.online](https://autoae.online/blog/minimax-h3-examples)
- **Artificial Analysis Elo (seen only as search snippets; I could not fetch the pages to confirm which figure is on which page):**
  - H3 "placed first in Video Editing, second in Text-to-Video, third in Image-to-Video".
  - Elo 1,239 with 6,034 samples, #2 overall and #1 open-weight.
  - On boards read 10 Oct: Elo 1,181 for I2V and **1,137 for T2V**.
  - H3 at Elo 1,184 vs the derivative H3 Max at 1,204 on I2V with audio.

  Sources: [kompozy](https://kompozy.io/news/minimax-h3-first-open-model-tops-video-ranking); [orcarouter H3 Max vs H3](https://www.orcarouter.ai/es/blog/h3-max-vs-minimax-h3); [orcarouter HiDream vs H3](https://www.orcarouter.ai/es/blog/hidream-o1-video-1-0-vs-minimax-h3). The Artificial Analysis model page URL returned 404 when fetched. — [artificialanalysis.ai](https://artificialanalysis.ai/video/models/minimax-h3)
- **Arena claims:** Arena reported 1,390 on Video Edit Arena per one outlet and 1,388 per another. An Aug 3 review did not find H3 on Arena's text-to-video board, so its Arena ranking remains a MiniMax claim. — [cryptobriefing](https://cryptobriefing.com/minimax-h3-video-edit-arena-top-rank/); [runtimewire, 2 Aug 2026](https://runtimewire.com/article/minimax-h3-open-video-benchmark-lead); [DeepLearning.AI The Batch](https://www.deeplearning.ai/the-batch/minimaxs-state-of-the-art-video-model-is-only-minimally-open)
- **Motion physics [reseller-adjacent, treat with caution]:** Atlas Cloud scored H3 **7.1/10 overall and 6.2/10 on Motion Physics**, versus 8.4 for Seedance 2.5 and 7.2 for Wan 3.0. It noted fluid stride but an object-consistency error (an object "pops into" a hand). — [Atlas Cloud blog](https://www.atlascloud.ai/zh-TW/blog/tips/choose-ai-video-model-wan-3.0-seedance-2.5-minimax-h3)
- **Not ready for unattended delivery:** reviewers say speech, lip sync, hand topology, object trajectories and text still need review and repair. — [autoae.online](https://autoae.online/blog/minimax-h3-examples)
- **Community physics fix:** the Licon VBVR LoRA is marketed as fixing "H3's worst motion failures" (duplicated objects, clipping, broken motion), which implies those failures are common. — [hermes-ai.net](https://hermes-ai.net/news/liconstudio-s-licon-vbvr-fixes-minimax-h3-s-worst-motion-failures/)
- **Distillation cost:** FastH3 "trades some motion and audio fidelity for speed". — [ComfyUI docs](https://docs.comfy.org/tutorials/video/minimax/minimax-h3-fastvideo)
- **Quantization cost:**
  - PipeNetwork's 4-bit video velocity error (rel-L2 0.165) is about 5x that of 8-bit. — [PipeNetwork](https://github.com/PipeNetwork/minimax-h3-mlx)
  - Argus says its INT8 DiT "is not mathematically lossless". — [Argus](https://github.com/Argus-AiTeam/minimax-h3-mac)
  - Bambushu says EasyCache and Spectrum "failed visual review with Parasyte". — [Bambushu](https://github.com/Bambushu/minimax-h3-mac)

### Inferences
- Even taking the leaderboard figures at face value, they describe the hosted model. The local 24 GB routes add Q4/INT8 quantization, a Turbo LoRA at 4–8 steps, and no Context-IR. Local motion-direction correctness against LTX-2.5's 6/6 has to be tested, not assumed. [EST]

### Gaps
- No independent VBench run.
- No public "motion direction" test (e.g. "car drives left to right") for H3.
- No head-to-head of H3 and LTX-2.x on prompt adherence from a neutral evaluator.
- Could not fetch the live Artificial Analysis leaderboard to confirm current Elo.

---

## Q5. What do the license terms mean for a large company (revenue far above US$20M): territory, commercial thresholds, attribution?

### Takeaway
The excluded territories are the EU, UK, US and South Korea. Commercial use is another matter: products or services earning more than US$20M a year need **prior written authorization from MiniMax**, and any commercial product must prominently display "MiniMax H3".

### Cited Findings
- **Territory:** the Excluded Territories are "the European Union, the United Kingdom, the Republic of Korea and the United States of America". Hong Kong appears only as the governing law (Section IX.1). — [LICENSE](https://huggingface.co/MiniMaxAI/MiniMax-H3/blob/main/LICENSE)
- The official FAQ says the license "currently excludes the EU, UK, US, and South Korea" and that MiniMax "will expand the territory scope as the regulatory picture clarifies". This means the territory list may change. — [design.minimax.io/h3](https://design.minimax.io/h3)
- **Commercial threshold:** Section IV.1 requires prior written authorization if products or services "generate more than 20 million US dollars" in yearly revenue. There is no MAU or headcount threshold. — [LICENSE](https://huggingface.co/MiniMaxAI/MiniMax-H3/blob/main/LICENSE)
- The FAQ wording is "if your commercial products or services exceed US$20 million in yearly revenue". To apply, email api@minimax.io with subject "MiniMax H3 licensing – authorization request". It does not say whether parent or affiliate revenue counts. — [design.minimax.io/h3](https://design.minimax.io/h3)
- **Attribution:**
  - Section IV.2 requires that commercial products "prominently display" "MiniMax H3" in the UI.
  - Section III.3(a) "encourages" a "Powered by MiniMax H3" notice.
  - Redistribution needs a NOTICE file ("MiniMax H3 is licensed under the MiniMax H3 Community License Agreement, Copyright © 2026 MiniMax").

  — [LICENSE](https://huggingface.co/MiniMaxAI/MiniMax-H3/blob/main/LICENSE)
- **Outputs and derivatives:**
  - "MiniMax claims no rights over the Outputs" (Section VI.4).
  - Derivatives are yours, as between you and MiniMax (Section VI.1).
  - Section V.3 bars using H3 or its outputs "to improve any other artificial intelligence model". The FAQ says distilling into non-H3 models is not permitted.

  — [LICENSE](https://huggingface.co/MiniMaxAI/MiniMax-H3/blob/main/LICENSE); [FAQ](https://design.minimax.io/h3)
- **Acceptable Use Policy (Exhibit A):** includes "Use for military purposes" and high-risk automated decisions (healthcare, law enforcement, credit). Anyone hosting H3 for third parties must implement content safeguards. Breach allows termination, after which copies must be deleted. — [LICENSE](https://huggingface.co/MiniMaxAI/MiniMax-H3/blob/main/LICENSE); [FAQ](https://design.minimax.io/h3)
- The HF card notes that the application form is only for the US, EU, UK and South Korea. — [HF model card](https://huggingface.co/MiniMaxAI/MiniMax-H3)
- **Derivatives carry the license:** FastH3 Omni and the Pika H3 Flex adapters are under the same MiniMax H3 Community License. Pika calls its adapters "Model Derivatives". Licenses for community Turbo LoRAs (LightX2V, Parasyte, Larry) and the Argus INT8 weights are not stated. — [FastVideo card](https://huggingface.co/FastVideo/FastVideo-FastH3-Omni-8-Step-V1); [Pika card](https://huggingface.co/Pika-Labs/Pika-H3-Flex); [Argus](https://github.com/Argus-AiTeam/minimax-h3-mac)
- **Unverified single-source claim:** a ComfyUI-related source says "commercial use of locally generated outputs requires a MiniMax commercial license sold through Comfy". This conflicts with the license's "no rights over the Outputs" wording and could not be verified. It appeared in search snippets around [ModelFit Mac blog](https://modelfit.io/blog/minimax-h3-on-mac/) and [instasd](https://www.instasd.com/post/minimax-h3-comfyui-nodes-open-weights).
- **Port code licenses:** PipeNetwork and Argus code is Apache-2.0. mlx-h3 says it is not affiliated with MiniMax. — [PipeNetwork](https://github.com/PipeNetwork/minimax-h3-mlx); [Argus](https://github.com/Argus-AiTeam/minimax-h3-mac); [PyPI](https://pypi.org/project/mlx-h3/)

### Inferences
- Internal, non-commercial technical evaluation on a Mac appears permitted without applying. Any production or customer-facing use by a company of this size would very likely trigger the US$20M clause, which means written authorization plus "MiniMax H3" shown in the UI. [Legal review needed; not legal advice]
- If any development, hosting or users sit in the US, EU, UK or South Korea (cloud regions, vendors, staff), the territory exclusion could apply.
- The anti-distillation clause matters if the team ever wants to use H3 outputs to fine-tune LTX or other models.

### Gaps
- Whether "your products or services" means the specific H3-powered product's revenue or group revenue.
- Whether internal-only or R&D use by a >US$20M company counts as "commercial".
- Licenses of the community Turbo LoRAs and GGUF repacks.
- The license effective date: one secondary source says 2 Aug 2026; not confirmed on the license page.

---

## Q6. Bottom line: is anything in the H3 family worth a local test on this 24 GB Mac, and what exactly would the test need?

### Takeaway
**Base H3 FL2VA (text-to-video) is the only family member worth a test, and only as a feasibility and quality probe, not as an LTX replacement.** On 24 GB-class hardware it is measured at roughly 3x slower per video-second than the LTX-2.5 baseline, at lower resolution. There is no evidence yet that its local motion correctness beats LTX's 6/6.

The practical routes:
- **ComfyUI GGUF route:** the only one that fits the 42 GiB disk budget (~31–37 GB). It fits only after another model is removed, and it is **untested on 24 GB**.
- **Argus MLX streaming route:** the only one with a **measured 24 GB success**, but it needs ~115 GB of disk (external SSD).

FastH3 Omni (NVIDIA-only, ref2v-only) and Pika H3 Flex (H100-validated LoRAs on a ~210 GB base) are not worth testing on this Mac.

### Cited Findings (inputs for the test spec)

**Option 1: ComfyUI GGUF on MPS**
- **Files** (fits ≤42 GiB; does not fit 15 GiB):

  | File | Size |
  |---|---|
  | DiT `MiniMax-H3-FL2VA-Pruned-Q3_K_M` (or Q5_K_M) | 8.8 GB (14.1 GB) |
  | `qwen3vl-32B-MiniMax-H3-Q4_K_M.gguf` | 14.6 GB |
  | Video VAE fp16 | 5.2 GB |
  | Audio VAE fp32 | 0.6 GB |
  | Optional Turbo LoRA (Parasyte or LightX2V) | 2.1 GB or 1.38 GB |
  | **Total** | **~29.2–36.6 GB**, plus ComfyUI and PyTorch |

- **Launch:** `--reserve-vram 1` for Macs under 32 GB.
- **Measured reference:** 6 min 54 s for 352x608, 5.17 s, 8 steps on an M5 Pro 48 GB.

  — [Bambushu](https://github.com/Bambushu/minimax-h3-mac); [ModelFit GGUF](https://modelfit.io/video/minimax-h3/gguf/); [Argus](https://github.com/Argus-AiTeam/minimax-h3-mac)

**Option 2: Argus MLX streaming on 24 GB**
- **Measured:** ~12.0 GB max RSS and 1,378 s for 768x448, 5.17 s, 8 NFE on an M4 Pro 24 GB. ~15.8 GB peak footprint for BF16 at 1344x768. — [Argus](https://github.com/Argus-AiTeam/minimax-h3-mac)
- **Disk:**
  - INT8 DiT ~37.8 GB.
  - Upstream text encoder needed to build the 4-bit encoder (~66.7 GB full).
  - VAEs ~10.4 GB.
  - Turbo weights.
  - ModelFit puts the total at **115.53 GB**.

  — [Argus](https://github.com/Argus-AiTeam/minimax-h3-mac); [PipeNetwork](https://github.com/PipeNetwork/minimax-h3-mlx); [ModelFit](https://modelfit.io/video/minimax-h3/)

**Option 3: h3.c with `--ssd-streaming`**
- DiT tracked storage ~2 GiB, and it has M5-specific int8 paths.
- Measured on an M5 Pro 64 GB: 576x1024, 124 frames in 1,440–1,859 s.
- It needs the official BF16 weights (model file "37 GiB" plus a streamed text encoder), so it also exceeds 42 GiB.

  — [antirez/h3.c](https://github.com/antirez/h3.c); [ModelFit](https://modelfit.io/video/minimax-h3/)

### Inferences (recommended test spec, all estimates)
- **Recommended test: ComfyUI GGUF, Option 1 with the Q3_K_M DiT.** This requires deleting the other model to free ~42 GiB.
  - **Download:** ~29–31 GB of model files, plus the ComfyUI/PyTorch environment (a few GB).
  - **Settings:**
    - Text-to-video (FL2VA t2va).
    - **352x608 or 448x768, 56 frames (2.3 s)** to match the LTX 2-second protocol.
    - 4 steps with the LightX2V/Parasyte Turbo LoRA, or 8 steps without it.
    - `--reserve-vram 1 --cache-none --disable-smart-memory`.
    - Keep the LoRA off the GPU, or merge it.
  - **Expected peak memory [EST]:**
    - Text-encoder stage ~15–16 GB (Q4_K_M 14.6 GB of weights plus overhead).
    - DiT stage ~11–13 GB with Q3_K_M (8.8 GB of weights plus small-canvas activations; PipeNetwork measured 9.3 GB of activations at full 1344x768, 5 s, so small canvases should need much less).
    - **Q5_K_M (14.1 GB) plus LoRA plus activations is likely to exceed the ~17.8 GiB GPU working set.** Start with Q3_K_M.
    - The VAE decode stage is ~5–8 GB.
  - **Expected time [EST]:** ~3–8 min per 2.3 s clip at 352x608. This extrapolates the measured 6 min 54 s for 124 frames on the 48 GB M5 Pro. It is very uncertain because the 24 GB run will stage and evict models.
  - **Quality risk:** Q3_K_M is a heavier quantization than any configuration quality-checked in these sources. Q4 was 22 dB PSNR in PipeNetwork's 256x256 check. Motion and direction correctness has to be scored on the same 6 prompts used for LTX.
- **If an external Thunderbolt SSD of ≥150 GB is acceptable:** the Argus INT8 + 4-bit text encoder route is the most defensible test, because it is the only one with a measured 24 GB success.
  - Expect ~12 GB max RSS (peak footprint likely higher, not reported).
  - Expect ~23 min per 5.17 s clip at 768x448 on an M4 Pro, and perhaps ~8–12 min for a 56-frame clip [EST].
  - SSD streaming speed will depend on the external drive. h3.c measured 13–14.6 GiB/s on internal SSD, and external drives are slower.
- **Not worth testing on this Mac:**
  - FastH3 Omni: NVIDIA formats, ref2v only, BF16 checkpoint ~40–66 GB [EST].
  - Pika H3 Flex: H100-validated, needs the full base model.
  - mlx-h3: 70 GiB default budget, 8-bit text encoder.
  - PipeNetwork: tested only on a 550 GB M3 Ultra, no quantized text encoder.
  - ddalcu mlx-serve: 66–77 GB peaks.
- **Overall:** if the goal is a production-speed upgrade over LTX-2.5 on 24 GB, the H3 family is unlikely to deliver it in Oct 2026. If the goal is checking whether H3 follows prompts and motion directions better than LTX, one small 2.3 s run via ComfyUI GGUF is a reasonable, low-cost probe. Before any business use, check the license (US$20M authorization clause).

### Gaps
- **No measured M5 Pro 24 GB run of any route.**
- No measured peak memory for the GGUF route.
- The 4-bit text encoder's size and quality (Argus) are unknown.
- Turbo LoRA quality and licenses are unknown.
- Unknown whether the 2.3 s / 56-frame clips (below the "intended" 4–15 s range) degrade H3's motion quality. h3.c and Bambushu ran 22-frame clips, but no quality assessment was published.
