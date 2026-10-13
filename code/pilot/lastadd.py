import json, numpy as np, math
from PIL import Image, ImageFilter
from scipy import ndimage as ndi
goods=json.load(open('goods.json'))
CW,CH=900,1200
def clean_crop(path):
    im=Image.open(path).convert('RGB'); a=np.asarray(im).astype(int)
    near=a.min(axis=2)>=249
    lab,k=ndi.label(near)
    border=set(lab[0,:])|set(lab[-1,:])|set(lab[:,0])|set(lab[:,-1]); border.discard(0)
    bg=np.isin(lab,list(border))
    soft=ndi.gaussian_filter(bg.astype(float),0.8)[...,None]
    b=(a*(1-soft)+255*soft).round().astype('uint8')
    fg=ndi.binary_opening(~bg,iterations=2); ys,xs=np.where(fg)
    box=(max(0,xs.min()-2),max(0,ys.min()-2),min(im.width,xs.max()+3),min(im.height,ys.max()+3))
    return Image.fromarray(b).crop(box)
def grid(q,A,M=36,G=20):
    W,H=CW-2*M,CH-2*M; best=None
    for r in range(1,q+1):
        c=math.ceil(q/r); w=min((W-(c-1)*G)/c, A*(H-(r-1)*G)/r); s=w*(1.15 if q%r==0 else 1)
        if best is None or s>best[0]+0.5: best=(s,r,w)
    _,rows,w=best; w=int(w); h=round(w/A); base,extra=divmod(q,rows)
    y=round((CH-(rows*h+(rows-1)*G))/2); pos=[]; lay=[]
    for i in range(rows):
        n=base+(1 if i<extra else 0); x=round((CW-(n*w+(n-1)*G))/2); lay.append(n)
        pos+= [(x+j*(w+G),y) for j in range(n)]; y+=h+G
    return w,h,pos,lay
lastlog=[]
for x in goods:
    item=clean_crop(f"src/{x['code']}_{x['W']:02d}.jpg"); A=item.width/item.height
    for c in x['cards']:
        q=c['quant']; w,h,pos,lay=grid(q,A)
        t=item.resize((w,h),Image.LANCZOS); S=Image.new('RGB',(CW,CH),(255,255,255))
        for p in pos: S.paste(t,p)
        name=f"{c['idvh']}_{q}_last.jpg"; S.save('out/last/'+name,quality=92)
        lastlog.append(dict(file=name,code=x['code'],quant=q,src=x['W'],layout='+'.join(map(str,lay)),item_w=w,scale=round(w/item.width,2)))
json.dump(lastlog,open('lastlog.json','w'),ensure_ascii=False,indent=1)
print('last',len(lastlog),'min item w',min(l['item_w'] for l in lastlog),'max scale',max(l['scale'] for l in lastlog))
# ---- доп. фото
addlog=[]
def is_white(a):
    fr=np.concatenate([a[:3].reshape(-1,3),a[-3:].reshape(-1,3),a[:,:3].reshape(-1,3),a[:,-3:].reshape(-1,3)])
    return (fr.min(axis=1)>=247).mean()
for x in goods:
    for n in x['V']:
        p=f"src/{x['code']}_{n:02d}.jpg"; im=Image.open(p).convert('RGB'); a=np.asarray(im)
        name=f"{x['idvh']}_ADD_{n:02d}.jpg"; wf=is_white(a)
        if wf>=0.97:
            item=clean_crop(p); M=40
            s=min((CW-2*M)/item.width,(CH-2*M)/item.height, 1.6)
            t=item.resize((max(1,round(item.width*s)),max(1,round(item.height*s))),Image.LANCZOS)
            S=Image.new('RGB',(CW,CH),(255,255,255)); S.paste(t,((CW-t.width)//2,(CH-t.height)//2)); mode='белый фон: поля обрезаны, товар вписан'
            sc=round(s,2)
        else:
            s=min(CW/im.width,CH/im.height); t=im.resize((round(im.width*s),round(im.height*s)),Image.LANCZOS); sc=round(s,2)
            top=np.asarray(t)[:6].reshape(-1,3).astype(float); bot=np.asarray(t)[-6:].reshape(-1,3).astype(float)
            y0=(CH-t.height)//2
            if top.std(axis=0).max()<9 and bot.std(axis=0).max()<9:
                S=Image.new('RGB',(CW,CH),tuple(int(v) for v in np.median(top,axis=0)))
                S.paste(Image.new('RGB',(CW,CH-y0-t.height+2),tuple(int(v) for v in np.median(bot,axis=0))),(0,y0+t.height-2)); mode='слайд: поля в цвет края'
            else:
                cov=max(CW/im.width,CH/im.height); B=im.resize((round(im.width*cov),round(im.height*cov)),Image.BILINEAR)
                B=B.crop(((B.width-CW)//2,(B.height-CH)//2,(B.width-CW)//2+CW,(B.height-CH)//2+CH)).filter(ImageFilter.GaussianBlur(28))
                S=B; mode='слайд: размытые поля'
            S.paste(t,((CW-t.width)//2,y0))
        S.save('out/add/'+name,quality=90)
        addlog.append(dict(file=name,code=x['code'],idvh=x['idvh'],n=n,src_size=f'{im.width}×{im.height}',mode=mode,scale=sc))
json.dump(addlog,open('addlog.json','w'),ensure_ascii=False,indent=1)
import collections; print('add',len(addlog),collections.Counter(l['mode'] for l in addlog),'max scale',max(l['scale'] for l in addlog))
