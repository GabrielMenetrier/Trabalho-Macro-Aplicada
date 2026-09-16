"""Assemble existing evidence and explanatory notes for the revised class deck."""
from pathlib import Path
import sys,json,hashlib,runpy
import numpy as np,pandas as pd
R=Path(__file__).resolve().parents[1];H=R/'presentation'
sys.stdout.reconfigure(encoding='utf-8')
D=json.loads((H/'data_v6.json').read_text(encoding='utf-8'))
old=json.loads((H/'content_v6.json').read_text(encoding='utf-8')); by={s['old']:s for s in old['slides']}
used=[]
def read(p):
    used.append(p);return pd.read_csv(R/p)
def rec(df):return json.loads(df.to_json(orient='records',double_precision=15))
full=read('ejr_trade/tables/metrics.csv');sel=read('ejr_trade_selected/tables/metrics.csv')
D['tt_full']=rec(full[(full.scenario=='main')&(full.period=='all')&full.model.isin(['EJR','TOT_both'])])
D['tt_selected']=rec(sel[(sel.scenario=='fixed')&sel.model.isin(['EJR','TOT_LOG_LD','TOT_DEV_LD','TOT_SLOG_LD'])])
D['tt_transforms']=rec(sel[(sel.scenario=='fixed')&(sel.country=='POOL')&((sel.model=='EJR')|sel.model.str.startswith('TOT_'))])
D['pooling']=rec(read('ejr_trade_selected/tables/pooling_diagnostics.csv'))
six=read('horizon_tests/tables/with_terms_of_trade.csv');six=six[~six.metodo.str.contains('mensal')]
three=read('horizon_tests/tables/restricted_table.csv');three=three[three.method!='monthly120']
D['six_table']=rec(six);D['three_table']=rec(three)
# Rebase all curves from the first common return; cached nav includes pre-period USD cash.
raw=read('horizon_tests/tables/returns.csv.gz');tt=read('horizon_tests/tables/with_tot_returns.csv.gz')
rr=read('horizon_tests/tables/restricted_returns.csv.gz');D['wealth']={};audit=[]
for universe,table in [('six',six),('three',three)]:
    rows=[]
    for method in ['Ranking','long60']:
        signals=['Carry','EJR','EJR_trio','EJR_TOT_trio'] if universe=='six' else ['Carry','EJR','TT_all','Matched']
        for sig in signals:
            for hold in [12,60]:
                if universe=='six':
                    methodlabel='Dois pares' if method=='Ranking' else 'Máximo Sharpe — risco de 60 meses'
                    match=table[(table.scenario=='Base')&(table.metodo==methodlabel)&(table.variant==sig)].iloc[0]
                    if sig in ['Carry','EJR']:
                        name=('Pairs_'+sig) if method=='Ranking' else ('Sharpe_'+sig+'_long60')
                        a=raw[(raw.scenario=='Base')&(raw.name==name)&(raw.hold==hold)]
                    else:a=tt[(tt.scenario=='Base')&(tt.method==methodlabel)&(tt.variant==sig)&(tt.hold==hold)]
                else:
                    match=table[(table.scenario=='Base')&(table.method==method)&(table.signal==sig)].iloc[0]
                    a=rr[(rr.scenario=='Base')&(rr.method==method)&(rr.signal==sig)&(rr.hold==hold)]
                a=a.sort_values('month');assert len(a)==180 and a.month.iloc[0]=='2010-03' and a.month.iloc[-1]=='2025-02'
                nav=100*np.r_[1,np.cumprod(1+a.net.to_numpy())]
                cash=100*np.r_[1,np.cumprod(1+a.cash.to_numpy())]
                cagr=(nav[-1]/100)**(1/15)-1
                assert abs(cagr-match[f'cagr_{hold}'])<1e-10
                dates=['2010-02']+a.month.tolist()
                x=[int(t[:4])+(int(t[5:])-1)/12 for t in dates]
                rows.append(dict(method=method,signal=sig,hold=hold,x=x,nav=nav.tolist(),cash=cash.tolist()))
                audit.append(dict(universe=universe,method=method,signal=sig,hold=hold,cagr=cagr,table_cagr=match[f'cagr_{hold}'],passed=True))
    D['wealth'][universe]=rows
# Reproduce historical fitted values for the two displayed methods, without changing research outputs.
e=runpy.run_path(str(R/'ejr_trade_selected/run.py'),run_name='selected_engine')
X=e['designs'](e['T']-1);ins=read('ejr_trade_selected/tables/in_sample.csv');pred=read('ejr_trade_selected/tables/predictions.csv.gz')
D['tt_scatter']=[]
for j,cc in enumerate(e['CC']):
    y=e['S'][60:,j]-e['S'][:-60,j]
    ob=pred[(pred.h==60)&(pred.country==cc)].sort_values('origin')
    for model in ['EJR','TOT_LOG_LD']:
        cols=['Q']+e['MODELS'][model];a=np.c_[np.ones(len(y)),np.stack([X[k][:-60,j] for k in cols],axis=1)]
        fit=a@np.linalg.lstsq(a,y,rcond=None)[0]
        r2=1-(np.sum((y-fit)**2)/(len(y)-a.shape[1]))/(np.sum((y-y.mean())**2)/(len(y)-1))
        ref=ins[(ins.h==60)&(ins.country==cc)&(ins.model==model)].iloc[0]
        assert abs(r2-ref.adjusted_r2)<1e-10
        metric=sel[(sel.h==60)&(sel.scenario=='fixed')&(sel.country==cc)&(sel.model==model)].iloc[0]
        D['tt_scatter'].append(dict(country=cc,model=model,fitted=(100*fit).tolist(),actual_fit=(100*y).tolist(),
            predicted=(100*ob[model]).tolist(),actual_oos=(100*ob.actual).tolist(),r2=r2,rmse=metric.rmse_rw))
D['new_sources']=[dict(path=p,sha256=hashlib.sha256((R/p).read_bytes()).hexdigest()) for p in used]
(H/'data_v7.json').write_text(json.dumps(D,ensure_ascii=False),encoding='utf-8')
(H/'build/evidence_audit_v7.json').write_text(json.dumps(audit,indent=2),encoding='utf-8')

slides=[]
def add(key,title,seconds,core,concepts,reading,speech,caution,training,sources,qa='',transition=''):
    slides.append(dict(old=key,title=title,seconds=seconds,core=core,concepts=concepts,reading=reading,speech=speech,caution=caution,training=training,sources=sources,qa=qa,transition=transition))
for i,sec in [(1,25),(2,60),(3,60),(4,75),(5,55),(6,55)]:
    s=dict(by[i]);s['seconds']=sec;slides.append(s)
slides[0].update(title='Câmbio real, termos de troca e carry trade',core='Separar capacidade de previsão de valor econômico em carteiras.',
 speech='O trabalho parte da previsão de câmbio nominal a partir do câmbio real. Primeiro verifico o que consigo reproduzir. Depois testo se termos de troca ajudam a previsão e se essa informação melhora carteiras de carry, comparando decisões anuais e de cinco anos.',transition='Começo pela hipótese econômica do artigo.')
slides[4]['concepts']+=' Nos testes finais, a expectativa é formada diretamente em 60 meses. O retorno de cada mês usa os juros e o câmbio realizados, com caixa USD e custos.'
slides[5]['transition']='Esse fracasso motivou duas revisões: acrescentar termos de troca à previsão e testar carteiras que mantêm a escolha por doze ou sessenta meses.'
train='Previsão nominal de 60 meses. Treino inicial: origens out/1999–dez/2004, alvos até dez/2009. Treino expansivo com j+60 <= t−1. Origens avaliadas jan/2010–ago/2021, alvos jan/2015–ago/2026.'
src=['ejr_trade/run.py','ejr_trade_selected/run.py','ejr_trade_selected/tables/metrics.csv']
add('tt_model','Termos de troca na previsão nominal',65,
 'A extensão pergunta se preços de exportação e importação acrescentam informação ao câmbio real.',
 'Termos de troca são preços de exportação divididos pelos de importação. Uma melhora permite importar mais com a mesma quantidade exportada. Pode alterar renda externa e demanda pela moeda, mas não fixa um sinal causal universal. O modelo base prevê a mudança do log da cotação nominal usando o desvio do log do câmbio real. A extensão acrescenta log do índice de TT e sua mudança anual, centrados com história disponível. Não se prevê o próprio câmbio real.',
 'Leia primeiro a variável dependente. Depois identifique o regressor EJR e os dois termos adicionais. O exemplo 120/110 mostra que TT sobe 9,1%, não 10%.',
 'A previsão continua sendo a variação do câmbio nominal em cinco anos. Acrescentei preços relativos do comércio: quanto o país recebe pelo que exporta em relação ao que paga para importar. Testo o nível e a mudança anual dessa relação. A ideia é verificar se o câmbio real parece barato porque vai se corrigir, ou porque as condições econômicas do país mudaram.',
 'TT agregado vem dos deflatores de bens e serviços das contas nacionais. Não confundir com cesta de commodities. Para o euro, os dados comerciais usam Alemanha como aproximação.',
 train+' TT anual do ano Y−2, CPI com dois meses de atraso. Séries revisadas, sem vintages históricos.',src,
 'É efeito causal? Não. É ganho preditivo condicionado às outras variáveis.','Primeiro mostro o que acontece com o painel completo.')
add('tt_full','Seis moedas: termos de troca não melhoram o painel',55,
 'No painel original, TT não recupera a previsão agregada em cinco anos.',
 'RMSE é a raiz da média do erro quadrático. Dividir pelo erro de nenhuma mudança produz uma referência igual a 1. Abaixo de 1 é melhora pontual na amostra avaliada, sem significância estatística automática. A coluna TT usa o mesmo conjunto de países para estimar os coeficientes. BRL, EUR e CAD apresentam EJR abaixo de 1 em cinco anos.',
 'Compare horizontalmente EJR e EJR+TT. Depois compare cada número com 1. Mostre a linha agregada apenas depois das moedas.',
 'Nas seis moedas, o erro agregado passa de 1,037 para 1,092 quando incluo termos de troca. Portanto, a adição não resolve o problema do painel completo. Brasil, euro e Canadá são os casos em que a previsão EJR supera a referência de nenhuma mudança. Essa observação motiva o próximo recorte.',
 'A escolha do trio usa esta avaliação inteira e é retrospectiva. Não era uma seleção conhecida no início do backtest.',train,src,
 'Por que um número maior que 1? Porque, nesse país ou agregado e nessa avaliação, a previsão errou mais do que supor cotação constante.')
add('tt_selected','O ganho com termos de troca se concentra no Brasil',65,
 'No trio reestimado, o erro agregado cai, mas euro e Canadá pioram com TT.',
 'Reestimar no trio muda o coeficiente comum do EJR. Por isso 0,802 não é o mesmo objeto que o agregado de seis moedas 1,037. O comparativo correto da adição é EJR e EJR+TT estimados no mesmo trio. O agregado usual soma erros quadráticos em log antes de tirar a raiz, e o Brasil pesa bastante por ter movimentos maiores. As formas comparadas são log centrado, desvio percentual da média e log com sinal. Todas usam nível mais mudança.',
 'Leia as três moedas antes do agregado. Na pequena tabela de transformações, compare as variantes em cinco anos. Log do desvio negativo puro não é definido nos reais.',
 'Quando reestimo EJR nos três países, o agregado é 0,802. Com termos de troca em log e mudança anual, cai para 0,628. Parece um ganho forte, mas ele está concentrado no Brasil: 0,804 para 0,544. Euro e Canadá pioram. Então vou testar tanto TT nas três moedas quanto TT apenas no Brasil.',
 'A transformação vencedora foi escolhida na mesma história. A agregação que normaliza o erro por país muda a conclusão: EJR 0,810 e TT 0,844.',train,src+['ejr_trade_selected/tables/pooling_diagnostics.csv'],
 'Isso prova que TT ajuda todos os países? Não. O ganho agregado padrão é dominado pelo Brasil.')
add('tt_fit','Ajuste histórico das regressões, por país',45,
 'O ajuste dentro da amostra melhora especialmente no Brasil e no Canadá.',
 'Cada ponto compara a variação nominal ajustada pela regressão com a observada nos cinco anos seguintes. Pontos na diagonal correspondem a ajuste perfeito. Azul é EJR, laranja é EJR+TT. Aqui há intercepto e regressão individual por país para diagnóstico, estimada usando a amostra inteira. É diferente da regressão agrupada recursiva do teste seguinte.',
 'Eixo horizontal: valor ajustado. Vertical: valor realizado. Compare a distância da nuvem azul e da laranja à diagonal. Mostre R² ajustado, que penaliza regressoras adicionais.',
 'Aqui estou olhando o ajuste histórico, não uma previsão que eu poderia ter feito naquela data. A adição aproxima bastante os pontos da diagonal no Brasil e no Canadá. O passo essencial é perguntar se esse ajuste também funciona quando o modelo só conhece o passado.',
 'Não chamar R² alto de prova de previsão. As regressões deste diagnóstico usam toda a amostra, com intercepto por país.',
 'Ajuste individual na amostra: origens out/1999–ago/2021, alvos out/2004–ago/2026. Horizonte 60m. Sem avaliação fora da amostra neste slide.',
 ['ejr_trade_selected/figures.py','ejr_trade_selected/tables/in_sample.csv'])
add('tt_oos','Previsões com informação passada, por país',55,
 'O ganho fora da amostra permanece no Brasil e não se generaliza ao trio.',
 'A diagonal agora representa uma previsão perfeita. Cada ponto é uma origem mensal, mas horizontes sobrepostos tornam os erros dependentes. Os coeficientes são agrupados no trio e reestimados a cada origem com alvos encerrados. O contraste com o slide anterior envolve tanto a avaliação fora da amostra quanto a especificação agrupada.',
 'Horizontal: previsão formada na origem. Vertical: resultado cinco anos depois. As cores continuam azul EJR e laranja EJR+TT. Leia os RMSE relativos abaixo de cada país.',
 'Ao exigir informação disponível no momento da previsão, o resultado fica menos uniforme. Brasil melhora, euro e Canadá pioram. Este é o ponto que a comparação de ajuste histórico não revelava. Esses são os sinais que passam para a aplicação de carteira.',
 'As origens se sobrepõem. Um ganho pontual de RMSE não estabelece significância nem lucro de mercado.',train,src)
booktrain='Backtest mar/2010–fev/2025, 180 retornos. Sinal inicial jan/2010, execução fev/2010. Treino cambial inicial out/1999–dez/2004, alvos até dez/2009. Expansivo, somente alvos encerrados até t−1.'
booksrc=['horizon_tests/run.py','horizon_tests/add_terms_of_trade.py','horizon_tests/restricted_countries.py','src/models.py']
add('book_rules','Carteiras com escolha a cada 12 ou 60 meses',75,
 'Comparar os mesmos sinais, métodos, custos e datas, mudando o intervalo entre escolhas.',
 'Ranking compra as maiores expectativas e vende as menores. Máximo Sharpe considera retorno esperado e covariância dos retornos acumulados em 60 meses. O objetivo usa juros correntes extrapolados por cinco anos menos depreciação nominal prevista. As posições têm 50% comprado e 50% vendido. Com seis moedas, ranking usa duas em cada lado a 25%. Com três, usa uma em cada lado a 50%. O otimizador pode distribuir os pesos dentro desses limites. A covariância usa só resultados encerrados até t−1, com 20% de regularização diagonal.',
 'Diferencie horizonte previsto de intervalo de decisão. Janeiro de 2010 escolhe a carteira. No caso anual, nova escolha em janeiro de 2011. No caso 60m, nova escolha em janeiro de 2015. Os pesos-alvo recebem manutenção mensal.',
 'Agora faço a comparação que faltava: escolher a carteira por um ano ou por cinco anos. A previsão é de cinco anos nos dois casos. O risco do otimizador também vem de retornos acumulados em cinco anos. Líquida zero significa compras e vendas de mesmo tamanho em dólares, mas não significa risco zero.',
 'Manutenção mensal dos pesos não é congelar quantidades. Com atraso de execução, a última realização de uma posição de 60 meses ocorre em t+61, enquanto a previsão aponta t+60. Há só três blocos de cinco anos.',booktrain,booksrc,
 'O resultado inclui juros? Sim. Caixa USD, juros locais, variação cambial, custos e financiamento. O retorno mensal usa a composição exata de juros e câmbio.')
for key,univ in [('six','seis moedas'),('three','BRL, EUR e CAD')]:
    specific=('No universo de seis moedas, EJR original foi estimado nas seis. O controle substitui as previsões do trio por EJR reestimado no trio. A linha TT substitui essas mesmas três previsões por EJR+TT. JPY, GBP e SEK mantêm EJR original. Logo, TT não significa uma carteira restrita ao trio.' if key=='six' else
              'No universo selecionado, só BRL, EUR e CAD entram nas posições. EJR é estimado no trio. TT nas três usa a extensão em todas. Combinado usa TT apenas no BRL, mantendo EJR no EUR/CAD. O teto por moeda sobe de 25% para 50%, necessário para manter exposição bruta de 100%.')
    conclusion=('Carry puro tem retorno maior que EJR e TT nas alternativas exibidas. Escolher pesos por cinco anos não produz vantagem geral.' if key=='six' else
                'EJR com risco de 60 meses e escolha anual apresenta retorno 3,29% a.a. e Sharpe 0,393. TT, inclusive só no BRL, piora frente ao EJR nas quatro comparações exibidas de método e prazo.')
    add(key+'_wealth','Patrimônio das carteiras: '+univ,75,
        conclusion,specific+' Patrimônio começa em 100 antes do primeiro retorno comum e acumula retornos líquidos. Cada painel fixa método e prazo. Cor representa sinal. Caixa USD é referência, não outra moeda escolhida pelo otimizador.',
        'Leia primeiro os títulos dos quatro painéis. Colunas: escolhas a cada 12 ou 60 meses. Linhas: ranking ou máximo Sharpe com risco 60m. Compare cores dentro de um painel e depois o mesmo sinal entre os prazos.',
        ('Nas seis moedas, somar a previsão ao carry não melhora o retorno das carteiras mostradas. A comparação laranja versus violeta isola adicionar termos de troca ao controle com o mesmo trio de estimação. A curva cinza é apenas o caixa americano.' if key=='six' else 'Agora só negocio nas moedas em que EJR melhorou a previsão. A carteira azul com máximo Sharpe e escolha anual tem o maior retorno deste quadro. A informação de termos de troca, em laranja, não transforma o ganho de previsão brasileiro em melhor carteira. Mesmo usar TT só no Brasil, em verde, não resolve isso.'),
        'A seleção de países e da forma de TT usa a avaliação inteira. Retrospectivo, sem teste independente. Não comparar seis e três como se o teto por moeda fosse igual.',booktrain,booksrc,
        'A curva mostra retorno cambial puro? Não. É patrimônio em USD após juros, câmbio, financiamento e custos.')
    add(key+'_table','Retorno e risco: '+univ,45,
        conclusion,specific+' Cada célula informa retorno anual composto / Sharpe anualizado / queda máxima. Sharpe é o excesso ao caixa USD dividido pelo desvio padrão desse excesso, anualizado. A queda máxima é a pior perda desde o pico da curva.',
        'Leia só uma linha inteira para explicar a tripla. Compare laranja contra o EJR correspondente. O sinal de queda máxima é negativo. 12m/60m se refere às escolhas, não ao período de cálculo do CAGR.',
        'A tabela dá os números exatos das curvas anteriores. Cada tripla é retorno anual, Sharpe e queda máxima. O Sharpe aqui é uma medida realizada para resumir o backtest. O risco utilizado na escolha dos pesos continua sendo a covariância em sessenta meses.',
        'Não interpretar a maior célula entre várias alternativas exploradas como evidência estatística de vantagem persistente.',booktrain,booksrc)
add('costs','O ganho com EJR permanece sob custos maiores',50,
 'No trio, a carteira EJR com escolha anual ainda supera o carry sob os custos de estresse assumidos.',
 'Custos básicos: BRL 10pb, SEK 3pb, demais 2pb por negociação. Spread adicional de 50pb a.a. sobre o notional vendido, além dos juros. Estresse multiplica negociação por quatro e eleva spread para 150pb. Os pesos são os mesmos. A comparação apresentada fixa trio, máximo Sharpe com risco de 60 meses e escolha anual.',
 'Compare a mudança de cada sinal entre custos básicos e estresse. Em seguida, olhe volatilidade e queda máxima da alternativa EJR. Não conclua que os custos são executáveis só porque o resultado resiste ao cenário.',
 'No caso selecionado, o retorno do EJR cai de 3,29 para 2,65 por cento ao ano quando aumento os custos. O carry cai de 2,86 para 2,25. A vantagem histórica permanece, mas ainda falta conferir spreads realmente negociáveis e testar a regra em dados novos.',
 'Custos assumidos, não cotações executáveis. Testar estresse não remove seleção retrospectiva, revisões dos dados ou incerteza estatística.',booktrain,booksrc)
add('conclusion','O que os testes permitem concluir',55,
 'Há evidência preditiva localizada e um resultado de carteira exploratório com EJR.',
 'O projeto separa quatro objetos: relação histórica da aula, previsão fora da amostra, extensão por termos de troca e tradução da previsão em pesos de carteira. O ganho de TT no RMSE individual do Brasil não impõe que a classificação relativa das moedas ou o resultado de juros+câmbio melhore. O recorte de países e os parâmetros foram escolhidos na história já avaliada. Três blocos de cinco anos limitam conclusões sobre o prazo de manutenção.',
 'Feche com a distinção entre o que funcionou na previsão e o que funcionou nas carteiras. As referências sobre regras de exposição ficam depois deste fechamento, para perguntas.',
 'Consegui reproduzir parte da relação preditiva, principalmente em Brasil, euro e Canadá no horizonte de cinco anos. Termos de troca melhoram bastante a previsão brasileira, mas não melhoram as carteiras testadas. O resultado econômico mais interessante é EJR com escolha anual no trio selecionado. É um resultado histórico que merece validação futura, não uma prova de arbitragem ou de retorno garantido.',
 'Amostra usada para escolher e avaliar. Não chamar esta seleção retrospectiva de carteira fora da amostra independente.',
 'Previsões: origens jan/2010–ago/2021 para 60m. Carteiras finais: mar/2010–fev/2025. Seleção informada por alvos até ago/2026.',src+booksrc)
assert len(slides)==18
# Additional evidence stays after the conclusion to respect the class time limit.
add('transform_backup','Apoio: transformações e horizontes dos termos de troca',0,
 'O ganho depende do horizonte e da forma de entrada dos termos de troca.',
 'As três extensões usam nível e mudança anual. Log usa log do índice centrado; desvio usa índice dividido pela média passada menos um; log com sinal aplica sinal(desvio) vezes log(1+abs(desvio)). Log(1+desvio), quando centrado, coincide com log centrado e não é um quarto candidato independente.',
 'Compare cada variante com EJR no mesmo horizonte. Os calendários diferem porque horizontes longos precisam de treino e alvos completos mais longos.',
 'Estas são as variações que testei. A especificação que levei às carteiras usa log e mudança anual em log, escolhida no teste de cinco anos. Esta tabela ajuda a ver que a escolha depende do horizonte.',
 'Escolha da forma na mesma amostra. Não é teste independente do vencedor.',
 'Treino expansivo desde out/1999. Mínimo 60 origens maduras. Origens 12m: jan/2010–ago/2025; 24m até ago/2024; 36m até ago/2023; 60m até ago/2021; 84m nov/2011–ago/2019; 96m nov/2012–ago/2018.',src)
add('pooling_backup','Apoio: o agregado depende do peso do Brasil',0,
 'Uma média mais equilibrada entre os países enfraquece o ganho agregado de TT.',
 'Agregado padrão calcula RMSE com todas as observações em log. Erros maiores no Brasil pesam mais. A medida normalizada por país divide cada erro pelo RMSE de nenhuma mudança do país antes de agregar. O teste sem BRL reestima nos dois países restantes. São comparações distintas, identificadas na tabela.',
 'Na primeira linha, TT melhora. Na segunda, a mudança na normalização inverte a ordem. Na terceira, retirar o Brasil também elimina a melhora.',
 'O ganho agregado de termos de troca não é uniforme. Ele depende muito do Brasil. Isso explica por que examinei cada país e também tentei TT só no Brasil, embora essa escolha não tenha melhorado a carteira.',
 'Normalização do diagnóstico usa a avaliação completa. Sem BRL também muda os coeficientes estimados.',train,
 ['ejr_trade_selected/tables/pooling_diagnostics.csv'])
for key in [10,11,12,'tenure',17]:
    s=dict(by[key]);s['seconds']=0;s['title']=s['title'].replace('Referência exploratória:','Referência:');s['transition']='Material de referência para perguntas. A conclusão principal já foi apresentada.'
    if key=='tenure':s['training']='Backtest abr/2018–ago/2026. Primeiro sinal fev/2018: treino EJR out/1999–jan/2013, risco jan/2011–dez/2016, alvos até jan/2018. Depois, expansivo. Lotes 6, 12 ou 24m; risco comercial previsto em 12m.'
    slides.append(s)
C=dict(title='Câmbio real, termos de troca e carry trade',subtitle='Replicação de EJR e aplicações com horizonte de cinco anos',main_slides=18,slides=slides)
(H/'content_v7.json').write_text(json.dumps(C,ensure_ascii=False,indent=2),encoding='utf-8')
md=['# Guia de estudo e fala','',C['title'],'',f"18 slides principais, {sum(s['seconds'] for s in slides)//60} min {sum(s['seconds'] for s in slides)%60}s de roteiro. 7 slides de apoio."]
for i,s in enumerate(slides,1):
    md+=['',f"## Slide {i:02d}: {s['title']}",'',f"Tempo: {s['seconds']} segundos."]
    for key in ['core','concepts','reading','training','speech','caution','qa','transition']:md+=['',key+': '+s.get(key,'')]
    md+=['','Fontes: '+', '.join(s['sources'])]
(H/'guia_slides_v7.md').write_text('\n'.join(md),encoding='utf-8')
print('Prepared',len(slides),'slides; seconds',sum(s['seconds'] for s in slides),'curves checked',len(audit))
