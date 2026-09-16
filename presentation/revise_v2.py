"""Update presentation explanations from existing results, with explicit clocks."""
from pathlib import Path
import json,hashlib
import pandas as pd
R=Path(__file__).resolve().parents[1];H=R/'presentation'
C=json.loads((H/'archive_v1/content.json').read_text(encoding='utf-8'))
D=json.loads((H/'archive_v1/data.json').read_text(encoding='utf-8'))
def read(p):return pd.read_csv(R/p)
def records(a):return json.loads(a.to_json(orient='records'))
extra=['output/tables/portfolio_returns.csv','output/tables/timing_audit.csv','third/tables/sensitivity.csv','trade_extension/tables/audit.csv']
for p in extra:
 if not any(s['path']==p for s in D['sources']):D['sources'].append({'path':p,'sha256':hashlib.sha256((R/p).read_bytes()).hexdigest()})
a=read('output/tables/forecast_accuracy.csv');D['horizons']=records(a[(a.model=='ejr')&a.country.isin(['POOL','BRL'])])
a=read(extra[0]);D['initial_returns']=records(a[a.strategy.isin(['Carry','EJR + carry'])])
a=read('synthesis/tables/robustness.csv');D['tenure']=records(a[a.variant.isin(['Base','Tenure6','Tenure24'])&a.name.isin(['Equal_modules','Cohort_risk'])&(a.period=='all')])
for i,s in enumerate(C['slides'],1):s['old']=i
S={s['old']:s for s in C['slides']}
S[4].update(title='A previsão varia por país e horizonte',
 core='O Brasil melhora em todos os seis horizontes. O painel agrupado perde para nenhuma mudança nas janelas completas de cada horizonte.',
 reading='A tabela compara o erro do modelo EJR agrupado com o erro de prever nenhuma mudança nominal. A coluna Brasil usa a mesma inclinação estimada para as seis moedas, avaliando somente os erros brasileiros. Abaixo de 1 há melhora. Em cinco anos, o Brasil tem 0,792 e o painel tem 1,037. Em oito anos, 0,816 e 1,115. A última coluna informa as datas de origem avaliadas. As janelas mudam porque alvos mais longos exigem mais história de treinamento e só podem ser avaliados quando terminam.',
 speech='O teste fora da amostra não diz que a regressão falha em todo lugar. O Brasil melhora em todos os horizontes mostrados. Em cinco anos, seu erro é cerca de 21% menor que o de prever nenhuma mudança. Mas o resultado agregado das seis moedas é pior que essa referência. Essa heterogeneidade é central. Também não estamos comparando exatamente a regressão brasileira do slide anterior: agora a inclinação é comum às moedas e muda conforme novas observações ficam disponíveis. As janelas da última coluna são diferentes. Quando uso as mesmas datas de origem, o painel melhora em um, dois e três anos. Portanto, a conclusão depende do país, horizonte e período.',
 caution='Não conclua que câmbio é imprevisível em qualquer horizonte. As linhas têm períodos distintos. O ganho de erro não basta, sozinho, para demonstrar significância estatística ou valor de investimento.',
 qa='E se estimarmos só para o Brasil? A regressão brasileira com intercepto e inclinação próprios tem erro relativo 0,596 em oito anos. É outro modelo e um resultado favorável, mas com forte sobreposição dos alvos. No painel com origens comuns de nov/2012 a ago/2018, os erros são 0,958, 0,950 e 0,964 em um, dois e três anos.',
 sources=['output/tables/forecast_accuracy.csv','output/tables/forecast_common_origins.csv','output/tables/timing_audit.csv'])
S[4]['concepts']='Em cada origem t, estimamos a mudança futura do log da cotação a partir do desvio real. A inclinação é comum a seis moedas, e a média histórica de q é específica de cada moeda. A janela de treinamento se expande desde outubro de 1999. Exigimos pelo menos 60 origens de treinamento por moeda cujos alvos já tenham terminado até t−1. O CPI entra com dois meses de defasagem. Repetimos a estimação a cada mês, prevemos e avaliamos o erro quando o horizonte termina. O RMSE relativo compara esse erro com nenhuma mudança. O teste de Clark–West usa correção para dependência temporal. O resultado agregado de cinco anos não estabelece superioridade estatística. Dados revisados limitam o caráter estritamente em tempo real.'
S[6]['concepts']='Não usamos a otimização média-variância de Markowitz. Ordenamos seis moedas por um sinal e compramos as duas de maior sinal, vendendo as duas de menor sinal. Cada ponta recebe 25% do patrimônio em notional: 100% bruto e zero líquido. O carry usa diferencial de juros. O ranking alternativo soma apreciação prevista, aproximada como −previsão de Δs em 60 meses/60. Reavaliamos mensalmente, sem compromisso de manter cada moeda por cinco anos. O caixa em dólar serve de colateral. Retorno anual composto é crescimento do patrimônio, volatilidade é dispersão anualizada, Sharpe usa excesso sobre o caixa e queda máxima mede a perda desde o pico.'
S[6]['reading']='Compare retorno anual de 4,11% e 2,73%, e Sharpe de 0,60 e 0,31. Depois leia o rodapé: backtest de março de 2010 a agosto de 2026, sinal de cinco anos, revisão mensal e treinamento expansivo. Os custos de negociação por notional transacionado são 10 pontos-base para BRL, 3 para SEK e 2 para as outras moedas. Há também spread de financiamento de 50 pontos-base ao ano na ponta vendida. Um ponto-base é 0,01 ponto percentual. Entrada, rebalanceamento e liquidação final pagam os custos assumidos.'
S[6]['speech']='Não montamos uma carteira de Markowitz. As duas estratégias usam um ranking com pesos iguais: duas compras e duas vendas. Na primeira, o ranking olha só os juros. Na segunda, acrescenta a previsão cambial. Ambas recebem juros, carregam risco cambial e pagam os custos indicados no rodapé. O carry rendeu 4,11% ao ano e a alternativa 2,73%, com Sharpe menor. A previsão olha cinco anos à frente, mas a carteira é revista todo mês. Esse prazo de previsão não é o vencimento de uma operação. Escolhemos aplicações curtas para estudar carry e câmbio. Usar bolsa adicionaria retorno e risco acionário e exigiria uma avaliação diferente.'
S[6]['caution']='Não diga Markowitz, otimização de pesos ou posição fixa de cinco anos. Os custos são hipóteses agregadas de negociação e financiamento, não uma lista de tarifas executadas por corretora. Não incluem uma tributação específica do investidor.'
S[6]['qa']='Por que usar juros em vez de bolsa? Para manter a pergunta focada em diferencial de juros e câmbio, sem adicionar prêmio de ações ou risco de duração de títulos longos. Isso é uma escolha adequada ao experimento, não uma demonstração de que juros sejam sempre o melhor ativo.'
S[6]['transition']='O gráfico seguinte mostra como essa diferença se acumulou no patrimônio.'
S[8]['title']='Commodities na previsão feita em cada mês'
S[8]['concepts']='Origem é o mês em que fazemos a previsão. Exemplo: origem em janeiro de 2010 com horizonte de 60 meses tem alvo em janeiro de 2015. A tabela não separa treinos feitos em 2010 e 2019. Ela compara conjuntos de previsões emitidas nessas datas, cada uma com seu treinamento admissível. O modelo mantém o desvio real EJR e acrescenta preços reais de commodities, com componente global e componente de exposição comercial específica. Pesos comerciais fixos usam 1994–1996. Os preços entram defasados dois meses. Estimamos os coeficientes em conjunto, com janela expansiva e sem usar resultados futuros.'
S[8]['reading']='A coluna de 2010–2021 contém 140 origens mensais, de janeiro de 2010 a agosto de 2021, cujos alvos terminam de janeiro de 2015 a agosto de 2026. A coluna de 2019–2021 contém 32 origens, com alvos de janeiro de 2024 a agosto de 2026. Ela é um subconjunto recente, não um teste independente. O erro da referência de nenhuma mudança vale 1 em cada coluna. EJR + commodities tem 0,890 na janela completa e 1,630 na recente. Os alvos de cinco anos se sobrepõem fortemente.'
S[8]['speech']='Origem é a data em que emitimos uma previsão. Se ela nasce em janeiro de 2010 e olha cinco anos à frente, verificamos seu resultado em janeiro de 2015. Aqui, cada previsão usa uma regressão reestimada com a história admissível naquela data. Na coluna completa há 140 previsões mensais por moeda. Na recente, usamos apenas as 32 feitas de 2019 a agosto de 2021. Acrescentar commodities reduz o erro para 0,890 no conjunto completo, mas o erro recente é 1,630, acima da referência. Assim, há uma melhora em parte da história, sem estabilidade no período recente. Essas datas não são o treinamento: são as datas em que as previsões foram feitas.'
S[8]['qa']='Por que paramos as origens em agosto de 2021 se temos dados até 2026? Porque precisamos observar os cinco anos seguintes para avaliar cada previsão. Uma previsão emitida em 2025 ainda não pode ser avaliada em seu horizonte completo de 60 meses.'
S[12]['concepts']='O gráfico acumula retornos líquidos, com patrimônio inicial 100. O retorno final é semelhante, mas as trajetórias de perdas diferem. A carteira recebe novas decisões mensais e não tem uma única janela fixa de treinamento. Em fevereiro de 2018, primeiro sinal para retorno em abril, o EJR usa origens de outubro de 1999 a janeiro de 2013, com alvos terminados até janeiro de 2018. O modelo de risco comercial usa origens de janeiro de 2011 a dezembro de 2016, com resultados disponíveis até janeiro de 2018. Depois as duas janelas se expandem e os modelos são reestimados. A combinação contém também regras baseadas em preços e limiares calculados com a história passada.'
S[12]['qa']='A previsão foi treinada de 2018 a 2026? Não em uma única estimação que olha todo o período. A cada mês, usamos apenas a história admissível, mas a escolha dos módulos usou pesquisa sobre essa história já examinada. Para o primeiro retorno, o sinal vem de fevereiro de 2018 e a execução de março. Em junho de 2026, o EJR já usa origens até maio de 2021 e alvos até maio de 2026.'
training={
3:'Ajuste descritivo: jan/1995–abr/2026. Sem divisão entre treino e teste. Origens de oito anos até abr/2018.',
4:'Treino expansivo desde out/1999; mínimo de 60 origens maduras por moeda. Alvos de treino até t−1. A tabela mostra origens de avaliação, com alvos realizados até ago/2026.',
6:'Primeiro sinal: jan/2010. Treino EJR: origens out/1999–dez/2004 (63 meses por moeda), alvos até dez/2009. A janela se expande mensalmente. Previsão: 60 meses. Sinal t, execução t+1 e retorno t+2. Backtest: mar/2010–ago/2026.',
8:'Primeira origem avaliada: jan/2010. Treino: origens out/1999–dez/2004, alvos até dez/2009. Janela expansiva, mínimo 60 origens maduras por moeda. Previsão nominal de 60 meses. Última origem avaliada: ago/2021, alvo ago/2026.',
9:'Primeira origem avaliada: jan/2013. Treino da extensão e da base pareada: dez/2000–out/2007, com disponibilidade dos alvos até dez/2012. Expansivo, mínimo 60 origens. Alvo de cinco anos, com CPI defasado dois meses. Avaliação: jan/2013–ago/2021, alvos até ago/2026.',
10:'EJR: janela expansiva desde out/1999 e previsão nominal de 60 meses. Risco comercial: origens desde jan/2011, mínimo 36 datas maduras e alvo de 12 meses, mais atraso de execução. Limiares comerciais: mínimo 36 meses anteriores. Backtest comum: abr/2018–ago/2026.',
11:'Primeiro sinal da janela comum: fev/2018. EJR: origens out/1999–jan/2013. Risco comercial: jan/2011–dez/2016. Resultados disponíveis até jan/2018. Reestimação expansiva mensal. Backtest: abr/2018–ago/2026.',
12:'Primeiro sinal: fev/2018. EJR: out/1999–jan/2013, alvos até jan/2018. Risco comercial: jan/2011–dez/2016, alvos disponíveis até jan/2018. Janelas expansivas. Backtest: abr/2018–ago/2026.',
13:'Mesmas previsões, regras e treinamento expansivo da combinação. Atribuição realizada no backtest de abr/2018 a ago/2026. Não há um novo modelo de previsão para a atribuição.',
16:'Janela de treinamento começa em out/1999 no EJR nominal. Para horizonte h, uma origem j só entra se j+h ≤ t−1. Mínimo 60 origens maduras por moeda. CPI e preços defasados. As janelas de avaliação variam por horizonte.',
17:'Treino mensal expansivo da combinação, com primeiro sinal em fev/2018. Backtest comum: abr/2018–ago/2026. A exposição média do controle retrospectivo só é conhecida ao final.'}
for i,t in training.items():S[i]['training']=t
wealth={
 'old':'initial_wealth','title':'O ranking com previsão acumulou menos patrimônio','seconds':50,
 'core':'As duas carteiras incluem juros, câmbio e custos. O ranking com previsão termina abaixo do carry por juros.',
 'concepts':'Patrimônio base 100 é o valor acumulado após reinvestir os retornos mensais líquidos. Um nível de 195 significa ganho total próximo de 95%, e não retorno anual de 95%. A linha de caixa usa a mesma remuneração USD do backtest. Comparar o patrimônio não muda a estratégia: é outra forma de mostrar os resultados da tabela anterior.',
 'reading':'As linhas cobrem março de 2010 a agosto de 2026. Compare os pontos finais e depois o caminho, sem tentar explicar cada oscilação. O gráfico usa os mesmos 198 retornos da tabela do slide 6, com inicialização em 100 antes do primeiro retorno.',
 'speech':'Este é o resultado acumulado das mesmas duas regras. A linha do carry por juros termina acima da linha que acrescenta a previsão cambial. A diferença não vem de excluir os juros de uma delas: ambas incluem juros, câmbio, financiamento e negociação. A linha de caixa permite visualizar quanto seria recebido apenas no colateral em dólar. O gráfico reforça o fracasso da alteração direta do ranking nesta implementação.',
 'caution':'O horizonte de cinco anos pertence à previsão. A regra da carteira revê posições todo mês e pode continuar na mesma moeda por vários meses.',
 'qa':'São operações independentes de um mês? A carteira tem decisões mensais. Uma moeda pode permanecer na posição se o ranking continuar favorável. Calculamos o resultado dessa exposição sucessiva, com custos sobre as mudanças do notional.',
 'transition':'Depois desse resultado, investiguei se commodities e comércio ajudam a própria previsão.',
 'training':training[6],
 'sources':['output/tables/portfolio_returns.csv','output/tables/portfolio_metrics.csv','src/models.py']}
tenure={
 'old':'tenure','title':'O prazo dos lotes altera a exposição e o resultado','seconds':65,
 'core':'A carteira funciona continuamente, mas a duração máxima dos lotes do módulo de permanência modifica a composição, a exposição e o risco.',
 'concepts':'A combinação tem três módulos. Os dois primeiros revêm o carry mensalmente. O terceiro abre novos lotes mensais e permite carregá-los até um prazo máximo, com saída antecipada por risco. Aqui só variamos esse máximo entre 6, 12 e 24 meses. O orçamento de entrada mensal desse módulo é 1/H, onde H é o prazo máximo, preservando o teto de exposição. As previsões permanecem as mesmas: EJR de 60 meses e risco de consumo dos juros em 12 meses. Portanto, é uma sensibilidade de política de permanência, não uma comparação de novos modelos de previsão para cada prazo.',
 'reading':'A tabela mostra a combinação inteira na mesma janela de abril de 2018 a agosto de 2026, com os mesmos custos. Para 6, 12 e 24 meses, os retornos anuais são 5,96%, 5,94% e 5,77%. A exposição média cai de 51% para 48% e 44%. Essa mudança de exposição participa da diferença de risco. A saída pode ocorrer antes do máximo e a entrada é gradual.',
 'speech':'Mesmo com uma carteira contínua, o prazo importa. Aqui mantive os outros dois módulos e alterei apenas o prazo máximo dos lotes do módulo de permanência. O retorno muda pouco entre seis e doze meses e cai um pouco em vinte e quatro. A exposição também cai conforme aumenta o prazo máximo, porque as entradas são menores e podem sair antes por risco. Isso mostra que o prazo muda a política, mas não prova que doze meses seja ótimo. E não mudamos o horizonte do modelo de risco: ele continua olhando doze meses.',
 'caution':'Os prazos são máximos, não permanências garantidas. Não confunda prazo do lote, frequência mensal de revisão, previsão nominal de 60 meses e previsão de risco de 12 meses. Os testes usam a mesma história exploratória.',
 'qa':'Por que o prazo maior reduziu a exposição? Com orçamento 1/H por entrada e saída antecipada, muitos lotes podem sair antes de completar H meses. A formação gradual e o cancelamento entre pontas também influenciam a exposição líquida por moeda. Isso deve ser considerado ao comparar o risco.',
 'transition':'A trajetória do patrimônio da combinação-base, com lotes de até doze meses, aparece no próximo gráfico.',
 'training':training[11],
 'sources':['synthesis/tables/robustness.csv: Base, Tenure6, Tenure24','synthesis/model.py: make_policies, cohorts','synthesis/robustness.py']}
new=[]
for s in C['slides']:
 new.append(s)
 if s['old']==6:new.append(wealth)
 if s['old']==11:new.append(tenure)
C['slides']=new;C['main_count']=17
times=[30,70,75,90,85,80,50,65,80,65,105,80,65,50,55,60,35,0,0]
assert sum(times)==1140
for s,t in zip(new,times):s['seconds']=t
# Remove obsolete cross-references in the detailed explanations.
S[15]['caution']='Encerre no slide 17. Os slides 18 e 19 são apoio para perguntas e ficam fora dos 19 minutos.'
S[4]['transition']='A heterogeneidade preditiva motivou testar se a previsão ajuda na escolha das posições de carry.'
S[11]['transition']='Antes de ver o gráfico, verifico o que muda quando altero o prazo dos lotes.'
(H/'content_v2.json').write_text(json.dumps(C,ensure_ascii=False,indent=2),encoding='utf-8')
(H/'data_v2.json').write_text(json.dumps(D,ensure_ascii=False,indent=2),encoding='utf-8')
print('19 slides, 17 main, 19 minutes; read-only empirical sources.')
