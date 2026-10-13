# Крупный просмотр вырезок на фоне плашки: python3 zoomcut.py out.jpg код код ...
import sys, json
from PIL import Image, ImageDraw, ImageFont
meta=json.load(open('cutmeta.json')); F=ImageFont.truetype('fonts/Manrope.ttf',15)
ks=sys.argv[2:]; T=380; C=5; R=(len(ks)+C-1)//C
S=Image.new('RGB',(C*(T+6),R*(T+24)),(150,40,20)); d=ImageDraw.Draw(S)
for i,k in enumerate(ks):
    im=Image.open(f'cut/{k}.png'); im.thumbnail((T,T),Image.LANCZOS); x=(i%C)*(T+6)+3; y=(i//C)*(T+24)+2
    S.paste(im,(x+(T-im.width)//2,y+(T-im.height)//2),im); m=meta[k]; d.text((x,y+T+2),f"{k} {m['tone']} n{m['ncomp']} f{m['fill']} r{m['ratio']}",fill=(255,255,255),font=F)
S.save(sys.argv[1],quality=88)
