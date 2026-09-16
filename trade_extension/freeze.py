from pathlib import Path
import hashlib,json
R=Path(__file__).resolve().parents[1];H=R/'trade_extension'
p=H/'previous_hashes.json'
if p.exists():
    old=json.loads(p.read_text());bad=[x for x,h in old.items() if not (R/x).exists() or hashlib.sha256((R/x).read_bytes()).hexdigest()!=h]
    assert not bad,bad;print('Previous files preserved:',len(old))
else:
    files=[x for folder in ['src','data','report','secondary','third','output','tests'] for x in (R/folder).rglob('*') if x.is_file() and '__pycache__' not in x.parts]
    files += [x for x in R.iterdir() if x.is_file()]
    p.write_text(json.dumps({str(x.relative_to(R)):hashlib.sha256(x.read_bytes()).hexdigest() for x in files},indent=2));print('Frozen',len(files))
