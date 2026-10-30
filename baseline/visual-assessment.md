# Visual assessment — one prompt, short clips

Scores are 1–5, higher is better. Assessment uses six decoded keyframes per clip and full-frame decoding/statistics, rather than real-time playback. Flicker/temporal ratings are provisional with this method.

| Seed / frames | Prompt adherence | Shape/color consistency | Motion | Flicker/distortion | Observation |
|---|---:|---:|---:|---:|---|
| 41 / 25 smoke | 2 | 5 | 1 | 4 | Red round ball, wooden table and beige wall; very little translation, so the intended roll is not established by this short smoke clip. |
| 42 / 49 | 2 | 5 | 1 | 4 | Small red ball near the right edge remains almost stationary. Window is on the right. |
| 43 / 49 | 4 | 5 | 4 | 4 | Ball moves visibly left to right across the table; maintains its round shape and red color. Best prompt following of these measured seeds. |
| 44 / 49 | 2 | 5 | 1 | 4 | Large red ball remains nearly stationary; slight surface/highlight changes. |

The pipeline successfully generates readable animation/video. Desired motion is inconsistent across seeds; these short tests do not establish general model quality.

All benchmark WebM files decode to 49 frames at 25 FPS (1.96 seconds). The seed42 WebP contains 34 stored frames and seed44 WebP contains 47, each retaining a total duration of 1960 ms. Use the WebM files for frame-count comparisons. The 25-frame smoke WebM and WebP both decode correctly.
