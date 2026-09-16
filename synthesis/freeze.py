from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parents[1];H=R/'synthesis';p=H/'previous_hashes.json'
if p.exists():
    old=json.loads(p.read_text());bad=[f for f,h in old.items() if not (R/f).is_file() or hashlib.sha256((R/f).read_bytes()).hexdigest()!=h];assert not bad,bad;print('Previous files preserved:',len(old))
else:
    files=[p for folder in ['src','data','report','output','secondary','third','trade_extension','tests'] for p in (R/folder).rglob('*') if p.is_file() and '__pycache__' not in p.parts]
    files += [p for p in R.iterdir() if p.is_file()]
    p.write_text(json.dumps({str(f.relative_to(R)):hashlib.sha256(f.read_bytes()).hexdigest() for f in files},indent=2));print('Frozen',len(files))
