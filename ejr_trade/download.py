from pathlib import Path
import requests,json,hashlib,datetime
from concurrent.futures import ThreadPoolExecutor
D=Path(__file__).resolve().parent/'data'
INDS=['TT.PRI.MRCH.XD.WD','NE.EXP.GNFS.CN','NE.EXP.GNFS.KN','NE.IMP.GNFS.CN','NE.IMP.GNFS.KN']
def fetch(ind):
    url=f'https://api.worldbank.org/v2/country/BRA;CAN;JPN;GBR;SWE;DEU/indicator/{ind}?format=json&date=1960:2025&per_page=5000'
    r=requests.get(url,timeout=40);r.raise_for_status();a=r.json()
    assert len(a)==2 and isinstance(a[1],list),(ind,a)
    path=D/(ind+'.json');path.write_bytes(r.content)
    coverage={c:[min([int(x['date']) for x in a[1] if x['countryiso3code']==c and x['value'] is not None],default=None),max([int(x['date']) for x in a[1] if x['countryiso3code']==c and x['value'] is not None],default=None)] for c in ['BRA','CAN','DEU','GBR','JPN','SWE']}
    return dict(indicator=ind,url=url,sha256=hashlib.sha256(r.content).hexdigest(),downloaded=datetime.datetime.now(datetime.timezone.utc).isoformat(),coverage=coverage)
if __name__=='__main__':
    with ThreadPoolExecutor(max_workers=4) as pool: a=list(pool.map(fetch,INDS))
    (D/'manifest.json').write_text(json.dumps(a,indent=2),encoding='utf-8')
    print(json.dumps(a,indent=2))
