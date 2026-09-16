# Revisão de integridade econométrica e financeira

Execução: 10/09/2026. Parecer: o algoritmo respeita a ordem temporal declarada nos testes implementados. **Não equivale a certificação de dados point-in-time**, porque as fontes macroeconômicas não oferecem aqui um histórico completo de vintages por data de decisão.

## Verificações e evidência

| Risco | Controle executado | Limite residual |
|---|---|---|
| Treinar com retornos futuros de cinco/oito anos | Apenas origens j com j+h <= t-1; log de todas as origens | Dependência entre alvos sobrepostos permanece |
| Média/normalização usando amostra completa | Média específica por país apenas até t, recalculada recursivamente | Referência histórica pode não ser equilíbrio econômico |
| CPI do próprio mês antes da publicação | Lag de 2 meses, robustez com 3 | Calendário histórico completo de releases e vintages não foi reconstruído |
| Interpolar IPC com dado futuro | Sem interpolação; último dado passado limitado a um mês extra | Em dez/2025 o sinal usa CPI americano mais antigo |
| Apagar um mês e encurtar horizontes | Índice mensal regular; shift antes de dropna | Regressão descritiva perde somente origens não válidas |
| Executar no fechamento que gerou o sinal | Sinal t, execução t+1, P&L t+2 | Referência cambial não garante preço contratado |
| Revisões e ajustes sazonais | CPI sem ajuste sazonal no modelo operacional; dados congelados | NSA também pode sofrer revisões; não é um backtest de vintage |
| Dividendos ajustados no preditor | ETFs entram apenas como resultado realizado | Provedor pode revisar o histórico de adjusted close |
| Confundir cotação invertida | Toda moeda em unidades locais por USD; teste sintético de sinal | Quotes de mercados diferentes não são perfeitamente simultâneos |
| Ignorar financiamento | Remuneração de cada aplicação/passivo + spread nas vendas + colateral | Taxas oficiais são proxies, sem curva a termo histórica |
| Chamar valorização de câmbio de lucro puro | Retorno de ativo convertido e custo de oportunidade explícitos | Sem modelagem de imposto ou acesso a taxa institucional |
| Rebalancear gratuitamente | Peso anterior deriva de marcação a mercado e NAV; custos de entrada/saída | Custos assumidos, sem calibração de capacidade |
| Somar 60 retornos sobrepostos como capital livre | Coortes 1/60 com exposição líquida <=1 | Coortes são pesos mensais, não quantidades fixas |
| Escolher melhor país/modelo/horizonte após o resultado | Universo e base fixados antes da primeira execução; todas as alternativas publicadas | Tema e especificações não foram registrados prospectivamente |
| Tratar 840 previsões como independentes | Agregação temporal para HAC, bootstrap conjunto de inovações, contagem não sobreposta | Pouquíssima informação independente em horizontes longos |
| Vários testes com p pequeno | Holm e divulgação de todas as variantes | Correção cobre a família executada, não toda pesquisa anterior da literatura |
| Chamar períodos históricos de filtro causal | Classificação ex-ante por volatilidade/juros; episódios só descritivos | Correlação condicional não identifica causalidade |
| Usar janeiro–agosto como ano completo | 198 meses e CAGR com 12/N | Anualização não prevê o restante de 2026 |

## Testes automatizados

`tests/test_integrity.py` cobre:

1. Alterar dados após uma data não altera previsões anteriores.
2. Cortar o arquivo numa data reproduz as previsões disponíveis naquela data.
3. O último alvo de treinamento é anterior à origem e o coeficiente coincide com cálculo independente.
4. Rebase dos índices de preço não muda previsões centradas.
5. Ausência de CPI não consulta dados futuros.
6. Ranking mantém 50% long, 50% short, soma zero e gross 1; sinal inválido não gera posição.
7. Apreciação da moeda local gera lucro em USD para compra e prejuízo para venda.
8. Caixa sem posição recebe apenas a remuneração de caixa.
9. Um salto antes da execução não pode ser capturado pelo sinal.
10. Custos de entrada, drift dos pesos e liquidação são cobrados, além do spread da venda.
11. Perda no primeiro período conta no drawdown.
12. Arquivos brutos mantêm os hashes e a base mensal preserva o calendário.
13. Juros do BCE respeitam a data de vigência; juros do Japão e preços dos ETFs têm cobertura nas janelas exigidas.
14. Retorno líquido se reconcilia com caixa, contribuições e custos; NAV se reconcilia com a composição mensal.

Resultado final: **14 testes aprovados**. São 14 funções de teste, algumas com várias verificações relacionadas.

## Revisão econométrica

- A equação descritiva com CPI contemporâneo não entra no algoritmo de negociação.
- O horizonte h refere-se a meses de calendário, não à quantidade de observações remanescentes após excluir ausências.
- EJR sem intercepto é hipótese de variação nominal de longo prazo média nula. Painel FE e OLS com intercepto relaxam a restrição, sem demonstrar superioridade automática.
- R² dentro da amostra não mede habilidade de previsão. A comparação externa usa RMSE contra passeio sem drift e mesmas origens quando se comparam horizontes.
- O bootstrap de previsões retém covariância contemporânea de choques entre moedas. Não é idêntico ao bootstrap do artigo: usa AR(1), cap de persistência, 999 simulações, frequência mensal e outra amostra.
- Clark–West é diagnóstico aproximado. O relatório se apoia também no bootstrap e na avaliação econômica; não interpreta testes isolados como prova de uma relação estável.
- O intervalo de retorno excedente principal inclui zero com blocos de 12 e 60 meses.
- O diferencial frente ao carry e o alfa condicional não demonstram ganho incremental.
- O período pós-2021 é pós-publicação final, não um holdout prospectivamente registrado.

## Revisão financeira

A carteira internacional é caixa USD + overlay de aplicações e passivos nas seis moedas. O sinal de juros não é somado a um retorno de forward: não há dupla contagem de carry. Taxas anuais são transformadas pela convenção comum `(1+i/100)^(1/12)-1`, uma aproximação de depósito efetivo mensal, não reprodução das convenções de dias de cada contrato.

O orçamento de 50% comprado e 50% vendido refere-se aos ativos/passivos estrangeiros do overlay. O colateral de 100% é adicional e rende caixa USD. Na variante direcional, a soma das moedas pode diferir de zero e há perna USD compensatória; logo, a exposição bruta incluindo essa perna pode chegar a 2. Ela não deve ser confundida com o orçamento do ranking neutro.

O funding extra é 50 pb anuais sobre o nocional short, proporcionalmente ao mês e convertido pelo câmbio final. A aproximação de spread simples é explicitada. O mark-to-market altera o peso anterior ao rebalanceamento, inclusive após custos. A última observação inclui encerramento das posições.

Na implementação brasileira, o caixa em BRL remunera a parte não aplicada em USD. BIL/SPY usam retornos ajustados de mercado, sem usar seus preços futuros para formar sinais. Manter SPY adiciona prêmio e risco de bolsa; lucro em SPY não identifica habilidade cambial. O modelo usa a mesma previsão de câmbio e juros para BIL e SPY e não estima um prêmio acionário.

## Limites materiais não removidos

Faltam vintages completas, forwards bid/ask e basis históricos, taxas reais de aluguel/captação por investidor, impostos, limites de margem, capacidade de negociação e perdas intramês. Essas ausências impedem afirmar que o resultado do painel é uma arbitragem executável ou um retorno líquido que um investidor específico obteria. A implementação com ETFs reduz a distância em relação a ativos negociados, mas não remove o restante das hipóteses.
