# Проход, шаг 3. Контактные листы sh_NN.jpg: блок — товар, все фото поставщика по порядку. Метка номера: зелёная — кандидат U, чёрная — в доп. фото, красная — убрано раньше; «=N» — изображение стоит у N товаров
import json, collections, urllib.parse, sys
from PIL import Image, ImageDraw, ImageFont
T=int(sys.argv[1]) if len(sys.argv)>1 else 138; COLS=11; ROWS=9; HDR=32
F=ImageFont.truetype('/home/claude/gen/fonts/Manrope.ttf',13); FB=ImageFont.truetype('/home/claude/gen/fonts/Manrope.ttf',15)
c=json.load(open('cards.json')); h=c['hdr']; ix={n:i for i,n in enumerate(h)}
g=json.load(open('goods_t.json')); gh=g['hdr']; gx={n:i for i,n in enumerate(gh)}
G={str(r[gx['Код поставщика']]):dict(zip(gh,r)) for r in g['rows']}
by=collections.OrderedDict()
for r in c['rows']: by.setdefault(str(r[ix['Код поставщика']]),[]).append(r)
urls=json.load(open('urls.json')); meta=json.load(open('meta.json')); hsh=json.load(open('hash.json'))
norm=lambda u: urllib.parse.unquote(u.strip()).replace('http://','https://')
# раскладка блоков по строкам
rows=[[]]; used=0
for k in by:
    n=max(len(urls[k]),2)
    while n>0:
        take=min(n,COLS)
        if used+take>COLS and used>0: rows.append([]); used=0
        rows[-1].append((k,len(urls[k])-n if len(urls[k])>=2 else 0,take)); used+=take; n-=take
        if n>0: rows.append([]); used=0
pages=[rows[i:i+ROWS] for i in range(0,len(rows),ROWS)]
idx={}
for pn,pg in enumerate(pages,1):
    im=Image.new('RGB',(COLS*(T+2),len(pg)*(T+HDR+4)),(215,215,215)); d=ImageDraw.Draw(im)
    for ri,row in enumerate(pg):
        x=0; y=ri*(T+HDR+4)
        for k,start,take in row:
            xg=G[k]; rs=by[k]; r=rs[0]
            U=norm(r[20]) if r[20] else None; V={norm(v) for v in (r[21] or '').split(';') if v.strip()}
            if start==0:
                st='' if xg['Статус']=='Активный' else ' НЕТ-ОСТ'
                d.rectangle([x,y,x+take*(T+2)-3,y+HDR-1],fill=(255,255,255) if not st else (255,225,200))
                d.text((x+3,y),f"{k} {xg['Поставщик'][0]}{st} {r[25][:3]} {'' if r[23]=='нет' else r[23][:5].upper()}",font=FB,fill=(0,0,0))
                d.text((x+3,y+16),'кв '+','.join(str(q[4]) for q in rs)[:22*take],font=F,fill=(60,60,60))
                idx[k]=pn
            ph=urls[k]
            for j in range(take):
                i=start+j
                if i>=len(ph): break
                key=f'{k}_{i+1:02d}'; t=Image.open(f'th/{key}.jpg'); t.thumbnail((T,T))
                bg=Image.new('RGB',(T,T),(255,255,255)); bg.paste(t,((T-t.width)//2,(T-t.height)//2)); im.paste(bg,(x+j*(T+2),y+HDR))
                u=norm(ph[i]); col=(0,140,0) if u==U else ((0,0,0) if u in V else (210,0,0))
                lab=str(i+1); n=len(hsh.get(meta[key]['md5'],[]))
                if n>1: lab+=f'={n}'
                w=d.textlength(lab,font=F)+6
                d.rectangle([x+j*(T+2),y+HDR,x+j*(T+2)+w,y+HDR+16],fill=col); d.text((x+j*(T+2)+3,y+HDR-1),lab,font=F,fill=(255,255,255))
            x+=take*(T+2)
    im.save(f'sh_{pn:02d}.jpg',quality=88); print(pn,im.size,[b[0] for row in pg for b in row][:3])
json.dump(idx,open('sheet_idx.json','w'))
