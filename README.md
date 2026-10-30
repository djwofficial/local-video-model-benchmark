# Local text-to-video benchmark on a 24 GB Mac

**Question:** which local video model can make one simple prompt correctly every time, within 24 GB of unified memory? The target machine is a Mac mini M5 Pro (24 GB).

**Prompt:** a single red ball rolls from left to right across a wooden table. A video counts as correct when exactly one ball visibly rolls left → right and stays round.

**Test setup:**
- MacBook Pro M4 Pro, 24 GB, macOS 27.
- Every run was local and offline, 29–30 Oct 2026.
- Every number below was measured on this Mac; none were copied from elsewhere.

## Answer

Use **LTX-2.3 distilled (MLX 4-bit) with start and end keyframes**:
- **9 of 9 seeds correct**;
- **about 132 s per video**;
- **peak process memory 14.6 GiB**.

| Part | Details |
|---|---|
| Model | [`dgrauet/ltx-2.3-mlx-q4`](https://huggingface.co/dgrauet/ltx-2.3-mlx-q4) |
| Text encoder | [`mlx-community/gemma-3-12b-it-4bit`](https://huggingface.co/mlx-community/gemma-3-12b-it-4bit) |
| Runtime | [ltx-2-mlx](https://github.com/dgrauet/ltx-2-mlx) at commit `895201df379b079c2154738bcf92005b7a371923` |
| Output | 768×512, 49 frames (2 s), 25 FPS |
| Keyframes | One still pins the first frame (ball on the left); another guides the last frame (ball on the right) |

- **Ready-to-run script for the Mac mini:** [`experiments/mac-mini-recipe/`](experiments/mac-mini-recipe/). It covers setup, the weights list with SHA-256 checksums, and `generate_red_ball.py`.
- **Slides:**
  - [`deck/Local-video-model-summary-M4-Pro.pptx`](deck/Local-video-model-summary-M4-Pro.pptx): a 3-slide summary of the setup that passed every seed (the table, its videos with what the name means, and how big it can go on 24 GB).
  - [`deck/Local-video-model-comparison-M4-Pro-rev7.pptx`](deck/Local-video-model-comparison-M4-Pro-rev7.pptx): every configuration in the mentor's table format, with videos embedded.

## Every configuration tested

| Model | Weights | Settings | Power | Mean s/video | Memory GiB¹ | Correct |
|---|---|---|---|---:|---:|---:|
| LTX-Video 2B v0.9.5 | BF16 | 512×320, original prompt | battery² | 78.84 | 8.15 | 1/3 |
| LTX-Video 2B distilled v0.9.6 | BF16 | 512×320, original prompt | battery² | 16.55 | 8.15 | 0/3 |
| Wan 2.1 T2V 1.3B | FP16 | 512×320, original prompt | battery² | 825.73 | 11.16 | 0/3 |
| LTX-2.3 distilled | MLX 4-bit | 512×320, original prompt | AC | 52.67 | 7.68 | 1/3 |
| Wan 2.2 TI2V 5B | FP16 | 512×320, original prompt | AC | 274.06 | 14.94 | 1/3 |
| LTX-Video 2B v0.9.5 | BF16 | 768×512, new prompt | AC | 142.91 | 15.12 | 0/3 |
| LTX-2.3 distilled | MLX 4-bit | 768×512, new prompt | AC | 108.97 | 9.19 | 3/3 (8/9 over seeds 42–50) |
| **LTX-2.3 distilled + keyframes** | MLX 4-bit | 768×512, new prompt, start + end keyframes | AC | 132.22 | 9.19 | **9/9** |

¹ The memory column uses different counters per runtime:
- ComfyUI rows: the mean of each run's sampled maximum MPS driver allocation.
- MLX rows: the mean of each run's sampled MLX peak.

Neither counter is total RAM. For the process peak that Activity Monitor shows (GPU buffers included), see the ladder below; it is 14.6 GiB for the MLX setup.

² The battery runs used Low Power Mode, so times are only comparable within one power condition.

"New prompt" drops the word "slowly" and states the motion explicitly. Details: [`experiments/RESULTS.md`](experiments/RESULTS.md).

## How big can it go on 24 GB? (round 4)

The keyframe setup was run at larger sizes and longer clips, one process per size, with seed 42 (cold) and seed 43 (warm).

| Size × frames | Peak GiB | 2nd-video GiB | s/video | Correct |
|---|---:|---:|---:|---:|
| 768×512 × 49 | 14.58 | 5.85 | 131 | 2/2 |
| 960×640 × 49 | 14.58 | 5.57 | 210 | 2/2 |
| 1152×768 × 49 | 14.57 | 5.64 | 302 | 2/2 |
| 1344×896 × 49 | 14.61 | 6.96 | 427 | 1/2 |
| 1536×1024 × 49 | 14.57 | 8.66 | 597 | 2/2 |
| 768×512 × 97 | 14.59 | 9.89 | 238 | 0/2 |
| 768×512 × 121 | 14.61 | 7.98 | 288 | 1/2 |
| 768×512 × 145 | 14.56 | 9.26 | 377 | 1/2 |
| 1536×1024 × 97 | 14.60 | 13.74 | 1199 | 0/2 |

- **Every size fits.** macOS recommends at most 17.8 GiB (19.07 GB) of GPU memory on a 24 GB Mac.
- **The peak is the same for every size.** It comes from loading the text encoder at start-up.
- **Keep clips at 49 frames (2 s).** Longer clips mostly fail: the keyframes fix only the first and last frame, so the ball crosses in about 2 s and then rolls back or leaves the frame.
- With two seeds per size, these are spot checks, not pass rates.

Details: [`experiments/round4/ltx23-mlx-ladder/`](experiments/round4/ltx23-mlx-ladder/).

## What is in this repository

| Folder | Contents |
|---|---|
| `experiments/` | One folder per model or round. Each has a `benchmark.py`, `results.jsonl` (raw timings, memory and power per run), `output/` (MP4s and contact sheets), `visual-assessment.md` and `visual-task-results.json` (the verdict per seed), and `logs/`. Also: `RESULTS.md`, `STATUS.md`, `summarize_results.py`, and the queue / battery-guard / memory-probe scripts (`claude_*.py`). |
| `experiments/ltx-distilled`, `wan21`, `wan22`, `ltx23-mlx` | Round 1: original prompt, 512×320. |
| `experiments/round2/` | New prompt, 768×512, including extra seeds 45–50. |
| `experiments/round3/ltx23-mlx-keyframes` | Keyframe anchors, seeds 42–50. |
| `experiments/round4/ltx23-mlx-ladder` | Memory and size ladder, plus `check_ball.py`. |
| `experiments/mac-mini-recipe/` | The standalone script and setup guide. |
| `baseline/` | The original LTX-Video 2B v0.9.5 ComfyUI benchmark that the comparison started from. |
| `deck/` | Both PowerPoints, plus the python-pptx scripts and assets (frames, H.264 copies of the videos) that build it. |
| `docs/HANDOFF.md` | Running notes from the whole project. |

**Left out:**
- **Model weights (about 26 GB).** Sources and checksums are in `experiments/models-sources.json`, `experiments/ltx23-mlx/download_ranges.py` and the recipe README.
- **The ltx-2-mlx and ComfyUI source code.** Get them from upstream at the versions named above.

The scripts use this Mac's absolute paths (`/Users/dyn/AI/...`), so adjust them before rerunning anything.
