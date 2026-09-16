from pathlib import Path
import sys,json,hashlib
sys.path.insert(0,str(Path(__file__).resolve().parent))
from model import *
checks=[]
def ck(name,x):
    assert bool(x),name;checks.append(dict(check=name,result='PASS'))
W,normal,full,events=make_policies();saved=dict(np.load(H/'cache/weights.npz'))
ck('Reproduction of every policy',all(np.allclose(W[n],saved[n]) for n in W))
ck('Neutral net exposure',all(np.max(np.abs(w.sum(axis=1)))<1e-12 for w in W.values()))
ck('Gross exposure never exceeds one',all(np.max(np.abs(w).sum(axis=1))<=1+1e-12 for w in W.values()))
ck('Finite weights',all(np.isfinite(w).all() for w in W.values()))
ck('No positions before admissible signals',all(np.all(w[~normal]==0) for w in W.values()))
ck('Risk modules do not start early',all(np.all(W[n][~full]==0) for n in ['Cohort_base','Cohort_risk','Equal_modules','Integrated_cohort','All_filters']))
ck('Equal ensemble at weights, before costs',np.allclose(W['Equal_modules'][full],((W['Size_structure']+W['Gate_price']+W['Cohort_risk'])/3)[full]))
ck('Core satellite fixed half allocation',np.allclose(W['Core_satellite'][full],(.5*W['Carry']+.5*W['Equal_modules'])[full]))
# Perturb all signal inputs after a historical date and regenerate the policies.
import model
cut=260;original={n:getattr(model,n) for n in ['f','Fcommodity','carry','D','P']}
model.f=model.f.copy();model.f[cut:]+=10;model.Fcommodity=model.Fcommodity.copy();model.Fcommodity[cut:]-=10;model.carry=model.carry.copy();model.carry[cut:]+=.1
model.D={k:v.copy() for k,v in D.items()};model.P={k:v.copy() for k,v in P.items()}
for d in [model.D,model.P]:
    for k,v in d.items():
        if v.shape[0]==T:v[cut:]+=100
altered,_,_,_=model.make_policies()
for n,v in original.items():setattr(model,n,v)
ck('Future corruption cannot change past weights',all(np.allclose(W[n][:cut],altered[n][:cut]) for n in W))
old=pd.read_csv(R/'third/tables/predictions.csv.gz');a=old[(old.task=='B_FX_60')&(old.model=='REJR_Specific')]
repro=np.array([Fcommodity[dates.get_loc(pd.Period(r.origin)),CC.index(r.unit)] for r in a.itertuples()])
ck('Commercial forecast reproduces third study',np.allclose(repro,a.pred,atol=1e-8))
aud=pd.read_csv(H/'tables/commodity_audit.csv');ck('Commercial labels mature before forecast',(aud.last_available<aud.origin).all())
sel=pd.read_csv(H/'tables/selection_audit.csv');ck('Selector only sees earlier returns',(sel.last_return<sel.origin).all())
pair=np.load(H/'cache/pair.npz');from engine import oos
pr,aa=oos(pair['Z'],pair['Y'],13,min_dates=36);ck('Joint-pair forecast reproduced',np.allclose(np.clip(pr,.01,.99),pair['aug'],equal_nan=True))
pa=pd.read_csv(H/'tables/pair_audit.csv');ck('Joint-pair labels mature before fit',(pa.last_available<pa.origin).all())
ck('Joint-pair portfolio neutrality',np.max(np.abs(pair['weights'].sum(axis=1)))<1e-12)
start='2018-04';mask=dates>=pd.Period(start);m=pd.read_csv(H/'tables/metrics.csv')
for name in ['Carry','Equal_modules','Cohort_base','Cohort_risk']:
    b,t,c=book(W[name],start);row=m[(m.window=='common')&(m.period=='all')&(m.name==name)].iloc[0]
    ck('Reported metrics '+name,abs(stats(b,mask)['cagr']-row.cagr)<1e-8)
    ck('Delayed execution '+name,np.allclose(t[2:],np.where((dates[:-2]>=pd.Period(start)-2)[:,None],W[name][:-2],0)))
    ck('Funding and transaction ledger '+name,np.allclose(b.net,b.cash+c.sum(axis=1)-b.cost))
    b2,_,_=book(W[name],start,cost=2);ck('Costs monotone '+name,b2.nav.iloc[-1]<b.nav.iloc[-1])
at=pd.read_csv(H/'tables/attribution.csv');cols=['FX','Interest','Interaction','Borrow','Trading']
for name in ['Carry','Equal_modules','Cohort_risk']:
    total=at[(at.window=='common')&(at.name==name)&at.component.isin(cols)].annual.sum();r=m[(m.window=='common')&(m.period=='all')&(m.name==name)].mean_excess.iloc[0];ck('Exact return attribution '+name,abs(total-r)<1e-8)
for key in ['cohort_base','cohort_risk','integrated']:
    a=pd.DataFrame(events[key]);ck('Cohort age and expiry '+key,(a.age>0).all() and (a.age<=12).all())
    ck('Closed cohort legs not reopened as same entry '+key,not a.duplicated(['entry','long','short']).any())
hedges=dict(np.load(H/'cache/hedge_rules.npz'));ck('Hedge ratios bounded',all(np.nanmin(v)>=0 and np.nanmax(v)<=1 for v in hedges.values()))
hr=pd.read_csv(H/'tables/hedge_returns.csv');u=hr[(hr.asset=='BIL')&(hr.name=='Unhedged')].set_index('month');v=hr[(hr.asset=='SPY')&(hr.name=='Unhedged')].set_index('month')
for n in ['Half','Full','EJR_FX','Equal_signals']:
    a=hr[(hr.asset=='BIL')&(hr.name==n)].set_index('month');b=hr[(hr.asset=='SPY')&(hr.name==n)].set_index('month')
    ck('Same hedge overlay across assets '+n,np.allclose((a.net-u.net).iloc[:-1],(b.net-v.net).iloc[:-1]))
old=json.loads((H/'previous_hashes.json').read_text());ck('All previous files unchanged',all(hashlib.sha256((R/f).read_bytes()).hexdigest()==h for f,h in old.items()))
save(checks,'validation');print(len(checks),'checks passed')
