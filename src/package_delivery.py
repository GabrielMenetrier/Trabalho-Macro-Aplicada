"""Package only deliverables, not portable runtimes, scratch files or course PDFs."""
from pathlib import Path
import zipfile, json, hashlib
ROOT=Path(__file__).resolve().parents[1]
members=[]
for folder in ['src','tests','data','report','output/figures','output/tables','output/pdf']:
    members.extend(p for p in (ROOT/folder).rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix not in ['.pyc','.log','.aux','.out'])
members.extend(ROOT/p for p in ['README.md','AUDITORIA.md','ROTEIRO_APRESENTACAO.md','requirements-lock.txt','run.ps1','main.tex'])
members=sorted(set(members))
dest=ROOT/'entrega_macro_cambio.zip'
with zipfile.ZipFile(dest,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
    for p in members:z.write(p,p.relative_to(ROOT).as_posix())
with zipfile.ZipFile(dest) as z:
    assert z.testzip() is None
    names=z.namelist()
    assert 'output/pdf/relatorio.pdf' in names and 'report/relatorio.tex' in names
    assert not any(n.startswith(('tools/','tmp/')) for n in names)
print(json.dumps({'file':dest.name,'files':len(members),'bytes':dest.stat().st_size,
                  'sha256':hashlib.sha256(dest.read_bytes()).hexdigest()},indent=2))
