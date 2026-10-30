# Visual inspection of actual decoded outputs (round 2)

Inspected six-keyframe contact sheets (`output/*-contact.jpg`) of all three measured seeds; the WebP files coalesce repeated frames (44, 24 and 47 stored frames), which itself shows how little changes. Round 2 settings: prompt without "slowly" and with explicit left-to-right motion, 768×512. Measured on AC power with Low Power Mode off.

- Seed 42: one ball near the right edge shifts slightly, then disappears before the end.
- Seed 43: no ball appears; the table stays empty (mean absolute frame difference 0.10).
- Seed 44: one ball in the centre stays still (mean absolute frame difference 0.11).

Narrow task result: 0/3, against 1/3 in round 1. The prompt and resolution change did not make LTX-Video 2B v0.9.5 follow the motion instruction.
