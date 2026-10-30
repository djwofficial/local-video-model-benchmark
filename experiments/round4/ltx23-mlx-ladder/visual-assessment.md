# Round 4 ladder: does the ball still roll correctly?

Task: exactly one red ball rolls left → right and stays round, without leaving the frame or reversing direction.
Evidence: five-frame strips of every video (`output/*-strip.jpg`), denser strips for borderline cases, and
`check_ball.py` (HSV red-blob over every frame, `ball-check.json`). Details per video in `visual-task-results.json`.

| Config (W×H×frames) | Memory fits 24 GB | Correct | Notes |
|---|---|---:|---|
| 768×512×49 (recipe) | yes | 2/2 | clean |
| 960×640×49 | yes | 2/2 | clean |
| 1152×768×49 | yes | 2/2 | clean |
| 1344×896×49 | yes | 1/2 | seed 42 overshoots past the right edge, then rolls back in to the end keyframe |
| 1536×1024×49 | yes | 2/2 | clean |
| 768×512×97 | yes | 0/2 | ball reaches the right side halfway, then rolls back or leaves the frame |
| 768×512×121 | yes | 1/2 | seed 42 leaves the frame for 29 frames; seed 43 reaches the right and rests |
| 768×512×145 | yes | 1/2 | seed 42 rolls right, back left, and right again; seed 43 reaches the right and rests |
| 1536×1024×97 | yes | 0/2 | seed 42 rolls back; seed 43 loses the ball for 23 frames |

## Reading

- **Memory is not the limit.** Every case fits (peak ≈ 14.6 GiB, set by the text encoder at start-up).
- **Resolution at 2 s is fine:** 9/10 correct up to 1536×1024. The one miss (1344×896, seed 42) is a small overshoot at the edge.
- **Longer clips break the task:** 2/8 correct at 97–145 frames. The keyframes fix only the first and last frame. The model still finishes the roll in about 2 s, then fills the remaining time by rolling back, leaving the frame or losing the ball, before the end keyframe pulls it back. Longer clips would need extra keyframes in the middle (or a slower-motion prompt). That was not tested here.
- Only two seeds per configuration (42 cold, 43 warm), so these are spot checks, not pass rates.
