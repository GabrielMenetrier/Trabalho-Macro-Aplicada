# Pesos ótimos e prazo de manutenção

Resultados novos, sem alteração dos slides. Não encontramos superioridade robusta da otimização e manter os pares por cinco anos não melhorou sistematicamente o resultado.

## 1. Máximo Sharpe previsto versus dois pares

Backtest março/2010–agosto/2026, 198 retornos mensais, revisão mensal. Todas as carteiras abaixo mantêm net=0, gross=100%, limite absoluto de 25% por moeda. Sharpe em excesso ao caixa USD; retorno total em USD, líquido dos custos assumidos. O otimizador usa expectativa EJR+juros para 60 meses; não escolhe pesos a partir dos resultados futuros.

| Carteira | Retorno anual composto | Volatilidade anual | Sharpe | Queda máxima |
|---|---:|---:|---:|---:|
| Dois pares por juros, referência | 4,11% | 4,43% | 0,601 | −9,09% |
| Dois pares por juros + EJR | 2,73% | 4,16% | 0,309 | −7,01% |
| Máximo Sharpe EJR, risco por retornos mensais | 2,65% | 3,17% | 0,371 | −6,76% |
| Máximo Sharpe EJR, risco por movimentos de 60 meses | 2,13% | 2,52% | 0,260 | −4,74% |

A versão com risco mensal melhora o Sharpe em 0,062, mas reduz o retorno. Intervalo bootstrap pareado de 95%, em blocos de 12 meses: [−0,116; +0,280]; em blocos de 60 meses: [−0,112; +0,293]. Não há melhora estatística estabelecida. A versão que estima o risco diretamente em cinco anos piora o Sharpe. As duas mantêm exposição bruta de 100%; a queda da volatilidade é compatível com a escolha e combinação de moedas, não com uma redução mecânica do orçamento bruto. Nenhuma supera a referência simples de carry por juros nesta amostra.

## 2. Manter os pares por 12 ou 60 meses

Mesmo sinal EJR de 60 meses, mesmas regras de escolha e custos. A diferença é quando escolher novamente as moedas. Sem filtro de saída antecipada. Janela março/2010–fevereiro/2025: 180 meses e três ciclos completos de cinco anos, evitando liquidar um último ciclo incompleto.

| Escolha das moedas e pesos | Retorno anual composto | Sharpe | Queda máxima |
|---|---:|---:|---:|
| Todo mês | 2,47% | 0,298 | −7,01% |
| A cada 12 meses | 2,62% | 0,319 | −8,02% |
| A cada 60 meses | 2,22% | 0,265 | −8,74% |

Os pares e pesos-alvo ficam fixos durante cada período. Pequenos rebalanceamentos mensais preservam net=0 e gross=100%, pagando negociação. Não há troca de moeda ou encerramento obrigatório em 12 meses na carteira de 60 meses. Mesmo assim, manter por cinco anos perde cerca de 0,40 ponto percentual anual para reescolher a cada ano. A diferença de Sharpe tem intervalo de 95% [−0,353; +0,196] com blocos de 12 meses: a amostra não estabelece uma diferença generalizável.

Com custos de negociação multiplicados por quatro e spread de financiamento de 1,50% a.a., os retornos ficam em 2,02% a.a. para 12 meses e 1,65% para 60 meses. O resultado não se inverte.

### Sem ajuste mensal de pesos

Fizemos também uma manutenção das posições sem rebalancear até a data da troca, capitalizando os juros nas aplicações e dívidas. Nesse caso a exposição é neutra na entrada, mas os pesos e a exposição líquida flutuam com os preços e juros. Não é possível simultaneamente congelar as posições e garantir neutralidade de valor continuamente.

| Manutenção sem rebalanceamento | Retorno anual composto | Sharpe | Queda máxima |
|---|---:|---:|---:|
| 12 meses | 2,59% | 0,313 | −7,93% |
| 60 meses | 2,01% | 0,218 | −8,56% |

A conclusão não se inverte. A exposição líquida absoluta média foi 2,02% e 4,05%, respectivamente. Não há mecanismo de chamada de margem ou execução forçada nesta simulação.

### Dependência da data de entrada

139 origens mensais, janeiro/2010–julho/2021, cada uma com 60 retornos completos até no máximo agosto/2026. Em cada janela comparamos manter os pares iniciais por 60 meses com cinco ciclos sucessivos de 12 meses, reescolhidos apenas com informações então disponíveis.

- Pesos-alvo constantes: 60 meses ganha em 51/139 janelas (36,7%). Diferença média de CAGR, 60 menos 12: −0,416 p.p. a.a.
- Posições sem rebalanceamento: 60 meses ganha em 50/139 janelas (36,0%). Diferença média: −0,560 p.p. a.a.

Essas janelas se sobrepõem fortemente. Não equivalem a 139 experimentos independentes, e as frequências não são probabilidades estimadas para o futuro.

## Implementação e calendário

- Universo: BRL, EUR, JPY, GBP, CAD, SEK; numerário USD. Ranking: duas compras de 25% e duas vendas de 25%. O otimizador pode usar até seis moedas, respeitando as mesmas restrições de concentração, 50% comprado e 50% vendido.
- Expectativa no otimizador: 60 vezes o diferencial de juros mensal atual menos a previsão de variação nominal EJR de 60 meses. Subtrai ainda o spread de financiamento esperado para cinco anos sobre a ponta vendida. Trata-se de aproximação em log, com juros atuais extrapolados; não de retorno contratado por cinco anos. O backtest usa retornos exatos das aplicações e taxas efetivamente observadas em cada mês.
- A otimização considera covariâncias entre moedas, enumera as 50 partições de compra/venda viáveis com teto de 25% e usa SLSQP com gradiente analítico. Maximiza Sharpe previsto, não o realizado. Custos de negociação são descontados depois, não incluídos no objetivo de escolha. Covariância regularizada com 20% de peso na diagonal, fixados antes dos novos resultados.
- Risco mensal: 120 retornos mensais anteriores a cada origem, covariância multiplicada por 60. Essa escala supõe que o risco mensal possa ser agregado dessa forma. No primeiro sinal, janeiro/2010, os retornos usados vão de janeiro/2000 a dezembro/2009.
- Risco de cinco anos: covariância de retornos log acumulados em 60 meses, com endpoints anteriores à origem e janela expansiva. No primeiro sinal há 63 endpoints, de outubro/2004 a dezembro/2009. Eles compartilham muitos meses; a informação independente para risco longo é escassa.
- Treinamento EJR inicial: origens outubro/1999–dezembro/2004, alvos até dezembro/2009; 63 origens por moeda. Depois, expansão mensal apenas com alvos maduros. CPI defasado dois meses, bases históricas revisadas.
- Sinal em janeiro/2010, execução no fechamento de fevereiro/2010, primeiro retorno março/2010. As reescolhas de cinco anos usam sinais de janeiro/2010, janeiro/2015 e janeiro/2020. A previsão é para t+60 e o investimento de 60 meses termina em t+61 por conta do atraso de execução de um mês. Essa diferença foi mantida de forma idêntica entre os testes e consta no protocolo.
- Custos básicos: BRL10, SEK3 e outras moedas2 pb por notional negociado; spread adicional na ponta vendida de 50 pb a.a.; entrada, rebalanceamento e liquidação final cobrados. Estresse conjunto: 4x negociação e 150pb a.a. de spread. Não representa execução validada em corretora, tributação ou remuneração líquida efetiva de saldos.
- Fonte técnica do otimizador: [documentação SciPy SLSQP](https://docs.scipy.org/doc/scipy/reference/optimize.minimize-slsqp.html). Os dados e os resultados são locais; não foram substituídos por informações atuais de mercado.

## Limites e interpretação econômica

Os novos testes não encontraram uma melhora robusta de Sharpe pela otimização nem vantagem sistemática em esperar 60 meses. Isso não refuta a relação preditiva do artigo: avalia a nossa implementação agrupada, nosso universo e período, a extrapolação de juros e as regras de financiamento e posição escolhidas. Esperar pelo horizonte previsto não garante que a previsão se realize nem que a posição supere seu financiamento.

Os 180 meses contêm somente três ciclos consecutivos de cinco anos. Os intervalos são condicionais aos sinais e decisões salvos e não corrigem a seleção histórica de todo o projeto. Não há estimação de Sharpe ótimo usando a amostra de teste.

Reprodução: `tools/python/python.exe horizon_tests/run.py`, depois `tools/python/python.exe horizon_tests/frozen_and_validate.py`. O cache evita recalcular otimizações idênticas; alterar o desenho requer novo cache. 37 verificações aprovadas, incluindo neutralidade, orçamento, teto por moeda, repetibilidade, exclusão de retornos futuros, reprodução independente de previsões por prefixo, manutenção das escolhas durante 60 meses e reprodução dos backtests originais.

Tabelas completas em `tables/metrics.csv`, `entry_windows.csv`, `frozen_metrics.csv`, `frozen_windows.csv`, `intervals.csv`, `full_monthly_intervals.csv`. Pesos mensais em `cache/weights.npz`; auditoria em `tables/optimization_audit.csv` e `tables/validation.json`.
