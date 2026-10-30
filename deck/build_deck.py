# /// script
# requires-python = ">=3.12"
# dependencies = ["python-pptx==1.0.2"]
# ///
"""Build the editable multi-model comparison deck from the measured result files.

Run (after extract_frames.py):  uv run build_deck.py [output.pptx]
Every timing and memory value is read from results.jsonl / comparison-results.json under
/Users/dyn/AI; none is typed in here. Task pass counts come from each model's
visual-task-results.json, and the short wording below is checked against those files.
A <deck>.data.json file next to the deck records every value that was placed on a slide.
"""
import json,statistics,sys
from pathlib import Path
from lxml import etree
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR,PP_ALIGN
from pptx.oxml.ns import qn
from pptx.util import Emu,Inches,Pt

HERE=Path(__file__).resolve().parent
AI=Path('/Users/dyn/AI');C=AI/'video-model-comparison-2026-10-29'
OUT=Path(sys.argv[1]) if len(sys.argv)>1 else HERE/'output/Local-video-model-comparison-M4-Pro-rev2.pptx'
NAVY,BORDER,MUTED,TEAL,PALE,WHITE,BG=(RGBColor.from_string(x) for x in ('152B3C','DCE5EB','536A80','007B87','EDF3F6','FFFFFF','F8FAFC'))
FONT='Aptos'
OK={'success','finished','execution_success'}
RUNS=[('smoke-25f-seed41','Cold smoke 25f'),('warmup-49f-seed41','Warm-up 49f'),('benchmark-49f-seed42','Seed 42'),('benchmark-49f-seed43','Seed 43'),('benchmark-49f-seed44','Seed 44')]

# name must equal the "model" field in comparison-results.json.
MODELS=[
    {'key':'ltx095','name':'LTX-Video 2B v0.9.5','short':'LTX 2B v0.9.5','root':AI/'ltx-benchmark-2026-10-29','weights':'BF16','sampling':'30 steps, CFG 3, res_multistep'},
    {'key':'ltx096d','name':'LTX-Video 2B distilled v0.9.6','short':'LTX 2B distilled','root':C/'ltx-distilled','weights':'BF16','sampling':'8 steps, CFG 1, euler_ancestral'},
    {'key':'wan21','name':'Wan 2.1 T2V 1.3B','short':'Wan 2.1 1.3B','root':C/'wan21','weights':'FP16','sampling':'30 steps, CFG 6, uni_pc'},
    {'key':'ltx23mlx','name':'LTX-2.3 distilled MLX','short':'LTX-2.3 MLX','root':C/'ltx23-mlx','weights':'MLX 4-bit','sampling':'8 + 3 steps, two-stage, 2× upscale'},
    {'key':'wan22','name':'Wan 2.2 TI2V 5B','short':'Wan 2.2 5B','root':C/'wan22','weights':'FP16','sampling':'30 steps, CFG 5, uni_pc'},
    # Round 2 (user-approved): prompt without "slowly" and with explicit motion, 768×512.
    {'key':'ltx095_r2','name':'LTX-Video 2B v0.9.5 (round 2)','short':'LTX 2B v0.9.5 · round 2','root':C/'round2/ltx095','weights':'BF16','sampling':'30 steps, CFG 3, res_multistep'},
    {'key':'ltx23mlx_r2','name':'LTX-2.3 distilled MLX (round 2)','short':'LTX-2.3 · round 2','root':C/'round2/ltx23-mlx','weights':'MLX 4-bit','sampling':'8 + 3 steps, two-stage, 2× upscale'},
    # Round 3: round-2 settings plus start/end keyframe anchors; reviewed on seeds 42–50.
    {'key':'ltx23mlx_kf','name':'LTX-2.3 distilled MLX (keyframes)','short':'LTX-2.3 · keyframes','root':C/'round3/ltx23-mlx-keyframes','weights':'MLX 4-bit','sampling':'8 + 3 steps, two-stage, 2× upscale, 2 anchors'},
]
# Task wording per model: (expected pass count from visual-task-results.json, one-line summary).
OBS={
    'ltx095':(1,'Seed 43 rolls left→right; 42 and 44 nearly static'),
    'ltx096d':(0,'Seed 42 adds a second ball; 43 and 44 nearly static'),
    'wan21':(0,'Ball drops left (42); red bead grid (43); morphing mesh (44)'),
    'ltx23mlx':(1,'Seed 44 rolls left→right; 42 goes right→left, 43 static'),
    'wan22':(1,'Seed 42 moves right; 43 and 44 smeared artifacts'),
    'ltx095_r2':(0,'Ball vanishes (42), no ball (43), static ball (44)'),
    'ltx23mlx_r2':(3,'One ball rolls left→right in all three clips'),
    'ltx23mlx_kf':(9,'One ball rolls left→right in all nine clips (seeds 42–50)'),
}
# Shorter per-seed captions where the reviewed observation is too long for a slide caption.
CAPTION={('ltx095',43):'Clear left-to-right roll of one round ball',('ltx096d',42):'Second ball appears; original almost static',
         ('wan21',42):'Ball drops down-left off a striped box',('wan21',43):'Dozens of red beads, not one ball',('wan21',44):'Cartoon room; red mesh morphs, late ball'}
# Extra provenance for the speaker notes of slides 1 and 2.
RUN_NOTES={'wan21':'Wan 2.1: Claude interrupted the first server session 16 s into seed 42 for a colour check of the magenta-tinted smoke (wan21/logs/interrupted-for-colour-check/README.md). The warm-up and seeds 42-44 were then rerun in a second server session, so the warm-up shown (956.87 s) includes model loading and prompt encoding; the first session warm-up took 847.16 s and produced identical frames. The cold smoke (378.14 s) is from the first session.'}
# Why a candidate has no measured row (shown as footnote 2 and in its slide placeholders).
PENDING={
    'ltx23mlx':'runs after Wan 2.2; needs a 28.1 GB download once the Wan caches are retired, then a charger',
    'wan22':'weights were downloading when this deck was built; GPU tests wait for a charger (battery under 30%)',
}

def load(m):
    path=m['root']/'results.jsonl'
    rows=[json.loads(s) for s in path.read_text().splitlines() if s.strip()] if path.exists() else []
    good=lambda x:x['status'] in OK and x.get('sampler_executed',True)
    m['runs']={}
    for label,_ in RUNS:
        same=[x for x in rows if x['label']==label]
        m['runs'][label]=next((x for x in reversed(same) if good(x)),same[-1] if same else None)
    summary=next(x for x in json.loads((C/'comparison-results.json').read_text()) if x['model']==m['name'])
    m['measured']=summary['status']=='measured'
    m['done']=[s for s in (42,43,44) if (x:=m['runs'][f'benchmark-49f-seed{s}']) and x['status'] in OK]  # measured seeds finished so far
    if m['measured']:
        seeds=[m['runs'][f'benchmark-49f-seed{s}']['elapsed_client_s'] for s in (42,43,44)]
        assert abs(statistics.mean(seeds)-summary['mean_s_per_clip'])<1e-9,(m['name'],seeds,summary)
        m.update(mean=summary['mean_s_per_clip'],fps=49/summary['mean_s_per_clip'],mem=summary['memory_gib'],seed_seconds=seeds,memory_metric=summary['memory_metric'])
    task=m['root']/'visual-task-results.json'
    m['task']=json.loads(task.read_text()) if task.exists() else None
    if m['task']:
        assert m['key'] in OBS and OBS[m['key']][0]==m['task']['passed'],(m['key'],m['task']['passed'])
    if not m['measured']: assert m['key'] in PENDING,('missing pending reason',m['key'])
    return m

def run_memory_gib(x):
    v=x['memory']['sampled_max_mps_driver_bytes'] if 'memory' in x else x['mlx_peak_active_bytes']
    return v/1024**3

def add_run(p,text,size,color,bold=False,italic=False):
    r=p.add_run();r.text=text;f=r.font;f.name=FONT;f.size=Pt(size);f.bold=bold;f.italic=italic;f.color.rgb=color
    return r

def text(slide,x,y,w,h,paras,size=13.5,color=NAVY,bold=False,align=PP_ALIGN.LEFT,anchor=MSO_ANCHOR.TOP,after=0):
    """paras: list of paragraphs; a paragraph is a str or a list of (text, overrides) runs."""
    shp=slide.shapes.add_textbox(Inches(x),Inches(y),Inches(w),Inches(h))
    tf=shp.text_frame;tf.word_wrap=True;tf.vertical_anchor=anchor
    tf.margin_left=tf.margin_right=Inches(0.04);tf.margin_top=tf.margin_bottom=Inches(0.02)
    for i,para in enumerate(paras):
        p=tf.paragraphs[0] if i==0 else tf.add_paragraph()
        p.alignment=align;p.space_after=Pt(after)
        for t,o in ([(para,{})] if isinstance(para,str) else para):
            add_run(p,t,o.get('size',size),o.get('color',color),o.get('bold',bold),o.get('italic',False))
    return shp

def borders(cell,color='DCE5EB',width=5715):
    tcPr=cell._tc.get_or_add_tcPr()
    for i,tag in enumerate(('a:lnL','a:lnR','a:lnT','a:lnB')):
        old=tcPr.find(qn(tag))
        if old is not None: tcPr.remove(old)
        ln=tcPr.makeelement(qn(tag),{'w':str(width)})
        etree.SubElement(etree.SubElement(ln,qn('a:solidFill')),qn('a:srgbClr'),val=color)
        tcPr.insert(i,ln)

def table(slide,x,y,widths,header,rows,hdr_h=0.5,row_h=0.38,size=13.5,hdr_size=12.75,align=None):
    """rows: list of rows; a cell is a str, a (text, overrides) tuple or a list of those runs."""
    gf=slide.shapes.add_table(len(rows)+1,len(widths),Inches(x),Inches(y),Inches(sum(widths)),Inches(hdr_h+row_h*len(rows)))
    t=gf.table;pr=t._tbl.tblPr;pr.set('firstRow','0');pr.set('bandRow','0')
    sid=pr.find(qn('a:tableStyleId'))
    if sid is None: sid=etree.SubElement(pr,qn('a:tableStyleId'))
    sid.text='{2D5ABB26-0587-4C30-8999-92F81FD0307C}'  # "No Style, No Grid": fills and borders below are explicit
    for i,w in enumerate(widths): t.columns[i].width=Inches(w)
    t.rows[0].height=Inches(hdr_h)
    for r in range(1,len(rows)+1): t.rows[r].height=Inches(row_h)
    for r,cells in enumerate([header]+rows):
        for c,spec in enumerate(cells):
            cell=t.cell(r,c);cell.fill.solid();cell.fill.fore_color.rgb=NAVY if r==0 else WHITE if r%2 else PALE
            borders(cell)
            cell.margin_left=cell.margin_right=Inches(0.1);cell.margin_top=cell.margin_bottom=Inches(0.04)
            cell.vertical_anchor=MSO_ANCHOR.MIDDLE
            p=cell.text_frame.paragraphs[0];cell.text_frame.word_wrap=True
            if align and align[c]: p.alignment=align[c]
            for item in (spec if isinstance(spec,list) else [spec]):
                t_,o=(item,{}) if isinstance(item,str) else item
                if r==0: add_run(p,t_,o.get('size',hdr_size),WHITE,bold=True)
                else: add_run(p,t_,o.get('size',size),o.get('color',NAVY),o.get('bold',c==0),o.get('italic',False))
    return gf

def placeholder(slide,x,y,w,h,label,size=11):
    shp=slide.shapes.add_shape(MSO_SHAPE.RECTANGLE,Inches(x),Inches(y),Inches(w),Inches(h))
    shp.fill.solid();shp.fill.fore_color.rgb=PALE;shp.line.color.rgb=BORDER;shp.line.width=Emu(5715);shp.shadow.inherit=False
    tf=shp.text_frame;tf.word_wrap=True;tf.vertical_anchor=MSO_ANCHOR.MIDDLE
    p=tf.paragraphs[0];p.alignment=PP_ALIGN.CENTER;add_run(p,label,size,MUTED,italic=True)
    return shp

def strip(m,seed): return HERE/'assets/strips'/f"{m['key']}-seed{seed}.png"

def task_label(m):
    return f"Task {m['task']['passed']}/{m['task']['evaluated']} seeds" if m['task'] else 'Task not reviewed' if m['measured'] else 'Run in progress' if m['done'] else 'Not run'

def new_slide(prs,title,subtitle):
    s=prs.slides.add_slide(prs.slide_layouts[6])
    s.background.fill.solid();s.background.fill.fore_color.rgb=BG
    text(s,0.27,0.18,12.5,0.6,[title],size=33,bold=True)
    text(s,0.29,0.81,12.6,0.33,subtitle if isinstance(subtitle,list) else [subtitle],size=16.5,color=MUTED)
    return s

def build():
    models=[load(m) for m in MODELS]
    pending=[m for m in models if not m['measured']]
    prs=Presentation();prs.slide_width=Emu(12192000);prs.slide_height=Emu(6858000)
    prs.core_properties.title='Local video model benchmark results — MacBook Pro M4 Pro'
    prs.core_properties.subject='Measured local text-to-video comparison, battery / Low Power Mode'
    mem_note='¹ Memory: ComfyUI rows = mean of each warm run’s 1 Hz sampled maximum MPS driver allocation; MLX = mean peak active MLX allocation. Neither is total RAM or a true peak, and the two counters are not directly comparable.'
    pend_note='² Not run or still running: '+'; '.join(f"{m['short']} — {PENDING[m['key']]}" for m in pending)+'. No numbers are shown for runs that did not happen.' if pending else None
    record={'deck':str(OUT),'models':[]}

    # Slide 1: reference comparison layout, one row per model.
    s=new_slide(prs,'Local video model benchmark results',[[('MacBook Pro M4 Pro, 24GB unified memory  ·  ',{}),('Battery power, Low Power Mode on',{'color':TEAL,'bold':True})]])
    rows=[]
    for m in models:
        perf=f"{m['mean']:.2f} s/clip" if m['measured'] else (f"In progress ({len(m['done'])}/3)²" if m['done'] else 'Not run²',{'color':MUTED,'italic':True,'bold':False})
        rows.append([m['name'],m['weights'],perf,'—',f"{m['mem']:.2f}" if m['measured'] else '—'])
        record['models'].append({k:m.get(k) for k in ('name','weights','measured','mean','fps','mem','seed_seconds','memory_metric')}|{'task_passed':m['task']['passed'] if m['task'] else None,'pending_reason':PENDING.get(m['key'])})
    table(s,0.19,1.3,[2.6,1.0,1.75,0.9,1.15],['Model','Weights','Mean performance','TTFT (ms)','Memory GiB¹'],rows,row_h=0.38)
    text(s,0.27,3.76,7.4,0.3,['Mean of three warm 49-frame runs (seeds 42, 43, 44); lower is faster. Each clip is 1.96 s at 25 FPS.'],size=12,color=MUTED)
    text(s,0.27,4.1,7.4,0.33,['Task observations'],size=16.5,bold=True)
    obs=[]
    for m in models:
        if m['task']: obs.append([m['short'],(f"{m['task']['passed']}/{m['task']['evaluated']}",{'bold':True,'color':TEAL if m['task']['passed'] else NAVY}),OBS[m['key']][1]])
        elif m['measured']: obs.append([m['short'],'—',('Measured; visual review pending',{'color':MUTED,'italic':True})])
        elif m['done']: obs.append([m['short'],'—',('Run in progress; reviewed after the last seed²',{'color':MUTED,'italic':True})])
        else: obs.append([m['short'],'—',('Not run²',{'color':MUTED,'italic':True})])
    table(s,0.19,4.48,[2.0,0.8,4.6],['Model','Task³','What the measured clips show'],obs,hdr_h=0.34,row_h=0.31,size=11.5,hdr_size=11.5)
    text(s,8.05,1.18,5.0,0.33,['Generated video, 512×320'],size=16.5,bold=True)
    text(s,8.05,1.52,5.0,0.28,['Seed 42 for every model  ·  frames 1, 25 and 49'],size=12,color=MUTED)
    y=1.88
    for m in models:
        text(s,8.05,y,1.38,0.74,[[(m['short'],{'bold':True,'size':12})],[(task_label(m),{'size':10.5,'color':TEAL if m['task'] and m['task']['passed'] else MUTED})]],anchor=MSO_ANCHOR.MIDDLE)
        if 42 in m['done'] and strip(m,42).exists(): s.shapes.add_picture(str(strip(m,42)),Inches(9.45),Inches(y),width=Inches(3.6))
        else: placeholder(s,9.45,y,3.6,0.742,'Frames not extracted' if 42 in m['done'] else 'Not run²')
        y+=0.82
    text(s,8.05,y+0.02,5.0,0.4,['Seed 42 is the first measured seed, not chosen for quality. All three seeds are on slide 3.'],size=10.5,color=MUTED)
    foot=[mem_note]+([pend_note] if pend_note else [])+['³ Task = exactly one red ball visibly rolls left→right and stays round, judged on six keyframes of each measured clip. A narrow check, not an overall quality ranking. TTFT is a language-model metric with no equivalent measured here (—). Battery results are not an AC-power benchmark.']
    text(s,0.27,6.62,12.8,0.8,foot,size=9,color=MUTED,after=1)
    notes=['Sources: comparison-results.json and RESULTS.md in /Users/dyn/AI/video-model-comparison-2026-10-29; each model folder’s results.jsonl, output-verification.json, visual-assessment.md and visual-task-results.json. Baseline evidence: /Users/dyn/AI/ltx-benchmark-2026-10-29.']
    for m in models:
        if m['measured']: notes.append(f"{m['name']}: mean = ({' + '.join(f'{v:.3f}' for v in m['seed_seconds'])}) / 3 = {m['mean']:.4f} s per 49-frame clip; generated frames/s = 49 / {m['mean']:.4f} = {m['fps']:.4f}. Memory {m['mem']:.3f} GiB ({m['memory_metric']}).")
        elif m['done']: notes.append(f"{m['name']}: in progress — {PENDING[m['key']]}. Finished measured seeds: "+', '.join(f"{s}: {m['runs'][f'benchmark-49f-seed{s}']['elapsed_client_s']:.3f} s" for s in m['done'])+'. No mean until all three seeds finish.')
        else: notes.append(f"{m['name']}: not run — {PENDING[m['key']]}.")
    notes+=[RUN_NOTES[m['key']] for m in models if m['key'] in RUN_NOTES]
    notes.append('All runs on battery power with Low Power Mode on (pmset snapshot stored with every result). Each model keeps its native sampler, steps and CFG, so speed differences are pipeline-level, not architecture-only. Frames decoded from WebM/MP4, not WebP.')
    s.notes_slide.notes_text_frame.text='\n\n'.join(notes)

    # Slide 2: every run, so the mean can be traced.
    s=new_slide(prs,'Per-run timings and settings','Seconds per clip, from prompt submission until the video files are written. Downloads and setup excluded.')
    rows=[]
    for m in models:
        cells=[m['name'],(m['sampling'],{'size':11.5})]
        for label,_ in RUNS:
            x=m['runs'][label]
            cells.append('—' if x is None else f"{x['elapsed_client_s']:.2f}" if x['status'] in OK else (x['status'].replace('execution_',''),{'color':MUTED,'italic':True}))
        cells+= [(f"{m['mean']:.2f}",{'bold':True}),f"{m['fps']:.2f}",f"{m['mem']:.2f}"] if m['measured'] else [('In progress²' if m['done'] else 'Not run²',{'color':MUTED,'italic':True}),'—','—']
        rows.append(cells)
    right=PP_ALIGN.RIGHT
    table(s,0.27,1.3,[2.35,2.65,0.95,0.95,0.83,0.83,0.83,0.95,0.85,0.95],['Model','Native sampling','Cold smoke 25f','Warm-up 49f','Seed 42','Seed 43','Seed 44','Mean 49f','Frames /s','Memory GiB¹'],rows,hdr_h=0.56,row_h=0.4,size=12,hdr_size=11.5,align=[None,None]+[right]*8)
    text(s,0.27,4.12,6.2,0.32,['Protocol'],size=14,bold=True)
    text(s,0.27,4.46,6.2,2.0,['Same positive prompt for every model; 512×320, batch 1, 25 FPS output.','Cold smoke: 25 frames, seed 41, includes model loading and prompt encoding.','Warm-up: 49 frames, seed 41. Measured: 49 frames, seeds 42, 43, 44; the mean uses only these three.','Each model keeps its native sampler, steps and CFG, so speed differences are pipeline-level, not architecture-only.','One generation at a time; outbound network blocked during generation.'],size=11.5,color=NAVY,after=4)
    text(s,6.85,4.12,6.2,0.32,['Conditions'],size=14,bold=True)
    text(s,6.85,4.46,6.2,2.0,[[('Battery power with Low Power Mode on for every run',{'color':TEAL,'bold':True}),(' (pmset snapshot saved with each result); not an AC-power benchmark.',{})],'MacBook Pro 14-inch, Apple M4 Pro, 24GB unified memory, macOS 27.0.1.','ComfyUI 0.43.0 with PyTorch 2.15.0 on Apple MPS; LTX-2.3 uses ltx-2-mlx v0.18.0 (MLX).','ComfyUI timings include WebP and WebM writing; MLX timing includes MP4 writing.','Swap changes per run are logged in each results.jsonl; RSS and GPU counters overlap and are never added.'],size=11.5,color=NAVY,after=4)
    text(s,0.27,6.62,12.8,0.8,[mem_note]+([pend_note] if pend_note else []),size=9,color=MUTED,after=1)
    s.notes_slide.notes_text_frame.text='Per-run values are elapsed_client_s from each model’s results.jsonl (latest successful row per label). Mean, frames/s and memory come from comparison-results.json, regenerated by summarize_results.py. Native sampling: LTX settings from the saved ComfyUI workflows and PROVENANCE.md; Wan settings from the official ComfyUI example workflows; LTX-2.3 from the native MLX DistilledPipeline.\n\n'+'\n\n'.join(RUN_NOTES[m['key']] for m in models if m['key'] in RUN_NOTES)

    # Slide 3: visual evidence for the task column.
    s=new_slide(prs,'Visual check: all measured seeds','Frames 1, 25 and 49 of each 49-frame clip. Task: exactly one red ball rolls left→right and stays round.')
    xs=(1.95,5.65,9.35)
    for x,seed in zip(xs,(42,43,44)): text(s,x,1.22,3.6,0.3,[f'Seed {seed}'],size=13,bold=True)
    y=1.56
    for m in models:
        text(s,0.27,y,1.62,0.74,[[(m['short'],{'bold':True,'size':12})],[(task_label(m),{'size':10.5,'color':TEAL if m['task'] and m['task']['passed'] else MUTED})]],anchor=MSO_ANCHOR.MIDDLE)
        if not m['done']: placeholder(s,xs[0],y,xs[2]+3.6-xs[0],0.742,f"Not run — {PENDING[m['key']]}")
        else:
            for x,seed in zip(xs,(42,43,44)):
                if seed in m['done'] and strip(m,seed).exists(): s.shapes.add_picture(str(strip(m,seed)),Inches(x),Inches(y),width=Inches(3.6))
                else: placeholder(s,x,y,3.6,0.742,'Frames not extracted' if seed in m['done'] else 'Still running when this deck was built')
                verdict=next((v for v in (m['task'] or {}).get('seeds',[]) if v['seed']==seed),None)
                if verdict: text(s,x,y+0.75,3.6,0.24,[[('Pass  ' if verdict['pass'] else 'Fail  ',{'bold':True,'color':TEAL if verdict['pass'] else NAVY}),(CAPTION.get((m['key'],seed),verdict['observation']),{'color':MUTED})]],size=10)
                else: text(s,x,y+0.75,3.6,0.24,['Visual review pending'],size=10,color=MUTED)
        y+=1.04
    text(s,0.27,6.86,12.8,0.5,['Human review of six-keyframe contact sheets per clip (output/*-contact.jpg) plus these decoded frames; no real-time playback claim. One prompt and three seeds cannot rank overall model quality.'],size=9,color=MUTED)
    s.notes_slide.notes_text_frame.text='Strips: assets/strips/<model>-seed<S>.png from extract_frames.py, which decodes the WebM (ComfyUI) or MP4 (MLX) and records each source clip in assets/frames/index.json. Pass/fail and observations: each model’s visual-task-results.json.'

    OUT.parent.mkdir(parents=True,exist_ok=True);prs.save(OUT)
    OUT.with_suffix('.data.json').write_text(json.dumps(record,indent=2,default=str))
    print('Saved',OUT)

if __name__=='__main__': build()
