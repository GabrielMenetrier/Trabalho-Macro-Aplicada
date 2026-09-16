from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import requests,json,hashlib,datetime,time
H=Path(__file__).resolve().parent;D=H/'data/raw';D.mkdir(parents=True,exist_ok=True)
inds=[f'{d}.VAL.{g}.ZS.UN' for d in ['TX','TM'] for g in ['FUEL','FOOD','AGRI','MMTL']]+['TX.VAL.MRCH.CD.WT','TM.VAL.MRCH.CD.WT','TT.PRI.MRCH.XD.WD']
def fetch(ind):
    url=f'https://api.worldbank.org/v2/country/BRA;CAN;JPN;GBR;SWE;DEU/indicator/{ind}?format=json&date=1994:2025&per_page=5000';p=D/(ind+'.json')
    if not p.exists():
        for k in range(3):
            try:
                r=requests.get(url,timeout=60);r.raise_for_status();a=r.json();assert len(a)==2 and isinstance(a[1],list);p.write_bytes(r.content);break
            except Exception:
                if k==2:raise
                time.sleep(1)
    a=p.read_bytes();print(ind,len(a),flush=True)
    return dict(indicator=ind,url=url,file=str(p.relative_to(H)),sha256=hashlib.sha256(a).hexdigest(),downloaded_utc=datetime.datetime.fromtimestamp(p.stat().st_mtime,datetime.timezone.utc).isoformat())
if __name__=='__main__':
    with ThreadPoolExecutor(max_workers=4) as pool:out=list(pool.map(fetch,inds))
    (H/'data/manifest.json').write_text(json.dumps(out,indent=2),encoding='utf8')
