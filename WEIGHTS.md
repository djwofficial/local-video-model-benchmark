# Model weights

**Why the weights are not in this repository:**
- Each weight file is 0.5–11 GB. GitHub accepts at most 100 MB per file, or 2 GB per file with Git LFS on the free plan.
- The LTX-2.5 weights are gated: everyone who downloads them has to accept the terms on Hugging Face.

Download them from the original sources below. Each manifest lists every file with its SHA-256 checksum.

| Setup | Source (Hugging Face) | Size | Manifest |
|---|---|---:|---|
| LTX-2.3 distilled MLX 4-bit | `dgrauet/ltx-2.3-mlx-q4` + `mlx-community/gemma-3-12b-it-4bit` | 28.1 GB | [`experiments/ltx23-mlx/models-sources.json`](experiments/ltx23-mlx/models-sources.json) |
| LTX-2.5 distilled MLX 4-bit (gated) | `dgrauet/ltx-2.5-mlx-q4` @ `e9a20add` | 28.8 GB | [`experiments/ltx25-mlx/models-sources.json`](experiments/ltx25-mlx/models-sources.json) |
| Kandinsky 6.0 Lite distill | `kandinskylab/Kandinsky-6.0-Lite-distill-5s-Diffusers` @ `4c487e8b` | 24.5 GB (no audio) | [`experiments/round6/kandinsky6-lite-redball/PROVENANCE.md`](experiments/round6/kandinsky6-lite-redball/PROVENANCE.md) |
| LTX-Video 2B v0.9.5 (ComfyUI baseline) | `Lightricks/LTX-Video` + T5-XXL text encoder | 15 GB | [`baseline/models-sources.json`](baseline/models-sources.json) |
| Other tested models (LTX-Video 2B distilled, Wan 2.1, Wan 2.2) | See recovery URLs | — | [`experiments/retired-candidate-cache.json`](experiments/retired-candidate-cache.json) |

## Download

You need the Hugging Face CLI (`pip install huggingface_hub`). For LTX-2.5, first accept the terms on its model page, then run `hf auth login`.

LTX-2.3 (used by `experiments/mac-mini-recipe/`):

```bash
hf download dgrauet/ltx-2.3-mlx-q4 --include "*.json" "connector.safetensors" "transformer-distilled-1.1.safetensors" "spatial_upscaler_x2_v1_1.safetensors" "vae_decoder.safetensors" "vae_encoder.safetensors" --local-dir model
hf download mlx-community/gemma-3-12b-it-4bit --local-dir gemma
```

LTX-2.5. The script downloads only the files the distilled pipeline needs and checks every SHA-256:

```bash
python experiments/ltx25-mlx/download_ltx25.py
```

Kandinsky 6.0 Lite distill, without the audio parts:

```bash
hf download kandinskylab/Kandinsky-6.0-Lite-distill-5s-Diffusers --revision 4c487e8b4aeeb9059e5a77905aa2ddb59ec28f81 --exclude "audio_vae/*" "vocoder/*" "assets/*" --local-dir kandinsky6-lite
```

**Licenses:**
- LTX-2.3 and LTX-2.5: LTX-2 Community License.
- Gemma: Gemma Terms of Use.
- Kandinsky 6.0: MIT.

Check each license before redistributing weights.
