"""PDF projection copy and matching teaching guide for the revised presentation."""
from pathlib import Path
import json
R=Path(__file__).resolve().parents[1];H=R/'presentation'
# Reuse the project's established ReportLab typography and pagination class only.
old=(H/'build_pdfs_v6.py').read_text(encoding='utf-8')
prefix=old[:old.index('# Universal PDF copy')].replace('content_v6','content_v8')
klass=old[old.index('class Guide:'):old.index('\ng=Guide()')].replace('guia_apresentacao_macro_v6','guia_apresentacao_macro_v8')
exec(prefix+klass,globals())
O.mkdir(exist_ok=True)
deck=canvas.Canvas(str(O/'apresentacao_macro_aula_v8.pdf'),pagesize=(960,540))
deck.setTitle(C['title']);deck.setAuthor('Projeto de Macroeconomia Aplicada')
for i,s in enumerate(C['slides'],1):
    deck.bookmarkPage(f'slide{i}');deck.addOutlineEntry(f'{i:02d}. {s["title"]}',f'slide{i}',level=0)
    deck.drawImage(str(H/f'build/rendered_v8/slide-{i:02d}.png'),0,0,960,540)
    deck.showPage()
deck.save()
g=Guide();g.new('Como estudar e apresentar o trabalho',key='inicio')
g.put(C['title'],'core')
g.put('A apresentação principal tem 18 slides e roteiro de 17 minutos e 15 segundos. Os slides 19 a 25 são apoio para perguntas e ficam fora desse tempo. Termine a fala no slide 18. Os tempos são metas de ensaio, não uma garantia de duração.')
g.block('A história em um parágrafo','O artigo motiva prever a variação do câmbio nominal em horizontes longos usando o câmbio real. A replicação recupera uma relação histórica forte e encontra desempenho preditivo desigual por moeda. A primeira aplicação mensal ao carry falha. Termos de troca melhoram a previsão brasileira, mas não melhoram as carteiras testadas. A melhor alternativa do trio selecionado usa juros mais EJR, risco de 60 meses e escolha anual. Países e modelos foram escolhidos na história já analisada, então o resultado é exploratório.')
g.block('As distinções que sustentam a apresentação','1. Ajuste na amostra e previsão com informação passada são avaliações diferentes.\n2. Horizonte de previsão de 60 meses e intervalo de escolha de 12 ou 60 meses são decisões diferentes.\n3. O retorno realizado sempre inclui juros e câmbio. O que muda é o sinal usado para escolher pesos.\n4. Exposição líquida zero é igualdade entre compras e vendas em dólares, sem eliminar risco cambial.\n5. Uma seleção retrospectiva de países não se torna conhecida em tempo real só porque cada regressão usou dados passados.')
g.block('Cores dos gráficos finais','Azul escuro: juros. Azul claro: juros + EJR. Laranja: juros + EJR + termos de troca. Cinza: caixa USD. A cor representa o sinal. Os títulos dos painéis representam o método e o intervalo de escolha.')
g.block('Como ler as tabelas finais','As linhas estão ordenadas do maior para o menor retorno anual composto. Sinal, método e intervalo entre escolhas aparecem em colunas próprias, seguidos por retorno, Sharpe e queda máxima. Exemplo: EJR, máximo Sharpe, escolha a cada 12 meses, retorno 3,29% a.a., Sharpe 0,393 e queda máxima de 13,31%. Esses indicadores vêm dos mesmos retornos mensais líquidos que geram as curvas de patrimônio.')
g.block('Uma resposta segura se surgir uma dúvida','“O que posso afirmar é o desempenho histórico da regra e desta amostra. Para dizer que a vantagem persiste, preciso congelar a regra e avaliar dados novos, com custos executáveis.”')
g.new('Roteiro e controle do tempo',key='roteiro');rows=[['Slide','Assunto','Fala','Acumulado']];elapsed=0
short=['Pergunta','Artigo e mecanismo','Relação histórica','Erros por horizonte','Carry e retorno','Primeira aplicação','Termos de troca','Painel de seis moedas','Recorte do trio','Ajuste histórico','Previsão recursiva','Regras finais','Curvas: seis moedas','Tabela: seis moedas','Curvas: trio','Tabela: trio','Custos e risco','Conclusão']
for i,s in enumerate(C['slides'][:18]):
    elapsed+=s['seconds'];rows.append([i+1,short[i],f"{s['seconds']//60}:{s['seconds']%60:02d}",f'{elapsed//60}:{elapsed%60:02d}'])
g.table(rows,[38,305,64,96])
g.block('Se o tempo apertar','Nos slides 10 e 11, compare apenas o Brasil e mencione que euro e Canadá não repetem o ganho. Nas tabelas 14 e 16, explique as colunas e destaque a primeira linha, sem ler todas. Preserve o desenho do teste, os gráficos e a conclusão. Os detalhes das transformações e as regras de exposição estão no apoio.')
g.block('Ensaio','Faça uma passagem só com os slides e um cronômetro. Ao final do slide 6, a meta é 5min30s. Ao final do slide 12, 11min30s. Termine o slide 18 em 17min15s. Use a margem até 20 minutos para transições e uma pergunta curta.')
labels=[('concepts','Conceitos que você precisa dominar','body'),('reading','Como ler o slide','body'),('training','Treinamento, previsão e avaliação','body'),('speech','Fala sugerida','speech'),('caution','Cuidado com a interpretação','body'),('qa','Pergunta provável','body'),('transition','Transição','speech')]
for i,s in enumerate(C['slides'],1):
    g.new(f'Slide {i:02d} · {s["title"]}',key=f'slide{i}')
    for st in ['body','speech']:
        styles[st].leading=13.0 if i==4 else 13.4
        styles[st].spaceAfter=3 if i==4 else 6
    g.put(f"Tempo sugerido: {s['seconds']//60} min {s['seconds']%60:02d} s" if s['seconds'] else 'Referência para perguntas. Fora do roteiro principal.','small')
    g.put(s['core'],'core')
    for key,title,sty in labels:
        if s.get(key):g.block(title,s[key],sty)
    g.put('Fontes: '+'; '.join(s['sources']),'small')
g.new('Glossário para as perguntas',key='glossario')
for title,body in [
 ('EJR','Eichenbaum, Johannsen e Rebelo (2021), Monetary Policy and the Predictability of Nominal Exchange Rates, Review of Economic Studies, 88, 192–228. No projeto, EJR também nomeia a regressão preditiva inspirada no artigo. A replicação é parcial, sem reproduzir todo o modelo DSGE.'),
 ('Cotação e sinal','S é moeda local por dólar. S subir indica depreciação da moeda local. Δlog(S) positiva significa dólar mais caro. Quem compra a moeda local perde com esse movimento, razão pela qual a expectativa da carteira subtrai a depreciação nominal prevista.'),
 ('Câmbio real','Q = S × P_US / P_local. Em log, q = log S + log P_US − log P_local. O desvio em relação à média histórica disponível é um regressor. Ele não garante um valor justo fixo ou uma convergência futura.'),
 ('Termos de troca','Razão entre preços de exportação e importação. A medida agregada usada vem de deflatores de bens e serviços nas contas nacionais. É diferente de preços de commodities ponderados por uma cesta comercial. Para EUR, a informação comercial usa Alemanha como aproximação.'),
 ('RMSE relativo','Erro quadrático médio com raiz dividido pelo erro de supor nenhuma mudança na cotação. 0,628 significa 62,8% do RMSE dessa referência, não uma probabilidade de acerto. A redução de 0,802 para 0,628 é de aproximadamente 21,7% em relação ao EJR.'),
 ('Origem e alvo','Origem é a data em que fazemos a previsão. Alvo é a data futura em que medimos a mudança prevista. Em janeiro de 2010, h=60 aponta para janeiro de 2015. Uma origem só entra no treino depois que seu alvo já foi observado.'),
 ('Seleção retrospectiva','Escolher países ou transformações por seus resultados na mesma história que será usada para avaliar carteiras. As regressões podem respeitar o calendário e, ainda assim, a estratégia completa ter viés de seleção.'),
 ('Máximo Sharpe e risco de 60m','O algoritmo escolhe pesos para maximizar retorno esperado em excesso ao caixa em relação ao risco. Aqui a matriz de risco usa retornos acumulados de 60 meses, com história até t−1. O Sharpe mostrado na tabela é um resumo anualizado do retorno realizado, não o valor da função objetivo.'),
 ('Caixa USD','Aplicação curta em dólar com a taxa americana usada na base. Serve de caixa e referência para medir excesso de retorno. Não é uma posição em bolsa americana.'),
 ('12m/60m na carteira final','Intervalo entre escolhas de moedas e pesos. Entre escolhas, os pesos-alvo recebem manutenção mensal. Isso difere do prazo máximo dos lotes das regras de exposição no apêndice, que permitem entradas mensais e saídas antecipadas.'),
 ('Custo em pontos-base','Um ponto-base é 0,01 ponto percentual. Dez pb equivalem a 0,10% do valor negociado. O custo entra sobre a negociação, incluindo ajustes e liquidação. O spread de financiamento entra sobre o notional vendido ao longo do tempo.'),
 ('Lucro cambial e carrego','Para um ativo comprado, o retorno em USD combina multiplicativamente o rendimento local com a variação da moeda. Subtrair financiamento e custos completa o cálculo. A soma de juros e valorização é uma aproximação didática, não a identidade exata usada na simulação.')]:
    if title=='Seleção retrospectiva':g.new('Glossário: carteiras e limites',key='glossario2')
    g.block(title,body)
g.new('Mapa das fontes e limites da evidência',key='fontes')
g.block('Artigo e aula','Eichenbaum, Johannsen e Rebelo (2021), Review of Economic Studies, DOI 10.1093/restud/rdaa024. A apresentação retoma a relação ilustrada na aula 8 e distingue a replicação da aplicação de carteira criada neste projeto.')
g.block('Previsão com termos de troca','ejr_trade/tables/metrics.csv contém o painel completo. ejr_trade_selected/tables/metrics.csv contém o trio e as transformações. in_sample.csv e predictions.csv.gz separam ajuste e previsão recursiva. pooling_diagnostics.csv mostra a sensibilidade ao peso do Brasil.')
g.block('Carteiras finais','horizon_tests/tables/with_terms_of_trade.csv e restricted_table.csv são as tabelas finais. returns.csv.gz, with_tot_returns.csv.gz e restricted_returns.csv.gz fornecem os retornos mensais dos gráficos. Os arquivos de protocolo documentam restrições, custos, atrasos e a natureza retrospectiva da seleção.')
g.block('Regras de exposição','synthesis/model.py e synthesis/tables documentam os resultados de referência no apêndice. A combinação tem uma janela de 2018–2026 e regras próprias. Não é a mesma experiência das carteiras finais de 2010–2025.')
g.block('Limites que devem permanecer explícitos','Países e modelos foram escolhidos usando a história já avaliada. Séries macroeconômicas revisadas não equivalem a dados realmente disponíveis em cada data passada. Custos são hipóteses. Previsões longas e retornos de 60 meses se sobrepõem. O backtest final tem só três blocos de cinco anos. Não há identificação causal, arbitragem demonstrada ou garantia de retorno futuro.')
g.end()
(H/'build/guide_pages_v8.json').write_text(json.dumps(dict(pages=g.page,mapping=g.mapping),indent=2))
print('PDF slides:',len(C['slides']),'Guide pages:',g.page)
