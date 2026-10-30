# Red-ball video on a 24 GB Mac mini: verified recipe

Model: **LTX-2.3 distilled, MLX 4-bit** (`dgrauet/ltx-2.3-mlx-q4`) with the Gemma 3 12B 4-bit text encoder, run by `ltx-2-mlx` (github.com/dgrauet/ltx-2-mlx) at commit `895201df379b079c2154738bcf92005b7a371923` (v0.18.0), MLX 0.32.4, Python 3.12.

Settings: `DistilledPipeline` (8 steps at 384×256, 2× spatial latent upscale, 3 steps at 768×512), 49 frames at 25 FPS (1.96 s), low-RAM block streaming, audio off, the prompt in `generate_red_ball.py` (no "slowly"; the left-to-right motion stated explicitly), and by default two keyframe anchors from `anchors/`: `start-ball-left.png` pins frame 0 and `end-ball-right.png` guides the last frame (both cut from a passing generated clip, seed 47).

## Evidence (MacBook Pro M4 Pro, 24 GB, AC power, 29–30 Oct 2026)

**With keyframes (default): 9 of 9 seeds correct (42–50)**, every clip one round ball rolling from x 0.19 to 0.91 of the frame with no ghost or duplicate ball. Mean 132.2 s per video (seeds 42–44) after the first load; peak process memory 14.6 GiB. Review: `../round3/ltx23-mlx-keyframes/visual-assessment.md`. Trade-off: every clip shows the same table, and the ball starts and ends at the anchored positions.

Without keyframes (`--no-keyframes`, pure text-to-video):

- Seeds 42, 43, 44: **3 of 3 correct** (exactly one round red ball rolls left to right). Videos and review: `../round2/ltx23-mlx/output`, `../round2/ltx23-mlx/visual-assessment.md`.
- Mean 108.97 s per video after the first load; MLX memory peaks at 14.2 GiB while the Gemma text encoder runs and 9.2 GiB during generation.
- Extra seeds 45–50 with the same settings: **5 of 6 correct** (seed 46 rolled towards the camera instead), so 8 of 9 seeds overall (≈ 89% per seed). Mean 112.6 s per video. Peak process memory (phys_footprint) 14.6 GiB at the first load, 5.6–6.3 GiB per later run: comfortably inside 24 GB. Details: `../round2/ltx23-mlx-moreseeds/visual-assessment.md`.
- The same model with the old prompt at 512×320 got only 1 of 3, and older models (LTX-Video 2B, Wan 2.1, Wan 2.2) got 0–1 of 3: see `../RESULTS.md`.

## Setup on the Mac mini

1. Install uv and Python 3.12 (`uv python install 3.12`).
2. Get the runtime at the tested commit:
   `git clone https://github.com/dgrauet/ltx-2-mlx && git -C ltx-2-mlx checkout 895201df379b079c2154738bcf92005b7a371923`
3. Create the environment and install it:
   `uv venv --python 3.12 ltx-mlx && uv pip install --python ltx-mlx/bin/python -e ltx-2-mlx/packages/ltx-core-mlx ltx-2-mlx/packages/ltx-pipelines-mlx av imageio-ffmpeg psutil`
   (exact versions used here: `../ltx23-mlx/requirements-lock.txt`).
4. Weights, 28.1 GB in total; easiest is to copy the two folders from this Mac: `../ltx23-mlx/model` → `model/` and `../ltx23-mlx/gemma` → `gemma/` next to this README (they include the configuration and tokenizer files). From Hugging Face instead:
   - `dgrauet/ltx-2.3-mlx-q4`: `connector.safetensors` (6.34 GB), `transformer-distilled-1.1.safetensors` (11.32 GB), `spatial_upscaler_x2_v1_1.safetensors` (1.00 GB), `vae_decoder.safetensors` (0.81 GB), `vae_encoder.safetensors` (0.64 GB) plus the repo's `*.json` configuration files;
   - `mlx-community/gemma-3-12b-it-4bit`: both `model-0000x-of-00002.safetensors` shards (5.37 + 2.66 GB) plus its tokenizer and configuration files.
   SHA-256 of every weight file: `../ltx23-mlx/models-sources.json`.
5. Keep about 5 GB of disk free beyond the weights for macOS swap.

## Run

```sh
ltx-mlx/bin/python generate_red_ball.py --seed 42 --out red-ball-seed42.mp4
```

Seeds 43 and 44 the same way; add `--no-keyframes` for pure text-to-video, or `--size` for a larger tested resolution (see below). On this Mac the script reproduces the verified videos exactly in both modes (seed 42: 0.000 mean pixel difference over all 49 frames; 143 s with keyframes and 119 s without, both including the first load; peak process memory 14.6 GiB). It writes the MP4 with `ffmpeg` from PATH, or with the binary bundled in `imageio-ffmpeg` when none is installed. Without keyframes about 1 seed in 9 goes the wrong way, so look at each new video and rerun a failure with another seed. Each run prints the elapsed time and the peak process memory (`phys_footprint`, the figure Activity Monitor shows, GPU buffers included). The first run of a process also loads the text encoder, so it is slower and uses more memory.

## Larger sizes and longer clips (round-4 ladder, 30 Oct 2026)

These are the same settings with keyframes. Each configuration ran in its own process with seed 42 (cold) and seed 43 (warm). Details are in `../round4/ltx23-mlx-ladder/LADDER.md` and `visual-assessment.md`.

| Size × frames | Peak process GiB | 2nd-video GiB | s per video | Ball correct |
|---|---:|---:|---:|---:|
| 768×512 × 49 (default) | 14.58 | 5.85 | 131 | 2/2 |
| 960×640 × 49 | 14.58 | 5.57 | 210 | 2/2 |
| 1152×768 × 49 | 14.57 | 5.64 | 302 | 2/2 |
| 1344×896 × 49 | 14.61 | 6.96 | 427 | 1/2 |
| 1536×1024 × 49 | 14.57 | 8.66 | 597 | 2/2 |
| 768×512 × 97 | 14.59 | 9.89 | 238 | 0/2 |
| 768×512 × 121 | 14.61 | 7.98 | 288 | 1/2 |
| 768×512 × 145 | 14.56 | 9.26 | 377 | 1/2 |
| 1536×1024 × 97 | 14.60 | 13.74 | 1199 | 0/2 |

- **Memory is not the limit.** Every case stays under 17.8 GiB (19.07 GB), the most GPU memory macOS recommends on a 24 GB Mac (MLX itself refuses to go past 22.8 GiB, 95% of RAM). Swap did not grow. The peak (about 14.6 GiB) comes from loading the text encoder, not the video size.
- **Safe range for the Mac mini:** 49 frames at any size up to 1536×1024, chosen with `--size`, for example `--size 1152x768`. Bigger sizes only cost time. Keep 768×512 unless you need the extra resolution.
- **Do not make longer clips with this recipe.** At 97–145 frames, the keyframes pin only the first and last frame. The ball rolls across in about 2 s and then rolls back, leaves the frame or disappears, so only 2 of 8 videos were correct. The script therefore stays at 49 frames.
- Only two seeds per size were tested, so treat these as spot checks.
- `--size` other than 768×512 was tested only with keyframes.

## M5 Pro notes

Same weights, same memory use. MLX uses the M5 GPU neural accelerators on macOS 26.2 or later, so generation should be faster than on the M4 Pro (estimate, not measured). Use MLX 0.32.4 or newer: older MLX builds had a bf16 matrix-multiply bug on M5 (ml-explore/mlx#3797). Pixel-exact results can differ between chips, so check the first videos there; if a seed misbehaves, try the next seed.
