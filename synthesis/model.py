"""Read-only inputs; composable causal portfolio rules."""
from pathlib import Path
import sys,os
R=Path(__file__).resolve().parents[1];H=R/'synthesis'
sys.path.insert(0,str(R/'src'));sys.path.insert(0,str(R/'third'))
os.environ['MPLCONFIGDIR']=str(R/'tmp/matplotlib')
import numpy as np,pandas as pd
from models import features,forecast,rank_weights,run_book,metrics
from engine import ejr_extension
for d in ['tables','cache','figures']:(H/d).mkdir(exist_ok=True)
CC=['BRL','EUR','JPY','GBP','CAD','SEK'];C=6
def read(p):
    a=pd.read_csv(p,index_col=0);a.index=pd.PeriodIndex(a.index,freq='M');return a
z=dict(np.load(R/'secondary/cache/core.npz'));dates=pd.PeriodIndex(z['dates'],freq='M');T=len(dates)
fx=z['fx'];rates=z['rates'];carry=z['carry'];qdev=z['qdev'];f=z['f'];q=features(read(R/'data/processed/fx.csv')[CC],read(R/'data/processed/cpi.csv')).reindex(dates).to_numpy();s=np.log(fx)
D=dict(np.load(R/'trade_extension/cache/trade.npz'));P=dict(np.load(R/'trade_extension/cache/predictions.npz'));costs=np.array([10,2,2,2,2,3])
def save(a,n):pd.DataFrame(a).to_csv(H/'tables'/(n+'.csv'),index=False,float_format='%.10g')
def pastq(x,p=.8):return pd.DataFrame(x).expanding(min_periods=36).quantile(p).shift(1).to_numpy()
def third_forecast():
    cp=read(R/'data/processed/cpi.csv');sr=read(R/'third/data/sector_logprices.csv').sub(np.log(cp.USD.ffill(limit=1)),axis=0).shift(2).reindex(dates)[['energy','food','raw','metals']].to_numpy()
    w=pd.read_csv(R/'third/data/trade_weights.csv').pivot(index='currency',columns='sector',values='net_weight').reindex(index=CC,columns=['energy','food','raw','metals']).to_numpy()
    G=np.repeat(sr.mean(axis=1)[:,None],C,axis=1);specific=sr@w.T-G*w.sum(axis=1)
    Y=np.full((T,C),np.nan);Y[:-60]=s[60:]-s[:-60]
    pr,a=ejr_extension(np.stack([q,G,specific],axis=2),Y,60,start=int(np.flatnonzero(dates>=pd.Period('2010-01'))[0]))
    return pr,a
def make_policies(ix=None,quant=.8,gate_cut=.02,tenure=12,forecast_mix=.5,gate_mode='absolute'):
    ix=list(range(C)) if ix is None else list(ix)
    wc=np.zeros((T,C));wc[:,ix]=rank_weights(carry[:,ix]);ej=f.copy()
    agg=np.sum(wc*np.nan_to_num(carry-ej/60),axis=1)
    den=pd.Series(np.where(z['active'],agg,np.nan)).expanding(min_periods=24).median().shift(1).to_numpy()
    size=np.clip(agg/np.maximum(den,.0001),0,1)
    hurdle=gate_cut if gate_mode=='absolute' else (0 if gate_mode=='zero' else .5*12*den)
    gate=(pd.Series(agg).rolling(6).mean().to_numpy()*12>hurdle).astype(float)
    struct=D['structure'];slim=pastq(struct,quant);badstruct=struct>slim
    # Direction-specific hazards, independent of the currently favoured interest sign.
    longprice=-D['momentum'];shortprice=-longprice
    priceL=longprice>pastq(longprice,quant);priceS=shortprice>pastq(shortprice,quant)
    delta=np.sign(carry)*(P['erased_12__structure']-P['erased_12__Base_for__structure'])
    riskL=(delta>np.maximum(pastq(delta,quant),0));riskS=(-delta>np.maximum(pastq(-delta,quant),0))
    normal=z['active']&np.isfinite(slim[:,ix]).all(axis=1)&np.isfinite(size)
    full=normal&np.isfinite(pastq(delta,quant)[:,ix]).all(axis=1)&np.isfinite(pastq(-delta,quant)[:,ix]).all(axis=1)
    normal &=dates>=pd.Period('2013-01');full &=normal
    pairstruct=np.ones((T,C));pairprice=np.ones((T,C));pairrisk=np.ones((T,C))
    orders=[np.asarray(ix)[np.argsort(carry[t,ix],kind='stable')] for t in range(T)]
    for t,o in enumerate(orders):
        for lo,hi in zip(o[:2],o[-2:][::-1]):
            if badstruct[t,lo] or badstruct[t,hi]:pairstruct[t,[lo,hi]]=0
            if priceS[t,lo] or priceL[t,hi]:pairprice[t,[lo,hi]]=0
            if riskS[t,lo] or riskL[t,hi]:pairrisk[t,[lo,hi]]=0
    def cohorts(entry_size,entrystruct=False,exit_risk=False,exit_struct=False,ready=full):
        out=np.zeros((T,C));alive=[];events=[]
        for t in range(T):
            if not ready[t]:continue
            keep=[]
            for j,lo,hi,a in alive:
                expiry=t-j>=tenure;risk=exit_risk and (riskS[t,lo] or riskL[t,hi]);structure=exit_struct and (badstruct[t,lo] or badstruct[t,hi])
                if expiry or risk or structure:events.append(dict(origin=str(dates[t]),entry=str(dates[j]),short=CC[lo],long=CC[hi],age=t-j,cause='expiry' if expiry else ('risk' if risk else 'structure')))
                else:keep.append((j,lo,hi,a))
            alive=keep
            for lo,hi in zip(orders[t][:2],orders[t][-2:][::-1]):
                ok=(not entrystruct or not (badstruct[t,lo] or badstruct[t,hi])) and (not exit_risk or not(riskS[t,lo] or riskL[t,hi]))
                if ok:alive.append((t,lo,hi,.25*entry_size[t]/tenure))
            for j,lo,hi,a in alive:out[t,lo]-=a;out[t,hi]+=a
        return out,events
    co,ev0=cohorts(np.ones(T),ready=full)
    colong,_=cohorts(np.ones(T),ready=normal)
    riskco,ev1=cohorts(np.ones(T),exit_risk=True)
    integrated,ev2=cohorts(size,True,True,True)
    blended=carry-((1-forecast_mix)*f+forecast_mix*Fcommodity)/60
    aggb=np.sum(wc*np.nan_to_num(blended),axis=1);db=pd.Series(np.where(normal,aggb,np.nan)).expanding(min_periods=24).median().shift(1).to_numpy()
    bsize=np.clip(aggb/np.maximum(db,.0001),0,1)
    rank=np.zeros((T,C));rank[:,ix]=rank_weights((carry-f/60)[:,ix])
    out={'Cash':np.zeros((T,C)),'Carry':wc,'EJR_rank':rank,'EJR_size':wc*size[:,None],'EJR_gate':wc*gate[:,None],
         'Size_structure':wc*size[:,None]*pairstruct,'Gate_price':wc*gate[:,None]*pairprice,'Cohort_base':co,'Cohort_long':colong,'Cohort_risk':riskco,'Integrated_cohort':integrated,
         'All_filters':wc*size[:,None]*pairstruct*pairprice*pairrisk,'Commodity_blend':wc*bsize[:,None]}
    out['Equal_modules']=(out['Size_structure']+out['Gate_price']+out['Cohort_risk'])/3
    out['Core_satellite']=.5*out['Carry']+.5*out['Equal_modules']
    out['Two_modules']=(out['Size_structure']+out['Gate_price'])/2
    for name,w in out.items():
        ready=full if name in ['Cohort_base','Cohort_risk','Integrated_cohort','All_filters','Equal_modules','Core_satellite'] else normal
        w[~ready]=0;out[name]=np.nan_to_num(w)
    return out,normal,full,dict(cohort_base=ev0,cohort_risk=ev1,integrated=ev2)
Fcommodity,faudit=third_forecast()
def stats(b,m):
    a=metrics(b.net[m],b.cash[m]);ex=(b.net-b.cash).to_numpy()[m]
    for g in [3,5,10]:a[f'ce{g}']=12*(ex.mean()-.5*g*ex.var(ddof=1))
    a.update(exposure=b.gross_exposure[m].mean(),turnover=b.turnover[m].mean()*12,cost_ann=b.cost[m].mean()*12,borrow_ann=b.borrow[m].mean()*12)
    a['worst36']=float(pd.Series(ex).rolling(36).mean().min()*12) if len(ex)>=36 else np.nan
    return a
def book(w,start,cost=1,borrow=50,execution_lag=1):
    w=w.copy();w[dates<pd.Period(start)-2]=0
    b,target,contrib=run_book(w,fx,rates,cost_bps=costs*cost,borrow_bps=borrow,execution_lag=execution_lag);return b,target,contrib
