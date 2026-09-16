from pathlib import Path
import requests, json, hashlib, time
import pandas as pd

ROOT=Path(__file__).resolve().parent
(ROOT/'data/raw').mkdir(parents=True,exist_ok=True)
tickers=['IMAB11.SA','VALE3.SA','ITUB4.SA','SUZB3.SA','BBAS3.SA','BOVA11.SA']
series={}; manifest=[]
for ticker in tickers:
    url=f'https://query2.finance.yahoo.com/v8/finance/chart/{ticker}?period1=1167609600&period2=1788220800&interval=1d&events=div%2Csplits'
    path=ROOT/'data/raw'/f'{ticker}.json'
    if not path.exists():
        res=requests.get(url,headers={'User-Agent':'Mozilla/5.0'},timeout=60)
        res.raise_for_status(); path.write_bytes(res.content)
        time.sleep(.5)
    payload=json.loads(path.read_text(encoding='utf8')); obj=payload['chart']['result'][0]
    dates=pd.to_datetime(obj['timestamp'],unit='s',utc=True).tz_convert('America/Sao_Paulo').tz_localize(None).to_period('M')
    a=pd.Series(obj['indicators']['adjclose'][0]['adjclose'],index=dates).dropna().groupby(level=0).last()
    a=a.loc[:'2026-08']; series[ticker]=a
    manifest.append(dict(ticker=ticker,url=url,sha256=hashlib.sha256(path.read_bytes()).hexdigest(),first=str(a.index.min()),last=str(a.index.max()),n=len(a)))
pd.DataFrame(series).sort_index().to_csv(ROOT/'data/assets.csv',index_label='month')
(ROOT/'data/manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf8')
print(pd.DataFrame(manifest)[['ticker','first','last','n']].to_string(index=False))
