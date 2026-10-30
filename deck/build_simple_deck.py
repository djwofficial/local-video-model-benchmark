# /// script
# requires-python = ">=3.12"
# dependencies = ["python-pptx==1.0.2"]
# ///
"""Simple deck: which local model makes the red-ball video correctly, with the videos playable inside.

Run (after summarize_results.py, extract_frames.py and make_videos.py):  uv run build_simple_deck.py [out.pptx]
Slide 1: the reference table for every tested configuration plus how many of its three videos were correct.
Slide 2: the recommended keyframe setup (9/9) and its videos. Slide 3: the text-only setup that passed 3/3.
Slide 4: what changed to get there. Slide 5: memory vs size (round-4 ladder of the keyframe setup).
Slides 6+: every other configuration's three videos (seeds 42, 43, 44) with a plain reason per verdict.
Numbers are loaded exactly as in build_deck.py; verdicts come from each folder's visual-task-results.json
and every WHY entry must exist for a reviewed seed.
"""
import json,shutil,sys
from pathlib import Path
from PIL import Image
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR,PP_ALIGN
from pptx.util import Emu,Inches
import build_deck as b

OUT=Path(sys.argv[1]) if len(sys.argv)>1 else b.HERE/'output/Local-video-model-comparison-M4-Pro-rev7.pptx'
RED=RGBColor.from_string('B42318')
MINT=RGBColor.from_string('E3F2F1')
KF,WIN='ltx23mlx_kf','ltx23mlx_r2'
KEYS=['ltx23mlx_kf','ltx23mlx_r2','ltx23mlx','wan22','ltx095','ltx095_r2','ltx096d','wan21']  # table order: recommended first
SETTINGS={'ltx23mlx_kf':'768×512 · new prompt · keyframes','ltx23mlx_r2':'768×512 · new prompt','ltx095_r2':'768×512 · new prompt'}
ROBUST=b.C/'round2/ltx23-mlx-moreseeds'  # round-2 settings on seeds 45–50
LADDER=b.C/'round4/ltx23-mlx-ladder'  # keyframe setup at larger sizes / longer clips
# Two example strips for the ladder slide: (video stem, label).
LADDER_STRIPS=[('1536x1024-49f-seed42','Correct · 1536×1024, 2 s: one steady roll'),('768x512-145f-seed42','Wrong · 768×512, 6 s: rolls right, back left, then right again')]
# Plain-language reason for each reviewed video (from visual-assessment.md of each folder).
WHY={
    ('ltx095',42):'The ball barely moves.',
    ('ltx095',43):'One red ball rolls from left to right and stays round.',
    ('ltx095',44):'The ball barely moves.',
    ('ltx096d',42):'A second red ball appears; the first one hardly moves.',
    ('ltx096d',43):'The ball barely moves.',
    ('ltx096d',44):'The ball barely moves.',
    ('wan21',42):'The ball falls down to the left off a striped box instead of rolling across a table.',
    ('wan21',43):'Dozens of small red beads appear instead of one ball.',
    ('wan21',44):'Cartoon-style room; a red net shape keeps changing and the ball appears only at the end.',
    ('wan22',42):'One ball drops onto the table edge on the left, then moves clearly to the right.',
    ('wan22',43):'Blurred, overexposed scene; a red blob appears and vanishes.',
    ('wan22',44):'A large pink dome melts into a red smear.',
    ('ltx23mlx',42):'The ball rolls from right to left, the wrong direction.',
    ('ltx23mlx',43):'The ball barely moves.',
    ('ltx23mlx',44):'One ball enters from the left and rolls steadily to the right.',
    ('ltx095_r2',42):'The ball shifts slightly at the right edge, then disappears.',
    ('ltx095_r2',43):'No ball appears; the table stays empty.',
    ('ltx095_r2',44):'The ball stays still in the centre.',
    ('ltx23mlx_r2',42):'One ball rolls from the far left to the right, towards the camera.',
    ('ltx23mlx_r2',43):'One ball enters from the left and rolls steadily to the right.',
    ('ltx23mlx_r2',44):'One ball rolls right across the whole table and out of the frame.',
    ('ltx23mlx_kf',42):'One ball rolls steadily from the left to the right of the table.',
    ('ltx23mlx_kf',43):'One ball rolls steadily from the left to the right of the table.',
    ('ltx23mlx_kf',44):'One ball rolls steadily from the left to the right of the table.',
}
PROMPT_OLD='“A single bright red ball rolls slowly from the left side to the right side of a wooden table…”'
PROMPT_NEW='“A single bright red ball rolls from the left side to the right side of a wooden table, moving steadily across the whole table until it reaches the right edge…”'

def power(m):
    runs=[m['runs'][f'benchmark-49f-seed{s}'] for s in (42,43,44)]
    return 'AC' if all('AC Power' in r['before']['power'] for r in runs) else 'battery'

def settings(m): return SETTINGS.get(m['key'],'512×320 · original prompt')+' · '+power(m)

def robustness():
    rows=[json.loads(x) for x in (ROBUST/'results.jsonl').read_text().splitlines() if x.strip()]
    measured=[x for x in rows if x['label'].startswith('benchmark') and x['status']=='success']
    task=json.loads((ROBUST/'visual-task-results.json').read_text())
    return {'passed':task['passed'],'evaluated':task['evaluated'],'mean':sum(x['elapsed_client_s'] for x in measured)/len(measured),
            'footprint':max(x['phys_footprint_lifetime_max_bytes'] for x in rows)/2**30,'mlx':max(x['mlx_peak_sampled_max_bytes'] for x in rows)/2**30}

def ladder():
    rows=json.loads((LADDER/'ladder-results.json').read_text());task=json.loads((LADDER/'visual-task-results.json').read_text())
    for r in rows:
        v=[x['pass'] for x in task['seeds'] if x['config']==r['config']];assert len(v)==2,r['config'];r['passed']=sum(v)
    return rows

def box(slide,x,y,w,h,fill,rounded=False):
    shp=slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE if rounded else MSO_SHAPE.RECTANGLE,Inches(x),Inches(y),Inches(w),Inches(h))
    shp.fill.solid();shp.fill.fore_color.rgb=fill;shp.line.fill.background();shp.shadow.inherit=False
    if rounded: shp.adjustments[0]=0.18
    return shp

def badge(slide,x,y,ok):
    shp=box(slide,x,y,1.3,0.38,b.TEAL if ok else RED,rounded=True);tf=shp.text_frame;tf.margin_top=tf.margin_bottom=0;tf.vertical_anchor=MSO_ANCHOR.MIDDLE
    p=tf.paragraphs[0];p.alignment=PP_ALIGN.CENTER;b.add_run(p,'Correct' if ok else 'Wrong',14,b.WHITE,bold=True)

def callout(slide,x,y,w,h,paras,size=14):
    box(slide,x,y,w,h,MINT);box(slide,x,y,0.07,h,b.TEAL)
    return b.text(slide,x+0.22,y,w-0.32,h,paras,size=size,anchor=MSO_ANCHOR.MIDDLE)

def number_slides(prs):
    for i,s in enumerate(prs.slides,1): b.text(s,12.35,7.05,0.8,0.3,[str(i)],size=10,color=b.MUTED,align=PP_ALIGN.RIGHT)

def video_slide(prs,m,title,subtitle,footer):
    s=b.new_slide(prs,title,[subtitle])
    w,h=Image.open(b.HERE/'assets/frames'/m['key']/'seed42-f25.png').size;vh=4.1*h/w
    for i,(x,seed) in enumerate(zip((0.35,4.62,8.89),(42,43,44))):
        ok=m['verdict'][seed];run=m['runs'][f'benchmark-49f-seed{seed}']
        b.text(s,x,1.28,4.1,0.34,[[(f'Video {i+1}',{'bold':True}),(f'   seed {seed}',{'color':b.MUTED})]],size=15)
        s.shapes.add_movie(str(b.HERE/'assets/videos'/f"{m['key']}-seed{seed}.mp4"),Inches(x),Inches(1.68),Inches(4.1),Inches(vh),
                           poster_frame_image=str(b.HERE/'assets/frames'/m['key']/f'seed{seed}-f25.png'),mime_type='video/mp4')
        y=1.68+vh+0.12
        badge(s,x+0.05,y+0.04,ok)
        b.text(s,x+1.45,y+0.04,2.6,0.38,[f"{run['elapsed_client_s']:.1f} s to make"],size=11.5,color=b.MUTED,anchor=MSO_ANCHOR.MIDDLE)
        b.text(s,x,y+0.52,4.1,0.85,[[('Why: ',{'bold':True}),(WHY[(m['key'],seed)],{})]],size=13.5)
    b.text(s,0.35,6.3,11.9,0.95,footer,size=10,color=b.MUTED,after=2)
    s.notes_slide.notes_text_frame.text='\n'.join(f"Seed {sd}: {m['runs'][f'benchmark-49f-seed{sd}']['elapsed_client_s']:.3f} s, {'pass' if m['verdict'][sd] else 'fail'}. Reviewed observation: "+next(v['observation'] for v in m['task']['seeds'] if v['seed']==sd)+'.' for sd in (42,43,44))+'\n\nVideos: assets/videos/*.mp4 (H.264 copies of the original outputs, made by make_videos.py). Source folder: '+str(m['root'])
    return s

def build():
    models={m['key']:m for m in (b.load(dict(x)) for x in b.MODELS if x['key'] in KEYS)}
    for m in models.values():
        assert m['measured'] and m['task'],m['name']
        m['verdict']={v['seed']:v['pass'] for v in m['task']['seeds']}
        assert {42,43,44}<=set(m['verdict']) and all((m['key'],s) in WHY for s in (42,43,44)),m['name']
        assert all((b.HERE/'assets/videos'/f"{m['key']}-seed{s}.mp4").exists() for s in (42,43,44)),'run make_videos.py'
    win,kf=models[WIN],models[KF];assert win['task']['passed']==3 and kf['task']['passed']==kf['task']['evaluated']
    rob=robustness()
    prs=Presentation();prs.slide_width=Emu(12192000);prs.slide_height=Emu(6858000)
    prs.core_properties.title='Local video model benchmark — which model makes the red-ball video correctly'
    mem_note='¹ Memory: ComfyUI rows = mean of each run’s 1 Hz sampled maximum MPS driver allocation; MLX rows = mean of each run’s sampled MLX peak. Neither is total RAM.'

    # Slide 1: reference table for every configuration, winner first.
    s=b.new_slide(prs,'Local video model benchmark results',[[('MacBook Pro M4 Pro, 24GB unified memory  ·  same red-ball prompt, judged on every measured video',{})]])
    rows=[]
    for k in KEYS:
        m=models[k];p=m['task']['passed'];n=m['task']['evaluated']
        rows.append([m['name'].replace(' (round 2)',''),(settings(m),{'size':11.5,'color':b.MUTED,'bold':False}),m['weights'],f"{m['mean']:.2f} s/clip",'—',f"{m['mem']:.2f}",(f'{p} of {n}',{'bold':True,'color':b.TEAL if p==n else RED if p==0 else b.NAVY})])
    t=b.table(s,0.27,1.3,[3.3,3.05,1.1,1.7,0.95,1.2,1.45],['Model','Settings · power','Weights','Mean performance','TTFT (ms)','Memory GiB¹','Correct videos'],rows,row_h=0.4,size=13,hdr_size=12.5).table
    for r in (1,2):
        for c in range(7): t.cell(r,c).fill.fore_color.rgb=MINT
    callout(s,0.27,5.22,12.75,0.86,[[('Answer for the 24 GB Mac mini: ',{'bold':True}),(f"LTX-2.3 distilled (MLX, 4-bit) with start and end keyframes: {kf['task']['passed']} of {kf['task']['evaluated']} videos correct",{'bold':True,'color':b.TEAL}),
        (f", {kf['mean']:.0f} s per video on this Mac, peak process memory {rob['footprint']:.1f} GiB. Text only (no keyframes): 3 of 3, and {3+rob['passed']} of {3+rob['evaluated']} over nine seeds.",{})]],size=14)
    b.text(s,0.27,6.25,11.9,1.1,[mem_note,'Power: battery rows ran with Low Power Mode on, AC rows without it, so speeds are only comparable within one power condition. TTFT (time to first token) is a language-model metric and does not apply here (—).',
        '“New prompt” drops “slowly” and states the motion explicitly. Keyframes: a still of the ball on the left pins frame 1 and one of the ball on the right guides frame 49. Correct = exactly one red ball rolls left→right and stays round.'],size=9.5,color=b.MUTED,after=2)
    s.notes_slide.notes_text_frame.text='\n\n'.join([f"{m['name']} ({settings(m)}): mean = ({' + '.join(f'{v:.3f}' for v in m['seed_seconds'])}) / 3 = {m['mean']:.4f} s; memory {m['mem']:.3f} GiB; correct videos {m['task']['passed']}/3." for m in (models[k] for k in KEYS)]
        +[f"Extra seeds 45–50 (round-2 settings): {rob['passed']}/{rob['evaluated']} correct, mean {rob['mean']:.2f} s, peak MLX {rob['mlx']:.2f} GiB, peak process phys_footprint {rob['footprint']:.2f} GiB.",'Sources: comparison-results.json, RESULTS.md and each folder’s results.jsonl and visual-task-results.json under /Users/dyn/AI/video-model-comparison-2026-10-29.'])

    # Slide 2: the recommended keyframe setup.
    video_slide(prs,kf,f"Recommended: LTX-2.3 + keyframes, {kf['task']['passed']} of {kf['task']['evaluated']} correct",[(f"768×512 · new prompt · start + end keyframes · {kf['mean']:.2f} s per video · AC power  ·  ",{}),(f"Correct videos: {kf['task']['passed']} of {kf['task']['evaluated']} (seeds 42–50)",{'bold':True,'color':b.TEAL})],
        ['Click a video to play it (1.96 s). Seeds 45–50 (not shown) were also all correct.','Keyframes: frames 16 and 49 of the passing text-only clip (seed 47) anchor the first and last frames; the model generates the roll in between.',
         f"Peak process memory {rob['footprint']:.1f} GiB (Activity Monitor’s figure, GPU buffers included)."])

    # Slide 3: the text-only configuration that passed 3/3.
    video_slide(prs,win,'Text only: LTX-2.3 distilled (MLX 4-bit), 3 of 3 correct',[(f"768×512 · new prompt · {win['mean']:.2f} s per video · {win['mem']:.2f} GiB¹ · AC power  ·  ",{}),('Correct videos: 3 of 3',{'bold':True,'color':b.TEAL})],
        ['Click a video to play it (1.96 s). The still image is frame 25 of 49.',f"Six extra seeds (45–50) with the same settings: {rob['passed']} of {rob['evaluated']} correct. Peak process memory {rob['footprint']:.1f} GiB (Activity Monitor’s figure, GPU buffers included); first load {rob['mlx']:.1f} GiB of MLX memory while the Gemma text encoder runs.",
         mem_note])

    # Slide 4: what changed, as a ladder of correct-video rates.
    s=b.new_slide(prs,'What made it work','Same prompt idea, same seeds, same 49 frames: four steps from 1 of 3 to 9 of 9')
    old,t23=models['ltx095'],models['ltx23mlx']
    steps=[('Start: LTX-Video 2B','512×320, original prompt',old['task']['passed'],old['task']['evaluated']),
           ('1. Newer model: LTX-2.3 (MLX 4-bit)','same prompt and size; realistic scene, but one ball rolled the wrong way',t23['task']['passed'],t23['task']['evaluated']),
           ('2–3. Clearer prompt + 768×512','“slowly” removed, motion stated explicitly; seed 46 still rolled towards the camera',3+rob['passed'],3+rob['evaluated']),
           ('4. Start + end keyframes','the ball’s first and last positions are fixed; the model makes the roll',kf['task']['passed'],kf['task']['evaluated'])]
    for i,(name,detail,p,n) in enumerate(steps):
        y=1.4+i*0.92;last=i==len(steps)-1
        b.text(s,0.35,y,5.4,0.8,[[(name,{'bold':True,'size':15})],[(detail,{'size':11.5,'color':b.MUTED})]],anchor=MSO_ANCHOR.MIDDLE)
        box(s,5.95,y+0.2,5.2,0.42,b.PALE,rounded=True)
        if p: box(s,5.95,y+0.2,5.2*p/n,0.42,b.TEAL if last else b.NAVY,rounded=True)
        b.text(s,11.3,y+0.13,1.75,0.56,[[(f'{p} of {n}',{'bold':True,'color':b.TEAL if p==n else b.NAVY})]],size=18,anchor=MSO_ANCHOR.MIDDLE)
    cards=[('Why this is hard','Open video models follow a motion direction only about 27–30% of the time (CAPE-T2V, Aug 2026): 3 of 3 by chance is about 3%.'),
           ('Fits the 24 GB Mac mini',f"Peak process memory {rob['footprint']:.1f} GiB with low-RAM streaming; 28.1 GB of weights on disk; about {kf['mean']:.0f} s per video here."),
           ('On the M5 Pro','Same weights and memory; MLX uses the M5 GPU neural accelerators (macOS 26.2+), so it should be faster. Check the first videos there.')]
    for i,(head,body) in enumerate(cards):
        x=0.35+i*4.27;box(s,x,5.2,4.07,1.5,b.WHITE,rounded=True)
        b.text(s,x+0.15,5.3,3.8,1.35,[[(head,{'bold':True,'size':13.5})],[(body,{'size':11.5})]],after=3)
    b.text(s,0.35,6.82,11.9,0.4,['Prompt and size were changed together, so their separate effects are not measured. The 2B model with the new prompt and size got 0 of 3.'],size=9.5,color=b.MUTED)
    s.notes_slide.notes_text_frame.text='Direction-following rates: CAPE-T2V (https://arxiv.org/pdf/2608.03046) and T2V-CompBench (https://arxiv.org/html/2407.14505v2). Recipe and script: /Users/dyn/AI/video-model-comparison-2026-10-29/mac-mini-recipe.'

    # Slide 5: memory vs size for the keyframe setup.
    lad=ladder();assert all(r['fits'] for r in lad)
    s=b.new_slide(prs,'How big can it go on 24 GB?','Recommended setup (LTX-2.3 + keyframes) at larger sizes and longer clips · seeds 42 and 43 per size · AC power')
    rows=[]
    for r in lad:
        p=r['passed']
        rows.append([f"{r['width']}×{r['height']} × {r['frames']}",f"{r['frames']/25:.1f} s",f"{r['peak_footprint_gib']:.1f}",f"{r['warm_footprint_gib']:.1f}",f"{r['warm_seconds']:.0f} s",
                     (f'{p} of 2',{'bold':True,'color':b.TEAL if p==2 else RED if p==0 else b.NAVY})])
    C=PP_ALIGN.CENTER
    t=b.table(s,0.27,1.3,[2.15,0.9,1.2,1.3,1.15,1.15],['Size × frames','Length','Peak GiB²','2nd video GiB²','Time / video','Correct'],rows,row_h=0.36,size=12.5,hdr_size=11.5,align=[None,C,C,C,C,C]).table
    for c in range(6): t.cell(1,c).fill.fore_color.rgb=MINT
    shutil.copytree(LADDER/'output',b.HERE/'assets/ladder',dirs_exist_ok=True,ignore=lambda d,names:[n for n in names if not n.endswith('-strip.jpg')])
    for i,(stem,label) in enumerate(LADDER_STRIPS):
        y=1.3+i*1.95;ok=label.startswith('Correct')
        b.text(s,8.3,y,4.75,0.34,[[(label.split(' · ')[0]+'  ',{'bold':True,'color':b.TEAL if ok else RED}),(label.split(' · ')[1],{})]],size=12)
        s.shapes.add_picture(str(b.HERE/'assets/ladder'/f'{stem}-strip.jpg'),Inches(8.3),Inches(y+0.38),width=Inches(4.75))
        b.text(s,8.3,y+1.05,4.75,0.3,['five frames, start → end'],size=9.5,color=b.MUTED)
    callout(s,8.3,5.22,4.75,0.95,[[('Mac mini answer: ',{'bold':True}),('keep 49 frames (2 s); any size up to 1536×1024 fits and works',{'bold':True,'color':b.TEAL}),
        ('. Memory is never the limit; bigger sizes only cost time. Longer clips mostly fail.',{})]],size=12.5)
    b.text(s,0.27,5.3,7.85,0.75,[[('Why longer clips fail: ',{'bold':True}),('the keyframes fix only the first and last frame. The ball still crosses in about 2 s, then rolls back, leaves the frame or disappears before the last frame pulls it back.',{})]],size=12)
    b.text(s,0.27,6.35,11.9,0.85,['² Peak GiB = highest process memory (Activity Monitor’s figure, GPU buffers included), set by the text-encoder load at start-up; 2nd video GiB = highest memory while making the next video. macOS recommends at most 17.8 GiB (19.07 GB) of GPU memory on a 24 GB Mac; every size stayed below it (highest: 14.6 GiB) and swap never grew.',
        'Two seeds per size, so these are spot checks, not pass rates. 1344×896 seed 42 overshot the right edge and rolled back in.'],size=9.5,color=b.MUTED,after=2)
    s.notes_slide.notes_text_frame.text='\n'.join(f"{r['config']}: peak {r['peak_footprint_gib']:.3f} GiB, 2nd video {r['warm_footprint_gib']:.3f} GiB, MLX peak {r['mlx_peak_gib']:.3f} GiB, warm swap Δ {r['warm_swap_delta_gib']:.2f} GiB, cold {r['cold_seconds']:.1f} s, warm {r['warm_seconds']:.1f} s, correct {r['passed']}/2." for r in lad)+'\n\nSources: '+str(LADDER)+' (ladder-results.json, visual-task-results.json, visual-assessment.md, ball-check.json).'

    # Slides 6+: every other configuration.
    for k in KEYS[2:]:
        m=models[k];p=m['task']['passed']
        video_slide(prs,m,m['name'].replace(' (round 2)',' — new prompt'),[(f"{settings(m)} · {m['mean']:.2f} s per video · {m['mem']:.2f} GiB¹  ·  ",{}),(f'Correct videos: {p} of 3',{'bold':True,'color':b.TEAL if p==3 else RED if p==0 else b.NAVY})],
            ['Click a video to play it (1.96 s). The still image is frame 25 of 49.',mem_note])

    number_slides(prs)
    OUT.parent.mkdir(parents=True,exist_ok=True);prs.save(OUT);print('Saved',OUT)

if __name__=='__main__': build()
