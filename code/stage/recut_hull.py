# Шаг 3в (по необходимости). Повторная вырезка «по оболочке» — для упаковок с белым вкладышем и прозрачных обложек (этап 3):
# обычная вырезка cut.py принимает белое поле вкладыша или прозрачную середину обложки за фон и выедает товар с краёв.
# Маска дополняется по строкам и по столбцам (между крайними точками товара), у коллажей — отдельно по каждой части.
# python3 recut_hull.py            — только отчёт: у каких товаров оболочка добавляет больше 1 % площади
# python3 recut_hull.py код код …  — перевырезать эти товары
import json, sys, numpy as np
from PIL import Image, ImageFilter
from scipy import ndimage as ndi
import srcload
goods={x['code']:x for x in json.load(open('goods.json'))}; meta=json.load(open('cutmeta.json'))
def hull(m):
    out=m.copy(); ys,xs=np.where(m)
    if not len(ys): return out
    rows=np.where(m.any(axis=1))[0]
    for y in rows:
        r=np.where(m[y])[0]; out[y,r[0]:r[-1]+1]=True
    cols=np.where(m.any(axis=0))[0]
    for x in cols:
        c=np.where(m[:,x])[0]; out[c[0]:c[-1]+1,x]=True
    return out
def mask(code,n,percomp):
    im,rects=srcload.load(code,n); a=np.asarray(im).astype(int)
    near=a.min(axis=2)>=250; lab,k=ndi.label(near)
    border=set(lab[0,:])|set(lab[-1,:])|set(lab[:,0])|set(lab[:,-1]); border.discard(0)
    fg=~np.isin(lab,list(border)); fg=ndi.binary_opening(fg,iterations=1)
    l2,n2=ndi.label(fg); sz=ndi.sum(fg,l2,range(1,n2+1)); keep=[i+1 for i,s in enumerate(sz) if s>0.002*fg.size]
    fg=np.isin(l2,keep); base=ndi.binary_fill_holes(fg)
    if percomp:
        big=[i for i in keep if sz[i-1]>0.03*fg.size]; out=np.zeros_like(fg)
        for i in big: out|=hull(l2==i)
        out|=base & ndi.binary_dilation(out,iterations=3)      # мелкие части (этикетка) остаются, если лежат внутри крупных
        nc=len(big)
    else:
        out=hull(base); nc=1
    return im,a,base,ndi.binary_fill_holes(out),nc
if __name__=='__main__':
    codes=sys.argv[1:]
    if not codes:
        rep=[]
        for c,x in goods.items():
            if c in srcload.SLIDE: continue
            pc=x['assorti']=='ассорти' or (meta[c]['ncomp']>1 and x['assorti']!='нет')
            im,a,base,out,nc=mask(c,x['U'],pc); add=(out.sum()-base.sum())/max(1,out.sum())
            if add>0.01: rep.append((round(float(add),3),c,nc))
        print(len(rep),sorted(rep,reverse=True))
    for c in codes:
        x=goods[c]; pc=x['assorti']=='ассорти' or (meta[c]['ncomp']>1 and x['assorti']!='нет')
        im,a,base,fg,nc=mask(c,x['U'],pc); fg=ndi.binary_erosion(fg,iterations=1)
        alpha=Image.fromarray((fg*255).astype('uint8')).filter(ImageFilter.GaussianBlur(0.9))
        ys,xs=np.where(fg); box=(max(0,xs.min()-3),max(0,ys.min()-3),min(im.width,xs.max()+4),min(im.height,ys.max()+4))
        rgba=im.copy(); rgba.putalpha(alpha); rgba=rgba.crop(box)
        px=a[fg]; lum=(0.299*px[:,0]+0.587*px[:,1]+0.114*px[:,2]); sat=(px.max(axis=1)-px.min(axis=1))
        light=float((lum>215).mean()); gray=float((sat<28).mean())
        if max(rgba.size)>1200: rgba.thumbnail((1200,1200),Image.LANCZOS)
        rgba.save(f'cut/{c}.png')
        meta[c].update(w=rgba.size[0],h=rgba.size[1],ratio=round(rgba.size[0]/rgba.size[1],4),lum=round(float(lum.mean()),1),light=round(light,2),gray=round(gray,2),ncomp=nc,hull=True,
                       fill=round(float(fg[box[1]:box[3],box[0]:box[2]].mean()),2))
        meta[c]['tone']='panel' if (meta[c]['lum']>200 and light>0.55 and gray>0.6) else 'light'
        print(c,meta[c])
    json.dump(meta,open('cutmeta.json','w'),indent=1)
