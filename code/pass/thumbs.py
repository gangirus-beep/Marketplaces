# Проход, шаг 2. Миниатюры th/, контрольные суммы (hash.json — одинаковые изображения у разных товаров), доля белой рамки (meta.json)
import os, json, hashlib, collections
from PIL import Image
import numpy as np
os.makedirs('th',exist_ok=True)
urls=json.load(open('urls.json')); meta={}; hh=collections.defaultdict(set)
for k,ph in urls.items():
    for i in range(len(ph)):
        key=f'{k}_{i+1:02d}'; p=f'all/{key}.jpg'
        b=open(p,'rb').read(); h=hashlib.md5(b).hexdigest()
        im=Image.open(p); fmt=im.format; im=im.convert('RGBA')
        bg=Image.new('RGBA',im.size,(255,255,255,255)); im=Image.alpha_composite(bg,im).convert('RGB')
        w,hgt=im.size; a=np.asarray(im.resize((200,200))).astype(int)
        fr=np.concatenate([a[:6].reshape(-1,3),a[-6:].reshape(-1,3),a[:,:6].reshape(-1,3),a[:,-6:].reshape(-1,3)])
        white=float((fr.min(axis=1)>=248).mean()); corners=int(min(a[2,2].min(),a[2,-3].min(),a[-3,2].min(),a[-3,-3].min()))
        nonwhite=float((a.min(axis=2)<240).mean())
        t=im.copy(); t.thumbnail((300,300)); t.save(f'th/{key}.jpg',quality=85)
        # перцептивный хеш 8x8
        g=np.asarray(im.convert('L').resize((9,8))).astype(int); ph8=''.join('1' if x else '0' for x in (g[:,1:]>g[:,:-1]).flatten())
        meta[key]=dict(w=w,h=hgt,fmt=fmt,md5=h,white=round(white,3),corner=corners,fill=round(nonwhite,3),ph=ph8)
        hh[h].add(k)
json.dump(meta,open('meta.json','w'))
json.dump({h:sorted(v) for h,v in hh.items() if len(v)>1},open('hash.json','w'))
print(len(meta),'images; shared md5 groups',sum(1 for v in hh.values() if len(v)>1))
print(collections.Counter((m['w'],m['h']) for m in meta.values()).most_common(8))
print(collections.Counter(m['fmt'] for m in meta.values()))
