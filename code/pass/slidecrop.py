# Обрезка слайда Рельефа по контуру товара: размерные линии и плашка материала стоят снаружи товара и отбрасываются.
# bbox(path) -> (x0,y0,x1,y1) товара; сам товар не ретушируется.
import numpy as np
from PIL import Image
def segs(v,gap=3):
    out=[]; s=None; last=None
    for i,x in enumerate(v):
        if x:
            if s is None: s=i
            last=i
        elif s is not None and i-last>gap:
            out.append((s,last+1)); s=None
    if s is not None: out.append((s,last+1))
    return out
def bbox(path,thr=246):
    im=Image.open(path).convert('RGB'); a=np.asarray(im).astype(int)
    r,g,b=a[...,0],a[...,1],a[...,2]
    red=(r-np.minimum(g,b)>18)&(r>g)&(r>b)            # тонкие красные размерные линии и красный текст
    m=(a.min(axis=2)<thr)&~red
    H,W=m.shape
    cs=segs(m.sum(axis=0)>max(2,H*0.004))
    if not cs: return None,im
    x0,x1=max(cs,key=lambda s:s[1]-s[0])
    rs=segs(m[:,x0:x1].sum(axis=1)>max(2,(x1-x0)*0.02))
    if not rs: return None,im
    y0,y1=max(rs,key=lambda s:s[1]-s[0])
    # уточнить колонки внутри найденных строк
    cs=segs(m[y0:y1].sum(axis=0)>max(2,(y1-y0)*0.02))
    x0,x1=max(cs,key=lambda s:s[1]-s[0])
    return (x0,y0,x1,y1),im
if __name__=='__main__':
    import sys,json
    from PIL import ImageDraw, ImageFont
    F=ImageFont.truetype('/home/claude/gen/fonts/Manrope.ttf',14)
    keys=sys.argv[2:]; T=300; C=5; R=(len(keys)+C-1)//C
    sh=Image.new('RGB',(C*(T+4),R*(T+22)),(120,160,200)); d=ImageDraw.Draw(sh)
    for i,k in enumerate(keys):
        bb,im=bbox(f'all/{k}.jpg')
        x=(i%C)*(T+4); y=(i//C)*(T+22)
        if bb:
            cr=im.crop(bb); cr.thumbnail((T,T),Image.LANCZOS); sh.paste(cr,(x+(T-cr.width)//2,y+20+(T-cr.height)//2))
        d.text((x+3,y+1),f'{k} {bb}',font=F,fill=(255,255,255))
    sh.save(sys.argv[1],quality=90)
