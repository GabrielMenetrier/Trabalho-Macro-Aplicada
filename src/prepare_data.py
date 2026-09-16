"""Source selection and monthly alignment. Never interpolate or backfill prices."""
from pathlib import Path
import csv, zipfile, io, re, html, json
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
RAW=ROOT/'data/raw'; OUT=ROOT/'data/processed'
MAP={'BR':'BRL','XM':'EUR','JP':'JPY','GB':'GBP','CA':'CAD','SE':'SEK','US':'USD'}

def bis(kind, **selection):
    z=zipfile.ZipFile(RAW/f'bis_{kind}.zip')
    result={}; meta=[]
    for row in csv.DictReader(io.TextIOWrapper(z.open(z.namelist()[0]),encoding='utf-8-sig')):
        if row['FREQ']!='M' or row['REF_AREA'] not in MAP: continue
        if any(row[k]!=v for k,v in selection.items()): continue
        code=MAP[row['REF_AREA']]
        assert code not in result, (kind,code,'duplicate series')
        vals={pd.Period(k,freq='M'):float(v) for k,v in row.items() if re.fullmatch(r'\d{4}-\d{2}',k) and v!=''}
        result[code]=pd.Series(vals,dtype=float)
        meta.append({k:v for k,v in row.items() if not re.match(r'^\d{4}',k)})
    (OUT/f'metadata_{kind}_{selection.get("COLLECTION","")}.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2),encoding='utf-8')
    return pd.DataFrame(result).sort_index()

def cells(row):
    row=re.sub(r'<sup\b.*?</sup>','',row,flags=re.S|re.I)
    return [html.unescape(re.sub('<[^>]+>','',v)).strip() for v in re.findall(r'<t[dh]\b[^>]*>(.*?)</t[dh]>',row,re.S|re.I)]

def boj():
    rows=re.findall(r'<tr\b.*?</tr>',(RAW/'boj_call.html').read_text(encoding='utf-8',errors='replace'),re.S|re.I)
    vals={}
    for row in rows:
        c=cells(row)
        if len(c)==3 and re.fullmatch(r'\d{4}/\d{2}',c[0]):
            vals[pd.Period(c[0].replace('/','-'),freq='M')]=float(c[1])
    assert len(vals)>400
    return pd.Series(vals).sort_index()

def ecb(index):
    rows=re.findall(r'<tr\b.*?</tr>',(RAW/'ecb_rates.html').read_text(encoding='utf-8'),re.S|re.I)
    year=None; vals={}
    months={m:i for i,m in enumerate(['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'],1)}
    for row in rows:
        c=cells(row)
        if len(c)!=6: continue
        if re.fullmatch(r'\d{4}',c[0]): year=int(c[0])
        m=re.match(r'(\d+)\s+([A-Za-z]{3})',c[1])
        if year is None or m is None: continue
        d=pd.Timestamp(year,months[m[2]],int(m[1]))
        vals[d]=float(c[2].replace('\u2212','-'))
    s=pd.Series(vals).sort_index()
    assert len(s)>50
    # As-of matching of effective dated step function, no future effective rates.
    return s.reindex(index.to_timestamp('M'),method='ffill').set_axis(index)

def sgs(n):
    a=pd.DataFrame(json.loads((RAW/f'sgs_{n}.json').read_text()))
    return pd.Series(pd.to_numeric(a.valor).values,index=pd.to_datetime(a.data,dayfirst=True).dt.to_period('M')).sort_index()

def main():
    OUT.mkdir(exist_ok=True,parents=True)
    idx=pd.period_range('1994-01','2026-08',freq='M')
    fx=bis('fx',COLLECTION='E').reindex(idx)
    fxmean=bis('fx',COLLECTION='A').reindex(idx)
    cpi=bis('cpi',UNIT_MEASURE='628').reindex(idx)
    policy=bis('policy').reindex(idx)
    rates=policy.copy(); rates['JPY']=boj().reindex(idx); rates['EUR']=ecb(idx)
    for name,df in [('fx',fx),('fxmean',fxmean),('cpi',cpi),('rates',rates),('policy',policy)]:
        df.index.name='month'; df.to_csv(OUT/f'{name}.csv')
    cpi_br=(1+sgs(433)/100).cumprod()
    check=pd.concat([cpi_br.pct_change().rename('SGS'),cpi.BRL.pct_change().rename('BIS')],axis=1).dropna()
    report={'start':'1999-10','end_fx':'2026-08','end_cpi':str(cpi.dropna().index[-1]),
            'ipca_monthly_max_abs_difference':float((check.SGS-check.BIS).abs().max()),
            'rates_missing_after_1999_10':rates.loc['1999-10':].isna().sum().to_dict(),
            'fx_missing_after_1999_10':fx.loc['1999-10':].isna().sum().to_dict(),
            'cpi_missing_through_2026_07':cpi.loc['1999-10':'2026-07'].isna().sum().to_dict()}
    us=[]
    for p in RAW.glob('bls_cpi_sa_*.json'):
        raw=json.loads(p.read_text());
        if raw.get('status')!='REQUEST_SUCCEEDED': continue
        for s in raw['Results']['series']:
            for v in s['data']:
                if v['period']!='M13' and v['value']!='-': us.append((pd.Period(v['year']+'-'+v['period'][1:],freq='M'),float(v['value'])))
    classroom=pd.concat([sgs(3698).rename('S'),cpi_br.rename('P_BR'),cpi.USD.rename('P_US_NSA')],axis=1)
    if us: classroom['P_US_SA']=pd.Series(dict(us))
    classroom.index.name='month'; classroom.to_csv(OUT/'classroom.csv')
    etfs={}
    for ticker in ['BIL','SPY']:
        path=RAW/f'yahoo_{ticker}.json'
        if not path.exists(): continue
        j=json.loads(path.read_text())['chart']['result'][0]
        daily=pd.Series(j['indicators']['adjclose'][0]['adjclose'],index=pd.to_datetime(j['timestamp'],unit='s',utc=True).tz_convert('America/New_York').tz_localize(None))
        # Adjusted close includes distribution/split adjustments; NEVER used as a predictor.
        daily=daily.dropna(); monthly=daily.groupby(daily.index.to_period('M')).last()
        etfs[ticker]=monthly.reindex(idx)
    pd.DataFrame(etfs).to_csv(OUT/'etf_adjusted_close.csv',index_label='month')
    (OUT/'quality.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    print(json.dumps(report,indent=2))

if __name__=='__main__': main()
