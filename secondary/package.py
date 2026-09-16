from pathlib import Path
import zipfile,json,hashlib
R=Path(__file__).resolve().parents[1];H=R/'secondary'
out=R/'entrega_secundaria_cambio.zip'
files=[p for p in H.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix not in ['.pyc']]
files += [R/'output/pdf/relatorio_secundario.pdf']
with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
    for p in files:z.write(p,p.relative_to(R).as_posix())
with zipfile.ZipFile(out) as z:
    assert z.testzip() is None
    assert 'output/pdf/relatorio_secundario.pdf' in z.namelist()
print(f'Pacote secundario: {len(files)} arquivos, {out.stat().st_size/1024/1024:.2f} MiB. ZIP verificado.')
