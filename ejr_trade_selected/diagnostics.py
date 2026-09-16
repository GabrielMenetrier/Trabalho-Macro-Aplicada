from pathlib import Path
import sys,runpy,json
import pandas as pd,numpy as np
R=Path(__file__).resolve().parents[1];H=R/'ejr_trade_selected'
e=runpy.run_path(str(H/'run.py'),run_name='selected_engine')
sys.stdout.reconfigure(encoding='utf-8')
CC=e['CC'];dates=e['dates'];T=len(dates);S=e['S'];Q=e['Q'];L=e['L'];D=e['D'];fit=e['fit_at']
h=60;MODELS=['EJR','TOT_LOG_LD','COM_DEV_LD'];rows=[];extra=[];checks=[]
def scores(y,p,training,ccs):
    mask=(dates>=pd.Period('2010-01'))&np.isfinite(y).all(axis=1)
    for v in p.values():mask&=np.isfinite(v).all(axis=1)
    rw=(y[mask]**2).mean(axis=0)
    for k,v in p.items():
        mse=((y[mask]-v[mask])**2).mean(axis=0)
        rows.append(dict(training=training,evaluation='+'.join(ccs),model=k,rmse_rw=np.sqrt(mse.mean()/rw.mean()),equal_country_rmse=np.sqrt(np.mean(mse/rw)),n_dates=mask.sum()))
for training,ix in [('panel_3',[0,1,2]),('without_BRL',[1,2])]+[('individual_'+c,[j]) for j,c in enumerate(CC)]:
    y=np.full((T,len(ix)),np.nan);y[:-h]=S[h:,ix]-S[:-h,ix];p={k:np.full_like(y,np.nan) for k in MODELS}
    for t in range(h+61,T):
        pp,_=fit(t,h,S[:,ix],Q[:,ix],{k:v[:,ix] for k,v in L.items()},{k:v[:,ix] for k,v in D.items()})
        for k in p:p[k][t]=pp[k]
    scores(y,p,training,[CC[j] for j in ix])
    if len(ix)==1:
      for t in np.flatnonzero((dates>=pd.Period('2010-01'))&np.isfinite(y).all(axis=1)&np.isfinite(p['EJR']).all(axis=1)):
        extra.append(dict(origin=str(dates[t]),country=CC[ix[0]],actual=y[t,0],**{k:v[t,0] for k,v in p.items()}))
# Six-country estimated coefficients, evaluated on exactly the same three countries.
old=pd.read_csv(R/'ejr_trade/tables/predictions.csv.gz');old=old[(old.h==h)&old.country.isin(CC)]
yy=old.pivot(index='origin',columns='country',values='actual').reindex(columns=CC)
rw=(yy.to_numpy()**2).mean(axis=0)
for k,oldk in [('EJR','EJR'),('TOT_LOG_LD','TOT_both')]:
    pp=old.pivot(index='origin',columns='country',values=oldk).reindex(columns=CC).to_numpy()
    mse=((yy.to_numpy()-pp)**2).mean(axis=0)
    rows.append(dict(training='panel_6',evaluation='+'.join(CC),model=k,rmse_rw=np.sqrt(mse.mean()/rw.mean()),equal_country_rmse=np.sqrt(np.mean(mse/rw)),n_dates=len(yy)))
# Independently reproduce selected model at one forecast origin with statsmodels.
import statsmodels.api as sm
t=dates.get_loc('2015-06');X=e['designs'](t);y=(S[h:t]-S[:t-h]).ravel();checks=[]
allp=pd.read_csv(H/'tables/predictions.csv.gz');record=allp[(allp.h==60)&(allp.origin=='2015-06')].set_index('country').reindex(CC)
for k in MODELS:
    cols=['Q']+e['MODELS'][k];xx=np.stack([X[c][:t-h] for c in cols],axis=2).reshape(-1,len(cols));bb=np.stack([X[c][t] for c in cols],axis=1)
    pp=sm.OLS(y,xx,hasconst=False).fit().predict(bb)
    ok=np.allclose(pp,record[k],atol=1e-10);checks.append(dict(check='Independent statsmodels '+k,passed=bool(ok)));assert ok
pd.DataFrame(rows).to_csv(H/'tables/pooling_diagnostics.csv',index=False)
pd.DataFrame(extra).to_csv(H/'tables/individual_predictions.csv',index=False)
pd.DataFrame(checks).to_csv(H/'tables/extra_validation.csv',index=False)
print(pd.DataFrame(rows).round(4).to_string(index=False))
