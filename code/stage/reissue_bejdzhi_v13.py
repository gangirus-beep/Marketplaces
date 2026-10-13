"""Stage 4 v13: white photography tiles; protected masks and PyMatting for stacks.
Run in generator root with goods.json and src/. No generative product editing.
"""
import json,time,sys,ast,io
from pathlib import Path
import numpy as np,cv2
from PIL import Image,ImageDraw,ImageFont
from scipy import ndimage as ndi
from pymatting import estimate_alpha_cf,estimate_foreground_ml
sys.path.insert(0,str(Path.cwd()))
import texts,srcload

G=json.load(open('goods.json'));BASE=Path('stage4_v13');BASE.mkdir(exist_ok=True)
for n in ['cut','white','trimap','review','covers','last']: (BASE/n).mkdir(exist_ok=True)
# Existing hand-reviewed body boundaries are seeds, not final silhouettes.
tree=ast.parse(Path('stage/recut_bejdzhi.py').read_text());P={}
for n in tree.body:
 if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='P' for t in n.targets):P=ast.literal_eval(n.value);break
# Full bodies, replacing the old inset rectangles which sliced away plastic.
P['231906']=[[[355,296],[658,161],[893,553],[576,691]]]
P['231907']=[[[401,615],[765,354],[971,596],[611,863]]]
# Reviewed bodies in supplier-image coordinates. White inserts must remain opaque;
# the separate cord mask must not close the open space between ribbons.
for c in ['231153','231155','235703','235704','235705']:P[c]=P['231156']
for c in ['235698','235699','235700','235702']:P[c]=[[[620,604],[847,539],[964,883],[740,948]]]
P.update({
'232138':[[[574,680],[855,595],[970,775],[691,883]]],
'232139':[[[591,672],[776,571],[977,818],[779,932]]],
'235709':[[[169,542],[691,321],[970,669],[445,935]],[[318,239],[367,221],[476,375],[433,397]]],
'235711':[[[207,565],[676,300],[967,584],[508,904]],[[77,145],[374,353],[358,409],[48,164]]],
'235713':[[[66,448],[650,187],[972,544],[459,846]],[[211,195],[262,176],[381,296],[332,317]]],
'235714':[[[94,345],[483,153],[953,653],[545,900]],[[196,87],[260,71],[370,197],[311,220]]],
'235715':[[[16,526],[522,438],[662,741],[161,877]]],
'235716':[[[423,566],[701,491],[951,884],[616,964]]],
'235717':[[[423,566],[701,491],[951,884],[616,964]]],
'235718':[[[423,566],[701,491],[951,884],[616,964]]],
'235719':[[[423,566],[701,491],[951,884],[616,964]]],
'235721':[[[423,566],[701,491],[951,884],[616,964]]],
'284655':[[[10,313],[676,313],[676,814],[10,814]]],
'284642':[[[365,510],[662,410],[824,891],[493,989]]],
'284661':[[[365,530],[660,530],[660,984],[365,984]],[[479,245],[515,245],[534,552],[461,552]]],
'284662':[[[414,641],[570,662],[576,948],[409,948]]],
'284663':[[[430,656],[565,655],[565,980],[430,980]]],
'235464':[[[56,216],[960,216],[960,789],[56,789]]],
'284648':[[[202,16],[795,16],[795,977],[202,977]]],
'284654':[[[4,168],[988,168],[988,947],[4,947]]],
'284646':[[[346,488],[921,488],[921,984],[346,984]]],
'238237':[[[660,558],[717,540],[976,835],[889,927]]],
'238238':[[[459,565],[533,565],[556,959],[446,959]]],
'238240':[[[444,494],[566,494],[554,972],[437,972]]],
'350529':[[[28,194],[971,274],[971,809],[28,723]]],
'350535':[[[27,261],[973,330],[973,753],[27,684]]],
})
COUNTS={'231903':50,'231906':10,'231907':10,'238785':10}
SINGLE_IN_SET={'231906','231907'}
CROPS={'235723':(100,300,995,995),'232152':(270,0,1000,1000),'235726':(380,0,1000,1000),'235727':(270,0,1000,1000),'235728':(380,0,1000,1000),'359588':(0,0,500,1000),'359590':(0,0,500,1000)}
P['232152']=[[[429,614],[593,672],[933,868],[826,948]]]
P['235727']=P['232152']
P['235726']=[[[383,666],[555,666],[555,950],[383,950]]]
P['235728']=[[[467,668],[610,668],[610,966],[467,966]]]
for c in ['238902','238903','238904','238905']:P[c]=[[[633,588],[892,588],[892,955],[633,955]]]
for c in ['238906','238907','238908','238909']:P[c]=[[[493,623],[949,623],[949,952],[493,952]]]
P['238823']=[[[490,665],[796,492],[970,667],[647,872]],[[544,500],[601,474],[669,552],[611,584]]]
P['238824']=[[[362,466],[664,466],[664,970],[362,970]],[[493,297],[530,297],[533,484],[483,484]]]
P['238827']=[[[528,611],[730,492],[980,755],[805,880]],[[537,479],[591,455],[643,521],[593,563]]]
# Light separable buckles and plastic clips on the ribbon must remain joined.
def source(x):
 im,_=srcload.load(x['code'],x['U']);w,h=im.size
 if x['code'] in CROPS:
  a,b,c,d=CROPS[x['code']];im=im.crop((round(a*w/1000),round(b*h/1000),round(c*w/1000),round(d*h/1000)))
 # 58071: remove the upper-left package through a source-space exclusion only;
 # source face is retained in full, unlike the previous crop at x=29%.
 im.thumbnail((1000,1000),Image.Resampling.LANCZOS);return im
def connected(m,minimum=.00015):
 lab,n=ndi.label(m,structure=np.ones((3,3)));sz=ndi.sum(m,lab,range(1,n+1));return np.isin(lab,[i+1 for i,v in enumerate(sz) if v>minimum*m.size])
def save_image(im,path,**kw):
 b=io.BytesIO();im.save(b,format='PNG' if str(path).endswith('.png') else 'JPEG',**kw);path.write_bytes(b.getvalue())
def protected_mask(x,im):
 a=np.array(im);mn=a.min(2);sat=a.max(2)-mn;h,w=mn.shape;raw=connected(mn<246)
 isbadge=x['name'].lower().startswith('бейдж');cord=bool(texts.T[x['code']].get('cord'))
 if not raw.any():raise ValueError('empty source '+x['code'])
 keep=np.zeros_like(raw)
 if isbadge and not cord and x['code'] not in ['231906','231907']:
  # Individual flat units, or separate pieces of a supplied assortment.
  l,n=ndi.label(raw,structure=np.ones((3,3)));sz=ndi.sum(raw,l,range(1,n+1))
  for i,v in enumerate(sz,1):
   if v>.005*raw.size:keep|=ndi.binary_fill_holes(l==i)
  keep|=raw
  for poly in P.get(x['code'],[]):
   mask=np.zeros((h,w),np.uint8);cv2.fillPoly(mask,[(np.array(poly)*[w/1000,h/1000]).astype('int32')],1);keep|=mask>0
 else:
  # The cord retains open loops. Protect its light body independently.
  keep=connected((sat>28)|(mn<190))
  if x['code']=='380522':keep=connected(mn<251)
  if x['code'] in ['235729','235761','235762','235763','235764','235765']:
   keep=connected(mn<252)
  for poly in P.get(x['code'],[]):
   mask=np.zeros((h,w),np.uint8);cv2.fillPoly(mask,[(np.array(poly)*[w/1000,h/1000]).astype('int32')],1);keep|=mask>0
  if x['code'] in ['238238','238240']:
   l,n=ndi.label(connected(mn<252));
   for i in range(1,n+1):
    yy,xx=np.where(l==i);ww=xx.max()-xx.min()+1;hh=yy.max()-yy.min()+1
    if .65<ww/hh<1.5 and ww*hh>.04*h*w and yy.mean()<.5*h:keep|=ndi.binary_fill_holes(l==i)
   if x['code']=='238240':
    mask=np.zeros((h,w),np.uint8);cv2.ellipse(mask,(round(.5*w),round(.20*h)),(round(.175*w),round(.178*h)),0,0,360,1,-1);keep|=mask>0
  if isbadge and x['code'] not in P:
   light=raw & ~(ndi.binary_dilation((sat>45)|(mn<135),iterations=3))
   light=ndi.binary_closing(light,iterations=3);l,n=ndi.label(light);sz=ndi.sum(light,l,range(1,n+1))
   if n:
    for i in np.argsort(sz)[-3:]:
     m=l==i+1
     if m.sum()<.006*h*w:continue
     pts=np.column_stack(np.where(m)[::-1]).astype('float32');rect=cv2.minAreaRect(pts);ww,hh=rect[1]
     if min(ww,hh)<20 or m.sum()/max(1,ww*hh)<.28:continue
     mask=np.zeros((h,w),np.uint8);cv2.fillPoly(mask,[cv2.boxPoints(rect).astype('int32')],1);keep|=mask>0
 if x['code']=='235723':
  # The complete lower-right face is the largest remaining filled component.
  raw=connected(mn<248);l,n=ndi.label(raw);sz=ndi.sum(raw,l,range(1,n+1));keep=ndi.binary_fill_holes(l==1+int(np.argmax(sz)))
 if x['code'] in ['235726','235728']:keep[:,:round(.20*w)]=False
 holes=np.zeros_like(keep)
 if isbadge and not cord and x['unit']!='набор' and x['code']!='235723':
  ys,xs=np.where(keep);y0,y1=ys.min(),ys.max();x0,x1=xs.min(),xs.max()
  white=(mn>=250);l,n=ndi.label(white & keep);sz=ndi.sum(white & keep,l,range(1,n+1))
  for i,v in enumerate(sz,1):
   yy,xx=np.where(l==i)
   if .00012*h*w<v<.012*h*w and yy.max()<y0+.17*(y1-y0) and xx.min()>x0+4 and xx.max()<x1-4:
    holes|=l==i
 keep[holes]=False
 # Diagnostic case: exact three holes supplied by manual review.
 if x['code']=='235754':
  for cx,cy,rx,ry in [(520,132,40,24),(750,132,88,25),(975,132,36,24)]:
   hm=np.zeros((h,w),np.uint8);cv2.ellipse(hm,(round(cx*w/1500),round(cy*h/1500)),(round(rx*w/1500),round(ry*h/1500)),0,0,360,1,-1);holes|=hm>0
  keep[holes]=False
 # Definite white background outside protected body, including ribbon loops.
 trimap=np.full((h,w),.5);trimap[~ndi.binary_dilation(keep,iterations=6)]=0;trimap[ndi.binary_erosion(keep,iterations=6)]=1
 if cord or not isbadge:
  trimap[(mn>=250)&~keep]=0
 trimap[ndi.binary_erosion(holes,iterations=2)]=0
 return keep,trimap
def prepare(only=None):
 meta=json.load(open(BASE/'metadata.json')) if (BASE/'metadata.json').exists() else {}
 for no,x in enumerate(G):
  c=x['code']
  if only and c not in only:continue
  if c in meta and not only:continue
  begin=time.time();im=source(x);keep,tm=protected_mask(x,im);a=np.array(im)/255.
  alpha=estimate_alpha_cf(a,tm,laplacian_kwargs={'epsilon':1e-6},cg_kwargs={'maxiter':1500,'rtol':1e-6});fr=estimate_foreground_ml(a,alpha)
  rgba=Image.fromarray(np.dstack([np.clip(fr*255,0,255).astype('uint8'),np.clip(alpha*255,0,255).astype('uint8')]))
  yy,xx=np.where((alpha>.08)|keep);bb=(max(0,int(xx.min()-3)),max(0,int(yy.min()-3)),min(im.width,int(xx.max()+4)),min(im.height,int(yy.max()+4)))
  save_image(rgba.crop(bb),BASE/'cut'/f'{c}.png')
  white_im=im
  if c=='235723':
   cleaned=np.array(im).copy();cleaned[~ndi.binary_dilation(keep,iterations=3)]=255;white_im=Image.fromarray(cleaned)
  save_image(white_im.crop(bb),BASE/'white'/f'{c}.jpg',quality=97)
  save_image(Image.fromarray((tm*255).astype('uint8')),BASE/'trimap'/f'{c}.png')
  t=texts.T[c];count=COUNTS.get(c);heading=t['heading'];sub=t['sub'];chips=t['chips'].copy()
  if count:heading=f'Набор из {count} бейджей';sub=t['sub']+' · '+t['heading'].replace('Бейдж ','');chips[3]=f'{count} бейджей в наборе'
  tone='light';ca=np.array(rgba.crop(bb));pixels=ca[:,:,:3][ca[:,:,3]>230];light=float((pixels.min(1)>210).mean())
  if t.get('cord') and x['name'].lower().startswith('бейдж'):
   lower=ca[ca.shape[0]//2:];p=lower[:,:,:3][lower[:,:,3]>230]
   if len(p):light=max(light,float((p.min(1)>210).mean()))
  if x['name'].lower().startswith('бейдж'):
   ar=np.array(im)
   for poly in P.get(c,[]):
    pm=np.zeros((im.height,im.width),np.uint8);cv2.fillPoly(pm,[(np.array(poly)*[im.width/1000,im.height/1000]).astype('int32')],1)
    p=ar[pm>0]
    if len(p):light=max(light,float((p.min(1)>210).mean()))
  if light>.50 or any(v in x['name'].lower() for v in ['прозрачн','белый','белая','белое','белые','светло']) or c in ['238823','238824','238827']:tone='white'
  meta[c]=dict(idvh=x['idvh'],tone=tone,heading=heading,sub=sub,chips=chips,forms=t['forms'],bg=t['bg'],unit=x['unit'],count=count,
   source_units=1 if c in SINGLE_IN_SET else (count or 1),cord=bool(t.get('cord')),assorti=x['assorti']=='ассорти',width=bb[2]-bb[0],height=bb[3]-bb[1],
   seconds=round(time.time()-begin,2),method='pymatting-protected',light_fraction=round(light,3),mask_review='pending')
  (BASE/'metadata.json').write_text(json.dumps(meta,ensure_ascii=False,indent=1))
  print(no+1,c,round(time.time()-begin,1),flush=True)
 return meta
def sheets():
 meta=json.load(open(BASE/'metadata.json'));f=ImageFont.truetype('fonts/Manrope.ttf',18)
 for start in range(0,len(G),16):
  S=Image.new('RGB',(1440,1240),'#e6e9ec');d=ImageDraw.Draw(S)
  for i,x in enumerate(G[start:start+16]):
   c=x['code'];p=BASE/'cut'/f'{c}.png'
   if not p.exists():continue
   im=Image.open(p);im.thumbnail((335,265));C=Image.new('RGBA',(360,310),'#dce1e5');C.alpha_composite(im,((360-im.width)//2,35+(265-im.height)//2));S.paste(C.convert('RGB'),((i%4)*360,(i//4)*310));d.text(((i%4)*360+8,(i//4)*310+8),c+' / '+x['idvh'],font=f,fill='black')
  save_image(S,BASE/'review'/f'masks_{start//16:02d}.jpg',quality=94)
if __name__=='__main__':
 if sys.argv[1:] and sys.argv[1]=='sheets':sheets()
 elif sys.argv[1:] and sys.argv[1]=='checked':
  # Use only after inspecting the corresponding contrast-background sheet.
  m=json.load(open(BASE/'metadata.json'));codes=set(sys.argv[2:])
  if not codes:raise ValueError('Specify reviewed supplier codes')
  for c in codes:m[c]['mask_review']='checked-v13'
  (BASE/'metadata.json').write_text(json.dumps(m,ensure_ascii=False,indent=1))
 else:prepare(set(sys.argv[1:]) or None);sheets()
