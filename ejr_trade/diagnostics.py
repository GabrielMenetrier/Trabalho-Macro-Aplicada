"""Post-primary diagnostics: reconcile the prior global commodity specification."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import run as r
import numpy as np,pandas as pd,sys
sys.path.insert(0,str(r.R/'third'))
from engine import ejr_extension
sys.stdout.reconfigure(encoding='utf-8')
inp,_,_=r.inputs()
g=r.REAL.shift(2).reindex(r.dates).mean(axis=1).to_numpy()
inp['GLOBAL']=np.repeat(g[:,None],6,axis=1)
inp['SPECIFIC']=inp['LEG_l']-inp['GLOBAL']*r.LEGACY.sum(axis=1)[None,:]
models={'EJR':['Q'],'GLOBAL':['Q','GLOBAL'],'GLOBAL_OLD':['Q','GLOBAL','SPECIFIC'],'GLOBAL_PROXY':['Q','GLOBAL','COM_l']}
out=[];audit=[];checks=[]
for name,ids in [('main',list(range(6))),('no_BRL',[1,2,3,4,5]),('no_EUR',[0,2,3,4,5]),('no_BRL_EUR',[2,3,4,5])]:
    for h in r.HH:
        y,p,a,_=r.estimate(inp,r.dates,h,models,ids)
        out+=r.score(y,p,r.dates,h,name,ids,periods=name=='main')
        audit.extend(dict(scenario=name,**x) for x in a)
        if name=='main' and h==60:
            xx=np.stack([inp[k] for k in models['GLOBAL_OLD']],axis=2)
            previous,_=ejr_extension(xx,y,h,start=int(np.flatnonzero(r.dates>=pd.Period('2010-01'))[0]))
            valid=np.isfinite(previous)&np.isfinite(p['GLOBAL_OLD'])
            assert np.allclose(previous[valid],p['GLOBAL_OLD'][valid],atol=1e-11)
            checks.append({'check':'Exact match to old REJR_Specific implementation, h=60','passed':True})
pd.DataFrame(out).to_csv(r.H/'tables/global_diagnostics.csv',index=False)
pd.DataFrame(checks).to_csv(r.H/'tables/global_validation.csv',index=False)
m=pd.DataFrame(out)
print(m[(m.scenario=='main')&(m.period=='all')&(m.country=='POOL')].pivot(index='h',columns='model',values='rmse_rw').round(3).to_string())
print('\nPrimary country results at five years:')
m=pd.read_csv(r.H/'tables/metrics.csv')
print(m[(m.scenario=='main')&(m.period=='all')&(m.h==60)&m.model.isin(r.PRIMARY)].pivot(index='country',columns='model',values='rmse_rw').round(3).to_string())
print('\nSensitivity at five years:')
print(m[(m.period=='all')&(m.h==60)&(m.country=='POOL')&m.model.isin(r.PRIMARY)].pivot(index='scenario',columns='model',values='rmse_rw').round(3).to_string())
