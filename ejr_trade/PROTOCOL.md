# EJR com termos de troca: desenho antes da estimação

15/09/2026. Extensão exploratória solicitada pelo usuário. Nenhuma carteira ou alteração nos slides. Réplica da equação preditiva (3.4), não da amostra histórica, bootstrap estrutural ou DSGE completos de Eichenbaum, Johannsen e Rebelo (2021).

## Amostra e estimador

BRL, EUR, JPY, GBP, CAD, SEK; USD como numerário; outubro/1999–agosto/2026. Alemanha aproxima os dados comerciais do EUR. Prever log S[t+h] − log S[t], S em moeda local/USD, em h=12,24,36,48,60,72,84,96 meses. Avaliar origens desde janeiro/2010 e somente alvos encerrados. Treino expansivo, mínimo 60 origens maduras por moeda e alvos j+h <= t−1. CPI entra dois meses defasado. Mesma equação sem intercepto, inclinação comum e níveis centrados pela média por país disponível até t. Reestimar todos os coeficientes ao adicionar regressores. Mudanças anuais são centradas da mesma maneira, sem acrescentar efeitos fixos. Modelos são comparados nas mesmas linhas de treinamento e avaliação dentro de cada painel.

## Regressores

1. EJR: desvio do log câmbio real.
2. Termos de troca observados, contas nacionais: log[(X corrente/X constante)/(M corrente/M constante)], bens e serviços. Quatro séries anuais WDI baixadas antes de estimar, com história suficiente desde antes de 1999. O endpoint direto NE.TRM.TRAD.XU não retornou observações, por isso construção explícita pelos deflatores, sem alegar download desse índice pronto. Série revisada, sem vintages. Em ano Y usar somente Y−2. Mudança é diferença entre os dois últimos anos consecutivos admissíveis, não entre meses repetidos. Nenhuma interpolação. Não usar Y−1 no principal.
3. Proxy por cesta de commodities: quatro grupos já disponíveis (energia, alimentos, matérias-primas agrícolas, metais); médias de log preços por grupo. Pesos fixos de exportação menos importação como participação no respectivo total, média 1994–1996. Aplicar aos preços reais em USD (deflacionados pelo CPI americano), disponíveis t−2. Equivale à contribuição das commodities ao log da razão de duas cestas com o restante do comércio acompanhando o CPI americano. Não cobre preços efetivos de todo o comércio nem deve ser chamada de índice observado de termos de troca.
4. Para cada medida: nível; mudança de um ano; nível+mudança. Primárias: nível+mudança de termos observados versus EJR; nível+mudança da proxy versus EJR. Diagnósticas: cada componente isolado e ambas medidas juntas.
5. Série de mercadorias UNCTAD/WDI TT.PRI.MRCH.XD.WD: somente 2005–2024. Testar separadamente com EJR reestimado nas mesmas linhas. Não misturar definições ou preencher a história anterior com commodities. Não reduzir treinamento para forçar resultados de 7/8 anos.

## Comparação e variações fixadas

RMSE relativo à ausência de mudança e ao EJR; R2 fora da amostra, acerto de direção e coeficientes. Agregado por erros quadráticos de todas as observações, não média dos índices por moeda. Tabela por moeda em todos os horizontes. Período completo, origens 2019+ e origens comuns aos oito horizontes. Agrupar perda por mês antes de inferência; HAC com h+2 defasagens apenas com >=3(h+2) datas e >=36 datas. Holm para a família primária de dois modelos, oito horizontes, agregado na amostra completa; resultados sem dados suficientes sem p-valor. Intervalos em blocos condicionais não substituem o bootstrap do paper; não tratar meses sobrepostos como ensaios independentes. Diagnóstico não sobreposto em todos os offsets.

Variações: mais um ano de atraso anual e mais um mês de atraso da proxy; treino/avaliação em fins de trimestre com mínimo 20 origens maduras (não réplica de médias trimestrais do artigo); excluir BRL, EUR e ambos com reestimação; proxy antiga de exposição líquida (X*sx−M*sm)/(X+M), distinta da proxy de termos de troca. Nenhuma escolha por melhor RMSE será ocultada.

## Integridade e entrega

Congelar hashes de dados/código anteriores usados. Salvar previsões, coeficientes, amostras, disponibilidade anual, pesos e validação. Auditar truncamento e perturbação de futuro: alterar observações posteriores à origem não pode mudar sua previsão. Conferir EJR base contra src/models.py. Auditar separadamente níveis em amostra completa como descrição, nunca como previsão fora da amostra. Entregar relatório PDF, código e tabelas; transparência sobre poucos episódios de longo prazo, dados revisados, seleção histórica e escopo parcial da replicação.
