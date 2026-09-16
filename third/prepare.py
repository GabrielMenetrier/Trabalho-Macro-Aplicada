"""Read the public XLSX without modifying it; assemble fixed pre-sample trade weights."""
from pathlib import Path
import zipfile,xml.etree.ElementTree as ET,re,json
import numpy as np
import pandas as pd
H=Path(__file__).resolve().parent;D=H/'data';(H/'tables').mkdir(exist_ok=True)
NS={'m':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
def read_xlsx(path):
    out={}
    with zipfile.ZipFile(path) as z:
        strings=[]
        if 'xl/sharedStrings.xml' in z.namelist():
            strings=[''.join(x.itertext()) for x in ET.fromstring(z.read('xl/sharedStrings.xml'))]
        rels={x.attrib['Id']:x.attrib['Target'] for x in ET.fromstring(z.read('xl/_rels/workbook.xml.rels'))}
        for sh in ET.fromstring(z.read('xl/workbook.xml')).find('m:sheets',NS):
            ref=sh.attrib['{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id'];target=rels[ref]
            path=target.lstrip('/') if target.startswith('/') else 'xl/'+target
            rows=[]
            for row in ET.fromstring(z.read(path)).findall('.//m:sheetData/m:row',NS):
                vals={}
                for c in row:
                    letters=re.match(r'[A-Z]+',c.attrib['r']).group();idx=0
                    for letter in letters:idx=idx*26+ord(letter)-64
                    v=c.find('m:v',NS);text=v.text if v is not None else None
                    if c.attrib.get('t')=='s' and text is not None:text=strings[int(text)]
                    elif c.attrib.get('t')=='inlineStr':text=''.join(c.find('m:is',NS).itertext())
                    elif text is not None:
                        try:text=float(text)
                        except ValueError:pass
                    vals[idx-1]=text
                rows.append(vals)
            out[sh.attrib['name']]=pd.DataFrame(rows)
    return out

if __name__=='__main__':
    sheets=read_xlsx(D/'raw/pink_sheet.xlsx')
    a=sheets['Monthly Prices'];head=a.iloc[4]
    selected={'oil':'Crude oil, average','gas':'Natural gas, US','copper':'Copper','iron':'Iron ore, cfr spot','soy':'Soybeans','corn':'Maize','wheat':'Wheat, US HRW','gold':'Gold','cotton':'Cotton, A Index','rubber':'Rubber, RSS3','aluminum':'Aluminum','nickel':'Nickel'}
    m=a[0].astype(str).str.fullmatch(r'\d{4}M\d{2}');a=a[m]
    idx=pd.PeriodIndex(a[0].str.replace('M','-'),freq='M');prices={};desc=[]
    for code,label in selected.items():
        col=head[head==label].index[0];prices[code]=pd.to_numeric(a[col],errors='coerce').to_numpy()
        desc.append(dict(code=code,label=label,unit=sheets['Monthly Prices'].iloc[5,col]))
    prices=pd.DataFrame(prices,index=idx).loc['1994-01':'2026-08'];prices.index.name='month'
    assert prices.index.is_unique and (prices.dropna()>0).all().all()
    prices.to_csv(D/'commodities.csv');pd.DataFrame(desc).to_csv(D/'commodity_metadata.csv',index=False)
    # Do not use WB official index weights (based on 2002-04 trade) for 1999 training.
    sectors={'energy':['oil','gas'],'food':['soy','corn','wheat'],'raw':['cotton','rubber'],'metals':['copper','iron','aluminum','nickel']}
    logs=np.log(prices);basket=pd.DataFrame({k:logs[v].mean(axis=1,skipna=False) for k,v in sectors.items()})
    basket.to_csv(D/'sector_logprices.csv')
    iso={'BRL':'BRA','CAD':'CAN','EUR':'DEU','GBP':'GBR','JPY':'JPN','SEK':'SWE'}
    group={'energy':'FUEL','food':'FOOD','raw':'AGRI','metals':'MMTL'};raw={};inputrows=[]
    for file in (D/'raw').glob('*.json'):
        payload=json.loads(file.read_text(encoding='utf8'))
        for ob in payload[1]:
            key=(ob['countryiso3code'],int(ob['date']),file.stem);raw[key]=ob['value']
            inputrows.append(dict(iso=key[0],year=key[1],indicator=key[2],value=ob['value']))
    rows=[];weights={}
    for currency,country in iso.items():
        weights[currency]={}
        for sec,g in group.items():
            annual=[];xs=[];ms=[]
            for year in [1994,1995,1996]:
                x=raw[country,year,'TX.VAL.MRCH.CD.WT'];m=raw[country,year,'TM.VAL.MRCH.CD.WT'];sx=raw[country,year,f'TX.VAL.{g}.ZS.UN'];sm=raw[country,year,f'TM.VAL.{g}.ZS.UN']
                if None in [x,m,sx,sm]:continue
                annual.append((x*sx/100-m*sm/100)/(x+m));xs.append(sx/100);ms.append(sm/100)
            assert len(annual)>=2,(currency,sec,annual)
            weights[currency][sec]=float(np.mean(annual))
            rows.append(dict(currency=currency,proxy_country=country,sector=sec,n_years=len(annual),first_year=1994,last_year=1996,net_weight=np.mean(annual),export_share=np.mean(xs),import_share=np.mean(ms)))
    pd.DataFrame(rows).to_csv(D/'trade_weights.csv',index=False)
    pd.DataFrame(inputrows).to_csv(D/'trade_inputs.csv',index=False)
    trade=pd.DataFrame({c:sum(w[sec]*basket[sec] for sec in sectors) for c,w in weights.items()})
    trade.to_csv(D/'trade_logindex.csv',index_label='month')
    (D/'construction.json').write_text(json.dumps(dict(sectors=sectors,weights=weights,EUR_proxy='Germany',base_trade_years=[1994,1995,1996],official_WB_indices_used=False),indent=2),encoding='utf8')
    print('Prices:',prices.shape,prices.index.min(),prices.index.max(),'Missing:',int(prices.isna().sum().sum()))
    print(pd.DataFrame(weights).T.to_string())
