from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from model import *
import json
W,_,_,_=make_policies();start=json.loads((H/'cache/design.json').read_text())['common_start'];m=dates>=pd.Period(start);n=m.sum()
names=[x for x in W if x not in ['Cash','Carry']];base=book(W['Carry'],start)[0];cash=base.cash.to_numpy()[m];r0=base.net.to_numpy()[m]
net=np.stack([book(W[x],start)[0].net.to_numpy()[m] for x in names],axis=1)
out=[];risk=[];tests=[]
def measures(r):
    nav=np.cumprod(1+r,axis=1);nav=np.concatenate([np.ones((r.shape[0],1)),nav],axis=1);dd=(nav/np.maximum.accumulate(nav,axis=1)-1).min(axis=1)
    return r.std(axis=1,ddof=1)*np.sqrt(12),dd
for L in [12,36]:
    rng=np.random.default_rng(20260913+L);idx=((rng.integers(n,size=(3999,int(np.ceil(n/L)),1))+np.arange(L))%n).reshape(3999,-1)[:,:n]
    diff=net-r0[:,None];boot=diff[idx].mean(axis=1)*12;se=boot.std(axis=0,ddof=1);obs=diff.mean(axis=0)*12/np.maximum(se,1e-10);centered=(boot-12*diff.mean(axis=0))/np.maximum(se,1e-10);maxstat=centered.max(axis=1)
    for j,name in enumerate(names):
        lo,hi=np.quantile(boot[:,j],[.025,.975]);tests.append(dict(name=name,block=L,annual_difference=12*diff[:,j].mean(),low=lo,high=hi,max_t_p=(1+np.sum(maxstat>=obs[j]))/(len(maxstat)+1),n=n,family_size=len(names)))
    for name in ['EJR_gate','Size_structure','Gate_price','Cohort_risk','Equal_modules','Two_modules','Core_satellite','Integrated_cohort','Commodity_blend']:
        rr=book(W[name],start)[0];bname='Cohort_base' if name in ['Cohort_risk','Integrated_cohort'] else 'Carry';bb=book(W[bname],start)[0]
        ratio=rr.gross_exposure[m].mean()/bb.gross_exposure[m].mean()
        for control,b in [('base',bb),('expost',book(W[bname]*ratio,start)[0])]:
            a=rr.net.to_numpy()[m];b=b.net.to_numpy()[m];e=a-cash;f=b-cash
            for gamma in [3,5,10]:
                ce=12*(e.mean()-.5*gamma*e.var(ddof=1)-f.mean()+.5*gamma*f.var(ddof=1))
                ce_boot=12*(e[idx].mean(axis=1)-.5*gamma*e[idx].var(axis=1,ddof=1)-f[idx].mean(axis=1)+.5*gamma*f[idx].var(axis=1,ddof=1));lo,hi=np.quantile(ce_boot,[.025,.975])
                out.append(dict(name=name,benchmark=bname,control=control,block=L,gamma=gamma,ce_difference=ce,low=lo,high=hi))
            va,da=measures(a[idx]);vb,db=measures(b[idx]);av,ad=measures(a[None]);bv,bd=measures(b[None])
            for measure,actual,d in [('volatility',av[0]-bv[0],va-vb),('drawdown',ad[0]-bd[0],da-db)]:
                lo,hi=np.quantile(d,[.025,.975]);risk.append(dict(name=name,control=control,block=L,measure=measure,difference=actual,low=lo,high=hi))
save(tests,'search_adjustment');save(out,'economic_intervals');save(risk,'risk_intervals')
# Netting: compare executable combined weights with accounting as separate accounts.
modules=['Size_structure','Gate_price','Cohort_risk'];components=[book(W[x],start)[0] for x in modules];combined=book(W['Equal_modules'],start)[0];row=[]
for field in ['net','cost','borrow','gross_exposure']:
    sep=sum(b[field].to_numpy() for b in components)/3;row.append(dict(field=field,combined=combined[field].to_numpy()[m].mean(),separate=sep[m].mean(),difference=(combined[field].to_numpy()[m]-sep[m]).mean()))
save(row,'netting');pd.DataFrame(net-r0[:,None],columns=names).corr().to_csv(H/'tables/active_correlations.csv')
print('Inference',len(tests),len(out),len(risk))
