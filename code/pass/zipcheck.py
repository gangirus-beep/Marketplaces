# Сборка базы обратно в xlsx и сверка всех строк с исходной: python3 zipcheck.py "Тетради общие 40+ л и А4"
import zipfile, os, json, openpyxl, collections, sys
TYPE=sys.argv[1]
SRC='/mnt/project/Номенклатура_на_ВБ_медиаконтент.xlsx'; OUT='/mnt/user-data/outputs/Номенклатура_на_ВБ_медиаконтент.xlsx'
zi=zipfile.ZipFile(SRC)
with zipfile.ZipFile(OUT,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as zo:
    for info in zi.infolist():
        p='/home/claude/bx/'+info.filename
        if info.filename.endswith('/'): continue
        zo.write(p,info.filename)
print('size MB',round(os.path.getsize(OUT)/1e6,1))
new=json.load(open('new.json'))
a=openpyxl.load_workbook(SRC,read_only=True)['Карточки WB'].iter_rows(values_only=True)
wbn=openpyxl.load_workbook(OUT,read_only=True)
b=wbn['Карточки WB'].iter_rows(values_only=True)
n=0; diff_out=0; ok_in=0; bad=[]
ha=next(a); hb=next(b); assert ha==hb
E=lambda x: x or None
for ra,rb in zip(a,b):
    n+=1
    ra=tuple(ra)+(None,)*(29-len(ra)); rb=tuple(rb)+(None,)*(29-len(rb))
    if ra[11] in sys.argv[1:]:
        v=new[str(ra[9])]
        exp=(E(v['U']),E(v['V']),E(v['W']),E(v['X']),E(v['Y']),ra[25],E(v['AA']),E(v['AB']),E(v['AC']))
        if ra[:20]==rb[:20] and tuple(rb[20:29])==exp: ok_in+=1
        else: bad.append((n,rb[0]))
    elif ra!=rb: diff_out+=1
print('rows',n,'type rows ok',ok_in,'bad',bad[:5],'changed outside type',diff_out)
ws=wbn['Справка']
for r in ws.iter_rows(min_row=28,values_only=True): print([str(x)[:120] for x in r if x])
print([ (s.title) for s in wbn.worksheets])
