"""Pack the adjacent code directory into an XLSX; accepts version and output path."""
import os,io,zipfile,base64,hashlib,sys
from pathlib import Path
import openpyxl
from openpyxl.styles import Font,Alignment
root=Path(os.environ.get('WB_GENERATOR_ROOT',Path(__file__).resolve().parent))
out=Path(sys.argv[2]) if len(sys.argv)>2 else Path.cwd()/'output/Генератор_обложек_WB.xlsx'
version=sys.argv[1] if len(sys.argv)>1 else 'Рабочая версия генератора'
files=[]
for p in root.rglob('*'):
 if not p.is_file() or '__pycache__' in p.parts or p.suffix=='.pyc':continue
 rel=p.relative_to(root)
 if len(rel.parts)>1:
  if rel.parts[0] not in {'fonts','pass','pilot','stage'}:continue
 elif not(p.name=='axis.py' or p.name.startswith('catalog_') or p.name in {'README.md','cover.html','pack_gen.py','samson_download.py'}):continue
 files.append(p)
files.sort();buf=io.BytesIO()
with zipfile.ZipFile(buf,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
 for p in files:z.write(p,str(p.relative_to(root)))
raw=buf.getvalue();sha=hashlib.sha256(raw).hexdigest();b64=base64.b64encode(raw).decode()
wb=openpyxl.Workbook();ws=wb.active;ws.title='Как пользоваться';ws.column_dimensions['A'].width=150
code="import base64,io,zipfile,openpyxl\nfrom pathlib import Path\nsource=Path('Генератор_обложек_WB_v18.xlsx')\nwork=Path('work/gen')\nwb=openpyxl.load_workbook(source,read_only=True)\ndata=''.join(r[1] for r in wb['Файлы'].iter_rows(min_row=2,values_only=True) if r[1])\nzipfile.ZipFile(io.BytesIO(base64.b64decode(data))).extractall(work)\n# Read work/gen/README.md before running scripts."
rows=[version,'Распакованные скрипты, шаблон и шрифты. Действующие правила — в README.md и stage/assorti_rules.md.','Фото Самсона: последовательная загрузка, пауза >=2 секунд, общий кэш и остановка при 429.','Состав: '+', '.join(str(p.relative_to(root)) for p in files),'Контрольная сумма ZIP (SHA256): '+sha,'Код распаковки:',code]
for i,t in enumerate(rows,1):
 c=ws.cell(i,1,t);c.font=Font(name='Courier New' if i==7 else 'Arial',bold=i==1);c.alignment=Alignment(wrap_text=True,vertical='top')
w2=wb.create_sheet('Файлы');w2.append(['Часть','Данные (base64 zip-архива)']);w2.column_dimensions['B'].width=60
for i in range(0,len(b64),30000):w2.append([str(i//30000+1),b64[i:i+30000]])
out.parent.mkdir(parents=True,exist_ok=True);wb.save(out)
w=openpyxl.load_workbook(out,read_only=True);data=''.join(r[1] for r in w['Файлы'].iter_rows(min_row=2,values_only=True) if r[1]);check=base64.b64decode(data)
assert hashlib.sha256(check).hexdigest()==sha and zipfile.ZipFile(io.BytesIO(check)).testzip() is None
print(len(files),'files;',round(out.stat().st_size/1024),'KB;',sha)
