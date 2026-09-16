# Guia de apresentação: câmbio real, commodities e carry

17 slides principais, 19 minutos previstos, 2 slides de apoio.

## Slide 01 — Câmbio real, commodities e carry trade

Tempo: 30 segundos.

O trabalho investiga se uma informação útil para prever câmbio também ajuda a decidir como carregar uma posição.

### Conceitos que você precisa dominar

Há três objetos diferentes ao longo da apresentação. A replicação procura reproduzir uma relação econômica do artigo. A previsão avalia erros em observações futuras. O backtest calcula o resultado de uma regra de investimento, incluindo juros e câmbio. Um sucesso no primeiro objeto não implica sucesso nos seguintes. O projeto percorreu essas etapas e encontrou tanto fracassos quanto resultados históricos promissores.

### Como ler o slide

A capa apenas apresenta a pergunta e a referência. Não tente antecipar todos os resultados ou explicar todas as extensões aqui.

### Fala sugerida

Meu trabalho parte de uma ideia do artigo de Eichenbaum, Johannsen e Rebelo: o câmbio real pode conter informação sobre o câmbio nominal futuro. Eu verifico a relação da aula, testo se ela melhora uma estratégia de carry e investigo o papel de commodities e do comércio. A tentativa mais direta de carteira falhou. Os resultados posteriores sugerem alguma utilidade para controlar a exposição, com limitações importantes.

### Cuidado com a interpretação

Apresente como uma extensão empírica exploratória. Não anuncie uma estratégia comprovadamente superior.

### Pergunta provável

Qual é a pergunta central? A informação sobre câmbio real e comércio melhora a previsão e, separadamente, a decisão de assumir risco cambial?

### Transição

Primeiro, preciso explicar por que o artigo olha para o câmbio real.

Fontes: Artigo EJR, introdução; synthesis/README.md

## Slide 02 — A ideia econômica do artigo

Tempo: 70 segundos.

Uma diferença persistente de preços relativos pode se ajustar pelo câmbio nominal ou pela inflação relativa.

### Conceitos que você precisa dominar

Câmbio nominal S é o preço do dólar em moeda local. No Brasil, S = 5 significa R$ 5 por US$ 1. O câmbio real Q = S × P_US / P_local ajusta essa cotação pelos níveis de preços das duas economias. Trabalhamos com o logaritmo q. Quando q sobe, a moeda local sofre depreciação real, ficando relativamente barata. Essa classificação depende da referência histórica, não de um valor justo conhecido. A identidade implica que a mudança real soma a mudança nominal à inflação americana menos a inflação local. Se a inflação relativa responde pouco, o ajuste tende a aparecer mais no nominal.

### Como ler o slide

Leia a fórmula em palavras, sem demonstrá-la. Depois explique os dois achados do artigo: capacidade preditiva para câmbio nominal em países com metas de inflação e pouca capacidade para inflação futura. EJR é apenas a sigla dos sobrenomes dos três autores.

### Fala sugerida

Câmbio nominal é a cotação que vemos no mercado. Câmbio real também considera o que os preços fizeram nos dois países. Por exemplo, se os preços brasileiros sobem relativamente aos americanos e a cotação não muda, o real fica mais caro em termos reais. O artigo pergunta como esse tipo de diferença se ajusta. Nos países com metas de inflação estudados, o câmbio real ajuda a prever o nominal futuro, mas prevê pouco a inflação. A intuição é que, quando os preços estão mais ancorados, parte maior do ajuste pode aparecer na cotação. O artigo também estima um modelo estrutural. Meu exercício reproduz a parte preditiva e o exemplo da aula, sem reestimar esse modelo completo.

### Cuidado com a interpretação

A identidade contábil não prova reversão à média nem identifica o efeito causal das metas de inflação. Não diga que toda moeda barata necessariamente valoriza.

### Pergunta provável

Câmbio real é a cotação descontada do IPCA brasileiro? Não. Ele envolve preços relativos entre duas economias, com uma convenção definida para a cotação.

### Transição

A primeira verificação foi reproduzir a relação mostrada na aula.

Fontes: Artigo EJR, resumo e introdução; src/models.py: features

## Slide 03 — A relação da aula aparece na replicação

Tempo: 75 segundos.

A replicação brasileira recupera a inclinação de oito anos da aula, aproximadamente −1,808.

### Conceitos que você precisa dominar

Cada ponto relaciona o desvio do câmbio real em um mês à mudança do log da cotação nos oito anos seguintes. O eixo horizontal usa q menos sua média no exercício histórico. O eixo vertical usa log(S daqui a oito anos / S hoje). Um valor vertical negativo representa apreciação nominal da moeda local. A inclinação negativa indica que meses de real mais depreciado se associaram a apreciação posterior. O R² mede a fração da variação do alvo explicada pelo ajuste dentro da amostra. Não é a probabilidade de acertar uma previsão nem uma medida de rentabilidade.

### Como ler o slide

Comece pelos eixos. Aponte a inclinação descendente. Só então diga que o coeficiente de −1,808 praticamente coincide com o valor da aula e que o R² é 0,883. Há 280 origens mensais, de janeiro de 1995 a abril de 2018, com resultados até abril de 2026. As observações compartilham muitos dos mesmos meses futuros.

### Treinamento, previsão e avaliação

Ajuste descritivo: jan/1995–abr/2026. Sem divisão entre treino e teste. Origens de oito anos até abr/2018.

### Fala sugerida

Neste gráfico, cada ponto é um mês brasileiro. À direita estão momentos de maior depreciação real. Para baixo estão apreciações nominais nos oito anos seguintes. A relação é claramente negativa, e a inclinação de menos 1,808 praticamente reproduz o número da aula. O R² é alto, cerca de 88%. Mas esse resultado descreve o ajuste da relação na amostra histórica. Não significa que o modelo acerta 88% das operações. Além disso, previsões feitas em dois meses vizinhos usam quase os mesmos oito anos seguintes, então os pontos não são evidências independentes. A próxima etapa é perguntar se essa relação ajuda quando eu realmente escondo o futuro do modelo.

### Cuidado com a interpretação

Este gráfico usa ajuste dentro da amostra. Não o apresente como uma previsão produzida em tempo real ou como replicação integral do artigo.

### Pergunta provável

Por que o coeficiente é menor que −1? A regressão permite esse valor no horizonte longo. Isso não significa retorno mensal de 180% ou convergência garantida. É uma relação entre mudanças e desvios em log.

### Transição

Reproduzir a relação histórica e prever dados futuros são testes diferentes.

Fontes: output/tables/classroom_replication.csv; data/processed/classroom.csv; Macro_Aplicada_2026_shared/Slides/Macro_Aplicada_aula_8.pdf

## Slide 04 — A previsão varia por país e horizonte

Tempo: 90 segundos.

O Brasil melhora em todos os seis horizontes. O painel agrupado perde para nenhuma mudança nas janelas completas de cada horizonte.

### Conceitos que você precisa dominar

Em cada origem t, estimamos a mudança futura do log da cotação a partir do desvio real. A inclinação é comum a seis moedas, e a média histórica de q é específica de cada moeda. A janela de treinamento se expande desde outubro de 1999. Exigimos pelo menos 60 origens de treinamento por moeda cujos alvos já tenham terminado até t−1. O CPI entra com dois meses de defasagem. Repetimos a estimação a cada mês, prevemos e avaliamos o erro quando o horizonte termina. O RMSE relativo compara esse erro com nenhuma mudança. O teste de Clark–West usa correção para dependência temporal. O resultado agregado de cinco anos não estabelece superioridade estatística. Dados revisados limitam o caráter estritamente em tempo real.

### Como ler o slide

A tabela mostra cada moeda e o agregado das seis moedas, usando a mesma especificação EJR agrupada. BRL é real, EUR euro, JPY iene, GBP libra, CAD dólar canadense e SEK coroa sueca. Todas são avaliadas contra USD. Valores abaixo de 1 aparecem em verde e indicam menor RMSE que prever nenhuma mudança. O agregado reúne os erros do painel; não é uma soma nem uma média simples das razões individuais. Em cinco anos, o Brasil tem 0,792 e o agregado 1,037. Em oito anos, 0,816 e 1,115. Os períodos de origem de cada horizonte estão no rodapé e são diferentes entre as linhas.

### Treinamento, previsão e avaliação

Treino expansivo desde out/1999; mínimo de 60 origens maduras por moeda e alvos de treino até t−1. Origens avaliadas: 1 ano jan/2010–ago/2025; 2 anos jan/2010–ago/2024; 3 anos jan/2010–ago/2023; 5 anos jan/2010–ago/2021; 7 anos nov/2011–ago/2019; 8 anos nov/2012–ago/2018. Alvos realizados até ago/2026.

### Fala sugerida

O teste fora da amostra não diz que a regressão falha em todo lugar. O Brasil melhora em todos os horizontes mostrados. Em cinco anos, seu erro é cerca de 21% menor que o de prever nenhuma mudança. Mas o resultado agregado das seis moedas é pior que essa referência. Essa heterogeneidade é central. Também não estamos comparando exatamente a regressão brasileira do slide anterior: agora a inclinação é comum às moedas e muda conforme novas observações ficam disponíveis. As janelas indicadas no rodapé são diferentes. Quando uso as mesmas datas de origem, o painel melhora em um, dois e três anos. Portanto, a conclusão depende do país, horizonte e período.

### Cuidado com a interpretação

Não conclua que câmbio é imprevisível em qualquer horizonte. As linhas têm períodos distintos. O ganho de erro não basta, sozinho, para demonstrar significância estatística ou valor de investimento.

### Pergunta provável

E se estimarmos só para o Brasil? A regressão brasileira com intercepto e inclinação próprios tem erro relativo 0,596 em oito anos. É outro modelo e um resultado favorável, mas com forte sobreposição dos alvos. No painel com origens comuns de nov/2012 a ago/2018, os erros são 0,958, 0,950 e 0,964 em um, dois e três anos.

### Transição

A heterogeneidade preditiva motivou testar se a previsão ajuda na escolha das posições de carry.

Fontes: output/tables/forecast_accuracy.csv; output/tables/forecast_common_origins.csv; output/tables/timing_audit.csv

## Slide 05 — A proposta inicial para o carry

Tempo: 85 segundos.

Comparar escolher posições pelo diferencial de juros com escolher pelo diferencial de juros mais a valorização cambial prevista.

### Conceitos que você precisa dominar

Carry ou carrego é a remuneração associada ao diferencial de juros de uma posição financiada em outra moeda. Comprar uma moeda envolve um ativo nessa moeda, como um depósito, enquanto a outra ponta financia a operação. O projeto usa proxies de aplicações de curto prazo, não retornos de bolsa ou títulos longos. Quem compra a moeda de juros altos ganha com apreciação dessa moeda e perde com sua depreciação. No painel, cada regra compra as duas moedas de maior sinal e vende as duas de menor sinal, com 25% de notional em cada ponta. A soma dos valores absolutos é 100% e a exposição líquida é zero. Há caixa em dólar como colateral.

### Como ler o slide

Leia a aproximação de retorno: diferencial de juros mais valorização da moeda comprada, menos custos. O exemplo é hipotético: ativo rende 10%, financiamento custa 3% e a moeda comprada cai 8% em dólar. O resultado exato antes de custos é 1,10 × 0,92 − 1,03 = −1,8% sobre o notional. A soma simples daria −1%, pois ignora a interação entre juros e câmbio.

### Fala sugerida

Eu comparei duas formas de escolher as posições. A primeira olha apenas para quais moedas pagam mais juros. A segunda acrescenta a valorização cambial prevista pelo modelo. Nas duas, o retorno realizado inclui tanto os juros quanto a mudança do câmbio. O que muda é a informação usada para escolher a carteira. O risco é que a desvalorização da moeda consuma o juro recebido. Neste exemplo, ganhar 10% no ativo e pagar 3% no financiamento parece oferecer uma folga de 7%, mas uma queda de 8% da moeda já produz perda. No backtest, calculo o retorno combinado de forma exata, incluindo a interação e os custos. A previsão de cinco anos apenas orienta a decisão, sem garantir o caminho mensal.

### Cuidado com a interpretação

‘Carry sozinho’ significa sinal baseado só em juros. Não significa retorno sem câmbio. O retorno líquido não é apenas uma soma exata de duas parcelas.

### Pergunta provável

A estratégia compra dólar ou bolsa americana? Aqui o dólar é o numerário e o caixa de colateral. As posições cambiais usam aplicações curtas e financiamento nas moedas. Ações americanas seriam outro risco e outro exercício.

### Transição

A primeira tentativa foi simples, e o resultado foi pior que o carry original.

Fontes: src/models.py: run_book e rank_weights; report/relatorio.tex

## Slide 06 — Adicionar a previsão ao ranking piorou o retorno

Tempo: 80 segundos.

O carry com previsão rendeu menos e teve Sharpe menor, apesar de alguma redução do drawdown.

### Conceitos que você precisa dominar

Não usamos a otimização média-variância de Markowitz. Ordenamos seis moedas por um sinal e compramos as duas de maior sinal, vendendo as duas de menor sinal. Cada ponta recebe 25% do patrimônio em notional: 100% bruto e zero líquido. O carry usa diferencial de juros. O ranking alternativo soma apreciação prevista, aproximada como −previsão de Δs em 60 meses/60. Reavaliamos mensalmente, sem compromisso de manter cada moeda por cinco anos. O caixa em dólar serve de colateral. Retorno anual composto é crescimento do patrimônio, volatilidade é dispersão anualizada, Sharpe usa excesso sobre o caixa e queda máxima mede a perda desde o pico.

### Como ler o slide

Compare retorno anual de 4,11% e 2,73%, e Sharpe de 0,60 e 0,31. Depois leia o rodapé: backtest de março de 2010 a agosto de 2026, sinal de cinco anos, revisão mensal e treinamento expansivo. Os custos de negociação por notional transacionado são 10 pontos-base para BRL, 3 para SEK e 2 para as outras moedas. Há também spread de financiamento de 50 pontos-base ao ano na ponta vendida. Um ponto-base é 0,01 ponto percentual. Entrada, rebalanceamento e liquidação final pagam os custos assumidos.

### Treinamento, previsão e avaliação

Primeiro sinal: jan/2010. Treino EJR: origens out/1999–dez/2004 (63 meses por moeda), alvos até dez/2009. A janela se expande mensalmente. Previsão: 60 meses. Sinal t, execução t+1 e retorno t+2. Backtest: mar/2010–ago/2026.

### Fala sugerida

Não montamos uma carteira de Markowitz. As duas estratégias usam um ranking com pesos iguais: duas compras e duas vendas. Na primeira, o ranking olha só os juros. Na segunda, acrescenta a previsão cambial. Ambas recebem juros, carregam risco cambial e pagam os custos indicados no rodapé. O carry rendeu 4,11% ao ano e a alternativa 2,73%, com Sharpe menor. A previsão olha cinco anos à frente, mas a carteira é revista todo mês. Esse prazo de previsão não é o vencimento de uma operação. Escolhemos aplicações curtas para estudar carry e câmbio. Usar bolsa adicionaria retorno e risco acionário e exigiria uma avaliação diferente.

### Cuidado com a interpretação

Não diga Markowitz, otimização de pesos ou posição fixa de cinco anos. Os custos são hipóteses agregadas de negociação e financiamento, não uma lista de tarifas executadas por corretora. Não incluem uma tributação específica do investidor.

### Pergunta provável

Por que usar juros em vez de bolsa? Para manter a pergunta focada em diferencial de juros e câmbio, sem adicionar prêmio de ações ou risco de duração de títulos longos. Isso é uma escolha adequada ao experimento, não uma demonstração de que juros sejam sempre o melhor ativo.

### Transição

O gráfico seguinte mostra como essa diferença se acumulou no patrimônio.

Fontes: output/tables/portfolio_metrics.csv

## Slide 07 — O ranking com previsão acumulou menos patrimônio

Tempo: 50 segundos.

As duas carteiras incluem juros, câmbio e custos. O ranking com previsão termina abaixo do carry por juros.

### Conceitos que você precisa dominar

Patrimônio base 100 é o valor acumulado após reinvestir os retornos mensais líquidos. Um nível de 195 significa ganho total próximo de 95%, e não retorno anual de 95%. A linha de caixa usa a mesma remuneração USD do backtest. Comparar o patrimônio não muda a estratégia: é outra forma de mostrar os resultados da tabela anterior.

### Como ler o slide

As linhas cobrem março de 2010 a agosto de 2026. Compare os pontos finais e depois o caminho, sem tentar explicar cada oscilação. O gráfico usa os mesmos 198 retornos da tabela do slide 6, com inicialização em 100 antes do primeiro retorno.

### Treinamento, previsão e avaliação

Primeiro sinal: jan/2010. Treino EJR: origens out/1999–dez/2004 (63 meses por moeda), alvos até dez/2009. A janela se expande mensalmente. Previsão: 60 meses. Sinal t, execução t+1 e retorno t+2. Backtest: mar/2010–ago/2026.

### Fala sugerida

Este é o resultado acumulado das mesmas duas regras. A linha do carry por juros termina acima da linha que acrescenta a previsão cambial. A diferença não vem de excluir os juros de uma delas: ambas incluem juros, câmbio, financiamento e negociação. A linha de caixa permite visualizar quanto seria recebido apenas no colateral em dólar. O gráfico reforça o fracasso da alteração direta do ranking nesta implementação.

### Cuidado com a interpretação

O horizonte de cinco anos pertence à previsão. A regra da carteira revê posições todo mês e pode continuar na mesma moeda por vários meses.

### Pergunta provável

São operações independentes de um mês? A carteira tem decisões mensais. Uma moeda pode permanecer na posição se o ranking continuar favorável. Calculamos o resultado dessa exposição sucessiva, com custos sobre as mudanças do notional.

### Transição

Depois desse resultado, investiguei se commodities e comércio ajudam a própria previsão.

Fontes: output/tables/portfolio_returns.csv; output/tables/portfolio_metrics.csv; src/models.py

## Slide 08 — Commodities e condições de troca

Tempo: 65 segundos.

Uma mesma alta de commodities pode beneficiar um exportador e prejudicar um importador, alterando a referência econômica da moeda.

### Conceitos que você precisa dominar

Termos de troca são a razão entre preços das exportações e preços das importações. Sua melhora significa que uma dada quantidade exportada compra mais importações. Isso é diferente de saldo comercial, que também depende de quantidades, e de composição comercial, que descreve o que o país compra e vende. Um índice de preços de commodities ponderado pela exposição comercial é uma proxy parcial desses incentivos. Ele não é automaticamente o índice agregado de termos de troca do país. A hipótese é que o câmbio real compatível com os fundamentos possa mudar, tornando a média histórica uma referência incompleta.

### Como ler o slide

O exemplo de petróleo é ilustrativo: a alta tende a favorecer o exportador líquido e a encarecer a conta do importador líquido. Diga ‘pode’ ao falar do efeito cambial. A resposta depende também de importações, quantidades, política econômica e outros choques. Os testes seguintes só preveem variáveis, sem construir carteiras de commodities.

### Fala sugerida

A média histórica do câmbio real pode ser uma referência limitada. Imagine uma alta persistente do petróleo: o efeito econômico é diferente para um exportador líquido e para um importador líquido. Os termos de troca resumem a relação entre os preços do que o país vende e do que compra. Eu acrescentei preços de commodities e informações sobre a exposição comercial às regressões. A hipótese é que parte do aparente desvio cambial reflita uma mudança nos fundamentos. Aqui é importante separar três medidas: preços de commodities, termos de troca agregados e composição do comércio. Elas são relacionadas, mas não são a mesma variável. Nesta etapa, o resultado avaliado é apenas a previsão.

### Cuidado com a interpretação

Não chame toda alta de commodity de melhora nos termos de troca. Não interprete mudanças em pesos comerciais medidos em valor como prova de mudança estrutural de quantidades.

### Pergunta provável

O teste identifica o câmbio de equilíbrio? Não. Estima relações preditivas condicionais. Um equilíbrio estrutural exigiria hipóteses e identificação adicionais.

### Transição

A primeira extensão manteve o alvo do artigo: a mudança futura do câmbio nominal.

Fontes: third/README.md; third/data/trade_weights.csv; trade_extension/build_report.py

## Slide 09 — Commodities na previsão feita em cada mês

Tempo: 80 segundos.

A extensão nominal reduz o erro na janela completa, mas perde para nenhuma mudança nas origens mais recentes.

### Conceitos que você precisa dominar

Origem é o mês em que fazemos a previsão. Exemplo: origem em janeiro de 2010 com horizonte de 60 meses tem alvo em janeiro de 2015. A tabela não separa treinos feitos em 2010 e 2019. Ela compara conjuntos de previsões emitidas nessas datas, cada uma com seu treinamento admissível. O modelo mantém o desvio real EJR e acrescenta preços reais de commodities, com componente global e componente de exposição comercial específica. Pesos comerciais fixos usam 1994–1996. Os preços entram defasados dois meses. Estimamos os coeficientes em conjunto, com janela expansiva e sem usar resultados futuros.

### Como ler o slide

A coluna de 2010–2021 contém 140 origens mensais, de janeiro de 2010 a agosto de 2021, cujos alvos terminam de janeiro de 2015 a agosto de 2026. A coluna de 2019–2021 contém 32 origens, com alvos de janeiro de 2024 a agosto de 2026. Ela é um subconjunto recente, não um teste independente. O erro da referência de nenhuma mudança vale 1 em cada coluna. EJR + commodities tem 0,890 na janela completa e 1,630 na recente. Os alvos de cinco anos se sobrepõem fortemente.

### Treinamento, previsão e avaliação

Primeira origem avaliada: jan/2010. Treino: origens out/1999–dez/2004, alvos até dez/2009. Janela expansiva, mínimo 60 origens maduras por moeda. Previsão nominal de 60 meses. Última origem avaliada: ago/2021, alvo ago/2026.

### Fala sugerida

Origem é a data em que emitimos uma previsão. Se ela nasce em janeiro de 2010 e olha cinco anos à frente, verificamos seu resultado em janeiro de 2015. Aqui, cada previsão usa uma regressão reestimada com a história admissível naquela data. Na coluna completa há 140 previsões mensais por moeda. Na recente, usamos apenas as 32 feitas de 2019 a agosto de 2021. Acrescentar commodities reduz o erro para 0,890 no conjunto completo, mas o erro recente é 1,630, acima da referência. Assim, há uma melhora em parte da história, sem estabilidade no período recente. Essas datas não são o treinamento: são as datas em que as previsões foram feitas.

### Cuidado com a interpretação

‘Reduziu o erro’ precisa sempre nomear o benchmark e a janela. Não use a melhora sobre um modelo fraco como prova de previsibilidade robusta.

### Pergunta provável

Por que paramos as origens em agosto de 2021 se temos dados até 2026? Porque precisamos observar os cinco anos seguintes para avaliar cada previsão. Uma previsão emitida em 2025 ainda não pode ser avaliada em seu horizonte completo de 60 meses.

### Transição

Também testei uma pergunta diferente: prever o próprio câmbio real de longo prazo.

Fontes: third/tables/metrics.csv: B_FX_60, REJR_Specific, benchmark EJR; third/tables/sensitivity.csv; third/engine.py: ejr_extension

## Slide 10 — Prever o câmbio real continuou difícil

Tempo: 65 segundos.

A informação comercial melhora um pouco a regressão de câmbio real, mas não supera a previsão de nenhuma mudança.

### Conceitos que você precisa dominar

Agora o alvo muda: antes era a cotação nominal, agora é q daqui a cinco anos menos q hoje. A regressão base contém nível real centrado e sua mudança passada. A extensão adiciona o índice de preços comerciais com pesos que se atualizam usando informações históricas defasadas, além da variação passada desse índice. Para comparar modelos, a base é reestimada nas mesmas observações disponíveis para a extensão. Esse cuidado evita atribuir às novas variáveis uma melhora causada apenas por mudança de amostra.

### Como ler o slide

A previsão de nenhuma mudança real tem erro relativo 1. A base tem 2,20 e a extensão com preços e pesos comerciais tem 2,08. São 104 origens de janeiro de 2013 a agosto de 2021. A redução em relação à regressão base é aproximadamente 5%, mas o erro continua mais que o dobro do benchmark simples. Não compare esses níveis de erro diretamente aos do slide anterior: o alvo e a amostra são diferentes.

### Treinamento, previsão e avaliação

Primeira origem avaliada: jan/2013. Treino da extensão e da base pareada: dez/2000–out/2007, com disponibilidade dos alvos até dez/2012. Expansivo, mínimo 60 origens. Alvo de cinco anos, com CPI defasado dois meses. Avaliação: jan/2013–ago/2021, alvos até ago/2026.

### Fala sugerida

Aqui eu mudo a pergunta. Em vez de prever o câmbio nominal, tento prever a mudança do câmbio real em cinco anos. A informação comercial reduz o erro da regressão base de 2,20 para 2,08. É uma pequena melhora relativa, mas ambos os modelos perdem bastante para nenhuma mudança, que vale um. Os testes com termos de troca agregados anuais também não estabeleceram uma solução robusta e têm uma amostra ainda menor. Assim, não consigo defender que aprendi a prever de forma confiável uma nova referência real de longo prazo. Esse resultado negativo ajuda a limitar o que posso dizer sobre os fundamentos.

### Cuidado com a interpretação

O número 2,08 é razão de erro, não previsão de depreciação de 208%. A proxy comercial mensal e os termos de troca agregados anuais são testes distintos.

### Pergunta provável

E a hipótese de mudança no equilíbrio? Continua economicamente plausível, mas estes resultados preditivos não a estabelecem nem identificam um novo valor de equilíbrio.

### Transição

Com previsões frágeis, eu passei a testar decisões de exposição mais específicas.

Fontes: trade_extension/tables/prediction_metrics.csv: real_60; trade_extension/analyze.py

## Slide 11 — A informação passa a controlar a posição

Tempo: 105 segundos.

A combinação posterior mantém a lógica de carry e usa sinais para dimensionar, permitir ou encerrar posições.

### Conceitos que você precisa dominar

O módulo A reduz o tamanho do carry quando o retorno previsto é baixo em relação à referência passada e elimina pares com mudança comercial observada muito alta. O módulo B só entra se o retorno previsto anualizado, suavizado por seis meses, superar 2%, e evita pares com movimento adverso forte dos preços comerciais. O módulo C distribui entradas mensais em parcelas, cada uma com duração máxima de 12 meses, e antecipa a saída quando o modelo com composição comercial indica aumento relevante do risco de o câmbio consumir os juros, relativamente ao modelo base. Os limites de eventos extremos usam o percentil 80 da história passada. A combinação usa um terço dos pesos de cada módulo e calcula custos após agregar as posições.

### Como ler o slide

Explique cada linha como uma decisão concreta: quanto comprar, quando entrar, quando sair. Dê mais tempo ao terceiro módulo. Uma ‘coorte’ é simplesmente o lote de posições aberto em um mês. Cada lote tem orçamento limitado, em vez de multiplicar a exposição ao somar vários meses. Os pares retirados saem com as duas pontas, preservando a neutralidade líquida.

### Treinamento, previsão e avaliação

EJR: janela expansiva desde out/1999 e previsão nominal de 60 meses. Risco comercial: origens desde jan/2011, mínimo 36 datas maduras e alvo de 12 meses, mais atraso de execução. Limiares comerciais: mínimo 36 meses anteriores. Backtest comum: abr/2018–ago/2026.

### Fala sugerida

A mudança foi usar a informação para controlar o carry. O primeiro módulo decide quanto investir: reduz a posição quando a remuneração prevista está fraca e evita mudanças comerciais extremas. O segundo decide quando entrar: exige uma remuneração prevista mínima e evita movimentos comerciais adversos. O terceiro decide quando sair: abre pequenas parcelas ao longo dos meses, com prazo máximo de um ano, e encerra antes quando a informação comercial indica risco adicional relevante de o câmbio consumir os juros. Esse risco adicional compara o modelo com comércio ao modelo base, respeitando a direção original da posição. Eu combino os três com pesos iguais. Essas regras já são mais complexas e foram escolhidas depois de explorar a história, então os resultados seguintes precisam ser tratados como exploratórios.

### Cuidado com a interpretação

O sinal de risco adicional é uma diferença entre modelos, não simplesmente a mudança mensal de uma probabilidade. Não chame a combinação de modelo ótimo ou escolhido em uma amostra totalmente intocada.

### Pergunta provável

Por que pesos iguais? É uma combinação simples, que evita otimizar os pesos para o maior Sharpe. Ainda assim, a escolha dos componentes já usa aprendizados da história examinada.

### Transição

Para comparar, eu coloco o carry e a combinação exatamente nas mesmas datas.

Fontes: synthesis/model.py: make_policies; synthesis/PROTOCOL.md; synthesis/EXPLORATION.md

## Slide 12 — A combinação teve risco menor na janela comum

Tempo: 80 segundos.

Entre abril de 2018 e agosto de 2026, a combinação apresentou retorno semelhante ao carry com menor volatilidade e menor exposição.

### Conceitos que você precisa dominar

A janela comum começa quando todos os módulos já podem funcionar. Tem 101 retornos mensais. O retorno total inclui remuneração do caixa em dólar, contribuições dos ativos e financiamento, além de custos assumidos. O Sharpe usa excesso sobre o caixa. Exposição bruta é a soma do valor absoluto das posições dividida pelo patrimônio. A combinação teve exposição bruta média de 48%, contra 100% do carry. Isso explica parte da queda de risco e deve aparecer ao lado das métricas, não como ressalva escondida.

### Como ler o slide

Leia primeiro retorno anual de 5,78% e 5,94%: são próximos. Depois destaque volatilidade de 4,11% e 2,33%, e queda máxima de 9,09% e 1,43% em magnitude. Termine obrigatoriamente na exposição de 100% e 48%. O Sharpe sobe de 0,75 para 1,37. Os sinais negativos na linha de queda máxima representam perdas em relação ao pico.

### Treinamento, previsão e avaliação

Primeiro sinal da janela comum: fev/2018. EJR: origens out/1999–jan/2013. Risco comercial: jan/2011–dez/2016. Resultados disponíveis até jan/2018. Reestimação expansiva mensal. Backtest: abr/2018–ago/2026.

### Fala sugerida

Na janela comum, o retorno anual ficou próximo: 5,78% no carry e 5,94% na combinação. A diferença mais visível aparece no risco: a volatilidade caiu de 4,11% para 2,33% e a queda máxima observada caiu de 9,09% para 1,43%. O Sharpe aumentou. Mas existe uma explicação importante: a combinação carregou, em média, apenas 48% de exposição bruta. Parte do resultado vem simplesmente de assumir menos risco e permanecer mais em caixa. Eu fiz controles de exposição, mas eles não eliminam toda a incerteza sobre a vantagem. O que posso mostrar é uma trajetória histórica mais estável, sem afirmar uma rentabilidade superior garantida.

### Cuidado com a interpretação

A diferença de retorno de 0,16 ponto percentual de CAGR é pequena. Não apresente o Sharpe observado como prova estatística de alfa.

### Pergunta provável

Bastava investir metade no carry? O controle retrospectivo com exposição média de 48% rendeu 4,18% ao ano e teve queda máxima de 4,02%, contra 5,94% e 1,43% da combinação. Isso é diagnóstico útil, mas usa a média conhecida depois e não prova superioridade futura.

### Transição

Antes de ver o gráfico, verifico o que muda quando altero o prazo dos lotes.

Fontes: synthesis/tables/metrics.csv: common, all; synthesis/tables/exposure_controls.csv

## Slide 13 — O prazo dos lotes altera a exposição e o resultado

Tempo: 65 segundos.

A carteira funciona continuamente, mas a duração máxima dos lotes do módulo de permanência modifica a composição, a exposição e o risco.

### Conceitos que você precisa dominar

A combinação tem três módulos. Os dois primeiros revêm o carry mensalmente. O terceiro abre novos lotes mensais e permite carregá-los até um prazo máximo, com saída antecipada por risco. Aqui só variamos esse máximo entre 6, 12 e 24 meses. O orçamento de entrada mensal desse módulo é 1/H, onde H é o prazo máximo, preservando o teto de exposição. As previsões permanecem as mesmas: EJR de 60 meses e risco de consumo dos juros em 12 meses. Portanto, é uma sensibilidade de política de permanência, não uma comparação de novos modelos de previsão para cada prazo.

### Como ler o slide

A tabela mostra a combinação inteira na mesma janela de abril de 2018 a agosto de 2026, com os mesmos custos. Para 6, 12 e 24 meses, os retornos anuais são 5,96%, 5,94% e 5,77%. A exposição média cai de 51% para 48% e 44%. Essa mudança de exposição participa da diferença de risco. A saída pode ocorrer antes do máximo e a entrada é gradual.

### Treinamento, previsão e avaliação

Primeiro sinal da janela comum: fev/2018. EJR: origens out/1999–jan/2013. Risco comercial: jan/2011–dez/2016. Resultados disponíveis até jan/2018. Reestimação expansiva mensal. Backtest: abr/2018–ago/2026.

### Fala sugerida

Mesmo com uma carteira contínua, o prazo importa. Aqui mantive os outros dois módulos e alterei apenas o prazo máximo dos lotes do módulo de permanência. O retorno muda pouco entre seis e doze meses e cai um pouco em vinte e quatro. A exposição também cai conforme aumenta o prazo máximo, porque as entradas são menores e podem sair antes por risco. Isso mostra que o prazo muda a política, mas não prova que doze meses seja ótimo. E não mudamos o horizonte do modelo de risco: ele continua olhando doze meses.

### Cuidado com a interpretação

Os prazos são máximos, não permanências garantidas. Não confunda prazo do lote, frequência mensal de revisão, previsão nominal de 60 meses e previsão de risco de 12 meses. Os testes usam a mesma história exploratória.

### Pergunta provável

Por que o prazo maior reduziu a exposição? Com orçamento 1/H por entrada e saída antecipada, muitos lotes podem sair antes de completar H meses. A formação gradual e o cancelamento entre pontas também influenciam a exposição líquida por moeda. Isso deve ser considerado ao comparar o risco.

### Transição

A trajetória do patrimônio da combinação-base, com lotes de até doze meses, aparece no próximo gráfico.

Fontes: synthesis/tables/robustness.csv: Base, Tenure6, Tenure24; synthesis/model.py: make_policies, cohorts; synthesis/robustness.py

## Slide 14 — A trajetória explica o resultado de risco

Tempo: 50 segundos.

O patrimônio final é parecido, mas o carry apresenta perdas e recuperações mais pronunciadas.

### Conceitos que você precisa dominar

O gráfico acumula retornos líquidos, com patrimônio inicial 100. O retorno final é semelhante, mas as trajetórias de perdas diferem. A carteira recebe novas decisões mensais e não tem uma única janela fixa de treinamento. Em fevereiro de 2018, primeiro sinal para retorno em abril, o EJR usa origens de outubro de 1999 a janeiro de 2013, com alvos terminados até janeiro de 2018. O modelo de risco comercial usa origens de janeiro de 2011 a dezembro de 2016, com resultados disponíveis até janeiro de 2018. Depois as duas janelas se expandem e os modelos são reestimados. A combinação contém também regras baseadas em preços e limiares calculados com a história passada.

### Como ler o slide

Aponte a trajetória, sem tentar explicar cada oscilação. A queda do carry em torno de 2020 é mais visível que a da combinação. O painel de perdas mostra a profundidade em relação ao pico. Como o retorno final é semelhante, este slide reforça que o achado principal é a suavização histórica do caminho.

### Treinamento, previsão e avaliação

Primeiro sinal: fev/2018. EJR: out/1999–jan/2013, alvos até jan/2018. Risco comercial: jan/2011–dez/2016, alvos disponíveis até jan/2018. Janelas expansivas. Backtest: abr/2018–ago/2026.

### Fala sugerida

Aqui todas as estratégias começam em 100. O ponto final do carry e da combinação é próximo, mas o caminho é diferente. O carry atravessa uma queda mais pronunciada em torno de 2020, enquanto a combinação mantém uma trajetória mais estável nessa janela. O painel de baixo mostra a perda em relação ao pico anterior. A linha do caixa lembra que parte do retorno total vem da remuneração em dólar, mesmo quando a exposição cai. Esta figura ajuda a entender por que duas carteiras com retorno final parecido podem ter riscos bastante diferentes.

### Cuidado com a interpretação

O gráfico descreve o que ocorreu. Ele não identifica que um filtro específico causou cada diferença durante uma crise.

### Pergunta provável

A previsão foi treinada de 2018 a 2026? Não em uma única estimação que olha todo o período. A cada mês, usamos apenas a história admissível, mas a escolha dos módulos usou pesquisa sobre essa história já examinada. Para o primeiro retorno, o sinal vem de fevereiro de 2018 e a execução de março. Em junho de 2026, o EJR já usa origens até maio de 2021 e alvos até maio de 2026.

### Transição

Também vale separar contabilmente o que veio dos juros e o que veio do câmbio.

Fontes: synthesis/tables/returns.csv.gz: common; synthesis/tables/metrics.csv

## Slide 15 — Menos juros, contribuição cambial melhor

Tempo: 55 segundos.

Na combinação, a menor exposição reduziu o recebimento de juros, enquanto a contribuição cambial histórica melhorou.

### Conceitos que você precisa dominar

A atribuição divide a média mensal do retorno em excesso em parcelas contábeis e multiplica por 12. Os valores são pontos percentuais de contribuição anual, não CAGRs separáveis. Carry: câmbio 0,74 p.p. e juros 2,62 p.p. Combinação: câmbio 1,82 p.p. e juros 1,50 p.p. Interação, spread de financiamento e custos completam a conta. O excesso médio total é aproximadamente 3,07% e 3,17% ao ano, respectivamente. Isso é consistente com melhor seleção de exposição na história, mas não identifica um mecanismo causal.

### Como ler o slide

Compare as barras de cada componente. A remuneração de juros cai na combinação, enquanto a contribuição de câmbio sobe. Diga que os componentes mostrados não somam o retorno composto da tabela anterior. Para ilustrar custo de oportunidade, em 2019 o excesso médio anualizado da combinação foi 0,40%, contra 3,83% do carry. Em 2020–2021, foi 2,39% contra −1,43%.

### Treinamento, previsão e avaliação

Mesmas previsões, regras e treinamento expansivo da combinação. Atribuição realizada no backtest de abr/2018 a ago/2026. Não há um novo modelo de previsão para a atribuição.

### Fala sugerida

A decomposição contábil ajuda a entender o resultado. A combinação recebeu menos contribuição de juros, o que faz sentido porque operou com menor exposição. Em compensação, teve contribuição cambial maior na amostra. Isso manteve o excesso médio de retorno próximo ao do carry, com menos risco. Mas ficar de fora também tem custo: em 2019, a combinação ganhou pouco acima do caixa e ficou bastante atrás do carry. Em 2020 e 2021, ocorreu o contrário. Portanto, os filtros podem proteger em alguns episódios e deixar ganhos para trás em outros. Essa alternância é parte do resultado, não uma exceção a esconder.

### Cuidado com a interpretação

Não some 1,82% e 1,50% para chegar ao CAGR de 5,94%. A tabela de CAGR inclui caixa e composição. A atribuição usa médias aritméticas do excesso e ainda desconta outras parcelas.

### Pergunta provável

O resultado vem só do carrego? Não. As duas estratégias recebem juros e carregam risco cambial. A combinação mudou a exposição a essas duas fontes de resultado.

### Transição

Os resultados são interessantes, mas há limites claros para a interpretação.

Fontes: synthesis/tables/attribution.csv; synthesis/tables/episodes.csv

## Slide 16 — O resultado ainda exige validação

Tempo: 60 segundos.

Há uma melhora histórica de risco, mas a pesquisa ainda não estabelece uma vantagem generalizável de retorno.

### Conceitos que você precisa dominar

Vazamento temporal ocorre quando a decisão usa informação que só seria conhecida depois. O projeto controla defasagens, maturação dos alvos e atraso de execução. Seleção de modelos é outro problema: depois de testar muitas ideias, as que parecem melhores podem ser apenas as que tiveram sorte nessa história. Um backtest pode respeitar o calendário e ainda sofrer com seleção retrospectiva. Além disso, os dados macroeconômicos disponíveis foram revisados e as taxas são proxies, não cotações executáveis. A dependência de países também limita a generalização.

### Como ler o slide

Explique quatro limites em linguagem simples: mesma história explorada, exposição menor, concentração por país e dados sem todas as versões históricas. A atribuição de BRL e JPY representa cerca de 86% da contribuição por moeda antes de custos de negociação. Na sensibilidade sem BRL, o excesso da combinação cai de 3,17% para aproximadamente 0,65% ao ano. O teste corrigido para a grade principal não estabelece ganho de retorno médio sobre carry.

### Fala sugerida

A principal limitação é que os módulos foram escolhidos após explorar essa mesma história. Eu cuidei para que as decisões mensais não usassem o futuro, mas isso não transforma o resultado em uma validação independente da escolha das regras. O desempenho também depende bastante do Brasil e do iene, e a menor exposição explica parte da queda de risco. Os testes corrigidos para as alternativas principais não sustentam ganho de retorno médio sobre o carry. Finalmente, taxas oficiais e séries revisadas são aproximações da informação e dos preços disponíveis para um investidor. Por isso, a próxima validação teria de congelar as regras e acompanhar dados futuros e custos executáveis.

### Cuidado com a interpretação

Evite ‘não houve nenhum vazamento’ como certificação absoluta. Diga quais controles existem e quais limitações permanecem.

### Pergunta provável

Então o trabalho não tem valor? Tem. Reproduz a relação da aula, mostra onde extensões preditivas falham e documenta uma hipótese de controle de risco com resultados e limites transparentes.

### Transição

Com esses limites, a conclusão fica mais simples e mais defensável.

Fontes: synthesis/tables/search_adjustment.csv; synthesis/tables/robustness.csv; synthesis/PROTOCOL.md; AUDITORIA.md

## Slide 17 — O que o trabalho permite concluir

Tempo: 35 segundos.

A relação econômica se replica, a extensão preditiva é instável e o uso mais promissor apareceu no controle da exposição ao carry.

### Conceitos que você precisa dominar

A conclusão deve separar o que foi reproduzido do que ficou como hipótese. Primeiro, a relação histórica brasileira apresentada na aula foi recuperada. Segundo, acrescentar commodities melhora uma comparação nominal, mas não de forma estável, e prever a mudança real continua difícil. Terceiro, somar a previsão ao ranking falhou, enquanto regras de exposição apresentaram risco histórico menor. Nenhuma dessas etapas prova arbitragem, ganho causal de uma variável ou alfa persistente.

### Como ler o slide

Este é o fechamento. Não abra novos resultados e não leia uma lista de números. Reforce uma frase final: informação macroeconômica pode ser útil para decidir a exposição, mas o valor econômico precisa ser testado separadamente da qualidade da regressão.

### Fala sugerida

O trabalho deixa três aprendizados. A relação histórica da aula aparece na replicação. Commodities acrescentam informação em alguns testes, mas a capacidade preditiva depende da amostra. E a primeira tentativa de carteira falhou, enquanto o uso da informação para controlar a exposição produziu resultados históricos de risco mais favoráveis. A hipótese que merece continuidade é essa utilidade para a gestão da posição. Para transformá-la em uma conclusão de mercado, seria necessário validar regras congeladas em dados futuros.

### Cuidado com a interpretação

Encerre no slide 17. Os slides 18 e 19 são apoio para perguntas e ficam fora dos 19 minutos.

### Pergunta provável

Qual é a contribuição em uma frase? Separar uma regularidade cambial replicável de seu valor preditivo e mostrar que o controle de exposição é uma hipótese econômica mais promissora que o ranking direto nesta amostra.

### Transição

Obrigado. Posso detalhar a metodologia ou os resultados nas perguntas.

Fontes: Relatórios original, terciário, termos de troca e síntese

## Slide 18 — Apoio: equações e informação disponível

Tempo: 0 segundos.

A regressão nominal usa o desvio real e, na extensão, informações de preços comerciais disponíveis na origem.

### Conceitos que você precisa dominar

No EJR implementado, Δs(t,t+h) = β_h × [q_t − média histórica de q] + erro, com coeficiente agrupado e sem intercepto adicional. A média é calculada com dados disponíveis na origem. A extensão adiciona níveis centrados do componente global de preços reais de commodities e da exposição específica do país. Cada regressão em t só usa alvos j+h que terminaram até t−1. A observação atual do CPI entra com dois meses de atraso. Pesos fixos comerciais do exercício nominal usam 1994–1996. A previsão mensal usada no sinal de carry é a previsão de Δs em 60 meses dividida por 60, uma aproximação de ritmo médio, não uma trajetória estimada.

### Como ler o slide

Use somente se houver pergunta técnica. Explique cada letra antes de interpretar o coeficiente. Na extensão, β, γ e δ são estimados em conjunto, sem impor que o coeficiente EJR original permaneça fixo.

### Treinamento, previsão e avaliação

Janela de treinamento começa em out/1999 no EJR nominal. Para horizonte h, uma origem j só entra se j+h ≤ t−1. Mínimo 60 origens maduras por moeda. CPI e preços defasados. As janelas de avaliação variam por horizonte.

### Fala sugerida

Esta é a forma simplificada das regressões. A variável prevista é a mudança futura do log da cotação. A base usa o desvio do câmbio real. A extensão mantém esse regressor e adiciona informação global e específica de commodities. O cuidado temporal principal é que um alvo só entra no treinamento depois de terminar. Não treino uma previsão de cinco anos com resultados que ainda não poderiam ser conhecidos.

### Cuidado com a interpretação

A equação simplificada do slide omite índices de país para legibilidade. O exercício de dispersão da aula tem ajuste dentro da amostra e intercepto, diferentemente da previsão agrupada.

### Pergunta provável

Há identificação causal? Não. Há uma avaliação preditiva condicional. Não usamos uma fonte exógena de variação para identificar um efeito causal de commodities.

### Transição

O segundo apoio detalha a comparação econômica e o calendário de negociação.

Fontes: src/models.py; third/engine.py; synthesis/model.py

## Slide 19 — Apoio: exposição, custos e interpretação

Tempo: 0 segundos.

Comparações econômicas precisam manter datas, numerário e custos consistentes, além de distinguir controle retrospectivo de estratégia executável.

### Conceitos que você precisa dominar

No controle retrospectivo, o carry é escalado pela exposição média realizada da combinação, conhecida ao final. Serve para investigar quanto da melhora decorre de menor tamanho, não como regra que poderia ser escolhida antecipadamente. O controle estimado apenas com história passada tem outra exposição média e não iguala ex post o risco. O backtest calcula o ativo local em dólar como (1+i_local) × S_anterior/S_atual − 1. Soma o caixa USD e o resultado das posições, descontando financiamento adicional e negociação. Custos por notional: 10 pontos-base para BRL, 3 para SEK e 2 para as demais moedas, além de 50 pontos-base anuais de spread na ponta vendida. Um ponto-base é 0,01 ponto percentual.

### Como ler o slide

A tabela compara, em 2018–2026, carry a 100%, carry reduzido retrospectivamente a 48% e combinação. O calendário é sinal no fechamento de t, execução no fechamento de t+1 e primeiro retorno em t+2. As taxas curtas são proxies, não contratos a termo efetivamente negociados.

### Treinamento, previsão e avaliação

Treino mensal expansivo da combinação, com primeiro sinal em fev/2018. Backtest comum: abr/2018–ago/2026. A exposição média do controle retrospectivo só é conhecida ao final.

### Fala sugerida

O controle com o mesmo tamanho médio ajuda a separar exposição e seleção. Ele tem volatilidade até um pouco menor que a combinação, mas retorno menor e drawdown maior na história. Como usa a exposição média conhecida ao final, eu o trato como diagnóstico. Os retornos da simulação incluem juros, variação cambial e os custos definidos, sempre em dólar. Para execução real ainda faltariam cotações negociáveis, vintages históricas e outras fricções específicas do investidor.

### Cuidado com a interpretação

Drawdown é uma estatística da trajetória observada, não um limite de perda futura. Custos assumidos não são custos garantidos para qualquer investidor.

### Pergunta provável

Por que não é arbitragem? Porque há risco de perda, incerteza de convergência e custos de financiamento. Nenhum resultado positivo é garantido.

### Transição

Esses detalhes sustentam a leitura cautelosa dos resultados principais.

Fontes: synthesis/tables/exposure_controls.csv; src/models.py: run_book; synthesis/model.py
