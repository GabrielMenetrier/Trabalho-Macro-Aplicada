"""Causal-in-time predictive regressions; all indices are calendar months."""
import numpy as np
import pandas as pd

def features(spot, cpi, lag=2):
    # Carry last released observation for at most one missing reference month.
    p=cpi.ffill(limit=1).shift(lag)
    return np.log(spot)+np.log(p['USD']).to_numpy()[:,None]-np.log(p[spot.columns])

def forecast(s, q, h, min_train=60, window=None, train_countries=None):
    """At t, labels are restricted to j+h <= t-1 (one-month data buffer).

    EJR: pooled slope, no intercept, q demeaned using ONLY data up to t.
    FE: pooled slope plus currency-specific intercepts.
    OLS: independent intercept/slope. No estimation uses future q or returns.
    """
    s=np.asarray(s,float); q=np.asarray(q,float); T,C=s.shape
    preds={k:np.full((T,C),np.nan) for k in ['ejr','fe','ols','drift','ppp']}
    slopes=np.full((T,3),np.nan); nobs=np.zeros(T,int); last=np.full(T,-1,int)
    countries=np.arange(C) if train_countries is None else np.array(train_countries)
    for t in range(h+min_train+1,T):
        end=t-h # exclusive: maximum j=t-h-1 -> label ends t-1.
        beg=0 if window is None else max(0,end-window)
        x=q[beg:end]; y=s[beg+h:end+h]-s[beg:end]
        valid=np.isfinite(x)&np.isfinite(y)
        if np.min(valid.sum(axis=0))<min_train or not np.isfinite(q[t]).all(): continue
        mu=np.nanmean(q[:t+1],axis=0)
        xx=x-mu; xp=xx[:,countries]; yp=y[:,countries]; vp=valid[:,countries]
        beta=np.sum(np.where(vp,xp*yp,0))/np.sum(np.where(vp,xp*xp,0))
        preds['ejr'][t]=beta*(q[t]-mu)
        xm=np.array([x[valid[:,c],c].mean() for c in range(C)])
        ym=np.array([y[valid[:,c],c].mean() for c in range(C)])
        dx=x-xm; dy=y-ym
        beta_fe=np.sum(np.where(vp,dx[:,countries]*dy[:,countries],0))/np.sum(np.where(vp,dx[:,countries]**2,0))
        preds['fe'][t]=ym+beta_fe*(q[t]-xm)
        beta_ols=np.sum(np.where(valid,dx*dy,0),axis=0)/np.sum(np.where(valid,dx*dx,0),axis=0)
        preds['ols'][t]=ym+beta_ols*(q[t]-xm)
        preds['drift'][t]=(s[t-1]-s[0])/(t-1)*h
        preds['ppp'][t]=-(1-2**(-h/60))*(q[t]-mu)
        slopes[t]=[beta,beta_fe,float(np.mean(beta_ols))]
        nobs[t]=int(valid.sum()); last[t]=t-1
    return preds,slopes,nobs,last

def rank_weights(scores,k=2):
    scores=np.asarray(scores,float); w=np.zeros_like(scores)
    for t,a in enumerate(scores):
        if not np.isfinite(a).all(): continue
        # Stable sort makes ties deterministic in fixed ex-ante country order.
        order=np.argsort(a,kind='stable'); w[t,order[:k]]=-.5/k; w[t,order[-k:]]=.5/k
    return w

def run_book(weights, fx, rates, cost_bps=None, borrow_bps=50, execution_lag=1):
    """Returns at row t cover close t-1 -> close t; signal formed t-2.

    USD NAV; foreign assets minus USD funding + collateral cash. Trading costs
    include market drift of existing holdings, initial entry and final liquidation.
    Short interest spread is charged on the opening short notional (FX converted).
    """
    fx=np.asarray(fx,float); rates=np.asarray(rates,float); T,C=fx.shape
    rate_m=(1+rates/100)**(1/12)-1
    spot_ret=np.zeros_like(fx); spot_ret[1:]=fx[:-1]/fx[1:]-1
    rf=np.zeros(T); rf[1:]=rate_m[:-1,-1]
    asset=np.zeros_like(fx); asset[1:]=(1+rate_m[:-1,:C])*(1+spot_ret[1:])-1
    target=np.zeros_like(weights)
    shift=execution_lag+1
    target[shift:]=weights[:-shift]
    costs=np.repeat(2.,C) if cost_bps is None else np.asarray(cost_bps,float)
    nav=1.; prev=np.zeros(C); rows=[]; contributions=[]
    for t in range(T):
        w=target[t]
        turnover=np.abs(w-prev)
        fee=np.sum(turnover*costs/10000)
        spread=np.maximum(-w,0)*(borrow_bps/10000/12)*(1+spot_ret[t])
        contrib=w*(asset[t]-rf[t])-spread
        gross=rf[t]+np.sum(w*(asset[t]-rf[t]))
        ret=rf[t]+contrib.sum()-fee
        if t==T-1:
            liquidation=np.abs(w*(1+asset[t]))
            fee+=np.sum(liquidation*costs/10000)
            ret=rf[t]+contrib.sum()-fee
            turnover+=liquidation
        if 1+ret<=0: raise ValueError('Portfolio insolvent')
        nav*=1+ret
        rows.append([ret,gross,rf[t],fee,spread.sum(),turnover.sum(),nav,np.abs(w).sum()])
        contributions.append(contrib)
        # Pre-trade marked-to-market holdings / current NAV. No cost-free reset.
        prev=w*(1+asset[t])/(1+ret)
    cols=['net','gross','cash','cost','borrow','turnover','nav','gross_exposure']
    return pd.DataFrame(rows,columns=cols),target,np.array(contributions)

def metrics(ret,cash):
    r=np.asarray(ret); cash=np.asarray(cash); n=len(r)
    nav=np.r_[1,np.cumprod(1+r)]; dd=nav/np.maximum.accumulate(nav)-1
    exc=r-cash; vol=np.std(r,ddof=1)*np.sqrt(12)
    sharpe=np.mean(exc)/np.std(exc,ddof=1)*np.sqrt(12) if np.std(exc)>1e-12 else np.nan
    threshold=np.quantile(r,.05)
    underwater=0; max_under=0
    for d in dd:
        underwater=underwater+1 if d < -1e-10 else 0; max_under=max(max_under,underwater)
    return {'n':n,'cagr':nav[-1]**(12/n)-1,'vol':vol,'sharpe':sharpe,'maxdd':dd.min(),
            'mean_excess':np.mean(exc)*12,'worst_month':r.min(),'es95':r[r<=threshold].mean(),
            'win_rate':float(np.mean(r>0)),'max_underwater_months':max_under,'final_nav':nav[-1]}
