from pathlib import Path
import sys,json
sys.path.insert(0,str(Path(__file__).resolve().parent))
from model import *
W,normal,full,ev=make_policies();start=json.loads((H/'cache/design.json').read_text())['common_start'];mask=dates>=pd.Period(start)
selected=['Carry','EJR_size','EJR_gate','Size_structure','Gate_price','Cohort_base','Cohort_risk','Equal_modules','Core_satellite','Integrated_cohort','All_filters','Commodity_blend','Two_modules']
rows=[];controls=[];scenarios=[]
for variant,ix,quant,cut,tenure,mix in [('Base',None,.8,.02,12,.5),('q70',None,.7,.02,12,.5),('q90',None,.9,.02,12,.5),('Gate1pct',None,.8,.01,12,.5),('Gate3pct',None,.8,.03,12,.5),('Tenure6',None,.8,.02,6,.5),('Tenure24',None,.8,.02,24,.5),('NoBRL',list(range(1,6)),.8,.02,12,.5),('NoEUR',[0,2,3,4,5],.8,.02,12,.5),('Commodity25',None,.8,.02,12,.25),('Commodity75',None,.8,.02,12,.75)]:
    ws,_,_,_=make_policies(ix,quant,cut,tenure,mix)
    for name in selected:
        b,_,_=book(ws[name],start)
        for period,m in [('all',mask),('recent',mask&(dates>=pd.Period('2019-01')))]:rows.append(dict(variant=variant,name=name,period=period,**stats(b,m)))
for name in selected:
    for cost,borrow,lag in [(2,50,1),(4,50,1),(1,150,1),(1,300,1),(1,50,2)]:
        b,_,_=book(W[name],start,cost,borrow,lag);rows.append(dict(variant=f'cost{cost}_borrow{borrow}_lag{lag}',name=name,period='all',**stats(b,mask)))
    # Position volatility estimated with trailing realized currency excess returns,
    # before execution. Only reduce exposure; never scale above the budget of one.
    rm=np.expm1(np.log1p(rates/100)/12);r=np.zeros((T,C));r[1:]=(1+rm[:-1,:C])*fx[:-1]/fx[1:]-1-rm[:-1,-1,None]
    for targetvol in [.03,.04,.05]:
        scale=np.ones(T)
        for t in range(24,T):
            cov=np.cov(r[t-23:t+1].T,ddof=1);v=np.sqrt(max(0,W[name][t]@cov@W[name][t])*12);scale[t]=min(1,targetvol/max(v,.001))
        b,_,_=book(W[name]*scale[:,None],start);rows.append(dict(variant=f'vol{targetvol}',name=name,period='all',**stats(b,mask)))
    if name in ['Carry','Cohort_base']:continue
    b,_,_=book(W[name],start);base_name='Cohort_base' if name in ['Cohort_risk','Integrated_cohort'] else 'Carry';base,_,_=book(W[base_name],start)
    ratio=b.gross_exposure[mask].mean()/base.gross_exposure[mask].mean()
    exposure=np.abs(W[name]).sum(axis=1);be=np.abs(W[base_name]).sum(axis=1)
    ready=full if name in ['Cohort_risk','Integrated_cohort','All_filters','Equal_modules','Core_satellite'] else normal
    pe=pd.Series(np.where(ready,exposure,0)).cumsum().shift(1).to_numpy();pb=pd.Series(np.where(ready,be,0)).cumsum().shift(1).to_numpy()
    past=np.divide(pe,pb,out=np.zeros(T),where=pb>0)
    for tag,scale in [('base',np.ones(T)),('expost',np.full(T,ratio)),('past',np.minimum(1,past)),('rule',None)]:
        bb=b if tag=='rule' else book(W[base_name]*scale[:,None],start)[0]
        controls.append(dict(name=name,base=base_name,control=tag,**stats(bb,mask)))
    # Contribution of prespecified calendar episodes; no causal event attribution.
    for episode,a,e in [('2018','2018-04','2018-12'),('2019','2019-01','2019-12'),('2020_2021','2020-01','2021-12'),('2022','2022-01','2022-12'),('2023_2026','2023-01','2026-08')]:
        m=mask&(dates>=pd.Period(a))&(dates<=pd.Period(e))
        scenarios.append(dict(name=name,episode=episode,excess=12*(b.net[m]-b.cash[m]).mean(),base_excess=12*(base.net[m]-base.cash[m]).mean(),vol=b.net[m].std()*np.sqrt(12),exposure=b.gross_exposure[m].mean(),n=int(m.sum())))
save(rows,'robustness');save(controls,'exposure_controls');save(scenarios,'episodes')
print('Robustness rows',len(rows))
