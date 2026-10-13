# Шаг 3а (по необходимости). Повторная вырезка построчно — для товаров, у которых на самой обложке есть белая полоса до края
# (ОФИСМАГ на гребне 402793, 402794, 402797): обычная вырезка cut.py считает полосу фоном и делит товар на части.
# Признак: в cut.py у товара не «ассорти» ncomp > 1 или fill < 0.9. Запуск: python3 recut_rows.py 402793 402794 402797
import json, sys, numpy as np
from PIL import Image, ImageFilter
from scipy import ndimage as ndi
goods={x['code']:x for x in json.load(open('goods.json'))}; meta=json.load(open('cutmeta.json'))
def recut(code,n):
    im=Image.open(f'src/{code}_{n:02d}.jpg').convert('RGB'); a=np.asarray(im).astype(int)
    near=a.min(axis=2)>=250; lab,k=ndi.label(near)
    border=set(lab[0,:])|set(lab[-1,:])|set(lab[:,0])|set(lab[:,-1]); border.discard(0)
    fg=~np.isin(lab,list(border)); fg=ndi.binary_opening(fg,iterations=1)
    ys,xs=np.where(fg); y0,y1=ys.min(),ys.max()
    L=np.full(im.height,-1); R=np.full(im.height,-1)
    for y in range(y0,y1+1):
        r=np.where(fg[y])[0]
        if len(r): L[y],R[y]=r.min(),r.max()
    w=R-L; seg=w[y0:y1+1]; med=np.median(seg[seg>0]); ok=seg>0.9*med
    mL=int(np.median(L[y0:y1+1][ok])); mR=int(np.median(R[y0:y1+1][ok]))
    out=np.zeros_like(fg)
    for y in range(y0,y1+1):
        l,r=(L[y],R[y]) if w[y]>0.9*med else (mL,mR)      # строка с белой полосой получает типичные границы товара
        out[y,l:r+1]=True
    out=ndi.binary_erosion(out,iterations=1)
    alpha=Image.fromarray((out*255).astype('uint8')).filter(ImageFilter.GaussianBlur(0.9))
    ys,xs=np.where(out); box=(max(0,xs.min()-3),max(0,ys.min()-3),min(im.width,xs.max()+4),min(im.height,ys.max()+4))
    rgba=im.copy(); rgba.putalpha(alpha); rgba=rgba.crop(box)
    if max(rgba.size)>1200: rgba.thumbnail((1200,1200),Image.LANCZOS)
    rgba.save(f'cut/{code}.png')
    meta[code].update(w=rgba.size[0],h=rgba.size[1],ratio=round(rgba.size[0]/rgba.size[1],4),ncomp=1,fill=round(float(out[box[1]:box[3],box[0]:box[2]].mean()),2)); print(code,meta[code])
for c in sys.argv[1:]: recut(c,goods[c]['U'])
json.dump(meta,open('cutmeta.json','w'),indent=1)
