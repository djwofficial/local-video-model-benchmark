"""HSV red-blob check for the round-4 ladder outputs (added by Claude).

Every frame is decoded at 768×512 so the thresholds match rounds 2–3 (hue <14° or >340°, saturation >0.5,
value >0.3, binary opening, components ≥300 px). Per video: frames with exactly one ball-sized component, the
largest component's centroid x per frame, biggest backward step, and the bounding-box aspect (1.0 = round).
Also writes a five-frame strip per video (output/<name>-strip.jpg) for visual review.
Usage: python check_ball.py   (needs numpy, pillow, scipy; ffmpeg path via FFMPEG or the ltx-mlx venv binary)
"""
import json,os,subprocess
from pathlib import Path
import numpy as np
from PIL import Image
from scipy import ndimage
ROOT=Path(__file__).resolve().parent
FFMPEG=os.environ.get('FFMPEG','/Users/dyn/AI/venvs/ltx-mlx/lib/python3.12/site-packages/imageio_ffmpeg/binaries/ffmpeg-macos-aarch64-v7.1')
W,H=768,512

def frames(path):
    raw=subprocess.run([FFMPEG,'-v','error','-i',str(path),'-vf',f'scale={W}:{H}','-f','rawvideo','-pix_fmt','rgb24','-'],capture_output=True,check=True).stdout
    return np.frombuffer(raw,np.uint8).reshape(-1,H,W,3)

def red_components(f):
    hsv=np.asarray(Image.fromarray(f).convert('HSV')).astype(np.float32)
    h,s,v=hsv[...,0]*360/255,hsv[...,1]/255,hsv[...,2]/255
    mask=ndimage.binary_opening(((h<14)|(h>340))&(s>0.5)&(v>0.3),iterations=2)
    lab,n=ndimage.label(mask)
    out=[]
    for i,sl in enumerate(ndimage.find_objects(lab),1):
        area=int((lab[sl]==i).sum())
        if area<300: continue
        ys,xs=np.nonzero(lab[sl]==i);bh,bw=sl[0].stop-sl[0].start,sl[1].stop-sl[1].start
        out.append({'area':area,'cx':(xs.mean()+sl[1].start)/W,'aspect':min(bw,bh)/max(bw,bh)})
    return sorted(out,key=lambda c:-c['area'])

def strip(path,fr):
    idx=np.linspace(0,len(fr)-1,5).round().astype(int)
    im=Image.new('RGB',(5*384+4*6,256),'white')
    for k,i in enumerate(idx): im.paste(Image.fromarray(fr[i]).resize((384,256)),(k*390,0))
    p=path.with_name(path.stem+'-strip.jpg');im.save(p,quality=88);return str(p),[int(i)+1 for i in idx]

results=[]
for path in sorted((ROOT/'output').glob('*.mp4')):
    fr=frames(path);comps=[red_components(f) for f in fr]
    xs=[c[0]['cx'] if c else None for c in comps];seen=[x for x in xs if x is not None]
    steps=[b-a for a,b in zip(seen,seen[1:])]
    # Largest total roll-back (peak x so far minus a later x) and the longest run of frames with no ball.
    drawdown=max((max(seen[:i+1])-x for i,x in enumerate(seen)),default=0)
    gap=run=0
    for x in xs: run=run+1 if x is None else 0;gap=max(gap,run)
    sp,strip_frames=strip(path,fr)
    results.append({'video':path.name,'frames':len(fr),'frames_with_ball':sum(1 for c in comps if c),
        'frames_with_one_blob':sum(1 for c in comps if len(c)==1),'max_blobs':max(len(c) for c in comps),
        'start_x':round(seen[0],3) if seen else None,'end_x':round(seen[-1],3) if seen else None,
        'max_backward_step':round(-min(steps+[0]),3),'max_rollback':round(drawdown,3),'longest_gap_frames':gap,
        'x_at_strip':[round(xs[i-1],3) if xs[i-1] is not None else None for i in np.linspace(1,len(fr),5).round().astype(int)],'min_aspect':round(min(c[0]['aspect'] for c in comps if c),3) if seen else None,
        'area_range':[min(c[0]['area'] for c in comps if c),max(c[0]['area'] for c in comps if c)] if seen else None,
        'strip':sp,'strip_frames':strip_frames})
    print(json.dumps(results[-1]),flush=True)
(ROOT/'ball-check.json').write_text(json.dumps(results,indent=2))
