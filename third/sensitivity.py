"""Predeclared robustness plus explicitly labeled post-screening diagnostics."""
from pathlib import Path
import sys,json
sys.path.insert(0,str(Path(__file__).resolve().parent))
import analyze as a
import numpy as np,pandas as pd
from scipy.stats import norm
H=a.H;rows=[];preds=[];rng=np.random.default_rng(20260911)
def score(tag,family,h,Y,P,B,RW,period='all',extra=None,units=None):
    if Y.ndim==1:Y=Y[:,None];P=P[:,None];B=B[:,None];RW=RW[:,None]
    valid=np.isfinite(Y)&np.isfinite(P)&np.isfinite(B)&np.isfinite(RW);valid[:a.START]=False
    if period=='late':valid[a.dates<pd.Period('2019-01')]=False
    if period=='no_pandemic_targets':
        keep=(a.dates+h<pd.Period('2020-01'))|(a.dates>pd.Period('2022-02'));valid &= keep[:,None]
    if not valid.any():return
    yy=Y[valid];pp=P[valid];bb=B[valid];rr=RW[valid];tt=np.flatnonzero(valid.any(axis=1))
    out=dict(family=family,tag=tag,h=h,period=period,n=int(valid.sum()),n_dates=len(tt),first=str(a.dates[tt[0]]),last=str(a.dates[tt[-1]]),rmse_ratio=np.sqrt(np.mean((yy-pp)**2)/np.mean((yy-bb)**2)),rmse_rw=np.sqrt(np.mean((yy-pp)**2)/np.mean((yy-rr)**2)))
    if extra:out.update(extra)
    rows.append(out)
    if period=='all':
        for t,c in zip(*np.where(valid)):preds.append((family,tag,h,str(a.dates[t]),units[c] if units else str(c),Y[t,c],P[t,c],B[t,c]))

# Strict EJR extensions: preserve its intercept restriction and contemporaneous centering.
for h in a.HH:
    for spec in ['Global','Trade','Specific','Interaction']:
        for variant in ['base','ridge1','ridge10','ridge100','rolling120','lag_extra1','no_EUR','no_BRL']:
            ix=np.arange(a.C)
            if variant=='no_EUR':ix=np.array([i for i,c in enumerate(a.CC) if c!='EUR'])
            if variant=='no_BRL':ix=np.array([i for i,c in enumerate(a.CC) if c!='BRL'])
            G=np.repeat(a.globallev[:,None],a.C,axis=1);Z=a.tradelev.copy()
            if variant=='lag_extra1':G=pd.DataFrame(G).shift(1).to_numpy();Z=pd.DataFrame(Z).shift(1).to_numpy()
            X={'Global':[a.q,G],'Trade':[a.q,Z],'Specific':[a.q,G,Z-G*a.exposure[None,:]],'Interaction':[a.q,G]}[spec]
            X=np.stack(X,axis=2)[:,ix,:];Y=a.target_fx(h)[:,ix]
            penalty=float(variant[5:]) if variant.startswith('ridge') else 0.;window=120 if variant=='rolling120' else None
            P,_=a.ejr_extension(X,Y,h,a.START,interaction=spec=='Interaction',penalty=penalty,window=window)
            B,_=a.ejr_extension(a.q[:,ix,None],Y,h,a.START,penalty=penalty,window=window)
            for period in ['all','late','no_pandemic_targets']:
                score(spec+'_'+variant,'FX',h,Y,P,B,np.zeros_like(Y),period,dict(spec=spec,variant=variant),[a.CC[i] for i in ix])
    print('FX sensitivities:',h,flush=True)
# Commodity prediction robustness for the joint-currency model, not best-currency selection.
for unit in ['nominal','real']:
    known=a.knownnom if unit=='nominal' else a.knownreal
    underlying=a.logP if unit=='nominal' else a.logP.sub(np.log(a.CP.USD.ffill(limit=1)),axis=0);lag=1 if unit=='nominal' else 2
    for c in a.COM:
        own=np.c_[a.dev(known[c].to_numpy()[:,None])[:,0],underlying.diff(12).shift(lag).reindex(a.dates)[c],underlying.diff(3).shift(lag).reindex(a.dates)[c]]
        X=np.c_[own,a.qd]
        for h in [12,36]:
            Y,release=a.target_price(c,h,unit)
            for variant,penalty,window in [('ridge1',1,None),('ridge10',10,None),('ridge100',100,None),('rolling120',10,120)]:
                P,_=a.oos(X,Y,h,release,penalty=penalty,window=window,start=a.START);B,_=a.oos(own,Y,h,release,penalty=penalty,window=window,start=a.START)
                for period in ['all','late','no_pandemic_targets']:score(c+'_'+unit+'_'+variant,'commodity',h,Y,P[:,0],B[:,0],np.zeros(a.T),period,dict(commodity=c,unit=unit,variant=variant))
    print('Commodity sensitivities:',unit,flush=True)
# Equal release lag: nominal and real prices use the same t-2 information baseline.
for c in a.COM:
    known=a.logP.shift(2).reindex(a.dates)[c];actual=a.logP.reindex(a.dates)[c].to_numpy()
    own=np.c_[a.dev(known.to_numpy()[:,None])[:,0],a.logP.diff(12).shift(2).reindex(a.dates)[c],a.logP.diff(3).shift(2).reindex(a.dates)[c]]
    for h in [12,36]:
        Y=np.full(a.T,np.nan);Y[:-h]=actual[h:]-known.to_numpy()[:-h]
        # Match evaluation to real-price endpoints, including missing CPI months.
        realY,_=a.target_price(c,h,'real');Y[~np.isfinite(realY)]=np.nan
        P,_=a.oos(np.c_[own,a.qd],Y,h,release=2,start=a.START);B,_=a.oos(own,Y,h,release=2,start=a.START)
        score(c+'_nominal_lag2','same_lag',h,Y,P[:,0],B[:,0],np.zeros(a.T),'all',dict(commodity=c,unit='nominal_lag2',variant='same_lag'))

# Post-screening: block intervals for candidate long-horizon improvements.
observed=pd.read_csv(H/'tables/predictions.csv.gz');intervals=[];phase=[]
candidates=[('B_FX_60','REJR_Specific','EJR'),('B_FX_36','REJR_Specific','EJR'),('A_iron_real_36','S_EUR','history'),('A_oil_nominal_12','Q_CAD','history')]
for task,model,bench in candidates:
    sub=observed[observed.task==task];h=int(sub.h.iloc[0]);z=sub.pivot(index=['origin','unit'],columns='model',values='pred')
    yy=sub.groupby(['origin','unit']).actual.first();z['actual']=yy;z=z.dropna(subset=[model,bench,'RW','actual'])
    for benchmark in [bench,'RW']:
        z['difference']=(z.actual-z[benchmark])**2-(z.actual-z[model])**2;d=z.groupby(level=0).difference.mean().to_numpy();n=len(d)
        for L in [12,h+2]:
            L=min(L,n);starts=rng.integers(0,n,(1999,int(np.ceil(n/L))));ii=(starts[:,:,None]+np.arange(L))%n;sample=d[ii.reshape(1999,-1)[:,:n]].mean(axis=1)
            lo,hi=np.quantile(sample,[.025,.975]);intervals.append(dict(task=task,model=model,benchmark=benchmark,block=L,n_dates=n,mean_loss_gain=d.mean(),low=lo,high=hi,limited_independent_blocks=n/(h+2)<3))
        # Non-overlapping starts by calendar phase; do not select the best phase.
        org=pd.PeriodIndex(z.index.get_level_values('origin'),freq='M');ordinal=np.array([x.ordinal for x in org])
        for offset in range(h+2):
            m=ordinal%(h+2)==offset
            if not m.any():continue
            zz=z[m];phase.append(dict(task=task,model=model,benchmark=benchmark,phase=offset,n_dates=zz.index.get_level_values('origin').nunique(),rmse_ratio=np.sqrt(np.mean((zz.actual-zz[model])**2)/np.mean((zz.actual-zz[benchmark])**2))))
pd.DataFrame(rows).to_csv(H/'tables/sensitivity.csv',index=False,float_format='%.10g')
pd.DataFrame(preds,columns=['family','tag','h','origin','unit','actual','pred','base']).to_csv(H/'tables/sensitivity_predictions.csv.gz',index=False,compression='gzip',float_format='%.10g')
pd.DataFrame(intervals).to_csv(H/'tables/candidate_intervals.csv',index=False,float_format='%.10g')
pd.DataFrame(phase).to_csv(H/'tables/nonoverlap_phases.csv',index=False,float_format='%.10g')
print('Sensitivity rows:',len(rows));print(pd.DataFrame(rows).query("family=='FX' and spec=='Specific' and period=='all'")[['h','variant','rmse_ratio','rmse_rw']].to_string(index=False))
