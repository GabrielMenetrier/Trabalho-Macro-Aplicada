from pathlib import Path
import sys,json,hashlib
import numpy as np
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from models import forecast,features,rank_weights,run_book,metrics

def fixture():
    rng=np.random.default_rng(44); s=rng.normal(0,.02,(210,6)).cumsum(axis=0)
    q=s+np.arange(210)[:,None]*.001
    return s,q

def test_future_perturbation_does_not_change_past_forecasts():
    s,q=fixture(); baseline=forecast(s,q,24)[0]
    s[151:]+=25; q[151:]-=30; changed=forecast(s,q,24)[0]
    for m in baseline: np.testing.assert_allclose(baseline[m][:151],changed[m][:151],equal_nan=True)

def test_truncated_data_reproduces_full_forecast():
    s,q=fixture(); a=forecast(s,q,24)[0]; b=forecast(s[:151],q[:151],24)[0]
    for m in a: np.testing.assert_allclose(a[m][:151],b[m],equal_nan=True)

def test_training_labels_mature_before_origin():
    s,q=fixture(); _,_,n,last=forecast(s,q,60)
    assert all(last[t]<=t-1 for t in np.flatnonzero(n))
    t=150; x=q[:t-60]; y=s[60:t]-s[:t-60]; mu=q[:t+1].mean(axis=0)
    beta=np.sum((x-mu)*y)/np.sum((x-mu)**2)
    expected=beta*(q[t]-mu)
    np.testing.assert_allclose(forecast(s,q,60)[0]['ejr'][t],expected)

def test_price_rebasing_leaves_forecast_unchanged():
    s,q=fixture(); a=forecast(s,q,24)[0]; b=forecast(s,q+np.arange(6)*5,24)[0]
    for m in a: np.testing.assert_allclose(a[m],b[m],atol=1e-10,equal_nan=True)

def test_release_lag_and_missing_month_are_past_only():
    idx=pd.period_range('2020-01',periods=8,freq='M')
    cpi=pd.DataFrame({'USD':[100,101,102,np.nan,104,105,106,107],'BRL':100},index=idx)
    fx=pd.DataFrame({'BRL':5.},index=idx)
    a=features(fx,cpi,2)
    assert np.isclose(a.iloc[5,0],np.log(5*102/100))
    cpi.iloc[6:,0]=999
    np.testing.assert_allclose(a,features(fx,cpi,2),equal_nan=True)

def test_rank_budget_neutrality_and_invalid_signals():
    w=rank_weights([[1,2,3,4,5,6],[np.nan]*6])
    assert np.isclose(w[0].sum(),0); assert np.isclose(np.abs(w[0]).sum(),1)
    assert np.isclose(np.maximum(w[0],0).sum(),.5); assert np.all(w[1]==0)

def test_currency_direction_and_cash_accounting():
    fx=np.array([[5.],[5.],[5.],[4.]])
    w=np.ones_like(fx); r=np.zeros((4,2))
    b,_,_=run_book(w,fx,r,[0],0)
    assert np.isclose(b.net.iloc[-1],.25) # appreciation of BRL earns USD profit.
    b,_,_=run_book(-w,fx,r,[0],0)
    assert np.isclose(b.net.iloc[-1],-.25)
    r[:,-1]=12; b,_,_=run_book(w*0,fx,r,[0],0)
    assert np.isclose(b.net.iloc[-1],1.12**(1/12)-1)

def test_execution_lag_prevents_same_period_profits():
    w=np.array([[0.],[0.],[1.],[0.],[0.]])
    fx=np.array([[1.],[1.],[1.],[.5],[.5]])
    b,target,_=run_book(w,fx,np.zeros((5,2)),[0],0,1)
    assert target[3,0]==0 and target[4,0]==1
    assert np.isclose(b.net.sum(),0)

def test_costs_entry_drift_and_liquidation():
    w=np.ones((5,1)); fx=np.ones((5,1)); r=np.zeros((5,2))
    a,_,_=run_book(w,fx,r,[10],0)
    assert a.cost.sum()>.002 # entry, NAV drift, liquidation, all charged.
    assert a.net.sum()<0
    b,_,_=run_book(-w,fx,r,[10],100)
    assert b.borrow.sum()>0

def test_initial_drawdown_is_counted():
    m=metrics([-.1,.02],[0,0]); assert np.isclose(m['maxdd'],-.1)

def test_saved_timing_and_source_hashes():
    a=pd.read_csv(ROOT/'output/tables/timing_audit.csv')
    assert (a.latest_training_label<a.origin).all()
    delta=pd.PeriodIndex(a.origin,freq='M').asi8-pd.PeriodIndex(a.latest_training_origin,freq='M').asi8
    np.testing.assert_array_equal(delta,a.h+1)
    for row in json.loads((ROOT/'data/raw/manifest.json').read_text()):
        if 'error' not in row:
            assert hashlib.sha256((ROOT/'data/raw'/row['file']).read_bytes()).hexdigest()==row['sha256']

def test_actual_monthly_data_have_no_compressed_calendar():
    a=pd.read_csv(ROOT/'data/processed/fx.csv',index_col=0)
    idx=pd.PeriodIndex(a.index,freq='M').asi8
    assert (np.diff(idx)==1).all()
    c=pd.read_csv(ROOT/'data/processed/cpi.csv',index_col=0)
    assert np.isnan(c.loc['2025-10','USD']) # Preserve the actual missing CPI.

def test_effective_rates_and_etf_price_coverage():
    r=pd.read_csv(ROOT/'data/processed/rates.csv',index_col=0)
    assert np.isclose(r.loc['2026-08','EUR'],2.25) # Not Sep 16's future effective rate.
    assert r.loc['2013-05':'2016-08','JPY'].notna().all()
    e=pd.read_csv(ROOT/'data/processed/etf_adjusted_close.csv',index_col=0).loc['2010-02':'2026-08']
    assert (e>0).all().all() and e.notna().all().all()
    ret=pd.read_csv(ROOT/'output/tables/etf_returns.csv')
    assert ret.net.notna().all() and (ret.net>-1).all()
    assert ret.groupby(['ticker','rule']).size().eq(198).all()

def test_saved_portfolio_reconciles_contributions_and_nav():
    p=pd.read_csv(ROOT/'output/tables/portfolio_returns.csv')
    a=p[p.strategy.eq('EJR + carry')].set_index('month')
    c=pd.read_csv(ROOT/'output/tables/contributions_main.csv',index_col=0)
    np.testing.assert_allclose(a.net,a.cash+c.sum(axis=1)-a.cost,atol=2e-11)
    np.testing.assert_allclose(a.nav,(1+a.net).cumprod(),atol=1e-8)
    w=pd.read_csv(ROOT/'output/tables/weights_main.csv',index_col=0)
    np.testing.assert_allclose(w.sum(axis=1),0,atol=1e-12)
    np.testing.assert_allclose(w.abs().sum(axis=1),1,atol=1e-12)
