# Roteiro de apresentação — aproximadamente 12 minutos

## 1. Pergunta (1 minuto)

“O câmbio real pode prever o câmbio nominal em horizontes longos. Mas essa previsibilidade melhora uma carteira depois de pagar juros e custos?”

Explique a diferença entre previsão, retorno e arbitragem. O exercício é preditivo, sem identificação causal de política monetária.

## 2. Teoria e convenção (1 minuto)

S = moeda local por USD; q = log S + log P_US - log P_local. q alto significa moeda local relativamente barata. Se houver reversão, o nominal ou preços relativos precisam se ajustar. Comprar moeda estrangeira exige definir o ativo e a moeda de financiamento.

## 3. Replicação da aula (1 minuto)

Use `classroom_scatter.pdf`. Beta de oito anos -1,808; R² 0,883. Reproduz muito bem o exemplo brasileiro. Pontos sobrepostos não são experimentos independentes. Isso ainda não prova capacidade de negociação.

## 4. Dados e disciplina temporal (1,5 minuto)

Seis moedas, out/1999–ago/2026. CPI defasado 2 meses; alvos de treinamento precisam já ter terminado. Sinal em janeiro → execução fim de fevereiro → primeiro retorno em março. Nenhuma previsão de cinco anos vira lucro no mês seguinte.

Diga explicitamente: “Não tenho todas as vintages históricas; portanto, é pseudo fora da amostra com defasagens, não uma certificação point-in-time.”

## 5. Resultado preditivo (1,5 minuto)

Use `forecast_heatmap.pdf`. EJR agregado/RW = 1,037 em cinco anos. Brasil, Canadá e euro melhoram, mas libra, iene e coroa sueca pioram. Mostre `forecast_models.pdf` se houver tempo: a comparação muda quando as origens são idênticas.

O bootstrap não rejeita a hipótese de câmbio nominal imprevisível a 5%. Em oito anos há somente uma origem espaçada pelo horizonte na janela, mesmo com 70 previsões mensais.

## 6. Carteira e custos (1 minuto)

Duas compras de 25%, duas vendas de 25%, caixa USD de colateral, reestimativa mensal. Sinal = previsão de apreciação da moeda estrangeira + juros. Custos por ponta e spread de captação, entrada/saída e rebalanceamento cobrados. Taxas oficiais são proxies; não há contratos a termo executados.

## 7. Desempenho e falhas (1,5 minuto)

Use `portfolio_wealth.pdf` e `performance_regimes.pdf`. EJR + carry: 2,73% a.a., vol 4,16%, Sharpe 0,31 e queda 7,01%. Carry puro: 4,11%. Perde em 2020–2021; em 2024–2026 quase todo o retorno é caixa. Intervalo do excesso inclui zero; alfa condicional não significativo.

## 8. O ativo em dólar (1 minuto)

Use `brl_assets.pdf`. Caixa USD em BRL sofre risco cambial. BIL aproxima Treasury bills; SPY adiciona bolsa. Ficar comprado em SPY teve grande retorno, mas o sinal cambial não previa o prêmio de ações. O sinal ficou em USD só 13,1% do tempo, e a alocação em BIL não bateu caixa BRL.

## 9. Resposta final (30 segundos)

“Replicamos a relação econômica, mas não encontramos vantagem de negociação robusta sobre carry nesta implementação. O resultado depende de país, regime, custo e ativo financiado. Não demonstramos arbitragem.”

## Perguntas prováveis

- **De onde vem a identificação?** Variação temporal do câmbio real. Não é variação exógena para inferir causalidade. O teste é habilidade de previsão sobre informação passada.
- **Por que o artigo encontra mais previsibilidade?** Amostra, frequência, países e regimes diferentes. O artigo restringe o painel principal antes do limite inferior; a extensão inclui vários regimes posteriores. Também há diferenças de IPC e de lags.
- **Por que cinco anos?** Horizonte representativo da aula, definido antes da execução. Todos os horizontes alternativos foram divulgados; não se escolheu o melhor Sharpe.
- **Por que não selecionar só Brasil e Canadá?** Isso seria seleção após observar o resultado. Seria uma nova hipótese a validar em período futuro.
- **Onde estão os dividendos?** Nos retornos de adjusted close de BIL/SPY; só entram como resultados realizados. Não entram no preditor cambial.
- **A taxa Selic é retorno líquido?** Não. É proxy de caixa. Não há tributação, taxa contratada por investidor ou risco de crédito. Os cenários de custo são assumidos e explicitados.
- **Por que não chamar de arbitragem de longo prazo?** Não existe payoff garantido nem convergência assegurada antes de liquidação/margem. Pode haver perda persistente.
- **Como provar que não houve vazamento?** Mostrar os testes de truncamento e perturbação futura, o log de maturação dos alvos e a regra de execução. Ressalvar revisões históricas ainda não resolvidas.
- **O que faria depois?** Uma extensão específica para deslocamentos da referência real, por exemplo termos de troca, com dados point-in-time e holdout prospectivo, antes de discutir implementação operacional.
