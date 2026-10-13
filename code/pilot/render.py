import json, os, sys
from playwright.sync_api import sync_playwright
import texts
from axis import axis as AX
goods=json.load(open('goods.json')); meta=json.load(open('cutmeta.json'))
os.makedirs('out/covers',exist_ok=True)
only=set(sys.argv[1:])
log=[]
with sync_playwright() as p:
    b=p.chromium.launch(args=['--no-sandbox','--allow-file-access-from-files'])
    pg=b.new_page(viewport={'width':900,'height':1200})
    pg.goto('file:///home/claude/pilot/cover.html')
    for x in goods:
        t=texts.T[x['code']]; m=meta[x['code']]; tone=texts.TONE_FORCE.get(x['code'],m['tone'])
        single=all(c['quant']==1 for c in x['cards'])
        for c in x['cards']:
            name=f"{c['idvh']}_{c['quant']}.jpg"
            if only and name not in only and x['code'] not in only: continue
            q=c['quant']
            line2='' if q==1 else ('в комплекте' if x['unit']=='набор' else 'в наборе')
            d=dict(qty=q,forms=t['forms'],heading=t['heading'],sub=t['sub'],chips=t['chips'],bg='paper',tone=tone,accent='#6A3DB8',font='serif',img=f"cut/{x['code']}.png",ratio=m['ratio'],line2=line2,plaque=not single)
            d.update(AX(d['img']))            # ось вытянутости — для смещения стопки
            if t.get('copies'): d['copies']=t['copies']   # коллаж дизайнов — одна копия
            r=pg.evaluate('d=>render(d)',d)
            pg.screenshot(path='out/covers/'+name,type='jpeg',quality=92,clip={'x':0,'y':0,'width':900,'height':1200})
            log.append(dict(file=name,code=x['code'],quant=q,tone=tone,plaque=not single,**r))
    b.close()
json.dump(log,open('coverlog.json','w'),ensure_ascii=False,indent=1)
print(len(log),'covers; overflow:',[l['file'] for l in log if l['overflow']],'; wide heading:',[(l['file'],l['hw']) for l in log if l['hw']>788])
