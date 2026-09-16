"""Append a paired, six-currency hybrid TT forecast to the original portfolio table."""
from pathlib import Path
import json,sys,runpy,hashlib
import numpy as np,pandas as pd
R=Path(__file__).resolve().parents[1];H=R/'horizon_tests'
source=(H/'run.py').read_text(encoding='utf-8');b={'__file__':str(H/'run.py')}
exec(source.split("W={'Pairs_EJR'")[0],b)
exec(source[source.index('def schedule('):source.index('rows=[];rets=')],b)
e=runpy.run_path(str(R/'ejr_trade_selected/run.py'),run_name='selected_engine')
dates=b['dates'];T=b['T'];C=b['C'];start=b['start'];F=b['F'];carry=b['carry'];ids=[0,1,4];other=[2,3,5]
assert dates.equals(e['dates'])
inputs=[H/'tables/with_without_ejr.csv',H/'cache/weights.npz',H/'cache/carry_monthly_optimizer.npz',R/'secondary/cache/core.npz',R/'ejr_trade_selected/run.py',R/'ejr_trade_selected/tables/predictions.csv.gz']+[R/k for k in json.loads((R/'ejr_trade_selected/input_hashes.json').read_text())]
hashes={str(p.relative_to(R)):hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs}
(H/'tables/with_tot_input_hashes.json').write_text(json.dumps(hashes,indent=2))
orig=pd.read_csv(H/'tables/with_without_ejr.csv');before=orig.copy(deep=True)
checks=[]
def ck(k,v):checks.append(dict(check=k,passed=bool(v)));assert v,k
needed=list(range(start,start+180,12));pprev=pd.read_csv(R/'ejr_trade_selected/tables/predictions.csv.gz')
signals={'EJR_trio':F.copy(),'EJR_TOT_trio':F.copy()};forecastrows=[];aud=[];weightrows=[];new_weights={}
for t in needed:
    pp,_=e['fit_at'](t,60)
    signals['EJR_trio'][t,ids]=pp['EJR'];signals['EJR_TOT_trio'][t,ids]=pp['TOT_LOG_LD']
    for kind,key in [('EJR_trio','EJR'),('EJR_TOT_trio','TOT_LOG_LD')]:
        ck(f'Untouched currencies {kind} {dates[t]}',np.array_equal(signals[kind][t,other],F[t,other]))
        for c,cc in enumerate(b['CC']):forecastrows.append(dict(origin=str(dates[t]),currency=cc,variant=kind,nominal_forecast_60m=signals[kind][t,c],carry_monthly=carry[t,c],expected_total_60m=60*carry[t,c]-signals[kind][t,c],train_first=str(dates[0]),train_last=str(dates[t-61]),last_train_target=str(dates[t-1]),tt_source_year=dates[t].year-2 if c in ids and kind=='EJR_TOT_trio' else None))
        oldrows=pprev[(pprev.h==60)&(pprev.origin==str(dates[t]))].set_index('country').reindex(e['CC'])
        if oldrows[key].notna().all():ck(f'Reproduce saved prediction {kind} {dates[t]}',np.allclose(pp[key],oldrows[key],atol=1e-11))
    print('Forecast formed',str(dates[t]),flush=True)
for name,fp in signals.items():
    rank=np.zeros((T,C));rank[needed]=b['rank_weights'](carry[needed]-fp[needed]/60)
    new_weights['Pairs_'+name]=rank
    for risk in ['monthly120','long60']:
        ww=np.zeros((T,C))
        for t in needed:
            S,n=b['covariance'](t,risk);mu=60*carry[t]-fp[t]
            ww[t],obj,failed=b['optimize'](mu,S)
            score=lambda w:(mu@w-.0125)/np.sqrt(w@S@w)
            ck(f'Optimizer >= ranking {name} {risk} {dates[t]}',score(ww[t])+1e-7>=score(rank[t]))
            aud.append(dict(variant=name,risk=risk,origin=str(dates[t]),risk_n=n,last_risk_return=str(dates[t-1]),objective=obj,failed_partitions=failed,rank_objective=score(rank[t])))
        new_weights['Sharpe_'+name+'_'+risk]=ww
        print('Optimized',name,risk,flush=True)
for name,ww in new_weights.items():
    ck(name+' net zero',np.max(np.abs(ww[needed].sum(axis=1)))<1e-7)
    ck(name+' gross one',np.max(np.abs(np.abs(ww[needed]).sum(axis=1)-1))<1e-7)
    ck(name+' 25 percent cap',np.max(np.abs(ww[needed]))<.2500001)
    for t in needed:
        for c,cc in enumerate(b['CC']):weightrows.append(dict(name=name,origin=str(dates[t]),currency=cc,weight=ww[t,c]))
stored=dict(np.load(H/'cache/weights.npz',allow_pickle=True));stored.pop('dates',None)
stored['Sharpe_Carry_monthly120']=np.load(H/'cache/carry_monthly_optimizer.npz')['weights']
methods=[('Dois pares','Pairs_'),('Máximo Sharpe — risco mensal','Sharpe_','monthly120'),('Máximo Sharpe — risco de 60 meses','Sharpe_','long60')]
def name_for(method,signal):return method[1]+signal+('_'+method[2] if len(method)>2 else '')
# Re-run the baseline books: no change to optimizer or saved original weights.
for sc,cm,br in [('Base',1,50),('Stress',4,150)]:
    for method in methods:
        for sig,label in [('Carry','Sem EJR'),('EJR','Com EJR')]:
            ww=stored[name_for(method,sig)];oldrow=orig[(orig.scenario==sc)&(orig.metodo==method[0])&(orig.sinal==label)].iloc[0]
            for hold in [12,60]:
                mm=b['stats'](b['book'](ww,start,hold,180,cm,br))
                ck(f'Original result unchanged {sc} {method[0]} {sig} {hold}',all(abs(mm[k]-oldrow[f'{k}_{hold}'])<1e-11 for k in ['cagr','vol','sharpe','maxdd']))
rows=[];returns=[];detail=[]
for sc,cm,br in [('Base',1,50),('Stress',4,150)]:
    for method in methods:
        for sig,label in [('Carry','Juros'),('EJR','Juros + EJR original'),('EJR_trio','Juros + EJR do trio (controle)'),('EJR_TOT_trio','Juros + EJR do trio + TT')]:
            row=dict(scenario=sc,metodo=method[0],sinal=label,variant=sig)
            if sig in ['Carry','EJR']:
                v=orig[(orig.scenario==sc)&(orig.metodo==method[0])&(orig.sinal==('Sem EJR' if sig=='Carry' else 'Com EJR'))].iloc[0]
                for k in ['cagr','vol','sharpe','maxdd']:
                    for hold in [12,60]:row[f'{k}_{hold}']=v[f'{k}_{hold}']
            else:
                ww=new_weights[name_for(method,sig)]
                for hold in [12,60]:
                    bb=b['book'](ww,start,hold,180,cm,br);v=b['stats'](bb)
                    ck(f'Correct backtest window {sc} {method[0]} {sig} {hold}',v['n']==180 and v['first']=='2010-03' and v['last']=='2025-02')
                    ck(f'Net accounting {sc} {method[0]} {sig} {hold}',np.allclose(bb.net,bb.gross-bb.cost-bb.borrow,atol=1e-12))
                    for k in ['cagr','vol','sharpe','maxdd']:row[f'{k}_{hold}']=v[k]
                    detail.append(dict(scenario=sc,method=method[0],variant=sig,hold=hold,**v))
                    for month,r in bb.iterrows():returns.append(dict(scenario=sc,method=method[0],variant=sig,hold=hold,month=str(month),**r.to_dict()))
                    # Schedule only consults forecasts from the 15 precomputed origins.
                    scheduled=b['schedule'](ww,start,hold,start+182)
                    ck(f'No missing signal in book {sig} {hold}',np.allclose(np.abs(scheduled[start:start+180]).sum(axis=1),1,atol=1e-7))
            rows.append(row)
out=pd.DataFrame(rows);diff=[]
for sc in ['Base','Stress']:
 for method in methods:
  rr=out[(out.scenario==sc)&(out.metodo==method[0])].set_index('variant')
  for hold in [12,60]:
   diff.append(dict(scenario=sc,method=method[0],hold=hold,delta_cagr_TT_vs_matched=rr.loc['EJR_TOT_trio',f'cagr_{hold}']-rr.loc['EJR_trio',f'cagr_{hold}'],delta_sharpe_TT_vs_matched=rr.loc['EJR_TOT_trio',f'sharpe_{hold}']-rr.loc['EJR_trio',f'sharpe_{hold}'],delta_cagr_TT_vs_original=rr.loc['EJR_TOT_trio',f'cagr_{hold}']-rr.loc['EJR',f'cagr_{hold}']))
# Check the newest signal, whose target is beyond observed data, still uses only its prefix.
t=needed[-1]
pref,_=e['fit_at'](t,60,e['S'][:t+1],e['Q'][:t+1],{k:v[:t+1] for k,v in e['L'].items()},{k:v[:t+1] for k,v in e['D'].items()})
ck('2024 forecast independent of unavailable future endpoint',np.allclose(pref['TOT_LOG_LD'],signals['EJR_TOT_trio'][t,ids]))
ss=e['S'].copy();ss[t+1:]+=100;qq=e['Q'].copy();qq[t+1:]+=100
ll={k:v.copy() for k,v in e['L'].items()};dd={k:v.copy() for k,v in e['D'].items()}
for k in ll:ll[k][t+1:]+=100;dd[k][t+1:]+=100
pert,_=e['fit_at'](t,60,ss,qq,ll,dd)
ck('Future input perturbation cannot affect latest TT signal',np.allclose(pert['TOT_LOG_LD'],pref['TOT_LOG_LD']))
ck('All previous input files preserved',all(hashlib.sha256((R/k).read_bytes()).hexdigest()==v for k,v in hashes.items()))
for name,v in [('with_terms_of_trade',out),('with_tot_metrics',detail),('with_tot_forecasts',forecastrows),('with_tot_weights',weightrows),('with_tot_optimization_audit',aud),('with_tot_differences',diff),('with_tot_validation',checks)]:pd.DataFrame(v).to_csv(H/'tables'/f'{name}.csv',index=False)
pd.DataFrame(returns).to_csv(H/'tables/with_tot_returns.csv.gz',index=False)
np.savez_compressed(H/'cache/with_tot_weights.npz',**new_weights)
def fmt(x,pct=False):return (f'{100*x:.2f}%' if pct else f'{x:.3f}').replace('.',',')
md=['# Carteiras com juros, EJR e termos de troca','',
'**Backtest comum: março/2010–fevereiro/2025.** Retornos anuais compostos em USD, líquidos dos custos assumidos.','',
'Seis moedas e mesmas regras da tabela anterior. EJR do trio substitui somente as previsões de BRL/EUR/CAD; JPY/GBP/SEK permanecem com EJR original. TT é log dos termos de troca de bens e serviços + mudança anual em log. O controle reestima EJR no mesmo trio, mas não adiciona TT. Comparar a linha TT ao controle separa a adição da mudança no grupo de estimação.','']
for sc,title in [('Base','Custos básicos'),('Stress','Estresse: negociação 4x e spread adicional de 150pb a.a.')]:
 md+=['## '+title,'','| Método | Sinal | Retorno a.a. 12m | Retorno a.a. 60m | Sharpe 12m | Sharpe 60m |','|---|---|---:|---:|---:|---:|']
 for _,r in out[out.scenario==sc].iterrows():md.append('| '+' | '.join([r.metodo,r.sinal,fmt(r.cagr_12,True),fmt(r.cagr_60,True),fmt(r.sharpe_12),fmt(r.sharpe_60)])+' |')
 md+=['']
md+=['## Calendário e regras','',
'12m/60m é o intervalo de escolha das moedas e dos pesos-alvo. Os pesos são mantidos por ajustes mensais; não são quantidades congeladas. Exposição líquida zero, bruta 100%, teto 25% por moeda; ranking compra duas e vende duas. Previsão nominal de 60 meses em ambos os prazos. Juros correntes extrapolados para formar a expectativa, sem tratar essa extrapolação como taxa contratada.','',
'Sinal em janeiro/2010; execução em fevereiro/2010; primeiro retorno em março/2010. Reescolha anual: origens janeiro/2010 a janeiro/2024. Reescolha de 60m: janeiro/2010, janeiro/2015 e janeiro/2020. Nenhuma saída antecipada. A previsão aponta t+60 e uma manutenção de 60 meses acaba em t+61 devido ao atraso de execução, como na tabela original.','',
'Treino cambial inicial: origens outubro/1999–dezembro/2004, alvos conhecidos até dezembro/2009. Expansão a cada decisão, somente j+60<=t−1. Termos de troca anuais disponíveis Y−2; CPI t−2. No sinal janeiro/2024, o treino termina na origem dezembro/2018, alvo dezembro/2023. Não é preciso observar janeiro/2029 para formar essa previsão de cinco anos em janeiro/2024.','',
'Risco mensal: covariância dos últimos 120 retornos mensais de juros+câmbio em excesso ao USD, escalada a 60 meses. Risco 60m: covariância de movimentos acumulados de 60 meses, janela expansiva. Ambos usam só dados até t−1 e regularização de 20% em direção à diagonal. Sharpe reportado é realizado, anualizado, em excesso ao caixa USD; o otimizador maximiza o Sharpe esperado.','',
'Custos básicos por negociação: BRL 10pb, SEK 3pb, demais 2pb, com entrada, rebalanceamento e liquidação. Spread adicional de financiamento: 50pb a.a. sobre a ponta vendida, além dos juros. Caixa USD incluído. Custos assumidos, não comprovados por cotações executáveis. Estresse usa as mesmas posições, com negociação 4x e spread adicional de 150pb a.a.','',
'## Limite de interpretação','',
'A especificação TT e os países que a estimam foram escolhidos retrospectivamente nos testes anteriores, inclusive com alvos além de fevereiro/2025. Esta tabela explora valor econômico na mesma história; não é teste independente ou confirmação do vencedor. A comparação de previsão 0,802→0,628 era do trio de moedas; não é uma promessa de melhora das carteiras híbridas com seis moedas.','',
'Arquivos: tables/with_terms_of_trade.csv; with_tot_metrics.csv; with_tot_returns.csv.gz; with_tot_forecasts.csv; with_tot_weights.csv; with_tot_optimization_audit.csv; with_tot_differences.csv; with_tot_validation.csv. Código: add_terms_of_trade.py. Protocolo: TOT_PROTOCOL.md. As células da tabela original foram preservadas e reproduzidas pela rotina de contabilidade.']
(H/'COM_EJR_TT.md').write_text('\n'.join(md),encoding='utf-8')
print(out[out.scenario=='Base'][['metodo','sinal','cagr_12','cagr_60','sharpe_12','sharpe_60']].to_string(index=False))
print('Validation:',len(checks),'passed. Failed partitions:',sum(x['failed_partitions'] for x in aud))
