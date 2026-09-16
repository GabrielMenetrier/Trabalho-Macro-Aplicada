"""Paired, delayed carry overlays and cohort exits. All variants retained."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from core import *
P=dict(np.load(H/'cache/predictions.npz'));D=dict(np.load(H/'cache/trade.npz'))
agg=np.sum(wc*score,axis=1);den=pd.Series(agg).shift(1).expanding(min_periods=24).median().to_numpy()
bases={'Carry':wc.copy(),'EJR_gate':wc*(pd.Series(agg).rolling(6).mean().to_numpy()*12>.02)[:,None],
       'EJR_size':wc*np.clip(agg/np.maximum(den,.0001),0,1)[:,None]}
hazards={'price_observed':-sgn*D['momentum'],'price_forecast':-sgn*P['trade12_forecast'],
         'structure_observed':D['structure'],'structure_forecast':D['forecast_structure'],
         'real_shift36':sgn*(P['persistent_36__dynamic']-P['persistent_36__Base_for__dynamic']),
         'real_shift60':sgn*(P['persistent_60__dynamic']-P['persistent_60__Base_for__dynamic']),
         'real_depreciation60':sgn*P['real_60__dynamic'],
         'risk_increment':P['erased_12__structure']-P['erased_12__Base_for__structure']}
def pair_keep(hazard,threshold,reduce=1):
    bad=hazard>threshold;keep=np.ones((T,C))
    for t in range(T):
        order=np.argsort(carry[t],kind='stable')
        for lo,hi in zip(order[:2],order[-2:][::-1]):
            if bad[t,lo] or bad[t,hi]:keep[t,[lo,hi]]=1-reduce
    return keep
def cohort(base,keep,ready,tenure=12):
    w=np.zeros((T,C));alive=[]
    for t in range(T):
        if not ready[t]:continue
        # Each pair keeps its entry countries; a later alert closes both legs.
        alive=[(j,lo,hi,amount) for j,lo,hi,amount in alive if t-j<tenure and keep[t,lo]>0 and keep[t,hi]>0]
        order=np.argsort(carry[t],kind='stable')
        for lo,hi in zip(order[:2],order[-2:][::-1]):
            if keep[t,lo]>0 and keep[t,hi]>0:alive.append((t,lo,hi,abs(base[t,hi])/tenure))
        for j,lo,hi,amount in alive:w[t,hi]+=amount;w[t,lo]-=amount
    return w
def boot(a,b,L=12,B=1499):
    rng=np.random.default_rng(20260912+L);n=len(a);idx=(rng.integers(n,size=(B,int(np.ceil(n/L)),1))+np.arange(L))%n;ix=idx.reshape(B,-1)[:,:n]
    d=(a-b)[ix].mean(axis=1)*12
    return np.quantile(d,[.025,.975])
rows=[];retrows=[];conditions=[];intervals=[];weightcache={};readycache={}
def add(name,base_name,hazard,quant=.8,reduce=1,cost=1,mode='monthly'):
    hz=hazards[hazard];threshold=quantile_past(hz,quant)
    ready=np.isfinite(hz).all(axis=1)&np.isfinite(threshold).all(axis=1)&active&(dates>=pd.Period('2013-01'))
    if not ready.any():return
    assert ready[np.flatnonzero(ready)[0]:].all(),name
    keep=pair_keep(hz,threshold,reduce) if mode=='monthly' else 1-(hz>threshold).astype(float)
    base=bases[base_name].copy();base[~ready]=0
    w=base*keep if mode=='monthly' else cohort(base,keep,ready)
    if mode=='cohort':base=cohort(base,np.ones_like(keep),ready)
    w[~ready]=0
    exp=np.abs(w).sum(axis=1);baseexp=np.abs(base).sum(axis=1)
    # Historical retention, divided by the historical base exposure, not ex-post mean.
    pe=pd.Series(np.where(ready,exp,np.nan)).expanding(min_periods=1).sum().shift(1).to_numpy()
    pb=pd.Series(np.where(ready,baseexp,np.nan)).expanding(min_periods=1).sum().shift(1).to_numpy()
    scale=np.divide(pe,pb,out=np.zeros(T),where=pb>1e-12)
    volatility=np.sum(np.abs(wc)*vol,axis=1)
    med=pd.Series(volatility).expanding(min_periods=36).median().shift(1).to_numpy()
    vs=np.minimum(1,med/np.maximum(volatility,1e-8))
    ex_post=exp[:-2].sum()/baseexp[:-2].sum() if baseexp[:-2].sum()>0 else 0
    variants={'rule':w,'base':base,'past_exposure':base*scale[:,None],'vol_control':base*np.nan_to_num(vs)[:,None],
              'expost_exposure':base*ex_post} # Descriptive only: explicitly uses future average exposure.
    first=int(np.flatnonzero(ready)[0])+2
    books={}
    for control,weights in variants.items():
        b,target,_=run_book(weights,fx,rates,cost_bps=costs*cost);books[control]=b
        for period,start in [('all',dates[first]),('late',pd.Period('2019-01'))]:
            m=(np.arange(T)>=first)&(dates>=start)
            rows.append(dict(name=name,base=base_name,hazard=hazard,quantile=quant,reduce=reduce,cost=cost,mode=mode,control=control,period=period,first=str(dates[m][0]),last=str(dates[m][-1]),exposure=b.gross_exposure[m].mean(),turnover=b.turnover[m].mean()*12,cost_ann=b.cost[m].mean()*12,**metrics(b.net[m],b.cash[m])))
        for t in range(first,T):retrows.append(dict(name=name,control=control,month=str(dates[t]),net=b.net[t],cash=b.cash[t],exposure=b.gross_exposure[t]))
    weightcache[name]=w;readycache[name]=ready
    if quant==.8 and reduce==1 and cost==1:
        for bench in ['base','past_exposure','vol_control','expost_exposure']:
            for L in [12,36]:
                a=books['rule'].net.to_numpy()[first:];b=books[bench].net.to_numpy()[first:];lo,hi=boot(a,b,L)
                intervals.append(dict(name=name,benchmark=bench,block=L,n=len(a),mean_difference=12*np.mean(a-b),low=lo,high=hi))
    # Outcomes when the pre-execution alert would remove exposure, using unfiltered base.
    if base_name=='Carry' and quant==.8 and reduce==1 and cost==1 and mode=='monthly':
        removed=1-np.abs(w).sum(axis=1);applied=np.r_[0.,0.,removed[:-2]]
        for state,m in [('alert',applied>.01),('clear',applied<=.01)]:
            m &=np.arange(T)>=first;b=books['base'];r=b.net.to_numpy()[m];ex=r-b.cash.to_numpy()[m]
            conditions.append(dict(hazard=hazard,state=state,n=len(r),mean_excess=12*ex.mean(),vol=np.std(r,ddof=1)*np.sqrt(12),tail_fraction=np.mean(ex<-.02),worst=r.min(),mean_removed=applied[m].mean()))
if __name__=='__main__':
    for hazard in hazards:
        for base in bases:add(f'{base}__{hazard}',base,hazard)
        for quant in [.7,.9]:add(f'Carry__{hazard}__q{quant}', 'Carry',hazard,quant)
        add(f'Carry__{hazard}__half','Carry',hazard,reduce=.5)
        add(f'Carry__{hazard}__2cost','Carry',hazard,cost=2)
        add(f'Cohort__{hazard}','Carry',hazard,mode='cohort')
    save(rows,'strategy_metrics');pd.DataFrame(retrows).to_csv(H/'tables/strategy_returns.csv.gz',index=False,compression='gzip');save(intervals,'strategy_intervals');save(conditions,'conditions')
    np.savez_compressed(H/'cache/weights.npz',**weightcache);np.savez_compressed(H/'cache/ready.npz',**readycache)
    print('Strategies',len(weightcache),'rows',len(rows),'returns',len(retrows))
