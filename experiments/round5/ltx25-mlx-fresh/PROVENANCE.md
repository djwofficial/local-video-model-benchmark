# Provenance

Round 5 fresh-process memory test (30 Oct 2026, added by Claude, user request): LTX-2.5 distilled MLX int4, same settings and prompts as ../ltx25-mlx-redball and ../ltx25-mlx-bluecar, but every video (seeds 42-44 per prompt) runs in its own process with no warm-up, so each video includes loading the text encoder. fresh_case.py is ../ltx25-mlx-redball/benchmark.py with the prompt and seed taken from the command line and a single run.
