# LTX-2.3 distilled MLX 4-bit

Community runtime: https://github.com/dgrauet/ltx-2-mlx
Pinned runtime source:895201df379b079c2154738bcf92005b7a371923 (v0.18.0).
Weights: https://huggingface.co/dgrauet/ltx-2.3-mlx-q4
Text encoder: https://huggingface.co/mlx-community/gemma-3-12b-it-4bit
Exact selected files, byte counts and SHA-256 values in models-sources.json. Only the distilled1.1 transformer variant is selected; dev transformers and LoRAs excluded. All configuration/tokenizer files saved locally. Runtime offline during generation.

Native DistilledPipeline uses8steps at256×160, spatial2×latent upscale, then3steps at512×320. Final49frames25FPS; smoke25frames. Native Euler distilled sigma tables retained. Audio disabled to compare video generation. Low-RAM block streaming enabled for24GB Mac. MLX memory/cache safety limits are not raised; low-RAM runtime reduces cache limit to zero.

Small benchmark subclass caches identical prompt embeddings after cold smoke to match ComfyUI warm-prompt behavior. No changes to denoising, weights, decoder, sampling or low-memory model lifecycle. MP4 writing is included in timing; ComfyUI timings include WebP and WebM writing. Runtime/encoding/model residency differences remain part of end-to-end pipeline measurements, not isolated architecture speed.

MLX peak active allocation differs from PyTorch MPS driver allocation. Never add RSS to GPU counters or present either as whole-machine RAM. System swap deltas are logged separately. Battery/Low Power Mode conditions must be disclosed.
