# Visual inspection of actual decoded outputs

Inspected six-keyframe contact sheets (`output/*-contact.jpg`) of all three measured seeds. Limited prompt/seed evaluation, not an overall model ranking. All WebM outputs decode 49 frames at 512×320, 25 FPS (cold smoke 25 frames). Round 1 settings (original prompt, 512×320, well below this model's 1280×704 native size). Measured on AC power with Low Power Mode off, unlike the battery runs of the first three models.

- Seed 42: one red ball drops onto the table edge at the left and then moves clearly to the right along it, staying broadly round; slight wobble late in the clip. Red-pixel centroid moves right from x≈351 to x≈415. Passes the narrow task, although the ball enters from above rather than rolling the whole way.
- Seed 43: blurred, overexposed scene that drifts; a red blob appears and vanishes.
- Seed 44: a large translucent pink dome melts into a red smear; heavy artifacts.

Narrow task result: 1/3 (`visual-task-results.json`). Seeds 43 and 44 show the smearing typical of running far below native resolution.
