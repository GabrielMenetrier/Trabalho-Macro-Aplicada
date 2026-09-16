# Carteiras com e sem o sinal EJR

Mesma comparação: março/2010–fevereiro/2025, 180 retornos mensais, três ciclos completos de cinco anos. Retorno anual composto em USD, líquido dos custos assumidos. Exposição líquida zero, bruta 100%, teto 25% por moeda. As moedas e os pesos-alvo são escolhidos a cada 12 ou 60 meses; ajustes mensais preservam os pesos e a neutralidade. Sem saídas antecipadas.

Sem EJR: retorno esperado baseado apenas no diferencial de juros atual. Com EJR: acrescenta a variação nominal prevista em 60 meses a partir do câmbio real. Nas duas versões o retorno realizado contém juros e câmbio; não se remove o risco cambial ao retirar o sinal. A covariância e a regularização de risco são idênticas dentro de cada comparação.

## Custos básicos

| Método | Sinal | Retorno a.a. 12m | Retorno a.a. 60m | Sharpe 12m | Sharpe 60m |
|---|---|---:|---:|---:|---:|
| Dois pares | Sem EJR | 3,27% | 3,23% | 0,461 | 0,473 |
| Dois pares | Com EJR | 2,62% | 2,22% | 0,319 | 0,265 |
| Máximo Sharpe — risco mensal | Sem EJR | 1,89% | 2,02% | 0,190 | 0,232 |
| Máximo Sharpe — risco mensal | Com EJR | 2,35% | 2,01% | 0,324 | 0,246 |
| Máximo Sharpe — risco de 60 meses | Sem EJR | 2,13% | 1,91% | 0,263 | 0,208 |
| Máximo Sharpe — risco de 60 meses | Com EJR | 2,05% | 1,27% | 0,309 | 0,017 |

## Estresse conjunto: negociação 4x e spread de financiamento de 150pb a.a.

| Método | Sinal | Retorno a.a. 12m | Retorno a.a. 60m | Sharpe 12m | Sharpe 60m |
|---|---|---:|---:|---:|---:|
| Dois pares | Sem EJR | 2,69% | 2,65% | 0,335 | 0,342 |
| Dois pares | Com EJR | 2,02% | 1,65% | 0,187 | 0,120 |
| Máximo Sharpe — risco mensal | Sem EJR | 1,31% | 1,45% | 0,031 | 0,071 |
| Máximo Sharpe — risco mensal | Com EJR | 1,77% | 1,45% | 0,160 | 0,073 |
| Máximo Sharpe — risco de 60 meses | Sem EJR | 1,54% | 1,35% | 0,097 | 0,042 |
| Máximo Sharpe — risco de 60 meses | Com EJR | 1,47% | 0,72% | 0,093 | -0,181 |

## Treinamento e limites

Treino EJR inicial: origens out/1999–dez/2004, alvos conhecidos até dez/2009; expansão mensal com alvos maduros. Covariância mensal inicial: jan/2000–dez/2009, janela móvel de 120 meses. Covariância de 60m inicial: 63 movimentos completos, com endpoints out/2004–dez/2009, janela expansiva. Regularização de 20% na diagonal, mesma regra com e sem sinal. A expectativa de juros usa taxas atuais extrapoladas; taxas realizadas e financiamento variam no backtest.

Custos básicos: BRL10, SEK3, demais2 pb sobre negociação; spread adicional de 50pb a.a. na ponta vendida, além dos juros. Não são custos comprovados de execução em corretora. O horizonte da previsão é t+60; a manutenção de 60 meses acaba em t+61 devido ao atraso de execução de um mês, mantido igual entre métodos.

As células com EJR e os comparadores já calculados foram reaproveitados sem alteração. Foi estimada a combinação faltante: otimizador sem EJR com risco mensal. Não há otimização ex post dos pesos. A comparação é descritiva, em apenas três ciclos consecutivos de cinco anos; não estabelece significância das diferenças. Mais detalhes em RESULTADOS.md e PROTOCOL.md.