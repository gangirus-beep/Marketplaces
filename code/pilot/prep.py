import json, collections, urllib.parse, os, subprocess, concurrent.futures as cf
c=json.load(open('../cards.json')); h=c['hdr']; ix={n:i for i,n in enumerate(h)}
g=json.load(open('../goods44.json')); gh=g['hdr']
G={str(r[gh.index('Код поставщика')]):dict(zip(gh,r)) for r in g['rows']}
norm=lambda u: urllib.parse.unquote(u.strip()).replace('http://','https://')
by=collections.OrderedDict()
for r in c['rows']: by.setdefault(str(r[ix['Код поставщика']]),[]).append(r)
goods=[]; jobs=[]
for code,rs in by.items():
    x=G[code]; r=rs[0]
    urls=[x['Фото главное (ссылка поставщика)']]+[u.strip() for u in (x['Доп. фото (ссылки через «; »)'] or '').split(';') if u.strip()]
    pos={norm(u):i+1 for i,u in enumerate(urls)}
    def P(u):
        if not u: return None
        return pos.get(norm(u))
    V=[u for u in str(r[21] or '').split(';') if u.strip()]
    gd=dict(code=code, sup=r[ix['Поставщик']], idvh=str(r[ix['ID ВХ']]), status=x['Статус'], name=x['Наименование'], brand=x['Бренд'],
            unit=r[ix['Тип единицы']], assorti=r[ix['Ассорти']], nphotos=len(urls), U=P(r[20]), W=P(r[22]), AA=P(r[26]), AB=P(r[27]),
            V=[P(u) for u in V], pack_note=r[28], comment=r[24],
            cards=[dict(wb=str(q[ix['Артикул WB']]), seller=q[ix['Артикул продавца']], idvh=str(q[ix['ID ВХ']]), quant=int(q[ix['Квант, шт']])) for q in rs])
    goods.append(gd)
    for i,u in enumerate(urls,1): jobs.append((code,i,u))
json.dump(goods,open('goods.json','w'),ensure_ascii=False,indent=1)
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/126 Safari/537.36"
def dl(j):
    code,i,u=j; p=f'src/{code}_{i:02d}.jpg'
    if os.path.exists(p) and os.path.getsize(p)>2000: return 0
    uu=urllib.parse.quote(urllib.parse.unquote(u),safe=':/?=&').replace('http://','https://')
    r=subprocess.run(['curl','-s','-L','-A',UA,'-o',p,'-w','%{http_code}',uu],capture_output=True,text=True)
    return 0 if r.stdout.strip()=='200' else (code,i,r.stdout)
with cf.ThreadPoolExecutor(12) as ex: res=list(ex.map(dl,jobs))
print('photos',len(jobs),'errors',[r for r in res if r])
bad=[(x['code'],k) for x in goods for k in ('U','W') if x[k] is None]; print('unmapped U/W',bad)
print('unmapped V',[(x['code'],x['V']) for x in goods if None in x['V']])
print('cards',sum(len(x['cards']) for x in goods),'V total',sum(len(x['V']) for x in goods))
ids=collections.Counter(c['idvh'] for x in goods for c in x['cards']); print('distinct idvh',len(ids), [ (x['code'],x['idvh'],{c['idvh'] for c in x['cards']}) for x in goods if len({c['idvh'] for c in x['cards']})>1])
