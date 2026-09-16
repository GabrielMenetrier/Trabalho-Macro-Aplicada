from pathlib import Path
import sys,json,hashlib
import numpy as np,pandas as pd
R=Path(__file__).resolve().parents[1];H=R/'ejr_trade_selected'
sys.path.insert(0,str(R/'ejr_trade'))
import run as old
CC=['BRL','EUR','CAD'];IDS=[0,1,4];HH=old.HH;dates=old.dates;T=len(dates)
for f in ['tables','figures','cache','qa']:(H/f).mkdir(exist_ok=True)
raw,_,_=old.inputs();Q=old.Q[:,IDS];S=old.S[:,IDS]
L={k:raw[k+'_l'][:,IDS] for k in ['TOT','COM']};D={k:raw[k+'_d'][:,IDS] for k in ['TOT','COM']}
FORMS=['LOG','DEV','SLOG'];MODELS={'EJR':[]}
for family in ['TOT','COM']:
 for form in FORMS:
  for content in ['L','D','LD']:MODELS[f'{family}_{form}_{content}']=[(family,form,x) for x in content]
for f in FORMS:
 for k in FORMS:MODELS[f'JOINT_{f}_{k}']=[('TOT',f,'L'),('TOT',f,'D'),('COM',k,'L'),('COM',k,'D')]
def transformed(loglevel,logchange,form):
    """Input history ends exactly at the current origin; no full-sample scaling."""
    z=np.exp(loglevel-loglevel.mean(axis=0))
    dev=z/z.mean(axis=0)-1
    if form=='LOG':a=loglevel;b=logchange
    elif form=='DEV':a=dev;b=np.expm1(logchange)
    elif form=='LOG1P':a=np.log1p(dev);b=logchange
    else:
        a=np.sign(dev)*np.log1p(np.abs(dev));d=np.expm1(logchange);b=np.sign(d)*np.log1p(np.abs(d))
    return a-a.mean(axis=0),b-b.mean(axis=0)
def designs(t,q=Q,lev=L,change=D):
    out={'Q':q[:t+1]-q[:t+1].mean(axis=0)}
    for fam in ['TOT','COM']:
        for form in FORMS:
            l,d=transformed(lev[fam][:t+1],change[fam][:t+1],form)
            out[(fam,form,'L')]=l;out[(fam,form,'D')]=d
    return out
def fit_at(t,h,spot=S,q=Q,lev=L,change=D):
    cut=t-h;X=designs(t,q,lev,change);y=spot[h:cut+h]-spot[:cut]
    pp={};bb={}
    for model,extra in MODELS.items():
        columns=['Q']+extra
        a=np.stack([X[k][:cut] for k in columns],axis=2).reshape(-1,len(columns))
        b=np.stack([X[k][t] for k in columns],axis=1)
        coef=np.linalg.lstsq(a,y.ravel(),rcond=None)[0]
        pp[model]=b@coef;bb[model]=coef
    return pp,bb
def evaluate(y,p,h,scenario='fixed',mask=None):
    ok=np.isfinite(y).all(axis=1)&(dates>=pd.Period('2010-01'))
    for v in p.values():ok&=np.isfinite(v).all(axis=1)
    if mask is not None:ok&=mask
    ts=np.flatnonzero(ok);rows=[]
    if not len(ts):return []
    for cc,cols in [('POOL',[0,1,2])]+[(c,[j]) for j,c in enumerate(CC)]:
      yy=y[ts][:,cols];eb=np.mean((yy-p['EJR'][ts][:,cols])**2);rw=np.mean(yy**2)
      for model,v in p.items():
        err=(yy-v[ts][:,cols])**2;mse=err.mean()
        rows.append(dict(h=h,scenario=scenario,country=cc,model=model,first=str(dates[ts[0]]),last=str(dates[ts[-1]]),first_target=str(dates[ts[0]+h]),last_target=str(dates[ts[-1]+h]),n_dates=len(ts),n_obs=yy.size,rmse=np.sqrt(mse),rmse_rw=np.sqrt(mse/rw),rmse_ejr=np.sqrt(mse/eb),r2_ejr=1-mse/eb))
    return rows
def main():
    sys.stdout.reconfigure(encoding='utf-8');metrics=[];predrows=[];aud=[];coeff=[];selection=[];ins=[];checks=[];cache={}
    def check(k,v):checks.append(dict(check=k,passed=bool(v)));assert v,k
    for h in HH:
        y=np.full_like(S,np.nan);y[:-h]=S[h:]-S[:-h]
        p={k:np.full_like(S,np.nan) for k in MODELS}
        for t in range(h+61,T):
            pp,bb=fit_at(t,h)
            for k in p:
                p[k][t]=pp[k]
                coeff.extend(dict(h=h,origin=str(dates[t]),model=k,variable=str(col),beta=float(b)) for col,b in zip(['Q']+MODELS[k],bb[k]))
            aud.append(dict(h=h,origin=str(dates[t]),first_train=str(dates[0]),last_train=str(dates[t-h-1]),last_target=str(dates[t-1]),n_train_dates=t-h))
        for t in np.flatnonzero(np.isfinite(p['EJR']).all(axis=1)&np.isfinite(y).all(axis=1)&(dates>=pd.Period('2010-01'))):
            for j,c in enumerate(CC):predrows.append(dict(h=h,origin=str(dates[t]),target=str(dates[t+h]),country=c,actual=y[t,j],**{k:v[t,j] for k,v in p.items()}))
        metrics+=evaluate(y,p,h)
        metrics+=evaluate(y,p,h,'recent',dates>=pd.Period('2019-01'))
        # Nested chronological choice within each family, including no addition.
        for fam in ['TOT','COM','JOINT','ALL']:
            candidates=['EJR']+[k for k in MODELS if k!='EJR' and (fam=='ALL' or k.startswith(fam+'_'))]
            adaptive=np.full_like(S,np.nan)
            for t in range(h+61,T):
                ix=np.flatnonzero((np.arange(T)+h<t)&(dates>=pd.Period('2010-01'))&np.isfinite(y).all(axis=1)&np.isfinite(p['EJR']).all(axis=1))
                if len(ix)<24:continue
                losses=[np.mean((y[ix]-p[k][ix])**2) for k in candidates]
                chosen=candidates[int(np.argmin(losses))];adaptive[t]=p[chosen][t]
                selection.append(dict(h=h,family=fam,origin=str(dates[t]),selected=chosen,n_validation=len(ix),last_validation_origin=str(dates[ix[-1]]),last_validation_target=str(dates[ix[-1]+h]),past_mse=min(losses)))
            pp={**p,'ADAPTIVE_'+fam:adaptive}
            metrics+=evaluate(y,pp,h,'adaptive_'+fam)
        # Descriptive within-sample country OLS with intercept, all completed labels.
        X=designs(T-1)
        for j,c in enumerate(CC):
            yy=y[:-h,j]
            for model,extra in MODELS.items():
                a=np.c_[np.ones(len(yy)),np.stack([X[k][:-h,j] for k in ['Q']+extra],axis=1)]
                bb=np.linalg.lstsq(a,yy,rcond=None)[0];fitted=a@bb
                r2=1-np.sum((yy-fitted)**2)/np.sum((yy-yy.mean())**2)
                ins.append(dict(h=h,country=c,model=model,r2=r2,adjusted_r2=1-(1-r2)*(len(yy)-1)/(len(yy)-a.shape[1]),n=len(yy),beta_q=bb[1]))
        # Independent earlier estimator for the EJR restricted to this group.
        _,base,_,_=old.estimate(raw,dates,h,{'EJR':['Q']},IDS)
        check(f'Base EJR matches restricted prior estimator h={h}',np.allclose(base['EJR'],p['EJR'],equal_nan=True))
        cache[h]=(y,p)
        print('Completed',h,'months',flush=True)
    for t in [100,180,T-1]:
        for fam in ['TOT','COM']:
            z,d=transformed(L[fam][:t+1],D[fam][:t+1],'LOG');zz,dd=transformed(L[fam][:t+1],D[fam][:t+1],'LOG1P')
            check(f'log(1+deviation) equals centered log {fam} {t}',np.allclose(z,zz,atol=1e-12))
            for form in FORMS:
                z,d=transformed(L[fam][:t+1],D[fam][:t+1],form)
                zz,dd=transformed(L[fam][:t+1]+np.array([2.,5.,8.]),D[fam][:t+1],form)
                check(f'Unit invariance {fam} {form} {t}',np.allclose(z,zz,atol=1e-12) and np.allclose(d,dd,atol=1e-12))
    for h in [36,60,96]:
        t=T-h-2;pp,_=fit_at(t,h,spot=S[:t+1],q=Q[:t+1],lev={k:v[:t+1] for k,v in L.items()},change={k:v[:t+1] for k,v in D.items()})
        for k in MODELS:check(f'Prefix invariant {h} {k}',np.allclose(pp[k],cache[h][1][k][t]))
        sp=S.copy();sp[t+1:]+=123;qq=Q.copy();qq[t+1:]+=777;ll={k:v.copy() for k,v in L.items()};dd={k:v.copy() for k,v in D.items()}
        for k in ll:ll[k][t+1:]+=77;dd[k][t+1:]+=44
        pp,_=fit_at(t,h,sp,qq,ll,dd)
        for k in MODELS:check(f'Future perturbation {h} {k}',np.allclose(pp[k],cache[h][1][k][t]))
    mm=pd.DataFrame(metrics);sel=pd.DataFrame(selection)
    check('Selection uses only completed past targets',(sel.last_validation_target<sel.origin).all())
    check('Selection has >=24 prior validation origins',(sel.n_validation>=24).all())
    check('Training targets always mature',(pd.DataFrame(aud).last_target<pd.DataFrame(aud).origin).all())
    for _,v in mm.groupby(['h','scenario','country']):check('Paired dates '+str(tuple(v.iloc[0][['h','scenario','country']])),v.n_dates.nunique()==1 and v['first'].nunique()==1 and v['last'].nunique()==1)
    winners=[]
    for h in HH:
      for c in ['POOL']+CC:
       v=mm[(mm.h==h)&(mm.scenario=='fixed')&(mm.country==c)]
       for fam in ['TOT','COM','JOINT','ALL']:
        z=v[(v.model!='EJR') & (v.model.str.startswith(fam+'_') if fam!='ALL' else True)]
        b=z.sort_values(['rmse_rw','model']).iloc[0].to_dict();b['family']=fam;winners.append(b)
    for name,v in [('metrics',mm),('audit',aud),('coefficients',coeff),('selection',sel),('in_sample',ins),('winners',winners),('validation',checks)]:pd.DataFrame(v).to_csv(H/'tables'/f'{name}.csv',index=False)
    pd.DataFrame(predrows).to_csv(H/'tables/predictions.csv.gz',index=False)
    np.savez_compressed(H/'cache/data.npz',Q=Q,S=S,**{k+'_L':v for k,v in L.items()},**{k+'_D':v for k,v in D.items()})
    (H/'models.json').write_text(json.dumps(MODELS,indent=2))
    paths=[R/'ejr_trade/run.py',R/'ejr_trade/data/tot_national_accounts_log.csv',R/'third/data/trade_weights.csv',R/'third/data/sector_logprices.csv',R/'data/processed/fx.csv',R/'data/processed/cpi.csv']+list((R/'ejr_trade/data').glob('*.json'))
    (H/'input_hashes.json').write_text(json.dumps({str(p.relative_to(R)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths},indent=2))
    print('\nBest additions at five years:')
    print(pd.DataFrame(winners).query('h==60')[['country','family','model','rmse_rw','rmse_ejr']].to_string(index=False))
    print('\nChecks:',len(checks),'passed')
if __name__=='__main__':main()
