# Carteiras com juros, EJR e termos de troca

**Backtest comum: março/2010–fevereiro/2025.** Retornos anuais compostos em USD, líquidos dos custos assumidos.

Seis moedas e mesmas regras da tabela anterior. EJR do trio substitui somente as previsões de BRL/EUR/CAD; JPY/GBP/SEK permanecem com EJR original. TT é log dos termos de troca de bens e serviços + mudança anual em log. O controle reestima EJR no mesmo trio, mas não adiciona TT. Comparar a linha TT ao controle separa a adição da mudança no grupo de estimação.

## Custos básicos

| Método | Sinal | Retorno a.a. 12m | Retorno a.a. 60m | Sharpe 12m | Sharpe 60m |
|---|---|---:|---:|---:|---:|
| Dois pares | Juros | 3,27% | 3,23% | 0,461 | 0,473 |
| Dois pares | Juros + EJR original | 2,62% | 2,22% | 0,319 | 0,265 |
| Dois pares | Juros + EJR do trio (controle) | 2,62% | 2,22% | 0,319 | 0,265 |
| Dois pares | Juros + EJR do trio + TT | 1,93% | 1,81% | 0,175 | 0,152 |
| Máximo Sharpe — risco mensal | Juros | 1,89% | 2,02% | 0,190 | 0,232 |
| Máximo Sharpe — risco mensal | Juros + EJR original | 2,35% | 2,01% | 0,324 | 0,246 |
| Máximo Sharpe — risco mensal | Juros + EJR do trio (controle) | 2,37% | 1,99% | 0,328 | 0,242 |
| Máximo Sharpe — risco mensal | Juros + EJR do trio + TT | 2,34% | 1,57% | 0,383 | 0,130 |
| Máximo Sharpe — risco de 60 meses | Juros | 2,13% | 1,91% | 0,263 | 0,208 |
| Máximo Sharpe — risco de 60 meses | Juros + EJR original | 2,05% | 1,27% | 0,309 | 0,017 |
| Máximo Sharpe — risco de 60 meses | Juros + EJR do trio (controle) | 2,03% | 1,25% | 0,303 | 0,012 |
| Máximo Sharpe — risco de 60 meses | Juros + EJR do trio + TT | 1,85% | 1,01% | 0,276 | -0,097 |

## Estresse: negociação 4x e spread adicional de 150pb a.a.

| Método | Sinal | Retorno a.a. 12m | Retorno a.a. 60m | Sharpe 12m | Sharpe 60m |
|---|---|---:|---:|---:|---:|
| Dois pares | Juros | 2,69% | 2,65% | 0,335 | 0,342 |
| Dois pares | Juros + EJR original | 2,02% | 1,65% | 0,187 | 0,120 |
| Dois pares | Juros + EJR do trio (controle) | 2,02% | 1,65% | 0,187 | 0,120 |
| Dois pares | Juros + EJR do trio + TT | 1,31% | 1,22% | 0,033 | 0,011 |
| Máximo Sharpe — risco mensal | Juros | 1,31% | 1,45% | 0,031 | 0,071 |
| Máximo Sharpe — risco mensal | Juros + EJR original | 1,77% | 1,45% | 0,160 | 0,073 |
| Máximo Sharpe — risco mensal | Juros + EJR do trio (controle) | 1,78% | 1,43% | 0,164 | 0,067 |
| Máximo Sharpe — risco mensal | Juros + EJR do trio + TT | 1,74% | 1,02% | 0,179 | -0,078 |
| Máximo Sharpe — risco de 60 meses | Juros | 1,54% | 1,35% | 0,097 | 0,042 |
| Máximo Sharpe — risco de 60 meses | Juros + EJR original | 1,47% | 0,72% | 0,093 | -0,181 |
| Máximo Sharpe — risco de 60 meses | Juros + EJR do trio (controle) | 1,46% | 0,71% | 0,086 | -0,188 |
| Máximo Sharpe — risco de 60 meses | Juros + EJR do trio + TT | 1,27% | 0,47% | 0,017 | -0,327 |

## Calendário e regras

12m/60m é o intervalo de escolha das moedas e dos pesos-alvo. Os pesos são mantidos por ajustes mensais; não são quantidades congeladas. Exposição líquida zero, bruta 100%, teto 25% por moeda; ranking compra duas e vende duas. Previsão nominal de 60 meses em ambos os prazos. Juros correntes extrapolados para formar a expectativa, sem tratar essa extrapolação como taxa contratada.

Sinal em janeiro/2010; execução em fevereiro/2010; primeiro retorno em março/2010. Reescolha anual: origens janeiro/2010 a janeiro/2024. Reescolha de 60m: janeiro/2010, janeiro/2015 e janeiro/2020. Nenhuma saída antecipada. A previsão aponta t+60 e uma manutenção de 60 meses acaba em t+61 devido ao atraso de execução, como na tabela original.

Treino cambial inicial: origens outubro/1999–dezembro/2004, alvos conhecidos até dezembro/2009. Expansão a cada decisão, somente j+60<=t−1. Termos de troca anuais disponíveis Y−2; CPI t−2. No sinal janeiro/2024, o treino termina na origem dezembro/2018, alvo dezembro/2023. Não é preciso observar janeiro/2029 para formar essa previsão de cinco anos em janeiro/2024.

Risco mensal: covariância dos últimos 120 retornos mensais de juros+câmbio em excesso ao USD, escalada a 60 meses. Risco 60m: covariância de movimentos acumulados de 60 meses, janela expansiva. Ambos usam só dados até t−1 e regularização de 20% em direção à diagonal. Sharpe reportado é realizado, anualizado, em excesso ao caixa USD; o otimizador maximiza o Sharpe esperado.

Custos básicos por negociação: BRL 10pb, SEK 3pb, demais 2pb, com entrada, rebalanceamento e liquidação. Spread adicional de financiamento: 50pb a.a. sobre a ponta vendida, além dos juros. Caixa USD incluído. Custos assumidos, não comprovados por cotações executáveis. Estresse usa as mesmas posições, com negociação 4x e spread adicional de 150pb a.a.

## Limite de interpretação

A especificação TT e os países que a estimam foram escolhidos retrospectivamente nos testes anteriores, inclusive com alvos além de fevereiro/2025. Esta tabela explora valor econômico na mesma história; não é teste independente ou confirmação do vencedor. A comparação de previsão 0,802→0,628 era do trio de moedas; não é uma promessa de melhora das carteiras híbridas com seis moedas.

Arquivos: tables/with_terms_of_trade.csv; with_tot_metrics.csv; with_tot_returns.csv.gz; with_tot_forecasts.csv; with_tot_weights.csv; with_tot_optimization_audit.csv; with_tot_differences.csv; with_tot_validation.csv. Código: add_terms_of_trade.py. Protocolo: TOT_PROTOCOL.md. As células da tabela original foram preservadas e reproduzidas pela rotina de contabilidade.