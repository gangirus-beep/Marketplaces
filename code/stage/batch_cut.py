import json, sys, pathlib, concurrent.futures as cf, zipfile
from PIL import Image

def one(x):
    import cutlib
    m=cutlib.cut(x['code'],x['U'])
    m['tone']='panel' if m['lum']>200 and m['light']>0.55 and m['gray']>0.6 else 'light'
    return x['code'],m

if __name__=='__main__':
    start,end=map(int,sys.argv[1:3]); goods=json.load(open('goods.json'))
    meta=json.load(open('cutmeta.json')) if pathlib.Path('cutmeta.json').exists() else {}
    with cf.ProcessPoolExecutor(4) as ex:
        for c,m in ex.map(one,goods[start:end]):
            meta[c]=m
            print(c,m['tone'],flush=True)
    pathlib.Path('cutmeta.json').write_text(json.dumps(meta,indent=1))
    pathlib.Path('checkpoints').mkdir(exist_ok=True)
    dst=f'checkpoints/Stage2_cut_{start:03d}_{end:03d}.zip'
    with zipfile.ZipFile(dst,'w',zipfile.ZIP_DEFLATED) as z:
        for x in goods[start:end]:
            p=f"cut/{x['code']}.png"
            with Image.open(p) as im: im.verify()
            z.write(p,p)
        z.writestr('cutmeta.json',json.dumps({x['code']:meta[x['code']] for x in goods[start:end]}))
    print('COMPLETE',start,end,'total',len(meta),dst,flush=True)
