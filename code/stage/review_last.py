# Шаг 6а. Контактные листы последних фото (по одному на товар: младший и старший квант через один) → revl_N.jpg — для просмотра глазами
import json
from PIL import Image, ImageDraw, ImageFont
goods=[x for x in json.load(open('goods.json')) if x['W']]; f=ImageFont.truetype('fonts/Manrope.ttf',13)
cols,rows=16,5; w,h=180,240
for part in range(0,len(goods),cols*rows):
    gg=goods[part:part+cols*rows]; r=(len(gg)+cols-1)//cols
    S=Image.new('RGB',(cols*(w+6),r*(h+20)),(70,70,70)); d=ImageDraw.Draw(S)
    for i,x in enumerate(gg):
        cd=max(x['cards'],key=lambda c:c['quant']) if (i%2) else min(x['cards'],key=lambda c:c['quant'])
        im=Image.open(f"out/last/{cd['idvh']}_{cd['quant']}_last.jpg").resize((w,h),Image.LANCZOS)
        px=(i%cols)*(w+6)+3; py=(i//cols)*(h+20)+2; S.paste(im,(px,py)); d.text((px,py+h+1),f"{x['code']} q{cd['quant']}",fill=(255,255,255),font=f)
    S.save(f'revl_{part//(cols*rows)}.jpg',quality=86)
