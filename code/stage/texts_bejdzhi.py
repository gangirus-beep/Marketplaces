import json,re
DATE='08.10.2026';STAGE='этап 4';STAGE_NO=4;TYPE='Бейджи'
ARCH='Этап_04_Бейджи_обложки_и_последние_фото.zip'
ACCENT='#136F63';PLAQUE='бирюзовая';FONT='grotesk';BG='badges'
BGCODE={'badges':'Бж1 · контуры бейджей','ribbon':'Бж2 · лента'}
T={};NOTE={};TONE_FORCE={};NEW_RULES=[];STAGE_COMMENT=''
def note(c,s):NOTE[c]=(NOTE.get(c,'')+' '+s).strip()
def dim(s):
 m=re.search(r'(\d+)\s*[хx×*]\s*(\d+)',str(s),re.I)
 return f'{m[1]} × {m[2]} мм' if m else ''
for x in json.load(open('goods.json')):
 c=x['code'];a=x['chars'];n=x['name'];lo=n.lower();brand='ДПС' if x['brand']=='dpskanc' else x['brand'];isbadge=lo.startswith('бейдж');length=a.get('Длина ленты/шнурка') or (str(a.get('Длина держателя'))+' см' if a.get('Длина держателя') else '');reellen=a.get('Длина нити в держателе-рулетке','')
 size=dim(n);ins=dim(a.get('Размер вкладыша (ДхШ)',a.get('Размер вставки','')))
 mat=a.get('Материал корпуса',a.get('Материал бейджа',a.get('Материал',''))).replace('твердый','Твёрдый');mat=mat[:1].upper()+mat[1:]
 holder=a.get('Тип крепления',a.get('Крепление',a.get('Вид крепления держателя','')))
 orient=a.get('Положение',a.get('Ориентация',''));orient=orient[:1].upper()+orient[1:]
 # Название определяет крепление, даже если поле характеристик ошибочно.
 if 'без держателя' in lo:holder='Без держателя'
 elif '2 карабина' in lo:holder='Два карабина'
 elif 'клипсой и булавкой' in lo or 'клипом и булавкой' in lo:holder='Клипса и булавка'
 elif 'рулетк' in lo:holder='Держатель-рулетка'
 elif 'съемным клипом' in lo:holder='Съёмный клип'
 elif 'петля с карабином' in lo:holder='Петля с карабином'
 elif 'магнитн' in lo:holder='Магнитное крепление'
 elif 'лент' in lo:holder='Лента'+(' '+length if length else '')
 elif 'шнурк' in lo:holder='Шнурок'+(' '+length if length else '')
 holder=holder[:1].upper()+holder[1:]
 if isbadge:
  heading='Бейдж'+(' '+size if size else '')
  sub=brand+' · '+orient.lower()
  chips=[('Вкладыш '+ins) if ins else ('Размер '+size),holder,mat or 'Для пропуска и именной карточки','Для именной карточки']
  if 'магнитн' in lo:chips[3]='Магнитное крепление';chips[1]=orient
  if 'самоламиниру' in lo:chips[3]='Самоламинирующийся'
  if 'на 2 карты' in lo:chips[3]='Для двух карт'
  elif 'двусторонн' in lo:chips[3]='Двусторонний'
  elif 'матовая' in lo:chips[3]='Матовая поверхность'
  elif 'защита от влаги и пыли' in lo:chips[3]='Защита от влаги и пыли'
  elif 'слайдер' in lo:chips[3]='Крышка-слайдер'
  elif 'силиконов' in lo:chips[3]='Для пропусков и ID-карт'
  elif 'zip-lock' in lo:chips[3]='Замок ZIP-LOCK'
  if 'БОЛЬШ' in n:chips[3]='Большой формат'
  if 'MAGNETIC' in n and 'изогнутый' in lo:chips[3]='Изогнутая форма'
  if brand=='MESHU':
   design=re.search('"([^"]+)"',n)[1];sub=brand+' · «'+design+'»';chips=['Размер корпуса '+size,'Лента с карабином' if 'лента' in lo else 'Петля с карабином',mat,'3D-печать' if '3D' in n else '2D-печать'];note(c,'Поля размеров поставщика разбиты некорректно; 110 × 70 мм — размер корпуса из названия, размер вкладыша не заявлен. ')
  forms='бейдж|бейджа|бейджей'
 else:
  reel='рулетк' in lo;heading='Держатель-рулетка' if reel else ('Шнурок для бейджа' if lo.startswith('шнурок') else 'Лента для бейджа');sub=brand+' · для бейджей'
  if reel:
   m=re.search(r'(\d+)\s*см',n,re.I);reellen=m[1]+' см' if m else reellen;chips=['Нить '+reellen,('Два карабина' if '2 карабина' in lo else 'Карабин' if 'карабин' in lo else 'Клип'), 'Петелька' if 'петелька' in lo else ('Лента '+length if length else 'Для бейджей'),'Корпус из пластика' if mat else 'Для пропусков и карт'];forms='держатель|держателя|держателей'
  else:
   m=re.search(r'(\d+)\s*см',n,re.I);length=m[1]+' см' if m else length
   fast='Силиконовый клип' if 'силиконовый клип' in lo else 'Съёмный клип-замок' if 'клип-замок' in lo else 'Металлический карабин' if 'карабин' in lo else 'Металлический клип' if 'металл' in lo else 'Клип'
   chips=['Длина '+length,fast,mat or 'Для крепления бейджа','Безопасное сцепление' if ('безопасн' in lo or a.get('Наличие безопасной застежки')=='да') else 'Для бейджей и пропусков'];forms='шнурок|шнурка|шнурков' if lo.startswith('шнурок') else 'лента|ленты|лент'
  if c=='235724':chips=['Нить 70 см','Лента 45 см','Петелька','Корпус из пластика']
  if c=='350535':chips=['Нить 70 см','Лента 45 см','Клипса','Для бейджей и пропусков']
 t=dict(forms=forms,heading=heading,sub=sub,chips=chips,bg='badges' if isbadge else 'ribbon')
 if x['unit']=='набор':
  count=int(re.search(r'КОМПЛЕКТ\s+(\d+)',n)[1]);t.update(forms='набор|набора|наборов',line2=f'по {count} бейджей',line2_1=f'{count} бейджей');chips[3]=f'{count} бейджей в каждом наборе'
 if x['assorti']=='ассорти':t['copies']=1;chips[3]='Цвет — в ассортименте'
 if c=='284664':note(c,'Название: чёрный шнурок; характеристика «Цвет держателя»: жёлтый. Приоритет у названия; цвет не вынесен в подписи.')
 if isbadge and brand!='MESHU':
  titleinsert=re.search(r'размер вставки\s*([\d*хx× ]+)',n,re.I)
  if titleinsert:
   ds=dim(titleinsert[1]);chips[0]='Вкладыш '+ds
   if ds!=ins:note(c,f'Размер вставки в названии {ds}, в характеристиках {ins}; приоритет у названия.')
  if ins and size and not titleinsert and sorted(re.findall(r'\d+',size))!=sorted(re.findall(r'\d+',ins)):
   note(c,f'Размер в названии {size}, вкладыш в характеристиках {ins}; эти размеры не смешаны.')
 assert len(chips)==4 and all(v and len(v)<=38 for v in chips),(c,chips)
 if (a.get('Цвет корпуса',a.get('Цвет бейджа')) in ('прозрачный','белый') or c in ['231903','231906','231907','350529','350535','238785','235723']): TONE_FORCE[c]='panel'
 if isbadge and x['unit']=='штука' and ('лента' in holder.lower() or 'шнурок' in holder.lower() or 'съёмный клип' in holder.lower()) and brand!='MESHU': t['cord']=True
 T[c]=t

for c in ['359588','359590','380522','380521','380525','380524','380523']:
 T[c]['cord']=True
for c in ['232152','235723','235738','235727','359588','359590']:
 note(c,'На обложке выбран один вид изделия из исходного кадра с несколькими видами; квант считает изделия, а не виды.')

for x in json.load(open('goods.json')):
 if 'на синем шнурке' in x['name'].lower() or 'на красном шнурке' in x['name'].lower() or 'на черном шнурке' in x['name'].lower() or 'на зеленом шнурке' in x['name'].lower(): T[x['code']]['cord']=True
for ch in [{'code': '235738', 'oldU': 1, 'U': 2, 'Uurl': 'https://s3.ibta.ru/goods/235738/8c5a953f4ce71f5b30fdae6c5b84fb85_xl.jpg', 'oldW': 2, 'W': 2, 'Wurl': 'https://s3.ibta.ru/goods/235738/8c5a953f4ce71f5b30fdae6c5b84fb85_xl.jpg', 'AA': 2, 'AB': 1, 'reason': 'Полный кадр лицевой стороны анфас вместо коллажа двух видов.'}, {'code': '284662', 'oldU': 1, 'U': 2, 'Uurl': 'http://relefopt.ru/getimage.php?guid=f467a021-7c62-11e9-80c2-30e1715c5317_Ракурс_1', 'oldW': 1, 'W': 1, 'Wurl': 'http://relefopt.ru/getimage.php?guid=f467a021-7c62-11e9-80c2-30e1715c5317', 'AA': 1, 'AB': 2, 'reason': 'Одна рулетка без блистера, анфас.'}, {'code': '284663', 'oldU': 1, 'U': 6, 'Uurl': 'http://relefopt.ru/getimage.php?guid=f467a023-7c62-11e9-80c2-30e1715c5317_Ракурс_5', 'oldW': 1, 'W': 9, 'Wurl': 'http://relefopt.ru/getimage.php?guid=f467a023-7c62-11e9-80c2-30e1715c5317_Ракурс_9', 'AA': 9, 'AB': 6, 'reason': 'Чёрная рулетка без блистера, анфас; №1 показывает синюю. Упаковка чёрного товара — №9.'}, {'code': '238238', 'oldU': 1, 'U': 2, 'Uurl': 'https://s3.ibta.ru/goods/238238/bbf21fe1ad37cf6eec709e97a9bee510_xl.jpg', 'oldW': 5, 'W': 5, 'Wurl': 'https://s3.ibta.ru/goods/238238/3e1a399bc777b0353d957f63c96a5631_xl.jpg', 'AA': 5, 'AB': 1, 'reason': 'Белая рулетка анфас, полный кадр без упаковки.'}, {'code': '238240', 'oldU': 1, 'U': 2, 'Uurl': 'https://s3.ibta.ru/goods/238240/870a39557a4cb6f8bcaa0c2a1692398f_xl.jpg', 'oldW': 5, 'W': 5, 'Wurl': 'https://s3.ibta.ru/goods/238240/870636dc56223019cab8b52a448f20d7_xl.jpg', 'AA': 5, 'AB': 1, 'reason': 'Белая рулетка анфас, полный кадр без упаковки.'}, {'code': '238823', 'oldU': 1, 'U': 7, 'Uurl': 'https://s3.ibta.ru/goods/238823/dd140fdcfe34b6baf3df8267f6448df0_xl.jpg', 'oldW': 1, 'W': 1, 'Wurl': 'https://s3.ibta.ru/goods/238823/95ce37d6bcf35b0e536b97fd882c059f_xl.jpg', 'AA': 9, 'AB': 2, 'reason': 'Полное изделие со сложенной лентой; корпус крупнее в квантовой стопке.'}, {'code': '238827', 'oldU': 1, 'U': 7, 'Uurl': 'https://s3.ibta.ru/goods/238827/a00a4a0dde1915889d3a043434bd04d4_xl.jpg', 'oldW': 1, 'W': 1, 'Wurl': 'https://s3.ibta.ru/goods/238827/e25906073409edf3b715c315eb7662dc_xl.jpg', 'AA': 9, 'AB': 2, 'reason': 'Полное изделие со сложенной лентой; корпус крупнее в квантовой стопке.'}, {'code': '238830', 'oldU': 1, 'U': 3, 'Uurl': 'https://s3.ibta.ru/goods/238830/c5e2ea56065ebaedeaafbdcb09f52bd9_xl.jpg', 'oldW': 1, 'W': 1, 'Wurl': 'https://s3.ibta.ru/goods/238830/6509a3542578f4007ba131fa1590a071_xl.jpg', 'AA': 9, 'AB': 1, 'reason': 'Полное изделие со сложенной лентой; корпус крупнее в квантовой стопке.'}, {'code': '238831', 'oldU': 1, 'U': 3, 'Uurl': 'https://s3.ibta.ru/goods/238831/6e732a214717129a30c8cf686176335a_xl.jpg', 'oldW': 1, 'W': 1, 'Wurl': 'https://s3.ibta.ru/goods/238831/8ac81f6d96673e8bcf1cc23cb29d84e7_xl.jpg', 'AA': 9, 'AB': 1, 'reason': 'Полное изделие со сложенной лентой; корпус крупнее в квантовой стопке.'}, {'code': '238832', 'oldU': 1, 'U': 3, 'Uurl': 'https://s3.ibta.ru/goods/238832/b0e8fd5f98d12b0e9d3dcbf9d4fe8bf5_xl.jpg', 'oldW': 1, 'W': 1, 'Wurl': 'https://s3.ibta.ru/goods/238832/b21fe04612998f6e8a92d3f0489810e8_xl.jpg', 'AA': 8, 'AB': 1, 'reason': 'Полное изделие со сложенной лентой; корпус крупнее в квантовой стопке.'}, {'code': '238833', 'oldU': 1, 'U': 3, 'Uurl': 'https://s3.ibta.ru/goods/238833/a5bed52fd21a25ce916bee89ce9419b9_xl.jpg', 'oldW': 1, 'W': 1, 'Wurl': 'https://s3.ibta.ru/goods/238833/d1a6e0d1dda1a8786a1ab7439749b05e_xl.jpg', 'AA': 8, 'AB': 1, 'reason': 'Полное изделие со сложенной лентой; корпус крупнее в квантовой стопке.'}, {'code': '238834', 'oldU': 1, 'U': 3, 'Uurl': 'https://s3.ibta.ru/goods/238834/e7287abbe377ba4e34dbf762952d3e68_xl.jpg', 'oldW': 1, 'W': 1, 'Wurl': 'https://s3.ibta.ru/goods/238834/ee1eb8f16123c9505671bfbc300f9b85_xl.jpg', 'AA': 9, 'AB': 1, 'reason': 'Полное изделие со сложенной лентой; корпус крупнее в квантовой стопке.'}, {'code': '238835', 'oldU': 1, 'U': 3, 'Uurl': 'https://s3.ibta.ru/goods/238835/3e5934eeba8fda722b7d94df81911d9b_xl.jpg', 'oldW': 1, 'W': 1, 'Wurl': 'https://s3.ibta.ru/goods/238835/f92ada2d563f47141a71064ad2713c6f_xl.jpg', 'AA': 9, 'AB': 1, 'reason': 'Полное изделие со сложенной лентой; корпус крупнее в квантовой стопке.'}, {'code': '238904', 'oldU': 2, 'U': 3, 'Uurl': 'https://s3.ibta.ru/goods/238904/6daff5f81e2cd989684358bc4828160f_xl.jpg', 'oldW': 7, 'W': 7, 'Wurl': 'https://s3.ibta.ru/goods/238904/c15187abd0067597efdf11eebb5ec87d_xl.jpg', 'AA': 7, 'AB': 2, 'reason': 'Лицевая сторона без этикетки; прежний №2 — оборот.'}]:
 note(ch['code'],f'Пересмотр кандидатов 08.10.2026: обложка №{ch["oldU"]} → №{ch["U"]}. '+ch['reason'])
