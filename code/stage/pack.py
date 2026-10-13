# Шаг 8. Архив этапа: папки «обложки» и «последние_фото», без сжатия (JPEG не сжимается)
import zipfile, os, texts
dst='/mnt/user-data/outputs/'+texts.ARCH
with zipfile.ZipFile(dst,'w',zipfile.ZIP_STORED) as z:
    for d,a in (('out/covers','обложки'),('out/last','последние_фото')):
        for f in sorted(os.listdir(d)): z.write(f'{d}/{f}',f'{a}/{f}')
z=zipfile.ZipFile(dst); print(len(z.namelist()),'файлов',round(os.path.getsize(dst)/1e6,1),'МБ',z.testzip())
