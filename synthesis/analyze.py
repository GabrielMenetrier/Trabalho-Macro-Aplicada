from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from model import *
W,normal,full,events=make_policies();longstart='2013-03';fullstart=str(dates[np.flatnonzero(full)[0]+2]);rows=[];paths=[];attrib=[];cache={}
for window,start in [('long',longstart),('common',fullstart)]:
    for name,w in W.items():
        if window=='long' and name in ['Cohort_base','Cohort_risk','Integrated_cohort','All_filters','Equal_modules','Core_satellite']:continue
        b,t,c=book(w,start);cache[window+'__'+name]=b.net.to_numpy()
        for period,begin,end in [('all',start,'2026-08'),('early',start,'2018-12'),('recent','2019-01','2026-08'),('post2021','2022-01','2026-08')]:
            m=(dates>=pd.Period(max(begin,start)))&(dates<=pd.Period(end))
            if m.sum()<12:continue
            rows.append(dict(window=window,period=period,name=name,first=str(dates[m][0]),last=str(dates[m][-1]),**stats(b,m)))
        m=dates>=pd.Period(start)
        for i in np.flatnonzero(m):paths.append(dict(window=window,name=name,month=str(dates[i]),net=b.net[i],cash=b.cash[i],exposure=b.gross_exposure[i],turnover=b.turnover[i],cost=b.cost[i],borrow=b.borrow[i]))
        # Exact arithmetic contribution decomposition, matching the engine.
        rm=np.expm1(np.log1p(rates/100)/12);fxr=np.zeros((T,C));fxr[1:]=fx[:-1]/fx[1:]-1;interest=np.vstack([np.zeros(C),rm[:-1,:C]])
        funding=np.r_[0,rm[:-1,-1]];components={'FX':(t*fxr).sum(axis=1),'Interest':(t*(interest-funding[:,None])).sum(axis=1),'Interaction':(t*interest*fxr).sum(axis=1),'Borrow':-b.borrow.to_numpy(),'Trading':-b.cost.to_numpy()}
        assert np.allclose(sum(components.values()),b.net-b.cash)
        for component,a in components.items():attrib.append(dict(window=window,name=name,component=component,annual=12*a[m].mean()))
        for cidx,cc in enumerate(CC):attrib.append(dict(window=window,name=name,component=cc,annual=12*c[m,cidx].mean()))
save(rows,'metrics');pd.DataFrame(paths).to_csv(H/'tables/returns.csv.gz',index=False,compression='gzip');save(attrib,'attribution')
for n,a in events.items():save(a,'events_'+n)
np.savez_compressed(H/'cache/weights.npz',**W);np.savez_compressed(H/'cache/returns.npz',**cache);np.savez_compressed(H/'cache/signals.npz',commodity=Fcommodity,normal=normal,full=full)
(H/'cache/design.json').write_text(__import__('json').dumps(dict(long_start=longstart,common_start=fullstart,policies=list(W)),indent=2))
save([dict(origin=str(dates[t]),first_train=str(dates[a]),last_train=str(dates[b]),last_available=str(dates[c]),n=n,n_dates=nd) for t,a,b,c,n,nd in faudit],'commodity_audit')
print('Common start:',fullstart,'policies',len(W));print(pd.DataFrame(rows).query("window=='common' and period=='all'")[['name','cagr','mean_excess','vol','sharpe','maxdd','ce5','exposure']].to_string(index=False))
