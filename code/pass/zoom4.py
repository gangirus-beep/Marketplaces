# Крупный просмотр: 4 в ряд по 386 px
import sys
from PIL import Image, ImageDraw, ImageFont
F=ImageFont.truetype('/home/claude/gen/fonts/Manrope.ttf',15)
def sheet(keys,out,T=386,C=4):
    R=(len(keys)+C-1)//C
    im=Image.new('RGB',(C*(T+2),R*(T+20)),(200,200,200)); d=ImageDraw.Draw(im)
    for i,k in enumerate(keys):
        t=Image.open(f'all/{k}.jpg').convert('RGB'); t.thumbnail((T,T),Image.LANCZOS)
        x=(i%C)*(T+2); y=(i//C)*(T+20); im.paste(t,(x,y+18)); d.text((x+3,y),k,font=F,fill=(0,0,0))
    im.save(out,quality=90)
sheet(sys.argv[2:],sys.argv[1])
