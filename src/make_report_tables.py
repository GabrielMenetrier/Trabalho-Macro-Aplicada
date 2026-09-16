from pathlib import Path
import pandas as pd
import numpy as np
ROOT=Path(__file__).resolve().parents[1]; OUT=ROOT/'report/tables'; OUT.mkdir(exist_ok=True,parents=True)
def get(n):return pd.read_csv(ROOT/f'output/tables/{n}.csv')
def esc(s):return str(s).replace('&',r'\&').replace('%',r'\%').replace('_',r'\_')
def f(v,d=2):return '--' if pd.isna(v) else f'{v:.{d}f}'.replace('.',',')
def pct(v):return f(v*100)
def write(name,headers,rows,fmt=None):
    fmt=fmt or 'l'+'r'*(len(headers)-1)
    lines=[r'\begin{tabular}{'+fmt+'}',r'\toprule',' & '.join(headers)+r' \\',r'\midrule']
    lines += [' & '.join(map(str,row))+r' \\' for row in rows]
    lines += [r'\bottomrule',r'\end{tabular}']
    (OUT/f'{name}.tex').write_text('\n'.join(lines),encoding='utf-8')

a=get('classroom_replication');a=a[a.spec=='SA_BLS']
write('replication',['Anos',r'$\beta$ nos slides',r'$\widehat\beta$','EP HAC',r'$R^2$','$N$'],
      [[int(r.h/12),f(r.slide_beta,3),f(r.beta,3),f(r.se,3),f(r.r2,3),int(r.n)] for r in a.itertuples()])
a=get('forecast_accuracy');a=a[(a.country=='POOL')&(a.model=='ejr')]
write('accuracy',['Anos','RMSE/RW',r'$R^2_{OOS}$','Origens','Sem sobrep.','Última origem'],
      [[int(r.h/12),f(r.rmse_ratio,3),f(r.r2_oos,3),r.n_dates,r.nonoverlap_approx,r.last] for r in a.itertuples()])
a=get('bootstrap_null'); b=a[a.null=='stationary_ar1'].set_index('h');c=a[a.null=='unit_root'].set_index('h')
write('bootstrap',['Anos',r'$p$: RER estacionário',r'$p$: raiz unitária',r'$p$ Holm mínimo'],
      [[int(h/12),f(b.loc[h,'p_boot'],3),f(c.loc[h,'p_boot'],3),f(min(b.loc[h,'p_holm'],c.loc[h,'p_holm']),3)] for h in b.index])
a=get('portfolio_metrics')
write('performance',['Carteira','Ret. a.a.','Vol. a.a.','Sharpe','Queda máx.','Final'],
      [[esc(r.strategy),pct(r.cagr),pct(r.vol),f(r.sharpe),pct(r.maxdd),f(100*r.final_nav)] for r in a.itertuples()])
a=get('subperiods');a=a[a.strategy=='EJR + carry']
write('subperiods',['Período','Meses','Ret. a.a.','Excesso a.a.','Sharpe','Queda máx.'],
      [[r.period,int(r.n),pct(r.cagr),pct(r.mean_excess),f(r.sharpe),pct(r.maxdd)] for r in a.itertuples()])
a=get('regimes')
write('regimes',['Condição conhecida antes da operação','Meses','Excesso a.a.','Vol. a.a.'],
      [[esc(r.regime),r.n,pct(r.mean_excess),pct(r.vol)] for r in a.itertuples()])
a=get('robustness')
write('robustness',['Variação','Custo $\times$','Spread (pb)','Ret. a.a.','Sharpe','Queda máx.'],
      [[esc(r.variant),int(r.cost_mult),int(r.borrow_bps),pct(r.cagr),f(r.sharpe),pct(r.maxdd)] for r in a.itertuples()])
a=get('portfolio_horizons')
write('horizon_portfolio',['Horizonte (anos)','Ret. a.a.','Vol. a.a.','Sharpe','Queda máx.'],
      [[int(r.h/12),pct(r.cagr),pct(r.vol),f(r.sharpe),pct(r.maxdd)] for r in a.itertuples()])
a=get('brl_metrics')
write('brl',['Carteira em reais','Ret. a.a.','Vol. a.a.','Sharpe','Queda máx.'],
      [[esc(r.strategy),pct(r.cagr),pct(r.vol),f(r.sharpe),pct(r.maxdd)] for r in a.itertuples()])
a=get('etf_metrics')
write('etfs',['Ativo','Regra','Ret. a.a.','Vol. a.a.','Queda máx.'],
      [[r.ticker,esc(r.rule),pct(r.cagr),pct(r.vol),pct(r.maxdd)] for r in a.itertuples()])
a=get('latest_scenarios');a=a[a.h==60].set_index('country').loc[['BRL','EUR','JPY','GBP','CAD','SEK']]
write('scenarios',[r'Moeda/$\mathrm{USD}$','Cotação inicial','Cenário 5 anos','Faixa ilustrativa'],
      [[esc(c),f(r.spot,3),f(r.median_scenario,3),f(r.band_low,3)+' a '+f(r.band_high,3)] for c,r in a.iterrows()])
print('Generated 12 LaTeX tables from CSV outputs.')
