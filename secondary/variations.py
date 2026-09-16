"""Post-screening variations: all variants saved, none presented as fresh validation."""
from pathlib import Path
import sys,json
import numpy as np
import pandas as pd
from scipy.stats import norm
from statsmodels.stats.multitest import multipletests
R=Path(__file__).resolve().parents[1]; H=R/'secondary'; sys.path.insert(0,str(R/'src'))
from models import run_book,metrics
z=np.load(H/'cache/core.npz'); dates=pd.PeriodIndex(z['dates'],freq='M'); T=len(dates)
wc=z['wc']; active=z['active']; agg=z['agg']; ffx=z['ffx']; score=z['score']; fx=z['fx']; rates=z['rates']; carry=z['carry']; q=z['qdev']
costs=np.array([10,2,2,2,2,3]); mask=dates>=pd.Period('2013-01')
books={}; rows=[]; sources={}; infer=[]
def add(name,w,family,cost=1):
    w=np.nan_to_num(w); w[~active]=0
    b,_,_=run_book(w,fx,rates,cost_bps=costs*cost); b.index=dates
    books[name]=b; sources[name]=(w,family,cost)
    for period,start in [('common','2013-01'),('early','2013-01'),('late','2019-01')]:
        m=(dates>=pd.Period(start))
        if period=='early':m &= dates<pd.Period('2019-01')
        rows.append(dict(name=name,family=family,cost=cost,period=period,first=str(dates[m][0]),last=str(dates[m][-1]),exposure=b.gross_exposure[m].mean(),**metrics(b.net[m],b.cash[m])))
    return b
add('Carry',wc.copy(),'benchmark')
for cutoff in [0,.005,.01,.02,.04]:
    for smoothing in [1,3,6]:
        a=pd.Series(agg).rolling(smoothing,min_periods=smoothing).mean().to_numpy()
        add(f'Gate_{cutoff:g}_ma{smoothing}',wc*(a*12>cutoff)[:,None],'timing')
for history in [6,12,24,36]:
    den=pd.Series(agg).shift(1).expanding(min_periods=history).median().to_numpy()
    for cap in [.5,1.,1.5]:
        scale=np.clip(agg/np.maximum(den,.0001),0,cap)
        add(f'Size_hist{history}_cap{cap:g}',wc*scale[:,None],'sizing')
for normal in [.01,.02,.04]:
    scale=np.clip(12*agg/normal,0,1)
    add(f'Size_fixed{normal:g}',wc*scale[:,None],'sizing')
# A weaker benchmark: replace EJR with unit-coefficient / 60 raw deviation.
for coef in [0,.25,.5,1.,2.]:
    a=np.sum(wc*(carry+coef*q/60),axis=1)
    den=pd.Series(a).shift(1).expanding(min_periods=24).median().to_numpy()
    add(f'Rawq_coef{coef:g}',wc*np.clip(a/np.maximum(den,.0001),0,1)[:,None],'raw_q')
# Explicitly retain every selected variation in the stress test, including losers.
for name in list(books):
    if name=='Carry' or name in ['Gate_0_ma1','Gate_0.01_ma3','Gate_0.02_ma6','Size_hist24_cap1','Size_fixed0.02','Rawq_coef0.5']:
        w,family,cost=sources[name]; add(name+'_2cost',w.copy(),family,2)

rng=np.random.default_rng(20260910)
def bootstrap(d,L,B=1999):
    d=np.asarray(d); n=len(d); k=int(np.ceil(n/L)); origins=rng.integers(0,n,(B,k))
    ii=(origins[:,:,None]+np.arange(L))%n; means=d[ii.reshape(B,-1)[:,:n]].mean(axis=1)*12
    return np.quantile(means,[.025,.975])
for name,b in books.items():
    if name=='Carry':continue
    diff=(b.net-books['Carry'].net).to_numpy()[mask]
    for L in [12,36]:
        lo,hi=bootstrap(diff,L)
        infer.append(dict(name=name,block=L,annual_difference=12*diff.mean(),low=lo,high=hi))

# Primary timing comparison with causal and descriptive exposure controls.
orig=pd.read_csv(H/'tables/strategy_returns.csv'); orig['month']=pd.PeriodIndex(orig.month,freq='M')
pivot=orig.pivot(index='month',columns='strategy',values='net'); pm=pivot.index>=pd.Period('2010-03')
primary=[]
for name in ['Gate_FX','Gate_total','Pair_total','Pair_FX','Size_signal','Extreme_long','Extreme_short']:
    for bench in ['Carry',name+'_past_exposure',name+'_expost_exposure']:
        d=(pivot[name]-pivot[bench]).to_numpy()[pm]
        lo,hi=bootstrap(d,12)
        primary.append(dict(strategy=name,benchmark=bench,annual_difference=12*d.mean(),low=lo,high=hi))
# No claim of a formal randomized experiment: circular shifts preserve gate persistence.
placebo=[]
for name in ['Gate_FX','Gate_total','Size_signal']:
    # Reconstruct signal exposure from realized exposure shifted back two months.
    a=orig[orig.strategy==name].set_index('month').reindex(dates).gross_exposure.to_numpy()
    exposure=np.zeros(T); exposure[:-2]=np.nan_to_num(a[2:])
    loc=np.flatnonzero(active); obs=float(pivot[name].mean())
    fake=[]
    for shift in range(1,len(loc)):
        e=np.zeros(T); e[loc]=np.roll(exposure[loc],shift)
        b,_,_=run_book(wc*e[:,None],fx,rates,cost_bps=costs)
        fake.append(b.net.to_numpy()[dates>=pd.Period('2010-03')].mean())
    placebo.append(dict(strategy=name,rank_fraction=float(np.mean(np.asarray(fake)>=obs)),n_shifts=len(fake),actual_ann=12*obs,median_shift_ann=12*np.median(fake)))

# When does carry work? Labels use only conditions known before portfolio execution.
condition=[]; baseline=books['Carry']
conditions={'FX favorável':z['aggfx']>0,'FX desfavorável':z['aggfx']<=0,
            'Total positivo':agg>0,'Total não positivo':agg<=0}
v=z['vol']; med=pd.Series(v).expanding(min_periods=36).median().shift(1).to_numpy()
conditions.update({'Vol alta':v>med,'Vol baixa':v<=med})
for name,m in conditions.items():
    applied=np.r_[False,False,m[:-2]]&(dates>=pd.Period('2010-03'))
    rr=baseline.net.to_numpy()[applied]; cash=baseline.cash.to_numpy()[applied]
    condition.append(dict(condition=name,n=len(rr),ann_mean_excess=(rr-cash).mean()*12,vol=rr.std(ddof=1)*np.sqrt(12),loss_fraction=np.mean(rr<0),tail2_fraction=np.mean(rr<-.02),worst=rr.min() if len(rr) else np.nan))

# Hedge variations keep 100% allocation to the USD underlying.
etf=pd.read_csv(R/'data/processed/etf_adjusted_close.csv',index_col=0); etf.index=pd.PeriodIndex(etf.index,freq='M'); etf=etf.reindex(dates)
ret=etf.pct_change(fill_method=None); rm=np.expm1(np.log1p(rates/100)/12)
ratio=np.r_[1,fx[1:,0]/fx[:-1,0]]; forward=np.r_[1,(1+rm[:-1,0])/(1+rm[:-1,-1])]; cash=np.r_[0,rm[:-1,0]]
hedgerows=[]; hedgepaths={}; hedgeinf=[]
for asset in ['BIL','SPY']:
    rules={f'Fixed_{x:g}':np.full(T,x) for x in [0,.25,.5,.75,1]}
    for ma in [1,3,6]:
        f=pd.Series(z['f'][:,0]/60).rolling(ma,min_periods=ma).mean().to_numpy()
        for buffer in [-.01,0,.01]:rules[f'FX_ma{ma}_b{buffer:g}']=(12*f<buffer).astype(float)
    for shift in [-.01,0,.01]:rules[f'Total_b{shift:g}']=(12*(z['f'][:,0]/60-carry[:,0])<shift).astype(float)
    # Hedge under negative expected dollar return; interpolate within ±2% annual forecast.
    rules['Smooth_FX']=np.clip(.5-12*z['f'][:,0]/60/.04,0,1)
    appliedfx=np.r_[0,0,rules['FX_ma1_b0'][:-2]]
    rules['Matched_expost']=np.full(T,appliedfx[mask].mean())
    rules['Matched_smooth']=np.full(T,np.r_[0,0,rules['Smooth_FX'][:-2]][mask].mean())
    rules['Matched_total']=np.full(T,np.r_[0,0,rules['Total_b0'][:-2]][mask].mean())
    for name,Hedge in rules.items():
        for cost in ([2,5,10] if name in ['Fixed_0','Fixed_0.5','Fixed_1','FX_ma1_b0','Smooth_FX'] else [2]):
            applied=np.r_[0,0,Hedge[:-2]]
            r=(1+ret[asset].to_numpy())*ratio-1+applied*(forward-ratio)-applied*cost/10000
            # Common Jan-2013 start: charge new initial entry and terminal liquidation.
            r[np.flatnonzero(mask)[0]]-=.0012; r[-1]-=.0012*(1+r[-1])
            tag=f'{asset}:{name}:{cost}'; hedgepaths[tag]=r
            for period,mm in [('common',mask),('early',mask&(dates<pd.Period('2019-01'))),('late',dates>=pd.Period('2019-01'))]:
                hedgerows.append(dict(asset=asset,rule=name,cost=cost,period=period,hedge=applied[mm].mean(),**metrics(r[mm],cash[mm])))
    for rule in ['FX_ma1_b0','Smooth_FX','Total_b0']:
        matched={'FX_ma1_b0':'Matched_expost','Smooth_FX':'Matched_smooth','Total_b0':'Matched_total'}[rule]
        for benchmark in ['Fixed_0','Fixed_0.5','Fixed_1',matched]:
            d=(hedgepaths[f'{asset}:{rule}:2']-hedgepaths[f'{asset}:{benchmark}:2'])[mask]
            lo,hi=bootstrap(d,12)
            hedgeinf.append(dict(asset=asset,rule=rule,benchmark=benchmark,annual_difference=12*d.mean(),low=lo,high=hi))

for name,a in [('variation_metrics',rows),('variation_intervals',infer),('primary_intervals',primary),('timing_placebo',placebo),('conditions',condition),('hedge_variations',hedgerows),('hedge_intervals',hedgeinf)]:
    pd.DataFrame(a).to_csv(H/'tables'/f'{name}.csv',index=False,float_format='%.10g')
pd.DataFrame({name:b.net.to_numpy() for name,b in books.items()},index=dates).to_csv(H/'tables/variation_returns.csv',index_label='month')
pd.DataFrame(hedgepaths,index=dates).to_csv(H/'tables/hedge_variation_returns.csv',index_label='month')
print('Variations:',len(books),'carry specifications;',len(hedgepaths),'asset/hedge/cost combinations.')
print(pd.DataFrame(rows).query("period=='common'").sort_values('sharpe',ascending=False)[['name','cagr','sharpe','maxdd','exposure']].head(12).to_string(index=False))
print(pd.DataFrame(primary).to_string(index=False))
