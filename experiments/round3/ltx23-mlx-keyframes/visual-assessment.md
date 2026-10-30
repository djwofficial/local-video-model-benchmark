# Visual inspection of actual decoded outputs (round 3: keyframe anchors)

Reviewed frames 1, 13, 25, 37 and 49 of all nine measured seeds (42–50) side by side, the six-keyframe contact sheets, and an HSV red-blob check over all 49 decoded frames of each clip. Settings: round-2 prompt and size (768×512, 49 frames, 25 FPS) plus a hard start anchor (ball on the left) and a soft end anchor (ball on the right) cut from the passing round-2 clip of seed 47. AC power.

- All nine seeds: one round red ball rolls steadily from the left (centroid x 0.19) to the right (x 0.91) of the same table scene; the ball is found in all 49 frames and never moves backwards. No cross-fade, ghost or duplicate ball.
- The checker's occasional second region (1–3 frames in seeds 44, 47, 50; about 300 px) is a thin reddish strip on the table edge or a piece of the ball's own shadow/reflection, not a second ball.

Narrow task result: 9/9 (seeds 42–44: 3/3). Against round 2 without anchors (8/9 on the same seeds), the anchors remove the remaining wrong-direction case (seed 46). The trade-off: the scene and the ball's start and end positions are fixed by the anchor images, so every clip shows the same table; only the motion in between is generated.

Timing 129.52–139.91 s per video (mean of seeds 42–44: 132.22 s) after a 143.64 s warm-up. Memory: MLX peak 14.22 GiB during the first text encoding and 9.19 GiB during generation; process phys_footprint peaked at 14.63 GiB over the whole process and 5.1–7.5 GiB within each warm run.
