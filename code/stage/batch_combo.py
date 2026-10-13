import json,concurrent.futures as cf
from pathlib import Path

def one(c):
 import recut_combo as r
 r.cv2.setNumThreads(1)
 return c,r.combo(c)[1]
if __name__=='__main__':
 G=json.load(open('goods.json'));meta=json.load(open('cutmeta.json'))
 codes=[x['code'] for x in G if meta[x['code']]['shape'] in ('keep','hull') and x['code'] not in ['231903','231906','231907','235713','235714','235696','284645','284647','350527']]
 with cf.ProcessPoolExecutor(4) as ex:
  for c,m in ex.map(one,codes):meta[c].update(m);print(c,m['shape'],flush=True)
 Path('cutmeta.json').write_text(json.dumps(meta,indent=1))
