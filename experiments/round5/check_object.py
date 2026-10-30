"""HSV colour-blob check for the round-5 prompts (added by Claude; generalises round4/ltx23-mlx-ladder/check_ball.py).

Usage: python check_object.py <folder> <redball|bluecar>
Every frame of <folder>/output/benchmark-*.mp4 is decoded at 768×512. Per preset: the hue/saturation/value mask
(binary opening, components ≥300 px) and the direction the object should move (+1 left→right, -1 right→left).
Per video: frames with the object, frames with exactly one blob, the largest blob's centroid x per frame, net
progress in the expected direction, the largest move back against it, the longest run of frames without the object,
and a five-frame strip (output/<name>-strip.jpg) for the visual review, which decides the verdict.
Writes <folder>/object-check.json. Needs numpy, pillow, scipy; ffmpeg from FFMPEG or the ltx-mlx venv.
"""
import json,os,subprocess,sys
from pathlib import Path
import numpy as np
from PIL import Image
from scipy import ndimage
FFMPEG=os.environ.get('FFMPEG','/Users/dyn/AI/venvs/ltx-mlx/lib/python3.12/site-packages/imageio_ffmpeg/binaries/ffmpeg-macos-aarch64-v7.1')
W,H=768,512
PRESETS={'redball':{'hue':lambda h:(h<14)|(h>340),'sat':0.5,'val':0.3,'direction':1},
         'bluecar':{'hue':lambda h:(h>=200)&(h<=250),'sat':0.5,'val':0.25,'direction':-1}}

def frames(path):
    raw=subprocess.run([FFMPEG,'-v','error','-i',str(path),'-vf',f'scale={W}:{H}','-f','rawvideo','-pix_fmt','rgb24','-'],capture_output=True,check=True).stdout
    return np.frombuffer(raw,np.uint8).reshape(-1,H,W,3)

def blobs(f,p):
    hsv=np.asarray(Image.fromarray(f).convert('HSV')).astype(np.float32)
    h,s,v=hsv[...,0]*360/255,hsv[...,1]/255,hsv[...,2]/255
    lab,_=ndimage.label(ndimage.binary_opening(p['hue'](h)&(s>p['sat'])&(v>p['val']),iterations=2))
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

folder,preset=Path(sys.argv[1]).resolve(),sys.argv[2];p=PRESETS[preset];d=p['direction']
results=[]
for path in sorted((folder/'output').glob('benchmark-*.mp4')):
    fr=frames(path);comps=[blobs(f,p) for f in fr]
    xs=[c[0]['cx'] if c else None for c in comps];seen=[x for x in xs if x is not None]
    along=[d*x for x in seen]  # position along the expected direction
    back=max((max(along[:i+1])-a for i,a in enumerate(along)),default=0)
    gap=run=0
    for x in xs: run=run+1 if x is None else 0;gap=max(gap,run)
    sp,sf=strip(path,fr)
    results.append({'video':path.name,'preset':preset,'frames':len(fr),'frames_with_object':sum(1 for c in comps if c),
        'frames_with_one_blob':sum(1 for c in comps if len(c)==1),'max_blobs':max(len(c) for c in comps),
        'start_x':round(seen[0],3) if seen else None,'end_x':round(seen[-1],3) if seen else None,
        'progress':round(along[-1]-along[0],3) if seen else None,'max_move_back':round(back,3),'longest_gap_frames':gap,
        'min_aspect':round(min(c[0]['aspect'] for c in comps if c),3) if seen else None,
        'x_at_strip':[round(xs[i-1],3) if xs[i-1] is not None else None for i in sf],'strip':sp,'strip_frames':sf})
    print(json.dumps({k:v for k,v in results[-1].items() if k!='strip'}),flush=True)
(folder/'object-check.json').write_text(json.dumps(results,indent=2))
