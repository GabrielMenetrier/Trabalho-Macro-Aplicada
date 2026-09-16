"""Re-score saved forecasts and add the strictly nested EJR extensions.
Used after the first pass; analyze.py now produces this same complete specification.
"""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
import analyze as a
import numpy as np,pandas as pd
from statsmodels.stats.multitest import multipletests
obs=pd.read_csv(a.H/'tables/predictions.csv.gz');oldau=pd.read_csv(a.H/'tables/audit.csv')
for task,tab in obs.groupby('task',sort=False):
    block=tab.block.iloc[0];h=int(tab.h.iloc[0]);units=a.CC if block!='A' else [tab.unit.iloc[0]]
    Y=tab.pivot_table(index='origin',columns='unit',values='actual',aggfunc='first').reindex(index=a.dates.astype(str),columns=units).to_numpy()
    models={name:b.pivot(index='origin',columns='unit',values='pred').reindex(index=a.dates.astype(str),columns=units).to_numpy() for name,b in tab.groupby('model')}
    extra={}
    if block=='A':
        c=task.split('_')[1];unit=task.split('_')[2];lag=1 if unit=='nominal' else 2
        known=a.knownnom if unit=='nominal' else a.knownreal
        underlying=a.logP if unit=='nominal' else a.logP.sub(np.log(a.CP.USD.ffill(limit=1)),axis=0)
        own=np.c_[a.dev(known[c].to_numpy()[:,None])[:,0],underlying.diff(12).shift(lag).reindex(a.dates)[c],underlying.diff(3).shift(lag).reindex(a.dates)[c]]
        fullY,_=a.target_price(c,h,unit)
        for j,cc in enumerate(a.CC):models['DS_'+cc],extra['DS_'+cc]=a.oos(np.c_[own,a.mom[:,j]],fullY,h,release=lag,start=a.START)
    if block=='B':
        G=np.repeat(a.globallev[:,None],a.C,axis=1);GM=np.repeat(a.globalmom[:,None],a.C,axis=1)
        for name,xx,inter in [('REJR_Global',[a.q,G],False),('REJR_Trade',[a.q,a.tradelev],False),('REJR_GlobalMom',[a.q,G,GM],False),('REJR_Interaction',[a.q,G],True),('REJR_TradeInteraction',[a.q,a.tradelev],True),('REJR_Exposure',[a.q,G,G*a.exposure[None,:]],False),('REJR_Specific',[a.q,G,a.tradelev-G*a.exposure[None,:]],False)]:
            models[name],extra[name]=a.ejr_extension(np.stack(xx,axis=2),a.target_fx(h),h,start=a.START,interaction=inter)
    base='Q' if block=='B' else 'history';a.register(task,block,h,Y,models,base,extra)
    if block=='B':
        for name,P in models.items():
            if name in ['RW','EJR']:continue
            for group in ['POOL']+a.CC:
                for period in ['all','late']:a.score_series(task,name,Y,P,models['EJR'],models['RW'],h,group,period,'B','EJR')
    if block=='A':
        for name in ['QD_'+cc for cc in a.CC]:
            for period in ['all','late']:a.score_series(task,name,Y,models[name],models['dollar'],models['RW'],h,period=period,block='A',benchmark='dollar')
m=pd.DataFrame(a.metrics);m['p_holm']=np.nan;m['p_rw_holm']=np.nan
for block in ['A','B','C']:
    entries=[]
    for src,dst in [('p','p_holm'),('p_rw','p_rw_holm')]:
        mask=(m.block==block)&m[src].notna()&(m.model!='RW')
        if src=='p':mask &=m.model!=m.benchmark
        entries.extend((i,src,dst) for i in m.index[mask])
    vals=multipletests([m.loc[i,src] for i,src,dst in entries],method='holm')[1]
    for (i,src,dst),v in zip(entries,vals):m.loc[i,dst]=v
a.save(m,'metrics')
pd.DataFrame(a.predrows,columns=['block','task','h','model','origin','unit','actual','pred']).to_csv(a.H/'tables/predictions.csv.gz',index=False,compression='gzip',float_format='%.10g')
newau=pd.DataFrame(a.audits,columns=oldau.columns);oldau=oldau[~oldau.model.str.startswith(('REJR','DS_'))]
a.save(pd.concat([oldau,newau],ignore_index=True),'audit')
print(m[(m.block=='B')&(m.country=='POOL')&(m.period=='all')&(m.benchmark=='EJR')&m.model.str.startswith('REJR')][['h','model','rmse_ratio','rmse_rw','p_holm','p_rw_holm']].to_string(index=False))
