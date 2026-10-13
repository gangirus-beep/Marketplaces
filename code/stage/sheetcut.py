# Контактные листы всех вырезок на фоне плашки (после recut_shape.py): shc_N.jpg
import json
from PIL import Image, ImageDraw, ImageFont
goods=json.load(open('goods.json')); meta=json.load(open('cutmeta.json')); F=ImageFont.truetype('fonts/Manrope.ttf',13)
T=190; C=12; R=7
for part in range(0,len(goods),C*R):
    gg=goods[part:part+C*R]; S=Image.new('RGB',(C*(T+8),((len(gg)+C-1)//C)*(T+22)),(150,40,20)); d=ImageDraw.Draw(S)
    for i,x in enumerate(gg):
        k=x['code']; im=Image.open(f'cut/{k}.png'); im.thumbnail((T,T),Image.LANCZOS); px=(i%C)*(T+8)+4; py=(i//C)*(T+22)+3
        S.paste(im,(px+(T-im.width)//2,py+(T-im.height)//2),im); d.text((px,py+T+2),f"{k} {meta[k].get('shape','')}",fill=(255,255,255),font=F)
    S.save(f'shc_{part//(C*R)}.jpg',quality=88)
