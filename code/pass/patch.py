# Запись колонок U, V, W, Y, AA, AB, AC листа «Карточки WB» на уровне XML по new.json (из decide_*.py) + строка «Сделано в проходе» в «Справку» из spravka.txt.
# Перед запуском: mkdir /home/claude/bx && cd /home/claude/bx && unzip -q /mnt/project/Номенклатура_на_ВБ_медиаконтент.xlsx
# Колонки X (ассорти) и Z (тип единицы) скрипт не трогает; чтобы менять X, добавьте 'X' в COLS.
import json, re, collections
from xml.sax.saxutils import escape
BX='/home/claude/bx/xl/'
c=json.load(open('cards.json')); h=c['hdr']; ix={n:i for i,n in enumerate(h)}
new=json.load(open('new.json'))
wb2code={str(r[ix['Артикул WB']]):str(r[ix['Код поставщика']]) for r in c['rows']}
assert len(wb2code)==len(c['rows'])
head=open(BX+'sharedStrings.xml','rb').read(400).decode('utf-8','ignore')
m=re.search(r'count="(\d+)" uniqueCount="(\d+)"',head); cnt,ucnt=int(m.group(1)),int(m.group(2))
newstr=collections.OrderedDict()
def sid(t):
    if t not in newstr: newstr[t]=ucnt+len(newstr)
    return newstr[t]
COLS=['U','V','W','X','Y','AA','AB','AC']
def colnum(cn):
    n=0
    for ch in cn: n=n*26+ord(ch)-64
    return n
s=open(BX+'worksheets/sheet4.xml',encoding='utf-8').read()
cell_re=re.compile(r'<c r="([A-Z]+)(\d+)"[^>]*?(?:/>|>.*?</c>)',re.S)
out=[]; pos=0; done=0; refs_removed=0; refs_added=0
for m in re.finditer(r'<row r="(\d+)"[^>]*>(.*?)</row>',s,re.S):
    body=m.group(2)
    a=re.match(r'<c r="A\d+"[^>]*><v>(\d+)</v></c>',body)
    if not a or a.group(1) not in wb2code: continue
    rn=m.group(1); v=new[wb2code[a.group(1)]]
    cells=[(colnum(cm.group(1)),cm.group(0)) for cm in cell_re.finditer(body)]
    assert ''.join(x[1] for x in cells)==body, rn
    keep=[x for x in cells if x[0] not in {colnum(cc) for cc in COLS}]
    refs_removed+=len(cells)-len(keep)
    for cc in COLS:
        val=v[cc]
        if val:
            keep.append((colnum(cc),f'<c r="{cc}{rn}" s="0" t="s"><v>{sid(val)}</v></c>')); refs_added+=1
    keep.sort(key=lambda x:x[0])
    out.append(s[pos:m.start(2)]); out.append(''.join(x[1] for x in keep)); pos=m.end(2); done+=1
out.append(s[pos:]); s2=''.join(out)
assert done==len(wb2code),(done,len(wb2code))
open(BX+'worksheets/sheet4.xml','w',encoding='utf-8').write(s2)
# --- Справка: строка «Сделано в проходе» из spravka.txt (если файл есть)
import os
if os.path.exists('spravka.txt'):
    txt=open('spravka.txt',encoding='utf-8').read().strip()
    s7=open(BX+'worksheets/sheet7.xml',encoding='utf-8').read()
    rn7=len(re.findall(r'<row r=',s7))+1
    a7=re.search(r'<c r="A%d" s="17" t="s"><v>(\d+)</v></c>'%(rn7-1),s7).group(1)   # «Сделано в проходе» — та же строка, что выше
    row=f'<row r="{rn7}" customFormat="false" ht="135" hidden="false" customHeight="true" outlineLevel="0" collapsed="false"><c r="A{rn7}" s="17" t="s"><v>{a7}</v></c><c r="B{rn7}" s="18" t="s"><v>{sid(txt)}</v></c></row>'
    s7=s7.replace('</row></sheetData>','</row>'+row+'</sheetData>')
    s7=re.sub(r'<dimension ref="A1:B\d+"/>',f'<dimension ref="A1:B{rn7}"/>',s7)
    open(BX+'worksheets/sheet7.xml','w',encoding='utf-8').write(s7); refs_added+=2
# --- sharedStrings
b=open(BX+'sharedStrings.xml','rb').read()
assert b.rstrip().endswith(b'</sst>')
add=''.join(f'<si><t xml:space="preserve">{escape(t)}</t></si>' for t in newstr).encode('utf-8')
i=b.rfind(b'</sst>'); b=b[:i]+add+b[i:]
old=f'count="{cnt}" uniqueCount="{ucnt}"'.encode(); newh=f'count="{cnt-refs_removed+refs_added}" uniqueCount="{ucnt+len(newstr)}"'.encode()
assert b.count(old,0,500)==1; b=b.replace(old,newh,1)
open(BX+'sharedStrings.xml','wb').write(b)
print('rows patched',done,'new strings',len(newstr),'refs removed',refs_removed,'added',refs_added)
