# Round 2: settings tuned to find a 3/3 model

The user approved changing the test settings after round 1 (29 Oct 2026): the prompt drops "slowly" and states the left-to-right motion explicitly, and each model runs at its native or recommended resolution. Sampler, steps, CFG, negative prompt, seeds, frame counts and FPS stay as in round 1, so round 1 and round 2 differ only in prompt and resolution. Round 1 results are untouched in their own folders.

Each subfolder is a self-contained ComfyUI candidate (run_server.py, benchmark.py, verify_outputs.py, PROVENANCE.md, logs, output, results.jsonl) and is run with `claude_comfy_tests.py round2/<model> smoke,bench` or through `claude_queue.py`.
