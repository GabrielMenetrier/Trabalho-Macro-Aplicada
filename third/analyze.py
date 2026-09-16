"""15 hypotheses on commodity/FX forecasting; no portfolios or strategy returns."""
from pathlib import Path
import sys,json
import numpy as np
import pandas as pd
import statsmodels.api as sm
from statsmodels.stats.multitest import multipletests
R=Path(__file__).resolve().parents[1];H=R/'third';sys.path.insert(0,str(H));sys.path.insert(0,str(R/'src'))
from engine import oos,ejr_extension
from models import features,forecast
CC=['BRL','EUR','JPY','GBP','CAD','SEK'];COM=['oil','gas','copper','iron','soy','corn','wheat','gold'];HH=[3,12,36,60]
def read(p):
    a=pd.read_csv(p,index_col=0);a.index=pd.PeriodIndex(a.index,freq='M');return a.sort_index()
def save(a,name):pd.DataFrame(a).to_csv(H/'tables'/f'{name}.csv',index=False,float_format='%.10g')
FX=read(R/'data/processed/fx.csv')[CC];CP=read(R/'data/processed/cpi.csv')
dates=FX.loc['1999-10':'2026-08'].index;T=len(dates);START=int(np.flatnonzero(dates>=pd.Period('2010-01'))[0])
P=read(H/'data/commodities.csv');BASKET=read(H/'data/sector_logprices.csv');W=pd.read_csv(H/'data/trade_weights.csv').pivot(index='currency',columns='sector',values='net_weight').reindex(CC)
sectors=['energy','food','raw','metals'];W=W[sectors];exposure=W.sum(axis=1).to_numpy()
q=features(FX,CP).reindex(dates).to_numpy();s=np.log(FX).reindex(dates).to_numpy()
def dev(a):return a-pd.DataFrame(a).expanding().mean().to_numpy()
qd=dev(q);sd=dev(s);relative=q-s;reld=dev(relative)
mom=np.log(FX).diff(12).reindex(dates).to_numpy()
pi=(np.log(CP[CC])-np.log(CP.USD).to_numpy()[:,None]).reindex(dates).to_numpy()
infknown=(np.log(CP[CC].ffill(limit=1))-np.log(CP.USD.ffill(limit=1)).to_numpy()[:,None]).diff(12).shift(2).reindex(dates).to_numpy()
logP=np.log(P);logCP=np.log(CP.USD)
rawreal=logP.sub(logCP,axis=0);knownreal=logP.sub(np.log(CP.USD.ffill(limit=1)),axis=0).shift(2).reindex(dates)
knownnom=logP.shift(1).reindex(dates)
sectorreal=BASKET.sub(np.log(CP.USD.ffill(limit=1)),axis=0).shift(2).reindex(dates)[sectors]
globallev=sectorreal.mean(axis=1,skipna=False).to_numpy();globaldev=dev(globallev[:,None])[:,0]
globalmom=sectorreal.mean(axis=1,skipna=False).diff(12).to_numpy()
tradelev=sectorreal.to_numpy()@W.to_numpy().T;tradedev=dev(tradelev)
trademom=pd.DataFrame(tradelev).diff(12).to_numpy()
specific=tradedev-globaldev[:,None]*exposure[None,:]
dollar=sd.mean(axis=1);C=len(CC)
metadata={};predrows=[];audits=[];metrics=[];sensitivity=[];prediction_cache={}

def target_price(c,h,unit):
    if unit=='nominal':values=logP.reindex(dates)[c].to_numpy();known=knownnom[c].to_numpy();release=1
    else:values=rawreal.reindex(dates)[c].to_numpy();known=knownreal[c].to_numpy();release=2
    y=np.full(T,np.nan);y[:T-h]=values[h:]-known[:T-h]
    return y,release
def target_fx(h,values=s):
    y=np.full_like(values,np.nan);y[:T-h]=values[h:]-values[:-h];return y
def score_series(task,model,Y,PP,BASE,RW,h,group='POOL',period='all',block='A',benchmark='history'):
    if Y.ndim==1:Y=Y[:,None];PP=PP[:,None];BASE=BASE[:,None];RW=RW[:,None]
    valid=np.isfinite(Y)&np.isfinite(PP)&np.isfinite(BASE)&np.isfinite(RW)
    valid[:START]=False
    if period=='late':valid[dates<pd.Period('2019-01')]=False
    if group!='POOL' and Y.shape[1]>1:
        keep=np.zeros(Y.shape[1],bool);keep[CC.index(group)]=True;valid &=keep[None,:]
    if not valid.any():return
    y=Y[valid];p=PP[valid];b=BASE[valid];rw=RW[valid]
    counts=valid.sum(axis=1);ts=np.flatnonzero(counts)
    mse=np.mean((y-p)**2);bse=np.mean((y-b)**2);rwse=np.mean((y-rw)**2)
    loss=np.where(valid,(Y-BASE)**2-(Y-PP)**2,0).sum(axis=1)[ts]/counts[ts]
    mean=loss.mean();se=pval=p_rw=np.nan;lag=h+2
    # Overlapping long horizons are descriptive when fewer than three effective blocks.
    if len(ts)>=max(36,3*(h+2)) and loss.std()>1e-14:
        fit=sm.OLS(loss,np.ones(len(loss))).fit(cov_type='HAC',cov_kwds={'maxlags':lag,'use_correction':True})
        se=float(fit.bse[0]);pval=float(fit.pvalues[0])
    lossrw=np.where(valid,(Y-RW)**2-(Y-PP)**2,0).sum(axis=1)[ts]/counts[ts]
    if len(ts)>=max(36,3*(h+2)) and lossrw.std()>1e-14:
        rwfit=sm.OLS(lossrw,np.ones(len(lossrw))).fit(cov_type='HAC',cov_kwds={'maxlags':lag,'use_correction':True});p_rw=float(rwfit.pvalues[0])
    metrics.append(dict(block=block,task=task,h=h,model=model,benchmark=benchmark,country=group,period=period,n=len(y),n_dates=len(ts),first=str(dates[ts[0]]),last=str(dates[ts[-1]]),approx_blocks=len(ts)/(h+2),rmse=np.sqrt(mse),rmse_ratio=np.sqrt(mse/bse) if bse>0 else np.nan,rmse_rw=np.sqrt(mse/rwse),r2_oos=1-mse/bse,hit=np.mean(np.sign(p)==np.sign(y)),loss_gain=mean,se=se,p=pval,p_rw=p_rw))

def register(task,block,h,Y,models,base,audits_local=None):
    Y=np.asarray(Y)
    if Y.ndim==1:Y=Y[:,None]
    models={k:np.asarray(v).reshape(Y.shape) for k,v in models.items()}
    prediction_cache[task]=(Y,models)
    for model,PRED in models.items():
        for group in (['POOL']+CC if Y.shape[1]==6 else ['POOL']):
            for period in ['all','late']:score_series(task,model,Y,PRED,models[base],models['RW'],h,group,period,block,base)
        # Store observations only once, not again for the pooled evaluation.
        good=np.isfinite(Y)&np.isfinite(PRED);good[:START]=False
        ti,ci=np.where(good)
        for t,c in zip(ti,ci):predrows.append((block,task,h,model,str(dates[t]),CC[c] if Y.shape[1]==6 else task.split('_')[1],Y[t,c],PRED[t,c]))
    if audits_local:
        for model,records in audits_local.items():
            for t,begin,last,available,n,nd in records:audits.append((task,model,str(dates[t]),str(dates[begin]),str(dates[last]),str(dates[available]),n,nd))

def fx_designs(g=globaldev,gm=globalmom,z=tradedev,zm=trademom,sp=specific):
    G=np.repeat(g[:,None],C,axis=1);GM=np.repeat(gm[:,None],C,axis=1);E=np.repeat(exposure[None,:],T,axis=0)
    stack=lambda *xs:np.stack(xs,axis=2)
    return {'AR':stack(mom),'Q':stack(qd),'Commodity':stack(G,GM),'Trade_only':stack(z,zm),
            'Q_Global':stack(qd,G),'Q_Momentum':stack(qd,GM),'Q_GlobalMom':stack(qd,G,GM),
            'Q_Trade':stack(qd,z),'Q_TradeMom':stack(qd,z,zm),'Q_Interaction':stack(qd,G,qd*G),
            'Q_TradeInteraction':stack(qd,z,qd*z),'Q_Exposure':stack(qd,G,G*E,qd*E),
            'Q_Specific':stack(qd,G,sp),'Q_Equilibrium':stack(qd,z)}

if __name__=='__main__':
    # A: both price definitions, eight commodities, all single currencies plus combinations.
    for unit in ['nominal','real']:
        known=knownnom if unit=='nominal' else knownreal
        # Momentum is computed on complete pre-sample history, with the same release lag.
        underlying=logP if unit=='nominal' else logP.sub(np.log(CP.USD.ffill(limit=1)),axis=0)
        lag=1 if unit=='nominal' else 2
        momentum=underlying.diff(12).shift(lag).reindex(dates)
        momentum3=underlying.diff(3).shift(lag).reindex(dates)
        for c in COM:
            own=np.c_[dev(known[c].to_numpy()[:,None])[:,0],momentum[c],momentum3[c]]
            specs={'history':own,'dollar':np.c_[own,dollar],'Q_all':np.c_[own,qd],'Q_factor':np.c_[own,qd], 'Q_mean':np.c_[own,qd.mean(axis=1)]}
            for j,cc in enumerate(CC):
                specs['Q_'+cc]=np.c_[own,qd[:,j]];specs['S_'+cc]=np.c_[own,sd[:,j]];specs['PI_'+cc]=np.c_[own,reld[:,j]];specs['QD_'+cc]=np.c_[own,dollar,qd[:,j]]
                specs['DS_'+cc]=np.c_[own,mom[:,j]]
            for h in HH:
                task=f'A_{c}_{unit}_{h}';Y,release=target_price(c,h,unit);models={'RW':np.zeros(T)};aa={}
                for name,X in specs.items():
                    pr,au=oos(X,Y,h,release,mode='pca' if name=='Q_factor' else None,start=START);models[name]=pr[:,0];aa[name]=au
                models['Q_average']=np.mean(np.stack([models['Q_'+cc] for cc in CC]),axis=0)
                # Country groups are fixed by pre-1997 absolute net exposure to the sector.
                sector={'oil':'energy','gas':'energy','copper':'metals','iron':'metals','soy':'food','corn':'food','wheat':'food','gold':'metals'}[c]
                order=np.argsort(-np.abs(W[sector].to_numpy()),kind='stable');linked=[CC[i] for i in order[:2]];other=[CC[i] for i in order[2:]]
                models['Q_linked']=np.mean(np.stack([models['Q_'+cc] for cc in linked]),axis=0);models['Q_other']=np.mean(np.stack([models['Q_'+cc] for cc in other]),axis=0)
                metadata[task]={'linked':linked,'other':other,'sector':sector,'gold_proxy_caveat':c=='gold'}
                register(task,'A',h,Y,models,'history',aa)
                for name in ['QD_'+cc for cc in CC]:
                    for period in ['all','late']:score_series(task,name,Y,models[name],models['dollar'],models['RW'],h,period=period,block='A',benchmark='dollar')
            print('A completed:',unit,c,flush=True)
    # B/C: common estimator comparison; original EJR is separately included.
    for h in HH:
        Y=target_fx(h);models={'RW':np.zeros_like(Y)};aa={}
        ejr,_,_,last=forecast(s,q,h);models['EJR']=ejr['ejr']
        for name,X in fx_designs().items():
            models[name],aa[name]=oos(X,Y,h,mode='equilibrium' if name=='Q_Equilibrium' else None,start=START)
        G=np.repeat(globallev[:,None],C,axis=1);GM=np.repeat(globalmom[:,None],C,axis=1)
        for name,xx,inter in [('REJR_Global',[q,G],False),('REJR_Trade',[q,tradelev],False),('REJR_GlobalMom',[q,G,GM],False),('REJR_Interaction',[q,G],True),('REJR_TradeInteraction',[q,tradelev],True),('REJR_Exposure',[q,G,G*exposure[None,:]],False),('REJR_Specific',[q,G,tradelev-G*exposure[None,:]],False)]:
            models[name],aa[name]=ejr_extension(np.stack(xx,axis=2),Y,h,start=START,interaction=inter)
        register(f'B_FX_{h}','B',h,Y,models,'Q',aa)
        for name,PRED in models.items():
            if name in ['RW','EJR']:continue
            for group in ['POOL']+CC:
                for period in ['all','late']:score_series(f'B_FX_{h}',name,Y,PRED,models['EJR'],models['RW'],h,group,period,'B','EJR')
        # Inflation channel: future local-US price growth, release timing explicit.
        YI=target_fx(h,pi);MI={'RW':np.zeros_like(YI)};ai={};G=np.repeat(globaldev[:,None],C,axis=1)
        for name,X in {'history':np.stack([infknown],axis=2),'Q':np.stack([infknown,qd],axis=2),'Commodity':np.stack([infknown,G],axis=2),'Q_Global':np.stack([infknown,qd,G],axis=2),'Q_Trade':np.stack([infknown,qd,tradedev],axis=2),'Interaction':np.stack([infknown,qd,G,qd*G],axis=2)}.items():
            MI[name],ai[name]=oos(X,YI,h,release=2,start=START)
        register(f'C_inflation_{h}','C',h,YI,MI,'history',ai)
        print('B/C completed horizon:',h,flush=True)
    a=pd.DataFrame(metrics);a['p_holm']=np.nan;a['p_rw_holm']=np.nan
    for block in ['A','B','C']:
        entries=[]
        for source,dest in [('p','p_holm'),('p_rw','p_rw_holm')]:
            mask=(a.block==block)&a[source].notna()&(a.model!='RW')
            if source=='p':mask &= a.model!=a.benchmark
            entries.extend((i,source,dest) for i in a.index[mask])
        corrected=multipletests([a.loc[i,source] for i,source,dest in entries],method='holm')[1]
        for (i,source,dest),value in zip(entries,corrected):a.loc[i,dest]=value
    save(a,'metrics')
    obs=pd.DataFrame(predrows,columns=['block','task','h','model','origin','unit','actual','pred'])
    obs.to_csv(H/'tables/predictions.csv.gz',index=False,compression='gzip',float_format='%.10g')
    save(pd.DataFrame(audits,columns=['task','model','origin','first_train','last_train_origin','last_label_available','n_train','n_train_dates']),'audit')
    (H/'data/task_metadata.json').write_text(json.dumps(metadata,indent=2),encoding='utf8')
    np.savez_compressed(H/'data/core.npz',dates=dates.astype(str).to_numpy(dtype=str),s=s,q=q,qd=qd,globaldev=globaldev,globalmom=globalmom,tradedev=tradedev,trademom=trademom,specific=specific,exposure=exposure,mom=mom,pi=pi)
    print('Finished:',len(a),'metric rows;',len(obs),'evaluated forecasts;',len(audits),'audited fits.')
    print(a[(a.block=='B')&(a.country=='POOL')&(a.period=='all')&(a.benchmark=='Q')][['h','model','rmse_ratio','rmse_rw','p_holm']].to_string(index=False))
