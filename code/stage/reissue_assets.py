import json,io,hashlib,subprocess,concurrent.futures as cf,sys,zipfile,math
from pathlib import Path
import numpy as np
from scipy import ndimage as ndi
from scipy.signal import fftconvolve
from PIL import Image
G=json.load(open('reissue/goods.json'));root=Path('reissue/assets');root.mkdir(exist_ok=True);Path('reissue/extra').mkdir(exist_ok=True)
def atomic(im,p):
 b=io.BytesIO();im.save(b,format='PNG',compress_level=1);t=Path(str(p)+'.part');t.write_bytes(b.getvalue());t.replace(p)
def mask(im):
 sm=im.convert('RGB');sm.thumbnail((400,400));a=np.asarray(sm);lab,n=ndi.label(a.min(2)>=247);edge=np.unique(np.r_[lab[0],lab[-1],lab[:,0],lab[:,-1]]);fg=~np.isin(lab,edge[edge>0]);fg=ndi.binary_opening(fg,iterations=1);l,n=ndi.label(fg);sz=ndi.sum(fg,l,range(1,n+1));fg=ndi.binary_fill_holes(np.isin(l,[i+1 for i,s in enumerate(sz) if s>.004*fg.size]));return np.asarray(Image.fromarray(fg).resize(im.size,Image.Resampling.NEAREST))
def crop(im):
 fg=mask(im);y,x=np.where(fg);bb=(x.min(),y.min(),x.max()+1,y.max()+1);r=(bb[2]-bb[0])/(bb[3]-bb[1]);f=fg[bb[1]:bb[3],bb[0]:bb[2]].mean();out=im.convert('RGBA')
 if .57<r<.96 and f>.86:
  m=np.zeros(fg.shape,np.uint8);m[bb[1]+1:bb[3]-1,bb[0]+1:bb[2]-1]=255
 else:m=(fg*255).astype('uint8')
 out.putalpha(Image.fromarray(m));out=out.crop(bb);out.thumbnail((1200,1200));return out,r,float(f)
def center(im):
 fg=mask(im);ys,xs=np.where(fg);cx=(xs.min()+xs.max())//2;cy=(ys.min()+ys.max())//2
 if not fg[cy,cx]:return None
 x0=x1=cx;y0=y1=cy
 while x0>0 and fg[cy,x0-1]:x0-=1
 while x1+1<im.width and fg[cy,x1+1]:x1+=1
 while y0>0 and fg[y0-1,cx]:y0-=1
 while y1+1<im.height and fg[y1+1,cx]:y1+=1
 r=(x1-x0+1)/(y1-y0+1)
 if .62<r<.91 and fg[y0:y1+1,x0:x1+1].mean()>.985 and x1-x0<im.width*.7:
  d=max(3,min(12,int((x1-x0)*.02)));o=im.crop((x0+d,y0+d,x1-d,y1-d)).convert('RGBA');return o,o.width/o.height,1.
 return None
def parts(im,split=False):
 fg=mask(im);l,n=ndi.label(fg);out=[]
 for j,s in enumerate(ndi.find_objects(l)):
  if s is None:continue
  h=s[0].stop-s[0].start;w=s[1].stop-s[1].start;f=(l[s]==j+1).mean()
  if split and .3<w/h<.4 and w*h>.25*fg.size:
   ym=(s[0].start+s[0].stop)//2;bb=[(s[1].start,s[0].start,s[1].stop,ym),(s[1].start,ym,s[1].stop,s[0].stop)]
  elif .59<w/h<.96 and w*h>.02*fg.size and f>.87:bb=[(s[1].start,s[0].start,s[1].stop,s[0].stop)]
  else:continue
  for x0,y0,x1,y1 in bb:
   o=im.crop((x0+2,y0+2,x1-2,y1-2)).convert('RGBA');out.append((o,o.width/o.height,1.))
 return out
def corner(im):
 fg=mask(im);ys,xs=np.where(fg);x1=xs.max()+1;y1=ys.max()+1;cx=x1-6;cy=y1-6;x0=cx;y0=cy
 while x0>0 and fg[cy,x0-1]:x0-=1
 while y0>0 and fg[y0-1,cx]:y0-=1
 o=im.crop((x0+3,y0+3,x1-3,y1-3)).convert('RGBA');return o,o.width/o.height,1.
def score(im,o):
 im=im.convert('L');im.thumbnail((140,140));a=np.asarray(im,float)/255;a-=ndi.gaussian_filter(a,1.1);best=0.
 for f in [.25,.33,.4,.5,.65,.85]:
  w=max(20,int(a.shape[1]*f));h=int(w*o.height/o.width)
  if h>=a.shape[0] or w>=a.shape[1]:continue
  t=np.asarray(o.convert('L').resize((w,h)),float)/255;t-=ndi.gaussian_filter(t,1.1);t-=t.mean();sd=np.sqrt((t*t).sum())
  if sd<.03:continue
  ones=np.ones((h,w));s=fftconvolve(a,ones,'valid');ss=fftconvolve(a*a,ones,'valid');num=fftconvolve(a,t[::-1,::-1],'valid');best=max(best,float((num/(np.sqrt(np.maximum(ss-s*s/(w*h),1e-10))*sd)).max()))
 return best
jobs=[]
for g in G:
 jobs.append((g['Uurl'],Path('reissue/originals')/(g['id']+'.jpg')))
 if g['assorti']=='ассорти':
  for u in g['urls']:
   if 'ad34bd276e8db53f82f59ca187ea04b9' in u or '7b9708521771c130b0b0db8024d06b81' in u:continue
   jobs.append((u,Path('reissue/extra')/(hashlib.sha256(u.encode()).hexdigest()[:20]+'.jpg')))
jobs=list({str(p):(u,p) for u,p in jobs}.values())
def dl(j):
 u,p=j
 try:Image.open(p).load();return None
 except:pass
 t=Path(str(p)+'.part');r=subprocess.run(['curl','-sS','-L','--retry','1','--max-time','35','-A','Mozilla/5.0','-o',str(t),u.replace('http://','https://')],capture_output=True)
 try:Image.open(t).load();t.replace(p);return None
 except:t.unlink(missing_ok=True);return str(p)
if '--download' in sys.argv:
 with cf.ThreadPoolExecutor(64) as ex:
  bad=[]
  for i,b in enumerate(ex.map(dl,jobs)):
   if b:bad.append(b)
   if i%250==0:print(i,len(jobs),len(bad),flush=True)
 json.dump(bad,open('reissue/download_errors.json','w'));print('download done',len(bad));sys.exit()
M=json.load(open('reissue/assets.json')) if Path('reissue/assets.json').exists() else {};errors=[];start=int(sys.argv[1]) if len(sys.argv)>1 else 0;end=int(sys.argv[2]) if len(sys.argv)>2 else len(G)
over={'63106':(2,[2,3,4]),'63268':(2,[2,3,4]),'396458':(2,[2,3,4]),'797114':(4,[4,5]),'803054':(3,[3,4]),'63052':(2,[2,3])}
for index,g in enumerate(G[start:end],start):
 if g['id'] in M:continue
 im=Image.open('reissue/originals/'+g['id']+'.jpg').convert('RGB');whole=crop(im);variants=[];photo=1;chosen=None
 if g['assorti']!='ассорти':chosen=whole
 else:
  candidates=[];gallery={}
  for no,u in enumerate(g['urls'],1):
   p=Path('reissue/extra')/(hashlib.sha256(u.encode()).hexdigest()[:20]+'.jpg')
   if not p.exists() or no==1:continue
   try:o=crop(Image.open(p).convert('RGB'));gallery[no]=o
   except:continue
   if .60<o[1]<.92 and o[2]>.91:
    sc=score(im,o[0])
    if sc>.32:candidates.append((no,o,sc))
  if g['id'] in over:
   photo,vnos=over[g['id']];chosen=gallery.get(photo);candidates=[(n,gallery[n],1.) for n in vnos if n in gallery]
  elif g['id'] in ['788198','788200','788203','63145']:
   pp=parts(im,split=g['id']!='63145');chosen=pp[0] if pp else None;candidates=[(1,p,1.) for p in pp]
  elif g['id'] in ['63143','63144','63217','63528']:chosen=corner(im)
  elif g['id']=='63197':
   o=im.crop((507,417,1026,1076)).convert('RGBA');chosen=(o,o.width/o.height,1.)
  else:
   chosen=center(im)
   if chosen is None and candidates and max(c[2] for c in candidates)>.45:
    photo,chosen,_=max(candidates,key=lambda c:c[2])
   if chosen is None:
    pp=parts(im);chosen=max(pp,key=lambda p:p[0].width*p[0].height) if pp else None
  if chosen is None:errors.append(g['id']);continue
  for j,(n,o,sc) in enumerate(candidates[:8]):
   name=g['id']+'_v'+str(n)+'_'+str(j)+'.png';atomic(o[0],root/name);variants.append(name)
  if len(variants)<2:
   fg=mask(im);yy,xx=np.where(fg);raw=im.crop((max(0,xx.min()-3),max(0,yy.min()-3),min(im.width,xx.max()+4),min(im.height,yy.max()+4)));raw.thumbnail((1200,1200));name=g['id']+'_variants.png';atomic(raw,root/name);variants=[name]
 atomic(chosen[0],root/(g['id']+'.png'));M[g['id']]={'img':g['id']+'.png','ratio':chosen[1],'variants':variants,'photo':photo,'method':'original-source'}
 if index%25==0:print('assets',index,len(M),errors,flush=True)
 Path('reissue/assets.json.part').write_text(json.dumps(M,ensure_ascii=False,indent=1));Path('reissue/assets.json.part').replace('reissue/assets.json')
json.dump(errors,open('reissue/assets_errors.json','w'));print('asset batch done',start,end,len(M),errors,flush=True)

