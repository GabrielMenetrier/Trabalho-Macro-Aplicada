from pathlib import Path
import zipfile,json,hashlib
R=Path(__file__).resolve().parents[1];H=R/'third'
files=[p for p in H.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix!='.pyc']
files.append(R/'output/pdf/relatorio_terciario.pdf')
dest=R/'entrega_terciaria_commodities.zip'
with zipfile.ZipFile(dest,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
    for p in files:z.write(p,p.relative_to(R).as_posix())
with zipfile.ZipFile(dest) as z:assert z.testzip() is None
print('Verified ZIP:',len(files),'files;',round(dest.stat().st_size/1024/1024,2),'MiB')
