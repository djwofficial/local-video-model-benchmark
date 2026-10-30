"""Generate the red-ball clip with the settings that passed 3/3 on a 24 GB Mac.

Usage:  python generate_red_ball.py --seed 42 --out red-ball-seed42.mp4 [--size 768x512] [--model-dir DIR] [--gemma-dir DIR]
Model: LTX-2.3 distilled, MLX 4-bit (dgrauet/ltx-2.3-mlx-q4) with the Gemma 3 12B 4-bit text encoder, run by
ltx-2-mlx at commit 895201df379b079c2154738bcf92005b7a371923. Settings verified on 29 Oct 2026 (round 2):
native DistilledPipeline (8 steps at 384×256, 2× spatial latent upscale, 3 steps at 768×512), 49 frames at
25 FPS, low-RAM block streaming, audio off, prompt without "slowly" and with the motion stated explicitly.
By default the clip is also anchored: anchors/start-ball-left.png pins frame 0 (replace, strength 1.0) and
anchors/end-ball-right.png guides the last frame (strength 1.0). With anchors, seeds 42–50 were 9/9 correct;
without them (--no-keyframes, pure text-to-video) 8/9, including 3/3 on seeds 42–44.
Prints the elapsed time and the process's peak phys_footprint (Activity Monitor's figure, GPU buffers included).
--size picks one of the resolutions tested with keyframes in the round-4 ladder (30 Oct 2026); all stay at
49 frames, because longer clips (97-145 frames) rolled the ball back or lost it in 6 of 8 test videos.
"""
import argparse,json,os,shutil,tempfile,time
from pathlib import Path
os.environ.update(HF_HUB_OFFLINE='1',TRANSFORMERS_OFFLINE='1',HF_HUB_DISABLE_TELEMETRY='1',DO_NOT_TRACK='1')
from ltx_pipelines_mlx.distilled import DistilledPipeline
from ltx_pipelines_mlx.utils.types import ImageConditioningInput as Anchor
from memprobe import footprint

PROMPT=('A single bright red ball rolls from the left side to the right side of a wooden table, moving steadily across the whole '
        'table until it reaches the right edge. The ball remains round and keeps the same size and color throughout the shot. '
        'A plain beige wall is visible in the background. Soft daylight enters from a window on the left. The camera stays '
        'completely still, showing the entire table surface in one continuous shot.')

# Round-4 ladder, 49 frames, keyframes on, seeds 42 and 43: correct videos / seconds per video after the first load.
# Peak process memory was about 14.6 GiB for every size (the text-encoder load), so all fit a 24 GB Mac.
SIZES={'768x512':'2/2, 131 s','960x640':'2/2, 210 s','1152x768':'2/2, 302 s','1344x896':'1/2, 427 s','1536x1024':'2/2, 597 s'}

def ensure_ffmpeg():
    # ltx-2-mlx writes the MP4 with `ffmpeg` from PATH; fall back to the binary bundled with imageio-ffmpeg.
    if shutil.which('ffmpeg'): return
    import imageio_ffmpeg
    d=Path(tempfile.mkdtemp(prefix='ffmpeg-'));(d/'ffmpeg').symlink_to(imageio_ffmpeg.get_ffmpeg_exe())
    os.environ['PATH']=f"{d}{os.pathsep}{os.environ['PATH']}"

def main():
    here=Path(__file__).resolve().parent
    ap=argparse.ArgumentParser(description='Generate the verified red-ball clip (49 frames, 25 FPS; 768×512 by default).')
    ap.add_argument('--seed',type=int,required=True)
    ap.add_argument('--out',required=True)
    ap.add_argument('--model-dir',default=str(here/'model'),help='folder with the dgrauet/ltx-2.3-mlx-q4 files')
    ap.add_argument('--gemma-dir',default=str(here/'gemma'),help='folder with mlx-community/gemma-3-12b-it-4bit')
    ap.add_argument('--no-keyframes',action='store_true',help='pure text-to-video, without the start/end anchors')
    ap.add_argument('--size',default='768x512',choices=SIZES,help='tested sizes; results: '+'; '.join(f'{k}: {v}' for k,v in SIZES.items()))
    a=ap.parse_args()
    width,height=(int(x) for x in a.size.split('x'))
    ensure_ffmpeg()
    anchors=None if a.no_keyframes else [Anchor.replace(str(here/'anchors/start-ball-left.png'),0,1.0),Anchor.guide(str(here/'anchors/end-ball-right.png'),-1,1.0)]
    pipe=DistilledPipeline(model_dir=a.model_dir,gemma_model_id=a.gemma_dir,low_memory=True,low_ram_streaming=True)
    pipe.generate_audio=False
    start=time.perf_counter()
    pipe.generate_and_save(prompt=PROMPT,output_path=a.out,width=width,height=height,num_frames=49,frame_rate=25,seed=a.seed,images=anchors)
    print(json.dumps({'seed':a.seed,'size':a.size,'keyframes':anchors is not None,'output':a.out,'elapsed_s':round(time.perf_counter()-start,1),'peak_phys_footprint_gib':round(footprint()[1]/2**30,2)}))

if __name__=='__main__': main()
