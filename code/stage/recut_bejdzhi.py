# Проверенные вручную границы светлых деталей, координаты в тысячных долях кадра.
# Полные изделия остаются целыми; прямоугольные тела сохраняются, фон внутри петель удалён.
import json,io,numpy as np,cv2
from pathlib import Path
from PIL import Image
from scipy import ndimage as ndi
import srcload
P={
'231156':[[[521,623],[909,612],[969,859],[565,859]]],
'235697':[[[520,620],[900,608],[972,850],[566,850]]],
'235710':[[[242,477],[578,326],[969,762],[619,947]]],
'235761':[[[544,706],[834,600],[953,777],[659,893]]],
'235762':[[[524,705],[813,605],[935,783],[644,901]]],
'235763':[[[467,697],[836,591],[972,766],[589,888]]],
'235764':[[[493,680],[833,566],[958,694],[614,834]]],
'235765':[[[462,696],[817,601],[951,762],[581,870]]],
'236791':[[[75,373],[918,373],[918,963],[75,963]],[[462,38],[549,38],[549,426],[462,426]]],
'284645':[[[192,145],[800,145],[800,978],[192,978]],[[194,47],[360,47],[397,18],[658,18],[681,48],[800,48],[800,145],[194,145]]],
'284660':[[[216,506],[788,506],[788,972],[216,972]],[[459,317],[510,317],[520,541],[449,541]]],
'238241':[[[224,532],[767,532],[767,974],[224,974]],[[465,309],[515,309],[535,553],[454,553]]],
'238242':[[[232,516],[768,516],[768,966],[232,966]],[[466,309],[515,309],[526,538],[455,538]]],
'238243':[[[346,439],[655,439],[655,974],[346,974]],[[475,315],[522,315],[522,454],[475,454]]],
'238244':[[[343,426],[655,426],[655,965],[343,965]],[[473,301],[524,301],[524,445],[473,445]]],
'231906':[[[355,296],[658,161],[893,553],[576,691]]],
'231907':[[[401,615],[765,354],[971,596],[611,863]]],
}
ELL={'238240':(72,53,475,415),'238238':(107,274,542,1020),'238241':(403,29,594,215),'238243':(426,32,593,184)}
# 238238: эллипс тела по фактическому овалу; отдельные прозрачные держатели ниже.
P['238240']=[[[432,424],[490,456],[925,876],[827,949],[489,590]]]
P['238238']=[[[479,450],[575,458],[944,827],[825,924],[508,623]]]
ELL['238238']=(113,214,515,997) # повёрнутый овал рисуется ниже по контуру; здесь не используется
CROP={'235738':(215,400,990,940),'235723':(290,306,985,985),'237463':(20,264,987,749),'359588':(0,0,500,1000),'359590':(0,0,500,1000)}

def apply():
 G={x['code']:x for x in json.load(open('goods.json'))};M=json.load(open('cutmeta.json'))
 P['232152']=[[[583,614],[703,672],[951,868],[873,948]]]
 P['235727']=P['232152']
 for c in list(P)+['238238','238240']:
  im,_=srcload.load(c,G[c]['U']);a=np.asarray(im).astype(int);H,W=a.shape[:2];mn=a.min(2);sat=a.max(2)-mn
  content=ndi.binary_opening(((sat>25)|(mn<210)) if c in ['231906','232152','235727'] else mn<244,iterations=1);lab,n=ndi.label(content);sizes=ndi.sum(content,lab,range(1,n+1));content=np.isin(lab,[i+1 for i,s in enumerate(sizes) if s>0.0002*H*W]);A=np.zeros((H,W),np.uint8)
  for poly in P.get(c,[]):
   pp=np.array(poly,float)*[W/1000,H/1000];cv2.fillPoly(A,[pp.astype(np.int32)],255)
  if c in ELL and c!='238238':
   x0,y0,x1,y1=ELL[c];cv2.ellipse(A,(int((x0+x1)/2000*W),int((y0+y1)/2000*H)),(int((x1-x0)/2000*W),int((y1-y0)/2000*H)),0,0,360,255,-1)
  if c=='238238':
   cv2.fillPoly(A,[np.array([[105,268],[276,168],[421,198],[534,342],[487,482],[339,491],[171,420]])*[W/1000,H/1000]],255) if False else None
  if c in ['232152','235727']:cv2.ellipse(A,(int(.450*W),int(.425*H)),(int(.158*W),int(.158*H)),0,0,360,255,-1)
  if c=='238238':cv2.ellipse(A,(int(.291*W),int(.324*H)),(int(.233*W),int(.160*H)),44,0,360,255,-1)
  # Из внешней полосы убирается светлая бахрома, внутри фигуры сохраняется всё.
  band=(cv2.dilate(A,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(15,15)))>127)&(A<128);content&=~(band&(mn>=180)&(sat<45));A=np.maximum(A,(content*255).astype(np.uint8));
  if c in ['232152','235727']:A[:,:int(.27*W)]=0 # исключить миниатюры упаковки слева
  A=cv2.GaussianBlur(A,(0,0),.7)
  ys,xs=np.where(A>127);bb=(max(0,xs.min()-2),max(0,ys.min()-2),min(W,xs.max()+3),min(H,ys.max()+3));im.putalpha(Image.fromarray(A));im=im.crop(bb);im.thumbnail((1200,1200));b=io.BytesIO();im.save(b,format='PNG');Path(f'cut/{c}.png').write_bytes(b.getvalue());M[c].update(w=im.width,h=im.height,ratio=round(im.width/im.height,4),shape='combo:manual')
 for c,cr in CROP.items():
  im,_=srcload.load(c,G[c]['U']);W,H=im.size;im=im.crop(tuple(round(v*s/1000) for v,s in zip(cr,[W,H,W,H])));a=np.asarray(im).astype(int);fg=ndi.binary_fill_holes(a.min(2)<248);lab,n=ndi.label(fg);sizes=ndi.sum(fg,lab,range(1,n+1));fg=np.isin(lab,[i+1 for i,s in enumerate(sizes) if s>.0005*fg.size]);fg=ndi.binary_fill_holes(fg)
  if c in ['235738','235723']:
   lab,n=ndi.label(fg);sizes=ndi.sum(fg,lab,range(1,n+1));fg=lab==(1+int(np.argmax(sizes)))
  if c in ['359588','359590']: # петля остаётся прозрачной, тело целиком
   raw=a.min(2)<248;lab,n=ndi.label(~raw);border=set(lab[0])|set(lab[-1])|set(lab[:,0])|set(lab[:,-1]);holes=(~raw)&~np.isin(lab,list(border));lh,nh=ndi.label(holes);sz=ndi.sum(holes,lh,range(1,nh+1));
   for i,v in enumerate(sz,1):
    yy,xx=np.where(lh==i)
    if v>0.01*fg.size and yy.max()<.78*im.height:fg[lh==i]=False
  ys,xs=np.where(fg);bb=(max(0,xs.min()-2),max(0,ys.min()-2),min(im.width,xs.max()+3),min(im.height,ys.max()+3));im.putalpha(Image.fromarray(cv2.GaussianBlur((fg*255).astype(np.uint8),(0,0),.7)));im=im.crop(bb);im.thumbnail((1200,1200));b=io.BytesIO();im.save(b,format='PNG');Path(f'cut/{c}.png').write_bytes(b.getvalue());M[c].update(w=im.width,h=im.height,ratio=round(im.width/im.height,4),shape='face:content')
 Path('cutmeta.json').write_text(json.dumps(M,indent=1))
if __name__=='__main__':apply()
