import json, sys
sys.path.insert(0,'/home/claude/pilot')
from axis import axis as AX
from playwright.sync_api import sync_playwright
R=json.load(open('/home/claude/bgcat/ratios.json'))
A='/home/claude/assets/'; C='/home/claude/bgcat/cut/'
RED='#D3401F'; BLUE='#1F5FBF'; VIO='#6A3DB8'; GRN='#1E7A46'; TEAL='#136F63'
NB=dict(forms='тетрадь|тетради|тетрадей',font='grotesk',accent=RED)
nb_l=dict(NB,heading='Тетрадь 12 листов',sub='узкая линия · BG «Однотонный. Зелёный»',chips=['Формат А5, 165 × 205 мм','Пластиковая прозрачная обложка','Белизна бумаги 100%, 60 г/м²','С полями, на скрепке'],img=A+'notebook_382228.webp',ratio=0.8062)
nb_o=dict(NB,heading='Тетрадь 12 листов',sub='косая линия · BG «Однотонный. Зелёный»',chips=['Формат А5, 165 × 205 мм','Пластиковая прозрачная обложка','Белизна бумаги 100%, 60 г/м²','С полями, на скрепке'],img=C+'379114.png',ratio=R['379114'])
nb_g=dict(NB,heading='Тетрадь 48 листов',sub='А5, клетка · STAFF',chips=['Формат А5, 165 × 205 мм','Клетка с полями','Обложка — мелованный картон','Цвета в ассортименте'],img=C+'402782.png',ratio=R['402782'])
blk=dict(forms='блокнот|блокнота|блокнотов',font='grotesk',accent=RED,heading='Блокнот А7, 40 листов',sub='клетка, на гребне · BRAUBERG',chips=['75 × 105 мм','Гребень сверху','Обложка — мелованный картон','Дизайны в ассортименте'],img=C+'116430.png',ratio=R['116430'])
alb=dict(forms='альбом|альбома|альбомов',font='serif',accent=VIO,heading='Альбом для рисования',sub='А4, 24 листа, гребень · BRAUBERG',chips=['195 × 285 мм','Бумага 100 г/м²','Для красок, карандашей, фломастеров','Дизайны в ассортименте'],img=C+'106695.png',ratio=R['106695'])
pen=dict(forms='ручка|ручки|ручек',font='grotesk',accent=BLUE,heading='Ручка шариковая',sub='масляная, синяя · STAFF Basic',chips=['Узел 0,7 мм, линия 0,35 мм','Чернила на масляной основе','Трёхгранный корпус','Игольчатый наконечник'],img=C+'143023.png',ratio=R['143023'])
cray=dict(forms='набор|набора|наборов',font='serif',accent=VIO,heading='Восковые мелки',sub='набор 6 цветов · ПИФАГОР «Солнышко»',chips=['6 ярких цветов','Круглые, диаметр 8 мм','В бумажной обёртке','Коробка с европодвесом'],img=C+'227278.png',ratio=R['227278'],line2='в комплекте')
pcl=dict(forms='карандаш|карандаша|карандашей',font='grotesk',accent=RED,heading='Карандаш чернографитный',sub='HB, заточенный · STAFF EVERYDAY',chips=['Твёрдость HB, грифель 2,2 мм','Ударопрочный грифель','Шестигранный пластиковый корпус','Длина 176 мм'],img=C+'181938.png',ratio=R['181938'])
brush=dict(forms='кисть|кисти|кистей',font='serif',accent=VIO,heading='Кисть белка № 5',sub='круглая, с колпачком · ПИФАГОР',chips=['Волос белки','Для акварели, гуаши, туши','Деревянная лакированная ручка','Защитный колпачок'],img=C+'200819.png',ratio=R['200819'])
mat=dict(forms='покрытие|покрытия|покрытий',font='serif',accent=VIO,heading='Настольное покрытие',sub='для труда и творчества · BRAUBERG KIDS',chips=['50 × 35 см — почти на всю парту','ПВХ, легко очищается','Складывается, помещается в рюкзак','Каждое — в отдельном пакете'],img=A+'mat_272360.webp',ratio=1.4536)
reg=dict(forms='папка|папки|папок',font='grotesk',accent=TEAL,heading='Папка-регистратор',sub='80 мм, ПВХ, синяя · BRAUBERG',chips=['Формат А4, до 600 листов','Покрытие ПВХ — можно протирать','Карман на корешке','Металлическая защита нижней кромки'],img=C+'227191.png',ratio=R['227191'])
skor=dict(forms='скоросшиватель|скоросшивателя|скоросшивателей',font='grotesk',accent=TEAL,heading='Скоросшиватель картонный',sub='А4, 400 г/м² · BRAUBERG',chips=['До 200 листов','Картон 400 г/м², немелованный','Металлический механизм','Надпись «Дело №» на обложке'],img=C+'126524.png',ratio=R['126524'])
comp=dict(forms='циркуль|циркуля|циркулей',font='tech',accent=BLUE,heading='Циркуль «Козья ножка»',sub='металлический, 105 мм · ПИФАГОР',chips=['Металл, серебристый корпус','Длина 105 мм','Несгибаемая штанга','Без карандаша в комплекте'],img=A+'compass_210600.webp',ratio=0.2719)
disc=dict(forms='круг|круга|кругов',font='tech',accent=GRN,heading='Круг отрезной по металлу',sub='150 × 1,8 × 22,2 мм · DENZEL',chips=['Диаметр 150 мм, толщина 1,8 мм','Посадочный диаметр 22,2 мм','До 10 200 об/мин','Для углеродистой и нержавеющей стали'],img=A+'disc_73773.webp',ratio=0.9964)
CAT=[('Т1','lined','Тетради в линейку',nb_l,10),('Т2','grid','Тетради в клетку',nb_g,10),('Т3','oblique','Тетради в косую линейку',nb_o,10),('Т4','legal','Тетради общие — вариант 2',nb_g,20),('Т5','rings','Тетради на кольцах и спирали, сменные блоки',nb_g,5),
 ('Б1','dots','Блокноты, записные книжки',blk,10),('Б2','spiral','Блокноты и альбомы на гребне',blk,20),('Б3','sketch','Альбомы, бумага для рисования',alb,4),
 ('Р1','waves','Ручки',pen,10),('Р2','form','Ручки — вариант 2',pen,30),('К1','hatch','Цветные карандаши, мелки, фломастеры',cray,5),('К2','graphite','Чернографитные карандаши',pcl,50),
 ('Х1','strokes','Кисти, краски',brush,5),('Х2','paper','Аксессуары для рисования (уже в пилоте)',mat,4),
 ('П1','punched','Папки-регистраторы, файлы, скоросшиватели',reg,2),('П2','ledger','Папки, офис — вариант 2',reg,4),('П3','kraft','Архивные папки и короба',skor,10),
 ('Ч1','mm','Чертёжные принадлежности',comp,5),('Ч2','blueprint','Чертёжные — вариант 2',comp,10),('И1','pegboard','Инструмент МИ',disc,10),('И2','plate','Инструмент МИ — вариант 2',disc,4)]
json.dump([(c,b,t) for c,b,t,_,_ in CAT],open('/home/claude/bgcat/cat.json','w'),ensure_ascii=False)
with sync_playwright() as p:
    b=p.chromium.launch(args=['--no-sandbox','--allow-file-access-from-files']); pg=b.new_page(viewport={'width':900,'height':1200})
    pg.goto('file:///home/claude/pilot/cover.html')
    names=pg.evaluate('Object.fromEntries(Object.entries(BG).map(([k,v])=>[k,v.name]))'); json.dump(names,open('/home/claude/bgcat/names.json','w'),ensure_ascii=False)
    for code,bg,typ,d,q in CAT:
        dd=dict(d); dd.update(qty=q,bg=bg,tone='light'); dd.setdefault('line2','в наборе')
        dd.update(AX(dd['img']))
        if d is nb_g or d is blk or d is alb: dd['copies']=1
        r=pg.evaluate('d=>render(d)',dd); pg.screenshot(path=f'/home/claude/bgcat/out/{code}_{bg}.jpg',type='jpeg',quality=92,clip={'x':0,'y':0,'width':900,'height':1200})
        print(code,bg,r['font'],r['hsize'],r['mode'])
    b.close()
