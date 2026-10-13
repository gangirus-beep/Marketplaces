# Шаг 3г. Вырезка «по фигуре» (замечание владельца 06.10.2026 по этапу 3): у белых и прозрачных товаров автоудаление фона
# даёт ямы и торчащие куски фона. Вместо контура берётся фигура из прямых линий с заходом в товар на несколько пикселей:
#   quad  — четырёхугольник: к каждой стороне товара подбирается прямая (выбросы — ямы и выступы — отбрасываются), сдвиг внутрь;
#   rot   — то же для товара, лежащего под углом (кадр сначала поворачивается по minAreaRect);
#   tight — непрозрачный цветной товар сложной формы: плотная маска по цвету, сглаженный контур, заход внутрь;
#   hull  — выпуклый многоугольник с заходом внутрь;  keep — фигура не подошла, оставлена прежняя вырезка (смотреть глазами);
#   steps — ступенчатая фигура для коллажа внахлёст (перевыпуск этапа 1, 06.10.2026): у коллажа «четыре тетради по углам и одна
#           в центре» между тетрадями остаются выемки белого фона; четырёхугольник захватывал их целиком (белые прямоугольники
#           на обложке). Силуэт коллажа выпрямляется прямоугольным ядром (ямы уже 2 % кадра закрываются, выступы уже 4 % срезаются),
#           стороны остаются прямыми, выемки — фоном; заход в товар тот же;
#   cross — тот же коллаж, но у светлой тетради фон «проел» яму шире 2 % кадра (белая обложка сливается с фоном):
#           фигура — объединение пяти прямоугольников (четыре тетради по углам одного размера и центральная); размер тетради —
#           медиана четырёх замеров по выемкам, поэтому яма у одной тетради не мешает. Берётся сам, когда ступенчатая фигура
#           теряет больше 2 % площади прямоугольников и не выступает за них (у «Smart Cover» с отогнутой обложкой остаётся steps).
#   У коллажа на тёмной подложке (тон panel) заход в товар 9 px вместо 4: светлая тень вокруг тетрадей на тёмном видна каймой.
# У коллажей (ассорти и состав набора) фигура подбирается для каждой части. Слайды Рельефа (srcload) — прямоугольник с заходом.
# python3 recut_shape.py            — все товары;   python3 recut_shape.py код …  — только эти
import json, sys, numpy as np, cv2
from PIL import Image
from scipy import ndimage as ndi
import srcload
goods={x['code']:x for x in json.load(open('goods.json'))}; meta=json.load(open('cutmeta.json'))
try:
    import texts; COLL={c for c,x in goods.items() if x['assorti']=='ассорти'}|set(getattr(texts,'COLLAGE3',()))|set(getattr(texts,'SHAPE_PARTS',()))
    FORCE=getattr(texts,'SHAPE_FORCE',{}); TONE=getattr(texts,'TONE_FORCE',{})
except Exception: COLL={c for c,x in goods.items() if x['assorti']=='ассорти'}; FORCE={}; TONE={}
def base_mask(a):
    near=a.min(axis=2)>=250; lab,k=ndi.label(near)
    border=set(lab[0,:])|set(lab[-1,:])|set(lab[:,0])|set(lab[:,-1]); border.discard(0)
    fg=~np.isin(lab,list(border)); fg=ndi.binary_opening(fg,iterations=1)
    l2,n2=ndi.label(fg); sz=ndi.sum(fg,l2,range(1,n2+1))
    return l2,sz
def hullfill(m):
    out=m.copy()
    for y in np.where(m.any(axis=1))[0]:
        r=np.where(m[y])[0]; out[y,r[0]:r[-1]+1]=True
    for x in np.where(m.any(axis=0))[0]:
        c=np.where(m[:,x])[0]; out[c[0]:c[-1]+1,x]=True
    return ndi.binary_fill_holes(out)
def fit(t,v):
    # прямая v=a*t+b с отбрасыванием выбросов; возвращает a,b и долю точек на прямой
    a,b=0.0,float(np.median(v)); keep=np.ones(len(v),bool)
    for _ in range(4):
        r=v-(a*t+b); mad=np.median(np.abs(r[keep]-np.median(r[keep]))) if keep.any() else 0
        keep=np.abs(r)<=max(2.5,2.5*1.4826*mad)
        if keep.sum()<8: break
        a,b=np.polyfit(t[keep],v[keep],1)
    r=v-(a*t+b); return a,b,float((np.abs(r)<=3.5).mean())
def quad(m,d):
    ys,xs=np.where(m); y0,y1,x0,x1=ys.min(),ys.max(),xs.min(),xs.max(); h=y1-y0+1; w=x1-x0+1
    rows=np.arange(y0+int(.12*h),y1-int(.12*h)+1); cols=np.arange(x0+int(.12*w),x1-int(.12*w)+1)
    if len(rows)<12 or len(cols)<12: rows=np.arange(y0+int(.2*h),y1-int(.2*h)+1); cols=np.arange(x0+int(.05*w),x1-int(.05*w)+1)
    rows=rows[m[rows].any(axis=1)]; cols=cols[m[:,cols].any(axis=0)]
    L=np.array([np.argmax(m[y]) for y in rows]); R=np.array([m.shape[1]-1-np.argmax(m[y,::-1]) for y in rows])
    T=np.array([np.argmax(m[:,x]) for x in cols]); B=np.array([m.shape[0]-1-np.argmax(m[::-1,x]) for x in cols])
    aL,bL,qL=fit(rows.astype(float),L.astype(float)); aR,bR,qR=fit(rows.astype(float),R.astype(float))
    aT,bT,qT=fit(cols.astype(float),T.astype(float)); aB,bB,qB=fit(cols.astype(float),B.astype(float))
    def corner(av,bv,ah,bh):      # x=av*y+bv (вертикальная сторона), y=ah*x+bh (горизонтальная)
        y=(ah*bv+bh)/(1-ah*av); return [av*y+bv,y]
    def poly(dd): return np.array([corner(aL,bL+dd,aT,bT+dd),corner(aR,bR-dd,aT,bT+dd),corner(aR,bR-dd,aB,bB-dd),corner(aL,bL+dd,aB,bB-dd)],np.float32)
    p0=poly(0); P=np.zeros(m.shape,np.uint8); cv2.fillPoly(P,[np.round(p0).astype(np.int32)],1)
    cutoff=float((m&(P==0)).sum()/m.sum()); empty=float(((P==1)&~hullfill(m)).sum()/max(1,P.sum()))
    return poly(d),min(qL,qR,qT,qB),cutoff,empty
def draw(shape,polys,r=5):
    S=4; M=np.zeros((shape[0]*S,shape[1]*S),np.uint8)
    for p in polys: cv2.fillPoly(M,[np.round(p*S).astype(np.int32)],255)
    k=cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(2*r*S+1,2*r*S+1)); M=cv2.morphologyEx(M,cv2.MORPH_OPEN,k)      # скруглить углы
    return cv2.resize(M,(shape[1],shape[0]),interpolation=cv2.INTER_AREA)
def shape_of(a,m,d,force=None):
    # возвращает (метод, альфа uint8)
    H,W=m.shape
    if force in (None,'quad'):
        p,q,cut,emp=quad(m,d)
        if force=='quad' or (q>=0.55 and cut<=0.02 and emp<=0.02): return 'quad',draw(m.shape,[p]),(round(q,2),round(cut,3),round(emp,3))
    if force in (None,'rot'):
        cnt=np.column_stack(np.where(m)[::-1]).astype(np.float32); (cx,cy),(rw,rh),ang=cv2.minAreaRect(np.ascontiguousarray(cnt[::7]))
        Rm=cv2.getRotationMatrix2D((cx,cy),ang,1.0); mr=cv2.warpAffine(m.astype(np.uint8),Rm,(W,H),flags=cv2.INTER_NEAREST)>0
        if mr.sum()>0.9*m.sum():
            p,q,cut,emp=quad(mr,d)
            if force=='rot' or (q>=0.55 and cut<=0.03 and emp<=0.03):
                inv=cv2.invertAffineTransform(Rm); pb=(np.c_[p,np.ones(4)]@inv.T).astype(np.float32); return 'rot',draw(m.shape,[pb]),(round(q,2),round(cut,3),round(emp,3))
    px=a[m]; sat=(px.max(axis=1)-px.min(axis=1))
    if force=='tight' or (force is None and float((sat>60).mean())>0.85):
        t=((a.max(axis=2)-a.min(axis=2))>45)|(a.mean(axis=2)<150); t=ndi.binary_opening(t,iterations=2); l,n=ndi.label(t)
        if n:
            sz=ndi.sum(t,l,range(1,n+1)); t=ndi.binary_fill_holes(l==(1+int(np.argmax(sz))))
            t=ndi.binary_erosion(t,iterations=d-1); g=cv2.GaussianBlur(t.astype(np.float32),(0,0),2.2)>0.5
            return 'tight',(g*255).astype(np.uint8),(round(float((sat>60).mean()),2),)
    hull=cv2.convexHull(np.ascontiguousarray(np.column_stack(np.where(m)[::-1]).astype(np.int32)[::5])); Hm=np.zeros(m.shape,np.uint8); cv2.fillPoly(Hm,[hull],1)
    sol=float(m.sum()/max(1,Hm.sum()))
    if force=='hull' or (force is None and sol>=0.95):
        ap=cv2.approxPolyDP(hull,2.0,True).reshape(-1,2).astype(np.float32); M=draw(m.shape,[ap],r=3)
        M=cv2.erode(M,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(2*d+1,2*d+1))); return 'hull',M,(round(sol,3),)
    return 'keep',None,(round(sol,3),)
def steps(S,d):
    # S — силуэт коллажа (дыры залиты); возвращает альфу uint8
    ys,xs=np.where(S); k=max(9,int(round(max(ys.max()-ys.min(),xs.max()-xs.min())*0.02))|1); P=2*k+8
    A=np.pad(S.astype(np.uint8),P)
    A=cv2.morphologyEx(A,cv2.MORPH_CLOSE,np.ones((k,k),np.uint8)); A=cv2.morphologyEx(A,cv2.MORPH_OPEN,np.ones((2*k+1,2*k+1),np.uint8))
    A=cv2.erode(A,np.ones((2*d+1,2*d+1),np.uint8))[P:-P,P:-P]
    Sx=4; r=5; M=cv2.resize(A*255,(A.shape[1]*Sx,A.shape[0]*Sx),interpolation=cv2.INTER_NEAREST)
    M=cv2.morphologyEx(M,cv2.MORPH_OPEN,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(2*r*Sx+1,2*r*Sx+1)))      # скруглить углы, как у draw()
    return cv2.resize(M,(A.shape[1],A.shape[0]),interpolation=cv2.INTER_AREA)
def _notch(p,across):
    n=len(p); deep=p>0.05*across; c=n//2
    if not deep[c]:
        idx=np.where(deep[int(n*.3):int(n*.7)])[0]
        if not len(idx): return None
        c=int(n*.3)+idx[len(idx)//2]
    a=c
    while a>0 and deep[a-1]: a-=1
    b=c
    while b<n-1 and deep[b+1]: b+=1
    m=max(2,(b-a)//5)
    if b-a+1<=2*m: return None
    return a,n-1-b,float(np.median(p[a+m:b-m+1]))
def cross(S,d):
    # S — силуэт коллажа «четыре по углам и одна в центре»; возвращает (альфа uint8, разброс замеров) или None
    ys,xs=np.where(S); y0,y1,x0,x1=ys.min(),ys.max(),xs.min(),xs.max(); B=S[y0:y1+1,x0:x1+1]; H,W=B.shape
    nt,nb,nl,nr=_notch(np.argmax(B,axis=0),H),_notch(np.argmax(B[::-1],axis=0),H),_notch(np.argmax(B,axis=1),W),_notch(np.argmax(B[:,::-1],axis=1),W)
    if None in (nt,nb,nl,nr): return None
    ws=sorted([nt[0],nt[1],nb[0],nb[1]]); hs=sorted([nl[0],nl[1],nr[0],nr[1]]); w=(ws[1]+ws[2])/2; h=(hs[1]+hs[2])/2
    rects=[(x0,y0,x0+w,y0+h),(x1-w,y0,x1,y0+h),(x0,y1-h,x0+w,y1),(x1-w,y1-h,x1,y1),(x0+nl[2],y0+nt[2],x1-nr[2],y1-nb[2])]
    polys=[np.array([[a+d,b+d],[c-d,b+d],[c-d,e-d],[a+d,e-d]],np.float32) for (a,b,c,e) in rects]
    return draw(S.shape,polys),max((ws[2]-ws[1])/W,(hs[2]-hs[1])/H)
def run(code):
    x=goods[code]; im,rects=srcload.load(code,x['U']); a=np.asarray(im).astype(int); d=4 if max(im.size)>=1200 else 3
    parts=[]
    if rects:
        A=draw(a.shape[:2],[np.array([[x0+d-1,y0+d-1],[x1-d,y0+d-1],[x1-d,y1-d],[x0+d-1,y1-d]],np.float32) for (x0,y0,x1,y1) in rects]); parts=[('rect',())]*len(rects)
    else:
        l2,sz=base_mask(a); keep=[i+1 for i,s in enumerate(sz) if s>0.002*l2.size]
        if code in COLL:
            big=[i for i in keep if sz[i-1]>0.03*l2.size]; ms=[hullfill(l2==i) for i in big]
            # части, лежащие внахлёст, после заполнения сливаются — тогда коллаж идёт одной фигурой
            u=np.zeros(l2.shape,bool)
            for m in ms: u|=m
            lu,nu=ndi.label(u); ms=[lu==i for i in range(1,nu+1)]
            sil=ndi.binary_fill_holes(np.isin(l2,big))
        else: ms=[hullfill(np.isin(l2,keep))]; sil=None
        A=np.zeros(a.shape[:2],np.uint8)
        for m in ms:
            notch=0.0 if sil is None else 1-float((sil&m).sum())/float(m.sum())     # доля белого фона внутри заполненной фигуры
            if FORCE.get(code)=='steps' or (notch>0.015 and FORCE.get(code) in (None,'cross')):
                dd=9 if (TONE.get(code) or meta[code].get('tone'))=='panel' else d
                al=steps(sil&m,dd); meth='steps'; info=(round(notch,3),); cr=cross(sil&m,dd) if FORCE.get(code)!='steps' else None
                if cr is not None:
                    M=cr[0]>127; St=al>127; pits=float((M&~St).sum()/M.sum()); prot=float((St&~M).sum()/M.sum()); info=(round(notch,3),round(pits,4),round(prot,4),round(cr[1],4))
                    if FORCE.get(code)=='cross' or (cr[1]<0.01 and pits>=0.02 and prot<0.005): al=cr[0]; meth='cross'
                parts.append((meth,info)); A=np.maximum(A,al); continue
            meth,al,info=shape_of(a,m,d,FORCE.get(code)); parts.append((meth,info))
            if al is None:
                old=meta[code]; return [('keep',info)]
            A=np.maximum(A,al)
    al=cv2.GaussianBlur(A,(0,0),0.7); fg=A>127; ys,xs=np.where(fg)
    box=(max(0,xs.min()-2),max(0,ys.min()-2),min(im.width,xs.max()+3),min(im.height,ys.max()+3))
    rgba=im.copy(); rgba.putalpha(Image.fromarray(al)); rgba=rgba.crop(box)
    if max(rgba.size)>1200: rgba.thumbnail((1200,1200),Image.LANCZOS)
    import io, pathlib
    buf=io.BytesIO(); rgba.save(buf,format='PNG'); pathlib.Path(f'cut/{code}.png').write_bytes(buf.getvalue())
    px=a[fg]; lum=(0.299*px[:,0]+0.587*px[:,1]+0.114*px[:,2]); sat=(px.max(axis=1)-px.min(axis=1))
    meta[code].update(w=rgba.size[0],h=rgba.size[1],ratio=round(rgba.size[0]/rgba.size[1],4),lum=round(float(lum.mean()),1),light=round(float((lum>215).mean()),2),gray=round(float((sat<28).mean()),2),
                      ncomp=len(parts),fill=round(float(fg[box[1]:box[3],box[0]:box[2]].mean()),2),shape='+'.join(sorted({p[0] for p in parts})))
    return parts
if __name__=='__main__':
    import collections
    codes=sys.argv[1:] or list(goods); C=collections.Counter(); rep=[]
    for c in codes:
        parts=run(c); k='+'.join(sorted({p[0] for p in parts})); C[k]+=1
        if k not in ('quad','rect','steps') or len(codes)<30: rep.append((c,parts))
    json.dump(meta,open('cutmeta.json','w'),indent=1)
    print(dict(C)); [print(r) for r in rep]
