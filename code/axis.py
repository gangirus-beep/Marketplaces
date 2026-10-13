import numpy as np
from PIL import Image
def axis(path):
    """Ось вытянутости товара по маске: угол (град., ось Y вниз), вытянутость, толщина поперёк оси в долях высоты."""
    a=np.asarray(Image.open(path).convert('RGBA'))[...,3]>128; ys,xs=np.nonzero(a)
    if len(xs)>60000:
        idx=np.random.RandomState(1).choice(len(xs),60000,replace=False); xs,ys=xs[idx],ys[idx]
    P=np.stack([xs-xs.mean(),ys-ys.mean()]).astype(float); ev,evec=np.linalg.eigh(np.cov(P))
    v=evec[:,1]; th=float(np.degrees(np.arctan2(v[1],v[0]))); n=np.array([-v[1],v[0]]); pr=P.T@n
    return dict(axis=round(th,1),elong=round(float(np.sqrt(ev[1]/max(ev[0],1e-9))),2),thick=round(float((np.percentile(pr,99.5)-np.percentile(pr,0.5))/a.shape[0]),3))
