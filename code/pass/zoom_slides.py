# Проход, шаг 4. Крупные листы zs_NN.jpg: слайды и кадры с небелым фоном (по одному на изображение) — читать текст слайдов
# Отбор: белая рамка кадра меньше 97 % или угол темнее 248 (meta.json из thumbs.py); одинаковые изображения показываются один раз.
import json
from zoom_sel import sheet
meta=json.load(open('meta.json')); seen=set(); keys=[]
for k in sorted(meta):
    m=meta[k]
    if (m['white']<0.97 or m['corner']<248) and m['md5'] not in seen: seen.add(m['md5']); keys.append(k)
for i in range(0,len(keys),20): sheet(keys[i:i+20],f'zs_{i//20+1:02d}.jpg')
print('слайдов и кадров с небелым фоном:',len(keys),'листов:',(len(keys)+19)//20)
