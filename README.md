# Local text-to-video benchmark on a 24 GB Mac

**Goal:** find a local video model that renders the test prompts correctly every time, within 24 GB of unified memory.

| | |
|---|---|
| Test machine | MacBook Pro M4 Pro, 24 GB |
| Target machine | Mac mini M5 Pro, 24 GB |
| Dates | 29–31 Oct 2026 |
| Mode | Fully local and offline |
| Memory limit used | 17.8 GiB, the GPU memory macOS recommends on a 24 GB Mac |

## Result

| Use case | Setup | Correct | Time / video | Peak memory |
|---|---|---:|---:|---:|
| Highest reliability | **LTX-2.3 distilled (MLX 4-bit) + start/end keyframes** | 9/9 | 132 s | 14.6 GiB |
| Text only, newest model | **LTX-2.5 distilled (MLX 4-bit)** | 6/6 (2 prompts) | 172 s | 15.5 GiB |

- Both setups fit 24 GB. The Mac-mini script is in [`experiments/mac-mini-recipe/`](experiments/mac-mini-recipe/).
- **Slides:**
  - [`deck/LTX-2.3-vs-LTX-2.5-M4-Pro.pptx`](deck/LTX-2.3-vs-LTX-2.5-M4-Pro.pptx): latest comparison.
  - [`deck/Local-video-model-summary-M4-Pro-rev2.pptx`](deck/Local-video-model-summary-M4-Pro-rev2.pptx): summary deck.
  - [`deck/Local-video-model-comparison-M4-Pro-rev7.pptx`](deck/Local-video-model-comparison-M4-Pro-rev7.pptx): all models.

## LTX-2.3 vs LTX-2.5

Text only, 768×512, 49 frames, seeds 42–44.

| Model · prompt | Mean performance | Avg memory | Memory while making a video | Avg peak memory | Peak memory | Correct |
|---|---:|---:|---:|---:|---:|---:|
| LTX-2.3 · red ball | 108.97 s | 5.89 | 6.30 | 14.58* | 14.59 | 3/3 |
| LTX-2.3 · blue car | 109.64 s | 6.86 | 7.45 | 14.56* | 14.57 | 3/3 |
| LTX-2.5 · red ball | 175.14 s | 6.34 | 6.72 | 15.46 | 15.47 | 3/3 |
| LTX-2.5 · blue car | 168.30 s | 6.29 | 7.65 | 15.47 | 15.48 | 3/3 |

Memory columns are in GiB.

**How each column was measured:**
- **Mean performance:** average time per video, with the model and prompt already loaded.
- **Avg memory:** each video's highest memory when one run makes several videos from one prompt, averaged over the seeds. **Memory while making a video** is the highest of those.
- **Avg peak memory:** each video made in a fresh run that loads the model and reads the prompt, averaged over the seeds. Data: [`round5/ltx25-mlx-fresh`](experiments/round5/ltx25-mlx-fresh/FRESH.md).

\* These LTX-2.3 values are estimates. Its weights were removed before the fresh-run test, so they come from 12 earlier fresh LTX-2.3 runs, which measured 14.56–14.63 GiB.

**Prompts:**
1. Red ball: a single red ball rolls left → right across a wooden table.
2. Blue car: a small blue toy car drives right → left across a white desk.

Full texts are in the [deck](deck/LTX-2.3-vs-LTX-2.5-M4-Pro.pptx), with Traditional Chinese translations.

## All rounds

| Round | What changed | Outcome |
|---|---|---|
| 1 | 5 models, 512×320, original prompt | Best result 1/3 (LTX-Video 2B, LTX-2.3, Wan 2.2) |
| 2 | Clearer prompt, 768×512 | LTX-2.3 3/3 (8/9 over 9 seeds); LTX-Video 2B 0/3 |
| 3 | LTX-2.3 + start/end keyframes | 9/9 |
| 4 | Size ladder for LTX-2.3 + keyframes | Every size fits (peak ≈ 14.6 GiB). 2 s clips correct up to 1536×1024 (9/10); 4–6 s clips 2/8 |
| 5 | LTX-2.5 distilled, second prompt (blue car) | LTX-2.5 6/6, LTX-2.3 6/6. LTX-2.5 ≈ 1.6× slower, +0.9 GiB peak |
| 6 | Kandinsky 6.0 Lite distill (MIT), red ball | Not practical on 24 GB (see below); stopped |

Per-model numbers: [`experiments/RESULTS.md`](experiments/RESULTS.md). Each round folder has its scripts, raw results, videos and visual verdicts.

### Kandinsky 6.0 Lite (round 6)

Run with Diffusers on PyTorch MPS.

| Stage | Memory | Time |
|---|---:|---:|
| Read prompt (Qwen2.5-VL-7B text encoder) | 18.1 GiB peak, +8.8 GiB swap | 120 s |
| Denoise (3B model, 10 steps) | ~7 GiB of tensors | ~5 min |
| VAE decode | Driver memory up to 28.8 GiB, heavy swap | 520–928 s per video in total |

- Over the 17.8 GiB limit and 3–5× slower than LTX-2.5.
- The run was stopped after two videos, which were not reviewed for correctness.

## Other open models

The research report is [`docs/research/Model video layak diuji di Mac.md`](docs/research/Model%20video%20layak%20diuji%20di%20Mac.md), in Indonesian.

| Model | Maker | Verdict for a 24 GB Mac |
|---|---|---|
| HunyuanVideo 1.5 480p (4-step) | Tencent (China) | Worth a test via ComfyUI-GGUF; untested |
| Wan 2.2 TI2V-5B | Alibaba (China) | Fair retest with round-2 settings; untested |
| MiniMax H3 | MiniMax (China) | Quality reference only; ~23 min per clip on a 24 GB Mac |
| Kandinsky 6.0 Lite | Sber AI (Russia) | Tested in round 6: not practical |
| Kandinsky Pro, Cosmos 3, LongCat-Video, Helios, FastH3, Pika H3 Flex | — | Too large or NVIDIA-only |

## Licenses

| Model | License | Commercial terms |
|---|---|---|
| LTX-2.3 / LTX-2.5 | LTX-2 Community License | Free under US$10M yearly revenue (affiliates included); above that a paid agreement is needed |
| Kandinsky 6.0 | MIT | Free. Maker is Sber AI, so check compliance |
| Wan 2.2 | Apache-2.0 | Free |
| HunyuanVideo 1.5 | Tencent Hunyuan Community | Not valid in the EU, UK or South Korea; separate license above 100M MAU |
| MiniMax H3 | MiniMax H3 Community | Written authorization needed above US$20M revenue |

## Repository

| Path | Contents |
|---|---|
| `experiments/` | Benchmark scripts, raw results (`results.jsonl`), videos and verdicts, one folder per model or round |
| `experiments/mac-mini-recipe/` | Standalone LTX-2.3 + keyframes script and setup guide |
| `baseline/` | Original LTX-Video 2B ComfyUI benchmark |
| `deck/` | Slide decks and the python-pptx scripts that build them |
| `docs/research/` | Research report and notes on other models |
| `docs/HANDOFF.md` | Running project notes |

**Not included:**
- **Model weights.** Sources and checksums are in each folder's `models-sources.json`.
- **Third-party runtime code.** ltx-2-mlx is pinned at commit `895201d`.

All weights and Python environments were removed from the test Mac on 31 Oct 2026; videos and results are kept.
