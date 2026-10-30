# LTX-2.3 + keyframes: memory / size ladder

Limit for "fits": sampled process phys_footprint ≤ 19.0 GiB and warm-run swap growth ≤ 2 GiB. Seed 42 cold (includes text encoding), seed 43 warm. AC power, M4 Pro 24 GB.

|Config (W×H×frames)|Runs OK|Peak process GiB|Warm-run process GiB|MLX peak GiB|Warm swap Δ GiB|Warm s/video|Fits 24 GB|
|---|---|---:|---:|---:|---:|---:|---|
|768x512x49|yes|14.58|5.85|14.22|-0.80|130.515|yes|
|960x640x49|yes|14.58|5.57|14.22|-0.57|209.623|yes|
|1152x768x49|yes|14.57|5.64|14.22|-0.55|302.48|yes|
|1344x896x49|yes|14.61|6.96|14.22|-0.75|427.389|yes|
|1536x1024x49|yes|14.57|8.66|14.22|-0.45|596.541|yes|
|768x512x97|yes|14.59|9.89|14.25|-0.27|237.901|yes|
|768x512x121|yes|14.61|7.98|14.22|-0.10|288.089|yes|
|768x512x145|yes|14.56|9.26|14.22|-0.73|376.777|yes|
|1536x1024x97|yes|14.60|13.74|14.22|1.15|1199.462|yes|

Correction (30 Oct 2026): the 19.0 GiB limit above mixed up units. macOS recommends at most 19,069,665,280 bytes = 19.07 GB = **17.76 GiB** of GPU working set on this 24 GB Mac (`ltx23-mlx/runtime-stats.json`); MLX's own memory limit here is 22.8 GiB (95% of RAM). Every case's sampled peak (max 14.61 GiB) is also below 17.76 GiB, so the "Fits 24 GB" column does not change. `benchmark.py` is kept as it ran.
