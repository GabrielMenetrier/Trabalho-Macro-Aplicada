# Carteiras restritas aos países com ganho de previsão

Protocolo registrado antes da execução deste novo backtest. Critério: RMSE relativo à previsão de nenhuma mudança abaixo de 1, em 60 meses, para EJR ou EJR + termos de troca nos testes anteriores. Universo fixo resultante: BRL, EUR e CAD. Nenhuma posição em JPY, GBP ou SEK. A seleção de países, transformação e modelo usa a avaliação histórica completa; é retrospectiva, não uma regra de elegibilidade conhecida em 2010.

Comparar quatro sinais no mesmo trio: juros; juros + EJR estimado no trio; juros + EJR + TT estimado no trio; combinação por país (EJR + TT no BRL, EJR no EUR/CAD). Esta última usa TT somente onde houve ganho incremental. Não adicionar commodities. TT significa log centrado do índice e mudança anual em log, especificação TOT_LOG_LD já escolhida no estudo anterior. Reutilizar as previsões recursivas auditadas de janeiro/2010 a janeiro/2024.

Manter exposição bruta 100%, líquida zero: 50% comprado e 50% vendido. Com três moedas, relaxar o teto de 25% para 50% por moeda. Ranking passa a uma moeda comprada e outra vendida; máximo Sharpe pode distribuir a ponta oposta entre duas moedas. As mesmas restrições valem para todos os sinais. Não atribuir diferenças frente à tabela de seis moedas somente à escolha dos países, pois também mudou o teto.

Manter março/2010–fevereiro/2025, escolha de pesos a cada 12 ou 60 meses e manutenção mensal desses pesos, previsão de 60 meses, risco mensal de 120 observações escalado para 60 meses ou covariância expansiva de retornos acumulados de 60 meses, com 20% de regularização diagonal. Retorno esperado = diferencial mensal de juros corrente vezes 60 menos depreciação nominal prevista. USD é caixa e numerário. Custos BRL 10pb, EUR/CAD 2pb por negociação e spread de financiamento de 50pb a.a. sobre a ponta vendida. Estresse: custos de negociação 4x, spread 150pb a.a., mesmas posições.

No trio, maximizar o objetivo exatamente: enumerar as seis possibilidades de uma moeda em uma ponta e duas na oposta; a variável é a repartição de 0 a 50% entre as duas. Avaliar extremos e eventual ponto estacionário da razão retorno esperado/risco. Validar contra uma malha densa e contra ranking. Custos de negociação não entram no objetivo, como na comparação anterior; entram integralmente no retorno realizado.

Salvar elegibilidade, sinais, pesos, retornos, métricas, comparações, hashes dos insumos e validações. Não modificar relatórios, slides ou resultados anteriores.
