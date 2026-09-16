"""Separate long-horizon prediction from exploratory monthly portfolio policies."""
from pathlib import Path
import json
R=Path(__file__).resolve().parents[1];H=R/'presentation'
C=json.loads((H/'content_v4.json').read_text(encoding='utf-8'))
by={s['old']:s for s in C['slides']}
by[1]['speech']='O trabalho parte da previsibilidade cambial de médio e longo prazo estudada por Eichenbaum, Johannsen e Rebelo. Apresento uma replicação parcial da relação da aula e testes de previsão nominal com e sem commodities. Depois mostro, apenas como referência exploratória, aplicações mensais e filtros de exposição. Esses resultados de carteira não demonstram a exploração do ajuste de longo prazo do artigo.'
by[1]['caution']='Distinguir replicação parcial da relação preditiva e regras de investimento próprias. Os resultados posteriores de carteira são referências exploratórias.'
by[2]['reading']='Explique a relação entre câmbio real e nominal. A seção 3.3 do artigo encontra ganho agregado fora da amostra em horizontes acima de dois anos, destacando quatro e seis anos. Isso não demonstra previsão do caminho mensal. O artigo não propõe as regras de carteira posteriores deste trabalho.'
by[5]['caution']='Aplicação própria: convertemos a previsão de 60 meses em ritmo mensal dividindo por 60. Isso não estima uma trajetória mensal nem replica uma estratégia de investimento do artigo.'
by[6]['title']='Aplicação mensal de uma previsão de cinco anos'
by[6]['core']='O ranking mensal com sinal de cinco anos perdeu para o carry. Esse resultado avalia esta implementação, não rejeita a previsibilidade de longo prazo.'
by[6]['speech']='Esta é uma aplicação própria, não uma carteira do artigo. Usamos previsão cambial de cinco anos, dividida por sessenta para formar um sinal mensal. Compramos duas moedas e vendemos duas, com pesos iguais, revistos mensalmente. Não houve Markowitz. O resultado foi pior que o carry por juros. Isso não prova que a previsão de longo prazo falhou: o backtest testa uma tradução específica da previsão em decisões mensais, sem manter obrigatoriamente as posições até o horizonte previsto.'
by[6]['qa']='Qual prazo foi usado? Previsão de 60 meses, revisão mensal e nenhum prazo máximo de permanência no ranking. A dispersão da aula usa oito anos. São objetos distintos. A rotina inicial também calculou coortes de 60 meses, ausentes deste gráfico, mas não uma otimização de Markowitz.'
by['initial_wealth']['title']='Patrimônio da aplicação mensal do sinal de cinco anos'
by['initial_wealth']['caution']='Este gráfico não representa posições obrigatoriamente mantidas por cinco anos e não demonstra captura da convergência de longo prazo.'
by[8]['transition']='A seguir, mantenho apenas como referência os resultados exploratórios de regras de exposição. Eles não validam uma estratégia de investimento de longo prazo baseada no artigo.'
titles={10:'Referência exploratória: regras de exposição',11:'Referência exploratória: resultado da combinação','tenure':'Referência exploratória: prazo dos lotes',12:'Referência exploratória: trajetória da combinação',13:'Referência exploratória: decomposição do resultado'}
for key,title in titles.items():
    s=by[key];s['title']=title
    s['core']='Referência exploratória de uma regra própria; não valida a captura do ajuste cambial de longo prazo.'
    s['caution']='Resultado selecionado na pesquisa, mantido apenas como referência histórica. Previsão EJR de 60 meses, decisões mensais e risco de 12 meses são horizontes distintos. Não demonstra uma estratégia validada de convergência no horizonte do artigo.'
by[10]['speech']='Este bloco fica apenas como referência exploratória. Combinamos três regras próprias, com pesos iguais: ajuste de tamanho, permissão de entrada e saída de lotes. O sinal EJR olha cinco anos, mas as decisões são mensais e o modelo adicional de risco olha doze meses. Nenhuma dessas regras foi derivada como estratégia de longo prazo no artigo. O resultado serve para documentar o que testamos, sem substituir a avaliação econômica no horizonte previsto.'
by[14]['core']='As carteiras são referências exploratórias: falta validar a ligação entre previsão de longo prazo e execução econômica.'
by[15]['core']='A relação histórica foi parcialmente replicada. As aplicações mensais posteriores não validam uma estratégia no horizonte do artigo.'
by[15]['reading']='Separe a evidência preditiva do resultado das carteiras. Encerre sem apresentar os filtros mensais como a conclusão econômica do artigo.'
by[15]['speech']='A relação histórica da aula aparece na replicação parcial, e os testes preditivos variam por moeda e horizonte. As carteiras posteriores ficam como referências exploratórias. A conversão de uma previsão de cinco anos em sinal mensal e os filtros de doze meses não demonstram a captura do ajuste de longo prazo. Portanto, o trabalho ainda não estabelece uma estratégia econômica validada no horizonte do artigo.'
by[15]['qa']='O que falta para a conclusão econômica? Um desenho de investimento explicitamente alinhado ao horizonte previsto, com regras de manutenção e saída justificadas, financiamento, custos e comparação adequada.'
(H/'content_v5.json').write_text(json.dumps(C,ensure_ascii=False,indent=2),encoding='utf-8')
(H/'data_v5.json').write_bytes((H/'data_v4.json').read_bytes())
t=(H/'build/deck_v4.mjs').read_text(encoding='utf-8').replace('_v4','_v5')
repl={
 "foot(s,'Escopo deste trabalho: relação preditiva e exemplo da aula. O modelo estrutural completo do artigo fica fora da replicação.');":"foot(s,'EJR, seção 3.3: ganho agregado acima de 2 anos; destaque para 4 e 6 anos. Replicação parcial da relação preditiva, sem o DSGE.');",
 "slide(5,'Mesmos tipos de ativos e custos. O que muda é o sinal para escolher as moedas.')":"slide(5,'Aplicação própria: previsão de 60 meses convertida em sinal mensal. Não é uma carteira do artigo.')",
 "slide(6,'Retornos líquidos em dólar, março de 2010 a agosto de 2026.')":"slide(6,'Mar/2010–ago/2026. Este backtest testa a aplicação mensal; não rejeita a previsão de longo prazo.')",
 "slide('initial_wealth','Mesmas regras do slide anterior. Patrimônio líquido em USD, base 100.')":"slide('initial_wealth','Patrimônio líquido em USD, base 100. Sem permanência obrigatória de cinco anos.')",
 "slide(10,'Três módulos, combinados em partes iguais. O carry continua orientando as pontas.')":"slide(10,'Regras próprias: decisões mensais e risco de 12m. Não validam a convergência prevista em 60m.')",
 "slide(11,'Janela comum: abril de 2018 a agosto de 2026. Retornos líquidos em dólar.')":"slide(11,'Abr/2018–ago/2026. Resultado histórico das regras próprias; não é validação econômica do artigo.')",
 "slide('tenure','Variação do prazo máximo dos lotes do módulo C. Resultados da combinação inteira.')":"slide('tenure','Sensibilidade de regras próprias: lotes de 6–24m. Não é um teste de convergência em cinco anos.')",
 "slide(12,'Patrimônio líquido em dólar, base 100 antes de abril de 2018.')":"slide(12,'Abr/2018–ago/2026. Patrimônio líquido em USD. Referência das regras próprias de exposição.')",
 "text(s,'Escolha das regras após muitos testes na mesma história.'":"text(s,'Decisões mensais não validam o ajuste previsto em cinco anos.'",
 "text(s,'A relação histórica da aula se replica.'":"text(s,'A relação histórica da aula foi parcialmente replicada.'",
 "text(s,'Commodities ajudam em alguns testes, com instabilidade.'":"text(s,'A previsão varia por moeda, horizonte e período.'",
 "text(s,'Controlar a exposição ao carry foi a hipótese mais promissora\\npara reduzir risco na amostra.'":"text(s,'As carteiras posteriores são referências exploratórias.\\nFalta validar o investimento no horizonte previsto.'",
}
for a,b in repl.items():
    assert a in t,a
    t=t.replace(a,b)
(H/'build/deck_v5.mjs').write_text(t,encoding='utf-8')
t=(H/'build_pdfs_v4.py').read_text(encoding='utf-8').replace('_v4','_v5')
a=t.index(" 'Uma moeda pode parecer barata");b=t.index("\ng.block('O que aprender primeiro'",a)
t=t[:a]+" 'A apresentação distingue a replicação parcial da relação preditiva do artigo das aplicações de carteira criadas no projeto. O sinal inicial prevê cinco anos, mas foi convertido em ritmo mensal e usado em um ranking revisto todo mês. Os filtros posteriores também incluem previsões de risco em doze meses. Seus resultados ficam apenas como referências exploratórias; não demonstram captura da convergência de longo prazo. A hipótese de investimento no horizonte previsto permanece sem validação econômica.')\n"+t[b:]
t=t.replace("'Fracasso do ranking'","'Aplicação mensal do sinal'").replace("'Melhor resultado comum'","'Referência: combinação'")
t=t.replace('Defenderia a replicação do exemplo, o fracasso transparente do ranking com previsão e a hipótese de controle de exposição. A combinação apresentou menor risco na história. Eu não defenderia arbitragem, alfa garantido ou superioridade generalizável antes de uma validação futura com regras congeladas.','Defenderia a replicação parcial da relação preditiva e a transparência dos resultados. O ranking mensal e os filtros posteriores são extensões próprias. Não demonstram a captura do ajuste de longo prazo nem uma estratégia econômica validada no horizonte do artigo.')
(H/'build_pdfs_v5.py').write_text(t,encoding='utf-8')
