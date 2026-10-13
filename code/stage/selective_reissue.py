import json,pathlib,threading,http.server,functools,sys
from PIL import Image
import numpy as np
from scipy import ndimage as ndi
from playwright.sync_api import sync_playwright
import os
CODE=pathlib.Path(__file__).resolve().parents[1]
ROOT=pathlib.Path(os.environ.get('WB_PROJECT_ROOT',CODE.parent.parent))
R=pathlib.Path(os.environ.get('WB_REISSUE_ROOT',ROOT/'work/selective_reissue')); A=R/'assets';A.mkdir(exist_ok=True);(R/'covers').mkdir(exist_ok=True)
sys.path.insert(0,str(CODE/'stage'))
from variant_assets import trim,isolated,fragments
class QuietHandler(http.server.SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
server=http.server.ThreadingHTTPServer(('127.0.0.1',8767),functools.partial(QuietHandler,directory=str(ROOT)));threading.Thread(target=server.serve_forever,daemon=True).start()
def uri(p):return 'http://127.0.0.1:8767/'+str(p.relative_to(ROOT))
selected=json.load(open(R/'selected.json'));decisions=json.load(open(R/'decisions.json'));log=[]
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path=os.environ.get('WB_CHROMIUM','/usr/bin/chromium'),args=['--no-sandbox']);page=b.new_page(viewport={'width':900,'height':1200})
 for good in selected:
  id=good['id']
  if id not in decisions:continue
  d=decisions[id]
  def source(n):return Image.open(R/'gallery'/f'{id}_{n:02d}.jpg').convert('RGB')
  if d['mode']=='full':images=[trim(source(n)) for n in d['photos']]
  elif d['mode']=='isolated':images=isolated(source(d.get('source',1)),d['count'])
  elif d['mode']=='fragments':images=fragments(source(d.get('source',1)),d['rects'],d.get('normalized_to',1500))
  else:images=[trim(source(d.get('source',1)))]
  urls=[]
  for n,im in enumerate(images):
   p=A/f'{id}_v{n}.png';im.save(p);urls.append(uri(p))
  for c in good['cards']:
   name=c['Файл обложки'];q=c['Квант, шт'];top=740 if q==1 else 716
   mode='full' if d['mode']=='isolated' else d['mode']
   args={'qty':q,'mode':mode,'original':uri(R/'originals'/name),'variants':urls}
   if mode=='collage':
    bgcode=c['Фон'].split(' ')[0];bg={'Т11':'line_a','Т12':'line_b','Т13':'line_c','Т21':'grid_a','Т22':'grid_b','Т23':'grid_c','Т24':'grid_d','Т31':'oblique_a','Т41':'narrow_a','Т51':'big_a'}[bgcode]
    page.goto(uri(CODE/'cover.html'))
    page.evaluate("bg=>{const r=document.getElementById('root');r.style.background=BG[bg].css;document.getElementById('deco').innerHTML=BG[bg].deco||'';for(const e of [...r.children])if(e.id!=='deco')e.remove()}",bg)
    bgpath=A/(name+'_background.png');page.screenshot(path=str(bgpath),clip={'x':56,'y':350,'width':788,'height':top-350})
    original=Image.open(R/'originals'/name).convert('RGB').crop((56,350,844,top-12));bgim=Image.open(bgpath).convert('RGB').crop((0,0,788,top-362))
    diff=np.abs(np.array(original,dtype=float)-np.array(bgim,dtype=float)).max(2)>20
    diff=ndi.binary_opening(diff,iterations=1);lab,num=ndi.label(diff);sizes=np.bincount(lab.ravel());keep=np.where(sizes>80)[0];keep=keep[keep!=0];mask=ndi.binary_fill_holes(np.isin(lab,keep));mask=ndi.binary_dilation(mask,iterations=1)
    ys,xs=np.where(mask);assert len(xs)>100
    rgba=original.convert('RGBA');rgba.putalpha(Image.fromarray((mask*255).astype('uint8')));main=rgba.crop((xs.min(),ys.min(),xs.max()+1,ys.max()+1));mp=A/(name+'_accepted-main.png');main.save(mp)
    args.update(background=uri(bgpath),acceptedMain=uri(mp))
   page.goto(uri(CODE/'cover.html'));page.add_script_tag(path=str(CODE/'stage/replace_variants.js'))
   result=page.evaluate('async d=>await replaceVariantsOnCover(d)',args)
   out=R/'covers'/name;page.screenshot(path=str(out),type='jpeg',quality=95)
   log.append({'id':id,'file':name,'q':q,**result})
  print('Rendered',id,len(good['cards']),mode,flush=True)
 b.close()
json.dump(log,open(R/'renderlog.json','w'),ensure_ascii=False,indent=2);print('DONE',len(log),flush=True)
