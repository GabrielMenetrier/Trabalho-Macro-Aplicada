"""Remove the commodity forecasting section from the class presentation."""
from pathlib import Path
import json
R=Path(__file__).resolve().parents[1]; H=R/'presentation'
C=json.loads((H/'content_v5.json').read_text(encoding='utf-8'))
C['slides']=[s for s in C['slides'] if s['old'] not in (7,8)]
C['title']='Câmbio real e carry trade'
by={s['old']:s for s in C['slides']}
by[1]['title']=C['title']
by[1]['speech']=by[1]['speech'].replace(' com e sem commodities','')
by[1]['qa']='Qual é a pergunta central? A informação do câmbio real ajuda a prever o câmbio nominal e, separadamente, a decidir como assumir risco cambial?'
by['initial_wealth']['transition']='A seguir, mostro como referência exploratória os resultados das regras de exposição. Elas não validam uma estratégia de investimento de longo prazo baseada no artigo.'
by[15]['concepts']='A conclusão deve separar o que foi reproduzido do que ficou como hipótese. A relação histórica brasileira apresentada na aula foi recuperada. Somar a previsão ao ranking mensal falhou, enquanto regras de exposição apresentaram risco histórico menor. Nenhuma dessas etapas prova arbitragem, ganho causal de uma variável ou alfa persistente.'
by[15]['caution']='Encerre no slide 14. Os slides 15 e 16 são apoio para perguntas e ficam fora dos 15 minutos e 30 segundos.'
by[15]['sources']=['Relatórios original e síntese']
s=by[16]
s['core']='A regressão usa o desvio do câmbio real para prever a mudança futura do câmbio nominal.'
s['concepts']='No EJR implementado, Δs(t,t+h) = β_h × [q_t − média histórica de q] + erro, com coeficiente agrupado e sem intercepto adicional. A média é calculada com dados disponíveis na origem. Cada regressão em t só usa alvos j+h que terminaram até t−1. A observação atual do CPI entra com dois meses de atraso. A previsão mensal usada no sinal de carry é a previsão de Δs em 60 meses dividida por 60, uma aproximação de ritmo médio, não uma trajetória estimada.'
s['reading']='Use somente se houver pergunta técnica. Explique cada letra antes de interpretar o coeficiente. A variável prevista é nominal. O câmbio real é o regressor.'
s['speech']='Esta é a forma simplificada da regressão. A variável prevista é a mudança futura do log da cotação nominal. O regressor é o desvio do câmbio real em relação à sua média histórica disponível. Um alvo só entra no treinamento depois de terminar. Não treino uma previsão de cinco anos com resultados que ainda não poderiam ser conhecidos.'
s['qa']='Há identificação causal? Não. Há uma avaliação preditiva condicional, sem uma fonte exógena de variação que identifique um efeito causal.'
s['sources']=['src/models.py']
s['training']=s['training'].replace('CPI e preços defasados.','CPI defasado em dois meses.')
(H/'content_v6.json').write_text(json.dumps(C,ensure_ascii=False,indent=2),encoding='utf-8')
(H/'data_v6.json').write_bytes((H/'data_v5.json').read_bytes())
t=(H/'build/deck_v5.mjs').read_text(encoding='utf-8').replace('_v5','_v6')
a=t.index("{\n const s=slide(7,"); b=t.index("{\n const s=slide(10,",a);t=t[:a]+t[b:]
t=t.replace('physical>16','physical>14').replace('mainSlides:16','mainSlides:14')
t=t.replace('Câmbio real, commodities\\ne carry trade','Câmbio real\\ne carry trade')
t=t.replace('Extensão: base + γ × preços globais + δ × exposição específica','Desvio real = q(t) − média histórica disponível de q')
t=t.replace('CPI e preços comerciais entram defasados.','O CPI entra com dois meses de atraso.')
t=t.replace('Fontes: src/models.py e third/engine.py.','Fonte: src/models.py.')
(H/'build/deck_v6.mjs').write_text(t,encoding='utf-8')
t=(H/'build_pdfs_v5.py').read_text(encoding='utf-8').replace('_v5','_v6')
t=t.replace('Câmbio real, commodities e carry trade','Câmbio real e carry trade').replace('câmbio real, commodities e carry','câmbio real e carry')
t=t.replace('16 slides principais','14 slides principais').replace('17 minutos e 55 segundos','15 minutos e 30 segundos').replace('aproximadamente dois minutos de margem','quatro minutos e trinta segundos de margem')
t=t.replace('Só então passe aos slides 8–9, que tratam das extensões sem carteiras. Nos slides 10–15, concentre-se nas decisões econômicas e nos limites da evidência. A conclusão do slide 16','Nos slides 8–13, concentre-se nas regras exploratórias de carteira e nos limites da evidência. A conclusão do slide 14')
t=t.replace('slides 17 e 18','slides 15 e 16').replace("'Commodities e comércio','Previsão nominal ampliada',",'').replace("C['slides'][:16]","C['slides'][:14]")
t=t.replace('No 9, destaque somente o erro 0,890 na janela completa e 1,630 na recente. No 11,','No 9,').replace('No 12, compare os prazos','No 10, compare os prazos').replace('No 14, explique a troca','No 12, explique a troca').replace('slides 6, 10 e 15','slides 6, 8 e 13')
t=t.replace(",['8–9','Relatório terciário: relatorio_terciario.pdf. Tabelas em third/tables.']",'').replace("['10–15 e 18'","['8–13 e 16'").replace("['17','Equações e calendário em src/models.py e third/engine.py.']","['15','Equações e calendário em src/models.py.']")
t=t.replace('PDF slides: 18 pages.','PDF slides: 16 pages.')
(H/'build_pdfs_v6.py').write_text(t,encoding='utf-8')
t=(H/'qa_v5.py').read_text(encoding='utf-8').replace('_v5','_v6')
t=t.replace('==18','==16').replace('==1075','==930').replace("s['old']!=9","s['old'] not in (7,8,9)").replace('range(1,19)','range(1,17)').replace("_v6',18)","_v6',16)").replace("_v6',24)","_v6',22)").replace("'slides':18","'slides':16").replace("'guide_pages':24","'guide_pages':22").replace("'seconds':1075","'seconds':930").replace('18 slide renders, 24 guide pages','16 slide renders, 22 guide pages')
(H/'qa_v6.py').write_text(t,encoding='utf-8')
