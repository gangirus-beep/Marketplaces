"""Пилот: плавный силуэт палитр, стаканов, кейсов и покрытий.
RGB не изменяется. Отверстия палитр и ручек вырезаются отдельно;
остальные светлые области внутри изделия остаются непрозрачными.
Запуск из корня генератора после recut_shape.py, с pilot/texts.py.
"""
import json,io,pathlib,cv2,numpy as np
from PIL import Image
from scipy import ndimage as ndi
import srcload
PAL={'190303':(.382,.266),'227805':(.258,.365),'227806':(.583,.235),'227808':(.288,.516),'227809':(.112,.667),'192352':(.628,.194),'192353':(.610,.227),'192354':(.607,.235)}
CASES={'664631','664632','664633','665670','665671','665673','665674'}
CUPS={'191309','191311','191313','191314','191733','191734','192127'}
MATS={'227057','228115','228116','272373','272374','272375'}
TARGET=set(PAL)|CASES|CUPS|MATS

def make(g,meta):
 c=g['code'];im,_=srcload.load(c,g['U']);a=np.asarray(im);H,W=a.shape[:2]
 near=(a.min(2)>=250).astype('uint8');n,lab,st,cent=cv2.connectedComponentsWithStats(near)
 border=set(lab[0])|set(lab[-1])|set(lab[:,0])|set(lab[:,-1]);border.discard(0)
 m=(~np.isin(lab,list(border))).astype('uint8')
 # Close small edge cracks, smooth the silhouette, then trace curves rather than a convex hull.
 k=5 if max(W,H)>=1200 else 3
 m=cv2.morphologyEx(m,cv2.MORPH_CLOSE,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(k,k)))
 m=(cv2.GaussianBlur(m.astype(np.float32),(0,0),2.0)>.5).astype('uint8')
 contours,_=cv2.findContours(m,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
 mask=np.zeros((H,W),np.uint8)
 for co in contours:
  if cv2.contourArea(co)<.0008*W*H:continue
  co=cv2.convexHull(co) if c in MATS else co
  p=cv2.approxPolyDP(co,2.0,True);cv2.fillPoly(mask,[p],255)
 # One-pixel inward edge avoids the supplier's white shadow without cutting thin handles.
 mask=cv2.erode(mask,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(3,3)))
 removed=[]
 if c in PAL:
  cx,cy=PAL[c];candidates=[i for i in range(1,n) if i not in border and st[i,4]>5000 and np.linalg.norm(cent[i]/[W,H]-[cx,cy])<.05]
  assert len(candidates)==1,(c,candidates)
  i=candidates[0];ho=(lab==i).astype('uint8');cont,_=cv2.findContours(ho,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)
  ellipse=cv2.fitEllipse(max(cont,key=cv2.contourArea));center,size,angle=ellipse
  # Fit to the white interior of the opening; keep the moulded rim intact.
  cv2.ellipse(mask,(center,(size[0]+1,size[1]+1),angle),0,-1);removed.append('thumb')
  if c=='227809':
   for i in range(1,n):
    xx,yy=cent[i]/[W,H]
    if i not in border and .265<yy<.275 and .20<xx<.85 and st[i,4]>200:
     ho=(lab==i).astype('uint8');cont,_=cv2.findContours(ho,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE);co=max(cont,key=cv2.contourArea)
     if len(co)>=5:
      ellipse=cv2.fitEllipse(co)
      if min(ellipse[1])/max(ellipse[1])>.75:
       cv2.ellipse(mask,ellipse,0,-1);removed.append('brush')
 if c in CASES:
  ymax=.35 if c in {'665673','665674'} else .20
  for i in range(1,n):
   xx,yy=cent[i]/[W,H]
   if i not in border and .3<xx<.7 and yy<ymax and st[i,4]>5000:
    ho=(lab==i).astype('uint8');co,_=cv2.findContours(ho,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
    for cc in co:cv2.fillPoly(mask,[cv2.approxPolyDP(cc,1.5,True)],0)
    removed.append('handle')
 alpha=cv2.GaussianBlur(mask,(0,0),.65);ys,xs=np.where(mask>127)
 box=(max(0,xs.min()-2),max(0,ys.min()-2),min(W,xs.max()+3),min(H,ys.max()+3))
 out=im.copy();out.putalpha(Image.fromarray(alpha));out=out.crop(box)
 if max(out.size)>1200:out.thumbnail((1200,1200),Image.Resampling.LANCZOS)
 buf=io.BytesIO();out.save(buf,format='PNG');pathlib.Path(f'cut/{c}.png').write_bytes(buf.getvalue())
 meta[c].update(w=out.width,h=out.height,ratio=round(out.width/out.height,4),shape='curve+holes' if removed else 'curve',holes=removed)
 print(c,meta[c]['shape'],removed,flush=True)

if __name__=='__main__':
 goods=json.load(open('goods.json'));meta=json.load(open('cutmeta.json'))
 for g in goods:
  if g['code'] in TARGET:make(g,meta)
 pathlib.Path('cutmeta.json').write_text(json.dumps(meta,indent=1))
