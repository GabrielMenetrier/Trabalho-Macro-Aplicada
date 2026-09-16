from pathlib import Path
import zipfile,json,hashlib
R=Path(__file__).resolve().parents[1];H=R/'synthesis'
files=[p for p in H.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix!='.pyc']
extra=['output/pdf/relatorio_sintese.pdf','src/models.py','third/engine.py','data/processed/fx.csv','data/processed/cpi.csv','data/processed/rates.csv','data/processed/etf_adjusted_close.csv','secondary/cache/core.npz','third/data/sector_logprices.csv','third/data/trade_weights.csv','third/tables/predictions.csv.gz','trade_extension/cache/trade.npz','trade_extension/cache/predictions.npz','requirements-lock.txt']
files +=[R/f for f in extra]
files +=[R/'output/tables/classroom_replication.csv',R/'output/tables/forecast_accuracy.csv']
manifest={str(f.relative_to(R)):hashlib.sha256(f.read_bytes()).hexdigest() for f in files}
p=R/'entrega_sintese_economica.zip'
with zipfile.ZipFile(p,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
    for f in files:z.write(f,f.relative_to(R).as_posix())
    z.writestr('synthesis/package_manifest.json',json.dumps(manifest,indent=2))
with zipfile.ZipFile(p) as z:assert z.testzip() is None
print('Verified package:',len(files)+1,'files;',round(p.stat().st_size/1024/1024,2),'MiB')
