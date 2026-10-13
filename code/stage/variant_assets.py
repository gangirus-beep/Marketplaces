"""Exact rectangular crops from supplier photos; never restore hidden artwork."""
import numpy as np
from scipy import ndimage as ndi
from PIL import Image

def foreground(im):
    a=np.asarray(im.convert('RGB'));fg=a.min(2)<242
    fg=ndi.binary_opening(fg,iterations=1)
    lab,n=ndi.label(fg);sizes=np.bincount(lab.ravel());keep=np.where(sizes>max(50,fg.size*.001))[0];keep=keep[keep!=0]
    return np.isin(lab,keep)

def trim(im):
    fg=foreground(im);y,x=np.where(fg)
    if not len(x):raise ValueError('Empty photo')
    return im.crop((max(0,x.min()-2),max(0,y.min()-2),min(im.width,x.max()+3),min(im.height,y.max()+3)))

def isolated(im,expected):
    fg=foreground(im);lab,n=ndi.label(fg);out=[]
    for sl in ndi.find_objects(lab):
        if sl is None:continue
        h=sl[0].stop-sl[0].start;w=sl[1].stop-sl[1].start
        if .53<w/h<1.08 and w*h>fg.size*.025:
            out.append((sl[0].start,sl[1].start,im.crop((max(0,sl[1].start-2),max(0,sl[0].start-2),min(im.width,sl[1].stop+2),min(im.height,sl[0].stop+2)))))
    out.sort(key=lambda x:(round(x[0]/(im.height*.15)),x[1]))
    if len(out)!=expected:raise ValueError(f'Expected {expected} isolated whole designs, found {len(out)}')
    return [x[2] for x in out]

def fragments(im,rects,normalized_to=1500):
    out=[]
    for x,y,w,h in rects:
        rect=(round(x*im.width/normalized_to),round(y*im.height/normalized_to),round((x+w)*im.width/normalized_to),round((y+h)*im.height/normalized_to))
        if not(0<=rect[0]<rect[2]<=im.width and 0<=rect[1]<rect[3]<=im.height):raise ValueError('Fragment outside source')
        out.append(im.crop(rect))
    return out
