from pathlib import Path
import hashlib,json
R=Path(__file__).resolve().parents[1]
paths=[]
for folder in ['src','data','report','output']:
    paths.extend(p for p in (R/folder).rglob('*') if p.is_file() and '__pycache__' not in str(p) and 'relatorio_secundario' not in p.name)
for name in ['README.md','AUDITORIA.md','ROTEIRO_APRESENTACAO.md','entrega_macro_cambio.zip']:
    paths.append(R/name)
result={p.relative_to(R).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
target=R/'secondary/original_hashes.json'
if target.exists():
    old=json.loads(target.read_text()); changed=[p for p,h in old.items() if result.get(p)!=h]
    assert not changed,changed
    print(f'Preservação confirmada: {len(old)} arquivos originais idênticos.')
else:
    target.write_text(json.dumps(result,indent=2)); print(f'Congelados {len(result)} hashes originais.')
