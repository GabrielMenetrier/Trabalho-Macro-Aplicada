# Adição do sinal com termos de troca à tabela de carteiras

Registrado antes de executar este backtest. Mesma janela março/2010–fevereiro/2025, 180 retornos, custos, financiamento, seleção a cada 12 ou 60 meses e ajuste mensal dos pesos-alvo. Não alterar os relatórios e slides anteriores.

A previsão solicitada é a vencedora de cinco anos do estudo `ejr_trade_selected`: EJR + log dos termos de troca + mudança anual em log, estimada em BRL/EUR/CAD. A especificação foi escolhida retrospectivamente entre variantes avaliadas na mesma história, inclusive alvos posteriores ao fim deste backtest; a nova tabela é exploratória, não validação independente.

Manter seis moedas (BRL/EUR/JPY/GBP/CAD/SEK) é necessário para preservar a restrição original: 50% comprado, 50% vendido, teto de 25% por moeda e ranking duas compras/duas vendas. Três moedas não comportam essas restrições. Por isso:

1. Juros: sinal original sem EJR.
2. Juros + EJR original: previsão original estimada nas seis moedas.
3. Controle, juros + EJR reestimado no trio: substituir apenas BRL/EUR/CAD pelo EJR estimado no trio. JPY/GBP/SEK continuam com a previsão original.
4. Juros + EJR do trio + termos de troca: mesma composição do controle, adicionando termos de troca apenas nas três previsões do trio. Demais moedas continuam com EJR original.

Comparar 4 contra 3 identifica a mudança associada à adição do regressor neste desenho. Comparar 4 contra 2 também muda os países que determinam os coeficientes, e deve ser identificado como tal. Não tratar a carteira híbrida como carteira restrita a três moedas ou como modelo de termos de troca estimado em seis.

Retorno esperado em 60 meses = 60 × diferencial mensal de juros corrente − previsão de depreciação nominal em log. Preservar a aproximação anterior e não incorporar resultados futuros de juros. Otimização de Sharpe esperado, risco mensal (120 retornos, escalados a 60m) ou acumulado em 60m; mesma regularização 20% diagonal e somente retornos conhecidos até t−1.

Reestimar a previsão nas 15 origens anuais jan/2010–jan/2024 necessárias à tabela. Não usar somente previsões com alvos futuros já completos: isso eliminaria indevidamente as decisões de 2022–2024 no prazo de 12 meses. O treino usa apenas alvos j+60<=t−1; a realização futura do alvo não é necessária para formar a previsão em t. Conferir as previsões antigas salvas onde ambas existem.

Congelar as células originais; reaplicação deve reproduzi-las. Salvar sinais, pesos, retornos, custos, métricas, auditoria da otimização e diferenças incrementais. Testar exposição, teto, datas, maturidade, invariância a dados futuros e igualdade do objetivo otimizado ou melhora frente ao ranking com o mesmo sinal. Custos Base e Stress idênticos à tabela anterior. Não escolher especificação por retorno de carteira após observar os resultados.
