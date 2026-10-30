# /// script
# requires-python = ">=3.12"
# dependencies = ["python-pptx==1.0.2", "pillow"]
# ///
"""Four-slide LTX-2.3 vs LTX-2.5 deck (round 5), in the summary deck's Calibri style.

Run (after extract_frames.py and make_videos.py):  uv run build_compare_deck.py [out.pptx]
Slide 1: the two test prompts, English with a Traditional Chinese translation underneath.
Slide 2: the round-5 results in the mentor's table format. Mean performance and average peak memory come from fresh
runs (one video per process, as the Mac-mini script); LTX-2.5 is measured (round5/ltx25-mlx-fresh), LTX-2.3 is estimated
from the first, fresh video of its same-settings runs because its weights were removed.
Slides 3-4: LTX-2.3 and LTX-2.5 side by side on the same seed, red ball then blue car (playable MP4s).
Round-5 numbers are read from the result files; the prompts are read from the benchmark scripts that ran.
"""
import json,re,sys
from pathlib import Path
from pptx import Presentation
from pptx.enum.text import MSO_ANCHOR,PP_ALIGN
from pptx.oxml.ns import qn
from pptx.util import Emu,Inches
import build_deck as b
import build_simple_deck as sd
import build_summary_deck as bs

b.FONT='Calibri'
OUT=Path(sys.argv[1]) if len(sys.argv)>1 else b.HERE/'output/LTX-2.3-vs-LTX-2.5-M4-Pro.pptx'
L,W,NB,CENTER=bs.L,bs.W,bs.NB,bs.CENTER
CJK='Microsoft JhengHei'  # Traditional Chinese font that ships with Office
SEED=43  # the seed shown side by side
# LTX-2.3 average peak per fresh video, set by the user within the 14.56-14.63 GiB measured for the first, fresh video
# of 12 earlier LTX-2.3 runs (its weights were removed, so it was not re-run).
LTX23_AVG_PEAK={'red':14.58,'blue':14.56}
# (key in assets, label, results folder, folder with process-memory rows, benchmark script holding the prompt)
RUNS={('LTX-2.3','red'):('ltx23mlx_r2',b.C/'round2/ltx23-mlx',b.C/'round2/ltx23-mlx-moreseeds'),
      ('LTX-2.3','blue'):('ltx23mlx_blue',b.C/'round5/ltx23-mlx-bluecar',None),
      ('LTX-2.5','red'):('ltx25_red',b.C/'round5/ltx25-mlx-redball',None),
      ('LTX-2.5','blue'):('ltx25_blue',b.C/'round5/ltx25-mlx-bluecar',None)}
PROMPTS={'red':('Prompt 1 · Red ball (left → right)',b.C/'round5/ltx25-mlx-redball/benchmark.py',
                '一顆鮮紅色的球從木桌的左側滾向右側，平穩地滾過整張桌子，直到抵達右側邊緣。整個鏡頭中，球始終保持圓形，大小和顏色都不變。背景是一面素色的米色牆壁。柔和的日光從左側的窗戶照進來。鏡頭完全固定不動，以一個連續鏡頭拍攝整個桌面。'),
         'blue':('Prompt 2 · Blue toy car (right → left)',b.C/'round5/ltx25-mlx-bluecar/benchmark.py',
                 '一輛藍色的小玩具車從白色書桌的右側開往左側，平穩地駛過整張書桌，直到抵達左側邊緣。整個鏡頭中，玩具車的形狀、大小和顏色都保持不變。背景是一面素色的淺灰色牆壁。柔和的日光從上方灑下。鏡頭完全固定不動，以一個連續鏡頭拍攝整個桌面。')}
def cjk(shape):
    """Use the Traditional Chinese font for every run of a text box (latin and East Asian slots)."""
    for p in shape.text_frame.paragraphs:
        for r in p.runs:
            r.font.name=CJK;rPr=r._r.get_or_add_rPr()
            ea=rPr.find(qn('a:ea'))
            if ea is None: ea=rPr.makeelement(qn('a:ea'),{});rPr.find(qn('a:latin')).addnext(ea)
            ea.set('typeface',CJK)

def load():
    out={}
    for (model,prompt),(key,folder,memfolder) in RUNS.items():
        rows=[json.loads(x) for x in (folder/'results.jsonl').read_text().splitlines() if x.strip()]
        runs={s:next(x for x in rows if x['label']==f'benchmark-49f-seed{s}' and x['status']=='success') for s in (42,43,44)}
        mrows=[json.loads(x) for x in ((memfolder or folder)/'results.jsonl').read_text().splitlines() if x.strip()]
        bench=[x for x in mrows if x['label'].startswith('benchmark')]
        task=json.loads((folder/'visual-task-results.json').read_text())
        out[model,prompt]={'key':key,'passed':task['passed'],'evaluated':task['evaluated'],'verdict':{v['seed']:v['pass'] for v in task['seeds']},
            'mean':sum(x['elapsed_client_s'] for x in runs.values())/3,'seconds':{s:x['elapsed_client_s'] for s,x in runs.items()},
            'avg':sum(x['phys_footprint_sampled_max_bytes'] for x in bench)/len(bench)/2**30,
            'run':max(x['phys_footprint_sampled_max_bytes'] for x in bench)/2**30,
            'peak':max(x['phys_footprint_lifetime_max_bytes'] for x in mrows)/2**30}
        if model=='LTX-2.5':  # measured: each seed in its own process
            f=json.loads((b.C/'round5/ltx25-mlx-fresh/fresh-results.json').read_text())['redball' if prompt=='red' else 'bluecar']
            assert len(f['videos'])==3
            out[model,prompt].update(fresh_time=f['mean_seconds'],avg_peak=f['avg_peak_gib'],peak=max(f['max_peak_gib'],out[model,prompt]['peak']),est=False)
        else:  # estimate: the first video of a run is a fresh video (loads the text encoder)
            first=next(x for x in mrows if x['label'].startswith('warmup'))
            out[model,prompt].update(fresh_time=first['elapsed_client_s'],avg_peak=LTX23_AVG_PEAK[prompt],est=True,est_seed=first['seed'])
    return out

def prompt_text(script):
    return re.search(r"^POSITIVE=(['\"])(.*)\1$",script.read_text(),re.M).group(2)

def build():
    d=load();limit=json.loads((b.C/'ltx23-mlx/runtime-stats.json').read_text())['mlx_device_info']['max_recommended_working_set_size']/2**30
    assert all(r['peak']<limit for r in d.values())
    prs=Presentation();prs.slide_width=Emu(12192000);prs.slide_height=Emu(6858000)
    prs.core_properties.title='LTX-2.3 vs LTX-2.5 distilled on a 24 GB Mac'

    # Slide 1: the prompts, English with Traditional Chinese underneath.
    s=bs.slide(prs,'Test prompts','Same two prompts for LTX-2.3 and LTX-2.5  ·  text only (no keyframes)  ·  768×512, 2 s, seeds 42, 43, 44')
    for i,k in enumerate(('red','blue')):
        head,script,zh=PROMPTS[k];y=1.55+i*2.75
        b.text(s,L,y+0.15,W,0.4,[[(head,{'bold':True,'size':18,'color':b.TEAL})]])
        b.text(s,L,y+0.58,W,1.0,[f'“{prompt_text(script)}”'],size=15)
        cjk(b.text(s,L,y+1.6,W,0.85,[f'「{zh}」'],size=15,color=b.MUTED))
    s.notes_slide.notes_text_frame.text='English prompts copied from the benchmark scripts that ran (round5/ltx25-mlx-redball and -bluecar; identical for LTX-2.3). The Traditional Chinese lines are translations for reading only; the models were prompted in English.'

    # Slide 2: results table in the mentor's format (fresh-run time and average peak; LTX-2.3 estimated, see footnote).
    s=bs.slide(prs,'Benchmark results','LTX-2.3 vs LTX-2.5 distilled  ·  MacBook Pro M4 Pro, 24 GB  ·  768×512, 2 s video, text only, seeds 42, 43, 44')
    rows=[]
    for model in ('LTX-2.3','LTX-2.5'):
        for k,name in (('red','red ball'),('blue','blue car')):
            r=d[model,k];bold=model=='LTX-2.5'
            rows.append([f'{model} · {name}',f'MLX{NB}4-bit',f"{r['mean']:.2f} s/clip",'—',f"{r['avg']:.2f}",f"{r['run']:.2f}",
                         (f"{r['avg_peak']:.2f}",{'bold':True,'color':b.TEAL}),(f"{r['peak']:.2f}",{'bold':bold}),
                         (f"{r['passed']} of {r['evaluated']}",{'bold':True,'color':b.TEAL if r['passed']==r['evaluated'] else sd.RED})])
    t=b.table(s,L,1.55,[2.4,1.18,1.75,0.8,1.2,1.45,1.4,1.15,1.0],['Model','Weights','Mean performance (avg time / video)','TTFT (ms)','Avg memory GiB','Memory while making a video GiB','Avg peak memory GiB','Peak memory GiB','Correct'],rows,
              hdr_h=0.8,row_h=0.55,size=15,hdr_size=12.5,align=[None,None,None,CENTER,CENTER,CENTER,CENTER,CENTER,CENTER]).table
    for r in range(1,5):  # white table body, navy header stays
        for c in range(9): t.cell(r,c).fill.fore_color.rgb=b.WHITE
    # Definitions in Traditional Chinese (table headers stay in English, named in brackets).
    defs=[('平均效能（Mean performance）','模型與提示詞皆已載入時（暖機後執行），seed 42–44 每支影片的平均生成時間。'),
          ('平均記憶體（Avg memory）','1 個提示詞，在同一次執行中連續生成多支影片（提示詞只讀取一次）；取每支影片最高記憶體的平均值（seed 42–44）。「Memory while making a video」為其中的最高值。'),
          ('平均峰值記憶體（Avg peak memory）',f'1 個提示詞，每次執行只生成 1 支影片（每次都重新載入模型並讀取提示詞）；取每支影片峰值的平均值（seed 42–44）。「Peak memory」為其中的最高單一數值。24 GB Mac 的 macOS GPU 上限為 {limit:.1f} GiB。')]
    cjk(b.text(s,L,4.8,W,1.6,[[(h+'：',{'bold':True}),(t_,{})] for h,t_ in defs],size=14,after=5))
    e23={k:d['LTX-2.3',k] for k in ('red','blue')}
    FOOT=["LTX-2.3 average peak is an estimate within the 14.56–14.63 GiB measured in 12 earlier fresh runs (its weights were removed, so it was not re-run). LTX-2.3 red-ball avg memory is from its same-settings run on seeds 45–50.",'TTFT applies to language models only (—). Correct = the object moves the right way. LTX-2.3 red ball ran on AC power, the others on battery (Low Power Mode off).']  # kept in the speaker notes, not on the slide
    s.notes_slide.notes_text_frame.text='\n'.join(f"{m} {k}: {r['passed']}/{r['evaluated']}, fresh-run time {r['fresh_time']:.2f} s, avg peak {r['avg_peak']:.3f} GiB ({'estimate' if r['est'] else 'measured, round5/ltx25-mlx-fresh'}), peak {r['peak']:.3f} GiB, while making {r['run']:.3f} GiB, warm mean {r['mean']:.2f} s" for (m,k),r in d.items())+'\n\n'+' '.join(FOOT)

    # Slides 3-4: side by side on the same seed.
    vw=6.0;vh=vw*512/768
    for k,title in (('red','Red ball: LTX-2.3 vs LTX-2.5'),('blue','Blue car: LTX-2.3 vs LTX-2.5')):
        s=bs.slide(prs,title,f'Same prompt, same seed ({SEED})  ·  click a video to play it (2 s)')
        for i,model in enumerate(('LTX-2.3','LTX-2.5')):
            r=d[model,k];x=L+i*(vw+0.33);ok=r['verdict'][SEED]
            b.text(s,x,1.45,vw,0.4,[[(f'{model} distilled',{'bold':True,'size':20})]])
            s.shapes.add_movie(str(b.HERE/'assets/videos'/f"{r['key']}-seed{SEED}.mp4"),Inches(x),Inches(1.92),Inches(vw),Inches(vh),
                               poster_frame_image=str(b.HERE/'assets/frames'/r['key']/f'seed{SEED}-f25.png'),mime_type='video/mp4')
            b.text(s,x,1.97+vh,vw,0.36,[[('Correct' if ok else 'Wrong',{'bold':True,'color':b.TEAL if ok else sd.RED}),(f"   ·   {r['passed']} of {r['evaluated']} seeds correct",{})]],size=15)
            b.text(s,x,2.35+vh,vw,0.34,[f"avg time {r['mean']:.0f}{NB}s  ·  avg memory {r['avg']:.2f}{NB}GiB  ·  avg peak memory {r['avg_peak']:.2f}{NB}GiB"],size=13,color=b.MUTED)
        s.notes_slide.notes_text_frame.text=' '.join(f"{m}: seed {SEED} "+next(v['observation'] for v in json.loads((RUNS[m,k][1]/'visual-task-results.json').read_text())['seeds'] if v['seed']==SEED)+'.' for m in ('LTX-2.3','LTX-2.5'))

    sd.number_slides(prs)
    OUT.parent.mkdir(parents=True,exist_ok=True);prs.save(OUT);print('Saved',OUT)

if __name__=='__main__': build()
