# Visual inspection of actual decoded outputs (round 2)

Inspected six-keyframe contact sheets (`output/*-contact.jpg`) of all three measured seeds, plus an HSV red-blob check over all 49 decoded MP4 frames (frames 1/13/25/37/49 of seed 42 inspected with blob boxes). All MP4 outputs decode 49 frames at 768×512, 25 FPS. Round 2 settings: prompt without "slowly", motion stated explicitly ("moving steadily across the whole table until it reaches the right edge"), 768×512. Measured on AC power with Low Power Mode off.

- Seed 42: one round red ball starts at the far left of the table and rolls to the right and towards the camera (centroid x 0.08→0.42). The checker's second red-ish region is the static dark-red door frame at the top left, not a second ball.
- Seed 43: the table is empty at first; one round red ball enters from the left edge and rolls steadily to the right (x 0.00→0.47). Slight camera drift, which the narrow task does not score.
- Seed 44: one round red ball enters from the left and rolls right across the whole table until it leaves the frame at the right edge (x 0.02→0.97).

Narrow task result: 3/3. In two of three clips the ball enters from the left edge instead of starting on the table, and it never ends exactly at the right edge; the criterion (exactly one red ball visibly moving left to right and staying round) is met in all three.
