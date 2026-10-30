# /// script
# requires-python = ">=3.12"
# dependencies = ["python-pptx==1.0.2", "pillow"]
# ///
"""Three-slide summary of the one setup that was correct on every seed (project-manager version).

Run (after make_videos.py):  uv run build_summary_deck.py [out.pptx]
Slide 1: the mentor's table for LTX-2.3 distilled (MLX 4-bit) + keyframes, with three headline numbers.
Slide 2: that setup's videos (seeds 42-44, playable) and what each part of its name means.
Slide 3: how big it can go on 24 GB (round-4 ladder table, no videos).
Slide 4: upgrade test, LTX-2.5 distilled vs LTX-2.3 on two prompts (round 5). Slide 5: the six LTX-2.5 videos.
Every number is read from the result files under /Users/dyn/AI/video-model-comparison-2026-10-29, as in
build_simple_deck.py; the asserts stop the build if a source no longer supports a sentence on a slide.
"""
import json,sys
from pathlib import Path
from pptx import Presentation
from pptx.enum.text import MSO_ANCHOR,PP_ALIGN
from pptx.util import Emu,Inches
import build_deck as b
import build_simple_deck as sd

b.FONT='Calibri'  # Office-safe font: same widths on older Office and in preview_deck.py
OUT=Path(sys.argv[1]) if len(sys.argv)>1 else b.HERE/'output/Local-video-model-summary-M4-Pro-rev2.pptx'
KF=b.C/'round3/ltx23-mlx-keyframes'
L,W=0.5,12.33  # left margin and content width, inches
COLS=[(L+i*(3.89+0.33),3.89) for i in range(3)]  # three equal columns with 0.33" gaps
CENTER=PP_ALIGN.CENTER
NB='\u00a0'  # no-break space: keeps a number with its unit on one line

def slide(prs,title,subtitle):
    s=prs.slides.add_slide(prs.slide_layouts[6])
    s.background.fill.solid();s.background.fill.fore_color.rgb=b.WHITE
    b.text(s,L,0.32,W,0.7,[title],size=36,bold=True)
    b.text(s,L,1.0,W,0.4,[subtitle],size=16,color=b.MUTED)
    return s

def load():
    kf=b.load(dict(next(m for m in b.MODELS if m['key']=='ltx23mlx_kf')))
    rows=[json.loads(x) for x in (KF/'results.jsonl').read_text().splitlines() if x.strip()]
    kf['peak']=max(x['phys_footprint_lifetime_max_bytes'] for x in rows)/2**30
    kf['verdict']={v['seed']:v['pass'] for v in kf['task']['seeds']}
    assert kf['task']['passed']==kf['task']['evaluated']==9 and all(kf['verdict'].values())
    # "The only setup correct on every seed tested": text-only LTX-2.3 was 3/3 on seeds 42-44 but missed one of seeds 45-50.
    # Rounds 1-3 only (red-ball prompt); round 5 (blue car, LTX-2.5) has its own slide with 3 seeds per prompt.
    summary=[x for x in json.loads((b.C/'comparison-results.json').read_text()) if '(blue car)' not in x['model'] and not x['model'].startswith('LTX-2.5')]
    perfect={x['model'] for x in summary if x.get('task_passed')==x.get('task_evaluated')}
    assert perfect=={'LTX-2.3 distilled MLX (round 2)',kf['name']},perfect
    rob=sd.robustness();assert rob['passed']<rob['evaluated']
    kf['setups'],kf['models']=len(summary),len({x['model'].split(' (')[0] for x in summary})
    stats=json.loads((b.C/'ltx23-mlx/runtime-stats.json').read_text())['mlx_device_info']
    kf['gpu_limit']=stats['max_recommended_working_set_size']/2**30  # macOS recommended GPU working set on this 24 GB Mac
    return kf

# Round 5 (text only, 768×512×49): one folder per model and prompt; LTX-2.3 red ball is round 2 (memory from the
# same-settings extra-seed run, which recorded process memory).
R5=[('LTX-2.3','Red ball',b.C/'round2/ltx23-mlx',b.C/'round2/ltx23-mlx-moreseeds'),('LTX-2.3','Blue car',b.C/'round5/ltx23-mlx-bluecar',None),
    ('LTX-2.5','Red ball',b.C/'round5/ltx25-mlx-redball',None),('LTX-2.5','Blue car',b.C/'round5/ltx25-mlx-bluecar',None)]
WHY25={('ltx25_red',42):'small ball rolls left → right',('ltx25_red',43):'rolls left → right, exits',('ltx25_red',44):'rolls right; camera follows it',
       ('ltx25_blue',42):'drives right → left across',('ltx25_blue',43):'drives right → left across',('ltx25_blue',44):'drives right → left across'}

def round5():
    out=[]
    for model,prompt,folder,memfolder in R5:
        rows=[json.loads(x) for x in (folder/'results.jsonl').read_text().splitlines() if x.strip()]
        runs=[next(x for x in rows if x['label']==f'benchmark-49f-seed{s}' and x['status']=='success') for s in (42,43,44)]
        mrows=[json.loads(x) for x in ((memfolder or folder)/'results.jsonl').read_text().splitlines() if x.strip()]
        task=json.loads((folder/'visual-task-results.json').read_text())
        out.append({'model':model,'prompt':prompt,'passed':task['passed'],'evaluated':task['evaluated'],'mean':sum(x['elapsed_client_s'] for x in runs)/3,
                    'peak':max(x['phys_footprint_lifetime_max_bytes'] for x in mrows)/2**30,
                    'run':max(x['phys_footprint_sampled_max_bytes'] for x in mrows if x['label'].startswith('benchmark'))/2**30,
                    'power':'AC' if all('AC Power' in x['before']['power'] for x in runs) else 'battery','seconds':{s:x['elapsed_client_s'] for s,x in zip((42,43,44),runs)},
                    'verdict':{v['seed']:v['pass'] for v in task['seeds']}})
    return out

def build():
    kf=load();lad=sd.ladder();p,n=kf['task']['passed'],kf['task']['evaluated']
    assert all(r['fits'] and r['peak_footprint_gib']<kf['gpu_limit'] for r in lad)
    short=[r for r in lad if r['frames']==49];longer=[r for r in lad if r['frames']>49]
    prs=Presentation();prs.slide_width=Emu(12192000);prs.slide_height=Emu(6858000)
    prs.core_properties.title='LTX-2.3 + keyframes: the local video setup that was correct on every seed'

    # Slide 1: the table, then three headline numbers.
    s=slide(prs,'One setup made every video correct','Red-ball prompt  ·  tested on a MacBook Pro M4 Pro, 24 GB  ·  target: Mac mini M5 Pro, 24 GB')
    b.table(s,L,1.65,[3.2,1.25,1.7,2.05,1.15,1.3,1.68],['Model','Weights','Output','Mean performance','TTFT (ms)','Memory GiB¹','Correct videos'],
            [['LTX-2.3 distilled + keyframes','MLX 4-bit','768×512, 2 s',f"{kf['mean']:.2f} s/clip",'—',f"{kf['peak']:.1f}",(f'{p} of {n}',{'bold':True,'color':b.TEAL})]],
            hdr_h=0.5,row_h=0.6,size=15,hdr_size=14,align=[None,None,None,None,CENTER,CENTER,CENTER])
    tiles=[(f'{p} of {n}',f"videos correct: every seed tested ({min(kf['verdict'])}–{max(kf['verdict'])})",b.TEAL,sd.MINT),
           (f"{kf['peak']:.1f} GiB",f"peak memory; fits a 24{NB}GB Mac (macOS GPU limit {kf['gpu_limit']:.1f}{NB}GiB)",b.NAVY,b.PALE),
           (f"{kf['mean']:.0f} s",f'to make one 2-second video on this M4{NB}Pro',b.NAVY,b.PALE)]
    for (x,w),(big,label,col,fill) in zip(COLS,tiles):
        sd.box(s,x,3.15,w,1.7,fill,rounded=True)
        b.text(s,x+0.25,3.27,w-0.5,0.75,[[(big,{'bold':True,'size':40,'color':col})]])
        b.text(s,x+0.25,4.05,w-0.5,0.7,[label],size=14)
    b.text(s,L,5.2,W,0.45,[[('Out of ',{}),(f"{kf['setups']} red-ball setups tested across {kf['models']} models",{'bold':True}),(', this is the only one correct on all 9 seeds tested. LTX-2.5 results are on slide 4.',{})]],size=16)
    b.text(s,L,6.3,W,0.75,['¹ Memory = peak process memory (Activity Monitor’s figure, GPU buffers included). TTFT (time to first token) applies to language models, not video, so it is “—”.',
                           'Seed = the random start number: the same prompt with a different seed gives a different video.'],size=11,color=b.MUTED,after=3)
    s.notes_slide.notes_text_frame.text=(f"Mean = ({' + '.join(f'{v:.3f}' for v in kf['seed_seconds'])}) / 3 = {kf['mean']:.4f} s (seeds 42–44, AC power). "
        f"Peak process phys_footprint {kf['peak']:.3f} GiB (first load, with the Gemma text encoder). Correct {p}/{n} on seeds 42–50. "
        f"The text-only version of the same model was 3/3 on seeds 42–44 but 8/9 over seeds 42–50. Sources: {KF} and {b.C/'comparison-results.json'}.")

    # Slide 2: the model, its videos, and what the name means.
    s=slide(prs,'LTX-2.3 distilled (MLX 4-bit) + keyframes','Click a video to play it  ·  768×512, 49 frames (2 s), 25 FPS  ·  seeds 42–44 shown; seeds 45–50 were also correct')
    vh=3.89*512/768
    for (x,w),seed in zip(COLS,(42,43,44)):
        assert kf['verdict'][seed]
        s.shapes.add_movie(str(b.HERE/'assets/videos'/f'ltx23mlx_kf-seed{seed}.mp4'),Inches(x),Inches(1.45),Inches(w),Inches(vh),
                           poster_frame_image=str(b.HERE/'assets/frames/ltx23mlx_kf'/f'seed{seed}-f25.png'),mime_type='video/mp4')
        sec=kf['runs'][f'benchmark-49f-seed{seed}']['elapsed_client_s']
        b.text(s,x,1.45+vh+0.05,w,0.34,[[(f'Seed {seed}',{'bold':True}),('   Correct',{'bold':True,'color':b.TEAL}),(f'   ·   {sec:.0f} s to make',{'color':b.MUTED})]],size=14)
    b.text(s,L,4.5,W,0.32,['What the name means'],size=16,bold=True)
    cards=[('LTX-2.3 distilled','Lightricks’ open video model. “Distilled” means it was trained to need few steps: 8 at half size, then a 2× upscale and 3 more.'),
           ('MLX 4-bit',f"Runs on Apple’s MLX framework. The weights are stored in 4 bits, so the model and its text encoder fit a 24 GB Mac (peak {kf['peak']:.1f} GiB).")]
    for (x,w),(head,body) in zip(COLS,cards):
        sd.box(s,x,4.87,w,1.8,b.PALE,rounded=True)
        b.text(s,x+0.2,4.97,w-0.4,1.6,[[(head,{'bold':True,'size':16})],[(body,{})]],size=14,after=4)
    x,w=COLS[2];tw=1.2;th=tw*512/768
    sd.box(s,x,4.87,w,1.8,sd.MINT,rounded=True)
    b.text(s,x+0.2,4.97,w-0.4,0.35,[[('+ keyframes',{'bold':True,'size':16})]])
    for i,(img,label) in enumerate([('start-ball-left.png','frame 1: fixed'),('end-ball-right.png','frame 49: guided')]):
        tx=x+0.2+i*(w-0.4-tw)
        s.shapes.add_picture(str(KF/'anchors'/img),Inches(tx),Inches(5.4),width=Inches(tw))
        b.text(s,tx-0.1,5.42+th,tw+0.2,0.28,[label],size=11,color=b.MUTED,align=CENTER)
    b.text(s,x+0.2+tw,5.4,w-0.4-2*tw,th,[[('→',{'size':20,'bold':True})],[('the model makes the roll',{'size':11,'color':b.MUTED})]],align=CENTER,anchor=MSO_ANCHOR.MIDDLE)
    b.text(s,L,6.75,W,0.3,['Keyframe stills = frames 16 and 49 of one of the model’s own correct videos (seed 47, made without keyframes), so every video shows the same table and start and end positions.'],size=11,color=b.MUTED)
    s.notes_slide.notes_text_frame.text='\n'.join(f"Seed {sd_}: {kf['runs'][f'benchmark-49f-seed{sd_}']['elapsed_client_s']:.3f} s, correct. Reviewed observation: "
        +next(v['observation'] for v in kf['task']['seeds'] if v['seed']==sd_)+'.' for sd_ in (42,43,44))+f"\n\nPipeline: DistilledPipeline, 8 steps at 384×256, 2× spatial latent upscale, 3 steps at 768×512, low-RAM streaming, audio off. Anchors: {KF/'anchors'}."

    # Slide 3: how big it can go on 24 GB (table only).
    s=slide(prs,'How big can it go on 24 GB?',f"LTX-2.3 + keyframes at larger sizes and longer clips  ·  2 seeds per size (42, 43)  ·  AC power")
    rows=[[f"{r['width']}×{r['height']}",f"{r['frames']}  ({r['frames']/25:.1f} s)",f"{r['peak_footprint_gib']:.1f}",f"{r['warm_footprint_gib']:.1f}",f"{r['warm_seconds']:,.0f} s",
           (f"{r['passed']} of 2",{'bold':True,'color':b.TEAL if r['passed']==2 else sd.RED if r['passed']==0 else b.NAVY})] for r in lad]
    t=b.table(s,L,1.6,[2.3,2.2,2.1,2.75,1.6,1.38],['Size','Frames (length)','Peak memory GiB¹','Memory while making a video (GiB)','Time per video','Correct'],rows,
              hdr_h=0.6,row_h=0.38,size=14,hdr_size=13,align=[None,CENTER,CENTER,CENTER,CENTER,CENTER]).table
    for c in range(6): t.cell(1,c).fill.fore_color.rgb=sd.MINT  # the recipe's size
    ok_short=sum(r['passed'] for r in short)
    sd.box(s,L,5.85,W,0.85,sd.MINT,rounded=True)
    b.text(s,L+0.25,5.85,W-0.5,0.85,[[('Every size fits: ',{'bold':True}),(f"peak {max(r['peak_footprint_gib'] for r in lad):.1f}{NB}GiB, under the {kf['gpu_limit']:.1f}{NB}GiB macOS GPU limit.",{})],
        [(f'2-second clips work up to 1536×1024 ({ok_short}{NB}of{NB}{2*len(short)} correct)',{'bold':True,'color':b.TEAL}),(f"; longer clips fail ({sum(r['passed'] for r in longer)}{NB}of{NB}{2*len(longer)} correct).",{})]],size=15,anchor=MSO_ANCHOR.MIDDLE)
    b.text(s,L,6.8,W,0.3,['¹ Highest process memory, GPU buffers included. It comes from loading the text encoder at start-up, so it is the same for every size.'],size=11,color=b.MUTED)
    s.notes_slide.notes_text_frame.text='\n'.join(f"{r['config']}: peak {r['peak_footprint_gib']:.3f} GiB, while making the 2nd video {r['warm_footprint_gib']:.3f} GiB, warm swap Δ {r['warm_swap_delta_gib']:.2f} GiB, "
        f"cold {r['cold_seconds']:.1f} s, warm {r['warm_seconds']:.1f} s, correct {r['passed']}/2." for r in lad)+f"\n\nSources: {sd.LADDER} (ladder-results.json, visual-task-results.json, visual-assessment.md)."

    # Slide 4: upgrade test table.
    r5=round5();c23=[r for r in r5 if r['model']=='LTX-2.3'];c25=[r for r in r5 if r['model']=='LTX-2.5']
    s=slide(prs,'Upgrade test: LTX-2.5 distilled vs LTX-2.3','Text only (no keyframes)  ·  768×512, 2 s  ·  2 prompts × 3 seeds (42, 43, 44)  ·  MacBook Pro M4 Pro, 24 GB')
    rows=[[f"{r['model']} distilled",r['prompt'],(f"{r['passed']} of {r['evaluated']}",{'bold':True,'color':b.TEAL if r['passed']==r['evaluated'] else sd.RED}),f"{r['mean']:.0f} s",
           (f"{r['peak']:.1f}",{'bold':r['model']=='LTX-2.5'}),f"{r['run']:.1f}",r['power']] for r in r5]
    t=b.table(s,L,1.6,[2.4,1.7,1.5,1.8,1.75,1.88,1.3],['Model','Prompt','Correct','Time / video','Peak memory GiB¹','Memory making a video GiB','Power'],rows,
              hdr_h=0.6,row_h=0.5,size=15,hdr_size=13,align=[None,None,CENTER,CENTER,CENTER,CENTER,CENTER]).table
    for r in (3,4):
        for c in range(7): t.cell(r,c).fill.fore_color.rgb=sd.MINT
    p23,p25=max(r['peak'] for r in c23),max(r['peak'] for r in c25);m23=sum(r['mean'] for r in c23)/2;m25=sum(r['mean'] for r in c25)/2
    tiles=[(f"{sum(r['passed'] for r in c25)} of {sum(r['evaluated'] for r in c25)}",f"LTX-2.5 videos correct (LTX-2.3: {sum(r['passed'] for r in c23)} of {sum(r['evaluated'] for r in c23)})",b.TEAL,sd.MINT),
           (f'{p25:.1f} GiB',f"LTX-2.5 peak memory, under the {kf['gpu_limit']:.1f}{NB}GiB limit (LTX-2.3: {p23:.1f})",b.NAVY,b.PALE),
           (f'{m25/m23:.1f}×',f'slower: about {m25:.0f}{NB}s per video vs {m23:.0f}{NB}s',b.NAVY,b.PALE)]
    for (x,w),(big,label,col,fill) in zip(COLS,tiles):
        sd.box(s,x,4.45,w,1.55,fill,rounded=True)
        b.text(s,x+0.25,4.55,w-0.5,0.75,[[(big,{'bold':True,'size':40,'color':col})]])
        b.text(s,x+0.25,5.3,w-0.5,0.62,[label],size=14)
    b.text(s,L,6.2,W,0.85,['¹ Highest process memory incl. GPU buffers, set by loading the text encoder at start-up (LTX-2.5: Gemma-4, 9.8 GiB file). LTX-2.3 red-ball memory is from its same-settings run on seeds 45–50.',
        'Both models were correct on every seed here, so 3 seeds per prompt cannot show which follows prompts better; LTX-2.5 ranks higher in public tests (Artificial Analysis Elo 947 vs 838).'],size=11,color=b.MUTED,after=3)
    s.notes_slide.notes_text_frame.text='\n'.join(f"{r['model']} {r['prompt']}: {r['passed']}/{r['evaluated']}, mean {r['mean']:.2f} s (seeds "+', '.join(f'{v:.1f}' for v in r['seconds'].values())+f"), peak {r['peak']:.3f} GiB, while making {r['run']:.3f} GiB, {r['power']}." for r in r5)+'\n\nSources: '+', '.join(str(f) for _,_,f,_ in R5)+'. LTX-2.5 weights: dgrauet/ltx-2.5-mlx-q4 (int4), ltx-pipelines-mlx 0.18.0.'

    # Slide 5: the six LTX-2.5 videos.
    s=slide(prs,'LTX-2.5 distilled: the 6 test videos','Click a video to play it  ·  text only, 768×512, 49 frames (2 s), 25 FPS  ·  all 6 correct')
    vw=3.3;vh=vw*512/768;x0=2.1
    for i,(key,label,r) in enumerate([('ltx25_red','Red ball\nleft → right',c25[0]),('ltx25_blue','Blue car\nright → left',c25[1])]):
        y=1.5+i*(vh+0.75)
        b.text(s,L,y,1.5,vh,[[(t,{'bold':j==0,'size':16 if j==0 else 13,'color':b.NAVY if j==0 else b.MUTED})] for j,t in enumerate(label.split('\n'))],anchor=MSO_ANCHOR.MIDDLE)
        for j,seed in enumerate((42,43,44)):
            x=x0+j*(vw+0.33);ok=r['verdict'][seed]
            s.shapes.add_movie(str(b.HERE/'assets/videos'/f'{key}-seed{seed}.mp4'),Inches(x),Inches(y),Inches(vw),Inches(vh),
                               poster_frame_image=str(b.HERE/'assets/frames'/key/f'seed{seed}-f25.png'),mime_type='video/mp4')
            b.text(s,x,y+vh+0.04,vw,0.3,[[(f'Seed {seed}  ',{'bold':True}),('Correct' if ok else 'Wrong',{'bold':True,'color':b.TEAL if ok else sd.RED}),(f"  ·  {WHY25[(key,seed)]}",{'color':b.MUTED})]],size=12)
    s.notes_slide.notes_text_frame.text='\n'.join(f"{r['prompt']} seed {sd_}: {r['seconds'][sd_]:.1f} s, "+('correct' if r['verdict'][sd_] else 'wrong') for r in c25 for sd_ in (42,43,44))

    sd.number_slides(prs)
    OUT.parent.mkdir(parents=True,exist_ok=True);prs.save(OUT);print('Saved',OUT)

if __name__=='__main__': build()
