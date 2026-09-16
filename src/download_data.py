"""Download immutable public source snapshots; no keys or credentials required."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import hashlib, json, time, urllib.request, datetime
import requests

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / 'data/raw'
URLS = {
    'boj_call.html': 'https://www.stat-search.boj.or.jp/ssi/mtshtml/fm02_m_1_en.html',
    'ecb_rates.html': 'https://www.ecb.europa.eu/stats/policy_and_exchange_rates/key_ecb_interest_rates/html/index.en.html',
    'bis_cpi.zip': 'https://data.bis.org/static/bulk/WS_LONG_CPI_csv_col.zip',
    'bis_policy.zip': 'https://data.bis.org/static/bulk/WS_CBPOL_csv_col.zip',
    'bis_fx.zip': 'https://data.bis.org/static/bulk/WS_XRU_csv_col.zip',
    'bis_cpi_documentation.pdf': 'https://www.bis.org/statistics/cp/cp_long_documentation.pdf',
    'bis_policy_documentation.pdf': 'https://www.bis.org/statistics/cbpol/cbpol_doc.pdf',
    'sgs_433.json': 'https://api.bcb.gov.br/dados/serie/bcdata.sgs.433/dados?formato=json&dataInicial=01/01/1994&dataFinal=31/08/2026',
    'sgs_3698.json': 'https://api.bcb.gov.br/dados/serie/bcdata.sgs.3698/dados?formato=json&dataInicial=01/01/1995&dataFinal=31/08/2026',
}
for begin,end in [(1994,2003),(2004,2013),(2014,2023),(2024,2026)]:
    URLS[f'bls_cpi_sa_{begin}.json']=f'https://api.bls.gov/publicAPI/v2/timeseries/data/CUSR0000SA0?startyear={begin}&endyear={end}'
for ticker in ['BIL','SPY']:
    p1=int(datetime.datetime(2007,1,1,tzinfo=datetime.timezone.utc).timestamp())
    p2=int(datetime.datetime(2026,9,1,tzinfo=datetime.timezone.utc).timestamp())
    URLS[f'yahoo_{ticker}.json']=f'https://query2.finance.yahoo.com/v8/finance/chart/{ticker}?period1={p1}&period2={p2}&interval=1d&events=div%2Csplits'

def fetch(item):
    name,url = item
    p = RAW/name
    if not p.exists():
        for attempt in range(3):
            try:
                r=requests.get(url,timeout=30,headers={'User-Agent':'Mozilla/5.0'})
                r.raise_for_status()
                data=r.content
                if len(data)<20: raise ValueError('Empty response')
                p.write_bytes(data)
                break
            except Exception as e:
                if attempt==2: return {'file':name,'url':url,'error':str(e)}
                time.sleep(2)
    b=p.read_bytes()
    ans={'file':name,'url':url,'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest(),
         'downloaded_utc':datetime.datetime.fromtimestamp(p.stat().st_mtime,datetime.timezone.utc).isoformat()}
    print(name,len(b),flush=True)
    return ans

if __name__=='__main__':
    RAW.mkdir(parents=True,exist_ok=True)
    with ThreadPoolExecutor(max_workers=5) as ex: result=list(ex.map(fetch,URLS.items()))
    (RAW/'manifest.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    errors=[r for r in result if 'error' in r]
    print(json.dumps(errors,indent=2))
    if errors: raise SystemExit(1)
