import json
from pathlib import Path
import av,numpy as np
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parent;records=[]
for p in sorted((ROOT/'output').glob('*.mp4')):
 with av.open(str(p)) as c:
  v=c.streams.video[0];fps=float(v.average_rate);frames=[f.to_ndarray(format='rgb24') for f in c.decode(video=0)]
  expected=25 if '25f' in p.name else 49
  assert len(frames)==expected and (v.width,v.height)==(768,512) and fps==25,(p,len(frames),v.width,v.height,fps)
 indices=sorted(set(round(i*(len(frames)-1)/5) for i in range(6)))
 sheet=Image.new('RGB',(1536,700),'#202020');draw=ImageDraw.Draw(sheet)
 for j,i in enumerate(indices):
  tile=Image.fromarray(frames[i]);tile.thumbnail((512,320));sheet.paste(tile,((j%3)*512,(j//3)*350));draw.text(((j%3)*512+8,(j//3)*350+323),f'frame {i+1}/{len(frames)}',fill='white')
 path=ROOT/'output'/(p.stem+'-contact.jpg');sheet.save(path,quality=92)
 records.append({'path':str(p),'frames':len(frames),'fps':fps,'size':[v.width,v.height],'contact_sheet':str(path),'mean_absolute_frame_difference':float(np.mean([np.abs(a.astype(float)-b.astype(float)).mean() for a,b in zip(frames,frames[1:])]))})
(ROOT/'output-verification.json').write_text(json.dumps(records,indent=2));print(json.dumps(records,indent=2))
