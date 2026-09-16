from pathlib import Path
import sys,json,hashlib
import numpy as np,pandas as pd
R=Path(__file__).resolve().parents[1];H=R/'third';sys.path.insert(0,str(H))
import analyze as a
from prepare import read_xlsx
checks=[]
def check(name,ok,detail=''):
    assert bool(ok),name;checks.append(dict(check=name,status='PASS',detail=detail))
X=np.stack([a.q,np.repeat(a.globallev[:,None],a.C,axis=1)],axis=2);h=12;Y=a.target_fx(h);cut=240
base,_=a.ejr_extension(a.q[:,:,None],Y,h,start=a.START);original=a.forecast(a.s,a.q,h)[0]['ejr']
mask=np.isfinite(base)&np.isfinite(original);check('Nested EJR reproduces original restriction',np.allclose(base[mask],original[mask],atol=1e-12))
for mode in ['regular','interaction','equilibrium','pca']:
    if mode=='interaction':
        full,_=a.ejr_extension(X,Y,h,start=a.START,interaction=True);prefix,_=a.ejr_extension(X[:cut],Y[:cut],h,start=a.START,interaction=True)
    elif mode=='pca':
        xx=a.qd;yy=a.target_price('oil',h,'nominal')[0]
        full,_=a.oos(xx,yy,h,release=1,mode='pca',start=a.START);prefix,_=a.oos(xx[:cut],yy[:cut],h,release=1,mode='pca',start=a.START)
    else:
        md='equilibrium' if mode=='equilibrium' else None
        full,_=a.oos(X,Y,h,mode=md,start=a.START);prefix,_=a.oos(X[:cut],Y[:cut],h,mode=md,start=a.START)
    check('Prefix invariance: '+mode,np.allclose(full[:cut],prefix,equal_nan=True,atol=1e-12))
altered=Y.copy();altered[cut-h:]=999
f,_=a.oos(X,Y,h,start=a.START);g,_=a.oos(X,altered,h,start=a.START)
check('Future labels do not alter earlier predictions',np.allclose(f[:cut],g[:cut],equal_nan=True,atol=1e-12))
bad=X.copy();bad[cut:]+=999;g,_=a.oos(bad,Y,h,start=a.START)
check('Future predictors do not alter earlier predictions',np.allclose(f[:cut],g[:cut],equal_nan=True,atol=1e-12))
check('Real FX identity',np.allclose(a.qd,a.sd+a.reld,atol=1e-12))
check('Complete commodity panel',a.P.loc[a.dates].notna().all().all())
check('Strictly positive commodity levels',(a.P.loc[a.dates]>0).all().all())
check('Unique monthly commodity dates',a.P.index.is_unique)
w=pd.read_csv(H/'data/trade_weights.csv');check('Trade weights precede training',w.last_year.max()==1996)
check('Three historical years per trade cell',(w.n_years==3).all())
construct=json.loads((H/'data/construction.json').read_text());check('No future-weighted official WB indices',not construct['official_WB_indices_used'])
for item in json.loads((H/'data/manifest.json').read_text()):
    if 'error' in item:continue
    check('Source hash '+item['file'],hashlib.sha256((H/'data/raw'/item['file']).read_bytes()).hexdigest()==item['sha256'])
au=pd.read_csv(H/'tables/audit.csv');origin=pd.PeriodIndex(au.origin,freq='M');available=pd.PeriodIndex(au.last_label_available,freq='M')
check('All train labels available before origin',(available<origin).all(),str(len(au))+' fits')
check('At least 60 training dates',(au.n_train_dates>=60).all())
obs=pd.read_csv(H/'tables/predictions.csv.gz');check('Unique prediction keys',not obs.duplicated(['task','model','origin','unit']).any())
known=a.knownnom['oil'];own=np.c_[a.dev(known.to_numpy()[:,None])[:,0],a.logP.diff(12).shift(1).reindex(a.dates)['oil'],a.logP.diff(3).shift(1).reindex(a.dates)['oil']]
yy,_=a.target_price('oil',12,'nominal');pp,_=a.oos(np.c_[own,a.mom[:,0]],yy,12,release=1,start=a.START)
saved=obs[(obs.task=='A_oil_nominal_12')&(obs.model=='DS_BRL')].set_index('origin').pred
recomputed=pd.Series(pp[:,0],index=a.dates.astype(str)).reindex(saved.index)
check('Saved nominal-change model reproduces from full training history',np.allclose(saved,recomputed,atol=1e-9))
check('Finite evaluated predictions',np.isfinite(obs[['actual','pred']]).all().all())
check('Commodities not duplicated across countries',not obs[obs.block=='A'].duplicated(['task','model','origin']).any())
mm=pd.read_csv(H/'tables/metrics.csv');check('No false precision in long-horizon p-values',mm.loc[mm.n_dates<3*(mm.h+2),'p'].isna().all())
check('Holm correction never lowers p-value',(mm.dropna(subset=['p','p_holm']).p_holm+1e-12>=mm.dropna(subset=['p','p_holm']).p).all())
old=json.loads((H/'previous_hashes.json').read_text());check('Two earlier studies unchanged',all(hashlib.sha256((R/p).read_bytes()).hexdigest()==v for p,v in old.items()),str(len(old))+' files')
# Workbook's diagnostic sheet reports one discrepancy in a selected series.
# The selected Monthly Prices value matches the September 2026 official PDF, page 1.
check('Soy July 2026 matches official Pink Sheet PDF',a.P.loc['2026-07','soy']==478.,'World Bank September 2026, page 1, Soybeans July=478 USD/mt')
source=read_xlsx(H/'data/raw/pink_sheet.xlsx');monthly=source['Monthly Prices'];idx=monthly[0].astype(str).str.fullmatch(r'\d{4}M\d{2}')
check('All source monthly rows have unique dates',monthly.loc[idx,0].is_unique)
pd.DataFrame(checks).to_csv(H/'tables/validation.csv',index=False)
print(str(len(checks))+' integrity checks passed.')
