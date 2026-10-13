# Шаг 6. Последние фото ID ВХ_квант_last.jpg: кадр W (у слайдов Рельефа — после обрезки по контуру, srcload.py), сетка по кванту на белом фоне. У товаров без кадра W (ассорти с коллажем) фото не создаётся
import os; os.makedirs('out/last',exist_ok=True)
import json, numpy as np, math
from PIL import Image
from scipy import ndimage as ndi
goods=json.load(open('goods.json'))
CW,CH=900,1200
import srcload
def clean_crop(code,n):
    im,rects=srcload.load(code,n)
    if code in ['359588','359590'] and n==2: im=im.crop((0,0,im.width//2,im.height))
    if rects:      # слайд Рельефа: кадр уже обрезан по контуру товара, берётся прямоугольник обложки целиком
        (x0,y0,x1,y1)=rects[0]; return im.crop((x0,y0,x1,y1))
    a=np.asarray(im).astype(int)
    near=a.min(axis=2)>=249
    lab,k=ndi.label(near)
    border=set(lab[0,:])|set(lab[-1,:])|set(lab[:,0])|set(lab[:,-1]); border.discard(0)
    bg=np.isin(lab,list(border))
    soft=ndi.gaussian_filter(bg.astype(float),0.8)[...,None]
    b=(a*(1-soft)+255*soft).round().astype('uint8')
    # рамка товара — по оболочке (recut_hull.mask): у упаковок с белым вкладышем и прозрачных пакетов тонкий край пакета иначе теряется и кадр обрезается по вкладышу
    import recut_hull
    fg=recut_hull.mask(code,n,False)[3]
    if code in ['359588','359590'] and n==2: fg=fg[:,:fg.shape[1]//2]
    ys,xs=np.where(fg)
    box=(max(0,xs.min()-2),max(0,ys.min()-2),min(im.width,xs.max()+3),min(im.height,ys.max()+3))
    return Image.fromarray(b).crop(box)
def grid(q,A,M=36):
    G=20 if q<=20 else 12 if q<=60 else 7
    W,H=CW-2*M,CH-2*M; best=None
    for r in range(1,q+1):
        c=math.ceil(q/r); w=min((W-(c-1)*G)/c, A*(H-(r-1)*G)/r); s=w*(1.2 if q%r==0 else 1)
        if best is None or s>best[0]+0.5: best=(s,r,w)
    _,rows,w=best; w=int(w); h=round(w/A); base,extra=divmod(q,rows)
    y=round((CH-(rows*h+(rows-1)*G))/2); pos=[]; lay=[]
    for i in range(rows):
        n=base+(1 if i<extra else 0); x=round((CW-(n*w+(n-1)*G))/2); lay.append(n)
        pos+= [(x+j*(w+G),y) for j in range(n)]; y+=h+G
    return w,h,pos,lay
def layname(lay):
    return f'{lay[0]} × {len(lay)}' if len(set(lay))==1 and len(lay)>1 else '+'.join(map(str,lay))
if __name__=='__main__':
    lastlog=[]
    for x in goods:
        if not x['W']: continue
        item=clean_crop(x['code'],x['W']); A=item.width/item.height
        for c in x['cards']:
            q=c['quant']; w,h,pos,lay=grid(q,A)
            t=item.resize((w,h),Image.LANCZOS); S=Image.new('RGB',(CW,CH),(255,255,255))
            for p in pos: S.paste(t,p)
            name=f"{c['idvh']}_{q}_last.jpg"; buf=__import__('io').BytesIO(); S.save(buf,format='JPEG',quality=92); __import__('pathlib').Path('out/last/'+name).write_bytes(buf.getvalue())
            lastlog.append(dict(file=name,code=x['code'],quant=q,src=x['W'],layout=layname(lay),item_w=w,scale=round(w/item.width,2)))
    json.dump(lastlog,open('lastlog.json','w'),ensure_ascii=False,indent=1)
    import collections
    print('last',len(lastlog),'min item w',min(l['item_w'] for l in lastlog),'max scale',max(l['scale'] for l in lastlog))
    print(sorted({(l['quant'],l['layout'],l['item_w']) for l in lastlog}))
