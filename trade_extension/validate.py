from pathlib import Path
import sys,json,hashlib
sys.path.insert(0,str(Path(__file__).resolve().parent))
from core import *
import core
from strategies import hazards,pair_keep
checks=[]
def ck(name,value):
    assert bool(value),name
    checks.append(dict(check=name,result='PASS'))
D=trade_data();P=dict(np.load(H/'cache/predictions.npz'))
ck('Monthly observations unique and consecutive',dates.is_unique and len(pd.period_range(dates[0],dates[-1],freq='M'))==T)
ck('Same original universe',CC==['BRL','EUR','JPY','GBP','CAD','SEK'])
ck('FX and rates complete',np.isfinite(fx).all().all() and np.isfinite(rates).all().all())
ck('Known real base uses only t-2 FX and CPI',np.allclose(knownq[2:],qactual[:-2],equal_nan=True))
old=pd.read_csv(R/'third/data/trade_weights.csv').pivot(index='currency',columns='sector',values='net_weight').reindex(index=CC,columns=SECT).to_numpy()
yr,rw,sw,tt=annual_data();ck('Fixed pre-sample weights reproduce third study',np.allclose(old,np.mean(rw[:3],axis=0)))
ck('Dynamic weights use only annual data Y-2',all(np.allclose(D['W'][t],sw[np.where(yr==date.year-2)[0][0]]) for t,date in enumerate(dates)))
ck('Trade signal complete without future interpolation',np.isfinite(D['chain']).all())
origin=2018
original_annual=core.annual_data
def corrupt():
    y,r,w,t=original_annual();r[y>origin-2]+=100;w[y>origin-2]+=100;t[y>origin-2]+=100;return y,r,w,t
core.annual_data=corrupt
evil=core.trade_data();core.annual_data=original_annual
for k in ['W','chain','annual','structure','forecast_structure','repricing']:
    ck('Future annual corruption leaves earlier '+k,np.allclose(D[k][dates.year<=origin],evil[k][dates.year<=origin],equal_nan=True))
base=np.stack([center(knownq),diff(knownq,12)],axis=2);extra=np.stack([center(D['chain']),D['momentum']],axis=2);X=np.concatenate([base,extra],axis=2);Y=P['real_36__actual']
p,a=oos(X,Y,36,release=2);ck('Saved macro forecasts exactly reproduced',np.allclose(p,P['real_36__dynamic'],equal_nan=True))
cut=245;XX=X.copy();YY=Y.copy();XX[cut+1:]+=50;YY[cut+1-38:]+=50
pr,_=oos(XX,YY,36,release=2)
ck('Unavailable future labels and predictors do not change forecasts',np.allclose(p[:cut+1],pr[:cut+1],equal_nan=True))
B=base.copy();B[~np.isfinite(X).all(axis=2)]=np.nan;bp,ba=oos(B,Y,36,release=2)
ck('Augmented and base models train on identical rows',a==ba)
ck('Saved matched benchmark reproduced',np.allclose(bp,P['real_36__Base_for__dynamic'],equal_nan=True))
ejr,_,_,_=forecast(s,q,60);ck('EJR original preserved numerically',np.allclose(ejr['ejr'],P['nominal_60__EJR'],equal_nan=True))
audit=pd.read_csv(H/'tables/audit.csv');m=audit.origin.notna()
ck('Every monthly fit uses labels available before origin',(audit.loc[m,'last_available']<audit.loc[m,'origin']).all())
aa=audit[audit.kind=='annual_structure'];ck('Annual forecasts use only released training targets',(aa.last_training_target_year<=aa.last_source_year).all() and (aa.last_source_year<=aa.origin_year-2).all())
weights=dict(np.load(H/'cache/weights.npz'));ready=dict(np.load(H/'cache/ready.npz'))
ck('All strategies preserve long-short neutrality',all(np.max(np.abs(w.sum(axis=1)))<1e-12 for w in weights.values()))
ck('No strategy reallocates withdrawn gross risk',all(np.max(np.abs(w).sum(axis=1))<=1+1e-10 for w in weights.values()))
ck('Positions zero before signal availability',all(np.all(w[~ready[k]]==0) for k,w in weights.items()))
w=weights['Carry__structure_observed'];b,target,_=run_book(w,fx,rates,cost_bps=costs)
ck('Execution uses signal two rows before realized return',np.allclose(target[2:],w[:-2]) and np.all(target[:2]==0))
ck('Nonnegative cost and funding-spread charges',(b.cost>=0).all() and (b.borrow>=0).all())
b2,_,_=run_book(w,fx,rates,cost_bps=2*costs);ck('Duplicating costs reduces terminal wealth',b2.nav.iloc[-1]<=b.nav.iloc[-1])
hz=hazards['structure_observed'];future=hz.copy();future[245:]+=10
ck('Future alert data cannot alter prior thresholds',np.allclose(quantile_past(hz)[:245],quantile_past(future)[:245],equal_nan=True))
obs=pd.read_csv(H/'tables/predictions.csv.gz');ck('Prediction keys unique',not obs.duplicated(['task','country','origin','model']).any())
mm=pd.read_csv(H/'tables/prediction_metrics.csv');cell=obs[(obs.task=='erased_12')&(obs.model=='structure')]
ratio=np.sqrt(np.mean((cell.actual-cell.pred)**2)/np.mean((cell.actual-cell.base_pred)**2));saved=mm[(mm.task=='erased_12')&(mm.model=='structure')&(mm.country=='POOL')&(mm.period=='all')].ratio.iloc[0]
ck('Reported paired score recalculates from observations',abs(ratio-saved)<1e-8)
ck('Risk probabilities inside unit interval',obs[obs.task.str.contains('erased|tail')].pred.between(.01-1e-10,.99+1e-10).all())
sm=pd.read_csv(H/'tables/strategy_metrics.csv');ep=sm[sm.period=='all'].pivot(index='name',columns='control',values='exposure')
ck('Ex-post diagnostic matches realized mean gross exposure',np.allclose(ep.rule,ep.expost_exposure,atol=1e-8))
ck('Long horizon significance suppressed',mm[mm.n_dates<3*np.maximum(12,mm.h+2)].p.isna().all())
for x in json.loads((H/'data/manifest.json').read_text()):ck('Raw download hash '+x['indicator'],hashlib.sha256((H/x['file']).read_bytes()).hexdigest()==x['sha256'])
old=json.loads((H/'previous_hashes.json').read_text());ck('All previous deliverables preserved',all(hashlib.sha256((R/x).read_bytes()).hexdigest()==sha for x,sha in old.items()))
save(checks,'validation');print(len(checks),'checks PASS')
