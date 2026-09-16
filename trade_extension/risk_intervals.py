from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from core import *
a=pd.read_csv(H/'tables/strategy_returns.csv.gz');rows=[]
def measures(x):
    nav=np.cumprod(1+x,axis=1);nav=np.c_[np.ones(len(x)),nav];dd=(nav/np.maximum.accumulate(nav,axis=1)-1).min(axis=1)
    cut=np.quantile(x,.05,axis=1);tail=x<=cut[:,None];es=np.where(tail,x,0).sum(axis=1)/tail.sum(axis=1)
    return dict(vol=x.std(axis=1,ddof=1)*np.sqrt(12),maxdd=dd,es95=es)
for name in ['Carry__structure_observed','EJR_size__structure_observed','Cohort__risk_increment','EJR_gate__price_observed']:
    p=a[a.name==name].pivot(index='month',columns='control',values='net');n=len(p)
    for bench in ['base','expost_exposure']:
        for L in [12,36]:
            rng=np.random.default_rng(20260911+L);ii=((rng.integers(n,size=(1499,int(np.ceil(n/L)),1))+np.arange(L))%n).reshape(1499,-1)[:,:n]
            x=p.rule.to_numpy();y=p[bench].to_numpy();ma=measures(x[ii]);mb=measures(y[ii]);oa=measures(x[None]);ob=measures(y[None])
            for measure in ma:
                lo,hi=np.quantile(ma[measure]-mb[measure],[.025,.975]);rows.append(dict(name=name,benchmark=bench,block=L,measure=measure,difference=(oa[measure]-ob[measure])[0],low=lo,high=hi,n=n))
save(rows,'risk_intervals');print('Risk intervals',len(rows))
