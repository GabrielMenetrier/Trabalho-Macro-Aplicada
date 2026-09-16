"""Exploratory joint-pair probability, motivated by direction and covariance."""
from pathlib import Path
import sys,itertools
sys.path.insert(0,str(Path(__file__).resolve().parent))
from model import *
from engine import oos
import statsmodels.api as sm
pairs=list(itertools.combinations(range(C),2));K=len(pairs);Y=np.full((T,K),np.nan);X=np.full((T,K,5),np.nan);Z=np.full((T,K,3),np.nan)
for k,(i,j) in enumerate(pairs):
    ds=s[:,j]-s[:,i];dv=pd.Series(ds).diff().rolling(12).std().to_numpy()
    X[:,k]=np.stack([carry[:,j]-carry[:,i],dv,-pd.Series(ds).diff(12).to_numpy()/12,-(f[:,j]-f[:,i])/60,qdev[:,j]-qdev[:,i]],axis=1)
    Z[:,k]=np.stack([D['momentum'][:,j]-D['momentum'][:,i],D['structure'][:,j]+D['structure'][:,i],D['structure'][:,j]-D['structure'][:,i]],axis=1)
    for t in range(T-13):Y[t,k]=((carry[t+1:t+13,j]-carry[t+1:t+13,i]).sum()-(ds[t+13]-ds[t+1]))<0
X[~z['active']]=np.nan;ZZ=np.concatenate([X,Z],axis=2);XB=X.copy();XB[~np.isfinite(ZZ).all(axis=2)]=np.nan
base,ab=oos(XB,Y,13,min_dates=36);aug,aa=oos(ZZ,Y,13,min_dates=36);assert aa==ab;base=np.clip(base,.01,.99);aug=np.clip(aug,.01,.99)
delta=aug-base;limL=np.maximum(pastq(delta),0);limS=np.maximum(pastq(-delta),0)
W,_,full,_=make_policies();start='2018-04';mask=dates>=pd.Period(start);rows=[];obs=[];out=np.zeros((T,C));alive=[]
lookup={v:k for k,v in enumerate(pairs)}
def alert(t,lo,hi):
    k=lookup[tuple(sorted([lo,hi]))];return delta[t,k]>limL[t,k] if hi>lo else -delta[t,k]>limS[t,k]
for t in range(T):
    if not full[t]:continue
    alive=[(a,lo,hi) for a,lo,hi in alive if t-a<12 and not alert(t,lo,hi)]
    order=np.argsort(carry[t],kind='stable')
    for lo,hi in zip(order[:2],order[-2:][::-1]):
        if not alert(t,lo,hi):alive.append((t,int(lo),int(hi)))
    for a,lo,hi in alive:out[t,lo]-=.25/12;out[t,hi]+=.25/12
    for lo,hi in zip(order[:2],order[-2:][::-1]):
        k=lookup[tuple(sorted([lo,hi]))]
        if np.isfinite(Y[t,k]) and np.isfinite(aug[t,k]):
            orient=hi>lo;y=Y[t,k] if orient else 1-Y[t,k];p=aug[t,k] if orient else 1-aug[t,k];b=base[t,k] if orient else 1-base[t,k]
            obs.append(dict(origin=str(dates[t]),long=CC[hi],short=CC[lo],actual=y,pred=p,base=b))
for name,w in [('Cohort_pair_risk',out),('Cohort_leg_risk',W['Cohort_risk']),('Cohort_base',W['Cohort_base']),('Ensemble_pair',(W['Size_structure']+W['Gate_price']+out)/3)]:
    b,_,_=book(w,start);rows.append(dict(name=name,**stats(b,mask)))
a=pd.DataFrame(obs);daily=a.assign(d=(a.actual-a.base)**2-(a.actual-a.pred)**2).groupby('origin').d.mean();fit=sm.OLS(daily,np.ones(len(daily))).fit(cov_type='HAC',cov_kwds={'maxlags':15})
save([dict(n=len(a),n_dates=len(daily),brier_ratio=((a.actual-a.pred)**2).mean()/((a.actual-a.base)**2).mean(),p=float(fit.pvalues.iloc[0]))],'pair_prediction_metrics')
save(a,'pair_predictions');save(rows,'pair_strategy_metrics');save([dict(origin=str(dates[t]),last_available=str(dates[e]),n=n,n_dates=nd) for t,a,b,e,n,nd in aa],'pair_audit');np.savez_compressed(H/'cache/pair.npz',base=base,aug=aug,Y=Y,X=XB,Z=ZZ,weights=out)
print(pd.DataFrame(rows)[['name','mean_excess','sharpe','maxdd']].to_string(index=False))
