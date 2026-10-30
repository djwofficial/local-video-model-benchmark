# Visual inspection of actual decoded outputs

Inspected six-keyframe contact sheets (`output/*-contact.jpg`) of all three measured seeds, plus an HSV red-blob check over all 49 decoded MP4 frames. Limited prompt/seed evaluation, not an overall model ranking. All MP4 outputs decode 49 frames at 512×320, 25 FPS. Round 1 settings (original prompt with "slowly"). Measured on AC power with Low Power Mode off.

- Seed 42: one ball enters from the right and rolls to the left until it leaves the frame (centroid x 0.99→0.01 of the width). Wrong direction.
- Seed 43: one ball at the left of the table stays nearly still.
- Seed 44: one round red ball enters from the left edge and rolls steadily to the right (x 0.01→0.67). Passes.

Narrow task result: 1/3, in line with the ~27–30% direction-following rate reported for LTX-2.3 text-to-video. Scenes are photorealistic (wooden table, beige wall, window), far cleaner than LTX-Video 2B or Wan at this size.
