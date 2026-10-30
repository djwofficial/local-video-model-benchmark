# LTX-2.3 distilled MLX 4-bit — round 2 (settings change approved by the user)

Same runtime (ltx-2-mlx v0.18.0, pinned commit in ../../ltx23-mlx/PROVENANCE.md), the same downloaded weights (read from `../../ltx23-mlx/model` and `../../ltx23-mlx/gemma`), native DistilledPipeline (8-step half-resolution stage, 2× spatial latent upscale, 3-step refine), low-RAM block streaming, audio disabled, seeds (smoke 41 at 25 frames, warm-up 41 and measured 42/43/44 at 49 frames) and 25 FPS as round 1.

Changed only:
1. Positive prompt: "slowly" removed and the left-to-right motion stated explicitly, as in round2/ltx095.
2. Output 768×512 (stage 1 at 384×256) instead of 512×320. Two-stage paths need multiples of 64; 768×512 is LTX's standard size and the size the runtime documents for its 24–32 GB `--low-ram` measurements.

Purpose: find a model that passes the narrow task on all three measured seeds on a 24 GB Mac (target: M5 Pro Mac mini 24 GB).
