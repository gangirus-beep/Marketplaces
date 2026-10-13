import sys,pathlib,zipfile,json
start,end=map(int,sys.argv[1:3])
source=pathlib.Path('render.py').read_text()
source=source.replace("goods=json.load(open('goods.json'))",f"goods=json.load(open('goods.json'))[{start}:{end}]")
source=source.replace("only=set(sys.argv[1:])","only=set()")
source=source.replace("open('coverlog.json','w')",f"open('coverlog_{start:03d}_{end:03d}.json','w')")
exec(compile(source,'render.py','exec'))
log=json.load(open(f'coverlog_{start:03d}_{end:03d}.json'))
assert not any(x['overflow'] or x['subw']>788 for x in log)
with zipfile.ZipFile(f'checkpoints/Stage2_covers_{start:03d}_{end:03d}.zip','w',zipfile.ZIP_STORED) as z:
    for l in log:z.write('out/covers/'+l['file'],'обложки/'+l['file'])
    z.write(f'coverlog_{start:03d}_{end:03d}.json')
print('CHECKPOINT',start,end,len(log),flush=True)
