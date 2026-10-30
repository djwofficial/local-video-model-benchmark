import json
from pathlib import Path
import av,numpy as np
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parent
records=[]
for p in sorted((ROOT/'output').glob('*.webp')):
    image=Image.open(p);frames=[];duration=0
    for i in range(image.n_frames):
        image.seek(i);frames.append(np.asarray(image.convert('RGB')).copy());duration+=image.info.get('duration',0)
    indices=sorted(set(round(i*(len(frames)-1)/5) for i in range(6)))
    sheet=Image.new('RGB',(3*512,2*350),'#202020');draw=ImageDraw.Draw(sheet)
    centroids=[]
    for f in frames:
        red=(f[:,:,0]>100)&(f[:,:,0]>f[:,:,1]*1.45)&(f[:,:,0]>f[:,:,2]*1.45)
        y,x=np.where(red);centroids.append([round(float(x.mean()),1),round(float(y.mean()),1),int(len(x))] if len(x) else None)
    for j,index in enumerate(indices):
        tile=Image.fromarray(frames[index]);tile.thumbnail((512,320))
        x=(j%3)*512;y=(j//3)*350;sheet.paste(tile,(x,y));draw.text((x+8,y+323),f'frame {index+1}/{len(frames)}',fill='white')
    contact=ROOT/'output'/(p.stem+'-contact.jpg');sheet.save(contact,quality=92)
    rec={'path':str(p),'frames':len(frames),'size':list(image.size),'duration_ms':duration,'unique_decoded_frames':len({f.tobytes() for f in frames}),'mean_absolute_frame_difference':round(float(np.mean([np.abs(a.astype(float)-b.astype(float)).mean() for a,b in zip(frames,frames[1:])])),4) if len(frames)>1 else 0,'red_pixel_centroid_per_frame':centroids,'contact_sheet':str(contact)}
    assert rec['frames']>1 and rec['unique_decoded_frames']>1
    records.append(rec)
for p in sorted((ROOT/'output').glob('*.webm')):
    with av.open(str(p)) as c:
        v=c.streams.video[0];fps=float(v.average_rate);frames=sum(1 for _ in c.decode(video=0))
        records.append({'path':str(p),'format':'WebM','codec':v.codec_context.name,'width':v.width,'height':v.height,'fps':fps,'frames':frames,'playback_seconds':frames/fps})
        assert frames==(25 if '25f' in p.name else 49) and fps==25 and (v.width,v.height)==(768,512)
(ROOT/'output-verification.json').write_text(json.dumps(records,indent=2))
for r in records: print(json.dumps({k:v for k,v in r.items() if k!='red_pixel_centroid_per_frame'}))
