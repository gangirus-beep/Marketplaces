# Крупный просмотр выбранных кадров: лист 5 в ряд по 312 px
import sys
from PIL import Image, ImageDraw, ImageFont
F=ImageFont.truetype('/home/claude/gen/fonts/Manrope.ttf',15)
def sheet(keys,out,T=312,C=5):
    R=(len(keys)+C-1)//C
    im=Image.new('RGB',(C*(T+2),R*(T+20)),(200,200,200)); d=ImageDraw.Draw(im)
    for i,k in enumerate(keys):
        t=Image.open(f'all/{k}.jpg').convert('RGB'); t.thumbnail((T,T))
        x=(i%C)*(T+2); y=(i//C)*(T+20); im.paste(t,(x,y+18)); d.text((x+3,y),k,font=F,fill=(0,0,0))
    im.save(out,quality=88)
if __name__=='__main__':
    # python3 zoom_sel.py zz_1.jpg 357601_01 357601_02 …   (ключ = код_номер кадра)
    sheet(sys.argv[2:],sys.argv[1])
