"""White-background last-photo layout: grid <=20, compact stack above; exact copy count."""
import math
from PIL import Image

def layout(count,ratio,width=900,height=1200,margin=36,mode=None):
    if not isinstance(count,int) or count<1 or ratio<=0:raise ValueError('Positive integer count and ratio required')
    mode=mode or ('grid' if count<=20 else 'compact-stack')
    W,H=width-2*margin,height-2*margin
    if mode=='grid':
        gap=20 if count<=20 else 12
        best=None
        for rows in range(1,count+1):
            cols=math.ceil(count/rows);w=min((W-(cols-1)*gap)/cols,ratio*(H-(rows-1)*gap)/rows)
            score=w*(1.2 if count%rows==0 else 1)
            if best is None or score>best[0]:best=(score,rows,w)
        _,rows,w=best;w=max(1,int(w));h=max(1,round(w/ratio));base,extra=divmod(count,rows);pos=[];rowcounts=[];y=round((height-(rows*h+(rows-1)*gap))/2)
        for i in range(rows):
            n=base+(i<extra);rowcounts.append(n);x=round((width-(n*w+(n-1)*gap))/2)
            pos.extend((x+j*(w+gap),y) for j in range(n));y+=h+gap
        name='+'.join(map(str,rowcounts))
    elif mode=='compact-stack':
        # Bound total displacement rather than accumulating a long diagonal row.
        sx=min(64,max(0,2*(count-1)));sy=min(48,max(0,1.5*(count-1)))
        w=max(1,int(min(W-sx,ratio*(H-sy))));h=max(1,round(w/ratio));x0=round((width-w-sx)/2);y0=round((height-h-sy)/2)
        pos=[(round(x0+(count-1-i)*sx/max(1,count-1)),round(y0+i*sy/max(1,count-1))) for i in range(count)]
        name=f'compact-stack × {count}'
    else:raise ValueError('Unknown last-photo layout')
    assert len(pos)==count and all(0<=x and 0<=y and x+w<=width and y+h<=height for x,y in pos)
    return w,h,pos,name,mode

def render(item,count,mode=None):
    w,h,pos,name,mode=layout(count,item.width/item.height,mode=mode)
    t=item.resize((w,h),Image.Resampling.LANCZOS);canvas=Image.new('RGB',(900,1200),'white')
    for p in pos:canvas.paste(t,p,t if t.mode=='RGBA' else None)
    return canvas,{'layout':name,'layoutMode':mode,'representedUnits':count,'drawnCopies':len(pos),'item_w':w,'item_h':h}

def source_copies(quant,items_per_unit=1,items_in_source=1):
    for n in [quant,items_per_unit,items_in_source]:
        if not isinstance(n,int) or n<1:raise ValueError('Counts must be positive integers')
    total=quant*items_per_unit
    if total%items_in_source:raise ValueError('Source grouping contradicts sold contents')
    return total//items_in_source
