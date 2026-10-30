# Interrupted smoke at Codex→Claude handoff

The Codex serial controller started the Wan 2.1 cold smoke (25 frames, seed 41) at the handoff boundary and Codex stopped it at sampling step 3/30 (about 9.7 s/step) before completion. No result row was written. This is a controller stop, not a model or runtime failure.

Files here are copies made by Claude before re-running the same smoke, because the re-run overwrites `smoke-run.log`, the smoke events file and the smoke workflows in place. `server.log` and `memory-samples.jsonl` are append-only and still contain the interrupted session.
