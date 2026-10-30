# Visual inspection of actual decoded outputs

Inspected the six-keyframe contact sheets (`output/*-contact.jpg`) of the cold smoke, both warm-ups and all three measured seeds, plus frames 1, 25 and 49 decoded from the WebM files. This is a limited prompt/seed evaluation, not an overall model ranking. All WebM outputs decode 49 frames at 512×320, 25 FPS (cold smoke 25 frames).

- Smoke 41 (25 frames): red ball on a table in front of a window, nearly static. Strong magenta/red colour cast over the whole frame (mid-frame mean RGB about [185, 40, 88]); see `logs/interrupted-for-colour-check/README.md`.
- Warm-up 41 (49 frames, both server sessions): illustration-like style with natural colours; one red ball on a striped table, nearly static. Both warm-ups have identical frame statistics (mean absolute frame difference 2.1368), so the rerun reproduced the same output.
- Seed 42: one red ball starts on top of a striped box and drops down and to the left out of frame; a red ball rests at the lower left for the rest of the clip. Downward, right-to-left motion rather than a left-to-right roll; the wooden table is barely visible.
- Seed 43: one red ball floats at the right in frame 1, then a block and three floating rows made of dozens of small red beads fill the scene. Violates the single-ball instruction.
- Seed 44: cartoon-style room; a red cobblestone-like texture covers floor and walls, a red mesh shape appears and morphs into a cone, and a red ball appears floating only at the end. Violates the scene and motion instructions.

Narrow task result: 0/3 (`visual-task-results.json`). Wan 2.1 keeps its official sampling (30 steps, CFG 6, uni_pc), so its time is a pipeline-level comparison with the LTX rows, not an architecture-only one. The measured seeds ran on battery with Low Power Mode on while the charge fell from 43% to 14%; sampling slowed from about 26 to 34 s per step during the session.
