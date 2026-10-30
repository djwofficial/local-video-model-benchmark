# Visual inspection of actual decoded outputs (round-2 settings, seeds 45–50)

Inspected six-keyframe contact sheets (`output/*-contact.jpg`) of all six seeds, plus an HSV red-blob check over all 49 decoded MP4 frames. Settings identical to `../ltx23-mlx` (768×512, prompt without "slowly" and with explicit motion). AC power.

- Seeds 45, 47, 48, 50: the table is empty at first; one round red ball enters from the left edge and rolls right across the table, reaching or leaving the right edge (centroid x from about 0.01–0.02 to 0.88–0.96).
- Seed 49: one round red ball rolls from the left to the right and slightly towards the camera (x 0.01→0.79).
- Seed 46: one ball rolls towards the camera and slightly to the left on a reddish table; no left-to-right roll. Fails. (The automatic blob check is unreliable on this clip because the table itself passes the red mask.)

Narrow task result: 5/6. Together with seeds 42–44 (3/3), the round-2 settings pass 8 of 9 seeds.

Timing 109.98–115.36 s per video (mean 112.57 s) after a 126.44 s warm-up that also loads the Gemma text encoder. Memory: MLX peak 14.22 GiB during the first text encoding and 9.19 GiB during generation; process phys_footprint (Activity Monitor's figure, GPU buffers included) peaked at 14.59 GiB over the whole process and at 5.6–6.3 GiB within each warm run. System swap grew by 6.1 GiB during the first load only.
