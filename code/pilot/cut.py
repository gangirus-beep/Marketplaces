import json, numpy as np
from PIL import Image, ImageFilter, ImageDraw, ImageFont
from scipy import ndimage as ndi
goods=json.load(open('goods.json'))
PAL={'190303','227805','227806','227808','227809','192352','192353','192354'}
meta={}
def cut(code,n,holes):
    im=Image.open(f'src/{code}_{n:02d}.jpg').convert('RGB'); a=np.asarray(im).astype(int)
    near=a.min(axis=2)>=250
    lab,k=ndi.label(near)
    border=set(lab[0,:])|set(lab[-1,:])|set(lab[:,0])|set(lab[:,-1]); border.discard(0)
    bg=np.isin(lab,list(border))
    if holes:
        pure=a.min(axis=2)>=254; l3,k3=ndi.label(pure & ~bg); sz=ndi.sum(pure&~bg,l3,range(1,k3+1))
        big=[i+1 for i,s in enumerate(sz) if s>0.004*a.shape[0]*a.shape[1]]
        bg|=np.isin(l3,big)
    fg=~bg
    fg=ndi.binary_opening(fg,iterations=1)
    l2,n2=ndi.label(fg); sz=ndi.sum(fg,l2,range(1,n2+1))
    keep=[i+1 for i,s in enumerate(sz) if s>0.002*fg.size]
    fg=np.isin(l2,keep)
    fg=ndi.binary_erosion(fg,iterations=1)
    alpha=Image.fromarray((fg*255).astype('uint8')).filter(ImageFilter.GaussianBlur(0.9))
    ys,xs=np.where(fg); box=(max(0,xs.min()-3),max(0,ys.min()-3),min(im.width,xs.max()+4),min(im.height,ys.max()+4))
    rgba=im.copy(); rgba.putalpha(alpha); rgba=rgba.crop(box)
    px=a[fg]; lum=(0.299*px[:,0]+0.587*px[:,1]+0.114*px[:,2]); sat=(px.max(axis=1)-px.min(axis=1))
    light=float((lum>215).mean()); gray=float((sat<28).mean())
    if max(rgba.size)>1200: rgba.thumbnail((1200,1200),Image.LANCZOS)
    rgba.save(f'cut/{code}.png')
    return dict(w=rgba.size[0],h=rgba.size[1],ratio=round(rgba.size[0]/rgba.size[1],4),lum=round(float(lum.mean()),1),light=round(light,2),gray=round(gray,2),fill=round(float(fg[box[1]:box[3],box[0]:box[2]].mean()),2))
for x in goods:
    m=cut(x['code'],x['U'],x['code'] in PAL); meta[x['code']]=m
    m['tone']='panel' if (m['lum']>200 and m['light']>0.55 and m['gray']>0.6) else 'light'
    print(x['code'],m)
json.dump(meta,open('cutmeta.json','w'),indent=1)
f=ImageFont.truetype('fonts/Manrope.ttf',18)
cols=9; sz=200; rows=(len(goods)+cols-1)//cols
S=Image.new('RGB',(cols*(sz+8),rows*(sz+30)),(106,61,184)); d=ImageDraw.Draw(S)
for i,x in enumerate(goods):
    im=Image.open(f"cut/{x['code']}.png"); im.thumbnail((sz,sz)); px=(i%cols)*(sz+8)+4; py=(i//cols)*(sz+30)+4
    if meta[x['code']]['tone']=='light': d.rectangle([px-2,py-2,px+sz+2,py+sz+2],fill=(244,239,231))
    S.paste(im,(px,py),im); d.text((px,py+sz+2),f"{x['code']} {meta[x['code']]['tone']}",fill=(255,255,255),font=f)
S.save('sh_cut.jpg',quality=88)
