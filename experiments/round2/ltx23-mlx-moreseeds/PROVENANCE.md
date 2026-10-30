# LTX-2.3 distilled MLX 4-bit — round 2 settings on extra seeds

Identical to `../ltx23-mlx` (round 2: prompt without "slowly" and with explicit left-to-right motion, 768×512, 49 frames, 25 FPS, DistilledPipeline 8 + 3 steps with 2× spatial upscale, low-RAM streaming, audio off, weights from `../../ltx23-mlx`). Runs a 49-frame warm-up (seed 41) and then seeds 45–50, to check that the 3/3 on seeds 42–44 is not luck.

Added measurements: per-run maximum of the 1 Hz sampled MLX peak (`mlx_peak_sampled_max_bytes`; the old `mlx_peak_active_bytes` field covers only the VAE decode because the pipeline resets the peak there), per-run maximum of the sampled process phys_footprint and the process lifetime maximum phys_footprint (`claude_memprobe.py`, proc_pid_rusage V4), which is what has to fit in 24 GB of unified memory.
