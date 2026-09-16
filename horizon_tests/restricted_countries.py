"""Three-currency portfolio experiment; protocol in RESTRICTED_PROTOCOL.md."""
from pathlib import Path
import sys, json, hashlib
import numpy as np
import pandas as pd

sys.stdout.reconfigure(encoding='utf-8')
R=Path(__file__).resolve().parents[1]; H=R/'horizon_tests'
source=(H/'run.py').read_text(encoding='utf-8'); b={'__file__':str(H/'run.py')}
exec(source.split("W={'Pairs_EJR'")[0],b)
exec(source[source.index('def schedule('):source.index('rows=[];rets=')],b)
CC=['BRL','EUR','CAD']; ids=[0,1,4]
# Reuse precisely the original accounting, scheduling and risk definitions,
# with only the investable arrays restricted to these three currencies.
b.update(CC=CC,C=3,fx=b['fx'][:,ids],rates=b['rates'][:,ids+[6]],
         carry=b['carry'][:,ids],le=b['le'][:,ids],long=b['long'][:,ids],cost=np.array([10,2,2]))
dates=b['dates']; T=b['T']; start=b['start']; needed=list(range(start,start+180,12))
inputs=[H/'tables/with_tot_forecasts.csv',R/'secondary/cache/core.npz',
        R/'ejr_trade_selected/tables/metrics.csv',R/'ejr_trade/tables/metrics.csv',
        H/'RESTRICTED_PROTOCOL.md',H/'run.py',R/'src/models.py',Path(__file__)]
hashes={str(p.relative_to(R)):hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs}
checks=[]
def ck(k,v):
    checks.append(dict(check=k,passed=bool(v)))
    assert v,k

forecast=pd.read_csv(inputs[0]); mt=pd.read_csv(inputs[2]); full=pd.read_csv(inputs[3])
selection=full[(full.h==60)&(full.scenario=='main')&(full.period=='all')&
               full.model.isin(['EJR','TOT_both'])&(full.country!='POOL')]
selection=selection.pivot(index='country',columns='model',values='rmse_rw').reset_index()
selection['eligible']=selection[['EJR','TOT_both']].min(axis=1)<1
ck('Six-country evidence selects precisely BRL EUR CAD',set(selection.loc[selection.eligible,'country'])==set(CC))
elig=[]
for cc in CC:
    rr=mt[(mt.h==60)&(mt.scenario=='fixed')&(mt.country==cc)].set_index('model')
    ejr=float(rr.loc['EJR','rmse_rw']); tt=float(rr.loc['TOT_LOG_LD','rmse_rw'])
    elig.append(dict(currency=cc,ejr_rmse_rw=ejr,tt_rmse_rw=tt,
                     eligible=min(ejr,tt)<1,tt_improves_ejr=tt<ejr,
                     matched_model='TOT_LOG_LD' if tt<ejr else 'EJR'))
ck('Every selected country beats no-change at 60m',all(r['eligible'] for r in elig))
ck('TT improves incrementally only in BRL',[r['currency'] for r in elig if r['tt_improves_ejr']]==['BRL'])
signals={k:np.zeros((T,3)) for k in ['Carry','EJR','TT_all','Matched']}
frows=[]
for t in needed:
    for sig,variant in [('EJR','EJR_trio'),('TT_all','EJR_TOT_trio')]:
        rr=forecast[(forecast.origin==str(dates[t]))&(forecast.variant==variant)].set_index('currency').reindex(CC)
        ck(f'Complete and unique forecast {sig} {dates[t]}',len(rr)==3 and rr.nominal_forecast_60m.notna().all())
        signals[sig][t]=rr.nominal_forecast_60m.to_numpy()
        ck(f'Training labels precede decision {sig} {dates[t]}',all(pd.Period(x,'M')<dates[t] for x in rr.last_train_target))
        ck(f'Carry input matches cached data {sig} {dates[t]}',np.allclose(rr.carry_monthly,b['carry'][t],atol=1e-12))
    signals['Matched'][t]=signals['EJR'][t]
    signals['Matched'][t,0]=signals['TT_all'][t,0]
    for sig,ff in signals.items():
        for c,cc in enumerate(CC):
            frows.append(dict(origin=str(dates[t]),signal=sig,currency=cc,
                              depreciation_60m=ff[t,c],expected_total_60m=60*b['carry'][t,c]-ff[t,c]))

def optimize(mu,S):
    """Exact global maximum on six feasible 1-D segments; net=0, gross=1."""
    funding=.005*5*.5
    best=None; bestscore=-np.inf; gridbest=-np.inf
    for isolated in range(3):
        other=[c for c in range(3) if c!=isolated]
        for sign in [-1.,1.]:
            w0=np.zeros(3); w0[isolated]=sign*.5; w0[other[1]]=-sign*.5
            d=np.zeros(3); d[other[0]]=-sign; d[other[1]]=sign
            a=mu@d; bb=mu@w0-funding
            aa=d@S@d; B=2*d@S@w0; c=w0@S@w0
            den=a*B-2*bb*aa; num=2*a*c-bb*B
            candidates=[0.,.5]
            if abs(den)>1e-18:
                x=-num/den
                if 0<x<.5:candidates.append(x)
            for x in candidates:
                w=w0+x*d; score=(mu@w-funding)/np.sqrt(w@S@w)
                if score>bestscore:bestscore=score; best=w
            xx=np.linspace(0,.5,1001)
            gridbest=max(gridbest,np.max((a*xx+bb)/np.sqrt(aa*xx**2+B*xx+c)))
    return best,bestscore,gridbest

weights={}; audits=[]; wrows=[]
for sig,fp in signals.items():
    rank=np.zeros((T,3))
    rank[needed]=b['rank_weights'](b['carry'][needed]-fp[needed]/60,k=1)
    weights['Ranking_'+sig]=rank
    for risk in ['monthly120','long60']:
        ww=np.zeros((T,3))
        for t in needed:
            S,n=b['covariance'](t,risk); mu=60*b['carry'][t]-fp[t]
            ww[t],score,grid=optimize(mu,S)
            rankscore=(mu@rank[t]-.0125)/np.sqrt(rank[t]@S@rank[t])
            ck(f'Global optimum beats dense grid {sig} {risk} {dates[t]}',score+1e-9>=grid)
            ck(f'Global optimum beats ranking {sig} {risk} {dates[t]}',score+1e-9>=rankscore)
            audits.append(dict(signal=sig,risk=risk,origin=str(dates[t]),n_risk=n,
                               last_risk_return=str(dates[t-1]),score=score,grid_best=grid,rank_score=rankscore))
        weights[risk+'_'+sig]=ww
    print('Weights ready:',sig,flush=True)
for name,ww in weights.items():
    ck(name+' net zero',np.max(np.abs(ww[needed].sum(axis=1)))<1e-10)
    ck(name+' gross one',np.max(np.abs(np.abs(ww[needed]).sum(axis=1)-1))<1e-10)
    ck(name+' cap 50%',np.max(np.abs(ww[needed]))<=.5000000001)
    for t in needed:
        for c,cc in enumerate(CC):wrows.append(dict(name=name,origin=str(dates[t]),currency=cc,weight=ww[t,c]))

methods={'Ranking':'Ranking: 1 compra / 1 venda','monthly120':'Máximo Sharpe — risco mensal','long60':'Máximo Sharpe — risco de 60 meses'}
labels={'Carry':'Juros','EJR':'Juros + EJR','TT_all':'Juros + EJR + TT nas três','Matched':'Juros + TT no BRL; EJR em EUR/CAD'}
rows=[]; details=[]; returns=[]
for sc,cm,br in [('Base',1,50),('Stress',4,150)]:
    for method,label in methods.items():
        for sig in signals:
            row=dict(scenario=sc,method=method,method_label=label,signal=sig,signal_label=labels[sig])
            for hold in [12,60]:
                ww=weights[method+'_'+sig]; bb=b['book'](ww,start,hold,180,cm,br); mm=b['stats'](bb)
                ck(f'Dates {sc} {method} {sig} {hold}',mm['n']==180 and mm['first']=='2010-03' and mm['last']=='2025-02')
                ck(f'Net accounting {sc} {method} {sig} {hold}',np.allclose(bb.net,bb.gross-bb.cost-bb.borrow,atol=1e-12))
                scheduled=b['schedule'](ww,start,hold,start+182)
                ck(f'All scheduled decisions known {sc} {method} {sig} {hold}',np.allclose(abs(scheduled[start:start+180]).sum(axis=1),1))
                for k in ['cagr','vol','sharpe','maxdd']:row[f'{k}_{hold}']=mm[k]
                details.append(dict(scenario=sc,method=method,signal=sig,hold=hold,**mm))
                for month,r in bb.iterrows():returns.append(dict(scenario=sc,method=method,signal=sig,hold=hold,month=str(month),**r.to_dict()))
            rows.append(row)
out=pd.DataFrame(rows); diff=[]
for sc in ['Base','Stress']:
    for method in methods:
        rr=out[(out.scenario==sc)&(out.method==method)].set_index('signal')
        for sig in ['EJR','TT_all','Matched']:
            for baseline in ['Carry','EJR']:
                for hold in [12,60]:
                    diff.append(dict(scenario=sc,method=method,signal=sig,baseline=baseline,hold=hold,
                                     delta_cagr=rr.loc[sig,f'cagr_{hold}']-rr.loc[baseline,f'cagr_{hold}'],
                                     delta_sharpe=rr.loc[sig,f'sharpe_{hold}']-rr.loc[baseline,f'sharpe_{hold}']))
ck('Input files preserved',all(hashlib.sha256((R/k).read_bytes()).hexdigest()==v for k,v in hashes.items()))
for name,v in [('table',out),('eligibility',elig),('universe_selection',selection),('forecasts',frows),('weights',wrows),('optimization_audit',audits),('metrics',details),('differences',diff),('validation',checks)]:
    pd.DataFrame(v).to_csv(H/'tables'/f'restricted_{name}.csv',index=False)
pd.DataFrame(returns).to_csv(H/'tables/restricted_returns.csv.gz',index=False)
np.savez_compressed(H/'cache/restricted_weights.npz',**weights)
(H/'tables/restricted_input_hashes.json').write_text(json.dumps(hashes,indent=2),encoding='utf-8')
def fmt(v,pct=False):return (f'{100*v:.2f}%' if pct else f'{v:.3f}').replace('.',',')
md=['# Carteiras restritas a BRL, EUR e CAD','',
    '**Backtest comum: março/2010–fevereiro/2025.** Retornos anuais compostos em USD, líquidos dos custos assumidos.','',
    'Somente as três moedas com ganho de previsão em 60 meses entram nas posições. Todos os modelos cambiais abaixo foram estimados no mesmo trio. A combinação por país usa EJR + TT no BRL e EJR sem TT no EUR/CAD. A linha com TT nas três é uma comparação adicional; TT não melhorou EJR incrementalmente no EUR/CAD.','',
    '| Moeda | Erro EJR / nenhuma mudança | Erro EJR + TT / nenhuma mudança | Sinal da combinação |',
    '|---|---:|---:|---|']
for r in elig:md.append(f"| {r['currency']} | {fmt(r['ejr_rmse_rw'])} | {fmt(r['tt_rmse_rw'])} | {r['matched_model']} |")
md+=['','O filtro aplicado ao estudo original de seis moedas seleciona exatamente BRL, EUR e CAD; JPY, GBP e SEK ficam acima de 1 em ambos os modelos. Essa evidência está em tables/restricted_universe_selection.csv. Os erros acima são das previsões reestimadas no trio, efetivamente utilizadas nas carteiras.']
for sc,title in [('Base','Custos básicos'),('Stress','Estresse de custos')]:
    md+=['','## '+title,'','| Método | Sinal | Retorno a.a. 12m | Retorno a.a. 60m | Sharpe 12m | Sharpe 60m |','|---|---|---:|---:|---:|---:|']
    for _,r in out[out.scenario==sc].iterrows():
        md.append('| '+' | '.join([r.method_label,r.signal_label,fmt(r.cagr_12,True),fmt(r.cagr_60,True),fmt(r.sharpe_12),fmt(r.sharpe_60)])+' |')
md+=['','## Resultados principais','',
    'Entre as alternativas avaliadas, juros + EJR com risco de 60 meses e escolha anual apresentou o maior retorno e Sharpe: 3,29% a.a. e 0,393, contra 2,86% e 0,298 do carry puro sob a mesma regra. Com estresse de custos, esses números passam a 2,65% e 0,277, contra 2,25% e 0,195 do carry. A queda máxima da alternativa EJR básica foi 13,31%, com volatilidade anual de 5,45%.','',
    'TT nas três moedas e a combinação TT no BRL/EJR nas demais reduzem o retorno e o Sharpe frente a EJR sozinho em todas as seis comparações de método e prazo. A menor perda máxima de algumas carteiras TT não reverte essa perda de retorno. Ganho de precisão de uma previsão individual de cinco anos não assegura ganho na classificação relativa das moedas ou no retorno de uma carteira.','',
    'Escolha a cada 60 meses não superou a escolha anual em retorno nesta tabela (empate no ranking de juros). Há somente três blocos consecutivos de cinco anos no backtest. Essa comparação histórica não estabelece uma superioridade geral da escolha anual.','',
    '## Regras, treinamento e interpretação','',
    'Exposição bruta 100%, líquida zero, 50% comprado e 50% vendido; teto 50% por moeda. O teto anterior de 25% é inviável com três moedas mantendo exposição bruta 100%. Ranking agora escolhe uma moeda comprada e uma vendida, a ±50%. Máximo Sharpe pode dividir uma das pontas entre as duas outras moedas. Mudanças frente à tabela com seis moedas também refletem essa concentração maior.','',
    '12m e 60m indicam o intervalo entre escolhas de moedas e pesos-alvo. Há ajustes mensais para manter esses pesos; não são quantidades congeladas. Não há saída antecipada. Previsão nominal de 60 meses em todas as linhas com EJR/TT. Expectativa = diferencial mensal de juros corrente extrapolado por 60 meses menos depreciação nominal prevista. Juros futuros não são conhecidos ou fixados por essa extrapolação.','',
    'Treino inicial: origens outubro/1999–dezembro/2004, alvos encerrados até dezembro/2009. Treino expansivo: só j+60 <= t−1. Sinal em janeiro/2010, execução em fevereiro, primeiro retorno em março. Escolha anual usa janeiro/2010 a janeiro/2024; escolha a cada 60m usa janeiro/2010, janeiro/2015 e janeiro/2020. Último treino anual: origens até dezembro/2018, alvos até dezembro/2023. A previsão aponta t+60 e a posição de 60 meses termina em t+61 por causa do atraso de execução, como no teste anterior.','',
    'TT é o log do índice de termos de troca de bens e serviços e sua mudança anual em log (TOT_LOG_LD), centrados com história disponível. Ano Y−2; CPI com atraso de dois meses. Erros da tabela de elegibilidade são da avaliação de previsões nas origens janeiro/2010–agosto/2021 e alvos janeiro/2015–agosto/2026, com estimação no trio.','',
    'Risco mensal: últimos 120 retornos mensais de juros+câmbio em excesso ao USD, escalados para 60m. Risco 60m: covariância expansiva de retornos acumulados de 60 meses. Ambos param em t−1 e usam 20% de regularização diagonal. O Sharpe da tabela é o realizado, anualizado e em excesso ao caixa USD; o objetivo da escolha de pesos é o Sharpe esperado.','',
    'Custos por negociação: BRL 10pb, EUR/CAD 2pb; cobrados na entrada, nos ajustes e na liquidação final. Spread adicional de financiamento de 50pb a.a. sobre a ponta vendida. Estresse: custos de negociação multiplicados por quatro e spread de 150pb a.a., mantendo os mesmos pesos. O retorno inclui caixa USD, juros locais, câmbio e custos. Custos assumidos, sem comprovação por cotações executáveis.','',
    '**Seleção retrospectiva:** países, transformação de TT e modelo por país foram escolhidos pelos testes na mesma história, com alvos inclusive posteriores a fevereiro/2025. A estimação de cada previsão respeita os atrasos, mas a seleção do universo/modelo não é uma regra histórica fora da amostra. Resultados exploratórios; não demonstram desempenho de uma estratégia selecionável em tempo real. Séries macroeconômicas revisadas não equivalem a vintages históricos.','',
    f'Validação: {len(checks)} verificações aprovadas, incluindo restrições de exposição, ótimo global contra malha densa, comparação com ranking, maturidade dos alvos, datas e contabilidade. As previsões reutilizadas foram auditadas também por truncamento e perturbação de dados futuros no teste anterior.','',
    'Reprodução: tools/python/python.exe horizon_tests/restricted_countries.py. Código: restricted_countries.py; protocolo: RESTRICTED_PROTOCOL.md. Resultados detalhados: tables/restricted_*.csv, retornos mensais em tables/restricted_returns.csv.gz. Nenhum relatório ou slide anterior foi alterado.']
(H/'PAISES_SELECIONADOS.md').write_text('\n'.join(md),encoding='utf-8')
print(out[out.scenario=='Base'].to_string(index=False))
print('Checks passed:',len(checks))
