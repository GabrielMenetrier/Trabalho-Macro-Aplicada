from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import requests,json,hashlib,datetime,time
R=Path(__file__).resolve().parent;D=R/'data/raw';D.mkdir(parents=True,exist_ok=True)
URLS={
 'pink_sheet.xlsx':'https://thedocs.worldbank.org/en/doc/74e8be41ceb20fa0da750cda2f6b9e4e-0050012026/related/CMO-Historical-Data-Monthly.xlsx',
 'chen_rogoff_rossi.pdf':'https://scholar.harvard.edu/sites/scholar.harvard.edu/files/rogoff/files/125-3-1145.pdf',
 'chen_update.pdf':'https://scholar.harvard.edu/files/rogoff/files/crr2014a.pdf',
 'imf_ctot_methodology.pdf':'https://www.imf.org/-/media/files/publications/wp/2019/wp1921.pdf',
}
indicators=['TX.VAL.FUEL.ZS.UN','TM.VAL.FUEL.ZS.UN','TX.VAL.FOOD.ZS.UN','TM.VAL.FOOD.ZS.UN','TX.VAL.AGRI.ZS.UN','TM.VAL.AGRI.ZS.UN','TX.VAL.MMTL.ZS.UN','TM.VAL.MMTL.ZS.UN','TX.VAL.MRCH.CD.WT','TM.VAL.MRCH.CD.WT']
for ind in indicators:
    URLS[ind+'.json']='https://api.worldbank.org/v2/country/BRA;CAN;JPN;GBR;SWE;DEU/indicator/'+ind+'?format=json&date=1994:1996&per_page=1000'
def fetch(item):
    name,url=item;p=D/name
    if not p.exists():
        for attempt in range(3):
            try:
                res=requests.get(url,headers={'User-Agent':'Mozilla/5.0'},timeout=45);res.raise_for_status()
                assert len(res.content)>100
                p.write_bytes(res.content);break
            except Exception as e:
                if attempt==2:return dict(file=name,url=url,error=str(e))
                time.sleep(1)
    content=p.read_bytes();print(name,len(content),flush=True)
    return dict(file=name,url=url,bytes=len(content),sha256=hashlib.sha256(content).hexdigest(),downloaded_utc=datetime.datetime.fromtimestamp(p.stat().st_mtime,datetime.timezone.utc).isoformat())
with ThreadPoolExecutor(max_workers=4) as pool:manifest=list(pool.map(fetch,URLS.items()))
(R/'data/manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf8')
errors=[x for x in manifest if 'error'in x];print('Errors:',json.dumps(errors))
