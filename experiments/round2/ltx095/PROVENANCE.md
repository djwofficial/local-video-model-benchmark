# LTX-Video 2B v0.9.5 — round 2 (settings change approved by the user)

Same checkpoint, T5 text encoder, official workflow, sampler (res_multistep), 30 steps, CFG 3, LTXV scheduler values, negative prompt, seeds (cold smoke 41 at 25 frames, warm-up 41 and measured 42/43/44 at 49 frames) and 25 FPS as round 1 in `/Users/dyn/AI/ltx-benchmark-2026-10-29`.

Changed only:
1. Positive prompt: "slowly" removed and the motion stated explicitly ("rolls from the left side to the right side of a wooden table, moving steadily across the whole table until it reaches the right edge"). The rest of the prompt is unchanged.
2. Resolution 768×512 (LTX-Video's recommended size) instead of 512×320.

Purpose: find a model that passes the narrow task (exactly one red ball rolls left to right and stays round) on all three measured seeds on a 24 GB Mac; the target machine is an M5 Pro Mac mini with 24 GB. Power conditions are recorded with every run.
