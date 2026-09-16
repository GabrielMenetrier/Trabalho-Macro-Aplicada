"""Trade extension: full recursive prediction grid; no prior output mutated."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from core import *
from scipy.stats import norm,rankdata
from statsmodels.stats.multitest import multipletests
import statsmodels.api as sm

def hac(x,h):
    x=np.asarray(x);x=x[np.isfinite(x)];L=max(12,h+2)
    if len(x)<max(36,3*L):return np.nan
    return float(sm.OLS(x,np.ones(len(x))).fit(cov_type='HAC',cov_kwds={'maxlags':L,'use_correction':True}).pvalues[0])
def evaluate(task,ps,Y,h,base,binary=False,start='2013-01',family='macro',matched=None):
    common=np.isfinite(Y)&np.isfinite(ps[base])
    rows=[];out=[]
    for period,begin in [('all',start),('late','2019-01')]:
        m=common&(dates>=pd.Period(begin))[:,None]
        for group,ix in [('POOL',list(range(Y.shape[1])))]+([(cc,[i]) for i,cc in enumerate(CC)] if Y.shape[1]==C else []):
            mm=m.copy();mm[:,[j for j in range(Y.shape[1]) if j not in ix]]=False
            for model,p in ps.items():
                bp=ps[base] if matched is None else matched[model]
                paired=mm&np.isfinite(p)&np.isfinite(bp);nd=paired.sum(axis=1);valid=nd>0
                if not valid.any():continue
                loss=(Y-p)**2;b=(Y-bp)**2;zero=Y**2
                dl=np.nansum(np.where(paired,b-loss,np.nan),axis=1)[valid]/nd[valid]
                y=Y[paired];pr=p[paired];auc=np.nan;pos=y>.5
                if binary and pos.any() and (~pos).any():auc=(rankdata(pr)[pos].sum()-pos.sum()*(pos.sum()+1)/2)/(pos.sum()*(~pos).sum())
                rows.append(dict(task=task,family=family,h=h,period=period,country=group,model=model,base=base,n=int(paired.sum()),n_dates=int(valid.sum()),first=str(dates[valid][0]),last=str(dates[valid][-1]),rmse=np.sqrt(loss[paired].mean()),ratio=np.sqrt(loss[paired].mean()/b[paired].mean()),rw=np.sqrt(loss[paired].mean()/zero[paired].mean()) if not binary else np.nan,mean_actual=y.mean(),mean_pred=pr.mean(),auc=auc,p=hac(dl,h) if model!=base else np.nan))
    for model,p in ps.items():
        bp=ps[base] if matched is None else matched[model]
        ti,ci=np.where(common&np.isfinite(p)&np.isfinite(bp)&(dates>=pd.Period(start))[:,None])
        out.extend(dict(task=task,h=h,country=CC[c] if Y.shape[1]==C else 'portfolio',origin=str(dates[t]),model=model,actual=Y[t,c],pred=p[t,c],base_pred=bp[t,c]) for t,c in zip(ti,ci))
    return rows,out

def run():
    D=trade_data();np.savez_compressed(H/'cache/trade.npz',**{k:v for k,v in D.items() if isinstance(v,np.ndarray)})
    save(D['annual_predictions'],'annual_predictions');aud=D['audit'];rows=[];out=[];cache={}
    annual=pd.DataFrame(D['annual_predictions']);ars=[]
    for per,start in [('all',2013),('late',2019)]:
        a=annual[(annual.year>=start)].dropna(subset=['actual','ridge','trend'])
        for name in ['ridge','persistence','trend']:
            ars.append(dict(period=per,model=name,n_years=a.year.nunique(),n=len(a),rmse=np.sqrt(np.mean((a.actual-a[name])**2)),ratio=np.sqrt(np.mean((a.actual-a[name])**2)/np.mean(a.actual**2))))
    save(ars,'annual_metrics')
    fields={'fixed':np.stack([center(D['fixed']),diff(D['fixed'],12)],axis=2),
            'dynamic':np.stack([center(D['chain']),D['momentum']],axis=2),
            'annual':np.stack([center(D['annual']),diff(D['annual'],12)],axis=2),
            'structure':np.stack([D['structure'],D['forecast_structure'],D['repricing']],axis=2)}
    def predict(task,Y,h,baseX,release=0,binary=False,risk=False):
        ps={};matched={};extra={'Base':np.empty((T,Y.shape[1],0))}
        for k,v in fields.items():
            if Y.shape[1]==1:v=np.stack([np.sum(wc*v[:,:,j],axis=1) if k!='structure' else np.sum(np.abs(wc)*v[:,:,j],axis=1) for j in range(v.shape[2])],axis=1)[:,None,:]
            extra[k]=v
        extra['All']=np.concatenate([extra['dynamic'],extra['annual'],extra['structure']],axis=2)
        for name,v in extra.items():
            X=np.concatenate([baseX,v],axis=2)
            if risk:X=X.copy();X[~active]=np.nan
            p,a=oos(X,Y,h,release=release,min_dates=36 if risk else 60,penalty=10)
            BX=baseX.copy();BX[~np.isfinite(X).all(axis=2)]=np.nan
            bp,ba=oos(BX,Y,h,release=release,min_dates=36 if risk else 60,penalty=10)
            if binary:p=np.clip(p,.01,.99)
            if binary:bp=np.clip(bp,.01,.99)
            if 'adverse' in task:p=np.maximum(p,0)
            if 'adverse' in task:bp=np.maximum(bp,0)
            if 'underwater' in task:p=np.clip(p,0,1)
            if 'underwater' in task:bp=np.clip(bp,0,1)
            matched[name]=bp;cache[task+'__Base_for__'+name]=bp
            assert a==ba,'Unequal training dates in nested comparison'
            ps[name]=p;cache[task+'__'+name]=p
            aud.extend(dict(kind=task,model=name,origin=str(dates[t]),first_train=str(dates[first]),last_train=str(dates[last]),last_available=str(dates[end]),n=n,n_dates=nd) for t,first,last,end,n,nd in a)
        r,o=evaluate(task,ps,Y,h,'Base',binary,family='risk' if risk else 'macro',matched=matched);rows.extend(r);out.extend(o);cache[task+'__actual']=Y
        print(task,len(r),flush=True);return ps
    # Separate actual future q from the mixed-release q predictor used by EJR.
    for h in [12,36,60]:
        for typ in ['real','persistent']:
            Y=np.full((T,C),np.nan)
            for t in range(T-h):Y[t]=(qactual[t+h] if typ=='real' else qactual[t+h-11:t+h+1].mean(axis=0))-knownq[t]
            baseX=np.stack([center(knownq),diff(knownq,12)],axis=2)
            predict(f'{typ}_{h}',Y,h,baseX,release=2)
        Y=np.full((T,C),np.nan);Y[:-h]=s[h:]-s[:-h]
        ps={}
        for name,X in [('EJR',q[:,:,None]),('Fixed',np.stack([q,D['G'],center(D['fixed'])],axis=2)),('Dynamic',np.stack([q,D['G'],center(D['chain'])],axis=2))]:
            ps[name],a=ejr_extension(X,Y,h)
            if name=='EJR':ps[name]=forecast(s,q,h)[0]['ejr']
            cache[f'nominal_{h}__{name}']=ps[name]
            aud.extend(dict(kind=f'nominal_{h}',model=name,origin=str(dates[t]),first_train=str(dates[first]),last_train=str(dates[last]),last_available=str(dates[end]),n=n,n_dates=nd) for t,first,last,end,n,nd in a)
        r,o=evaluate(f'nominal_{h}',ps,Y,h,'EJR');rows.extend(r);out.extend(o);cache[f'nominal_{h}__actual']=Y
    # Direct monthly trade-index prediction, generated recursively for second-stage use.
    Y=np.full((T,C),np.nan);Y[:-12]=D['chain'][12:]-D['chain'][:-12]
    X=np.stack([center(D['chain']),D['momentum']],axis=2)
    p,a=oos(X,Y,12,release=1,penalty=10,min_dates=60)
    cache['trade12_forecast']=p;cache['trade12_actual']=Y
    aud.extend(dict(kind='trade12',model='ridge',origin=str(dates[t]),first_train=str(dates[first]),last_train=str(dates[last]),last_available=str(dates[end]),n=n,n_dates=nd) for t,first,last,end,n,nd in a)
    r,o=evaluate('trade12',{'Ridge':p,'Zero':np.zeros_like(p)},Y,12,'Zero');rows.extend(r);out.extend(o)
    fields['structure']=np.concatenate([fields['structure'],p[:,:,None]],axis=2)
    X=np.stack([np.abs(carry),vol,sgn*mom,sgn*ffx],axis=2)
    # Directional price/trade features: a deterioration matters oppositely for shorts.
    for k in ['fixed','dynamic','annual']:fields[k]=fields[k]*sgn[:,:,None]
    fields['structure'][:,:,-1]*=sgn
    for h in [12,36,60]:
        adverse=np.full((T,C),np.nan);under=adverse.copy();erased=adverse.copy()
        for t in range(T-h-1):
            path=np.cumsum(sgn[t]*(carry[t+1:t+h+1]-np.diff(s[t+1:t+h+2],axis=0)),axis=0)
            adverse[t]=-np.minimum(0,path.min(axis=0));under[t]=(path<0).mean(axis=0);erased[t]=(path[-1]<0).astype(float)
        predict(f'adverse_{h}',adverse,h+1,X,risk=True)
        predict(f'underwater_{h}',under,h+1,X,risk=True)
        if h==12:predict('erased_12',erased,h+1,X,binary=True,risk=True)
    b,_,_=run_book(wc*np.where(active,1,0)[:,None],fx,rates,cost_bps=costs)
    exc=(b.net-b.cash).to_numpy();pv=pd.Series(exc).rolling(12).std().to_numpy()
    XX=np.stack([np.sum(wc*carry,axis=1),pv,np.sum(wc*mom,axis=1),np.sum(wc*ffx,axis=1)],axis=1)[:,None,:]
    for h,cutoff in [(1,-.02),(3,-.04)]:
        Y=np.full((T,1),np.nan)
        for t in range(T-h-1):Y[t,0]=np.prod(1+exc[t+2:t+h+2])-1<cutoff
        predict(f'tail_{h}',Y,h+1,XX,binary=True,risk=True)
    M=pd.DataFrame(rows);M['p_holm']=np.nan
    for fam in M.family.unique():
        mask=(M.family==fam)&M.p.notna();M.loc[mask,'p_holm']=multipletests(M.loc[mask,'p'],method='holm')[1]
    save(M,'prediction_metrics');pd.DataFrame(out).to_csv(H/'tables/predictions.csv.gz',index=False,compression='gzip');save(aud,'audit');np.savez_compressed(H/'cache/predictions.npz',**cache)
    print('Metrics',len(M),'predictions',len(out),'fits',len(aud),flush=True)
if __name__=='__main__':run()
