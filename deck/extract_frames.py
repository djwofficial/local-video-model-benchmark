"""Extract fixed frames (1, 25, 49) of every measured clip for the comparison deck.

Run with the Comfy venv Python (PyAV, Pillow):
  /Users/dyn/AI/venvs/comfyui/bin/python extract_frames.py
Decodes the WebM (ComfyUI) or MP4 (MLX) of seeds 42/43/44, never the WebP, which may
coalesce repeated frames. Writes assets/frames/<key>/seed<S>-f<NN>.png, a three-frame strip
assets/strips/<key>-seed<S>.png and assets/frames/index.json naming the source clip of each
strip. Models without measured clips are skipped.
"""
import json
from pathlib import Path
import av
from PIL import Image

HERE=Path(__file__).resolve().parent
AI=Path('/Users/dyn/AI');C=AI/'video-model-comparison-2026-10-29'
MODELS={'ltx095':(AI/'ltx-benchmark-2026-10-29/output','webm'),'ltx096d':(C/'ltx-distilled/output','webm'),'wan21':(C/'wan21/output','webm'),'wan22':(C/'wan22/output','webm'),'ltx23mlx':(C/'ltx23-mlx/output','mp4'),
        'ltx095_r2':(C/'round2/ltx095/output','webm'),'ltx23mlx_r2':(C/'round2/ltx23-mlx/output','mp4'),
        'ltx23mlx_kf':(C/'round3/ltx23-mlx-keyframes/output','mp4'),
        # Round 5: LTX-2.3 on the blue-car prompt, and LTX-2.5 on both prompts (text only).
        'ltx23mlx_blue':(C/'round5/ltx23-mlx-bluecar/output','mp4'),'ltx25_red':(C/'round5/ltx25-mlx-redball/output','mp4'),
        'ltx25_blue':(C/'round5/ltx25-mlx-bluecar/output','mp4')}
FRAMES=(0,24,48);GAP=8;BG=(248,250,252)
index={}
for key,(folder,ext) in MODELS.items():
    for seed in (42,43,44):
        clips=sorted(folder.glob(f'benchmark-49f-seed{seed}*.{ext}'),key=lambda p:p.stat().st_mtime)
        if not clips: continue
        clip=clips[-1]
        with av.open(str(clip)) as c: frames=[f.to_image().convert('RGB') for f in c.decode(video=0)]
        assert len(frames)==49,(clip,len(frames))
        out=HERE/'assets/frames'/key;out.mkdir(parents=True,exist_ok=True)
        picked=[frames[i] for i in FRAMES]
        for i,im in zip(FRAMES,picked): im.save(out/f'seed{seed}-f{i+1:02d}.png')
        w,h=picked[0].size;strip=Image.new('RGB',(3*w+2*GAP,h),BG)
        for j,im in enumerate(picked): strip.paste(im,(j*(w+GAP),0))
        (HERE/'assets/strips').mkdir(parents=True,exist_ok=True);strip.save(HERE/'assets/strips'/f'{key}-seed{seed}.png')
        index.setdefault(key,{})[str(seed)]={'clip':str(clip),'frames_decoded':len(frames),'size':[w,h],'frame_numbers':[i+1 for i in FRAMES]}
(HERE/'assets/frames').mkdir(parents=True,exist_ok=True)
(HERE/'assets/frames/index.json').write_text(json.dumps(index,indent=2))
print(json.dumps({k:sorted(v) for k,v in index.items()}))
