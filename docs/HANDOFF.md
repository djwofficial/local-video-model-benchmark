# Handoff: local video model comparison on this Mac

## Claude checkpoint — 30 Oct 2026

New goal from the user: one setup that makes the red-ball prompt correctly 3/3 on a **Mac mini M5 Pro, 24 GB**; any method, any time per video, only this prompt.

**Recommended (user asked for ~100%): round-2 settings plus start/end keyframe anchors**, 9/9 correct on seeds 42–50, 132.22 s per video, peak process memory 14.63 GiB (`round3/ltx23-mlx-keyframes`; default mode of `mac-mini-recipe/generate_red_ball.py`). Text only, **LTX-2.3 distilled MLX 4-bit with round-2 settings** (768×512, prompt without "slowly" and with the motion stated explicitly): 3/3 on seeds 42–44, 108.97 s per video on AC, MLX peak 14.2 GiB at first load / 9.2 GiB during generation. Folder `/Users/dyn/AI/video-model-comparison-2026-10-29/round2/ltx23-mlx`; extra seeds 45–50 in `round2/ltx23-mlx-moreseeds`; Mac mini recipe and standalone `generate_red_ball.py` in `mac-mini-recipe/`. Research behind it: open text-to-video models follow motion direction only ~27–30% of the time (CAPE-T2V, Aug 2026); if a seed fails on the Mac mini, the next fallbacks are start/end image anchors (`ImageConditioningInput`, no download) and the LTX-2.3 Union-Control IC-LoRA with a procedural depth video (654 MB).

**Memory / size ladder (round 4, `/Users/dyn/AI/video-model-comparison-2026-10-29/round4/ltx23-mlx-ladder`, keyframes, seeds 42 cold + 43 warm per size):** every size fits 24 GB (peak process memory ≈ 14.6 GiB for all, set by the text-encoder load; worst 2nd-video 13.7 GiB at 1536×1024×97; swap never grew). Ball correct: 49 frames at 768×512 / 960×640 / 1152×768 / 1536×1024 2/2 each, 1344×896 1/2 (overshoot at the edge); longer clips 97/121/145 frames at 768×512 0/2, 1/2, 1/2 and 1536×1024×97 0/2 (ball rolls back or leaves the frame after ~2 s, since only the first and last frame are anchored). Safe range for the Mac mini: 49 frames at up to 1536×1024 (`generate_red_ball.py --size`); 131 s → 597 s per video. Review: `round4/ltx23-mlx-ladder/visual-assessment.md`, checker `check_ball.py`.

Next agreed with the user: one different prompt (blue toy car right→left), text-only then new keyframes, seeds 42–44 (`round5/`, plan in `~/.claude/plans/coba-kamu-deep-research-generic-wave.md`). Not started yet.

**Round 5 (30 Oct 2026): LTX-2.5 distilled MLX int4 (`dgrauet/ltx-2.5-mlx-q4`, gated; files in `ltx25-mlx/`), text only, 768×512×49, seeds 42–44.** Red ball 3/3 (175 s/video), blue car (new prompt, right→left) 3/3 (168 s/video); peak process memory 15.45 GiB (text encoder Gemma-4 at start-up), 5.6–7.7 GiB while making a video, under the 17.8 GiB macOS GPU limit. LTX-2.3 on the blue car: 3/3, 110 s, 14.57 GiB peak (`round5/ltx23-mlx-bluecar`). Runs on battery (Low Power Mode off) except LTX-2.3 red ball (AC). The LTX-2.3 weights were retired with user approval to fit LTX-2.5 (checksums and recovery URLs in `retired-candidate-cache.json`); the Mac-mini recipe needs them re-downloaded. Research: LTX-2.5 Fast Elo 947 vs LTX-2.3 Fast 838 (Artificial Analysis); MiniMax H3 (1161) needs ~100 GB, not feasible. Deck: summary rev2 (slides 4–5).

All configurations: `RESULTS.md` (now with settings, power condition and task-pass columns). Deck: `benchmark-ppt/output/Local-video-model-comparison-M4-Pro-rev7.pptx`, built by `benchmark-ppt/build_simple_deck.py` after `summarize_results.py`, `extract_frames.py` and `make_videos.py`.

## Claude checkpoint — 29 Oct 2026, 16:50 CST

Wan 2.1 is fully measured: 825.729 s per 49-frame clip (seeds 852.447 / 770.932 / 853.808 s), sampled MPS driver maximum 11.163 GiB, narrow task 0/3. Claude interrupted its first server session 16 s into seed 42 for a colour check (the 25-frame smoke has a magenta cast; the 49-frame warm-up did not), then reran warm-up and seeds in a second session. Details: `wan21/logs/interrupted-for-colour-check/README.md`, `wan21/visual-assessment.md`.

Running serial controller: `claude_continue_remaining.py` (started with `6 30`), watched by `claude_battery_guard.py` at 6%. Order: Wan 2.2 download (running at 16:45) -> Wan 2.2 smoke + bench + verify -> retire completed Comfy candidate caches -> LTX-2.3 MLX download + benchmark + verify. On battery, GPU stages start only at 30% or more and downloads at 10% or more; below that the controller writes `waiting_for_charger` to `comparison-state.json` and continues once AC power is connected. A guard stop copies that stage's logs to `<model>/logs/battery-stop-<time>/` and repeats the stage after charging. Check `pgrep -fl 'claude_|run_server|benchmark.py|download_ranges'` before starting anything else.

Editable comparison deck: `benchmark-ppt/output/Local-video-model-comparison-M4-Pro-rev2.pptx`, built by `benchmark-ppt/build_deck.py` (`uv run build_deck.py <out.pptx>`) after `summarize_results.py` and `benchmark-ppt/extract_frames.py`. When Wan 2.2 or LTX-2.3 finish: review their contact sheets, write `visual-assessment.md` and `visual-task-results.json`, add their wording to `OBS`/`CAPTION`, drop them from `PENDING`, rebuild as a new revision and check it with `preview_deck.py`.

## Earlier handoff checkpoint — user requested switching to Claude

Codex stopped the serial controllers at the user's explicit request to conserve Codex usage. All Wan2.1 files are fully downloaded and SHA-256 verified, including its shared UMT5 encoder and VAE. A race at the handoff boundary started the first Wan smoke; Codex stopped that controller/server/client before any new benchmark completion. Inspect Wan logs/results before resuming. No future Codex controller should be running. Wan2.1 has no completed measured benchmark. Wan2.2 and LTX-2.3 MLX have not generated a video yet. The PowerPoint comparison is unfinished; the existing PPT covers only the baseline and needs the multi-model revision.

Claude can resume `continue_comparison.py` with the Comfy Python and `continue_mlx.py` with the MLX Python, or run each candidate manually. Read those scripts first; they serialize jobs and stop on errors. Use temporary idle-sleep prevention while working and release it afterward. Existing state JSON is marked handed-off, rather than actively running. Update this document's stale candidate-status lines after actual results exist.

The user authorizes Claude to continue the remaining tests, troubleshoot actual failures, and finish the editable PPT in the mentor's format. Do not merely repeat installation instructions. Preserve the completed baseline, test evidence and source manifests. The user currently cannot connect a charger; report battery/Low Power Mode conditions honestly.

## Objective and current status

Continue the user's authorized local video model testing and produce a PowerPoint comparison matching the mentor's table layout. Check current state before doing any work; do not start duplicate downloads or GPU jobs.

Live experiment folder: `/Users/dyn/AI/video-model-comparison-2026-10-29`.
Read `STATUS.md`, `comparison-state.json`, `ltx23-mlx/pipeline-state.json`, `comparison-results.json` and `RESULTS.md` there first. Individual model folders contain `pipeline-state.json`, `results.jsonl`, logs, workflows, output movies, source/checksum manifests and visual assessments. These live files take precedence over this handoff if they are newer.

Baseline: `/Users/dyn/AI/ltx-benchmark-2026-10-29`.
Hardware: Apple M4 Pro,24GB unified memory; macOS27.0.1,arm64. This is not the mentor's M3 Max36GB machine. The current tests use battery power and Low Power Mode, because the user cannot connect a charger. Disclose this condition; never label these as AC-power results.

## Candidates

1. LTX-Video2B v0.9.5 baseline: completed,78.8353s/clip mean across3warm runs.
2. LTX-Video2B distilled v0.9.6: completed,16.5493s/clip mean across3warm runs. Seed42 duplicates the ball;43/44 nearly static.
3. Wan2.1 T2V1.3B: completed, 825.729 s/clip mean across 3 warm runs; task 0/3 (seed 42 ball drops left off a striped box, 43 red bead grid, 44 morphing mesh).
4. LTX-2.3 distilled MLX4-bit: round 1 (512×320, original prompt) 1/3, 52.67 s/clip; round 2 (768×512, new prompt) **3/3**, 108.97 s/clip (AC).
5. Wan2.2 TI2V5B: round 1 1/3, 274.06 s/clip (AC); weights retired afterwards.
6. LTX-Video2B v0.9.5 round 2 (768×512, new prompt): 0/3, 142.91 s/clip (AC).
7. LTX-2.3 distilled MLX4-bit round 3 (round 2 + start/end keyframes): 9/9 on seeds 42–50, 132.22 s/clip (AC).

Keep candidates labelled pending until actual measured results exist. Preserve errors from failed tests; a runtime import is not proof that video generation works. Never use the mentor's numbers as this Mac's measurements.

## Existing installation

- ComfyUI: `/Users/dyn/AI/ComfyUI`,v0.43.0.
- Comfy Python: `/Users/dyn/AI/venvs/comfyui/bin/python` (3.12.13),PyTorch2.15.0,MPS.
- MLX Python: `/Users/dyn/AI/venvs/ltx-mlx/bin/python`.
- MLX source: experiment folder `mlx-runtime`, pinned commit895201df379b079c2154738bcf92005b7a371923,v0.18.0.
- Shared model storage: `/Users/dyn/AI/models`.
- Baseline checkpoint and T5 encoder are retained. Task-created candidate weight caches may be removed after testing to make room for later candidates. Check `retired-candidate-cache.json` for exact files, SHA-256 and recovery URLs.
- Do not modify global Python or raise MPS/Metal memory safety limits.

## Test protocol

Same positive ball prompt,512×320,batch1,25FPS. Cold smoke25frames/seed41,49-frame warmup/seed41,then49-frame measured seeds42/43/44. Report mean elapsed seconds per49-frame clip. Playback duration1.96s differs from generation time. Preserve native model-specific sampling; details in each `PROVENANCE.md` and saved workflows.

Prompt: A single bright red ball rolls slowly from the left side to the right side of a wooden table. The ball remains round and keeps the same size and color throughout the shot. A plain beige wall is visible in the background. Soft daylight enters from a window on the left. The camera stays completely still, showing the entire table surface in one continuous shot.

Warm prompt embeddings are cached. Timings include native output writing and exclude installation/downloads. MLX uses a native two-stage8+3step distilled pipeline, spatial2×latent upscale and low-RAM streaming; other Comfy pipelines run directly at target size. Native residency and output encoders differ.

Comfy memory: mean per-run1Hz sampled maximum MPS driver allocation. MLX memory: mean per-run peak active allocation. These counters differ and neither is total RAM. System swap deltas are separate; do not add RSS and GPU counters.

## Safe resume / repeat on the same Mac

First inspect processes and live state. The serial controllers may already be running:

```sh
pgrep -fl 'continue_comparison|continue_mlx|continue_tests|download_ranges|run_server|benchmark.py'
```

Do not run any command below while an existing controller/download/generation is active. Read scripts before changing or invoking them. One model generation at a time.

For a Comfy candidate, restore weights using that folder's `download_ranges.py` if missing. It validates complete SHA-256 and resumes verified chunks. Then start that folder's `run_server.py` with the Comfy Python, and run its `benchmark.py smoke` followed by `benchmark.py bench`. Finally run `verify_outputs.py`. Model folders are `ltx-distilled`,`wan21`,`wan22`. Check free disk and memory first.

Example after verifying nothing else is running:

```sh
/Users/dyn/AI/venvs/comfyui/bin/python /Users/dyn/AI/video-model-comparison-2026-10-29/wan21/download_ranges.py
/Users/dyn/AI/venvs/comfyui/bin/python /Users/dyn/AI/video-model-comparison-2026-10-29/wan21/run_server.py
```

In another terminal, once the local server is ready:

```sh
/Users/dyn/AI/venvs/comfyui/bin/python /Users/dyn/AI/video-model-comparison-2026-10-29/wan21/benchmark.py smoke
/Users/dyn/AI/venvs/comfyui/bin/python /Users/dyn/AI/video-model-comparison-2026-10-29/wan21/benchmark.py bench
/Users/dyn/AI/venvs/comfyui/bin/python /Users/dyn/AI/video-model-comparison-2026-10-29/wan21/verify_outputs.py
```

For MLX, selected model/encoder weights total28,143,152,956bytes. Allow additional free disk for swap. Its `download_ranges.py` uses local `model/` and `gemma/` folders. Use the MLX Python to run `benchmark.py`, then `verify_outputs.py`. FFmpeg is isolated inside the MLX venv. Keep generation offline; scripts block outbound sockets.

Refresh summary after testing:

```sh
python3 /Users/dyn/AI/video-model-comparison-2026-10-29/summarize_results.py
```

Review actual contact sheets and movies before making quality claims. Visual-task counts use the narrow criterion saved in `visual-task-results.json`; keyframe inspection does not establish all temporal quality or overall model ranking.

## PowerPoint deliverable

Workspace: `/Users/dyn/Documents/ChatGPT/Taiwan Mobile Internship/benchmark-ppt`.
Reference: mentor's screenshot supplied in the conversation. Required table columns: Model,Weights,Mean performance,TTFT(ms),MemoryGiB. Use one row per model, not one row per seed. Video TTFT is unmeasured: use“—”. Match navy table header, alternating pale rows, off-white background, actual output frames on right, task observations below and honest memory/conditions footnotes. All performance values must come from actual logs. Keep tables/text editable and embed images.

The previous single-model deck `output/Local-video-benchmark-M4-Pro.pptx` was conceptually incomplete; final comparison should use a new revision filename. Check output folder for the latest comparison before recreating anything.

## Permissions and portability

Local backend API testing is allowed. Codex browser inspection of localhost8188 was denied; do not bypass that gate through another UI/control path. The user can open the local UI manually.

This handoff describes this Mac's paths. On another computer, detect hardware/backend, create an isolated environment and adapt paths. NVIDIA CUDA is for a supported NVIDIA machine, not this Mac. Re-run benchmarks there; do not reuse the Mac's measured numbers as that computer's results. Hardware details for the friend's RTX3050 machine remain unknown.

The handoff and result files can be attached to a Claude chat for analysis. Actually executing commands requires a Claude environment with access to the target computer's terminal and files; sharing this file alone does not grant that access.
