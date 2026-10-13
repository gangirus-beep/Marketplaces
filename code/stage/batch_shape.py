import json,sys,pathlib,zipfile,concurrent.futures as cf
from PIL import Image
def one(c):
    import recut_shape as r
    r.cv2.setNumThreads(1)
    parts=r.run(c)
    if parts[0][0]=='keep': r.meta[c]['shape']='keep'
    return c,r.meta[c],parts
if __name__=='__main__':
    start,end=map(int,sys.argv[1:3]);goods=json.load(open('goods.json'));meta=json.load(open('cutmeta.json'));report={}
    with cf.ProcessPoolExecutor(4) as ex:
        for c,m,parts in ex.map(one,[x['code'] for x in goods[start:end]]):
            meta[c]=m;report[c]=parts;print(c,m['shape'],flush=True)
    pathlib.Path('cutmeta.json').write_text(json.dumps(meta,indent=1))
    pathlib.Path('checkpoints').mkdir(exist_ok=True)
    dst=f'checkpoints/Stage2_shape_{start:03d}_{end:03d}.zip'
    with zipfile.ZipFile(dst,'w',zipfile.ZIP_DEFLATED) as z:
        for x in goods[start:end]:
            p=f"cut/{x['code']}.png"
            with Image.open(p) as im: im.verify()
            z.write(p,p)
        z.writestr('cutmeta.json',json.dumps({x['code']:meta[x['code']] for x in goods[start:end]}))
        z.writestr('shape_report.json',json.dumps(report))
    pathlib.Path(f'checkpoints/shape_report_{start:03d}_{end:03d}.json').write_text(json.dumps(report))
    print('COMPLETE',start,end,dst,flush=True)
