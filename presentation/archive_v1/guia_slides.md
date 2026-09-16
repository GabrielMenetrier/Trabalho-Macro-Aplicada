# Guia de apresentação: câmbio real, commodities e carry

15 slides principais, 18 minutos previstos, 2 slides de apoio.

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

Tempo: 75 segundos.

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

### Fala sugerida

Neste gráfico, cada ponto é um mês brasileiro. À direita estão momentos de maior depreciação real. Para baixo estão apreciações nominais nos oito anos seguintes. A relação é claramente negativa, e a inclinação de menos 1,808 praticamente reproduz o número da aula. O R² é alto, cerca de 88%. Mas esse resultado descreve o ajuste da relação na amostra histórica. Não significa que o modelo acerta 88% das operações. Além disso, previsões feitas em dois meses vizinhos usam quase os mesmos oito anos seguintes, então os pontos não são evidências independentes. A próxima etapa é perguntar se essa relação ajuda quando eu realmente escondo o futuro do modelo.

### Cuidado com a interpretação

Este gráfico usa ajuste dentro da amostra. Não o apresente como uma previsão produzida em tempo real ou como replicação integral do artigo.

### Pergunta provável

Por que o coeficiente é menor que −1? A regressão permite esse valor no horizonte longo. Isso não significa retorno mensal de 180% ou convergência garantida. É uma relação entre mudanças e desvios em log.

### Transição

Reproduzir a relação histórica e prever dados futuros são testes diferentes.

Fontes: output/tables/classroom_replication.csv; data/processed/classroom.csv; Macro_Aplicada_2026_shared/Slides/Macro_Aplicada_aula_8.pdf

## Slide 04 — O teste fora da amostra é mais exigente

Tempo: 75 segundos.

No painel de seis moedas, a previsão EJR de cinco anos não superou a previsão de nenhuma mudança nominal.

### Conceitos que você precisa dominar

Fora da amostra significa estimar com informação admissível até a data da previsão e avaliar depois. O benchmark de nenhuma mudança prevê que a cotação futura será igual à atual. É o passeio aleatório sem drift para a previsão de nível. O erro usado é a raiz da média dos erros ao quadrado, RMSE. Dividir o erro do modelo pelo erro do benchmark permite uma leitura simples: abaixo de 1 melhora, acima de 1 piora. O resultado 1,037 corresponde a um erro aproximadamente 3,7% maior. A previsão é para cinco anos à frente, não para o próximo mês.

### Como ler o slide

Mostre que o benchmark tem erro relativo 1 por definição e que EJR está ligeiramente acima. São BRL, EUR, JPY, GBP, CAD e SEK, sempre em relação ao dólar. As 140 datas de previsão vão de janeiro de 2010 a agosto de 2021, porque os últimos resultados de cinco anos terminam em agosto de 2026.

### Fala sugerida

Agora o modelo usa apenas a história admissível em cada data. Para avaliar uma previsão de cinco anos, também preciso esperar o alvo terminar antes de usá-lo no treinamento. A comparação é com uma regra muito simples: a cotação daqui a cinco anos será igual à de hoje. O erro dessa regra vale um na tabela. O erro do modelo EJR é 1,037, um pouco maior. Isso não contradiz mecanicamente o gráfico anterior: mudaram a pergunta, o horizonte e o universo, que agora reúne seis moedas. A conclusão é mais limitada: nesta implementação, a relação histórica forte não virou uma melhora agregada de previsão.

### Cuidado com a interpretação

Chamamos de pseudo fora da amostra: há defasagens e controles de calendário, mas as bases disponíveis contêm revisões históricas. Não prometa dados integralmente point-in-time.

### Pergunta provável

Por que 840 observações não garantem precisão? São seis moedas em 140 datas com alvos sobrepostos de 60 meses. Há dependência entre datas e entre países.

### Transição

Mesmo assim, uma previsão imperfeita pode ter valor econômico. Foi isso que eu testei com carry.

Fontes: output/tables/forecast_accuracy.csv; AUDITORIA.md; src/models.py

## Slide 05 — A proposta inicial para o carry

Tempo: 80 segundos.

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

Tempo: 75 segundos.

O carry com previsão rendeu menos e teve Sharpe menor, apesar de alguma redução do drawdown.

### Conceitos que você precisa dominar

Retorno anual composto, ou CAGR, transforma o crescimento acumulado em uma taxa anual constante equivalente. Volatilidade mede a dispersão dos retornos mensais, anualizada. Sharpe divide o retorno médio em excesso do caixa pelo risco desses excessos. Queda máxima, ou drawdown máximo, é a maior perda do patrimônio em relação ao pico anterior. Uma carteira pode ter drawdown menor e ainda ser uma pior troca entre remuneração e risco. As carteiras desta tabela usam a mesma janela e custos compatíveis.

### Como ler o slide

Priorize apenas duas linhas: retorno anual de 4,11% contra 2,73% e Sharpe de 0,60 contra 0,31. As demais ajudam se houver pergunta. A tabela cobre março de 2010 a agosto de 2026, com 198 retornos mensais líquidos em dólar. Esses números não devem ser comparados diretamente aos resultados de 2018–2026 sem ajustar a janela.

### Fala sugerida

O resultado da primeira proposta foi negativo. O carry por juros rendeu 4,11% ao ano, enquanto o ranking que acrescentou a previsão rendeu 2,73%. O Sharpe caiu de 0,60 para 0,31. Houve alguma redução da queda máxima, mas acompanhada de uma perda grande de remuneração. Portanto, esta implementação não sustenta a ideia de que basta somar a previsão cambial ao diferencial de juros para melhorar a carteira. Isso me levou a duas perguntas: a referência do câmbio real pode mudar com o comércio? E a informação pode ajudar a decidir quanto risco assumir, mesmo sem melhorar o ranking dos países?

### Cuidado com a interpretação

O fracasso é da regra específica testada. Não prova que toda previsão cambial seja inútil ou que o artigo esteja errado.

### Pergunta provável

Se houve menos queda, por que chamar de fracasso? A proposta era melhorar a relação econômica de retorno e risco. A redução modesta do risco veio com retorno e Sharpe substancialmente menores.

### Transição

Antes de testar novas carteiras, eu voltei à pergunta de previsão.

Fontes: output/tables/portfolio_metrics.csv

## Slide 07 — Commodities e condições de troca

Tempo: 70 segundos.

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

## Slide 08 — Commodities melhoram uma previsão, com fragilidade

Tempo: 85 segundos.

A extensão nominal reduz o erro na janela completa, mas perde para nenhuma mudança nas origens mais recentes.

### Conceitos que você precisa dominar

A extensão mantém a lógica da regressão EJR: prever a mudança do log da cotação em 60 meses a partir do desvio real. Acrescenta um componente global de preços reais de commodities e um componente específico da exposição comercial de cada país. Os pesos desse exercício usam 1994–1996, antes da avaliação, e os preços entram defasados. Energia, alimentos, matérias-primas e metais compõem os grupos. O modelo ampliado continua sendo uma regressão preditiva. Não atribui causalmente a cada commodity uma valorização da moeda.

### Como ler o slide

Cada coluna normaliza o erro da previsão de nenhuma mudança para 1. Na janela completa, EJR tem 1,037 e EJR com commodities tem 0,890: queda de aproximadamente 11% frente ao benchmark e 14% frente ao EJR. Nas origens de 2019 a agosto de 2021, a extensão tem erro 1,630: melhora relativamente ao EJR, mas perde para nenhuma mudança. As colunas contêm 140 e 32 origens mensais, respectivamente, com alvos de cinco anos sobrepostos.

### Fala sugerida

Esta é a extensão mais próxima do exercício original. O alvo continua sendo a mudança do câmbio nominal em cinco anos. Eu mantenho o desvio real e adiciono preços de commodities, separando o componente global da exposição específica do país. Na janela completa, o erro cai para 0,890, abaixo de um. Isso é um resultado preditivo interessante. Mas a conclusão muda no recorte recente: o erro sobe para 1,630. A extensão ainda melhora sobre o EJR, porém já perde para a previsão de nenhuma mudança. A vantagem sobre o benchmark também desaparece na sensibilidade sem o real brasileiro. Portanto, há informação potencial, mas ela depende bastante da amostra e do país.

### Cuidado com a interpretação

‘Reduziu o erro’ precisa sempre nomear o benchmark e a janela. Não use a melhora sobre um modelo fraco como prova de previsibilidade robusta.

### Pergunta provável

Por que o ganho desaparece sem BRL? O resultado é heterogêneo e o Brasil contribui bastante para a melhora agregada. Isso pede validação externa, não escolha retrospectiva de países vencedores.

### Transição

Também testei uma pergunta diferente: prever o próprio câmbio real de longo prazo.

Fontes: third/tables/metrics.csv: B_FX_60, REJR_Specific, benchmark EJR; third/tables/sensitivity.csv; third/engine.py: ejr_extension

## Slide 09 — Prever o câmbio real continuou difícil

Tempo: 70 segundos.

A informação comercial melhora um pouco a regressão de câmbio real, mas não supera a previsão de nenhuma mudança.

### Conceitos que você precisa dominar

Agora o alvo muda: antes era a cotação nominal, agora é q daqui a cinco anos menos q hoje. A regressão base contém nível real centrado e sua mudança passada. A extensão adiciona o índice de preços comerciais com pesos que se atualizam usando informações históricas defasadas, além da variação passada desse índice. Para comparar modelos, a base é reestimada nas mesmas observações disponíveis para a extensão. Esse cuidado evita atribuir às novas variáveis uma melhora causada apenas por mudança de amostra.

### Como ler o slide

A previsão de nenhuma mudança real tem erro relativo 1. A base tem 2,20 e a extensão com preços e pesos comerciais tem 2,08. São 104 origens de janeiro de 2013 a agosto de 2021. A redução em relação à regressão base é aproximadamente 5%, mas o erro continua mais que o dobro do benchmark simples. Não compare esses níveis de erro diretamente aos do slide anterior: o alvo e a amostra são diferentes.

### Fala sugerida

Aqui eu mudo a pergunta. Em vez de prever o câmbio nominal, tento prever a mudança do câmbio real em cinco anos. A informação comercial reduz o erro da regressão base de 2,20 para 2,08. É uma pequena melhora relativa, mas ambos os modelos perdem bastante para nenhuma mudança, que vale um. Os testes com termos de troca agregados anuais também não estabeleceram uma solução robusta e têm uma amostra ainda menor. Assim, não consigo defender que aprendi a prever de forma confiável uma nova referência real de longo prazo. Esse resultado negativo ajuda a limitar o que posso dizer sobre os fundamentos.

### Cuidado com a interpretação

O número 2,08 é razão de erro, não previsão de depreciação de 208%. A proxy comercial mensal e os termos de troca agregados anuais são testes distintos.

### Pergunta provável

E a hipótese de mudança no equilíbrio? Continua economicamente plausível, mas estes resultados preditivos não a estabelecem nem identificam um novo valor de equilíbrio.

### Transição

Com previsões frágeis, eu passei a testar decisões de exposição mais específicas.

Fontes: trade_extension/tables/prediction_metrics.csv: real_60; trade_extension/analyze.py

## Slide 10 — A informação passa a controlar a posição

Tempo: 110 segundos.

A combinação posterior mantém a lógica de carry e usa sinais para dimensionar, permitir ou encerrar posições.

### Conceitos que você precisa dominar

O módulo A reduz o tamanho do carry quando o retorno previsto é baixo em relação à referência passada e elimina pares com mudança comercial observada muito alta. O módulo B só entra se o retorno previsto anualizado, suavizado por seis meses, superar 2%, e evita pares com movimento adverso forte dos preços comerciais. O módulo C distribui entradas mensais em parcelas, cada uma com duração máxima de 12 meses, e antecipa a saída quando o modelo com composição comercial indica aumento relevante do risco de o câmbio consumir os juros, relativamente ao modelo base. Os limites de eventos extremos usam o percentil 80 da história passada. A combinação usa um terço dos pesos de cada módulo e calcula custos após agregar as posições.

### Como ler o slide

Explique cada linha como uma decisão concreta: quanto comprar, quando entrar, quando sair. Dê mais tempo ao terceiro módulo. Uma ‘coorte’ é simplesmente o lote de posições aberto em um mês. Cada lote tem orçamento limitado, em vez de multiplicar a exposição ao somar vários meses. Os pares retirados saem com as duas pontas, preservando a neutralidade líquida.

### Fala sugerida

A mudança foi usar a informação para controlar o carry. O primeiro módulo decide quanto investir: reduz a posição quando a remuneração prevista está fraca e evita mudanças comerciais extremas. O segundo decide quando entrar: exige uma remuneração prevista mínima e evita movimentos comerciais adversos. O terceiro decide quando sair: abre pequenas parcelas ao longo dos meses, com prazo máximo de um ano, e encerra antes quando a informação comercial indica risco adicional relevante de o câmbio consumir os juros. Esse risco adicional compara o modelo com comércio ao modelo base, respeitando a direção original da posição. Eu combino os três com pesos iguais. Essas regras já são mais complexas e foram escolhidas depois de explorar a história, então os resultados seguintes precisam ser tratados como exploratórios.

### Cuidado com a interpretação

O sinal de risco adicional é uma diferença entre modelos, não simplesmente a mudança mensal de uma probabilidade. Não chame a combinação de modelo ótimo ou escolhido em uma amostra totalmente intocada.

### Pergunta provável

Por que pesos iguais? É uma combinação simples, que evita otimizar os pesos para o maior Sharpe. Ainda assim, a escolha dos componentes já usa aprendizados da história examinada.

### Transição

Para comparar, eu coloco o carry e a combinação exatamente nas mesmas datas.

Fontes: synthesis/model.py: make_policies; synthesis/PROTOCOL.md; synthesis/EXPLORATION.md

## Slide 11 — A combinação teve risco menor na janela comum

Tempo: 80 segundos.

Entre abril de 2018 e agosto de 2026, a combinação apresentou retorno semelhante ao carry com menor volatilidade e menor exposição.

### Conceitos que você precisa dominar

A janela comum começa quando todos os módulos já podem funcionar. Tem 101 retornos mensais. O retorno total inclui remuneração do caixa em dólar, contribuições dos ativos e financiamento, além de custos assumidos. O Sharpe usa excesso sobre o caixa. Exposição bruta é a soma do valor absoluto das posições dividida pelo patrimônio. A combinação teve exposição bruta média de 48%, contra 100% do carry. Isso explica parte da queda de risco e deve aparecer ao lado das métricas, não como ressalva escondida.

### Como ler o slide

Leia primeiro retorno anual de 5,78% e 5,94%: são próximos. Depois destaque volatilidade de 4,11% e 2,33%, e queda máxima de 9,09% e 1,43% em magnitude. Termine obrigatoriamente na exposição de 100% e 48%. O Sharpe sobe de 0,75 para 1,37. Os sinais negativos na linha de queda máxima representam perdas em relação ao pico.

### Fala sugerida

Na janela comum, o retorno anual ficou próximo: 5,78% no carry e 5,94% na combinação. A diferença mais visível aparece no risco: a volatilidade caiu de 4,11% para 2,33% e a queda máxima observada caiu de 9,09% para 1,43%. O Sharpe aumentou. Mas existe uma explicação importante: a combinação carregou, em média, apenas 48% de exposição bruta. Parte do resultado vem simplesmente de assumir menos risco e permanecer mais em caixa. Eu fiz controles de exposição, mas eles não eliminam toda a incerteza sobre a vantagem. O que posso mostrar é uma trajetória histórica mais estável, sem afirmar uma rentabilidade superior garantida.

### Cuidado com a interpretação

A diferença de retorno de 0,16 ponto percentual de CAGR é pequena. Não apresente o Sharpe observado como prova estatística de alfa.

### Pergunta provável

Bastava investir metade no carry? O controle retrospectivo com exposição média de 48% rendeu 4,18% ao ano e teve queda máxima de 4,02%, contra 5,94% e 1,43% da combinação. Isso é diagnóstico útil, mas usa a média conhecida depois e não prova superioridade futura.

### Transição

A trajetória do patrimônio ajuda a visualizar essa diferença de risco.

Fontes: synthesis/tables/metrics.csv: common, all; synthesis/tables/exposure_controls.csv

## Slide 12 — A trajetória explica o resultado de risco

Tempo: 65 segundos.

O patrimônio final é parecido, mas o carry apresenta perdas e recuperações mais pronunciadas.

### Conceitos que você precisa dominar

O gráfico acumula retornos mensais líquidos. Cada estratégia começa com patrimônio 100 imediatamente antes do primeiro retorno da janela. Um nível 160 significa crescimento acumulado de aproximadamente 60%, não retorno anual de 60%. A linha de caixa é a referência em dólar. A linha inferior mede a perda percentual desde o maior patrimônio já alcançado. Ela volta a zero quando a estratégia recupera ou supera o pico anterior. A amostra começa com a formação gradual das parcelas do módulo de permanência.

### Como ler o slide

Aponte a trajetória, sem tentar explicar cada oscilação. A queda do carry em torno de 2020 é mais visível que a da combinação. O painel de perdas mostra a profundidade em relação ao pico. Como o retorno final é semelhante, este slide reforça que o achado principal é a suavização histórica do caminho.

### Fala sugerida

Aqui todas as estratégias começam em 100. O ponto final do carry e da combinação é próximo, mas o caminho é diferente. O carry atravessa uma queda mais pronunciada em torno de 2020, enquanto a combinação mantém uma trajetória mais estável nessa janela. O painel de baixo mostra a perda em relação ao pico anterior. A linha do caixa lembra que parte do retorno total vem da remuneração em dólar, mesmo quando a exposição cai. Esta figura ajuda a entender por que duas carteiras com retorno final parecido podem ter riscos bastante diferentes.

### Cuidado com a interpretação

O gráfico descreve o que ocorreu. Ele não identifica que um filtro específico causou cada diferença durante uma crise.

### Pergunta provável

Por que começar em 100? É uma normalização para comparar trajetórias. Multiplicar o patrimônio inicial não muda as taxas de retorno.

### Transição

Também vale separar contabilmente o que veio dos juros e o que veio do câmbio.

Fontes: synthesis/tables/returns.csv.gz: common; synthesis/tables/metrics.csv

## Slide 13 — Menos juros, contribuição cambial melhor

Tempo: 70 segundos.

Na combinação, a menor exposição reduziu o recebimento de juros, enquanto a contribuição cambial histórica melhorou.

### Conceitos que você precisa dominar

A atribuição divide a média mensal do retorno em excesso em parcelas contábeis e multiplica por 12. Os valores são pontos percentuais de contribuição anual, não CAGRs separáveis. Carry: câmbio 0,74 p.p. e juros 2,62 p.p. Combinação: câmbio 1,82 p.p. e juros 1,50 p.p. Interação, spread de financiamento e custos completam a conta. O excesso médio total é aproximadamente 3,07% e 3,17% ao ano, respectivamente. Isso é consistente com melhor seleção de exposição na história, mas não identifica um mecanismo causal.

### Como ler o slide

Compare as barras de cada componente. A remuneração de juros cai na combinação, enquanto a contribuição de câmbio sobe. Diga que os componentes mostrados não somam o retorno composto da tabela anterior. Para ilustrar custo de oportunidade, em 2019 o excesso médio anualizado da combinação foi 0,40%, contra 3,83% do carry. Em 2020–2021, foi 2,39% contra −1,43%.

### Fala sugerida

A decomposição contábil ajuda a entender o resultado. A combinação recebeu menos contribuição de juros, o que faz sentido porque operou com menor exposição. Em compensação, teve contribuição cambial maior na amostra. Isso manteve o excesso médio de retorno próximo ao do carry, com menos risco. Mas ficar de fora também tem custo: em 2019, a combinação ganhou pouco acima do caixa e ficou bastante atrás do carry. Em 2020 e 2021, ocorreu o contrário. Portanto, os filtros podem proteger em alguns episódios e deixar ganhos para trás em outros. Essa alternância é parte do resultado, não uma exceção a esconder.

### Cuidado com a interpretação

Não some 1,82% e 1,50% para chegar ao CAGR de 5,94%. A tabela de CAGR inclui caixa e composição. A atribuição usa médias aritméticas do excesso e ainda desconta outras parcelas.

### Pergunta provável

O resultado vem só do carrego? Não. As duas estratégias recebem juros e carregam risco cambial. A combinação mudou a exposição a essas duas fontes de resultado.

### Transição

Os resultados são interessantes, mas há limites claros para a interpretação.

Fontes: synthesis/tables/attribution.csv; synthesis/tables/episodes.csv

## Slide 14 — O resultado ainda exige validação

Tempo: 75 segundos.

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

## Slide 15 — O que o trabalho permite concluir

Tempo: 45 segundos.

A relação econômica se replica, a extensão preditiva é instável e o uso mais promissor apareceu no controle da exposição ao carry.

### Conceitos que você precisa dominar

A conclusão deve separar o que foi reproduzido do que ficou como hipótese. Primeiro, a relação histórica brasileira apresentada na aula foi recuperada. Segundo, acrescentar commodities melhora uma comparação nominal, mas não de forma estável, e prever a mudança real continua difícil. Terceiro, somar a previsão ao ranking falhou, enquanto regras de exposição apresentaram risco histórico menor. Nenhuma dessas etapas prova arbitragem, ganho causal de uma variável ou alfa persistente.

### Como ler o slide

Este é o fechamento. Não abra novos resultados e não leia uma lista de números. Reforce uma frase final: informação macroeconômica pode ser útil para decidir a exposição, mas o valor econômico precisa ser testado separadamente da qualidade da regressão.

### Fala sugerida

O trabalho deixa três aprendizados. A relação histórica da aula aparece na replicação. Commodities acrescentam informação em alguns testes, mas a capacidade preditiva depende da amostra. E a primeira tentativa de carteira falhou, enquanto o uso da informação para controlar a exposição produziu resultados históricos de risco mais favoráveis. A hipótese que merece continuidade é essa utilidade para a gestão da posição. Para transformá-la em uma conclusão de mercado, seria necessário validar regras congeladas em dados futuros.

### Cuidado com a interpretação

Encerre aqui. Os dois slides seguintes são apenas apoio para perguntas e não fazem parte dos 20 minutos.

### Pergunta provável

Qual é a contribuição em uma frase? Separar uma regularidade cambial replicável de seu valor preditivo e mostrar que o controle de exposição é uma hipótese econômica mais promissora que o ranking direto nesta amostra.

### Transição

Obrigado. Posso detalhar a metodologia ou os resultados nas perguntas.

Fontes: Relatórios original, terciário, termos de troca e síntese

## Slide 16 — Apoio: equações e informação disponível

Tempo: 0 segundos.

A regressão nominal usa o desvio real e, na extensão, informações de preços comerciais disponíveis na origem.

### Conceitos que você precisa dominar

No EJR implementado, Δs(t,t+h) = β_h × [q_t − média histórica de q] + erro, com coeficiente agrupado e sem intercepto adicional. A média é calculada com dados disponíveis na origem. A extensão adiciona níveis centrados do componente global de preços reais de commodities e da exposição específica do país. Cada regressão em t só usa alvos j+h que terminaram até t−1. A observação atual do CPI entra com dois meses de atraso. Pesos fixos comerciais do exercício nominal usam 1994–1996. A previsão mensal usada no sinal de carry é a previsão de Δs em 60 meses dividida por 60, uma aproximação de ritmo médio, não uma trajetória estimada.

### Como ler o slide

Use somente se houver pergunta técnica. Explique cada letra antes de interpretar o coeficiente. Na extensão, β, γ e δ são estimados em conjunto, sem impor que o coeficiente EJR original permaneça fixo.

### Fala sugerida

Esta é a forma simplificada das regressões. A variável prevista é a mudança futura do log da cotação. A base usa o desvio do câmbio real. A extensão mantém esse regressor e adiciona informação global e específica de commodities. O cuidado temporal principal é que um alvo só entra no treinamento depois de terminar. Não treino uma previsão de cinco anos com resultados que ainda não poderiam ser conhecidos.

### Cuidado com a interpretação

A equação simplificada do slide omite índices de país para legibilidade. O exercício de dispersão da aula tem ajuste dentro da amostra e intercepto, diferentemente da previsão agrupada.

### Pergunta provável

Há identificação causal? Não. Há uma avaliação preditiva condicional. Não usamos uma fonte exógena de variação para identificar um efeito causal de commodities.

### Transição

O segundo apoio detalha a comparação econômica e o calendário de negociação.

Fontes: src/models.py; third/engine.py; synthesis/model.py

## Slide 17 — Apoio: exposição, custos e interpretação

Tempo: 0 segundos.

Comparações econômicas precisam manter datas, numerário e custos consistentes, além de distinguir controle retrospectivo de estratégia executável.

### Conceitos que você precisa dominar

No controle retrospectivo, o carry é escalado pela exposição média realizada da combinação, conhecida ao final. Serve para investigar quanto da melhora decorre de menor tamanho, não como regra que poderia ser escolhida antecipadamente. O controle estimado apenas com história passada tem outra exposição média e não iguala ex post o risco. O backtest calcula o ativo local em dólar como (1+i_local) × S_anterior/S_atual − 1. Soma o caixa USD e o resultado das posições, descontando financiamento adicional e negociação. Custos por notional: 10 pontos-base para BRL, 3 para SEK e 2 para as demais moedas, além de 50 pontos-base anuais de spread na ponta vendida. Um ponto-base é 0,01 ponto percentual.

### Como ler o slide

A tabela compara, em 2018–2026, carry a 100%, carry reduzido retrospectivamente a 48% e combinação. O calendário é sinal no fechamento de t, execução no fechamento de t+1 e primeiro retorno em t+2. As taxas curtas são proxies, não contratos a termo efetivamente negociados.

### Fala sugerida

O controle com o mesmo tamanho médio ajuda a separar exposição e seleção. Ele tem volatilidade até um pouco menor que a combinação, mas retorno menor e drawdown maior na história. Como usa a exposição média conhecida ao final, eu o trato como diagnóstico. Os retornos da simulação incluem juros, variação cambial e os custos definidos, sempre em dólar. Para execução real ainda faltariam cotações negociáveis, vintages históricas e outras fricções específicas do investidor.

### Cuidado com a interpretação

Drawdown é uma estatística da trajetória observada, não um limite de perda futura. Custos assumidos não são custos garantidos para qualquer investidor.

### Pergunta provável

Por que não é arbitragem? Porque há risco de perda, incerteza de convergência e custos de financiamento. Nenhum resultado positivo é garantido.

### Transição

Esses detalhes sustentam a leitura cautelosa dos resultados principais.

Fontes: synthesis/tables/exposure_controls.csv; src/models.py: run_book; synthesis/model.py
