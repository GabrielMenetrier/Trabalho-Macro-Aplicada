"""Immutable inputs and strictly historical trade signals."""
from pathlib import Path
import sys,json,os
R=Path(__file__).resolve().parents[1];H=R/'trade_extension'
sys.path.insert(0,str(R/'src'));sys.path.insert(0,str(R/'third'))
os.environ['MPLCONFIGDIR']=str(R/'tmp/matplotlib')
import numpy as np,pandas as pd
from models import features,forecast,rank_weights,run_book,metrics
from engine import fit_predict,oos,ejr_extension
CC=['BRL','EUR','JPY','GBP','CAD','SEK'];ISO=['BRA','DEU','JPN','GBR','CAN','SWE'];SECT=['energy','food','raw','metals']
for folder in ['data','tables','cache','figures']:(H/folder).mkdir(exist_ok=True)
def read(p):
    a=pd.read_csv(p,index_col=0);a.index=pd.PeriodIndex(a.index,freq='M');return a
fx=read(R/'data/processed/fx.csv')[CC].loc['1999-10':'2026-08'];dates=fx.index;T,C=fx.shape
cpi=read(R/'data/processed/cpi.csv');rates=read(R/'data/processed/rates.csv').reindex(dates)[CC+['USD']]
s=np.log(fx.to_numpy());q=features(read(R/'data/processed/fx.csv')[CC],cpi).reindex(dates).to_numpy()
cpif=cpi.ffill(limit=1)
qactual=(np.log(fx)+np.log(cpif.USD.reindex(dates)).to_numpy()[:,None]-np.log(cpif[CC].reindex(dates))).to_numpy()
knownq=pd.DataFrame(qactual).shift(2).to_numpy();qdev=q-pd.DataFrame(q).expanding().mean().to_numpy()
z=np.load(R/'secondary/cache/core.npz');wc=z['wc'];carry=z['carry'];f=z['f'];ffx=z['ffx'];score=z['score'];active=z['active']
mom=-pd.DataFrame(s).diff(12).to_numpy()/12;vol=pd.DataFrame(-np.diff(s,axis=0,prepend=s[[0]])).rolling(12).std().to_numpy();sgn=np.sign(carry)
costs=np.array([10,2,2,2,2,3])
def save(a,name):pd.DataFrame(a).to_csv(H/'tables'/(name+'.csv'),index=False,float_format='%.10g')
def center(a):return a-pd.DataFrame(a).expanding().mean().to_numpy()
def lag(a,k):return pd.DataFrame(a).shift(k).to_numpy(copy=True)
def diff(a,k):return a-lag(a,k)
def annual_data():
    raw={};obs=[]
    for p in (H/'data/raw').glob('*.json'):
        for r in json.loads(p.read_text())[1]:
            raw[r['countryiso3code'],int(r['date']),p.stem]=r['value'];obs.append(dict(iso=r['countryiso3code'],year=int(r['date']),indicator=p.stem,value=r['value']))
    years=np.arange(1994,2026);w=np.full((len(years),C,4),np.nan);tt=np.full((len(years),C),np.nan)
    for j,y in enumerate(years):
        for c,iso in enumerate(ISO):
            v=raw.get((iso,int(y),'TT.PRI.MRCH.XD.WD'));tt[j,c]=np.log(v) if v is not None and v>0 else np.nan
            x=raw.get((iso,int(y),'TX.VAL.MRCH.CD.WT'));m=raw.get((iso,int(y),'TM.VAL.MRCH.CD.WT'))
            for k,g in enumerate(['FUEL','FOOD','AGRI','MMTL']):
                sx=raw.get((iso,int(y),f'TX.VAL.{g}.ZS.UN'));sm=raw.get((iso,int(y),f'TM.VAL.{g}.ZS.UN'))
                if None not in [x,m,sx,sm] and x+m>0:w[j,c,k]=(x*sx-m*sm)/100/(x+m)
    smooth=np.stack([pd.DataFrame(w[:,:,k]).rolling(3,min_periods=3).mean().to_numpy() for k in range(4)],axis=2)
    pd.DataFrame(obs).to_csv(H/'data/annual_inputs.csv',index=False)
    return years,w,smooth,tt
def trade_data(delay=2,penalty=10):
    years,raw,w,tt=annual_data();W=np.full((T,C,4),np.nan);A=np.full((T,C),np.nan);obschange=np.full((T,C),np.nan);predw=np.full((T,C,4),np.nan);aud=[];annualpred=[]
    # Each annual row appears once per country, not twelve times.
    for year in np.unique(dates.year):
        ii=np.flatnonzero(years<=year-delay);a=int(ii[-1]);now=w[a]
        X=np.concatenate([w,w-np.roll(w,3,axis=0)],axis=2);X[:5]=np.nan
        # Predict next calendar year's composition, from the last available year.
        h=delay+1;target=np.full_like(w,np.nan);target[:-h]=w[h:]-w[:-h]
        cut=a-h+1;valid=np.isfinite(X[:cut]).all(axis=2)&np.isfinite(target[:cut]).all(axis=2)
        wp=np.full((C,4),np.nan)
        if cut>0 and np.sum(valid.any(axis=1))>=8 and np.min(valid.sum(axis=0))>=8 and np.isfinite(X[a]).all():
            ti,ci=np.where(valid)
            for k in range(4):wp[:,k]=fit_predict(X[ti,ci],target[ti,ci,k],X[a],penalty,ci,np.arange(C),C)
            aud.append(dict(kind='annual_structure',origin_year=int(year),last_source_year=int(years[a]),last_training_target_year=int(years[ti.max()+h]),n_dates=len(np.unique(ti))))
            if a+h<len(years):
                for c in range(C):
                    for k in range(4):annualpred.append(dict(year=int(year),country=CC[c],sector=SECT[k],actual=target[a,c,k],ridge=wp[c,k],persistence=0.,trend=(w[a,c,k]-w[a-3,c,k])/3*h))
        loc=dates.year==year;W[loc]=now;predw[loc]=wp
        if a>=3:obschange[loc]=np.abs(w[a]-w[a-3]).sum(axis=1)
        for c in range(C):
            ix=ii[np.isfinite(tt[ii,c])];A[loc,c]=tt[ix[-1],c] if len(ix) and years[ix[-1]]>=year-delay-2 else np.nan
    # Fixed weight chain starts with the same arbitrary zero as the variable chain.
    b=read(R/'third/data/sector_logprices.csv').reindex(dates)[SECT].to_numpy()
    pc=lag(b,1);dp=np.vstack([np.zeros(4),np.diff(b,axis=0)]);dp=lag(dp,1);dp[0]=0
    fixed=np.mean(raw[:3],axis=0)
    inc=np.einsum('tck,tk->tc',W,dp);inc[0]=0
    assert np.isfinite(inc).all(),'Missing weights: no future filling allowed'
    chain=np.cumsum(inc,axis=0);fix=np.cumsum(dp@fixed.T,axis=0)
    globalprice=np.mean(pc,axis=1);G=np.repeat(globalprice[:,None],C,axis=1)
    # Structure repricing is a scenario using relative prices versus trailing 36m,
    # not a unit-dependent jump of w * absolute log prices.
    rel=pc-pd.DataFrame(pc).rolling(36,min_periods=12).mean().to_numpy()
    repricing=np.einsum('tck,tk->tc',predw,rel)
    return dict(W=W,annual=A,chain=chain,fixed=fix,momentum=diff(chain,12),G=center(G),structure=obschange,forecast_structure=np.abs(predw).sum(axis=2),repricing=repricing,predw=predw,audit=aud,annual_predictions=annualpred)
def quantile_past(a,quant=.8,min_history=36):
    return pd.DataFrame(a).expanding(min_periods=min_history).quantile(quant).shift(1).to_numpy()
