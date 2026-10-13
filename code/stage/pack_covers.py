# Архив перевыпуска: только папка «обложки» (последние фото остаются из прежнего архива этапа), без сжатия
import zipfile, os, texts
dst='/mnt/user-data/outputs/'+texts.REARCH
with zipfile.ZipFile(dst,'w',zipfile.ZIP_STORED) as z:
    for f in sorted(os.listdir('out/covers')): z.write(f'out/covers/{f}',f'обложки/{f}')
z=zipfile.ZipFile(dst); print(len(z.namelist()),'файлов',round(os.path.getsize(dst)/1e6,1),'МБ',z.testzip())
