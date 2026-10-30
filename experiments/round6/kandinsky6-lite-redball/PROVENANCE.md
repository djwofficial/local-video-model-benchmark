# Provenance

Round 6 (31 Oct 2026, added by Claude, user request): Kandinsky 6.0 Lite distill 5s (kandinskylab, MIT, revision 4c487e8b), Diffusers 0.42.1 + PyTorch 2.15 MPS in /Users/dyn/AI/venvs/kandinsky. Red-ball prompt (same text as round 2/5), text only, 768x512, 49 frames, 10 steps, guidance 1.0, no audio. Two phases: encode.py (text encoders only, saves embeddings) then benchmark.py (video model + VAE).

# Stopped and cleaned (31 Oct 2026, user request)

Run 2 (cache release between denoise and decode) was stopped by the user before finishing. The Kandinsky weights (/Users/dyn/AI/kandinsky6-lite/model, 23 GB) and its Python env (/Users/dyn/AI/venvs/kandinsky) were moved to the macOS Trash. Kept: scripts, logs, encode result, embeds.pt and the two run-1 videos (run1-as-is/output).
