"""Presentation PDF and per-slide teaching guide, from the reviewed slide content."""
from pathlib import Path
import json,html,sys
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph,Table,TableStyle,Spacer
from reportlab.lib.pagesizes import A4

R=Path(__file__).resolve().parents[1]; H=R/'presentation'; O=R/'output/pdf'
sys.stdout.reconfigure(encoding='utf-8')
C=json.loads((H/'content_v3.json').read_text(encoding='utf-8'))
for name,file in [('Arial','arial.ttf'),('ArialB','arialbd.ttf'),('ArialI','ariali.ttf')]:
    pdfmetrics.registerFont(TTFont(name,'C:/Windows/Fonts/'+file))
pdfmetrics.registerFontFamily('Arial',normal='Arial',bold='ArialB',italic='ArialI',boldItalic='ArialB')
NAVY=HexColor('#15354D'); TEAL=HexColor('#007F7B'); GRAY=HexColor('#52616B')
W,PAGEH=A4; M=46; BODYW=W-2*M
styles={
 'body':ParagraphStyle('body',fontName='Arial',fontSize=10.5,leading=13.4,textColor=NAVY,spaceAfter=6),
 'heading':ParagraphStyle('heading',fontName='ArialB',fontSize=11.3,leading=15,textColor=TEAL,spaceBefore=3,spaceAfter=3),
 'title':ParagraphStyle('title',fontName='ArialB',fontSize=23,leading=27,textColor=NAVY,spaceAfter=13),
 'core':ParagraphStyle('core',fontName='ArialB',fontSize=11.5,leading=16,textColor=TEAL,spaceAfter=13),
 'small':ParagraphStyle('small',fontName='Arial',fontSize=8.3,leading=11,textColor=GRAY,spaceAfter=5),
 'speech':ParagraphStyle('speech',fontName='ArialI',fontSize=10.5,leading=13.4,textColor=NAVY,spaceAfter=6),
}
def esc(s):return html.escape(s).replace('\n','<br/>')

# Universal PDF copy of the native PPTX, using the reviewed renderer output.
deck=canvas.Canvas(str(O/'apresentacao_macro_aula_v3.pdf'),pagesize=(960,540))
deck.setTitle(C['title']); deck.setAuthor('Projeto de Macroeconomia Aplicada')
for i,s in enumerate(C['slides'],1):
    deck.bookmarkPage(f'slide{i}');deck.addOutlineEntry(f'{i:02d}. {s["title"]}',f'slide{i}',level=0)
    deck.drawImage(str(H/f'build/rendered_v3/slide-{i:02d}.png'),0,0,960,540)
    deck.showPage()
deck.save()

class Guide:
    def __init__(self):
        self.c=canvas.Canvas(str(O/'guia_apresentacao_macro_v3.pdf'),pagesize=A4)
        self.c.setTitle('Guia de estudo e fala: câmbio real, commodities e carry')
        self.c.setAuthor('Projeto de Macroeconomia Aplicada')
        self.page=0;self.y=0;self.mapping={};self.section=''
    def new(self,title=None,key=None):
        if self.page:self.c.showPage()
        self.page+=1;self.y=PAGEH-49
        self.c.setFillColor(GRAY);self.c.setFont('Arial',8)
        self.c.drawString(M,PAGEH-26,'MACROECONOMIA APLICADA · GUIA DE ESTUDO E FALA')
        self.c.drawString(M,23,'Câmbio real, commodities e carry trade')
        self.c.drawRightString(W-M,23,str(self.page))
        if title:
            self.section=title
            if key:self.c.bookmarkPage(key);self.c.addOutlineEntry(title,key,level=0);self.mapping[key]=self.page
            self.put(title,'title')
    def put(self,text,style='body',raw=False):
        p=Paragraph(text if raw else esc(text),styles[style]);_,height=p.wrap(BODYW,1000)
        space=styles[style].spaceBefore+styles[style].spaceAfter
        if self.y-height-space<45:
            self.new(self.section+' (continuação)')
        self.y-=styles[style].spaceBefore
        p.drawOn(self.c,M,self.y-height);self.y-=height+styles[style].spaceAfter
    def block(self,title,body,style='body'):
        needed=sum(Paragraph(esc(t),styles[st]).wrap(BODYW,1000)[1]+styles[st].spaceBefore+styles[st].spaceAfter for t,st in [(title,'heading'),(body,style)])
        if self.y-needed<45:self.new(self.section+' (continuação)')
        self.put(title,'heading');self.put(body,style)
    def table(self,rows,widths=None):
        v=[[Paragraph(esc(str(t)),styles['small' if r==0 else 'body']) for t in row] for r,row in enumerate(rows)]
        table=Table(v,colWidths=widths or [BODYW/len(rows[0])]*len(rows[0]))
        table.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),HexColor('#E8EEF2')),('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),7),('RIGHTPADDING',(0,0),(-1,-1),7),('TOPPADDING',(0,0),(-1,-1),5),('BOTTOMPADDING',(0,0),(-1,-1),5),('LINEBELOW',(0,0),(-1,0),.5,GRAY)]))
        _,height=table.wrap(BODYW,1000)
        if self.y-height<45:self.new(self.section+' (continuação)')
        table.drawOn(self.c,M,self.y-height);self.y-=height+12
    def end(self):self.c.save()

g=Guide()
g.new('Como entender e apresentar o trabalho',key='inicio')
g.put('Câmbio real, commodities e carry trade','core')
g.put('Este guia acompanha os 17 slides principais e os dois slides de apoio. O roteiro soma 19 minutos, deixando aproximadamente um minuto de margem até o limite de 20. Os tempos são metas de ensaio, não uma duração garantida de leitura.')
g.block('A história do trabalho em linguagem simples',
 'Uma moeda pode parecer barata quando sua cotação é comparada aos preços dos dois países. O artigo mostra que essa informação pode se relacionar com o câmbio futuro. A replicação brasileira recupera a relação da aula. Mas a primeira tentativa de usar a previsão para escolher posições de carry rendeu menos. Commodities e informações de comércio melhoram alguns testes, com resultados instáveis. O uso mais promissor na história foi controlar o tamanho e a permanência das posições, assumindo menos exposição. Ainda falta uma validação independente dessas regras.')
g.block('O que aprender primeiro',
 'Comece pelos slides 2 e 5: câmbio real e mecânica do carry. Depois leia os slides 3 e 4 para separar ajuste histórico de previsão. Só então passe aos slides 8–10, que tratam das extensões sem carteiras. Nos slides 11–16, concentre-se nas decisões econômicas e nos limites da evidência. A conclusão do slide 17 precisa fazer sentido sem nenhuma fórmula.')
g.block('Como usar cada página',
 'A ideia central é o que a turma deve levar do slide. Os conceitos explicam o que você precisa entender. A leitura indica como apontar o gráfico ou a tabela. A fala sugerida é uma base para ensaiar com suas palavras. O cuidado evita interpretações incorretas. A pergunta provável prepara uma resposta curta. Você não deve ler todo este guia durante a apresentação.')
g.block('O que pode ficar para as perguntas',
 'As equações completas, os percentis dos filtros, os detalhes de custo, a diferença entre controle retrospectivo e executável, e a correção por múltiplos testes. Os slides 18 e 19 estão no fim para esse apoio. Não os apresente após o fechamento, a menos que alguém peça.')
g.block('Uma resposta honesta se você se perder',
 '“Esse é um resultado histórico da regra testada. A comparação usa as mesmas datas e os mesmos tipos de custos, mas ainda não demonstra uma vantagem que se mantenha fora dessa história.”')

g.new('Roteiro e controle do tempo',key='roteiro')
elapsed=0;rows=[['Slide','Assunto','Fala','Relógio ao final']]
short=['Pergunta','Ideia do artigo','Replicação brasileira','Previsão em seis horizontes','Como funciona o carry','Fracasso do ranking','Patrimônio do ranking','Commodities e comércio','Previsão nominal ampliada','Previsão real ampliada','Regras de exposição','Melhor resultado comum','Prazos dos lotes','Patrimônio da combinação','Decomposição e episódios','Limitações','Conclusão']
for i,s in enumerate(C['slides'][:17]):
    elapsed+=s['seconds'];rows.append([i+1,short[i],f"{s['seconds']//60}:{s['seconds']%60:02d}",f'{elapsed//60:02d}:{elapsed%60:02d}'])
g.table(rows,[40,285,65,113])
g.block('Se o tempo apertar',
 'No slide 3, leia apenas os eixos e a inclinação. No 9, destaque somente o erro 0,890 na janela completa e 1,630 na recente. No 12, priorize retorno, queda máxima e exposição. No 13, compare os prazos sem ler todas as células. No 15, explique a troca entre juros e câmbio sem detalhar os episódios. Preserve os limites e a conclusão. Não acelere as definições dos slides 2 e 5: elas sustentam o restante.')
g.block('Ensaio sugerido',
 'Faça uma primeira passagem com o guia aberto. Na segunda, use apenas os slides e um cronômetro. Anote o relógio ao terminar os slides 6, 11 e 16. Na terceira, peça que alguém interrompa com duas perguntas simples: “o que está sendo previsto?” e “o retorno inclui juros?”. A fala deve continuar clara mesmo com essas interrupções.')

labels=[('concepts','Conceitos que você precisa dominar','body'),('reading','Como ler o slide','body'),('training','Treinamento, previsão e avaliação','body'),('speech','Fala sugerida','speech'),('caution','Cuidado com a interpretação','body'),('qa','Pergunta provável','body'),('transition','Transição','speech')]
for i,s in enumerate(C['slides'],1):
    g.new(f'Slide {i:02d} · {s["title"]}',key=f'slide{i}')
    for st in ['body','speech']:
        styles[st].leading=13.0 if i==4 else 13.4
        styles[st].spaceAfter=3 if i==4 else 6
    g.put(f"Tempo sugerido: {s['seconds']//60} min {s['seconds']%60:02d} s" if s['seconds'] else 'Apoio para perguntas. Fora dos 19 minutos.','small')
    g.put(s['core'],'core')
    for field,title,sty in labels:
        if s.get(field):g.block(title,s[field],sty)
    g.put('Fontes do slide: '+'; '.join(s['sources']),'small')

g.new('Glossário: câmbio e comércio',key='glossario1')
for title,body in [
 ('EJR','Eichenbaum, Johannsen e Rebelo, autores do artigo de 2021. A sigla também nomeia a regressão preditiva inspirada no artigo nesta implementação.'),
 ('Cotação nominal e sinal','S é moeda local por dólar. S subir significa dólar mais caro e moeda local depreciada. Para quem comprou a moeda local com financiamento em dólar, essa depreciação prejudica o retorno.'),
 ('Câmbio real','Q = S × P_US / P_local. Em logaritmos, q = log S + log P_US − log P_local. Um q maior indica depreciação real da moeda local. “Barata” significa relativamente à referência escolhida, sem garantir valor justo ou convergência.'),
 ('Por que usamos logaritmos','O log transforma produtos em somas. A diferença de logs aproxima a variação percentual quando ela é pequena. Uma diferença de log de 0,10 corresponde exatamente a aproximadamente 10,52%, e não exatamente 10%.'),
 ('Termos de troca','Razão entre o índice de preços de exportação e o índice de preços de importação. Exemplo: preço exportado sobe 20% e importado sobe 10%. A melhora é 1,20/1,10 − 1 = aproximadamente 9,1%.'),
 ('Composição comercial','Distribuição do comércio entre tipos de produtos. Participações medidas em valor podem mudar por preços ou quantidades. Por isso, sua mudança não identifica sozinha uma transformação estrutural da economia.'),
 ('Proxy comercial','Medida aproximada da exposição a preços de commodities, combinando pesos comerciais e índices de preços. Cobre apenas parte do comércio. Na extensão, os termos de troca agregados anuais também foram testados separadamente.'),
 ('Moedas e numerário','BRL: real. EUR: euro. JPY: iene. GBP: libra. CAD: dólar canadense. SEK: coroa sueca. USD: dólar americano. O numerário é a unidade em que o retorno é medido. Para informações comerciais do euro, o projeto usa a Alemanha como proxy, o que limita a interpretação para toda a área do euro.')]:g.block(title,body)

g.new('Glossário: previsão e investimento',key='glossario2')
for title,body in [
 ('Carry e sinal cambial','O carry por juros escolhe posições pelo diferencial de taxas. O carry com sinal cambial acrescenta uma expectativa de apreciação ou depreciação à decisão. As duas carteiras continuam sujeitas a juros e câmbio no retorno realizado.'),
 ('RMSE e erro relativo','RMSE é a raiz da média dos quadrados dos erros. A razão RMSE_modelo/RMSE_referência é menor que 1 quando o modelo melhora a previsão. O número não é retorno, probabilidade nem R².'),
 ('R² dentro e fora da amostra','Dentro da amostra, R² descreve quanto o ajuste explica do alvo. Fora da amostra, R² pode ser definido como 1 − erro quadrático do modelo/erro quadrático da referência. Pode ser negativo. Não se compara mecanicamente o R² da dispersão brasileira de oito anos com o erro do painel de cinco anos.'),
 ('CAGR e média de excesso','CAGR é o crescimento anual composto equivalente do patrimônio. O excesso médio anualizado é 12 vezes a média mensal do retorno líquido menos o caixa USD. São estatísticas diferentes e os componentes da atribuição não somam o CAGR.'),
 ('Volatilidade e Sharpe','A volatilidade anualiza a dispersão mensal com a raiz de 12. O Sharpe usa média do excesso dividida pelo desvio-padrão do excesso, também anualizado. Ele resume remuneração por risco, mas não descreve sozinho perdas extremas ou dependência temporal.'),
 ('Drawdown e exposição','Drawdown é a perda desde o pico do patrimônio. A exposição bruta soma os valores absolutos das pontas. Duas compras de 25% e duas vendas de 25% geram 100% bruto e zero líquido. Zero líquido não significa ausência de risco cambial.'),
 ('Coorte, caixa e colateral','Uma coorte é o lote aberto em um mês. No módulo de permanência, lotes têm orçamento limitado e prazo máximo de 12 meses. Colateral é o capital que sustenta as posições. O caixa USD desse capital recebe juros mesmo quando a exposição diminui.'),
 ('Ponto percentual e ponto-base','De 4% para 5% há aumento de 1 ponto percentual ou 25% em termos relativos. Um ponto-base corresponde a 0,01 ponto percentual. Dez pontos-base são 0,10%.')]:g.block(title,body)

g.new('Perguntas de metodologia e defesa',key='defesa')
for title,body in [
 ('“O professor pediu identificação. Qual é a sua?”','A pergunta é preditiva. O exercício não estima um efeito causal de commodities ou política monetária e não oferece uma variação exógena para isso. A disciplina é temporal: estimar com informação admissível e avaliar erros futuros contra referências simples. A extensão também relata limites de amostra e seleção.'),
 ('“Por que o R² alto não produziu uma boa carteira?”','Porque ajuste histórico, previsão fora da amostra e retorno líquido são objetos diferentes. O gráfico brasileiro usa oito anos e a carteira utiliza informação de cinco anos em um painel. Mesmo uma previsão útil pode ser lenta, instável entre países ou insuficiente para compensar câmbio adverso, juros e custos ao longo do caminho.'),
 ('“Vocês realmente previram uma mudança estrutural no comércio?”','Tentamos prever componentes da mudança comercial, mas a previsão da composição não superou a persistência no teste correspondente. O ganho de risco da carteira não autoriza afirmar que uma transformação estrutural foi identificada ou prevista corretamente.'),
 ('“Quanto houve de pesquisa até chegar à combinação?”','Houve vários relatórios e tentativas. A combinação usa aprendizados dessa exploração, inclusive dos fracassos. Pesos iguais evitam uma otimização adicional, mas não tornam a escolha dos módulos independente. A correção por testes múltiplos cobre apenas a grade principal, não toda a história de pesquisa.'),
 ('“Qual é a diferença entre vazamento e seleção?”','Vazamento seria usar no sinal de janeiro um dado conhecido apenas depois. Seleção seria testar muitas regras e escolher a que funcionou melhor em uma história já examinada. O projeto controla o primeiro por calendário e testes de integridade, mas ainda enfrenta o segundo, além de revisões das bases.'),
 ('“Então qual resultado você defenderia?”','Defenderia a replicação do exemplo, o fracasso transparente do ranking com previsão e a hipótese de controle de exposição. A combinação apresentou menor risco na história. Eu não defenderia arbitragem, alfa garantido ou superioridade generalizável antes de uma validação futura com regras congeladas.')]:g.block(title,body)

g.new('Referências e localização dos resultados',key='referencias')
g.block('Referência acadêmica',
 'Eichenbaum, M. S.; Johannsen, B. K.; Rebelo, S. T. (2021). Monetary Policy and the Predictability of Nominal Exchange Rates. Review of Economic Studies, 88, 192–228. DOI: 10.1093/restud/rdaa024.')
g.put('<link href="https://doi.org/10.1093/restud/rdaa024" color="#007F7B">Abrir o artigo pelo DOI</link>','body',raw=True)
g.block('Material da disciplina',
 'Macroeconomia Aplicada, EPGE/FGV, 2026.2. Professor Marcos Sonnervig. Aula 8 e instruções de trabalho disponíveis na pasta Macro_Aplicada_2026_shared. O estudo replica a relação preditiva e o exemplo brasileiro, não o modelo estrutural completo do artigo.')
g.table([['Slides','Resultado de origem'],['3–7','Relatório original: relatorio.pdf. Tabelas em output/tables.'],['8–9','Relatório terciário: relatorio_terciario.pdf. Tabelas em third/tables.'],['10','Extensão comercial: relatorio_termos_troca.pdf. Tabelas em trade_extension/tables.'],['11–16 e 19','Síntese: relatorio_sintese.pdf. Tabelas em synthesis/tables.'],['18','Equações e calendário em src/models.py e third/engine.py.']],[85,418])
g.block('Dados e limites de disponibilidade',
 'As séries cambiais, preços ao consumidor e taxas curtas vêm das bases oficiais já documentadas no relatório original. A extensão usa preços de commodities e informações comerciais do Banco Mundial, com defasagens e proxies descritas nos relatórios correspondentes. Séries revisadas e taxas oficiais não substituem um histórico completo de vintages ou cotações executáveis. As datas dos alvos e as janelas de avaliação constam nos slides.')
g.block('Uma delimitação importante',
 'A apresentação seleciona resultados já calculados no projeto para explicar uma pergunta em 19 minutos. Os estudos completos também incluem commodities como variável prevista, outros testes de risco e aplicações a ativos em dólar. Esses blocos não são necessários para sustentar a história apresentada e permanecem nos relatórios originais.')
g.end()
(H/'build/guide_pages_v3.json').write_text(json.dumps({'pages':g.page,'mapping':g.mapping},ensure_ascii=False,indent=2),encoding='utf-8')

# Editable text companion, sharing the same content as the PDF.
md=['# Guia de apresentação: câmbio real, commodities e carry','',
    '17 slides principais, 19 minutos previstos, 2 slides de apoio.','']
for i,s in enumerate(C['slides'],1):
    md.extend([f'## Slide {i:02d} — {s["title"]}','',f'Tempo: {s["seconds"]} segundos.','',s['core'],''])
    for field,title,_ in labels:
        if s.get(field):md.extend([f'### {title}','',s[field],''])
    md.extend(['Fontes: '+'; '.join(s['sources']),''])
(H/'guia_slides_v3.md').write_text('\n'.join(md),encoding='utf-8')
print('PDF slides: 19 pages. Guide:',g.page,'pages.')
print(json.dumps(g.mapping,ensure_ascii=False))
