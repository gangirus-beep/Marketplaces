# Загрузка кадра поставщика для вырезки и последнего фото (этап 3, решение владельца 06.10.2026 «размеры, разметку обрезаем»).
# У товаров с пометкой «slidecrop.py» в «Комментарии по фото» кадр сначала обрезается по контуру товара (pass/slidecrop.py):
# размерные стрелки, тонкие красные линии и плашка материала стоят снаружи товара и отбрасываются, сам товар не ретушируется.
# load(code,n) -> (кадр RGB на белом поле 24 px, rects): rects — прямоугольники товара на кадре (None у обычных кадров).
# Слайд-коллаж (279542: четыре цвета) режется по четвертям, каждая обложка обрезается отдельно и ставится в сетку 2×2.
import json, numpy as np
from PIL import Image
import slidecrop
_g={x['code']:x for x in json.load(open('goods.json'))}
SLIDE={c for c,x in _g.items() if 'slidecrop.py' in (x['comment'] or '')}
COLLAGE={c for c in SLIDE if 'по каждой из' in (_g[c]['comment'] or '')}
PAD=24; GAP=36
def _bbox_im(im):
    import tempfile, os
    p=tempfile.mktemp(suffix='.png'); im.save(p); bb,_=slidecrop.bbox(p); os.remove(p); return bb
def load(code,n):
    path=f'src/{code}_{n:02d}.jpg'; im=Image.open(path).convert('RGB')
    if code not in SLIDE: return im,None
    if code in COLLAGE:
        a=np.asarray(im).astype(int); m=a.min(axis=2)<246
        cs=slidecrop.segs(m.sum(axis=0)>im.height*0.3,gap=8); rs=slidecrop.segs(m.sum(axis=1)>im.width*0.3,gap=8)
        cs=sorted(cs,key=lambda s:s[0]-s[1])[:2]; rs=sorted(rs,key=lambda s:s[0]-s[1])[:2]; cs.sort(); rs.sort()
        parts=[im.crop((x0,y0,x1,y1)) for (y0,y1) in rs for (x0,x1) in cs]   # цветные обложки: красный фильтр slidecrop.bbox здесь не годится (розовая и жёлтая)
        w=max(p.width for p in parts); h=max(p.height for p in parts)
        C=Image.new('RGB',(2*w+GAP+2*PAD,2*h+GAP+2*PAD),(255,255,255)); rects=[]
        for i,p in enumerate(parts):
            x=PAD+(i%2)*(w+GAP); y=PAD+(i//2)*(h+GAP); C.paste(p,(x,y)); rects.append((x,y,x+p.width,y+p.height))
        return C,rects
    bb,_=slidecrop.bbox(path); cr=im.crop(bb)
    C=Image.new('RGB',(cr.width+2*PAD,cr.height+2*PAD),(255,255,255)); C.paste(cr,(PAD,PAD))
    return C,[(PAD,PAD,PAD+cr.width,PAD+cr.height)]
