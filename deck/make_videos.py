"""Convert each measured clip to H.264 MP4 so PowerPoint can play it (it cannot play WebM/VP9).

Run (after extract_frames.py):  /Users/dyn/AI/venvs/comfyui/bin/python make_videos.py
Uses the FFmpeg inside the MLX venv and the source clips recorded in assets/frames/index.json,
so the videos and the still frames come from the same files. Writes assets/videos/<key>-seed<S>.mp4
(libx264, CRF 18, yuv420p, 25 FPS, faststart) and checks every result decodes 49 frames at the source size.
"""
import json,subprocess
from pathlib import Path
import av

HERE=Path(__file__).resolve().parent
FFMPEG='/Users/dyn/AI/venvs/ltx-mlx/bin/ffmpeg'
out=HERE/'assets/videos';out.mkdir(parents=True,exist_ok=True)
for key,seeds in json.loads((HERE/'assets/frames/index.json').read_text()).items():
    for seed,info in seeds.items():
        dest=out/f'{key}-seed{seed}.mp4'
        subprocess.run([FFMPEG,'-hide_banner','-loglevel','error','-y','-i',info['clip'],'-an','-c:v','libx264','-crf','18','-preset','slow','-pix_fmt','yuv420p','-r','25','-movflags','+faststart',str(dest)],check=True)
        with av.open(str(dest)) as c:
            v=c.streams.video[0];frames=sum(1 for _ in c.decode(video=0))
            assert frames==49 and [v.width,v.height]==info['size'],(dest,frames,v.width,v.height)
        print(dest.name,frames,'frames',dest.stat().st_size,'bytes')
