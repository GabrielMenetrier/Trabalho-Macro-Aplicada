# Comparação de pesos e prazo de manutenção

Desenho escrito antes dos novos resultados, dentro de uma pesquisa histórica já explorada; não é pré-registro independente.

- Mesmas seis moedas, dados salvos e previsão EJR de 60 meses. Não altera slides ou estudos anteriores.
- Ranking top2/bottom2 versus máximo Sharpe previsto, ambos com exposição líquida zero, bruta 100%, limite absoluto de 25% por moeda. O otimizador pode usar até seis moedas.
- Expectativa: diferencial de juros atual acumulado por 60 meses menos variação nominal prevista. A extrapolação de juros é hipótese, não uma taxa contratada por cinco anos.
- Risco principal: covariância de mudanças acumuladas em 60 meses dos retornos log de aplicações estrangeiras em excesso ao USD, apenas horizontes já realizados até t−1. Janela expansiva, mínimo 36 endpoints; regularização fixa 20% em direção à diagonal. Observações sobrepostas não são independentes. Sensibilidade: covariância dos últimos 120 retornos mensais multiplicada por 60, mesma regularização.
- Otimização numérica em todas as partições viáveis de compras/vendas. Maximiza Sharpe previsto com spread anual adicional de financiamento de 50pb; negociação é descontada no backtest, não otimizada. Não maximiza o Sharpe realizado.
- Carteiras mantêm moedas e pesos-alvo por 1, 12 ou 60 meses, sem saídas por risco. Pesos-alvo são rebalanceados mensalmente para preservar net=0 e gross=1. Isto mantém as moedas, não congela quantidades. Preços e juros realizados variam mensalmente.
- Calendário original: sinal ao fim de t; entrada no fechamento de t+1; primeiro retorno t+2. Previsão aponta t+60; manutenção de 60 meses termina em t+61 por causa do atraso de execução, explicitamente uma diferença de um mês.
- Comparação principal: março/2010–fevereiro/2025, 180 retornos e três ciclos completos de 60 meses. Diagnóstico de revisão mensal também até agosto/2026.
- Sensibilidade de início: todas as origens mensais desde janeiro/2010 com 60 retornos subsequentes completos, avaliando 60 meses de carteira mantida versus cinco ciclos de 12 meses; comparação pareada. Relatar dependência por sobreposição.
- Custos originais: BRL10/SEK3/demais2 pb por notional, entrada/rebalanceamento/saída, spread adicional na venda 50pb a.a. Estresse conjunto: negociação4x e spread150pb a.a. Remuneração por taxas de referência, sem comprovação de execução em corretora.
- Comparadores: carry por juros e carry+EJR com os mesmos pesos/régua de prazo. Intervalos bootstrap de diferenças de Sharpe são condicionais às decisões salvas, em blocos de 12 e 60 meses, sem resolver seleção histórica.
