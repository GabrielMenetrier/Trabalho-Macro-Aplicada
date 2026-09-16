"""Read frozen empirical outputs. No estimation, selection, or source-file edits."""
from pathlib import Path
import hashlib,json,sys
import numpy as np
import pandas as pd
R=Path(__file__).resolve().parents[1]; H=R/'presentation'
sys.stdout.reconfigure(encoding='utf-8')
files=['output/tables/classroom_replication.csv','data/processed/classroom.csv',
       'output/tables/forecast_accuracy.csv','output/tables/portfolio_metrics.csv',
       'third/tables/metrics.csv','trade_extension/tables/prediction_metrics.csv',
       'synthesis/tables/metrics.csv','synthesis/tables/returns.csv.gz',
       'synthesis/tables/attribution.csv','synthesis/tables/episodes.csv',
       'synthesis/tables/exposure_controls.csv','synthesis/tables/search_adjustment.csv',
       'synthesis/tables/robustness.csv']
def read(p):return pd.read_csv(R/p)
def records(a):return json.loads(a.to_json(orient='records'))
d={}
a=read(files[0]);d['replication']=records(a[a.spec=='SA_BLS'])
a=pd.read_csv(R/files[1],index_col=0).sort_index().loc['1995-01':'2026-04']
q=np.log(a.S*a.P_US_SA/a.P_BR);q-=q.mean();y=np.log(a.S.shift(-96)/a.S);ok=q.notna()&y.notna()
d['scatter']={'x':q[ok].tolist(),'y':y[ok].tolist(),'first':a.index[ok][0],'last':a.index[ok][-1]}
a=read(files[2]); d['oos']=records(a[(a.h==60)&(a.model=='ejr')&(a.country=='POOL')])[0]
d['initial']=records(read(files[3]))
a=read(files[4]);d['commodity']=records(a[(a.task=='B_FX_60')&(a.model=='REJR_Specific')&(a.country=='POOL')&(a.benchmark=='EJR')])
a=read(files[5]);d['real']=records(a[(a.task=='real_60')&(a.period=='all')&(a.country=='POOL')])
a=read(files[6]);d['best']=records(a[(a.window=='common')&(a.period=='all')])
a=read(files[7]);d['returns']=records(a[(a.window=='common')&a.name.isin(['Carry','Equal_modules','Cash'])])
a=read(files[8]);d['attribution']=records(a[(a.window=='common')&a.name.isin(['Carry','Equal_modules'])])
a=read(files[9]);d['episodes']=records(a[a.name=='Equal_modules'])
a=read(files[10]);d['controls']=records(a[a.name=='Equal_modules'])
a=read(files[11]);d['inference']=records(a[a.name=='Equal_modules'])
d['sources']=[{'path':p,'sha256':hashlib.sha256((R/p).read_bytes()).hexdigest()} for p in files]
(H/'data.json').write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
print('Saved evidence without modifying the original studies.')
print('Initial:',[(x.get('strategy',x.get('name')),x.get('cagr')) for x in d['initial']])
print('Best:',[(x['name'],x['cagr']) for x in d['best'] if x['name'] in ['Carry','Equal_modules']])
print('Scatter:',d['scatter']['first'],d['scatter']['last'],len(d['scatter']['x']))
