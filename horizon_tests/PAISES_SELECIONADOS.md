# Carteiras restritas a BRL, EUR e CAD

**Backtest comum: março/2010–fevereiro/2025.** Retornos anuais compostos em USD, líquidos dos custos assumidos.

Somente as três moedas com ganho de previsão em 60 meses entram nas posições. Todos os modelos cambiais abaixo foram estimados no mesmo trio. A combinação por país usa EJR + TT no BRL e EJR sem TT no EUR/CAD. A linha com TT nas três é uma comparação adicional; TT não melhorou EJR incrementalmente no EUR/CAD.

| Moeda | Erro EJR / nenhuma mudança | Erro EJR + TT / nenhuma mudança | Sinal da combinação |
|---|---:|---:|---|
| BRL | 0,804 | 0,544 | TOT_LOG_LD |
| EUR | 0,898 | 0,998 | EJR |
| CAD | 0,719 | 0,920 | EJR |

O filtro aplicado ao estudo original de seis moedas seleciona exatamente BRL, EUR e CAD; JPY, GBP e SEK ficam acima de 1 em ambos os modelos. Essa evidência está em tables/restricted_universe_selection.csv. Os erros acima são das previsões reestimadas no trio, efetivamente utilizadas nas carteiras.

## Custos básicos

| Método | Sinal | Retorno a.a. 12m | Retorno a.a. 60m | Sharpe 12m | Sharpe 60m |
|---|---|---:|---:|---:|---:|
| Ranking: 1 compra / 1 venda | Juros | 2,61% | 2,61% | 0,232 | 0,232 |
| Ranking: 1 compra / 1 venda | Juros + EJR | 3,27% | 2,61% | 0,331 | 0,232 |
| Ranking: 1 compra / 1 venda | Juros + EJR + TT nas três | 1,87% | 1,67% | 0,129 | 0,099 |
| Ranking: 1 compra / 1 venda | Juros + TT no BRL; EJR em EUR/CAD | 1,70% | 1,34% | 0,099 | 0,045 |
| Máximo Sharpe — risco mensal | Juros | 2,81% | 2,27% | 0,281 | 0,202 |
| Máximo Sharpe — risco mensal | Juros + EJR | 2,84% | 2,46% | 0,289 | 0,219 |
| Máximo Sharpe — risco mensal | Juros + EJR + TT nas três | 2,52% | 1,63% | 0,257 | 0,099 |
| Máximo Sharpe — risco mensal | Juros + TT no BRL; EJR em EUR/CAD | 2,12% | 1,29% | 0,174 | 0,037 |
| Máximo Sharpe — risco de 60 meses | Juros | 2,86% | 1,90% | 0,298 | 0,146 |
| Máximo Sharpe — risco de 60 meses | Juros + EJR | 3,29% | 2,35% | 0,393 | 0,205 |
| Máximo Sharpe — risco de 60 meses | Juros + EJR + TT nas três | 2,43% | 1,36% | 0,284 | 0,045 |
| Máximo Sharpe — risco de 60 meses | Juros + TT no BRL; EJR em EUR/CAD | 2,70% | 1,14% | 0,293 | 0,010 |

## Estresse de custos

| Método | Sinal | Retorno a.a. 12m | Retorno a.a. 60m | Sharpe 12m | Sharpe 60m |
|---|---|---:|---:|---:|---:|
| Ranking: 1 compra / 1 venda | Juros | 2,02% | 2,02% | 0,146 | 0,146 |
| Ranking: 1 compra / 1 venda | Juros + EJR | 2,66% | 2,02% | 0,241 | 0,146 |
| Ranking: 1 compra / 1 venda | Juros + EJR + TT nas três | 1,22% | 1,10% | 0,024 | 0,002 |
| Ranking: 1 compra / 1 venda | Juros + TT no BRL; EJR em EUR/CAD | 1,02% | 0,73% | -0,003 | -0,047 |
| Máximo Sharpe — risco mensal | Juros | 2,21% | 1,69% | 0,183 | 0,102 |
| Máximo Sharpe — risco mensal | Juros + EJR | 2,23% | 1,87% | 0,189 | 0,127 |
| Máximo Sharpe — risco mensal | Juros + EJR + TT nas três | 1,89% | 1,05% | 0,142 | -0,019 |
| Máximo Sharpe — risco mensal | Juros + TT no BRL; EJR em EUR/CAD | 1,46% | 0,68% | 0,063 | -0,057 |
| Máximo Sharpe — risco de 60 meses | Juros | 2,25% | 1,32% | 0,195 | 0,037 |
| Máximo Sharpe — risco de 60 meses | Juros + EJR | 2,65% | 1,77% | 0,277 | 0,111 |
| Máximo Sharpe — risco de 60 meses | Juros + EJR + TT nas três | 1,82% | 0,80% | 0,147 | -0,094 |
| Máximo Sharpe — risco de 60 meses | Juros + TT no BRL; EJR em EUR/CAD | 2,03% | 0,53% | 0,168 | -0,090 |

## Resultados principais

Entre as alternativas avaliadas, juros + EJR com risco de 60 meses e escolha anual apresentou o maior retorno e Sharpe: 3,29% a.a. e 0,393, contra 2,86% e 0,298 do carry puro sob a mesma regra. Com estresse de custos, esses números passam a 2,65% e 0,277, contra 2,25% e 0,195 do carry. A queda máxima da alternativa EJR básica foi 13,31%, com volatilidade anual de 5,45%.

TT nas três moedas e a combinação TT no BRL/EJR nas demais reduzem o retorno e o Sharpe frente a EJR sozinho em todas as seis comparações de método e prazo. A menor perda máxima de algumas carteiras TT não reverte essa perda de retorno. Ganho de precisão de uma previsão individual de cinco anos não assegura ganho na classificação relativa das moedas ou no retorno de uma carteira.

Escolha a cada 60 meses não superou a escolha anual em retorno nesta tabela (empate no ranking de juros). Há somente três blocos consecutivos de cinco anos no backtest. Essa comparação histórica não estabelece uma superioridade geral da escolha anual.

## Regras, treinamento e interpretação

Exposição bruta 100%, líquida zero, 50% comprado e 50% vendido; teto 50% por moeda. O teto anterior de 25% é inviável com três moedas mantendo exposição bruta 100%. Ranking agora escolhe uma moeda comprada e uma vendida, a ±50%. Máximo Sharpe pode dividir uma das pontas entre as duas outras moedas. Mudanças frente à tabela com seis moedas também refletem essa concentração maior.

12m e 60m indicam o intervalo entre escolhas de moedas e pesos-alvo. Há ajustes mensais para manter esses pesos; não são quantidades congeladas. Não há saída antecipada. Previsão nominal de 60 meses em todas as linhas com EJR/TT. Expectativa = diferencial mensal de juros corrente extrapolado por 60 meses menos depreciação nominal prevista. Juros futuros não são conhecidos ou fixados por essa extrapolação.

Treino inicial: origens outubro/1999–dezembro/2004, alvos encerrados até dezembro/2009. Treino expansivo: só j+60 <= t−1. Sinal em janeiro/2010, execução em fevereiro, primeiro retorno em março. Escolha anual usa janeiro/2010 a janeiro/2024; escolha a cada 60m usa janeiro/2010, janeiro/2015 e janeiro/2020. Último treino anual: origens até dezembro/2018, alvos até dezembro/2023. A previsão aponta t+60 e a posição de 60 meses termina em t+61 por causa do atraso de execução, como no teste anterior.

TT é o log do índice de termos de troca de bens e serviços e sua mudança anual em log (TOT_LOG_LD), centrados com história disponível. Ano Y−2; CPI com atraso de dois meses. Erros da tabela de elegibilidade são da avaliação de previsões nas origens janeiro/2010–agosto/2021 e alvos janeiro/2015–agosto/2026, com estimação no trio.

Risco mensal: últimos 120 retornos mensais de juros+câmbio em excesso ao USD, escalados para 60m. Risco 60m: covariância expansiva de retornos acumulados de 60 meses. Ambos param em t−1 e usam 20% de regularização diagonal. O Sharpe da tabela é o realizado, anualizado e em excesso ao caixa USD; o objetivo da escolha de pesos é o Sharpe esperado.

Custos por negociação: BRL 10pb, EUR/CAD 2pb; cobrados na entrada, nos ajustes e na liquidação final. Spread adicional de financiamento de 50pb a.a. sobre a ponta vendida. Estresse: custos de negociação multiplicados por quatro e spread de 150pb a.a., mantendo os mesmos pesos. O retorno inclui caixa USD, juros locais, câmbio e custos. Custos assumidos, sem comprovação por cotações executáveis.

**Seleção retrospectiva:** países, transformação de TT e modelo por país foram escolhidos pelos testes na mesma história, com alvos inclusive posteriores a fevereiro/2025. A estimação de cada previsão respeita os atrasos, mas a seleção do universo/modelo não é uma regra histórica fora da amostra. Resultados exploratórios; não demonstram desempenho de uma estratégia selecionável em tempo real. Séries macroeconômicas revisadas não equivalem a vintages históricos.

Validação: 514 verificações aprovadas, incluindo restrições de exposição, ótimo global contra malha densa, comparação com ranking, maturidade dos alvos, datas e contabilidade. As previsões reutilizadas foram auditadas também por truncamento e perturbação de dados futuros no teste anterior.

Reprodução: tools/python/python.exe horizon_tests/restricted_countries.py. Código: restricted_countries.py; protocolo: RESTRICTED_PROTOCOL.md. Resultados detalhados: tables/restricted_*.csv, retornos mensais em tables/restricted_returns.csv.gz. Nenhum relatório ou slide anterior foi alterado.