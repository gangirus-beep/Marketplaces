# Шаг 2. goods.json (товар, карточки, номера кадров U/W/AA/AB в карусели поставщика, характеристики, описание) + скачивание кадров U и W в src/
import json, collections, urllib.parse, os, subprocess, concurrent.futures as cf
c=json.load(open('cards.json')); h=c['hdr']; ix={n:i for i,n in enumerate(h)}
g=json.load(open('goods_t.json')); gh=g['hdr']
G={(r[gh.index('Поставщик')],str(r[gh.index('Код поставщика')])):dict(zip(gh,r)) for r in g['rows']}
norm=lambda u: urllib.parse.unquote(u.strip()).replace('http://','https://')
by=collections.OrderedDict()
for r in c['rows']: by.setdefault((r[ix['Поставщик']],str(r[ix['Код поставщика']])),[]).append(r)
goods=[]
for (sup,code),rs in by.items():
    x=G[(sup,code)]; r=rs[0]
    urls=[x['Фото главное (ссылка поставщика)']]+[u.strip() for u in (x['Доп. фото (ссылки через «; »)'] or '').split(';') if u.strip()]
    pos={}
    for i,u in enumerate(urls): pos.setdefault(norm(u),i+1)
    ok=lambda u: bool(u) and u!='None'
    P=lambda u: pos.get(norm(u)) if ok(u) else None
    chars={}
    for kv in (x['Характеристики (имя: значение | …)'] or '').split(' | '):
        if ': ' in kv: k,v=kv.split(': ',1); chars[k.strip()]=v.strip()
    goods.append(dict(code=code,sup=sup,idvh=str(r[ix['ID ВХ']]),status=x['Статус'],name=x['Наименование'],brand=x['Бренд'],series=x['Серия / модель'],
      unit=r[ix['Тип единицы']],assorti=r[ix['Ассорти']],nphotos=len(urls),U=P(r[20]),W=P(r[22]),AA=P(r[26]),AB=P(r[27]),
      Uurl=r[20] if ok(r[20]) else None,Wurl=r[22] if ok(r[22]) else None,pack_note=r[28],comment=r[24],chars=chars,descr=x['Описание'],
      cards=[dict(wb=str(q[ix['Артикул WB']]),seller=q[ix['Артикул продавца']],idvh=str(q[ix['ID ВХ']]),quant=int(q[ix['Квант, шт']])) for q in rs]))
json.dump(goods,open('goods.json','w'),ensure_ascii=False,indent=1)
os.makedirs('src',exist_ok=True)
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/126 Safari/537.36"
jobs={(x['code'],x[k],x[k+'url']) for x in goods for k in ('U','W') if x[k]}
def dl(j):
    code,i,u=j; p=f'src/{code}_{i:02d}.jpg'
    if os.path.exists(p) and os.path.getsize(p)>2000: return 0
    uu=urllib.parse.quote(urllib.parse.unquote(u),safe=':/?=&').replace('http://','https://')
    r=subprocess.run(['curl','-s','-L','-A',UA,'--max-time','60','-o',p,'-w','%{http_code}',uu],capture_output=True,text=True)
    return 0 if r.stdout.strip()=='200' else (code,i,r.stdout)
with cf.ThreadPoolExecutor(10) as ex: res=list(ex.map(dl,sorted(jobs)))
print('goods',len(goods),'cards',sum(len(x['cards']) for x in goods),'photos',len(jobs),'errors',[r for r in res if r])
print('нет кадра U:',[x['code'] for x in goods if x['U'] is None],'| нет W и не ассорти:',[x['code'] for x in goods if x['W'] is None and x['assorti']!='ассорти'])
ids=collections.Counter((k['idvh'],k['quant']) for x in goods for k in x['cards']); print('повтор имён файлов:',[k for k,v in ids.items() if v>1])
