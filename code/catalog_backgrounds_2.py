import json, sys
sys.path.insert(0,'/home/claude/pilot')
from axis import axis as AX
from playwright.sync_api import sync_playwright
from PIL import Image, ImageDraw, ImageFont
R=json.load(open('/home/claude/bgcat/ratios.json'))
A='/home/claude/assets/'; C='/home/claude/bgcat/cut/'
RED='#D3401F'; BLUE='#1F5FBF'; VIO='#6A3DB8'; TEAL='#136F63'
NB=dict(forms='тетрадь|тетради|тетрадей',font='grotesk',accent=RED)
nb_line=dict(NB,heading='Тетрадь 48 листов',sub='А5, линия · STAFF',chips=['Формат А5, 165 × 205 мм','Линия с полями','Обложка — мелованный картон','Цвета в ассортименте'],img=C+'402786.png',ratio=R['402786'],copies=1)
nb_grid=dict(NB,heading='Тетрадь 48 листов',sub='А5, клетка · STAFF',chips=['Формат А5, 165 × 205 мм','Клетка с полями','Обложка — мелованный картон','Цвета в ассортименте'],img=C+'402782.png',ratio=R['402782'],copies=1)
nb_obl=dict(NB,heading='Тетрадь 12 листов',sub='косая линия · BG «Однотонный. Зелёный»',chips=['Формат А5, 165 × 205 мм','Пластиковая прозрачная обложка','Белизна бумаги 100%, 60 г/м²','С полями, на скрепке'],img=C+'379114.png',ratio=R['379114'])
nb_nar=dict(NB,heading='Тетрадь 12 листов',sub='узкая линия · BG «Однотонный. Зелёный»',chips=['Формат А5, 165 × 205 мм','Пластиковая прозрачная обложка','Белизна бумаги 100%, 60 г/м²','С полями, на скрепке'],img=A+'notebook_382228.webp',ratio=0.8062)
nb_big=dict(NB,heading='Тетрадь 12 листов',sub='крупная клетка · BG «Первая пятёрка»',chips=['Крупная клетка с полями','Обложка — офсет','Белизна бумаги 100%','На скрепке'],img=C+'357463.png',ratio=R['357463'])
blk=dict(forms='блокнот|блокнота|блокнотов',font='grotesk',accent=RED,heading='Блокнот А7, 40 листов',sub='клетка, на гребне · BRAUBERG',chips=['75 × 105 мм','Гребень сверху','Обложка — мелованный картон','Дизайны в ассортименте'],img=C+'116430.png',ratio=R['116430'],copies=1)
pen=dict(forms='ручка|ручки|ручек',font='grotesk',accent=BLUE,heading='Ручка шариковая',sub='масляная, синяя · STAFF Basic',chips=['Узел 0,7 мм, линия 0,35 мм','Чернила на масляной основе','Трёхгранный корпус','Игольчатый наконечник'],img=C+'143023.png',ratio=R['143023'])
cray=dict(forms='набор|набора|наборов',font='serif',accent=VIO,heading='Восковые мелки',sub='набор 6 цветов · ПИФАГОР «Солнышко»',chips=['6 ярких цветов','Круглые, диаметр 8 мм','В бумажной обёртке','Коробка с европодвесом'],img=C+'227278.png',ratio=R['227278'],line2='в комплекте')
brush=dict(forms='кисть|кисти|кистей',font='serif',accent=VIO,heading='Кисть белка № 5',sub='круглая, с колпачком · ПИФАГОР',chips=['Волос белки','Для акварели, гуаши, туши','Деревянная лакированная ручка','Защитный колпачок'],img=C+'200819.png',ratio=R['200819'])
reg=dict(forms='папка|папки|папок',font='grotesk',accent=TEAL,heading='Папка-регистратор',sub='80 мм, ПВХ, синяя · BRAUBERG',chips=['Формат А4, до 600 листов','Покрытие ПВХ — можно протирать','Карман на корешке','Металлическая защита нижней кромки'],img=C+'227191.png',ratio=R['227191'])
CAT=[('Т11','line_a','Тетради в линейку',nb_line,10),('Т12','line_b','Тетради в линейку',nb_line,20),('Т13','line_c','Тетради в линейку',nb_line,5),('Т31','oblique_a','Тетради в косую линейку',nb_obl,10),('Т41','narrow_a','Тетради в узкую линейку',nb_nar,10),
 ('Т21','grid_a','Тетради в клетку',nb_grid,10),('Т22','grid_b','Тетради в клетку',nb_grid,20),('Т23','grid_c','Тетради в клетку',nb_grid,5),('Т24','grid_d','Тетради в клетку',nb_grid,15),('Т51','big_a','Тетради в крупную клетку',nb_big,10),
 ('Р11','propis','Ручки',pen,10),('Р12','flourish','Ручки',pen,10),('Р13','plus','Ручки',pen,10),('Р14','geo','Ручки',pen,10),('Р15','diag','Ручки',pen,10),('Р16','halftone','Ручки',pen,10),
 ('К11','edge','Цветные карандаши, мелки, фломастеры',cray,5),('К12','tips','Цветные карандаши, мелки, фломастеры',cray,5),('К13','confetti','Цветные карандаши, мелки, фломастеры',cray,5),('К14','arcs','Цветные карандаши, мелки, фломастеры',cray,5),
 ('Х11','canvas','Кисти, краски',brush,5),('Х12','dabs','Кисти, краски',brush,5),('Х13','papercool','Кисти, краски',brush,5),('Х14','paperwarm','Кисти, краски',brush,5),
 ('П11','tabs','Папки-регистраторы, файлы',reg,2),('П12','greygrid','Папки, офис',reg,2),('П13','diagt','Папки, офис',reg,2),('П14','stack','Папки, офис',reg,2),
 ('Б11','grid_b','Блокноты в клетку — фон по линовке',blk,10),('Б12','geow','Блокноты',blk,10),('Б13','plusg','Блокноты',blk,10)]
with sync_playwright() as p:
    b=p.chromium.launch(args=['--no-sandbox','--allow-file-access-from-files']); pg=b.new_page(viewport={'width':900,'height':1200})
    pg.goto('file:///home/claude/pilot/cover.html')
    names=pg.evaluate('Object.fromEntries(Object.entries(BG).map(([k,v])=>[k,v.name]))')
    for code,bg,typ,d,q in CAT:
        dd=dict(d); dd.update(qty=q,bg=bg,tone='light'); dd.setdefault('line2','в наборе'); dd.update(AX(dd['img']))
        r=pg.evaluate('d=>render(d)',dd); pg.wait_for_timeout(60); pg.screenshot(path=f'/home/claude/bgcat/out2/{code}_{bg}.jpg',type='jpeg',quality=92,clip={'x':0,'y':0,'width':900,'height':1200})
    b.close()
json.dump([(c,b,t,names[b]) for c,b,t,_,_ in CAT],open('/home/claude/bgcat/cat2.json','w'),ensure_ascii=False)
fb=ImageFont.truetype('/home/claude/pilot/fonts/Manrope.ttf',30); fb.set_variation_by_axes([800])
fs=ImageFont.truetype('/home/claude/pilot/fonts/Manrope.ttf',21); fs.set_variation_by_axes([500])
def sheet(items,path,cols,w=540):
    h=w*4//3; pad=24; cap=92; rows=(len(items)+cols-1)//cols
    S=Image.new('RGB',(cols*(w+pad)+pad,rows*(h+cap+pad)+pad),(255,255,255)); d=ImageDraw.Draw(S)
    for i,(c,bg,t,_,_) in enumerate(items):
        x=pad+(i%cols)*(w+pad); y=pad+(i//cols)*(h+cap+pad)
        im=Image.open(f'/home/claude/bgcat/out2/{c}_{bg}.jpg').resize((w,h),Image.LANCZOS); S.paste(im,(x,y)); d.rectangle([x,y,x+w-1,y+h-1],outline=(200,200,200))
        d.text((x,y+h+8),f'{c} · {names[bg]}',fill=(20,20,20),font=fb); d.text((x,y+h+50),t,fill=(90,90,90),font=fs)
    S.save(path,quality=90)
O='/home/claude/bgcat/'
sheet(CAT[:10],O+'Фоны_серия2_лист1_тетради.jpg',5)
sheet(CAT[10:16],O+'Фоны_серия2_лист2_ручки.jpg',3)
sheet(CAT[16:24],O+'Фоны_серия2_лист3_карандаши_кисти.jpg',4)
sheet(CAT[24:],O+'Фоны_серия2_лист4_папки_блокноты.jpg',4)
