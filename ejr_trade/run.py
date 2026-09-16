"""Reproducible paired EJR forecasting extensions. No portfolio code."""
from pathlib import Path
import sys,json,hashlib,warnings,os
import numpy as np
import pandas as pd
from scipy.stats import norm
from statsmodels.stats.multitest import multipletests
R=Path(__file__).resolve().parents[1]; H=R/'ejr_trade'
sys.path.insert(0,str(R/'src'))
from models import features,forecast
CC=['BRL','EUR','JPY','GBP','CAD','SEK']; ISO=['BRA','DEU','JPN','GBR','CAN','SWE']
HH=[12,24,36,48,60,72,84,96]; SECT=['energy','food','raw','metals']
for f in ['tables','figures','cache']:(H/f).mkdir(exist_ok=True)
def read(p):
    a=pd.read_csv(p,index_col=0);a.index=pd.PeriodIndex(a.index,freq='M');return a
FX=read(R/'data/processed/fx.csv')[CC]; CPI=read(R/'data/processed/cpi.csv')
dates=FX.loc['1999-10':'2026-08'].index; T=len(dates)
S=np.log(FX.reindex(dates).to_numpy()); Q=features(FX,CPI).reindex(dates).to_numpy()
def annual(ind):
    a=json.loads((H/'data'/f'{ind}.json').read_text())
    out=pd.DataFrame([dict(year=int(x['date']),iso=x['countryiso3code'],value=x['value']) for x in a[1]])
    return out.pivot(index='year',columns='iso',values='value').reindex(columns=ISO)
A={k:annual(k) for k in ['NE.EXP.GNFS.CN','NE.EXP.GNFS.KN','NE.IMP.GNFS.CN','NE.IMP.GNFS.KN','TT.PRI.MRCH.XD.WD']}
TOT=np.log(A['NE.EXP.GNFS.CN']/A['NE.EXP.GNFS.KN'])-np.log(A['NE.IMP.GNFS.CN']/A['NE.IMP.GNFS.KN'])
MER=np.log(A['TT.PRI.MRCH.XD.WD'])
weights=pd.read_csv(R/'third/data/trade_weights.csv')
def weight(col):return weights.pivot(index='currency',columns='sector',values=col).reindex(index=CC,columns=SECT).to_numpy()
W=weight('export_share')-weight('import_share'); LEGACY=weight('net_weight')
B=read(R/'third/data/sector_logprices.csv')[SECT]
REAL=B.sub(np.log(CPI.USD.ffill(limit=1)),axis=0)
def annual_known(a,delay=2):
    lev=np.full((T,6),np.nan);chg=lev.copy();src=lev.copy()
    for t,d in enumerate(dates):
        yr=d.year-delay
        if yr in a.index:
            lev[t]=a.loc[yr];src[t]=np.where(np.isfinite(lev[t]),yr,np.nan)
            if yr-1 in a.index:chg[t]=a.loc[yr]-a.loc[yr-1]
    return lev,chg,src
def inputs(delay=2,price_lag=2):
    l,d,src=annual_known(TOT,delay);ml,md,msrc=annual_known(MER,delay)
    p=REAL.shift(price_lag).reindex(dates).to_numpy()@W.T
    dp=REAL.diff(12).shift(price_lag).reindex(dates).to_numpy()@W.T
    leg=REAL.shift(price_lag).reindex(dates).to_numpy()@LEGACY.T
    dlg=REAL.diff(12).shift(price_lag).reindex(dates).to_numpy()@LEGACY.T
    return dict(Q=Q,TOT_l=l,TOT_d=d,COM_l=p,COM_d=dp,LEG_l=leg,LEG_d=dlg,MER_l=ml,MER_d=md),src,msrc
MODELS={'EJR':['Q'],'TOT_level':['Q','TOT_l'],'TOT_change':['Q','TOT_d'],'TOT_both':['Q','TOT_l','TOT_d'],
        'COM_level':['Q','COM_l'],'COM_change':['Q','COM_d'],'COM_both':['Q','COM_l','COM_d'],
        'JOINT':['Q','TOT_l','TOT_d','COM_l','COM_d'],'LEGACY':['Q','LEG_l','LEG_d']}
PRIMARY=['EJR','TOT_both','COM_both']
def estimate(inp,months,h,models=MODELS,countries=None,quarterly=False,keep_audit=True,spot=None):
    """Use common training mask for all requested models; center at current t."""
    ids=list(range(6)) if countries is None else countries
    spot=S if spot is None else spot
    N=len(months); ss=spot[:N,ids]; x={k:v[:N,ids] for k,v in inp.items()}
    y=np.full_like(ss,np.nan);y[:-h]=ss[h:]-ss[:-h]
    used=list(dict.fromkeys(k for cols in models.values() for k in cols))
    admissible=np.isfinite(np.stack([x[k] for k in used],axis=2)).all(axis=2)
    pred={m:np.full_like(ss,np.nan) for m in models}; audits=[];coefs=[]
    minimum=20 if quarterly else 60
    sample=np.array([d.month in (3,6,9,12) for d in months]) if quarterly else np.ones(N,bool)
    for t in range(h+1,N):
        if not quarterly and t<h+61:continue  # Preserve original project start convention.
        if not sample[t] or not admissible[t].all():continue
        cut=t-h
        valid=admissible[:cut]&np.isfinite(y[:cut])&sample[:cut,None]
        if valid.sum(axis=0).min()<minimum:continue
        ti,ci=np.where(valid)
        means={k:np.nanmean(x[k][:t+1],axis=0) for k in used}
        for m,cols in models.items():
            xx=np.stack([x[k][ti,ci]-means[k][ci] for k in cols],axis=1)
            new=np.stack([x[k][t]-means[k] for k in cols],axis=1)
            beta=np.linalg.lstsq(xx,y[ti,ci],rcond=None)[0]
            pred[m][t]=new@beta
            if keep_audit:
                coefs.extend(dict(h=h,model=m,origin=str(months[t]),variable=k,beta=float(b)) for k,b in zip(cols,beta))
        if keep_audit:
            audits.append(dict(h=h,origin=str(months[t]),first_train=str(months[ti.min()]),last_train=str(months[ti.max()]),last_target=str(months[ti.max()+h]),n_dates=len(np.unique(ti)),n_obs=len(ti),n_years=len(np.unique(months[ti].year))))
        assert ti.max()+h<t
    return y,pred,audits,coefs

def hac_p(loss,h,step=1):
    n=len(loss);lags=int(np.ceil((h+2)/step))
    if n<max(36/step,3*lags):return np.nan
    z=loss-loss.mean();v=z@z/n
    for k in range(1,lags+1):v+=2*(1-k/(lags+1))*(z[k:]@z[:-k])/n
    return float(2*norm.sf(abs(loss.mean())/np.sqrt(v/n))) if v>0 else np.nan

def score(y,p,months,h,scenario,ids,periods=True,step=1):
    rows=[]; common=np.isfinite(y).all(axis=1)
    for v in p.values():common&=np.isfinite(v).all(axis=1)
    common&=months>=pd.Period('2010-01')
    subsets={'all':common}
    if periods:
        subsets['late']=common&(months>=pd.Period('2019-01'))
        subsets['same_origins']=common&(months>=pd.Period('2012-11'))&(months<=pd.Period('2018-08'))
    for period,mask in subsets.items():
        ts=np.flatnonzero(mask)
        if not len(ts):continue
        for group,cols in [('POOL',list(range(len(ids))))]+[(CC[c],[j]) for j,c in enumerate(ids)]:
            yy=y[ts][:,cols];base=p['EJR'][ts][:,cols];rw=np.mean(yy**2)
            for m in ['RW']+list(p):
                pr=np.zeros_like(yy) if m=='RW' else p[m][ts][:,cols]
                mse=np.mean((yy-pr)**2);bse=np.mean((yy-base)**2)
                loss=((yy-base)**2-(yy-pr)**2).mean(axis=1)
                rows.append(dict(scenario=scenario,period=period,h=h,country=group,model=m,n_dates=len(ts),n_obs=yy.size,first=str(months[ts[0]]),last=str(months[ts[-1]]),first_target=str(months[ts[0]+h]),last_target=str(months[ts[-1]+h]),blocks=len(ts)*step/h,rmse=float(np.sqrt(mse)),rmse_rw=float(np.sqrt(mse/rw)),rmse_ejr=float(np.sqrt(mse/bse)),r2_ejr=float(1-mse/bse),hit=float(np.mean(np.sign(pr)==np.sign(yy))),p_hac=hac_p(loss,h,step)))
    return rows

def main():
    sys.stdout.reconfigure(encoding='utf-8')
    files=[R/'src/models.py',R/'third/data/trade_weights.csv',R/'third/data/sector_logprices.csv',R/'data/processed/fx.csv',R/'data/processed/cpi.csv']+list((H/'data').glob('*.json'))
    hashes={str(f.relative_to(R)):hashlib.sha256(f.read_bytes()).hexdigest() for f in files}
    (H/'input_hashes.json').write_text(json.dumps(hashes,indent=2))
    inp,src,msrc=inputs();out=[];aud=[];coef=[];predrows=[];cache={};checks=[];nonoverlap=[]
    def check(name,ok):checks.append(dict(check=name,passed=bool(ok)));assert ok,name
    check('All main predictors available from start',all(np.isfinite(inp[k]).all() for k in dict.fromkeys(k for v in MODELS.values() for k in v)))
    check('Annual source year <= origin year minus two',np.all(src<=dates.year.to_numpy()[:,None]-2))
    check('Fixed weights precede sample',weights.last_year.max()<dates[0].year)
    for h in HH:
        y,p,a,c=estimate(inp,dates,h);cache[h]=(y,p)
        out+=score(y,p,dates,h,'main',list(range(6)))
        aud.extend(dict(scenario='main',**r) for r in a);coef.extend(c)
        old=forecast(S,Q,h)[0]['ejr']
        check(f'EJR availability matches existing implementation h={h}',np.array_equal(np.isfinite(old),np.isfinite(p['EJR'])))
        mask=np.isfinite(old)&np.isfinite(p['EJR'])
        check(f'EJR reproduces existing implementation h={h}',np.allclose(old[mask],p['EJR'][mask],atol=1e-11))
        mask=np.isfinite(y)&np.isfinite(p['EJR']);mask[dates<pd.Period('2010-01')]=False
        for t,ci in zip(*np.where(mask)):
            predrows.append(dict(h=h,origin=str(dates[t]),target=str(dates[t+h]),country=CC[ci],actual=y[t,ci],**{m:p[m][t,ci] for m in p}))
        ts=np.flatnonzero(mask.all(axis=1))
        for offset in range(h):
            ix=ts[offset::h]
            if len(ix)<2:continue
            for m in ['TOT_both','COM_both']:
                r=np.sqrt(np.mean((y[ix]-p[m][ix])**2)/np.mean((y[ix]-p['EJR'][ix])**2))
                nonoverlap.append(dict(h=h,offset=offset,model=m,n_dates=len(ix),rmse_ejr=r))
        print('Main horizon',h,'months complete',flush=True)
    scenarios=[('late_release',list(range(6)),False,inputs(3,3)[0]),('no_BRL',[1,2,3,4,5],False,inp),('no_EUR',[0,2,3,4,5],False,inp),('no_BRL_EUR',[2,3,4,5],False,inp),('quarterly',list(range(6)),True,inp)]
    for name,ids,quarterly,xx in scenarios:
        for h in HH:
            y,p,a,_=estimate(xx,dates,h,{k:MODELS[k] for k in PRIMARY},ids,quarterly)
            out+=score(y,p,dates,h,name,ids,periods=False,step=3 if quarterly else 1)
            aud.extend(dict(scenario=name,**r) for r in a)
        print('Sensitivity',name,'complete',flush=True)
    mm={'EJR':['Q'],'MER_level':['Q','MER_l'],'MER_change':['Q','MER_d'],'MER_both':['Q','MER_l','MER_d']}
    for h in HH:
        y,p,a,_=estimate(inp,dates,h,mm)
        out+=score(y,p,dates,h,'merchandise',list(range(6)),periods=False)
        aud.extend(dict(scenario='merchandise',**r) for r in a)
    # In-sample regressions by currency, with intercept as in descriptive eq. (3.2).
    ins=[]
    for h in HH:
        y=cache[h][0]
        for ci,cc in enumerate(CC):
            for m in PRIMARY:
                xx=np.stack([inp[k][:,ci] for k in MODELS[m]],axis=1)
                mask=np.isfinite(y[:,ci])&np.isfinite(xx).all(axis=1)
                xx=np.c_[np.ones(mask.sum()),xx[mask]];yy=y[mask,ci]
                beta=np.linalg.lstsq(xx,yy,rcond=None)[0];ssr=np.sum((yy-xx@beta)**2);sst=np.sum((yy-yy.mean())**2)
                ins.append(dict(h=h,country=cc,model=m,n=len(yy),first=str(dates[np.flatnonzero(mask)[0]]),last=str(dates[np.flatnonzero(mask)[-1]]),r2=1-ssr/sst,adjusted_r2=1-(ssr/(len(yy)-xx.shape[1]))/(sst/(len(yy)-1)),beta_q=beta[1]))
    # Future perturbation tests check centering, fitting and all primary forecasts.
    for h in [12,60,96]:
        t=T-h-2
        y,p,_,_=estimate(inp,dates[:t+1],h,keep_audit=False,spot=S[:t+1])
        for m in MODELS:check(f'Truncation {m} h={h}',np.allclose(p[m][t],cache[h][1][m][t],atol=1e-12,equal_nan=True))
        changed={k:v.copy() for k,v in inp.items()}
        for k in changed:changed[k][t+1:]+=777
        sp=S.copy();sp[t+1:]+=888
        _,p,_,_=estimate(changed,dates,h,keep_audit=False,spot=sp)
        for m in MODELS:check(f'Future perturbation {m} h={h}',np.allclose(p[m][t],cache[h][1][m][t],atol=1e-12,equal_nan=True))
    metrics=pd.DataFrame(out);metrics['p_holm']=np.nan
    family=(metrics.scenario=='main')&(metrics.period=='all')&(metrics.country=='POOL')&metrics.model.isin(['TOT_both','COM_both'])
    # Family includes untestable horizons as p=1, so no silent reduction of multiplicity.
    metrics.loc[family,'p_holm']=multipletests(metrics.loc[family,'p_hac'].fillna(1),method='holm')[1]
    metrics.loc[family&metrics.p_hac.isna(),'p_holm']=np.nan
    for name,values in [('metrics',metrics),('audit',aud),('coefficients',coef),('nonoverlap',nonoverlap),('in_sample',ins)]:pd.DataFrame(values).to_csv(H/'tables'/f'{name}.csv',index=False)
    pd.DataFrame(predrows).to_csv(H/'tables/predictions.csv.gz',index=False)
    known=[]
    for t,dt in enumerate(dates):
        for ci,cc in enumerate(CC):known.append(dict(origin=str(dt),country=cc,tot_source_year=src[t,ci],tot_level=inp['TOT_l'][t,ci],tot_change=inp['TOT_d'][t,ci],commodity_source_month=str(dt-2),commodity_level=inp['COM_l'][t,ci],commodity_change=inp['COM_d'][t,ci],merchandise_source_year=msrc[t,ci]))
    pd.DataFrame(known).to_csv(H/'tables/available_inputs.csv',index=False)
    wr=weights.copy();wr['tot_proxy_weight']=wr.export_share-wr.import_share;wr.to_csv(H/'tables/basket_weights.csv',index=False)
    TOT.rename(columns=dict(zip(ISO,CC))).to_csv(H/'data/tot_national_accounts_log.csv')
    MER.rename(columns=dict(zip(ISO,CC))).to_csv(H/'data/tot_merchandise_log.csv')
    aa=pd.DataFrame(aud)
    check('Every target ends before forecast origin',(aa.last_target<aa.origin).all())
    check('Every training window has required history',(aa.n_dates>=np.where(aa.scenario=='quarterly',20,60)).all())
    # Base and extended errors must use exactly the same evaluation records.
    for _,g in metrics.groupby(['scenario','period','h','country']):
        check('Paired dates '+str(tuple(g.iloc[0][['scenario','period','h','country']])),g.n_dates.nunique()==1 and g['first'].nunique()==1 and g['last'].nunique()==1)
    check('Prior files preserved',all(hashlib.sha256((R/f).read_bytes()).hexdigest()==v for f,v in hashes.items()))
    pd.DataFrame(checks).to_csv(H/'tables/validation.csv',index=False)
    print(metrics.query("scenario=='main' and period=='all' and country=='POOL'").pivot(index='h',columns='model',values='rmse_rw').round(3).to_string())
    print('Validation:',len(checks),'passed; saved all models including failures.')
if __name__=='__main__':main()
