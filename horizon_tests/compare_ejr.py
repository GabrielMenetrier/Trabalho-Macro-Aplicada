"""Matched with/without EJR tables; adds missing monthly-risk carry optimizer."""
from pathlib import Path
import json
import numpy as np,pandas as pd
R=Path(__file__).resolve().parents[1];H=R/'horizon_tests'
source=(H/'run.py').read_text(encoding='utf-8');ns={'__file__':str(H/'run.py')}
exec(source.split("W={'Pairs_EJR'")[0],ns)
exec(source[source.index('def schedule('):source.index('rows=[];rets=')],ns)
globals().update({k:v for k,v in ns.items() if not k.startswith('__')})
w=np.zeros((T,C));audit=[]
for t in range(start,T-2):
 S,n=covariance(t,'monthly120');mu=60*carry[t]
 w[t],value,fail=optimize(mu,S)
 assert abs(w[t].sum())<1e-7 and abs(abs(w[t]).sum()-1)<1e-7 and abs(w[t]).max()<.2500001
 rank=rank_weights(carry[[t]])[0]
 score=lambda a:(mu@a-.0125)/np.sqrt(a@S@a)
 assert score(w[t])+1e-7>=score(rank)
 audit.append(dict(origin=str(dates[t]),risk_n=n,last_risk_return=str(dates[t-1]),expected_sharpe=value,failed_partitions=fail))
rows=[]
for scenario,cm,br in [('Base',1,50),('Stress',4,150)]:
 for h in [1,12,60]:rows.append(dict(scenario=scenario,name='Sharpe_Carry_monthly120',hold=h,**stats(book(w,start,h,180,cm,br))))
rows.append(dict(scenario='FullMonthly',name='Sharpe_Carry_monthly120',hold=1,**stats(book(w,start,1,T-start-2))))
np.savez_compressed(H/'cache/carry_monthly_optimizer.npz',weights=w)
pd.DataFrame(audit).to_csv(H/'tables/carry_monthly_optimizer_audit.csv',index=False)
new=pd.DataFrame(rows);new.to_csv(H/'tables/carry_monthly_optimizer_metrics.csv',index=False)
allm=pd.concat([pd.read_csv(H/'tables/metrics.csv'),new],ignore_index=True)
out=[]
names=[('Dois pares','Pairs_Carry','Pairs_EJR'),('Máximo Sharpe — risco mensal','Sharpe_Carry_monthly120','Sharpe_EJR_monthly120'),('Máximo Sharpe — risco de 60 meses','Sharpe_Carry_long60','Sharpe_EJR_long60')]
for scenario in ['Base','Stress']:
 for label,without,with_ejr in names:
  for flag,name in [('Sem EJR',without),('Com EJR',with_ejr)]:
   row={'scenario':scenario,'metodo':label,'sinal':flag}
   for h in [12,60]:
    a=allm[(allm.scenario==scenario)&(allm.name==name)&(allm.hold==h)].iloc[0]
    assert a.n==180 and a['first']=='2010-03' and a['last']=='2025-02'
    for field in ['cagr','vol','sharpe','maxdd']:row[f'{field}_{h}']=a[field]
   out.append(row)
df=pd.DataFrame(out);df.to_csv(H/'tables/with_without_ejr.csv',index=False)
def fmt(x,pct=False):return (f'{100*x:.2f}%' if pct else f'{x:.3f}').replace('.',',')
md=['# Carteiras com e sem o sinal EJR','',
'Mesma comparação: março/2010–fevereiro/2025, 180 retornos mensais, três ciclos completos de cinco anos. Retorno anual composto em USD, líquido dos custos assumidos. Exposição líquida zero, bruta 100%, teto 25% por moeda. As moedas e os pesos-alvo são escolhidos a cada 12 ou 60 meses; ajustes mensais preservam os pesos e a neutralidade. Sem saídas antecipadas.','',
'Sem EJR: retorno esperado baseado apenas no diferencial de juros atual. Com EJR: acrescenta a variação nominal prevista em 60 meses a partir do câmbio real. Nas duas versões o retorno realizado contém juros e câmbio; não se remove o risco cambial ao retirar o sinal. A covariância e a regularização de risco são idênticas dentro de cada comparação.','']
for sc,title in [('Base','Custos básicos'),('Stress','Estresse conjunto: negociação 4x e spread de financiamento de 150pb a.a.')]:
 md += ['## '+title,'','| Método | Sinal | Retorno a.a. 12m | Retorno a.a. 60m | Sharpe 12m | Sharpe 60m |','|---|---|---:|---:|---:|---:|']
 for _,a in df[df.scenario==sc].iterrows():md.append('| '+' | '.join([a.metodo,a.sinal,fmt(a.cagr_12,True),fmt(a.cagr_60,True),fmt(a.sharpe_12),fmt(a.sharpe_60)])+' |')
 md+=['']
md+=['## Treinamento e limites','',
'Treino EJR inicial: origens out/1999–dez/2004, alvos conhecidos até dez/2009; expansão mensal com alvos maduros. Covariância mensal inicial: jan/2000–dez/2009, janela móvel de 120 meses. Covariância de 60m inicial: 63 movimentos completos, com endpoints out/2004–dez/2009, janela expansiva. Regularização de 20% na diagonal, mesma regra com e sem sinal. A expectativa de juros usa taxas atuais extrapoladas; taxas realizadas e financiamento variam no backtest.','',
'Custos básicos: BRL10, SEK3, demais2 pb sobre negociação; spread adicional de 50pb a.a. na ponta vendida, além dos juros. Não são custos comprovados de execução em corretora. O horizonte da previsão é t+60; a manutenção de 60 meses acaba em t+61 devido ao atraso de execução de um mês, mantido igual entre métodos.','',
'As células com EJR e os comparadores já calculados foram reaproveitados sem alteração. Foi estimada a combinação faltante: otimizador sem EJR com risco mensal. Não há otimização ex post dos pesos. A comparação é descritiva, em apenas três ciclos consecutivos de cinco anos; não estabelece significância das diferenças. Mais detalhes em RESULTADOS.md e PROTOCOL.md.']
(H/'COM_SEM_EJR.md').write_text('\n'.join(md),encoding='utf-8')
print(df[df.scenario=='Base'].to_string(index=False));print('All weight/expected-objective/date constraints passed. Failed partitions:',sum(a['failed_partitions'] for a in audit))
