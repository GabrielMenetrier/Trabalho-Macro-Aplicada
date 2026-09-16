from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
import run as r
import numpy as np,pandas as pd
import statsmodels.api as sm
checks=[]
def check(k,v):checks.append(dict(check=k,passed=bool(v)));assert v,k
x,_,_=r.inputs();t=r.dates.get_loc('2015-06');h=60;cut=t-h
y=r.S[h:cut+h]-r.S[:cut]
for m,cols in r.MODELS.items():
    aa=np.stack([x[k][:cut]-x[k][:t+1].mean(axis=0) for k in cols],axis=2).reshape(-1,len(cols))
    bb=np.stack([x[k][t]-x[k][:t+1].mean(axis=0) for k in cols],axis=1)
    pp=sm.OLS(y.ravel(),aa,hasconst=False).fit().predict(bb)
    stored=pd.read_csv(r.H/'tables/predictions.csv.gz')
    row=stored[(stored.h==h)&(stored.origin=='2015-06')].set_index('country').reindex(r.CC)
    check('Independent statsmodels regression '+m,np.allclose(pp,row[m],atol=1e-10))
changed=r.TOT.copy();changed.loc[changed.index>=2014]+=999
cl,cd,_=r.annual_known(changed)
check('Future annual revisions do not enter old origin',np.allclose(cl[t],x['TOT_l'][t]) and np.allclose(cd[t],x['TOT_d'][t]))
rebased=r.TOT+np.arange(6)*20
rl,rd,_=r.annual_known(rebased)
check('Arbitrary country base index cancels',np.allclose(rl[t]-rl[:t+1].mean(axis=0),x['TOT_l'][t]-x['TOT_l'][:t+1].mean(axis=0)) and np.allclose(rd[t],x['TOT_d'][t]))
altered=r.REAL.copy();altered.loc[altered.index>=r.dates[t]-1]+=888
check('Future commodity information blocked',np.allclose(altered.shift(2).reindex(r.dates).iloc[t].to_numpy()@r.W.T,x['COM_l'][t]))
check('Export/import baskets have positive shares',((r.weight('export_share')>=0)&(r.weight('import_share')>=0)).all())
check('Commodity shares leave nonnegative noncommodity residual',(r.weight('export_share').sum(axis=1)<=1).all() and (r.weight('import_share').sum(axis=1)<=1).all())
for k,a in r.A.items():check('Observed raw indicator positive in usable history, 1994 onward '+k,(a.loc[1994:].stack().dropna()>0).all())
pd.DataFrame(checks).to_csv(r.H/'tables/extra_validation.csv',index=False)
print(len(checks),'extra checks passed')
