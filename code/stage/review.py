# Шаг 5а. Контактные листы готовых обложек (по одной на товар, старший квант) → rev_N.jpg — для просмотра глазами
import json
from PIL import Image, ImageDraw, ImageFont
goods=json.load(open('goods.json')); f=ImageFont.truetype('fonts/Manrope.ttf',14)
cols,rows=11,4; w,h=228,304
for part in range(0,len(goods),cols*rows):
    gg=goods[part:part+cols*rows]; r=(len(gg)+cols-1)//cols
    S=Image.new('RGB',(cols*(w+6),r*(h+22)),(40,40,40)); d=ImageDraw.Draw(S)
    for i,x in enumerate(gg):
        cd=x['cards'][-1]; im=Image.open(f"out/covers/{cd['idvh']}_{cd['quant']}.jpg").resize((w,h),Image.LANCZOS)
        px=(i%cols)*(w+6)+3; py=(i//cols)*(h+22)+2; S.paste(im,(px,py)); d.text((px,py+h+2),f"{x['code']} q{cd['quant']}",fill=(255,255,255),font=f)
    S.save(f'rev_{part//(cols*rows)}.jpg',quality=86)
