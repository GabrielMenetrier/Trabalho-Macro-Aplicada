from pathlib import Path
import sys,json,hashlib,itertools,time
import numpy as np,pandas as pd
from scipy.optimize import minimize
R=Path(__file__).resolve().parents[1];H=R/'horizon_tests';sys.path.insert(0,str(R/'src'))
from models import run_book,metrics,rank_weights,forecast,features
for d in ['tables','cache']:(H/d).mkdir(exist_ok=True)
CC=['BRL','EUR','JPY','GBP','CAD','SEK'];z=dict(np.load(R/'secondary/cache/core.npz'))
dates=pd.PeriodIndex(z['dates'],freq='M');fx=z['fx'];rates=z['rates'];F=z['f'];carry=z['carry'];T,C=fx.shape
start=int(np.flatnonzero(dates==pd.Period('2010-01'))[0]);first=start+2
rm=np.expm1(np.log1p(rates/100)/12);le=np.zeros((T,C));le[1:]=np.log1p(rm[:-1,:C])+np.log(fx[:-1]/fx[1:])-np.log1p(rm[:-1,-1,None])
long=np.full_like(le,np.nan)
for t in range(60,T):long[t]=le[t-59:t+1].sum(axis=0)
cost=np.array([10,2,2,2,2,3]);audit=[];solves=[]
parts=[]
for k in [2,3,4]:
 for ids in itertools.combinations(range(C),k):
  signs=-np.ones(C);signs[list(ids)]=1
  A=np.array([signs==1,signs==-1],float)
  init=np.where(signs==1,.5/k,.5/(C-k))
  parts.append((signs,A,init))
def covariance(t,kind):
 hist=long[60:t] if kind=='long60' else le[max(1,t-120):t]
 assert np.isfinite(hist).all() and len(hist)>=36
 S=np.cov(hist,rowvar=False)
 if kind=='monthly120':S*=60
 return .8*S+.2*np.diag(np.diag(S))+np.eye(C)*1e-10,len(hist)
def optimize(mu,S):
 # Standardize units for stable numerical objective; spread on 50% short side.
 funding=.005*5*.5;best=None;bestval=-np.inf;fails=0
 for sign,A,x0 in parts:
  M=S*sign[:,None]*sign[None,:];m=mu*sign
  def obj(x):
   v=M@x;sd=np.sqrt(x@v);a=m@x-funding
   return -a/sd,-m/sd+a*v/sd**3
  res=minimize(obj,x0,jac=True,method='SLSQP',bounds=[(0,.25)]*C,
   constraints={'type':'eq','fun':lambda x,A=A:A@x-.5,'jac':lambda x,A=A:A},options={'ftol':1e-10,'maxiter':100})
  feasible=np.max(np.abs(A@res.x-.5))<1e-7 and np.max(res.x)<=.2500001 and np.min(res.x)>=-1e-7
  if not res.success:fails+=1
  if feasible and -res.fun>bestval:bestval=-res.fun;best=res.x*sign
 assert best is not None
 return best,bestval,fails
W={'Pairs_EJR':rank_weights(carry-F/60),'Pairs_Carry':rank_weights(carry)}
cache=H/'cache/optimized.npz'
if cache.exists():
 a=dict(np.load(cache));W.update(a)
 audit=json.loads((H/'cache/optimization_audit.json').read_text())
else:
 for kind in ['long60','monthly120']:
  for signal in ['EJR','Carry']:
   if kind=='monthly120' and signal=='Carry':continue
   name='Sharpe_'+signal+'_'+kind;w=np.zeros((T,C))
   for t in range(start,T-2):
    mu=60*carry[t]-(F[t] if signal=='EJR' else 0);S,n=covariance(t,kind)
    w[t],val,fail=optimize(mu,S)
    audit.append(dict(name=name,origin=str(dates[t]),last_risk_return=str(dates[t-1]),risk_n=n,expected_sharpe=val,solver_failures=fail))
    if (t-start)%36==0:print(name,str(dates[t]),flush=True)
   W[name]=w
 np.savez_compressed(cache,**{k:v for k,v in W.items() if k.startswith('Sharpe')})
 (H/'cache/optimization_audit.json').write_text(json.dumps(audit))
def schedule(w,origin,h,end):
 a=np.zeros_like(w)
 for t in range(origin,end-1):a[t]=w[origin+((t-origin)//h)*h]
 return a
def book(w,origin,h,n,costmult=1,borrow=50):
 end=origin+2+n
 a=schedule(w,origin,h,end)
 b,_,_=run_book(a[:end],fx[:end],rates[:end],cost*costmult,borrow)
 b=b.iloc[origin+2:end].copy();b.index=dates[origin+2:end]
 return b
def stats(b):
 m=metrics(b.net,b.cash)
 m.update(first=str(b.index[0]),last=str(b.index[-1]),cost_ann=12*b.cost.mean(),borrow_ann=12*b.borrow.mean(),turnover=12*b.turnover.mean(),gross=b.gross_exposure.mean())
 return m
rows=[];rets=[];saved={}
for scenario,cm,br in [('Base',1,50),('Stress',4,150)]:
 for name,w in W.items():
  for h in [1,12,60]:
   b=book(w,start,h,180,cm,br);rows.append(dict(scenario=scenario,name=name,hold=h,**stats(b)))
   saved[scenario,name,h]=b
   for month,r in b.iterrows():rets.append(dict(scenario=scenario,name=name,hold=h,month=str(month),**r.to_dict()))
for name,w in W.items():
 b=book(w,start,1,T-first);rows.append(dict(scenario='FullMonthly',name=name,hold=1,**stats(b)))
pd.DataFrame(rows).to_csv(H/'tables/metrics.csv',index=False)
pd.DataFrame(rets).to_csv(H/'tables/returns.csv.gz',index=False,compression='gzip')
# Same sixty-month windows: 60-month holding versus renewed twelve-month positions.
entry=[]
for origin in range(start,T-61):
 for name in ['Pairs_EJR','Pairs_Carry','Sharpe_EJR_long60']:
  for h in [12,60]:
   b=book(W[name],origin,h,60)
   entry.append(dict(origin=str(dates[origin]),name=name,hold=h,**stats(b)))
pd.DataFrame(entry).to_csv(H/'tables/entry_windows.csv',index=False)
# Paired block intervals; resample realized returns, never optimize on resamples.
rng=np.random.default_rng(20260915);intervals=[]
comparisons=[(('Sharpe_EJR_long60',h),('Pairs_EJR',h)) for h in [1,12,60]]+[(('Pairs_EJR',60),('Pairs_EJR',12)),(('Pairs_Carry',60),('Pairs_Carry',12))]
for a,b in comparisons:
 x=saved['Base',*a];y=saved['Base',*b];ex=(x.net-x.cash).to_numpy();ey=(y.net-y.cash).to_numpy()
 def sharpe(v):return np.mean(v,axis=-1)/np.std(v,axis=-1,ddof=1)*np.sqrt(12)
 for block in [12,60]:
  idx=(rng.integers(0,180,(3000,int(np.ceil(180/block)),1))+np.arange(block)).reshape(3000,-1)[:,:180]%180
  ds=sharpe(ex[idx])-sharpe(ey[idx]);dr=(ex[idx]-ey[idx]).mean(axis=1)*12
  intervals.append(dict(a=str(a),b=str(b),block=block,delta_sharpe=sharpe(ex)-sharpe(ey),low=np.quantile(ds,.025),high=np.quantile(ds,.975),mean_excess_delta=(ex-ey).mean()*12,mean_low=np.quantile(dr,.025),mean_high=np.quantile(dr,.975)))
pd.DataFrame(intervals).to_csv(H/'tables/intervals.csv',index=False)
pd.DataFrame(audit).to_csv(H/'tables/optimization_audit.csv',index=False)
np.savez_compressed(H/'cache/weights.npz',dates=dates.astype(str).to_numpy(),**W)
print(pd.DataFrame(rows)[['scenario','name','hold','cagr','sharpe','maxdd']].to_string(index=False),flush=True)
