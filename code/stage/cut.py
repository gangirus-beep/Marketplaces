# Шаг 3. Вырезка кадра U для обложки (кадры с пометкой «slidecrop.py» сначала обрезаются по контуру товара — srcload.py) → cut/КОД.png, cutmeta.json (тон: panel — белый товар, тёмная подложка), контактные листы sh_cut_N.jpg
import os; os.makedirs('cut',exist_ok=True)
import json, numpy as np, sys, pathlib
from PIL import Image, ImageFilter, ImageDraw, ImageFont
from scipy import ndimage as ndi
import srcload
goods=json.load(open('goods.json'))
meta={}
ASS={x['code']:x['assorti']=='ассорти' for x in goods}
def cut(code,n):
    im,rects=srcload.load(code,n); a=np.asarray(im).astype(int)
    if rects:      # слайд Рельефа, обрезанный по контуру: товар — прямоугольник обложки целиком (прозрачная плёнка на белом не отделяется по цвету)
        fg=np.zeros(a.shape[:2],bool); keep=rects
        for (x0,y0,x1,y1) in rects: fg[y0:y1,x0:x1]=True
    else:
        near=a.min(axis=2)>=250
        lab,k=ndi.label(near)
        border=set(lab[0,:])|set(lab[-1,:])|set(lab[:,0])|set(lab[:,-1]); border.discard(0)
        bg=np.isin(lab,list(border))
        fg=~bg
        fg=ndi.binary_opening(fg,iterations=1)
        l2,n2=ndi.label(fg); sz=ndi.sum(fg,l2,range(1,n2+1))
        keep=[i+1 for i,s in enumerate(sz) if s>0.002*fg.size]
        fg=np.isin(l2,keep)
        fg=ndi.binary_fill_holes(fg)
        if not ASS.get(code):
            pad=np.pad(fg,10); pad=ndi.binary_closing(pad,iterations=7); fg=ndi.binary_fill_holes(pad[10:-10,10:-10])
        fg=ndi.binary_erosion(fg,iterations=1)
    alpha=Image.fromarray((fg*255).astype('uint8')).filter(ImageFilter.GaussianBlur(0.9))
    ys,xs=np.where(fg); box=(max(0,xs.min()-3),max(0,ys.min()-3),min(im.width,xs.max()+4),min(im.height,ys.max()+4))
    rgba=im.copy(); rgba.putalpha(alpha); rgba=rgba.crop(box)
    px=a[fg]; lum=(0.299*px[:,0]+0.587*px[:,1]+0.114*px[:,2]); sat=(px.max(axis=1)-px.min(axis=1))
    light=float((lum>215).mean()); gray=float((sat<28).mean())
    if max(rgba.size)>1200: rgba.thumbnail((1200,1200),Image.LANCZOS)
    import io
    buf=io.BytesIO(); rgba.save(buf,format='PNG'); pathlib.Path(f'cut/{code}.png').write_bytes(buf.getvalue())
    return dict(src=f'{im.width}x{im.height}',w=rgba.size[0],h=rgba.size[1],ratio=round(rgba.size[0]/rgba.size[1],4),lum=round(float(lum.mean()),1),light=round(light,2),gray=round(gray,2),fill=round(float(fg[box[1]:box[3],box[0]:box[2]].mean()),2),ncomp=len(keep),cover=round(float(fg.mean()),2))
for x in goods:
    m=cut(x['code'],x['U']); meta[x['code']]=m
    m['tone']='panel' if (m['lum']>200 and m['light']>0.55 and m['gray']>0.6) else 'light'
json.dump(meta,open('cutmeta.json','w'),indent=1)
f=ImageFont.truetype('fonts/Manrope.ttf',15)
cols=13; sz=150
for part in range(0,len(goods),cols*7):
    gg=goods[part:part+cols*7]; rows=(len(gg)+cols-1)//cols
    S=Image.new('RGB',(cols*(sz+8),rows*(sz+24)),(211,64,31)); d=ImageDraw.Draw(S)
    for i,x in enumerate(gg):
        im=Image.open(f"cut/{x['code']}.png"); im.thumbnail((sz,sz)); px=(i%cols)*(sz+8)+4; py=(i//cols)*(sz+24)+4
        if meta[x['code']]['tone']=='light': d.rectangle([px-2,py-2,px+sz+2,py+sz+2],fill=(244,239,231))
        S.paste(im,(px+(sz-im.width)//2,py),im); d.text((px,py+sz+2),f"{x['code']} {'A' if x['assorti']=='ассорти' else ''} {meta[x['code']]['tone'][0]}{meta[x['code']]['ncomp']}",fill=(255,255,255),font=f)
    S.save(f'sh_cut_{part//(cols*7)}.jpg',quality=85)
import collections
print(collections.Counter(m['tone'] for m in meta.values()), collections.Counter(m['src'] for m in meta.values()))
print('ratios',sorted((m['ratio'],c) for c,m in meta.items())[:8],sorted((m['ratio'],c) for c,m in meta.items())[-12:])
print('low fill',[(c,m['fill']) for c,m in meta.items() if m['fill']<0.8])
print('panel',[c for c,m in meta.items() if m['tone']=='panel'])
