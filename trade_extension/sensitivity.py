from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from core import *
from strategies import hazards,boot
P=dict(np.load(H/'cache/predictions.npz'));rows=[];policy=[];intervals=[]
for variant,pen,delay,window,excluded in [('Base',10,2,None,None),('Ridge1',1,2,None,None),('Ridge100',100,2,None,None),('Lag3',10,3,None,None),('Window120',10,2,120,None),('NoBRL',10,2,None,0),('NoEUR',10,2,None,1)]:
    D=trade_data(delay,pen);ix=[i for i in range(C) if i!=excluded]
    bx=np.stack([center(knownq),diff(knownq,12)],axis=2)
    extras={'dynamic':np.stack([center(D['chain']),D['momentum']],axis=2),'annual':np.stack([center(D['annual']),diff(D['annual'],12)],axis=2),'structure':np.stack([D['structure'],D['forecast_structure'],D['repricing']],axis=2)}
    extras['All']=np.concatenate(list(extras.values()),axis=2)
    for task in ['real_36','real_60','persistent_36','persistent_60']:
        h=int(task.split('_')[-1]);Y=P[task+'__actual'][:,ix]
        for spec,v in extras.items():
            X=np.concatenate([bx,v],axis=2)[:,ix];B=bx[:,ix].copy();B[~np.isfinite(X).all(axis=2)]=np.nan
            pred,a=oos(X,Y,h,release=2,penalty=pen,window=window);base,b=oos(B,Y,h,release=2,penalty=pen,window=window);assert a==b
            for period,start in [('all','2013-01'),('late','2019-01')]:
                m=np.isfinite(pred)&np.isfinite(base)&np.isfinite(Y)&(dates>=pd.Period(start))[:,None]
                if m.any():rows.append(dict(variant=variant,task=task,spec=spec,period=period,n_dates=int(m.any(axis=1).sum()),ratio=np.sqrt(np.mean((Y[m]-pred[m])**2)/np.mean((Y[m]-base[m])**2)),rw=np.sqrt(np.mean((Y[m]-pred[m])**2)/np.mean(Y[m]**2))))
    # Same family of structure alerts, under data/estimation/universe changes.
    for name,hz in [('structure_observed',D['structure']),('structure_forecast',D['forecast_structure'])]:
        threshold=quantile_past(hz,.8);ready=np.isfinite(hz[:,ix]).all(axis=1)&np.isfinite(threshold[:,ix]).all(axis=1)&active&(dates>=pd.Period('2013-01'))
        base=np.zeros((T,C));base[:,ix]=rank_weights(carry[:,ix]);base[~ready]=0;w=base.copy()
        for t in range(T):
            order=np.asarray(ix)[np.argsort(carry[t,ix],kind='stable')]
            for lo,hi in zip(order[:2],order[-2:][::-1]):
                if hz[t,lo]>threshold[t,lo] or hz[t,hi]>threshold[t,hi]:w[t,[lo,hi]]=0
        first=np.flatnonzero(ready)[0]+2
        br,_,_=run_book(base,fx,rates,cost_bps=costs);rr,_,_=run_book(w,fx,rates,cost_bps=costs)
        for period,start in [('all',dates[first]),('late',pd.Period('2019-01'))]:
            mask=(np.arange(T)>=first)&(dates>=start)
            for ctrl,b in [('base',br),('rule',rr)]:policy.append(dict(variant=variant,hazard=name,period=period,control=ctrl,exposure=b.gross_exposure[mask].mean(),**metrics(b.net[mask],b.cash[mask])))
    print(variant,flush=True)
save(rows,'prediction_sensitivity');save(policy,'policy_sensitivity')
# Conditional block intervals and disjoint-origin phases for long-real predictions.
obs=pd.read_csv(H/'tables/predictions.csv.gz');ph=[];bi=[]
for task in ['persistent_36','persistent_60','real_36','real_60']:
    h=int(task.split('_')[-1])
    for model in ['dynamic','annual','structure','All']:
        a=obs[(obs.task==task)&(obs.model==model)].copy();a['loss']=(a.actual-a.pred)**2;a['base_loss']=(a.actual-a.base_pred)**2;a['rw_loss']=a.actual**2
        g=a.groupby('origin')[['loss','base_loss','rw_loss']].mean();n=len(g)
        if not n:continue
        rng=np.random.default_rng(123+h);L=h+2;idx=(rng.integers(n,size=(1499,int(np.ceil(n/L)),1))+np.arange(L))%n;ii=idx.reshape(1499,-1)[:,:n]
        for b in ['base_loss','rw_loss']:
            d=(g[b]-g.loss).to_numpy();ci=np.quantile(d[ii].mean(axis=1),[.025,.975]);bi.append(dict(task=task,model=model,benchmark=b,n=n,block=L,gain=d.mean(),low=ci[0],high=ci[1]))
            for phase in range(h+2):
                sub=g.iloc[phase::h+2]
                if len(sub)>=2:ph.append(dict(task=task,model=model,benchmark=b,phase=phase,n=len(sub),ratio=np.sqrt(sub.loss.mean()/sub[b].mean())))
save(bi,'prediction_intervals');save(ph,'nonoverlap')
