# Visual inspection of actual decoded outputs

Inspected six-keyframe contact sheets from the smoke and all three measured seeds. This is a limited prompt/seed evaluation, not an overall model ranking. All WebM outputs decode49frames at512×320,25FPS (cold smoke25frames). Animated WebP may coalesce identical frames; use WebM for fixed frame indexing.

- Smoke41: ball drifts slightly left, contrary to prompt direction. Unrequested garbled subtitle-like text appears along bottom.
- Seed42: original ball remains almost stationary; a second red ball emerges and moves right. Violates the single-ball instruction. Round shapes/red color broadly stable.
- Seed43: nearly static single red ball. Round shape/color stable; little visible displacement in inspected frames.
- Seed44: nearly static single red ball. Round shape/color stable; little visible displacement in inspected frames.

No clear improvement in instruction-following movement over baseline. Faster warm pipeline timing uses8steps/CFG1 rather than baseline30steps/CFG3; do not call this a controlled architecture-only speed comparison.
