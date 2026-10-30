# /// script
# requires-python = ">=3.12"
# dependencies = ["python-pptx==1.0.2"]
# ///
"""Approximate PNG previews of a deck for layout QA when PowerPoint/Quick Look rendering is unavailable.

Run: uv run preview_deck.py <deck.pptx> <out_dir>
Draws backgrounds, pictures, rectangles, text boxes and tables with the Aptos fonts bundled in
Microsoft PowerPoint, wrapping text the way PowerPoint does (greedy, 1.2 line spacing) and growing
table rows to fit. Text that runs past its box or the slide edge is outlined in red and listed.
It is a layout check, not a pixel-exact PowerPoint render.
"""
import sys
from pathlib import Path
from io import BytesIO
from PIL import Image,ImageDraw,ImageFont
from pptx import Presentation
from pptx.util import Emu

DPI=144;FONTS='/Applications/Microsoft PowerPoint.app/Contents/Resources/DFonts/'
_cache={}
def font(pt,bold,italic):
    name={(False,False):'Aptos',(True,False):'Aptos-Bold',(False,True):'Aptos-Italic',(True,True):'Aptos-Bold-Italic'}[(bool(bold),bool(italic))]
    key=(name,pt)
    if key not in _cache: _cache[key]=ImageFont.truetype(FONTS+name+'.ttf',size=round(pt*DPI/72))
    return _cache[key]
px=lambda emu:emu/914400*DPI
def rgb(c,default=(0,0,0)):
    try: return tuple(int(str(c.rgb)[i:i+2],16) for i in (0,2,4))
    except Exception: return default

def layout(tf,width):
    """Wrap a text frame into lines: list of (height_px, [(text, font, colour)])."""
    lines=[]
    for p in tf.paragraphs:
        words=[];size=None
        for r in p.runs:
            f=r.font;pt=f.size.pt if f.size else 18;size=max(size or 0,pt)
            fnt=font(pt,bool(f.bold),bool(f.italic));col=rgb(f.color) if f.color and f.color.type else (0,0,0)
            for i,part in enumerate(r.text.split(' ')):
                words.append([('' if i==0 else ' ')+part,fnt,col])
        size=size or 18;h=size*1.2*DPI/72;after=(p.space_after.pt if p.space_after is not None else 0)*DPI/72
        cur=[];w=0
        for t,fnt,col in words:
            tw=fnt.getlength(t)
            if cur and w+tw>width and t.startswith(' '):
                lines.append((h,cur));cur=[(t[1:],fnt,col)];w=fnt.getlength(t[1:])
            else: cur.append((t,fnt,col));w+=tw
        lines.append((h,cur))
        if after: lines[-1]=(lines[-1][0]+after,lines[-1][1])
    return lines

def draw_text(d,lines,x,y,align=None):
    for h,segs in lines:
        cx=x
        for t,fnt,col in segs: d.text((cx,y),t,font=fnt,fill=col);cx+=fnt.getlength(t)
        y+=h
    return y

def render(prs,slide,issues,idx):
    W,H=int(px(prs.slide_width)),int(px(prs.slide_height))
    bg=rgb(slide.background.fill.fore_color,(255,255,255)) if slide.background.fill.type else (255,255,255)
    im=Image.new('RGB',(W,H),bg);d=ImageDraw.Draw(im)
    for sh in slide.shapes:
        x,y,w,h=px(sh.left),px(sh.top),px(sh.width),px(sh.height)
        if sh.shape_type in (13,16):  # picture, or a movie drawn as its poster frame with a play marker
            pic=Image.open(BytesIO((sh.image if sh.shape_type==13 else sh.poster_frame).blob)).convert('RGB').resize((max(1,int(w)),max(1,int(h))));im.paste(pic,(int(x),int(y)))
            if sh.shape_type==16: d.polygon([(x+w/2-18,y+h/2-22),(x+w/2-18,y+h/2+22),(x+w/2+22,y+h/2)],fill=(255,255,255),outline=(21,43,60))
            continue
        if sh.has_table if hasattr(sh,'has_table') else False:
            t=sh.table;widths=[px(c.width) for c in t.columns];cy=y
            for r,row in enumerate(t.rows):
                cells=[t.cell(r,c) for c in range(len(widths))]
                laid=[layout(c.text_frame,widths[i]-px(c.margin_left)-px(c.margin_right)) for i,c in enumerate(cells)]
                need=max(sum(l[0] for l in L)+px(c.margin_top)+px(c.margin_bottom) for L,c in zip(laid,cells))
                rh=max(px(row.height),need);cx=x
                for i,(c,L) in enumerate(zip(cells,laid)):
                    fill=rgb(c.fill.fore_color,(255,255,255)) if c.fill.type else (255,255,255)
                    d.rectangle([cx,cy,cx+widths[i],cy+rh],fill=fill,outline=(220,229,235))
                    th=sum(l[0] for l in L);draw_text(d,L,cx+px(c.margin_left),cy+(rh-th)/2)
                    cx+=widths[i]
                cy+=rh
            if cy>y+h+2: issues.append(f'slide {idx}: table "{t.cell(0,0).text}" grows {(cy-y-h)/DPI:.2f} in beyond its frame, ends at {cy/DPI:.2f} in')
            continue
        if sh.shape_type==1:  # autoshape rectangle
            fill=rgb(sh.fill.fore_color,(237,243,246)) if sh.fill.type else None
            d.rectangle([x,y,x+w,y+h],fill=fill,outline=(220,229,235))
        if sh.has_text_frame and sh.text_frame.text.strip():
            tf=sh.text_frame
            ml=px(tf.margin_left);mr=px(tf.margin_right);mt=px(tf.margin_top)
            L=layout(tf,w-ml-mr);th=sum(l[0] for l in L)
            anchor=tf.vertical_anchor;ty=y+mt if anchor in (None,1) else y+(h-th)/2 if anchor==3 else y+h-th
            if sh.shape_type==1: ty=y+(h-th)/2
            if sh.shape_type==1:
                for hgt,segs in L:
                    lw=sum(f.getlength(t) for t,f,_ in segs);cx=x+(w-lw)/2
                    for t,fnt,col in segs: d.text((cx,ty),t,font=fnt,fill=col);cx+=fnt.getlength(t)
                    ty+=hgt
                end=ty
            else: end=draw_text(d,L,x+ml,ty)
            if end>y+h+3 or end>H:
                d.rectangle([x,y,x+w,end],outline=(220,0,0),width=3)
                issues.append(f'slide {idx}: text "{tf.text[:50]}" needs {(end-y)/DPI:.2f} in, box {h/DPI:.2f} in, ends at {end/DPI:.2f} in (slide {H/DPI:.2f})')
    return im

def main():
    deck,out=Path(sys.argv[1]),Path(sys.argv[2]);out.mkdir(parents=True,exist_ok=True)
    prs=Presentation(deck);issues=[]
    for i,s in enumerate(prs.slides,1): render(prs,s,issues,i).save(out/f'slide{i}.png')
    print('\n'.join(issues) if issues else 'No overflow found')

if __name__=='__main__': main()
