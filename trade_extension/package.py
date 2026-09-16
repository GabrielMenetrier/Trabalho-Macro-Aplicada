from pathlib import Path
import zipfile
R=Path(__file__).resolve().parents[1];H=R/'trade_extension'
files=[p for p in H.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix!='.pyc']
files.append(R/'output/pdf/relatorio_termos_troca.pdf')
p=R/'entrega_termos_troca_risco.zip'
with zipfile.ZipFile(p,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
    for f in files:z.write(f,f.relative_to(R).as_posix())
with zipfile.ZipFile(p) as z:assert z.testzip() is None
print('Verified package',len(files),'files',round(p.stat().st_size/1024/1024,2),'MiB')
