# Шаг 5. Рендер обложек ID ВХ_квант.jpg в Chromium. Запуск из корня генератора: python3 render.py [коды товаров для пробы]
import json, os, sys, time
from playwright.sync_api import sync_playwright
import texts
from axis import axis as AX
goods=json.load(open('goods.json')); meta=json.load(open('cutmeta.json'))
os.makedirs('out/covers',exist_ok=True)
only=set(sys.argv[1:]); log=[]; t0=time.time()
ACC=getattr(texts,'ACCENT','#D3401F'); FONT=getattr(texts,'FONT','grotesk')   # цвет плашки и шрифт заголовка этапа — в texts.py
def NB(v):
    import re
    for a,b in ((' %','\u00a0%'),(' г/м²','\u00a0г/м²'),('ГОСТ Р ','ГОСТ\u00a0Р\u00a0'),('ГОСТ ','ГОСТ\u00a0'),('12063-89','12063\u2060-\u206089'),('54543-2011','54543\u2060-\u20602011'),(' — ','\u00a0— ')): v=v.replace(a,b)
    return re.sub('(\\d+) (лист)',lambda m: m.group(1)+'\u00a0'+m.group(2),v)
with sync_playwright() as p:
    launch_args=['--no-sandbox','--allow-file-access-from-files']
    if os.environ.get('WB_SINGLE_PROCESS')=='1': launch_args+=['--single-process','--disable-gpu']
    launch_kw={'args':launch_args}
    if os.environ.get('WB_CHROMIUM'): launch_kw['executable_path']=os.environ['WB_CHROMIUM']
    b=p.chromium.launch(**launch_kw)
    pg=b.new_page(viewport={'width':900,'height':1200})
    pg.goto('file://'+os.path.abspath('cover.html'))
    for n,x in enumerate(goods):
        if only and x['code'] not in only: continue
        t=texts.T[x['code']]; m=meta[x['code']]; tone=texts.TONE_FORCE.get(x['code'],m['tone'])
        single=all(c['quant']==1 for c in x['cards']); ax=AX(f"cut/{x['code']}.png")
        for c in x['cards']:
            name=f"{c['idvh']}_{c['quant']}.jpg"; q=c['quant']
            d=dict(qty=q,forms=t['forms'],heading=t['heading'],sub=NB(t['sub']),chips=[NB(v) for v in t['chips']],bg=t.get('bg',getattr(texts,'BG','plain')),tone=tone,accent=t.get('accent',ACC),font=t.get('font',FONT),img=f"cut/{x['code']}.png",ratio=m['ratio'],line2=t.get('line2_1','') if q==1 else t.get('line2',('в комплекте' if x['unit'] in ('набор','упаковка') else 'в наборе')),plaque=not single)
            d.update(ax)
            if t.get('copies'): d['copies']=t['copies']
            if t.get('cord') and q>=4: d['compactCord']=True
            r=pg.evaluate('d=>render(d)',d)
            pg.screenshot(path='out/covers/'+name,type='jpeg',quality=92,clip={'x':0,'y':0,'width':900,'height':1200})
            log.append(dict(file=name,code=x['code'],quant=q,tone=tone,bg=t['bg'],plaque=not single,**r))
        if n%20==0: print(n,len(log),round(time.time()-t0),flush=True)
    b.close()
if not only: json.dump(log,open('coverlog.json','w'),ensure_ascii=False,indent=1)
print(len(log),'covers; overflow:',[l['file'] for l in log if l['overflow']],'; wide heading:',[(l['file'],l['hw']) for l in log if l['hw']>788],'; sub<30:',sorted({(l['code'],l['subsize']) for l in log if l['subsize']<30}),'; sub wide:',sorted({l['code'] for l in log if l['subw']>788}),'; fonts:',sorted({(l['font'],l['hsize']) for l in log}),'chipsH',sorted({l['chipsH'] for l in log}),'zoneH',sorted({l['zoneH'] for l in log}),round(time.time()-t0))
