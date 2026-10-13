# Шаг 3д. Вырезка «тело по фигуре + держатель по цвету» для товаров из прямоугольного белого или прозрачного тела и цветной ленты,
# шнурка, рулетки или клипсы (бейджи; проверка после проходки П1, 06.10.2026). recut_shape.py у таких товаров даёт keep или hull
# с кусками белого фона внутри петли ленты. Здесь: тело товара — четырёхугольник с заходом внутрь (как quad в recut_shape.py),
# остальное (лента, рулетка, клипса) — маска по небелым пикселям со сглаженным краем; белое внутри петли остаётся фоном.
#   python3 recut_combo.py код …   → cut/КОД.png, в cutmeta.json shape='combo:quad|rot|hull' (тело найдено) или 'content' (тела нет: лента, рулетка, цветной бейдж)
import json, sys, numpy as np, cv2
from PIL import Image
from scipy import ndimage as ndi
import srcload, recut_shape as R
def combo(code,n=None,out='cut'):
    x=R.goods[code]; im,_=srcload.load(code,n or x['U']); a=np.asarray(im).astype(int); H,W=a.shape[:2]; d=4 if max(im.size)>=1200 else 3
    mn=a.min(axis=2); sat=a.max(axis=2)-mn
    def enclosed(content):
        lab,k=ndi.label(~content); border=set(lab[0,:])|set(lab[-1,:])|set(lab[:,0])|set(lab[:,-1]); border.discard(0)
        return (~content)&~np.isin(lab,list(border))
    content=mn<244
    content=ndi.binary_opening(content,iterations=1)
    c2=ndi.binary_opening(mn<250,iterations=1)
    encl=enclosed(ndi.binary_closing(c2,iterations=3)); le,ne=ndi.label(encl)
    if ne:
        sz=ndi.sum(encl,le,range(1,ne+1)); content|=np.isin(le,[i+1 for i,s_ in enumerate(sz) if s_<0.003*H*W])   # мелкие белые детали внутри товара
    col=ndi.binary_opening((sat>50)|(mn<120),iterations=1)                        # цветное и тёмное: лента, шнурок, рулетка, цветная рамка
    light=c2&~ndi.binary_dilation(col,iterations=4)                               # светлое: кромка прозрачного тела, вкладыш, пакет
    light=ndi.binary_closing(np.pad(light,24),iterations=10)[24:-24,24:-24]
    Q=np.zeros((H,W),np.uint8); meth='content'; cands=[]
    def rectness(m):
        pts=np.column_stack(np.where(m)[::-1]).astype(np.float32)[::9]; (cx,cy),(rw,rh),ang=cv2.minAreaRect(np.ascontiguousarray(pts))
        return m.sum()/(rw*rh+1),ang
    lb,nb=ndi.label(light)
    if nb:                                                                        # способ А: светлое тело-прямоугольник (кромка, вкладыш, пакет)
        m=R.hullfill(lb==1+int(np.argmax(ndi.sum(light,lb,range(1,nb+1))))); r,ang=rectness(m)
        if m.sum()>0.04*H*W and r>=0.8: cands.append((m,ang))
    if not cands and ne:                                                          # способ Б: белое поле внутри цветной рамки или кромки
        wh=np.isin(le,[i+1 for i,s_ in enumerate(sz) if s_>=0.003*H*W]); wh=ndi.binary_closing(np.pad(wh,24),iterations=10)[24:-24,24:-24]
        lw,nw=ndi.label(wh)
        for i in sorted(range(1,nw+1),key=lambda i:-(lw==i).sum())[:3]:
            m=R.hullfill(lw==i); r,ang=rectness(m)
            if m.sum()>0.03*H*W and r>=0.85: cands.append((m,ang)); break
    if cands:
        m,ang=cands[0]; sm,al,info=R.shape_of(a,m,d)
        if al is None: sm,al,info=R.shape_of(a,m,d,'rot' if min(abs(ang)%90,90-abs(ang)%90)>4 else 'quad')
        Q=al; meth='combo:'+sm
        band=(cv2.dilate(Q,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(25,25)))>127)&(Q<128)
        content&=~(band&(mn>=185)&(sat<45))                                       # рваная светлая кромка тела снаружи фигуры
    lc,nc=ndi.label(content)
    if nc:
        sz=ndi.sum(content,lc,range(1,nc+1)); content=np.isin(lc,[i+1 for i,s in enumerate(sz) if s>0.0004*H*W])
    g=cv2.GaussianBlur(content.astype(np.float32),(0,0),1.6)>0.55
    A=np.maximum(Q,(g*255).astype(np.uint8)); al=cv2.GaussianBlur(A,(0,0),0.7); fg=A>127; ys,xs=np.where(fg)
    box=(max(0,xs.min()-2),max(0,ys.min()-2),min(im.width,xs.max()+3),min(im.height,ys.max()+3))
    rgba=im.copy(); rgba.putalpha(Image.fromarray(al)); rgba=rgba.crop(box)
    if max(rgba.size)>1200: rgba.thumbnail((1200,1200),Image.LANCZOS)
    import io, pathlib
    buf=io.BytesIO(); rgba.save(buf,format='PNG'); pathlib.Path(f'{out}/{code}.png').write_bytes(buf.getvalue())
    px=a[fg]; lum=(0.299*px[:,0]+0.587*px[:,1]+0.114*px[:,2]); st=(px.max(axis=1)-px.min(axis=1))
    return meth,dict(w=rgba.size[0],h=rgba.size[1],ratio=round(rgba.size[0]/rgba.size[1],4),lum=round(float(lum.mean()),1),light=round(float((lum>215).mean()),2),gray=round(float((st<28).mean()),2),
                     ncomp=1,fill=round(float(fg[box[1]:box[3],box[0]:box[2]].mean()),2),shape=meth)
if __name__=='__main__':
    meta=json.load(open('cutmeta.json'))
    for c in sys.argv[1:]:
        meth,m=combo(c); meta.setdefault(c,{}).update(m); print(c,meth)
    json.dump(meta,open('cutmeta.json','w'),indent=1)
