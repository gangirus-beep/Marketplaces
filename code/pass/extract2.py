# выборка нескольких типов сразу (точные названия типов)
import openpyxl, json, sys
TYPES=sys.argv[1:]
wb=openpyxl.load_workbook('/mnt/project/Номенклатура_на_ВБ_медиаконтент.xlsx',read_only=True)
for sheet,out in (('Карточки WB','cards.json'),('Товары','goods_t.json')):
    it=wb[sheet].iter_rows(values_only=True); hdr=list(next(it)); ti=hdr.index('Тип')
    rows=[r for r in it if isinstance(r[ti],str) and any(T in r[ti] for T in TYPES)]
    json.dump(dict(hdr=hdr,rows=rows),open(out,'w'),ensure_ascii=False,default=str)
    import collections
    print(sheet,len(rows),collections.Counter(r[ti] for r in rows))
