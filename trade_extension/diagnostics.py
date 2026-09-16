"""Annual terms-of-trade prediction and conditional risk diagnostics."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from core import *
from strategies import hazards
P=dict(np.load(H/'cache/predictions.npz'));years,raw,w,tt=annual_data();annual=[];aud=[]
X=np.stack([tt,tt-np.roll(tt,1,axis=0)],axis=2);X[0]=np.nan
target=np.full_like(tt,np.nan);target[:-3]=tt[3:]-tt[:-3]
for year in range(2013,2027):
    a=int(np.flatnonzero(years<=year-2)[-1]);cut=a-3+1
    valid=np.isfinite(X[:cut]).all(axis=2)&np.isfinite(target[:cut])
    if np.min(valid.sum(axis=0))<8 or not np.isfinite(X[a]).all():continue
    ti,ci=np.where(valid);pr=fit_predict(X[ti,ci],target[ti,ci],X[a],10,ci,np.arange(C),C)
    aud.append(dict(origin_year=year,last_source_year=int(years[a]),last_train_target=int(years[ti.max()+3]),n_years=len(np.unique(ti))))
    if a+3<len(years):
        for c in range(C):annual.append(dict(year=year,country=CC[c],actual=target[a,c],forecast=pr[c],zero=0.,trend=(tt[a,c]-tt[a-1,c])*3))
save(annual,'annual_tot_predictions');save(aud,'annual_tot_audit')
a=pd.DataFrame(annual).dropna();m=[]
for name in ['forecast','zero','trend']:
    m.append(dict(model=name,n_years=a.year.nunique(),n=len(a),first=a.year.min(),last=a.year.max(),ratio=np.sqrt(np.mean((a.actual-a[name])**2)/np.mean(a.actual**2))))
save(m,'annual_tot_metrics')
rows=[]
for hazard,z in hazards.items():
    threshold=quantile_past(z,.8);known=np.isfinite(threshold)&np.isfinite(z)&(dates>=pd.Period('2013-01'))[:,None];high=z>threshold
    for task in ['erased_12','adverse_12','adverse_36','adverse_60','nominal_60']:
        y=P[task+'__actual'].copy()
        if task=='nominal_60':y=(y-P['nominal_60__EJR'])**2
        for state,select in [('high',high),('low',~high)]:
            mask=known&select&np.isfinite(y)
            for country,ix in [('POOL',range(C))]+[(c,[i]) for i,c in enumerate(CC)]:
                mm=mask.copy();mm[:,[i for i in range(C) if i not in ix]]=False
                if mm.any():rows.append(dict(hazard=hazard,task=task,country=country,state=state,n=int(mm.sum()),n_dates=int(mm.any(axis=1).sum()),mean=y[mm].mean()))
save(rows,'conditional_targets')
print('Annual ToT years',a.year.nunique(),'conditional cells',len(rows))
