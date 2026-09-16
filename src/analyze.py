"""Run all reported estimates/backtests from saved data; no network access."""
from pathlib import Path
import os, json, hashlib, sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
os.environ['MPLCONFIGDIR']=str(ROOT/'tmp/matplotlib')
import numpy as np
import pandas as pd
import scipy.stats as st
import statsmodels.api as sm
from statsmodels.stats.multitest import multipletests
from models import features,forecast,rank_weights,run_book,metrics

OUT=ROOT/'output'; TABLES=OUT/'tables'
CC=['BRL','EUR','JPY','GBP','CAD','SEK']; HH=[12,24,36,60,84,96]
START='1999-10'; OOS='2010-01'; SEED=20260910

def read(name):
    df=pd.read_csv(ROOT/f'data/processed/{name}.csv',index_col=0)
    df.index=pd.PeriodIndex(df.index,freq='M'); return df.sort_index()

def save(df,name):
    df.to_csv(TABLES/f'{name}.csv',index=False,float_format='%.10g')

def hac_fit(x,y,h):
    valid=np.isfinite(x)&np.isfinite(y); x=np.asarray(x)[valid]; y=np.asarray(y)[valid]
    fit=sm.OLS(y,sm.add_constant(x)).fit(cov_type='HAC',cov_kwds={'maxlags':min(h,len(y)-3),'use_correction':True})
    return dict(n=len(y),beta=fit.params[1],se=fit.bse[1],p=fit.pvalues[1],r2=fit.rsquared,alpha=fit.params[0])

def forecast_scores(records):
    df=pd.DataFrame(records); rows=[]
    for (h,model,country),a in df.groupby(['h','model','country']):
        actual=a.actual.to_numpy(); pred=a.pred.to_numpy()
        e0=actual; e1=actual-pred
        r=np.sqrt(np.mean(e1**2)/np.mean(e0**2))
        # Averaging currencies at each date preserves common shocks in HAC.
        a=a.assign(cw=e0**2-e1**2+pred**2,loss=e0**2-e1**2)
        ts=a.groupby('origin')[['cw','loss']].mean()
        nw=min(h+8,max(1,len(ts)-2))
        cw=sm.OLS(ts.cw,np.ones(len(ts))).fit(cov_type='HAC',cov_kwds={'maxlags':nw,'use_correction':True})
        rows.append(dict(h=h,model=model,country=country,n=len(a),n_dates=len(ts),nonoverlap_approx=int(np.ceil(len(ts)/h)),
                         rmse_ratio=r,r2_oos=1-r*r,hit=float(np.mean(np.sign(pred)==np.sign(actual))),
                         cw_p_one_sided=float(st.norm.sf(cw.tvalues.iloc[0])),first=a.origin.min(),last=a.origin.max()))
    result=pd.DataFrame(rows)
    result['cw_p_holm']=multipletests(result.cw_p_one_sided,method='holm')[1]
    save(result,'forecast_accuracy'); save(df,'forecast_observations')
    return result

def null_bootstrap(s,q,dates,reps=999):
    """Joint innovation bootstrap under an unpredictable nominal FX null.

    AR(1) or unit root for q; contemporaneous covariance is retained across all
    nominal and real currencies by drawing entire residual rows. Reestimate EJR
    at every origin in every simulation. Conditional on full-sample null fit;
    this is an extension, not the article's AR(AIC<=8)/10,000-draw bootstrap.
    """
    rng=np.random.default_rng(SEED); T,C=s.shape; a=np.zeros(C); rho=np.zeros(C)
    residual=np.zeros((T-1,C))
    for c in range(C):
        fit=np.linalg.lstsq(np.column_stack([np.ones(T-1),q[:-1,c]]),q[1:,c],rcond=None)[0]
        a[c],rho[c]=fit; residual[:,c]=q[1:,c]-a[c]-rho[c]*q[:-1,c]
    rho=np.clip(rho,-.995,.995)
    ds=np.diff(s,axis=0); nominal=ds-ds.mean(axis=0)
    rows=[]
    # Vectorized across independent bootstrap replications and origins.
    for kind in ['stationary_ar1','unit_root']:
        qr=residual if kind=='stationary_ar1' else np.diff(q,axis=0)
        joint=np.column_stack([nominal,qr-qr.mean(axis=0)])
        mu=q.mean(axis=0)
        burn=300 if kind=='stationary_ar1' else 0
        draws=joint[rng.integers(0,len(joint),size=(reps,T+burn))]
        qs=np.empty((reps,T+burn,C)); qs[:,0]=mu if burn else q[0]
        for t in range(1,T+burn):
            qs[:,t]=mu+rho*(qs[:,t-1]-mu)+draws[:,t,C:] if burn else qs[:,t-1]+draws[:,t,C:]
        qs=qs[:,burn:]; ss=np.cumsum(draws[:,burn:,:C],axis=1)
        qcum=np.cumsum(qs,axis=1)
        for h in HH:
            origin=np.array([t for t in range(h+61,T-h) if str(dates[t])>=OOS])
            y=ss[:,h:]-ss[:,:-h]
            x=qs[:,:-h]
            xy=np.cumsum(x*y,axis=1); x2=np.cumsum(x*x,axis=1); xc=np.cumsum(x,axis=1); yc=np.cumsum(y,axis=1)
            n=origin-h
            mu_t=qcum[:,origin]/(origin[None,:,None]+1)
            num=(xy[:,n-1]-mu_t*yc[:,n-1]).sum(axis=2)
            den=(x2[:,n-1]-2*mu_t*xc[:,n-1]+n[None,:,None]*mu_t**2).sum(axis=2)
            pred=(num/den)[:,:,None]*(qs[:,origin]-mu_t)
            actual=ss[:,origin+h]-ss[:,origin]
            ratios=np.sqrt(np.mean((actual-pred)**2,axis=(1,2))/np.mean(actual**2,axis=(1,2)))
            real=forecast(s,q,h)[0]['ejr'][origin]
            target=s[origin+h]-s[origin]
            observed=np.sqrt(np.mean((target-real)**2)/np.mean(target**2))
            p=(1+np.sum(ratios<=observed))/(reps+1)
            rows.append(dict(null=kind,h=h,rmse_ratio=observed,p_boot=p,mc_se=np.sqrt(p*(1-p)/reps),reps=reps,
                             rho_min=rho.min(),rho_max=rho.max()))
        print('Bootstrap complete:',kind,flush=True)
    result=pd.DataFrame(rows); result['p_holm']=multipletests(result.p_boot,method='holm')[1]
    save(result,'bootstrap_null')

def block_ci(r, cash,block=12,reps=4999):
    rng=np.random.default_rng(SEED+block); z=np.asarray(r)-np.asarray(cash); n=len(z)
    starts=rng.integers(0,n,size=(reps,int(np.ceil(n/block))))
    indices=(starts[:,:,None]+np.arange(block))%n
    samples=z[indices.reshape(reps,-1)[:,:n]]
    means=samples.mean(axis=1)*12
    return np.quantile(means,[.025,.975])

def main():
    TABLES.mkdir(parents=True,exist_ok=True)
    fx=read('fx').loc[START:,CC]; dates=fx.index
    cpi=read('cpi'); rates=read('rates').loc[START:,CC+['USD']]
    s=np.log(fx.to_numpy()); qdf=features(read('fx')[CC],cpi,2).loc[START:]; q=qdf.to_numpy()
    assert np.isfinite(s).all() and np.isfinite(q).all() and np.isfinite(rates).all().all()
    qdf.to_csv(ROOT/'data/processed/q_available.csv')
    # Descriptive replication: maintain regular calendar BEFORE shifting targets.
    classroom=read('classroom').loc['1995-01':'2026-04']
    replicated=[]
    slide_beta=[-.195,-.381,-.652,-.969,-1.238,-1.527,-1.722,-1.808,-1.739,-1.616]
    for name,pcol in [('SA_BLS','P_US_SA'),('NSA_BIS','P_US_NSA')]:
        if pcol not in classroom: continue
        qr=np.log(classroom.S*classroom[pcol]/classroom.P_BR)
        for k,h in enumerate(range(12,121,12)):
            fit=hac_fit(qr,np.log(classroom.S.shift(-h)/classroom.S),h)
            replicated.append(dict(spec=name,h=h,slide_beta=slide_beta[k],difference=fit['beta']-slide_beta[k],**fit))
    save(pd.DataFrame(replicated),'classroom_replication')
    reg=[]
    qfull=features(read('fx')[CC],cpi,0).loc[START:]
    pdiff=np.log(cpi.USD).to_numpy()[:,None]-np.log(cpi[CC].to_numpy())
    pdf=pd.DataFrame(pdiff,index=cpi.index,columns=CC).loc[START:]
    # No filling missing CPI in descriptive estimation.
    qexact=np.log(fx)+np.log(cpi.USD.reindex(dates)).to_numpy()[:,None]-np.log(cpi[CC].reindex(dates))
    for h in HH:
        for c,code in enumerate(CC):
            y=np.r_[s[h:,c]-s[:-h,c],np.repeat(np.nan,h)]
            reg.append(dict(country=code,h=h,equation='nominal',**hac_fit(qexact[code],y,h)))
            y2=pdf[code].shift(-h)-pdf[code]
            reg.append(dict(country=code,h=h,equation='relative_prices',**hac_fit(qexact[code],y2,h)))
    save(pd.DataFrame(reg),'horizon_regressions')
    forecasts={}; records=[]; audit=[]
    for h in HH:
        preds,slopes,n,last=forecast(s,q,h)
        forecasts[h]=preds
        for t in range(len(dates)):
            if not np.isfinite(preds['ejr'][t]).all(): continue
            audit.append(dict(origin=str(dates[t]),h=h,latest_training_label=str(dates[last[t]]),
                              latest_training_origin=str(dates[t-h-1]),price_reference_max=str(dates[t]-2),
                              n_training=n[t],beta_ejr=slopes[t,0],beta_fe=slopes[t,1]))
            if t+h>=len(dates) or str(dates[t])<OOS: continue
            for model,p in preds.items():
                for c,code in enumerate(CC):
                    rec=dict(origin=str(dates[t]),target_end=str(dates[t+h]),h=h,model=model,country=code,
                             actual=s[t+h,c]-s[t,c],pred=p[t,c])
                    records.append(rec)
                    records.append({**rec,'country':'POOL'})
    acc=forecast_scores(records); save(pd.DataFrame(audit),'timing_audit')
    # Matched origins across all horizons: avoid mistaking period for horizon.
    obs=pd.DataFrame(records); common=obs[(obs.h==96)&(obs.model=='ejr')].origin.unique()
    matched=[]
    for (h,model),a in obs[(obs.country=='POOL')&obs.origin.isin(common)].groupby(['h','model']):
        rr=np.sqrt(np.mean((a.actual-a.pred)**2)/np.mean(a.actual**2))
        matched.append(dict(h=h,model=model,n=len(a),first=a.origin.min(),last=a.origin.max(),rmse_ratio=rr))
    save(pd.DataFrame(matched),'forecast_common_origins')
    null_bootstrap(s,q,dates)
    # Predeclared portfolio universe, horizon 60, no search for best parameters.
    rate_m=(1+rates/100)**(1/12)-1
    carry=np.log1p(rate_m[CC]).sub(np.log1p(rate_m.USD),axis=0).to_numpy()
    f=forecasts[60]['ejr']; score=-f/60+carry
    weights={
        'EJR + carry':rank_weights(score),
        'EJR cambial':rank_weights(-f),
        'Carry':rank_weights(carry),
        'Momentum':rank_weights(-pd.DataFrame(s).diff(12).to_numpy()),
        'Painel FE + carry':rank_weights(-forecasts[60]['fe']/60+carry),
        'OLS + carry':rank_weights(-forecasts[60]['ols']/60+carry),
        'Direcional USD':np.sign(score)/len(CC),
    }
    for v in weights.values(): v[(dates<OOS) | ~np.isfinite(f).all(axis=1)]=0
    weights['Coortes 60m']=pd.DataFrame(weights['EJR + carry']).rolling(60,min_periods=1).sum().to_numpy()/60
    start_mask=dates>=pd.Period('2010-03','M')
    cost=np.array([10,2,2,2,2,3],float)
    books={}; summary=[]; details=[]
    for name,w in weights.items():
        book,target,contrib=run_book(w,fx,rates,cost,50)
        book.index=dates; book=book.loc[start_mask]
        book['nav']=(1+book.net).cumprod(); books[name]=book
        m=metrics(book.net,book.cash); ci=block_ci(book.net,book.cash)
        summary.append(dict(strategy=name,**m,turnover_ann=12*book.turnover.mean(),cost_ann=12*book.cost.mean(),
                            borrow_ann=12*book.borrow.mean(),excess_ci_low=ci[0],excess_ci_high=ci[1]))
        for t,d in enumerate(dates):
            if not start_mask[t]: continue
            details.append(dict(month=str(d),strategy=name,**book.loc[d].to_dict()))
        if name=='EJR + carry':
            wf=pd.DataFrame(target,index=dates,columns=CC).loc[start_mask]; wf.index.name='month'; wf.to_csv(TABLES/'weights_main.csv')
            cf=pd.DataFrame(contrib,index=dates,columns=CC).loc[start_mask]; cf.index.name='month'; cf.to_csv(TABLES/'contributions_main.csv')
    cash=books['EJR + carry'].cash
    summary.append(dict(strategy='Caixa USD',**metrics(cash,cash),turnover_ann=0,cost_ann=0,borrow_ann=0))
    save(pd.DataFrame(summary),'portfolio_metrics'); save(pd.DataFrame(details),'portfolio_returns')
    # Robustness grid is disclosed in full; it does not choose the main strategy.
    robust=[]
    variants=[('Base',weights['EJR + carry'],rates,1),('IPC lag 3',None,rates,1),('Execucao lag 2',weights['EJR + carry'],rates,2),
              ('Janela 120',None,rates,1),('Sem JPY no treino',None,rates,1),('Sem BRL no treino',None,rates,1)]
    q3=features(read('fx')[CC],cpi,3).loc[START:].to_numpy()
    alternate=[q3,q,q,q]
    for i,(name,w,rate,lag) in enumerate(variants):
        if w is None:
            kw={}
            qq=q3 if name=='IPC lag 3' else q
            if name=='Janela 120': kw['window']=120
            if name=='Sem JPY no treino': kw['train_countries']=[0,1,3,4,5]
            if name=='Sem BRL no treino': kw['train_countries']=[1,2,3,4,5]
            ff=forecast(s,qq,60,**kw)[0]['ejr']; w=rank_weights(-ff/60+carry); w[dates<OOS]=0
        for costmult,spread in ([(0,0),(1,50),(2,100),(5,200)] if name=='Base' else [(1,50)]):
            b,_,_=run_book(w,fx,rate,cost*costmult,spread,execution_lag=lag)
            a=b.loc[start_mask]; robust.append(dict(variant=name,cost_mult=costmult,borrow_bps=spread,**metrics(a.net,a.cash)))
    # Exclude each currency from trading as well (renormalized top/bottom 2).
    for drop in ['BRL','JPY']:
        ids=[i for i,c in enumerate(CC) if c!=drop]; ww=rank_weights(score[:,ids]); ww[dates<OOS]=0
        full=np.zeros_like(score); full[:,ids]=ww
        b,_,_=run_book(full,fx,rates,cost,50); a=b.loc[start_mask]
        robust.append(dict(variant='Sem '+drop+' na carteira',cost_mult=1,borrow_bps=50,**metrics(a.net,a.cash)))
    save(pd.DataFrame(robust),'robustness')
    hs=[]
    common_bt=dates>=pd.Period('2013-01','M')
    for h in HH:
        w=rank_weights(-forecasts[h]['ejr']/h+carry); w[dates<OOS]=0
        b,_,_=run_book(w,fx,rates,cost,50); a=b.loc[common_bt]
        hs.append(dict(h=h,**metrics(a.net,a.cash)))
    save(pd.DataFrame(hs),'portfolio_horizons')
    # Historical subperiods and ex-ante regimes, no optimized threshold.
    periods=[('2010-2014','2010-03','2014-12'),('2015-2019','2015-01','2019-12'),('2020-2021','2020-01','2021-12'),
             ('2022-2023','2022-01','2023-12'),('2024-2026','2024-01','2026-08'),('Pos-publicacao','2021-01','2026-08')]
    subs=[]
    for name,b in books.items():
        for label,beg,end in periods:
            a=b.loc[beg:end]; subs.append(dict(strategy=name,period=label,**metrics(a.net,a.cash)))
    save(pd.DataFrame(subs),'subperiods')
    # Lagged median 12m FX volatility; expanding median cutoff known at signal.
    vol=pd.DataFrame(s,index=dates).diff().rolling(12,min_periods=12).std().median(axis=1)*np.sqrt(12)
    cutoff=vol.expanding(min_periods=36).median()
    masks={'Vol alta':(vol>cutoff).shift(2),'Vol baixa':(vol<=cutoff).shift(2),
           'Juro USD <= 0,5%':(rates.USD<=.5).shift(2),'Juro USD > 0,5%':(rates.USD>.5).shift(2)}
    regimes=[]
    b=books['EJR + carry']
    for name,mask in masks.items():
        a=b.loc[mask.reindex(b.index).fillna(False).astype(bool)]
        regimes.append(dict(regime=name,n=len(a),mean_excess=12*(a.net-a.cash).mean(),vol=a.net.std()*np.sqrt(12),
                            win_rate=(a.net>0).mean()))
    save(pd.DataFrame(regimes),'regimes')
    # Brazilian numeraire: cash USD asset is bought against a BRL cash portfolio.
    brfx=(1/fx.BRL).to_numpy()[:,None]; brrates=rates[['USD','BRL']].to_numpy()
    usd_adv=f[:,0]/60+np.log1p(rate_m.USD)-np.log1p(rate_m.BRL)
    bw={'Caixa BRL':np.zeros((len(dates),1)), 'Caixa USD em BRL':np.ones((len(dates),1)),
        'Alocacao USD/BRL':(np.asarray(usd_adv)>0).astype(float)[:,None],
        'Alocacao so cambio':(f[:,0]>0).astype(float)[:,None]}
    brsum=[]; brdet=[]
    for name,w in bw.items():
        w[dates<OOS]=0
        b,_,_=run_book(w,brfx,brrates,np.array([10.]),50); b.index=dates; a=b.loc[start_mask]
        brsum.append(dict(strategy=name,**metrics(a.net,a.cash)))
        for d,r in a.iterrows(): brdet.append(dict(month=str(d),strategy=name,net=r.net,cash=r.cash))
    # Same USD NAV simply converted to BRL (different from choosing BRL collateral).
    b=books['EJR + carry']; brchange=fx.BRL.pct_change().reindex(b.index)
    converted=(1+b.net)*(1+brchange)-1
    brcash=((1+rates.BRL/100)**(1/12)-1).shift(1).reindex(b.index)
    brsum.append(dict(strategy='Long-short USD convertido',**metrics(converted,brcash)))
    save(pd.DataFrame(brsum),'brl_metrics'); save(pd.DataFrame(brdet),'brl_returns')
    # Real traded US assets, replacing the USD cash proxy in the Brazilian book.
    # ETF adjusted returns are outcomes only; the unchanged FX/carry signal does
    # not forecast equity premia. Actual fund expenses are embedded in prices.
    ep=read('etf_adjusted_close').reindex(dates)
    etfsum=[]; etfdet=[]
    for ticker in ep.columns:
        er=ep[ticker].pct_change(fill_method=None).to_numpy()
        fxr=fx.BRL.pct_change().to_numpy()
        asset=(1+er)*(1+fxr)-1
        brcash=rate_m.BRL.shift(1).to_numpy()
        for rule in ['Manter','Sinal FX + juros']:
            alloc=np.ones(len(dates)) if rule=='Manter' else (np.asarray(usd_adv)>0).astype(float)
            alloc[dates<OOS]=0
            target=np.r_[0,0,alloc[:-2]]; prev=0.; returns=[]
            for t in range(len(dates)):
                if not start_mask[t]: returns.append(np.nan); continue
                fee=abs(target[t]-prev)*.0012 # 10 bps FX + 2 bps ETF per one-way turnover.
                ret=brcash[t]+target[t]*(asset[t]-brcash[t])-fee
                if t==len(dates)-1: ret-=abs(target[t]*(1+asset[t]))*.0012
                returns.append(ret); prev=target[t]*(1+asset[t])/(1+ret)
            rr=np.array(returns)[start_mask]
            etfsum.append(dict(ticker=ticker,rule=rule,**metrics(rr,brcash[start_mask]),allocation_mean=target[start_mask].mean()))
            for d,r in zip(dates[start_mask],rr): etfdet.append(dict(month=str(d),ticker=ticker,rule=rule,net=r))
    save(pd.DataFrame(etfsum),'etf_metrics'); save(pd.DataFrame(etfdet),'etf_returns')
    # Last forecasts are unscored scenarios, not inferred true values.
    latest=[]
    for h in [12,36,60,96]:
        for c,code in enumerate(CC):
            t=len(dates)-1; pred=forecasts[h]['ejr'][t,c]
            mature=[j for j in range(t-h) if np.isfinite(forecasts[h]['ejr'][j,c]) and str(dates[j])>=OOS]
            errors=np.array([s[j+h,c]-s[j,c]-forecasts[h]['ejr'][j,c] for j in mature])
            se=np.sqrt(np.mean(errors**2)) if len(errors) else np.nan
            latest.append(dict(country=code,h=h,origin=str(dates[t]),spot=fx.iloc[t,c],pred_log=pred,
                               median_scenario=fx.iloc[t,c]*np.exp(pred),rmse_historical=se,
                               band_low=fx.iloc[t,c]*np.exp(pred-1.96*se),band_high=fx.iloc[t,c]*np.exp(pred+1.96*se),n_errors=len(errors)))
    save(pd.DataFrame(latest),'latest_scenarios')
    # CI at both 12- and 60-month block lengths for overlapping persistent signals.
    cis=[]
    for name in ['EJR + carry','Carry','Coortes 60m']:
        b=books[name]
        for block in [12,60]:
            lo,hi=block_ci(b.net,b.cash,block); cis.append(dict(strategy=name,block=block,ci_low=lo,ci_high=hi))
    save(pd.DataFrame(cis),'return_bootstrap_ci')
    mainbook=books['EJR + carry']; carrybook=books['Carry']
    difference=mainbook.net-carrybook.net
    diffci=block_ci(difference,np.zeros(len(difference)),12)
    factors=np.column_stack([carrybook.net-carrybook.cash,books['Momentum'].net-books['Momentum'].cash])
    alpha=sm.OLS(mainbook.net-mainbook.cash,sm.add_constant(factors)).fit(cov_type='HAC',cov_kwds={'maxlags':12,'use_correction':True})
    save(pd.DataFrame([dict(mean_difference_ann=12*difference.mean(),ci_low=diffci[0],ci_high=diffci[1],
                           alpha_ann=12*alpha.params.iloc[0],alpha_se_ann=12*alpha.bse.iloc[0],alpha_p=alpha.pvalues.iloc[0],
                           beta_carry=alpha.params.iloc[1],beta_momentum=alpha.params.iloc[2],r2=alpha.rsquared)]),'incremental_value')
    # Stress extension with shorter initial estimation: includes 2008, separately.
    ff=forecast(s,q,60,min_train=36)[0]['ejr']; ww=rank_weights(-ff/60+carry); ww[dates<'2008-01']=0
    bb,_,_=run_book(ww,fx,rates,cost,50); bb.index=dates
    save(pd.DataFrame([dict(period=label,**metrics(bb.loc[beg:end].net,bb.loc[beg:end].cash)) for label,beg,end in
                       [('2008-2009','2008-03','2009-12'),('2008-2026','2008-03','2026-08')]]),'short_training_stress')
    print(pd.DataFrame(summary)[['strategy','cagr','vol','sharpe','maxdd']].to_string(index=False))
    print(acc[(acc.country=='POOL')&(acc.model=='ejr')][['h','n_dates','rmse_ratio','r2_oos']].to_string(index=False))

if __name__=='__main__': main()
