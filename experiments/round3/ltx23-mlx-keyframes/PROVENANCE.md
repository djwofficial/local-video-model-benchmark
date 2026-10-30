# LTX-2.3 distilled MLX 4-bit — round 3: keyframe anchors (approved by the user)

Same as `../../round2/ltx23-mlx` (prompt without "slowly" and with explicit motion, 768×512, 49 frames, 25 FPS, DistilledPipeline 8 + 3 steps, low-RAM streaming, audio off, weights from `../../ltx23-mlx`), plus two image anchors through `ltx_pipelines_mlx.utils.types.ImageConditioningInput`:
- `anchors/start-ball-left.png`: frame 16 of the passing round-2 clip of seed 47 (one ball at x ≈ 98–193 px), `replace` at frame 0, strength 1.0;
- `anchors/end-ball-right.png`: frame 49 of the same clip (ball at x ≈ 662–736 px), `guide` at the last frame, strength 1.0.

Purpose: raise the per-seed success rate from 8/9 (round 2, seeds 42–50) toward 100% for this fixed prompt. Runs a warm-up (seed 41) and then seeds 42–50. Records the same memory fields as `../../round2/ltx23-mlx-moreseeds`.
