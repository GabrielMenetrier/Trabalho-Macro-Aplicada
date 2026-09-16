"""Fixed holdings cross-check and focused chronology/accounting validation."""
from pathlib import Path
import sys,json,hashlib
import numpy as np,pandas as pd
R=Path(__file__).resolve().parents[1];H=R/'horizon_tests'
ns={'__file__':str(H/'run.py')}
exec((H/'run.py').read_text(encoding='utf-8').split("W={'Pairs_EJR'")[0],ns)
globals().update({k:v for k,v in ns.items() if not k.startswith('__')})
W=dict(np.load(H/'cache/weights.npz',allow_pickle=True));W.pop('dates')
def schedule(w,origin,h,end):
 a=np.zeros_like(w)
 for t in range(origin,end-1):a[t]=w[origin+((t-origin)//h)*h]
 return a
def frozen(w,origin,h,n,cm=1,borrow=50):
 prev=np.zeros(C);rows=[]
 for t in range(origin+2,origin+2+n):
  k=t-origin-2
  new=w[origin+k].copy() if k%h==0 else prev.copy()
  spot=fx[t-1]/fx[t]-1;asset=(1+rm[t-1,:C])*(1+spot)-1;rf=rm[t-1,-1]
  turnover=np.abs(new-prev);fee=np.sum(turnover*cost*cm/10000)
  spread=np.sum(np.maximum(-new,0)*borrow/10000/12*(1+spot))
  gross=rf+np.sum(new*(asset-rf));net=gross-fee-spread
  if k==n-1:
   liq=np.abs(new*(1+asset));fee+=np.sum(liq*cost*cm/10000);turnover+=liq;net=gross-fee-spread
  rows.append(dict(net=net,cash=rf,cost=fee,borrow=spread,gross_exposure=np.abs(new).sum(),net_exposure=new.sum(),turnover=turnover.sum()))
  assert 1+net>0
  prev=new*(1+asset)/(1+net)
 return pd.DataFrame(rows,index=dates[origin+2:origin+2+n])
def stats(b):
 m=metrics(b.net,b.cash);m.update(first=str(b.index[0]),last=str(b.index[-1]),mean_gross=b.gross_exposure.mean(),max_gross=b.gross_exposure.max(),mean_abs_net=b.net_exposure.abs().mean(),max_abs_net=b.net_exposure.abs().max())
 return m
rows=[];windows=[]
for scenario,cm,br in [('Base',1,50),('Stress',4,150)]:
 for name in ['Pairs_EJR','Pairs_Carry']:
  for h in [12,60]:rows.append(dict(scenario=scenario,name=name,hold=h,**stats(frozen(W[name],start,h,180,cm,br))))
for origin in range(start,T-61):
 for h in [12,60]:windows.append(dict(origin=str(dates[origin]),hold=h,**stats(frozen(W['Pairs_EJR'],origin,h,60))))
pd.DataFrame(rows).to_csv(H/'tables/frozen_metrics.csv',index=False)
pd.DataFrame(windows).to_csv(H/'tables/frozen_windows.csv',index=False)
checks=[]
def ck(label,v):
 checks.append(dict(check=label,passed=bool(v)));assert v,label
for name,w in W.items():
 a=w[start:T-2]
 ck(name+' net zero',np.max(np.abs(a.sum(axis=1)))<1e-7)
 ck(name+' gross one',np.max(np.abs(np.abs(a).sum(axis=1)-1))<1e-7)
 ck(name+' 25pct cap',np.max(np.abs(a))<.2500001)
for t in [start,start+60,start+120]:
 S,n=covariance(t,'long60');mu=60*carry[t]-F[t]
 def objective(w):return (mu@w-.0125)/np.sqrt(w@S@w)
 ck('Optimizer improves expected Sharpe '+str(dates[t]),objective(W['Sharpe_EJR_long60'][t])+1e-8>=objective(W['Pairs_EJR'][t]))
 w,val,_=optimize(mu,S)
 ck('Optimizer repeatability '+str(dates[t]),np.allclose(w,W['Sharpe_EJR_long60'][t],atol=1e-6))
 original=long[t:].copy();long[t:]+=100
 S2,_=covariance(t,'long60');long[t:]=original
 ck('Future risk returns cannot affect covariance '+str(dates[t]),np.array_equal(S,S2))
 # Predictor construction in the saved project is independently reproduced.
 def read(n):
  a=pd.read_csv(R/f'data/processed/{n}.csv',index_col=0);a.index=pd.PeriodIndex(a.index,freq='M');return a
 q=features(read('fx')[CC],read('cpi')).reindex(dates).to_numpy()
 fp=forecast(np.log(fx[:t+1]),q[:t+1],60)[0]['ejr'][t]
 ck('Forecast prefix reproduces saved signal '+str(dates[t]),np.allclose(fp,F[t],rtol=1e-8,atol=1e-8))
for name in ['Pairs_EJR','Pairs_Carry']:
 a=schedule(W[name],start,60,start+182)
 for origin in [start,start+60,start+120]:ck('60-month selection fixed '+name+str(origin),np.array_equal(a[origin:origin+60],np.repeat(W[name][[origin]],60,axis=0)))
 # Holding one month must coincide exactly with the existing accounting engine.
 a=frozen(W[name],start,1,180)
 target=schedule(W[name],start,1,start+182)
 b=run_book(target[:start+182],fx[:start+182],rates[:start+182],cost,50)[0].iloc[start+2:]
 ck('Frozen engine matches existing monthly accounting '+name,np.allclose(a.net,b.net,atol=1e-12))
orig=pd.read_csv(R/'output/tables/portfolio_metrics.csv');new=pd.read_csv(H/'tables/metrics.csv')
for name,old in [('Pairs_EJR','EJR + carry'),('Pairs_Carry','Carry')]:
 ck('Original full backtest reproduced '+name,abs(new[(new.scenario=='FullMonthly')&(new.name==name)].cagr.iloc[0]-orig[orig.strategy==old].cagr.iloc[0])<1e-9)
# Full-monthly covariance sensitivity: paired inference over 198 common months.
rng=np.random.default_rng(20260915);ints=[]
for name in ['Sharpe_EJR_long60','Sharpe_EJR_monthly120']:
 n=T-start-2
 def path(name):
  a=schedule(W[name],start,1,T)
  return run_book(a,fx,rates,cost,50)[0].iloc[start+2:]
 a=path(name);b=path('Pairs_EJR');x=(a.net-a.cash).to_numpy();y=(b.net-b.cash).to_numpy()
 def sh(a):return a.mean(axis=-1)/a.std(axis=-1,ddof=1)*np.sqrt(12)
 for block in [12,60]:
  ix=(rng.integers(n,size=(3000,int(np.ceil(n/block)),1))+np.arange(block)).reshape(3000,-1)[:,:n]%n
  d=sh(x[ix])-sh(y[ix]);ints.append(dict(name=name,block=block,delta=sh(x)-sh(y),low=np.quantile(d,.025),high=np.quantile(d,.975)))
pd.DataFrame(ints).to_csv(H/'tables/full_monthly_intervals.csv',index=False)
(H/'tables/validation.json').write_text(json.dumps(checks,indent=2))
print(pd.DataFrame(rows).to_string(index=False));print('Checks passed:',len(checks));print(pd.DataFrame(ints).to_string(index=False))
