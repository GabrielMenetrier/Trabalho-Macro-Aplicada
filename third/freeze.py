from pathlib import Path
import hashlib,json
R=Path(__file__).resolve().parents[1];H=R/'third';H.mkdir(exist_ok=True)
paths=[]
for folder in ['src','data','report','output','secondary','tests']:
    paths.extend(p for p in (R/folder).rglob('*') if p.is_file() and '__pycache__' not in p.parts and 'relatorio_terciario' not in p.name)
paths.extend(p for p in R.iterdir() if p.is_file())
result={p.relative_to(R).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
target=H/'previous_hashes.json'
if target.exists():
    old=json.loads(target.read_text());changed=[p for p,h in old.items() if result.get(p)!=h]
    assert not changed,changed;print('Previous files preserved:',len(old))
else:target.write_text(json.dumps(result,indent=2));print('Previous files frozen:',len(result))
