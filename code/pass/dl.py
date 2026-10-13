import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from samson_download import download as samson_download, is_samson, valid as cached_image_valid
# Проход, шаг 1. Скачивание всех фото поставщика по типу (после extract.py): all/код_NN.jpg, urls.json. Запускать в фоне: setsid nohup python3 dl.py > dl.log 2>&1 &
import json, os, urllib.parse, urllib.request, concurrent.futures as cf, time
g=json.load(open('goods_t.json')); gh=g['hdr']; gx={n:i for i,n in enumerate(gh)}
os.makedirs('all',exist_ok=True)
urls={}
for r in g['rows']:
    k=str(r[gx['Код поставщика']]); ph=[]
    m=r[gx['Фото главное (ссылка поставщика)']]
    if m: ph.append(m.strip())
    for u in (r[gx['Доп. фото (ссылки через «; »)']] or '').split(';'):
        if u.strip(): ph.append(u.strip())
    urls[k]=ph
json.dump(urls,open('urls.json','w'),ensure_ascii=False)
enc=lambda u: urllib.parse.quote(urllib.parse.unquote(u.strip()),safe=':/?=&').replace('http://','https://')
jobs=[(f'all/{k}_{i+1:02d}.jpg',enc(u)) for k,ph in urls.items() for i,u in enumerate(ph)]
H={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36'}
def get(j):
    p,u=j
    if cached_image_valid(p): return p,'have'
    if is_samson(u):
        try: samson_download(u,p); return p,'ok'
        except Exception as e: return p,'ERR '+str(e)+' '+u
    for t in range(4):
        try:
            d=urllib.request.urlopen(urllib.request.Request(u,headers=H),timeout=40).read()
            if len(d)>500:
                open(p,'wb').write(d); return p,'ok'
        except Exception as e: err=str(e)[:80]; time.sleep(1+t)
    return p,'ERR '+err+' '+u
t=time.time()
with cf.ThreadPoolExecutor(12) as ex: res=list(ex.map(get,jobs))
bad=[r for r in res if r[1].startswith('ERR')]
json.dump(bad,open('dl_bad.json','w'),ensure_ascii=False)
print('jobs',len(jobs),'bad',len(bad),'sec',round(time.time()-t)); print(bad[:10])
