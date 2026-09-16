"""Direct multi-horizon regressions with an explicit label-availability clock."""
import numpy as np
import pandas as pd

def fit_predict(A,y,B,penalty=10.,groups=None,newgroups=None,n_groups=1,mode=None,intercept=True):
    mu=A.mean(axis=0);sd=np.maximum(A.std(axis=0),1e-10)
    A=(A-mu)/sd;B=(B-mu)/sd
    if mode=='pca':
        # Last six columns are currency predictors; fit PCA exclusively in training.
        _,_,v=np.linalg.svd(A[:,-6:],full_matrices=False);v=v[0]
        if v.sum()<0:v=-v
        A=np.c_[A[:,:-6],A[:,-6:]@v];B=np.c_[B[:,:-6],B[:,-6:]@v]
    dummy=np.eye(n_groups)[groups,1:] if n_groups>1 else np.empty((len(A),0))
    ndummy=np.eye(n_groups)[newgroups,1:] if n_groups>1 else np.empty((len(B),0))
    if mode=='equilibrium':
        # Constrained equilibrium residual: q conditioned on commodity exposure and FE.
        E=np.c_[np.ones(len(A)),dummy,A[:,1]];N=np.c_[np.ones(len(B)),ndummy,B[:,1]]
        beta=np.linalg.lstsq(E,A[:,0],rcond=None)[0]
        A=(A[:,0]-E@beta)[:,None];B=(B[:,0]-N@beta)[:,None]
    A=np.c_[dummy,A];B=np.c_[ndummy,B]
    if intercept:A=np.c_[np.ones(len(A)),A];B=np.c_[np.ones(len(B)),B]
    reg=np.eye(A.shape[1])*penalty
    # Fixed effects/intercept are nuisance parameters, not penalized.
    reg[:n_groups,:n_groups]=0
    beta=np.linalg.solve(A.T@A+reg,A.T@y)
    return B@beta

def oos(X,Y,h,release=0,penalty=10.,min_dates=60,window=None,mode=None,start=0):
    X=np.asarray(X,float);Y=np.asarray(Y,float)
    if X.ndim==2:X=X[:,None,:]
    if Y.ndim==1:Y=Y[:,None]
    T,C=Y.shape;pred=np.full_like(Y,np.nan);audit=[]
    for t in range(start,T):
        cut=t-h-release # last j=cut-1 -> j+h+release=t-1
        begin=0 if window is None else max(0,cut-window)
        if cut-begin<min_dates:continue
        valid=np.isfinite(X[begin:cut]).all(axis=2)&np.isfinite(Y[begin:cut])
        if np.sum(valid.any(axis=1))<min_dates or np.min(valid.sum(axis=0))<min_dates:continue
        current=np.isfinite(X[t]).all(axis=1)
        if not current.any():continue
        ti,ci=np.where(valid);ti=ti+begin
        latest=int(ti.max()+h+release);assert latest<t
        pred[t,current]=fit_predict(X[ti,ci],Y[ti,ci],X[t,current],penalty,ci,np.flatnonzero(current),C,mode)
        audit.append((t,int(ti.min()),int(ti.max()),latest,len(ti),len(np.unique(ti))))
    return pred,audit

def ejr_extension(X,Y,h,start=0,interaction=False,penalty=0.,window=None):
    """Original pooled/no-intercept EJR restriction, augmented by centered commodities.

    Historical levels are centered at the mean available at the current origin,
    exactly as in the existing EJR replication. No country intercept is added.
    """
    X=np.asarray(X,float);Y=np.asarray(Y,float);T,C=Y.shape
    P=np.full_like(Y,np.nan);audit=[]
    for t in range(start,T):
        cut=t-h;begin=0 if window is None else max(0,cut-window)
        if cut-begin<60 or not np.isfinite(X[t]).all():continue
        mu=np.nanmean(X[:t+1],axis=0);A=X[begin:cut]-mu;B=X[t]-mu
        if interaction:A=np.concatenate([A,(A[:,:,0]*A[:,:,1])[:,:,None]],axis=2);B=np.c_[B,B[:,0]*B[:,1]]
        valid=np.isfinite(A).all(axis=2)&np.isfinite(Y[begin:cut])
        if np.min(valid.sum(axis=0))<60:continue
        ti,ci=np.where(valid);xx=A[ti,ci];yy=Y[begin+ti,ci]
        scale=np.maximum(np.sqrt(np.mean(xx**2,axis=0)),1e-10);xx=xx/scale;bb=B/scale
        if penalty:beta=np.linalg.solve(xx.T@xx+penalty*np.eye(xx.shape[1]),xx.T@yy)
        else:beta=np.linalg.lstsq(xx,yy,rcond=None)[0]
        P[t]=bb@beta
        last=begin+ti.max();assert last+h<t
        audit.append((t,int(begin+ti.min()),int(last),int(last+h),len(ti),len(np.unique(ti))))
    return P,audit
