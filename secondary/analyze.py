"""All twelve exploratory extensions. Original inputs and output remain read-only."""
from pathlib import Path
import sys, os, json
ROOT=Path(__file__).resolve().parents[1]; HERE=ROOT/'secondary'
sys.path.insert(0,str(ROOT/'src'))
os.environ['MPLCONFIGDIR']=str(ROOT/'tmp/matplotlib')
import numpy as np
import pandas as pd
from scipy.stats import norm, rankdata
import statsmodels.api as sm
from statsmodels.stats.multitest import multipletests
from models import features,forecast,rank_weights,run_book,metrics

CC=['BRL','EUR','JPY','GBP','CAD','SEK']; SEED=20260910
for d in ['tables','figures','cache']: (HERE/d).mkdir(exist_ok=True)
def read(name):
    p=ROOT/'data/processed'/f'{name}.csv'
    a=pd.read_csv(p,index_col=0); a.index=pd.PeriodIndex(a.index,freq='M'); return a.sort_index()
def save(a,name):
    pd.DataFrame(a).to_csv(HERE/'tables'/f'{name}.csv',index=False,float_format='%.10g')
fx=read('fx')[CC].loc['1999-10':'2026-08']; dates=fx.index; T,C=fx.shape
cpi=read('cpi').reindex(dates); rates=read('rates').reindex(dates)[CC+['USD']]
assert fx.notna().all().all() and rates.notna().all().all()
s=np.log(fx.to_numpy()); q=features(fx,cpi).to_numpy()
# Original analysis forms q before truncating the sample, retaining released CPI at start.
q=features(read('fx')[CC],read('cpi')).reindex(dates).to_numpy()
rm=np.expm1(np.log1p(rates.to_numpy()/100)/12)
carry=np.log1p(rm[:,:C])-np.log1p(rm[:,-1,None])
F={}; audit=[]
for h in [12,36,60,96]:
    p,b,n,last=forecast(s,q,h); F[h]=p['ejr']
    for t in np.flatnonzero(n):
        audit.append(dict(kind='EJR',h=h,origin=str(dates[t]),last_label=str(dates[last[t]]),n=int(n[t])))
f=F[60]; ffx=-f/60; score=carry+ffx
qdev=q-pd.DataFrame(q).expanding().mean().to_numpy()
mom=-pd.DataFrame(s).diff(12).to_numpy()/12
vol=pd.DataFrame(-np.diff(s,axis=0,prepend=s[[0]])).rolling(12,min_periods=12).std().to_numpy()
active=(dates>=pd.Period('2010-01')) & np.isfinite(f).all(axis=1)
wc=rank_weights(carry); aggfx=np.sum(wc*ffx,axis=1); agg=np.sum(wc*score,axis=1)
books={}; weights={}; strategy_info={}; costs=np.array([10,2,2,2,2,3])
def add(name,w,family,start='2010-03',cost=1):
    w=np.nan_to_num(w,nan=0.); w[~active]=0
    b,target,contrib=run_book(w,fx,rates,cost_bps=costs*cost)
    b.index=dates; books[name]=b; weights[name]=w
    strategy_info[name]={'family':family,'start':start,'cost_multiple':cost}
    return b

add('Carry',wc.copy(),0); add('EJR_rank',rank_weights(score),0)
add('Gate_FX',wc*(aggfx>0)[:,None],1)
add('Gate_total',wc*(agg>0)[:,None],1)
pairw=np.zeros((T,C)); pairfx=np.zeros_like(pairw)
for t in range(T):
    order=np.argsort(carry[t],kind='stable')
    for lo,hi in zip(order[:2],order[-2:][::-1]):
        if score[t,hi]>score[t,lo]: pairw[t,hi]=.25; pairw[t,lo]=-.25
        if ffx[t,hi]>ffx[t,lo]: pairfx[t,hi]=.25; pairfx[t,lo]=-.25
add('Pair_total',pairw,2); add('Pair_FX',pairfx,2)
den=pd.Series(agg).shift(1).expanding(min_periods=24).median().to_numpy()
scale=np.clip(agg/np.maximum(den,.0001),0,1)
add('Size_signal',wc*scale[:,None],3)
portfx=np.sum(np.roll(wc,2,axis=0)*np.vstack([np.zeros(C),np.exp(s[:-1]-s[1:])-1]),axis=1)
pvol=pd.Series(portfx).rolling(12,min_periods=12).std().to_numpy()*np.sqrt(12)
vscale=np.clip(.04/np.maximum(pvol,.005),0,1)
add('Size_vol',wc*vscale[:,None],3)
add('Size_signal_vol',wc*(scale*vscale)[:,None],3)
# Agreement: preserve the same common history and identical risk budget.
common=np.isfinite(np.stack(list(F.values()))).all(axis=(0,2))&active
hsign=np.stack([np.sum(wc*(-F[h]/h),axis=1)>0 for h in F])
add('Agree_all',wc*(hsign.all(axis=0)&common)[:,None],7,'2013-01')
add('Agree_3of4',wc*((hsign.sum(axis=0)>=3)&common)[:,None],7,'2013-01')
save([dict(h=h,n=int(common.sum()),agreement_with_60=float(np.mean((F[h][common]>0)==(f[common]>0)))) for h in F],'horizon_agreement')
# Cohorts are funded with a fixed 1/12 NAV budget; early exits stay in cash until expiry.
def cohorts(rule,tenure=12):
    out=np.zeros_like(wc); alive=[]
    for t in range(T):
        if not active[t]: continue
        alive=[(j,w) for j,w in alive if t-j<tenure]
        alive.append((t,wc[t].copy()))
        keep=[]
        for j,w in alive:
            advantage=np.dot(w,score[t]); original=np.dot(w,score[j])
            valid= rule=='fixed' or (advantage>0 if rule=='total' else advantage*original>0)
            if valid: keep.append((j,w)); out[t]+=w/tenure
        alive=keep
    return out
for rule in ['fixed','total','reversal']: add('Exit_'+rule,cohorts(rule),8)
# Extremes: filter original carry pairs, separately inspecting high/low legs.
quant=np.full_like(qdev,np.nan)
for t in range(60,T):
    quant[t]=np.mean(qdev[:t]<=qdev[t],axis=0)
extreme=np.zeros_like(wc); cheap=np.zeros_like(wc); avoid=np.zeros_like(wc)
for t in range(T):
    order=np.argsort(carry[t],kind='stable')
    for lo,hi in zip(order[:2],order[-2:][::-1]):
        # Positive q means cheap foreign currency (local units/USD).
        for dest,ok in [(extreme,quant[t,hi]>.7 and quant[t,lo]<.3),(cheap,quant[t,hi]>.7),(avoid,quant[t,lo]<.3)]:
            if ok: dest[t,hi]=.25; dest[t,lo]=-.25
add('Extreme_both',extreme,9); add('Extreme_long',cheap,9); add('Extreme_short',avoid,9)
add('Gate_raw_q',wc*(np.sum(wc*qdev,axis=1)>0)[:,None],9)
# Matching exposure using only previous signals, plus full-sample match as descriptive control.
for name in ['Gate_FX','Gate_total','Pair_total','Pair_FX','Size_signal','Extreme_long','Extreme_short']:
    exposure=np.abs(weights[name]).sum(axis=1)
    past=pd.Series(np.where(active,exposure,np.nan)).expanding(min_periods=1).mean().shift(1).fillna(0).to_numpy()
    add(name+'_past_exposure',wc*past[:,None],90)
    mean=exposure[active].mean()
    add(name+'_expost_exposure',wc*mean,91)

def hac_diff(d,h):
    a=np.asarray(d); a=a[np.isfinite(a)]
    if len(a)<max(36,3*h):return float(a.mean()) if len(a) else np.nan,np.nan,np.nan
    fit=sm.OLS(a,np.ones(len(a))).fit(cov_type='HAC',cov_kwds={'maxlags':h,'use_correction':True})
    return float(fit.params[0]),float(fit.bse[0]),float(fit.pvalues[0])

predrows=[]; score_rows=[]; pred_audit=[]
def predict_task(task,X,Y,h,binary=False,release=0):
    """X base + one EJR column + one raw-q column. Equal train/evaluation rows."""
    X=np.asarray(X); Y=np.asarray(Y); K=X.shape[-1]; nc=X.shape[1]
    valid=np.isfinite(X).all(axis=2)&np.isfinite(Y)
    predicted={k:np.full_like(Y,np.nan) for k in ['base','ejr','q']}
    for t in range(T):
        if not active[t]:continue
        # Y[j] uses realized returns j+2,...,j+h+1; CPI adds publication delay.
        cut=t-h-1-release # exclusive, j+h+1+release <= t-1
        if cut<=0:continue
        vi=valid[:cut]&active[:cut,None]
        if np.sum(vi.any(axis=1))<36 or vi.sum()<max(36,100 if nc>1 else 36):continue
        now=np.isfinite(X[t]).all(axis=1)
        if not now.any():continue
        tt,cc=np.where(vi)
        y=Y[tt,cc]; latest=int(tt.max()+h+1+release)
        assert latest<t
        for model,cols in [('base',list(range(K-2))),('ejr',list(range(K-1))),('q',list(range(K-2))+[K-1])]:
            a=X[tt,cc][:,cols]; b=X[t,now][:,cols]
            mu=a.mean(axis=0); sd=np.maximum(a.std(axis=0),1e-8)
            a=(a-mu)/sd; b=(b-mu)/sd
            # Country intercepts; no separate independent-country significance claims.
            if nc>1:
                a=np.c_[a,np.eye(nc)[cc,1:]]; b=np.c_[b,np.eye(nc)[np.flatnonzero(now),1:]]
            a=np.c_[np.ones(len(a)),a]; b=np.c_[np.ones(len(b)),b]
            pen=np.eye(a.shape[1])*10.; pen[0,0]=0
            beta=np.linalg.solve(a.T@a+pen,a.T@y)
            pr=b@beta
            if binary:pr=np.clip(pr,.01,.99)
            if 'adverse' in task:pr=np.maximum(pr,0)
            if 'underwater' in task:pr=np.clip(pr,0,1)
            predicted[model][t,now]=pr
        pred_audit.append(dict(task=task,origin=str(dates[t]),last_label_available=str(dates[latest]),n_train=len(y),n_train_dates=len(np.unique(tt))))
    commonp=np.isfinite(Y)&np.isfinite(predicted['ejr'])&np.isfinite(predicted['base'])&np.isfinite(predicted['q'])
    ti,ci=np.where(commonp)
    for model,P in predicted.items():
        for t,c in zip(ti,ci):predrows.append(dict(task=task,h=h,origin=str(dates[t]),country=CC[c] if nc==6 else 'portfolio',model=model,actual=Y[t,c],pred=P[t,c],binary=binary))
        for period,start in [('all','2010-01'),('late','2019-01')]:
            m=commonp&(dates>=pd.Period(start))[:,None]
            if not m.any():continue
            y=Y[m]; p=P[m]; base=predicted['base'][m]; loss=(y-p)**2
            d=np.where(m,(Y-predicted['base'])**2-(Y-P)**2,np.nan)
            nd=np.sum(m,axis=1); daily=np.nansum(d,axis=1)[nd>0]/nd[nd>0]
            gain,se,pval=hac_diff(daily,max(h,12))
            pos=y>0.5; auc=np.nan
            if binary and pos.any() and (~pos).any():auc=(rankdata(p)[pos].sum()-pos.sum()*(pos.sum()+1)/2)/(pos.sum()*(~pos).sum())
            score_rows.append(dict(task=task,h=h,period=period,model=model,n=len(y),n_dates=int(np.sum(nd>0)),first=str(dates[np.flatnonzero(nd)[0]]),last=str(dates[np.flatnonzero(nd)[-1]]),mse=loss.mean(),rmse_ratio=np.sqrt(loss.mean()/np.mean((y-base)**2)),gain=gain,se=se,p=pval,auc=auc,event_rate=y.mean() if binary else np.nan))
    return predicted

# 4. Does adverse FX exceed the accumulated interest advantage?
sgn=np.sign(carry); Y=np.full((T,C),np.nan)
for t in range(T-13):
    fxlog=-(s[t+13]-s[t+1]); interest=carry[t+1:t+13].sum(axis=0)
    Y[t]=(sgn[t]*fxlog < -sgn[t]*interest).astype(float)
X=np.stack([np.abs(carry),vol,sgn*mom,sgn*ffx,sgn*qdev],axis=2)
predict_task('04_carry_erased',X,Y,12,True)
# 5. Fixed, economically interpretable tail thresholds; labels contain actual costs.
bcarry=books['Carry']; exc=(bcarry.net-bcarry.cash).to_numpy()
aggvol=pd.Series(exc).rolling(12).std().to_numpy()
XX=np.stack([np.sum(wc*carry,axis=1),aggvol,np.sum(wc*mom,axis=1),aggfx,np.sum(wc*qdev,axis=1)],axis=1)[:,None,:]
for h,threshold in [(1,-.02),(3,-.04)]:
    y=np.full((T,1),np.nan)
    for t in range(T-h-1):y[t,0]=(np.prod(1+exc[t+2:t+h+2])-1)<threshold
    predict_task(f'05_tail_{h}',XX,y,h,True)
# 6. Each currency's opening carry direction is held fixed through the path.
for h in [12,36,60]:
    adverse=np.full((T,C),np.nan); underwater=adverse.copy()
    for t in range(T-h-1):
        daily=sgn[t]*(carry[t+1:t+h+1]-np.diff(s[t+1:t+h+2],axis=0))
        path=np.cumsum(daily,axis=0)
        adverse[t]=-np.minimum(0,path.min(axis=0)); underwater[t]=(path<0).mean(axis=0)
    predict_task(f'06_adverse_{h}',X,adverse,h)
    predict_task(f'06_underwater_{h}',X,underwater,h)
# 11. Future relative CPI inflation; no updated historical prices enter predictors.
P=np.log(cpi[CC].to_numpy())-np.log(cpi.USD.to_numpy())[:,None]
pastinfl=pd.DataFrame(P).diff(12).shift(2).to_numpy()/12
XI=np.stack([pastinfl,carry,mom,ffx,qdev],axis=2)
for h in [12,36,60]:
    y=np.full((T,C),np.nan)
    for t in range(T-h-1):y[t]=(P[t+h+1]-P[t+1])/h*12
    predict_task(f'11_inflation_{h}',XI,y,h,release=2)
# 12. Outcomes in BRL, removing mechanical currency conversion.
assets=pd.read_csv(HERE/'data/assets.csv',index_col=0); assets.index=pd.PeriodIndex(assets.index,freq='M')
assets=assets.reindex(dates); ar=assets.pct_change(fill_method=None)
brcash=np.r_[np.nan,rm[:-1,0]]
marketmom=np.log(assets['BOVA11.SA']).diff(12).to_numpy()/12
asset_targets={'bond':ar['IMAB11.SA'].to_numpy()-brcash,
               'exporter_bank':ar['VALE3.SA'].to_numpy()-ar['ITUB4.SA'].to_numpy(),
               'exporter_bank_alt':ar['SUZB3.SA'].to_numpy()-ar['BBAS3.SA'].to_numpy()}
for target,r in asset_targets.items():
    ownmom=pd.Series(r).rolling(12).mean().to_numpy()
    xa=np.stack([carry[:,0],pastinfl[:,0],marketmom,ownmom,ffx[:,0],qdev[:,0]],axis=1)[:,None,:]
    for h in [1,12]:
        y=np.full((T,1),np.nan)
        for t in range(T-h-1):
            vals=r[t+2:t+h+2]
            if np.isfinite(vals).all():y[t,0]=vals.sum() # additive return spread, not a compounded wealth index
        predict_task(f'12_{target}_{h}',xa,y,h)
# 10. Underlying US asset is held continuously; monthly forward hedges opening USD notional.
etf=read('etf_adjusted_close').reindex(dates)
usdasset=etf.pct_change(fill_method=None)
spot=np.exp(s[:,0]); ratio=np.r_[1,spot[1:]/spot[:-1]]
forward=np.r_[1,(1+rm[:-1,0])/(1+rm[:-1,-1])]
hedges={'None':np.zeros(T),'Half':np.full(T,.5),'Full':np.ones(T),
        'FX':(f[:,0]<0).astype(float),'Total':(f[:,0]/60 < carry[:,0]).astype(float)}
hedge_books={}; hedge_rows=[]
for asset in ['BIL','SPY']:
    for name,H in hedges.items():
        applied=np.zeros(T); applied[2:]=H[:-2]
        r=(1+usdasset[asset].to_numpy())*ratio-1+applied*(forward-ratio)-applied*.0002
        mask=(dates>=pd.Period('2010-03'))&np.isfinite(r)
        rr=r[mask].copy(); rr[0]-=.0012; rr[-1]-=.0012*(1+rr[-1])
        rrfull=r.copy(); rrfull[np.flatnonzero(mask)]=rr
        hedge_books[asset+'_'+name]=rrfull
        for period,start in [('all','2010-03'),('late','2019-01')]:
            m=mask&(dates>=pd.Period(start)); vals=rrfull[m]
            hedge_rows.append(dict(asset=asset,rule=name,period=period,mean_hedge=applied[m].mean(),**metrics(vals,brcash[m])))
save(hedge_rows,'hedge_metrics'); save(pd.DataFrame(hedge_books).assign(month=dates.astype(str)),'hedge_returns')

def summarize_books():
    rows=[]; returns=[]
    for name,b in books.items():
        for period,start in [('all',strategy_info[name]['start']),('late','2019-01')]:
            m=dates>=pd.Period(max(start,strategy_info[name]['start']))
            rows.append(dict(strategy=name,period=period,**strategy_info[name],**metrics(b.net[m],b.cash[m]),exposure=b.gross_exposure[m].mean(),cost_ann=b.cost[m].mean()*12,turnover_ann=b.turnover[m].mean()*12))
        for t in np.flatnonzero(dates>=pd.Period('2010-03')):
            returns.append(dict(strategy=name,month=str(dates[t]),**b.iloc[t].to_dict()))
    save(rows,'strategy_metrics'); save(returns,'strategy_returns')
summarize_books()
scores=pd.DataFrame(score_rows)
adjust=(scores.model!='base')&scores.p.notna()
scores['p_holm']=np.nan; scores.loc[adjust,'p_holm']=multipletests(scores.loc[adjust,'p'],method='holm')[1]
save(scores,'prediction_metrics'); save(predrows,'prediction_observations'); save(pred_audit,'prediction_audit'); save(audit,'ejr_audit')
save(pd.DataFrame({'month':dates.astype(str),'aggregate_fx':aggfx,'aggregate_total':agg,'raw_q':np.sum(wc*qdev,axis=1),'vol':pvol}),'aggregate_signals')
np.savez_compressed(HERE/'cache/core.npz',dates=dates.astype(str).to_numpy(dtype=str),fx=fx.to_numpy(),rates=rates.to_numpy(),wc=wc,f=f,ffx=ffx,score=score,qdev=qdev,carry=carry,active=active,agg=agg,aggfx=aggfx,vol=pvol)
print('Completed 12 families:',len(books),'strategies;',len(scores),'predictive comparisons;',len(predrows),'prediction rows.')
print(pd.read_csv(HERE/'tables/strategy_metrics.csv').query("period=='all' and family<90")[['strategy','cagr','sharpe','maxdd','exposure']].to_string(index=False))
print(scores.query("model=='ejr' and period=='all'")[['task','n_dates','rmse_ratio','p','p_holm']].to_string(index=False))
