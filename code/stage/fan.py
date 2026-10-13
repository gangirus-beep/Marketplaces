# Шаг 3б (по необходимости). Широкий коллаж «тетради в ряд» → веером (решение владельца 05.10.2026, этап 2).
# Коллаж шире 1,8 : 1 из трёх и более отдельных тетрадей стоит на обложке узкой полосой; тетради накладываются веером:
# левая сверху, следующие сдвинуты вправо на 62 % ширины и вниз на 5 % высоты. Исходные вырезки сохраняются в cut_row/.
# Запуск после cut.py: python3 fan.py  (коды берутся сами по cutmeta.json; в texts.py таким товарам ставится fan=True для реестра)
import json, os, shutil, numpy as np
from PIL import Image
from scipy import ndimage as ndi
goods=json.load(open('goods.json')); meta=json.load(open('cutmeta.json')); os.makedirs('cut_row',exist_ok=True); done=[]
for x in goods:
    c=x['code']; m=meta[c]
    if x['assorti']!='ассорти' or m.get('fan') or m['ratio']<=1.8: continue
    if not os.path.exists(f'cut_row/{c}.png'): shutil.copy(f'cut/{c}.png',f'cut_row/{c}.png')
    im=Image.open(f'cut_row/{c}.png'); a=np.asarray(im)[...,3]>128
    lab,n=ndi.label(ndi.binary_opening(a,iterations=2)); sl=ndi.find_objects(lab)
    boxes=sorted([(s[1].start,s[0].start,s[1].stop,s[0].stop) for s in sl if (s[1].stop-s[1].start)*(s[0].stop-s[0].start)>0.05*a.size],key=lambda b:b[0])
    if len(boxes)<3: print(c,'частей',len(boxes),'— пропущен'); continue
    parts=[im.crop(b) for b in boxes]; w=max(p.width for p in parts); h=max(p.height for p in parts); step=int(w*0.62); dy=int(h*0.05); k=len(parts)
    C=Image.new('RGBA',(w+step*(k-1),h+dy*(k-1)),(0,0,0,0))
    for i in reversed(range(k)): C.alpha_composite(parts[i],(i*step,i*dy))
    C.save(f'cut/{c}.png'); m.update(w=C.width,h=C.height,ratio=round(C.width/C.height,4),fan=k); done.append(c)
json.dump(meta,open('cutmeta.json','w'),indent=1); print('веером:',len(done),done)
