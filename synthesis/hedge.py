from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from model import *
etf=read(R/'data/processed/etf_adjusted_close.csv').reindex(dates);ur=etf.pct_change(fill_method=None)
rm=np.expm1(np.log1p(rates/100)/12);ratio=np.r_[1,fx[1:,0]/fx[:-1,0]];forward=np.r_[1,(1+rm[:-1,0])/(1+rm[:-1,-1])];cash=np.r_[0,rm[:-1,0]]
smooth=lambda v:np.clip(.5-v/.04,0,1)
rules={'Unhedged':np.zeros(T),'Half':np.full(T,.5),'Full':np.ones(T),'EJR_FX':smooth(12*f[:,0]/60),'EJR_total':smooth(12*(f[:,0]/60-carry[:,0])),
       'Commodity_blend':smooth(12*(.5*f[:,0]+.5*Fcommodity[:,0])/60)}
rules['Equal_signals']=(rules['EJR_FX']+rules['EJR_total']+rules['Commodity_blend'])/3
# Simple shrinkage to a structural half hedge, not estimated from future performance.
rules['Half_plus_signal']=.5*rules['Half']+.5*rules['Equal_signals']
rows=[];paths=[];inference=[];start='2013-03';m=dates>=pd.Period(start);first=np.flatnonzero(m)[0]
def returns(asset,Hedge,cost):
    applied=np.r_[0.,0.,np.nan_to_num(Hedge[:-2],nan=.5)]
    r=(1+ur[asset].to_numpy())*ratio-1+applied*(forward-ratio)-applied*cost/10000
    r[first]-=.0012;r[-1]-=.0012*(1+r[-1]);return r,applied
for asset in ['BIL','SPY']:
    for name,h in rules.items():
        for cost in [2,5,10]:
            r,applied=returns(asset,h,cost)
            for period,mm in [('all',m),('recent',m&(dates>=pd.Period('2019-01'))),('common',m&(dates>=pd.Period('2018-04')))]:
                e=r[mm]-cash[mm];rows.append(dict(asset=asset,name=name,cost=cost,period=period,hedge=applied[mm].mean(),ce5=12*(e.mean()-2.5*e.var(ddof=1)),**metrics(r[mm],cash[mm])))
            if cost==2:
                for t in np.flatnonzero(m):paths.append(dict(asset=asset,name=name,month=str(dates[t]),net=r[t],cash=cash[t],hedge=applied[t]))
        if name not in ['EJR_FX','Equal_signals','Half_plus_signal']:continue
        r,ap=returns(asset,h,2)
        for bench,hb in [('Unhedged',rules['Unhedged']),('Half',rules['Half']),('Matched_expost',np.full(T,ap[m].mean()))]:
            br,_=returns(asset,hb,2);d=(r-br)[m];n=len(d)
            for L in [12,36]:
                rng=np.random.default_rng(912+L);idx=((rng.integers(n,size=(1999,int(np.ceil(n/L)),1))+np.arange(L))%n).reshape(1999,-1)[:,:n];lo,hi=np.quantile(12*d[idx].mean(axis=1),[.025,.975]);inference.append(dict(asset=asset,name=name,benchmark=bench,block=L,difference=d.mean()*12,low=lo,high=hi))
save(rows,'hedge_metrics');save(paths,'hedge_returns');save(inference,'hedge_intervals');np.savez_compressed(H/'cache/hedge_rules.npz',**rules)
print('Hedge combinations',len(rules)*2*3)
