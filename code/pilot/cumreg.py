import json, math, collections
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter
import texts, importlib.util
goods=json.load(open('goods.json')); meta=json.load(open('cutmeta.json')); last={l['file']:l for l in json.load(open('lastlog.json'))}
spec=importlib.util.spec_from_file_location('reg','/home/claude/pilot/reg.py')
NOTE={'191733':'Объём на обложку не вынесен: в характеристиках 250 мл, в описании 210 мл. «Ассорти» — проверить.','191734':'Объём на обложку не вынесен: в характеристиках «до уровня 50 мл», в описании 75 мл. «Ассорти» — проверить.','227808':'Размер на обложку не вынесен: в характеристиках 24 × 32 см и 8 мм, в описании 24 × 31 × 0,6 см.','881007':'Комплектность по этикетке: «4 предмета + альбом», один карандаш (решение 05.10.2026). «Ассорти» — проверить.','881009':'«Ассорти» — проверить: дизайн альбома на фото разный.','881010':'«Ассорти» — проверить: дизайн альбома на фото разный.','190303':'Бренд в базе — NO NAME; в подзаголовке стоит модель «ПХ-1».','272360':'Название дизайна на обложку не вынесено: у поставщика «Цветовая палитра», на изделии «Азбука цвета».'}
def forms(q,f):
    f=f.split('|'); n10,n100=q%10,q%100
    return f[0] if (n10==1 and n100!=11) else f[1] if (2<=n10<=4 and not 12<=n100<=14) else f[2]
wb=Workbook(); H=Font(bold=True,color='FFFFFF',name='Arial',size=10); HF=PatternFill('solid',fgColor='4B2A8C'); BF=Font(name='Arial',size=10); YF=PatternFill('solid',fgColor='FFF2CC')
def sheet(ws,head,rows,widths,yellow=()):
    ws.append(head)
    for r in rows: ws.append(r)
    for c in ws[1]: c.font=H; c.fill=HF; c.alignment=Alignment(wrap_text=True,vertical='center')
    for row in ws.iter_rows(min_row=2):
        for c in row:
            c.font=BF; c.alignment=Alignment(vertical='top',wrap_text=True)
            if c.column in yellow: c.fill=YF
    for i,w in enumerate(widths,1): ws.column_dimensions[get_column_letter(i)].width=w
    ws.freeze_panes='A2'; ws.auto_filter.ref=ws.dimensions; ws.row_dimensions[1].height=34
# ---------- Готово
ws=wb.active; ws.title='Готово'; rows=[]
for x in goods:
    t=texts.T[x['code']]; tone=texts.TONE_FORCE.get(x['code'],meta[x['code']]['tone']); single=all(k['quant']==1 for k in x['cards'])
    for c in x['cards']:
        q=c['quant']; cf=f"{c['idvh']}_{q}.jpg"; lf=f"{c['idvh']}_{q}_last.jpg"; l2='' if q==1 else (' в комплекте' if x['unit']=='набор' else ' в наборе')
        rows.append(['05.10.2026','пилот','Аксессуары для рисования',int(c['wb']),c['seller'],int(c['idvh']),q,x['sup'],x['code'],x['name'],x['status'],cf,lf,'Х2 · акварель','фиолетовая','с засечками',
            'тёмная подложка под фото' if tone=='panel' else 'светлый','без плашки' if single else f"{q} {forms(q,t['forms'])}{l2}",f"№{x['U']}",f"№{x['W']}",last[lf]['layout'],NOTE.get(x['code'],''),'Аксессуары_для_рисования_пилот_обложки_и_фото.zip'])
sheet(ws,['Дата','Этап','Тип','Артикул WB','Артикул продавца','ID ВХ','Квант, шт','Поставщик','Код поставщика','Наименование','Статус товара','Файл обложки','Файл последнего фото','Фон','Цвет плашки','Шрифт заголовка','Тон обложки','Плашка','Фото для обложки (№ у поставщика)','Фото для последнего (№)','Раскладка последнего фото','Что проверить','Архив'],rows,[11,8,24,13,18,9,8,10,10,50,12,16,20,16,13,14,16,24,12,12,14,46,34])
# ---------- Тексты
ws=wb.create_sheet('Тексты обложек'); rows=[]
for x in goods:
    t=texts.T[x['code']]; rows.append(['пилот',int(x['idvh']),x['code'],x['name'],', '.join(str(c['quant']) for c in x['cards']),t['forms'],t['heading'],t['sub']]+t['chips']+[NOTE.get(x['code'],'')])
sheet(ws,['Этап','ID ВХ','Код поставщика','Наименование','Кванты','Формы слова в плашке','Заголовок','Подзаголовок','Подпись 1','Подпись 2','Подпись 3','Подпись 4','Что проверить'],rows,[8,9,10,50,16,28,24,36,30,30,30,30,46])
# ---------- Этапы
TS=json.load(open('/home/claude/typestats.json'))
def bgfor(d,t):
    tl=t.lower()
    if '(ми)' in d.lower(): return 'И1 / И2','зелёная','узкий'
    if 'тетради' in tl or 'дневники' in tl: return 'по линовке товара: Т11–Т13 линейка, Т21–Т24 клетка, Т31 косая, Т41 узкая, Т51 крупная клетка','красная','гротеск'
    if 'блокноты' in tl or 'блоки для записей' in tl: return 'Б11 по линовке / Б12 / Б13','красная','гротеск'
    if 'книги учёта' in tl: return 'П2','красная','гротеск'
    if 'чертёжные' in tl: return 'Ч1 / Ч2','синяя','узкий'
    if 'чернографитные' in tl or 'точилки' in tl: return 'К2','синяя','гротеск'
    if 'ручки' in tl or 'стержни' in tl: return 'Р11–Р16','синяя','гротеск'
    if 'маркеры' in tl or 'корректоры' in tl: return 'М1 / М2','синяя','гротеск'
    if d=='Письменные принадлежности': return 'Р13 / Р15','синяя','гротеск'
    if 'аксессуары для рисования' in tl: return 'Х2 — сделано в пилоте','фиолетовая','с засечками'
    if 'карандаши цветные' in tl or 'фломастеры' in tl or 'цветная бумага' in tl or 'пластилин' in tl: return 'К11–К14','фиолетовая','с засечками'
    if 'кисти' in tl or 'краски' in tl: return 'Х11–Х14, Х2','фиолетовая','с засечками'
    if 'альбомы' in tl or 'бумага для художников' in tl: return 'Б3','фиолетовая','с засечками'
    if 'графика' in tl: return 'К2 / К11','фиолетовая','с засечками'
    if d in('Рисование и творчество','Товары для художников'): return 'Х2 / Х11','фиолетовая','с засечками'
    if 'архивные' in tl: return 'П3','тёмно-бирюзовая','гротеск'
    if d=='Папки и архивация': return 'П11–П14, П2','тёмно-бирюзовая','гротеск'
    if 'обложки для тетрадей' in tl or 'подставки' in tl: return 'Шк1 / Шк2','красная','гротеск'
    if d=='Школьные товары': return 'Шк3 / Шк4','красная','гротеск'
    if 'бейджи' in tl: return 'Бж1 / Бж2','тёмно-бирюзовая','гротеск'
    if 'ножницы' in tl or 'клей' in tl: return 'Оф1–Оф3','тёмно-бирюзовая','гротеск'
    if 'скрепки' in tl or 'степлеры' in tl or 'дыроколы' in tl: return 'Оф4','тёмно-бирюзовая','гротеск'
    if 'доски' in tl: return 'Оф5','тёмно-бирюзовая','гротеск'
    if d=='Офисные принадлежности': return 'П12 / П13','тёмно-бирюзовая','гротеск'
    if d=='Хозтовары и бытовая химия': return 'Хз1–Хз3','голубая','гротеск'
    if 'картриджи' in tl: return 'Тх1','тёмно-бирюзовая','узкий'
    if d=='Техника и расходные материалы': return 'Тх2 / Тх3','тёмно-бирюзовая','узкий'
    if 'конверты' in tl: return 'Бм1','тёмно-бирюзовая','гротеск'
    if d=='Бумага, конверты, этикетки': return 'П14','тёмно-бирюзовая','гротеск'
    if 'рамки' in tl: return 'Пд2','фиолетовая','с засечками'
    if d=='Подарки, праздник, интерьер, прочее': return 'Пд1','фиолетовая','с засечками'
    return 'фон не выбран','не выбран','гротеск'
stages=[]; buckets=collections.OrderedDict(); CAP=300
def emit(lst): stages.append(lst)
for x in TS:
    if 'Аксессуары для рисования' in x['type']: continue
    if x['active']==0: continue
    if x['active']>=120:
        parts=math.ceil(x['active']/CAP)
        for p in range(parts): emit([(x,p+1,parts)])
    else:
        b=buckets.setdefault(x['dir'],[]); b.append((x,1,1))
        if sum(i[0]['active'] for i in b)>=200: emit(b); buckets[x['dir']]=[]
acc=[]
for d,b in buckets.items():
    acc+=b
    if sum(i[0]['active'] for i in acc)>=200: emit(acc); acc=[]
if acc:
    if stages and sum(i[0]['active'] for i in acc)<80: stages[-1]+=acc
    else: emit(acc)
rows=[]; pil=[x for x in TS if 'Аксессуары для рисования' in x['type']][0]
bg,col,fnt=bgfor(pil['dir'],pil['type'])
rows.append([0,'сделано 05.10.2026',pil['dir'],pil['type'],'',pil['active'],pil['cards_active'],pil['goods']-pil['active'],round(pil['orders']),bg,col,fnt,'Пилот: 44 товара, 158 карточек, включая товары без остатка'])
tot=0
for n,st in enumerate(stages,1):
    for x,p,parts in st:
        bg,col,fnt=bgfor(x['dir'],x['type']); part=f'{p} из {parts}' if parts>1 else ''
        act=math.ceil(x['active']/parts) if parts>1 else x['active']; crd=round(x['cards_active']/parts)
        rows.append([n,'',x['dir'],x['type'],part,act,crd,(x['goods']-x['active']) if p==1 else '',round(x['orders']) if p==1 else '',bg,col,fnt,''])
ws=wb.create_sheet('Этапы')
sheet(ws,['№ этапа','Статус','Направление','Тип','Часть типа','Активных товаров','Карточек WB у активных','Товаров без остатка и не в прайсе (вторая волна)','Заказы за 3 мес, ₽','Фон (код из каталога) — предложение','Цвет плашки — предложение','Шрифт заголовка — предложение','Комментарий'],rows,[9,16,30,46,10,11,12,16,12,36,16,16,40],yellow=(1,2,10,11,12))
print('stages',len(stages),'rows',len(rows)); 
import statistics; sz=[sum((math.ceil(x['active']/parts) if parts>1 else x['active']) for x,p,parts in st) for st in stages]; print(min(sz),statistics.median(sz),max(sz)); print(sz[:25])
json.dump([[ (x['type'],p,parts) for x,p,parts in st] for st in stages],open('stages.json','w'),ensure_ascii=False)
# ---------- Фоны
cat=json.load(open('/home/claude/bgcat/cat.json')); names=json.load(open('/home/claude/bgcat/names.json')); cat2=json.load(open('/home/claude/bgcat/cat2.json'))
KEEP='Оставлен (решение 05.10.2026)'
DEC={'Х2':'Утверждён 05.10.2026 — использован в пилоте','Б3':KEEP,'К2':KEEP,'П2':KEEP,'П3':KEEP,'Ч1':KEEP,'Ч2':KEEP,'И1':KEEP,'И2':KEEP,'П1':'Отклонён: отверстия отвлекают','Х1':'Отклонён: мазки заходят на название','К1':'Отклонён: штрихи мешают читать текст','Р1':'Отклонён','Р2':'Отклонён','Б1':'Отклонён: точки при линовке «клетка» вводят в заблуждение','Б2':'Отклонён: спираль не нужна','Т4':'Отклонён: фон тетради должен совпадать с линовкой','Т5':'Только для тетрадей на кольцах','Т1':'Заменён на Т11–Т13','Т2':'Заменён на Т21–Т24','Т3':'Заменён на Т31'}
cat3=json.load(open('/home/claude/bgcat/cat3.json'))
DEC3={'Пд2':'Принят 05.10.2026 — «супер»','Бм1':'Принят 05.10.2026 — «супер»','Пд1':'Принят 05.10.2026 как запасной — «так себе, можно взять»','Бм2':'Отклонён 05.10.2026; для бумаги и этикеток — П14','Хз4':'Отклонён 05.10.2026','М3':'Отклонён 05.10.2026','Хз1':'Принят 05.10.2026 — «отлично»','Хз2':'Принят 05.10.2026 — «отлично»','Хз3':'Принят 05.10.2026 — «отлично»'}
rows=[['1',c,names[b],t,DEC.get(c,''),''] for c,b,t in cat]+[['2',c,n,t,'Принят 05.10.2026 (общий отзыв: «вроде всё хорошо»)',''] for c,b,t,n in cat2]+[['3',c,n,t,DEC3.get(c,'Принят 05.10.2026'),''] for c,b,t,n in cat3]
ws=wb.create_sheet('Фоны'); sheet(ws,['Серия','Код','Фон','Для каких типов','Решение (утверждён / переделать / не нужен)','Комментарий'],rows,[8,8,28,46,50,40],yellow=(5,6))
# ---------- Правила
ws=wb.create_sheet('Правила')
info=['Накопительный реестр готовых обложек и последних фото. После каждого этапа на лист «Готово» дописываются новые карточки, на лист «Тексты обложек» — тексты, на листе «Этапы» ставится статус.',
'Файлы: обложка «ID ВХ_квант.jpg», последнее фото «ID ВХ_квант_last.jpg»; JPEG 900×1200. Доп. фото в выдачу не входят — в конце проекта скачиваются скриптом.',
'Плашка: «N <товар> в наборе»; у товаров-наборов — «N наборов в комплекте». У товаров с квантами плашка есть и на кванте 1; у одиночных товаров без квантов плашки нет.',
'Шрифт плашки: цифра — Unbounded, слово — Montserrat.',
'Стопка на обложке: столько копий фото, сколько единиц в кванте (не больше 40). У вытянутых товаров копии смещаются поперёк оси товара, чтобы количество считалось глазами. Если фото — коллаж из нескольких дизайнов, оно ставится один раз.',
'Белые и прозрачные товары: тёмная подложка под фото в цвет плашки.',
'Товары «ассорти», у которых главное фото — коллаж вариантов дизайна: на обложке коллаж ставится один раз; последнее фото не создаётся, в колонке «Файл последнего фото» пишется «НЕТ» (решение 05.10.2026).',
'Фон обложки тетрадей и блокнотов совпадает с линовкой товара (линейка, клетка, косая линейка, узкая линейка, крупная клетка). Рисунок фона не заходит под заголовок.',
'Последнее фото: белый фон #FFFFFF, без текста; товар в упаковке (если такого кадра нет — без упаковки; у наборов в гофрокоробе — раскрытая коробка); в кадре столько единиц, сколько в кванте.',
'Тексты обложек — только из названий, характеристик и описаний поставщика; при расхождении комплектности с этикеткой на фото приоритет у этикетки.',
'Лист «Этапы»: жёлтые колонки можно менять — номер этапа, фон, цвет плашки, шрифт. Один этап рассчитан на один чат.',
'Лист «Фоны»: серия 1 — первый каталог от 05.10.2026 с решениями; серия 2 — вторая подборка, принята; серия 3 — фоны для остальных типов, решения записаны 05.10.2026.']
for r in info: ws.append([r])
ws.column_dimensions['A'].width=160
for row in ws.iter_rows():
    for c in row: c.font=BF; c.alignment=Alignment(wrap_text=True,vertical='top')
wb.save('/mnt/user-data/outputs/Реестр_обложек_и_последних_фото.xlsx')
