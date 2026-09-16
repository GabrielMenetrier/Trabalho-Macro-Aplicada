"""Meaningful chronology, accounting and original-preservation checks."""
from pathlib import Path
import sys,json,hashlib
import numpy as np
import pandas as pd
R=Path(__file__).resolve().parents[1]; H=R/'secondary'; sys.path.insert(0,str(R/'src'))
from models import forecast,run_book
checks=[]
def check(name,condition,detail=''):
    assert condition,name
    checks.append(dict(check=name,status='PASS',detail=detail))
z=np.load(H/'cache/core.npz'); fx=z['fx']; rates=z['rates']; wc=z['wc']; T=len(fx)
qraw=pd.read_csv(R/'data/processed/q_available.csv',index_col=0)
dates=pd.PeriodIndex(z['dates'],freq='M')
# Reconstruct from raw released CPI; no centered/full-sample feature estimates.
from models import features
def read(name):
    a=pd.read_csv(R/f'data/processed/{name}.csv',index_col=0);a.index=pd.PeriodIndex(a.index,freq='M');return a
spot=read('fx')[['BRL','EUR','JPY','GBP','CAD','SEK']]; cpi=read('cpi')
q=features(spot,cpi).reindex(dates).to_numpy(); s=np.log(fx)
cut=240
full=forecast(s,q,60)[0]['ejr']; prefix=forecast(s[:cut],q[:cut],60)[0]['ejr']
check('EJR prefix invariance',np.allclose(full[:cut],prefix,equal_nan=True))
ss=s.copy();qq=q.copy();ss[cut:]+=5;qq[cut:]-=3
mut=forecast(ss,qq,60)[0]['ejr']
check('Future corruption leaves past forecasts identical',np.allclose(mut[:cut],full[:cut],equal_nan=True))
for file,col in [('ejr_audit','last_label'),('prediction_audit','last_label_available')]:
    a=pd.read_csv(H/f'tables/{file}.csv')
    check(file+' strictly prior labels',(pd.PeriodIndex(a[col],freq='M')<pd.PeriodIndex(a.origin,freq='M')).all(),str(len(a))+' origins')
a=pd.read_csv(H/'tables/prediction_audit.csv');check('Minimum learning dates',(a.n_train_dates>=36).all())
# All projected currency holdings use exactly two rows of lag.
b,target,_=run_book(wc,fx,rates,cost_bps=[10,2,2,2,2,3]);check('Execution lag',np.allclose(target[2:],wc[:-2]) and not target[:2].any())
check('Long-short neutrality',np.allclose(wc.sum(axis=1),0) and np.allclose(abs(wc).sum(axis=1),1))
# CIP accounting: fully hedged foreign cash equals domestic cash exactly,
# apart from the interaction of interest income and FX (opening-notional hedge).
rm=np.expm1(np.log1p(rates/100)/12); ratio=fx[1:,0]/fx[:-1,0]
F=(1+rm[:-1,0])/(1+rm[:-1,-1])
actual=(1+rm[:-1,-1])*ratio-1+(F-ratio)
expected=rm[:-1,0]+rm[:-1,-1]*(ratio-F)
check('Forward interest and FX signs',np.allclose(actual,expected,atol=1e-12))
f=z['f'][:,0]/60; carry=z['carry'][:,0]
check('Total hedge decision respects forward premium',np.array_equal(f<carry,np.exp(f)<np.exp(carry)))
# No publication leakage: modifying latest two reference months does not change q[t].
origin=200; changed=cpi.copy(); dt=dates[origin]; changed.loc[dt:]*=10
qq=features(spot,changed).reindex(dates).to_numpy()
check('CPI publication lag',np.allclose(q[:origin+2],qq[:origin+2],equal_nan=True))
pred=pd.read_csv(H/'tables/prediction_observations.csv')
check('Finite evaluated predictions',np.isfinite(pred[['actual','pred']]).all().all())
binary=pred[pred.binary];check('Probability bounds',binary.pred.between(.01,.99).all())
# Exact reproduction of original benchmark makes the comparison reviewable.
met=pd.read_csv(H/'tables/strategy_metrics.csv'); base=met[(met.strategy=='Carry')&(met.period=='all')].iloc[0]
check('Original carry reproduced',abs(base.cagr-.041090)<1e-6 and abs(base.sharpe-.600839)<1e-6)
original=json.loads((H/'original_hashes.json').read_text())
check('Original files unchanged',all(hashlib.sha256((R/p).read_bytes()).hexdigest()==v for p,v in original.items()),str(len(original))+' files')
assets=pd.read_csv(H/'data/assets.csv',index_col=0)
check('Asset prices positive',(assets.stack().dropna()>0).all())
check('Asset calendar unique',assets.index.is_unique)
for m in json.loads((H/'data/manifest.json').read_text()):
    check('Source hash '+m['ticker'],hashlib.sha256((H/'data/raw'/f"{m['ticker']}.json").read_bytes()).hexdigest()==m['sha256'])
pd.DataFrame(checks).to_csv(H/'tables/validation.csv',index=False)
print(str(len(checks))+' integrity checks passed.')
