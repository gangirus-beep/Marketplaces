# Шаг 1. Карточки и товары одного типа из базы → cards.json, goods_t.json (запуск из рабочей папки этапа)
# python3 extract.py "Тетради общие"      — подстрока названия типа с листа «Типы»
import openpyxl, json, sys
TYPE=sys.argv[1]
wb=openpyxl.load_workbook('/mnt/project/Номенклатура_на_ВБ_медиаконтент.xlsx',read_only=True)
for sheet,out,ncol in (('Карточки WB','cards.json',20),('Товары','goods_t.json',12)):
    it=wb[sheet].iter_rows(values_only=True); hdr=list(next(it)); ti=hdr.index('Тип')
    rows=[r for r in it if isinstance(r[ti],str) and TYPE in r[ti]]
    json.dump(dict(hdr=hdr,rows=rows),open(out,'w'),ensure_ascii=False,default=str)
    print(sheet,len(rows),sorted({r[ti] for r in rows}))
