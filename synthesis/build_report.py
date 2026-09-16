"""Research synthesis with executable policies, economic attribution and negative tests."""
from pathlib import Path
import os,json,re
R=Path(__file__).resolve().parents[1];H=R/'synthesis';F=H/'figures'
os.environ['MPLCONFIGDIR']=str(R/'tmp/matplotlib')
import numpy as np,pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
def read(n):return pd.read_csv(H/'tables'/(n+'.csv'))
M=read('metrics');V=read('robustness');EC=read('exposure_controls');A=read('attribution');I=read('economic_intervals');RI=read('risk_intervals');S=read('selection_metrics');HM=read('hedge_metrics');HI=read('hedge_intervals');J=read('search_adjustment');EP=read('episodes');REF=read('hurdle_refinement');PAIR=read('pair_strategy_metrics');PM=read('pair_prediction_metrics');VAL=read('validation')
O=pd.read_csv(H/'tables/returns.csv.gz');HO=read('hedge_returns')
labels={'Carry':'Carry puro','EJR_rank':'Ranking EJR','EJR_size':'Tamanho EJR','EJR_gate':'Filtro EJR','Size_structure':'Tamanho + composição','Gate_price':'Filtro + preços','Cohort_base':'Coortes sem saída','Cohort_risk':'Coortes + risco','Integrated_cohort':'Coortes integradas','All_filters':'Todos os filtros','Commodity_blend':'Previsão comercial 50%','Equal_modules':'Média de três módulos','Core_satellite':'Núcleo carry + média','Two_modules':'Média de dois módulos','Cash':'Caixa USD','Cohort_long':'Coortes desde 2013'}
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,'axes.spines.right':False,'axes.grid':True,'grid.alpha':.15,'text.color':'#163447','axes.labelcolor':'#163447','pdf.fonttype':42,'savefig.bbox':'tight','axes.prop_cycle':matplotlib.cycler(color=['#156078','#d28a2f','#728b4e','#a65269','#807498'])})
def fs(n,f):f.savefig(F/(n+'.pdf'));f.savefig(F/(n+'.png'),dpi=170);plt.close(f)
def num(x,d=2):return '--' if pd.isna(x) else f'{float(x):.{d}f}'.replace('.',',')
def pct(x):return num(100*x)+r'\%'
def esc(x):return str(x).replace('_',r'\_').replace('%',r'\%').replace('&',r'\&')
def tab(head,rows,align=None,size=r'\small'):
    cell=lambda x:re.sub(r'(?<!\\)%',r'\\%',str(x))
    return size+r'\begin{center}\begin{tabular}{'+(align or 'l'+'r'*(len(head)-1))+r'}\toprule '+' & '.join(head)+r'\\\midrule '+'\n'+'\n'.join(' & '.join(cell(x) for x in r)+r'\\' for r in rows)+r'\bottomrule\end{tabular}\end{center}\normalsize'+'\n'
def fig(n,caption,w='.98'):return r'\begin{figure}[H]\centering\includegraphics[width='+w+r'\linewidth]{figures/'+n+r'.pdf}\caption{'+caption+r'}\end{figure}'
def get(n,w='common',p='all'):return M[(M.name==n)&(M.window==w)&(M.period==p)].iloc[0]
def vr(n,v):return V[(V.name==n)&(V.variant==v)&(V.period=='all')].iloc[0]
def path(n):
    a=O[(O.name==n)&(O.window=='common')].sort_values('month');return pd.PeriodIndex(a.month,freq='M').to_timestamp(),a
f,ax=plt.subplots(2,1,figsize=(9,5.1),sharex=True)
for n in ['Carry','Equal_modules','Core_satellite','Cohort_risk']:
    d,a=path(n);v=np.r_[1,np.cumprod(1+a.net.to_numpy())];ax[0].plot(d,v[1:],label=labels[n]);ax[1].plot(d,100*(v/np.maximum.accumulate(v)-1)[1:])
ax[0].set_ylabel('Patrimônio em USD, início = 1');ax[0].legend(ncol=2,fontsize=8);ax[1].set(ylabel='Queda desde o pico, %',xlabel='Mês do retorno');f.tight_layout();fs('wealth',f)
f,ax=plt.subplots(figsize=(9,3.4))
for n in ['Carry','EJR_size','EJR_rank','Size_structure','Gate_price','Cohort_risk','Equal_modules','All_filters','Core_satellite']:
    offsets={'Carry':(8,12),'EJR_size':(8,-13),'EJR_rank':(6,5),'Size_structure':(7,11),'Gate_price':(-84,-15),'Cohort_risk':(-15,24),'Equal_modules':(-86,13),'All_filters':(8,-16),'Core_satellite':(10,-13)}
    a=get(n);ax.scatter(a.vol*100,a.mean_excess*100,s=40);ax.annotate(labels[n],(a.vol*100,a.mean_excess*100),xytext=offsets[n],textcoords='offset points',fontsize=8,bbox=dict(facecolor='white',edgecolor='none',alpha=.85,pad=1),arrowprops=dict(arrowstyle='-',color='#94a3b8',lw=.6))
ax.set(xlabel='Volatilidade anual, %',ylabel='Excesso líquido médio, % a.a.');ax.margins(.2);f.tight_layout();fs('risk_return',f)
f,axes=plt.subplots(1,2,figsize=(9,3.4))
for ax,components,title in zip(axes,[['FX','Interest','Interaction','Borrow','Trading'],['BRL','EUR','JPY','GBP','CAD','SEK']],['Decomposição contábil','Contribuição por moeda']):
    a=A[(A.window=='common')&(A.name=='Equal_modules')].set_index('component');ax.bar(range(len(components)),[100*a.loc[c,'annual'] for c in components]);ax.set_xticks(range(len(components)),['Câmbio','Juros','Interação','Emprést.','Custos'] if components[0]=='FX' else components,rotation=15);ax.axhline(0,color='gray',lw=.6);ax.set(title=title,ylabel='Contribuição, p.p. a.a.')
f.tight_layout();fs('attribution',f)
f,ax=plt.subplots(figsize=(9,3.1))
for n in ['Carry','Equal_modules','Cohort_risk','Gate_price']:
    d,a=path(n);ax.plot(d,a.exposure,label=labels[n])
ax.set(ylabel='Exposição bruta / patrimônio',xlabel='Mês do retorno');ax.legend(fontsize=8,ncol=2);f.tight_layout();fs('exposure',f)
f,ax=plt.subplots(figsize=(9,3.3));episodes=['2018','2019','2020_2021','2022','2023_2026'];xx=np.arange(len(episodes));a=EP[EP.name=='Equal_modules'].set_index('episode')
ax.bar(xx-.18,[100*a.loc[e,'excess'] for e in episodes],.36,label='Média dos módulos');ax.bar(xx+.18,[100*a.loc[e,'base_excess'] for e in episodes],.36,label='Carry');ax.set_xticks(xx,['2018 parcial','2019','2020-2021','2022','2023-ago/26']);ax.set_ylabel('Excesso médio anualizado, %');ax.legend();f.tight_layout();fs('episodes',f)
vs=['Base','q70','q90','Gate1pct','Gate3pct','Tenure6','Tenure24','NoBRL','NoEUR','cost4_borrow50_lag1','cost1_borrow300_lag1','cost1_borrow50_lag2']
f,ax=plt.subplots(figsize=(9,3.6));vals=np.array([[vr(n,v).sharpe for v in vs] for n in ['Carry','Cohort_risk','Equal_modules','Two_modules']]);im=ax.imshow(vals,aspect='auto',cmap='YlGnBu',vmin=.3,vmax=1.5)
ax.set_xticks(range(len(vs)),['Base','Corte70','Corte90','Filtro1%','Filtro3%','6 meses','24 meses','Sem BRL','Sem EUR','Custo 4x','Spread 300','Atraso +1'],rotation=35,ha='right');ax.set_yticks(range(4),['Carry','Coortes/risco','Média 3','Média 2']);ax.grid(False)
for i in range(4):
    for j in range(len(vs)):ax.text(j,i,f'{vals[i,j]:.2f}',ha='center',va='center',fontsize=7,color='white' if vals[i,j]>1.1 else '#17384b')
f.tight_layout();fs('robustness',f)
f,ax=plt.subplots(figsize=(9,3.1));a=S[(S.family=='long')&(S.history==36)];xx=np.arange(len(a));ax.bar(xx,a.ce5*100);ax.set_xticks(xx,['Seleção passada','Média fixa','Carry','Melhor ex post']);ax.set_ylabel('Certeza equivalente excedente, % a.a.');f.tight_layout();fs('selection',f)
f,axes=plt.subplots(1,2,figsize=(9,3.4),sharey=False)
for ax,asset in zip(axes,['BIL','SPY']):
    for n,label in [('Unhedged','Sem hedge'),('Half','Hedge 50%'),('EJR_FX','EJR gradual'),('Equal_signals','Média de sinais')]:
        a=HO[(HO.asset==asset)&(HO.name==n)].sort_values('month');ax.plot(pd.PeriodIndex(a.month,freq='M').to_timestamp(),np.cumprod(1+a.net.to_numpy()),label=label)
    ax.set(title=asset,ylabel='Patrimônio em BRL, início = 1');ax.legend(fontsize=7)
f.tight_layout();fs('hedge_wealth',f)
f,ax=plt.subplots(figsize=(9,3.2));a=I[(I.control=='base')&(I.block==12)&(I.gamma==5)&I.name.isin(['Equal_modules','Cohort_risk','Size_structure','Commodity_blend'])].copy();xx=np.arange(len(a));ax.errorbar(100*a.ce_difference,xx,xerr=[100*(a.ce_difference-a.low),100*(a.high-a.ce_difference)],fmt='o',capsize=4);ax.axvline(0,color='gray',ls=':');ax.set_yticks(xx,[labels[x] for x in a.name]);ax.set_xlabel('Ganho de certeza equivalente, p.p. a.a.; IC condicional 95%');f.tight_layout();fs('uncertainty',f)

pages=[]
def page(title,body):pages.append(r'\section*{'+title+'}\n'+body)
pages.append(r'''\thispagestyle{empty}
{\large\color{navy}MACROECONOMIA APLICADA \quad | \quad SÍNTESE FINAL}
\vspace{1.3cm}

{\Huge\bfseries\color{navy}Prever menos,\\[6pt]decidir melhor}
\vspace{.6cm}

{\Large Câmbio real, condições comerciais\\e gestão econômica do carrego}
\vspace{.8cm}

\textbf{Pergunta de pesquisa.} A informação macroeconômica gera mais valor ao escolher a moeda, dimensionar a posição ou decidir quando permanecer exposto?

\textbf{Resultado central.} Uma combinação simples de três módulos preserva aproximadamente o retorno do carry, com menor risco histórico. A maior contribuição está na decisão de exposição e permanência; acrescentar complexidade à previsão não garante valor econômico.
\vspace{.5cm}
'''+tab(['Abr/2018--ago/2026','Carry puro','Média dos módulos'],[[lab,pct(get('Carry')[field]),pct(get('Equal_modules')[field])] for lab,field in [('Retorno composto anual','cagr'),('Volatilidade anual','vol'),('Maior queda desde o pico','maxdd')]]+[ ['Sharpe',num(get('Carry').sharpe),num(get('Equal_modules').sharpe)] ])+r'''
\vspace{.5cm}
\textbf{Natureza da evidência.} Pesquisa empírica preditiva e avaliação de decisões, com dados e custos explícitos. Não identifica choques causais nem demonstra arbitragem. As combinações são novas, mas a história já foi examinada nos estudos anteriores. A vantagem de retorno não é significativa após controlar a busca na grade principal.

\vfill
Dados congelados até agosto de 2026.\\
Relatório, código, resultados completos e documentação reproduzível.\\
Baseado na aula 8 e em Eichenbaum, Johannsen e Rebelo (2021).
''')
page('1. As descobertas que merecem permanecer',r'''
\textbf{A informação pode valer mais na decisão do que no ranking.} Trocar o ranking de juros por juros mais previsão EJR não foi uma boa escolha na amostra. Usar a previsão para dimensionar ou condicionar exposição foi mais útil. Não é a mesma hipótese estatística ou econômica.

\textbf{A carteira melhor não é a interseção de todos os filtros.} Exigir aprovação simultânea de valorização, preços, composição e risco elimina oportunidades. Uma média com pesos iguais permite que os módulos tenham funções e horizontes diferentes.

\textbf{O melhor aprendizado comercial é a adaptação.} Mudanças observadas na composição ajudam mais que tentar prever toda a transformação comercial. A extensão de commodities que melhora alguns erros de cinco anos não melhora automaticamente a carteira líquida.

\textbf{A fonte do prêmio muda.} Na combinação, a contribuição anual de juros cai de 2,62 para 1,50 pontos percentuais em relação ao carry; a contribuição cambial sobe de 0,74 para 1,82. O ganho vem da exposição escolhida, não de receber mais juros.

\textbf{O custo da proteção aparece nos meses bons perdidos.} A combinação fica quase fora do mercado em 2019 e perde uma alta favorável do carry. Em 2020--2021, evita parte relevante da deterioração. Desde 2023, rende menos que carry na média, com menos volatilidade.

\textbf{O resultado não é universal.} BRL e JPY concentram aproximadamente 86\% da contribuição antes dos custos de transação da combinação. Excluir BRL reduz fortemente o ganho econômico absoluto. Não podemos extrapolar a regra para qualquer conjunto de países.

\textbf{No hedge, o ativo continua importando.} BIL e SPY têm riscos próprios diferentes. A mesma operação cambial adiciona praticamente o mesmo retorno aritmético aos dois, mas muda patrimônio, volatilidade e drawdown de formas distintas.

Este relatório prioriza essas descobertas e mostra também as tentativas que falharam. Os arquivos completos mantêm todas as especificações executadas, sem substituir a grade pela sua melhor linha.
''')
page('2. Teoria mínima: previsão não é retorno',r'''
Se $S$ é moeda local por USD, uma posição comprada na moeda local ganha com queda de $S$. O retorno de um depósito estrangeiro, convertido em USD, é
\[
R^i_{t+1}=(1+i^i_t)\frac{S_t}{S_{t+1}}-1.
\]
Seu excesso sobre o funding USD contém juros, variação cambial e a interação entre ambos. Com posições compradas e vendidas, remuneração do caixa e custos:
\[
R^p_{t+1}=r^{USD}_t+\sum_i w_{i,t}(R^i_{t+1}-r^{USD}_t)-c_t-b_t.
\]
Não é uma operação de ``só câmbio''. O ativo subjacente do painel é um depósito/passivo curto aproximado por taxas oficiais. A simulação não usa retorno total de títulos longos nem contratos negociáveis observados.

O EJR relaciona o câmbio real atual à variação nominal futura em países com metas de inflação. O argumento econômico é que o ajuste real pode aparecer mais no nominal que na inflação relativa. Nosso projeto replica a relação preditiva e avalia decisões; não replica todo o DSGE identificado do artigo.

Uma previsão de cinco anos é convertida em sinal mensal dividindo a variação log prevista por 60. Isso é uma aproximação de velocidade média, não uma previsão identificada do caminho mensal. Daí a importância de testar tamanho, permanência e perdas no caminho.

A literatura de carry associa o prêmio cambial a riscos que podem aparecer de forma assimétrica. Nosso backtest não mede todos os riscos de liquidez, margem ou execução. Um Sharpe alto sem um episódio extremo na janela não prova que esses riscos desapareceram.

\textbf{Três critérios separados.} Erro de previsão mede acurácia; retorno líquido mede resultado financeiro; certeza equivalente mede uma troca entre média e risco para uma preferência especificada. Uma regra pode melhorar um e piorar outro.
''')
page('3. Dados, amostra e o que está identificado',r'''
Reutilizamos o snapshot dos quatro estudos: BRL, EUR, JPY, GBP, CAD e SEK; câmbio mensal de fechamento, CPI, juros e preços comerciais. A amostra de estimação começa em outubro de 1999 e termina em agosto de 2026. A avaliação longa de módulos disponíveis começa em março de 2013. A comparação integral dos módulos começa em abril de 2018, com 101 retornos mensais.

CPI entra com dois meses de atraso e preenchimento de no máximo um mês passado. Commodities usam defasagem de publicação; a extensão específica do terceiro estudo usa preços reais conhecidos com dois meses. Pesos comerciais anuais usam média de três anos, somente até $Y-2$. Alemanha aproxima o comércio da área do euro. Os arquivos atuais contêm revisões e não reconstruem todos os vintages.

\textbf{Identificação.} Este é um exercício de previsão e comparação de políticas condicionais. A variação vem do câmbio real, diferenciais de juros, preços comerciais e sua composição, observados no tempo e entre moedas. Não há instrumento ou experimento que torne essas mudanças exógenas. Portanto, não identificamos o efeito causal dos termos de troca sobre o câmbio, nem o efeito de adotar metas de inflação. Essa limitação responde explicitamente à orientação do professor sobre o que a estratégia empírica identifica.

As previsões são recursivas: cada estimação só admite rótulos realizados e disponíveis antes da origem. Os modelos de risco com informação adicional têm bases reestimadas nas mesmas linhas de treino. O relatório original e seus resultados desfavoráveis continuam preservados.

\textbf{Ponto de partida empírico.} A replicação brasileira dos slides recuperou inclinação de oito anos de -1,808 e $R^2$ de 0,883 na amostra. No painel, o EJR em cinco anos teve RMSE relativo ao passeio aleatório de 1,037. A diferença entre ajuste histórico forte e desempenho preditivo limitado motivou a análise econômica das regras, em vez de presumir lucro a partir do $R^2$.

\textbf{Seleção histórica.} Os componentes foram escolhidos por aprendizado nos estudos anteriores. Não existe uma amostra historicamente intocada nesta entrega. Fixamos combinações simples antes de rodá-las, avaliamos seleção usando só o passado e corrigimos a busca na grade principal. Isso reduz interpretações exageradas, mas não elimina a seleção acumulada em todo o projeto.
''')
page('4. Uma política com três funções econômicas',r'''
O ponto de partida é o carry: duas pernas compradas e duas vendidas, 25\% cada, escolhidas pelo diferencial de juros. A conta tem colateral em USD; a exposição bruta máxima é um. A síntese combina três módulos:

\textbf{A. Dimensionar e adaptar.} O sinal agregado soma o diferencial mensal de juros à apreciação EJR prevista, dividida pelo horizonte. O tamanho é o sinal atual dividido por sua mediana histórica anterior, limitado a $[0,1]$. Um alerta de mudança observada da composição comercial retira o par afetado. O limite é o percentil 80 passado da soma das mudanças absolutas dos pesos em três anos.

\textbf{B. Exigir remuneração e evitar deterioração.} O carry só é aberto quando seu retorno previsto agregado, suavizado por seis meses, supera 2\% a.a. Pares são retirados quando o índice comercial em 12 meses deteriora para a perna comprada ou melhora contra a perna vendida, acima do percentil de risco histórico.

\textbf{C. Controlar a permanência.} Coortes mensais de pares recebem orçamento $1/12$ e duram até 12 meses. Um aumento positivo da probabilidade de o câmbio consumir o carry, além do percentil 80 passado, impede entrada ou fecha a coorte. A direção do alerta acompanha a posição aberta, mesmo se o diferencial de juros atual mudar de sinal.

A combinação principal é
\[
w^{\mathrm{média}}_t=\frac13w^A_t+\frac13w^B_t+\frac13w^C_t.
\]
Os pesos são combinados antes de calcular custos e empréstimos. Não há otimização de Sharpe. Posições retiradas ficam em caixa. A versão ``núcleo + média'' mantém 50\% do orçamento no carry e 50\% na combinação.

Essa arquitetura permite discordância: tamanho responde à remuneração, condições comerciais à fragilidade e coortes à permanência. A alternativa de multiplicar todos os filtros também é testada, em vez de presumir que mais restrições são melhores.
''')
main=['Carry','EJR_rank','EJR_size','EJR_gate','Size_structure','Gate_price','Cohort_base','Cohort_risk','Integrated_cohort','All_filters','Commodity_blend','Two_modules','Equal_modules','Core_satellite']
page('5. Comparação principal em datas iguais',tab(['Regra','CAGR','Excesso','Vol.','Sharpe','Queda'],[[labels[n],pct(get(n).cagr),pct(get(n).mean_excess),pct(get(n).vol),num(get(n).sharpe),pct(get(n).maxdd)] for n in main],size=r'\footnotesize')+r'''
Abril de 2018 a agosto de 2026. CAGR é crescimento composto líquido em USD; excesso é média aritmética anualizada sobre caixa USD; volatilidade usa retornos totais e Sharpe usa excessos. Queda é o drawdown máximo, com caixa e custos incluídos.

\textbf{Resultado de síntese.} A média de três módulos tem retorno composto de 5,94\% a.a., versus 5,78\% do carry. Sua volatilidade é 2,33\%, versus 4,11\%, e o Sharpe sobe de 0,75 para 1,37. A maior queda observada passa de 9,09\% para 1,43\%.

O módulo de coortes por risco tem maior retorno e certeza equivalente nesta janela, mas a média é a síntese principal por construção econômica e ausência de pesos otimizados. A regra que exige todos os filtros entrega menos retorno que a média, sem melhor drawdown.

Não se deve comparar estes números diretamente com os retornos desde 2010 do primeiro estudo ou chamar a diferença de alfa: as datas e o desenho mudaram. Todas as comparações desta tabela compartilham o calendário.
''')
page('6. A trajetória importa mais que o número final',fig('wealth','Comparação líquida em USD. A média reduz quedas, mas também fica para trás em alguns meses favoráveis ao carry.')+r'''
A trajetória mostra por que a política pode ter valor para um orçamento de risco limitado: o investidor atravessa perdas menores para obter patrimônio final parecido. O módulo de coortes por risco e a média evitam boa parte do caminho negativo concentrado em 2020--2021.

Essa proteção é histórica e condicional à janela. A média ainda perdeu dinheiro em meses individuais; sua pior perda mensal foi '''+pct(get('Equal_modules').worst_month)+r'''. A perda média nos piores 5\% dos meses foi '''+pct(get('Equal_modules').es95)+r'''. Não estamos estimando um limite máximo de perda futura.

O teste não inclui a crise financeira de 2008 na avaliação dessas regras, porque os sinais recursivos completos ainda não existiam. A ausência desse episódio é uma limitação relevante para qualquer interpretação de risco de carry.
''')
page('7. A contribuição marginal de cada ideia',fig('risk_return','Mais filtros não deslocam automaticamente a relação entre retorno e risco para uma posição melhor.')+tab(['Comparação','Δ excesso, p.p. a.a.','Δ CE, p.p. a.a.'],[[label,num(100*(get(a).mean_excess-get(b).mean_excess)),num(100*(get(a).ce5-get(b).ce5))] for a,b,label in [('EJR_size','Carry','Tamanho EJR / carry'),('Size_structure','EJR_size','Composição / tamanho'),('Gate_price','EJR_gate','Preços / filtro EJR'),('Cohort_risk','Cohort_base','Saída / coortes'),('Equal_modules','Two_modules','Terceiro módulo / média de dois'),('All_filters','Equal_modules','Interseção / média')]])+r'''
A contribuição depende da função. Preços sobre o filtro EJR reduzem retorno, mas produzem uma trajetória de menor risco. A saída das coortes melhora ambos nesta janela. Acrescentar o terceiro módulo à média aumenta ligeiramente retorno e certeza equivalente, mas a média de dois já captura boa parte da melhora de Sharpe.

Estas diferenças são remoções/substituições de módulos, não efeitos causais independentes. Os sinais têm correlação, regras de entrada diferentes e frequências distintas. Uma decomposição de retorno não identifica o mecanismo estrutural que gerou cada ganho.
''')
page('8. De onde vem o dinheiro?',fig('attribution','Contribuições aritméticas da média de módulos. A soma das moedas exclui apenas o custo de transação; a soma dos cinco componentes reconcilia exatamente o excesso líquido.')+tab(['Componente','Carry, p.p. a.a.','Média, p.p. a.a.'],[[lab]+[num(100*A[(A.window=='common')&(A.name==n)&(A.component==c)].annual.iloc[0],3) for n in ['Carry','Equal_modules']] for c,lab in [('FX','Câmbio'),('Interest','Juros líquidos de funding'),('Interaction','Interação juros/câmbio'),('Borrow','Spread de empréstimo'),('Trading','Transações')]])+r'''
O carry puro recebe mais juros; a média obtém maior contribuição cambial com menos exposição. Isso é compatível com a hipótese original de usar informação macro para escolher quando suportar o risco cambial do carrego. Mas a decomposição é contábil: não prova que o sinal previu causalmente uma mudança de regime.

A compensação de ordens entre módulos economiza aproximadamente 0,25 ponto-base por ano nesta amostra. Logo, a melhora não é explicada por um grande benefício oculto de compensação contábil. O efeito vem principalmente das posições e dos momentos em que são mantidas.
''')
page('9. Quanto da proteção é simplesmente menor exposição?',fig('exposure',r'A exposição média da combinação é cerca de 48\% do patrimônio. Ficar em caixa é parte deliberada da política.')+tab(['Regra','Exp.','Excesso','Vol.','Queda'],[[lab]+[pct(a[c]) for c in ['exposure','mean_excess','vol','maxdd']] for ctrl,lab in [('base','Carry'),('rule','Média dos módulos'),('expost','Carry / média ex post'),('past','Carry / exposição passada')] for a in [EC[(EC.name=='Equal_modules')&(EC.control==ctrl)].iloc[0]]])+r'''
O controle ex post iguala a exposição média, mas usa a média futura e serve apenas como diagnóstico. O controle passado usa informações disponíveis, porém sua exposição realizada difere por causa da adaptação lenta do histórico.

À mesma exposição média, a combinação tem volatilidade um pouco maior, retorno maior e drawdown menor que o carry reduzido. O intervalo da diferença de drawdown contra esse controle inclui zero. Portanto, o resultado sugere seleção útil de retorno; não estabelece proteção superior com o mesmo orçamento de exposição.
''')
page('10. Medindo valor econômico, além do Sharpe',r'''
Usamos uma aproximação de certeza equivalente excedente para preferências média-variância:
\[
CE_\gamma=12\left(\overline{R-r_f}-\frac\gamma2\,\widehat{\mathrm{Var}}(R-r_f)\right),\quad \gamma\in\{3,5,10\}.
\]
Ela põe retorno e variância na mesma unidade anual. Não é utilidade esperada exata sob caudas assimétricas. O parâmetro representa preferência; não foi escolhido para maximizar a vantagem da estratégia.
'''+tab(['Regra','CE γ=3','CE γ=5','CE γ=10'],[[labels[n],pct(get(n).ce3),pct(get(n).ce5),pct(get(n).ce10)] for n in ['Carry','EJR_gate','Size_structure','Cohort_risk','Two_modules','Equal_modules','Core_satellite']])+fig('uncertainty','Intervalos condicionais em blocos de 12 meses para a diferença contra a base. A vantagem média de utilidade não é estabelecida para a combinação frente ao carry pleno.')+r'''
Para $\gamma=5$, a média supera o carry em aproximadamente 38 pontos-base anuais de certeza equivalente. Essa é uma margem econômica amostral antes de uma eventual taxa adicional de gestão; não é uma taxa recomendada nem um ganho garantido. Seu intervalo de 95\% inclui valores negativos.
''')
page('11. Quando funciona e quando custa caro',fig('episodes','Janelas de calendário fixadas para diagnóstico. Anualizar uma janela curta não cria mais observações nem identifica o efeito causal de um evento.')+r'''
\textbf{2019: custo de oportunidade.} A média entrega cerca de 0,40\% a.a. de excesso, enquanto carry entrega 3,83\%. Os módulos de composição e de filtro estão quase sempre em caixa. A proteção pode parecer inútil durante um período favorável.

\textbf{2020--2021: principal contribuição de proteção.} O carry tem excesso médio anualizado de -1,43\%, e a média de módulos, +2,39\%. A menor participação em posições desfavoráveis compensa o custo de ter ficado de fora antes.

\textbf{2022: participação em parte do prêmio.} A média obtém 7,46\% de excesso anual, contra 6,89\% do carry, com menor exposição média. Esse resultado ajuda o desempenho total, mas não deve ser tratado como padrão garantido para todo choque monetário.

\textbf{2023--agosto de 2026: menor retorno com menor risco.} A média entrega 3,85\% a.a. de excesso contra 4,90\% do carry. A estratégia troca parte da alta por uma trajetória menos volátil.

Na pior janela móvel de 36 meses, o excesso anualizado da média foi '''+pct(get('Equal_modules').worst36)+r''', contra '''+pct(get('Carry').worst36)+r''' do carry. A evidência depende de poucos episódios macroeconômicos, apesar das 101 observações mensais.
''')
page('12. O Brasil é parte da estratégia, não um detalhe',tab(['Universo','Regra','Excesso','Vol.','CE γ=5'],[[un,labels[n],pct(vr(n,v).mean_excess),pct(vr(n,v).vol),pct(vr(n,v).ce5)] for un,v in [('Completo','Base'),('Sem BRL','NoBRL'),('Sem EUR','NoEUR')] for n in ['Carry','Cohort_risk','Equal_modules']])+r'''
Retirar BRL derruba o excesso da média de 3,17\% para 0,65\% a.a. A volatilidade cai junto. O Sharpe ainda fica perto de um, mas a certeza equivalente fica muito abaixo do carry do universo sem BRL. Um Sharpe razoável com pouca exposição não resolve a falta de retorno econômico absoluto.

As exclusões refazem o ranking e as regras de posição no universo restante. As previsões de risco reaproveitadas continuam estimadas no painel original; esta é uma sensibilidade de alocação, não uma estimação inteiramente sem informação brasileira.

Parte do mecanismo é a barreira absoluta de 2\% a.a.: com prêmios menores, um módulo quase desliga. Investigamos depois da primeira rodada barreiras de zero e metade da mediana histórica do prêmio. Sem BRL, a média sobe de 0,65\% para aproximadamente 0,87\% a.a., ainda abaixo do carry de 2,00\%.

\textbf{Aprendizado de mercado.} O nível mínimo de remuneração aceitável depende do universo, dos custos e do mandato. Um parâmetro plausível para seis moedas não pode ser transplantado sem avaliar como altera a participação. Esse diagnóstico ajuda a entender a regra; não autoriza escolher retrospectivamente uma barreira que restaure o melhor backtest.
''')
page('13. Custos, atraso, orçamento de risco e parâmetros',fig('robustness','Sharpe nas variantes. O desenho principal é a coluna Base; as demais são sensibilidades e não candidatos escolhidos pela maior célula.')+tab(['Condição','Carry: excesso','Média: excesso','Média: queda'],[[lab,pct(vr('Carry',v).mean_excess),pct(vr('Equal_modules',v).mean_excess),pct(vr('Equal_modules',v).maxdd)] for v,lab in [('Base','Base'),('cost4_borrow50_lag1','Transações 4 vezes'),('cost1_borrow300_lag1','Empréstimo 300 pb/ano'),('cost1_borrow50_lag2','Execução mais um mês'),('vol0.03',r'Redução para alvo 3\%')]])+r'''
A combinação é relativamente estável aos custos e ao atraso adicional nesta amostra, em parte por negociar menos risco que carry. O spread de empréstimo importa mais que pequenos custos por transação porque incide continuamente sobre a perna vendida.

Alvos de volatilidade 3/4/5\% usam covariância de 24 meses observada antes da execução. Só reduzem posições; não há alavancagem para alcançar a meta. O carry com alvo de 3\% já reduz bastante sua queda, reforçando a necessidade de compará-lo com controles simples.

A tabela completa contém 390 linhas de métricas de sensibilidade, incluindo mudanças que não afetam certos módulos. Contá-las como 390 descobertas independentes seria incorreto.
''')
page('14. Escolher o vencedor recente foi pior que combinar',fig('selection','Família longa, escolha anual com janela de 36 meses. A seleção ex post é apenas um teto ilustrativo: usa o resultado futuro para identificar o membro vencedor.')+tab(['História','Regra','Início','Sharpe','CE γ=5'],[[int(a.history),{'Past_selection':'Escolha passada','Equal_members':'Média fixa','Carry':'Carry','Hindsight_static':'Melhor ex post'}[a.rule],a.first,num(a.sharpe),pct(a.ce5)] for a in S[(S.family=='long')].itertuples(index=False)],size=r'\footnotesize')+r'''
Todo janeiro, a regra escolhe o membro com maior certeza equivalente nos últimos 36 ou 60 meses, usando apenas retornos até o mês anterior. Mantém essa escolha até a próxima atualização, com execução atrasada e custos da carteira resultante.

Nas duas janelas da família longa, a escolha passada perde para a média fixa. A família com todos os sinais começa a ser selecionável mais tarde e também não mostra vantagem consistente de perseguir o melhor desempenho recente.

Isso não prova que toda adaptação é ruim. Mostra que o erro de escolher qual regra dominará o próximo regime pode superar o benefício da flexibilidade. Com amostra curta e sinais persistentes, pesos iguais são uma disciplina econômica útil, além de uma simplificação operacional.
''')
page('15. Uma previsão melhor pode dar uma carteira pior',r'''
O terceiro estudo encontrou melhora de erro nominal em cinco anos ao incluir um componente de commodities específico à composição comercial. Reproduzimos essa previsão e combinamos 50\% dela com 50\% do EJR. A carteira usa o resultado combinado para dimensionar carry. Também variamos esse peso para 25/75\%.
'''+tab(['Janela','Sinal','Excesso','Sharpe','CE γ=5'],[[lab,labels[n],pct(get(n,w).mean_excess),num(get(n,w).sharpe),pct(get(n,w).ce5)] for w,lab in [('long','Desde 2013'),('common','Desde 2018')] for n in ['EJR_size','Commodity_blend']])+r'''
Na janela longa, o blend comercial tem excesso de 2,28\% a.a., contra 2,81\% do tamanho EJR. Na janela comum, os resultados são muito próximos. A melhora estatística de um endpoint distante não se traduz em uma trajetória mensal mais remuneradora depois de juros e custos.

\textbf{Uma tentativa economicamente mais direta também falhou.} Estimamos a probabilidade de perda de 15 pares, incluindo sua volatilidade e informação comercial conjunta. Avaliamos só os dois pares efetivamente escolhidos a cada origem. O Brier relativo é '''+num(PM.brier_ratio.iloc[0],3)+r''', com 90 datas avaliadas: não melhora a base.
'''+tab(['Regra de permanência','Excesso','Sharpe','Queda'],[[{'Cohort_pair_risk':'Risco conjunto do par','Cohort_leg_risk':'Risco orientado das pernas','Cohort_base':'Coortes sem saída','Ensemble_pair':'Média com risco do par'}[a.name],pct(a.mean_excess),num(a.sharpe),pct(a.maxdd)] for a in PAIR.itertuples()])+r'''
Esse resultado negativo impede que a síntese se torne apenas uma coleção de acertos. Uma hipótese economicamente plausível pode falhar por pouco sinal, excesso de parâmetros ou instabilidade; sua plausibilidade não substitui validação.
''')
page('16. Permanência: o desenho correto da posição',r'''
Uma coorte guarda quais moedas foram compradas e vendidas na entrada. A regra de saída deve avaliar o risco \emph{dessa posição}; não pode simplesmente usar a direção favorecida pelo diferencial de juros atual.

No modelo de risco herdado, o evento é o câmbio consumir o diferencial de juros em 12 meses, orientado pela posição de carry em cada origem. Para a síntese, convertemos a mudança de probabilidade para a perna comprada ou vendida efetivamente mantida. Para direção oposta, usamos o complemento do evento log de perda, uma aproximação que não inclui custos nesse rótulo preditivo. A contabilidade da carteira inclui os custos.

Também exigimos aumento positivo do risco, além do percentil histórico. Uma variação apenas menos negativa não basta. Por essas razões, este módulo é uma \textbf{nova especificação}, e seu drawdown de 1,72\% não deve ser apresentado como reprodução dos 3,23\% encontrados no complemento anterior.

Coortes são fechadas no primeiro sinal admissível ou no vencimento. A informação em $t$ produz operação em $t+1$ e retorno em $t+2$. Encerrar a coorte retira o risco; não transfere o orçamento retirado para multiplicar a exposição de outra coorte. Novas entradas mensais são decisões distintas.

A base de comparação abre coortes nas mesmas datas, com a mesma formação gradual. Isso evita atribuir ao filtro o simples benefício de começar com menos capital alocado.

O resultado econômico é atraente nesta janela: excesso de 3,51\% a.a. contra 2,78\% da base, com menor drawdown. Seu ganho de certeza equivalente frente à base tem intervalo amplo que inclui zero. Permanece um candidato de pesquisa, não uma política de saída comprovada.
''')
page('17. Mercado: a mesma previsão aplicada ao hedge',fig('hedge_wealth','Ativos americanos mantidos continuamente, com resultados em BRL desde março de 2013. O painel do SPY usa escala própria por seu prêmio acionário.')+r'''
Aqui a pergunta muda: um investidor em BRL já possui BIL ou SPY e escolhe quanto do risco USD/BRL proteger. Ele não vende o ativo para ir a caixa. O retorno do ETF e o overlay cambial são registrados separadamente.

Testamos hedge 0/50/100\%, EJR gradual, retorno total gradual, blend comercial, média das três previsões e metade hedge 50\% mais metade sinal. A média reduz a sensibilidade a uma previsão específica, sem otimizar pesos.

O hedge mensal é aproximado por um forward sintético com diferencial de juros. A execução tem o mesmo atraso; cobramos custo por notional rolado, variando 2/5/10 pontos-base. O ativo recebe custo de entrada e saída. Não possuímos cotações históricas executáveis de forwards ou swaps cambiais, base, margem e limites de contraparte.

As taxas aqui não são diretamente comparáveis às carteiras em USD. O numerário, o ativo e o benchmark de caixa são BRL. Um retorno nominal alto em BRL pode refletir juros locais, inflação, prêmio acionário e câmbio, não a capacidade do modelo.
''')
page('18. A escolha do ativo muda o valor do hedge',tab(['Ativo / hedge','CAGR BRL','Vol.','Queda','Hedge médio'],[[a.asset+' / '+{'Unhedged':'zero','Half':r'50\%','Full':r'100\%','EJR_FX':'EJR gradual','Equal_signals':'média','Half_plus_signal':r'50\% + sinal'}[a.name],pct(a.cagr),pct(a.vol),pct(a.maxdd),pct(a.hedge)] for a in HM[(HM.cost==2)&(HM.period=='all')&HM.name.isin(['Unhedged','Half','Full','EJR_FX','Equal_signals','Half_plus_signal'])].itertuples()],size=r'\footnotesize')+r'''
\textbf{BIL.} O ativo tem pouco risco próprio de preço em USD. Por isso, a proteção cambial reduz muito a volatilidade em BRL. Hedge integral aproxima o resultado do carry implícito nos juros locais, mas não remove risco de implementação. O EJR gradual teve maior retorno nesta amostra, com mais risco que hedge integral.

\textbf{SPY.} O ativo mantém risco acionário. Mesmo com hedge, o drawdown permanece acima de 20\%. O hedge 50\% reduz volatilidade em relação a zero e 100\% nesta história; a covariância entre ações e dólar importa. Não usamos o câmbio para afirmar que prevemos o prêmio acionário.

A diferença aritmética entre aplicar o mesmo hedge a BIL e SPY é praticamente idêntica: o overlay protege um notional USD inicial. A diferença de CAGR não é idêntica porque a composição no tempo interage com a trajetória do ativo. Esse é um resultado contábil auditado, não dois testes independentes que confirmam alfa.

Os intervalos de ganho do hedge dinâmico contra hedge fixo e média de exposição ex post incluem zero. O valor mais defensável aqui é alinhar risco cambial ao mandato e ao ativo mantido; o timing lucrativo permanece incerto.
''')
page('19. Controle da busca e confiança nas descobertas',r'''
Testar muitas regras aumenta a chance de encontrar uma curva atraente por acaso. Reamostramos em blocos de 12 e 36 meses as diferenças de retorno de 14 alternativas frente ao carry, preservando sua dependência conjunta. Centralizamos as diferenças e usamos a maior estatística padronizada em cada réplica para um controle max-t unilateral na grade principal.
'''+tab(['Regra','Δ excesso a.a.','p ajustado 12m','p ajustado 36m'],[[labels[n],pct(a.annual_difference),num(a.max_t_p,3),num(J[(J.name==n)&(J.block==36)].max_t_p.iloc[0],3)] for n in ['EJR_size','Size_structure','Cohort_risk','Equal_modules','Commodity_blend'] for a in [J[(J.name==n)&(J.block==12)].iloc[0]]])+r'''
Nenhuma dessas vantagens médias de retorno é significativa nesse teste. Os p-valores não cobrem toda a exploração acumulada nos quatro estudos anteriores nem todas as sensibilidades posteriores. São um controle parcial, explicitamente delimitado.

Os intervalos de certeza equivalente, volatilidade e drawdown são condicionais aos sinais; não reestimam todos os modelos em cada amostra e não incorporam toda seleção. Contra carry pleno, a redução de volatilidade e drawdown da média aparece nos intervalos de 12 meses. Contra a mesma exposição média ex post, as diferenças de risco têm intervalos que incluem zero.

\textbf{O que pode ser dito.} A arquitetura produz uma relação histórica interessante entre retorno e risco e gera hipóteses econômicas testáveis. \textbf{O que não pode ser dito.} Que descobrimos alfa universal, arbitragem, proteção confiável contra o próximo crash ou uma taxa de gestão garantidamente suportada pelo ganho futuro.

A seleção anual usando somente o passado e os testes negativos dão contexto adicional: a estabilidade vem mais da combinação disciplinada que de nossa capacidade de identificar antecipadamente o próximo vencedor.
''')
page('20. Contribuição acadêmica e aplicação de mercado',r'''
\textbf{Contribuição acadêmica.} O trabalho conecta uma relação macro de longo prazo a decisões com restrições, juros e custos. A evidência sugere que a utilidade da informação depende da margem de decisão: escolher a moeda, escolher a quantidade ou escolher a permanência são problemas diferentes. O ranking falha, o dimensionamento melhora modestamente e a combinação de funções produz resultado de risco interessante.

Uma segunda contribuição é distinguir adaptação comercial observada de previsão estrutural. A composição prevista foi fraca; acrescentar informação ao modelo estatístico não bastou. A proxy observada tem valor condicional em certas regras, sem identificar transformação produtiva ou causalidade.

Uma terceira contribuição é mostrar a distância entre horizonte estatístico e horizonte de gestão. Acertar melhor o endpoint em cinco anos não assegura suportar o caminho. Os resultados do blend comercial e do risco conjunto de pares deixam essa diferença concreta.

\textbf{Aplicação de mercado.} A arquitetura pode servir como desenho de orçamento de risco: núcleo carry, tamanho condicionado à remuneração, alertas de fragilidade e regras de saída. A média de módulos é simples, auditável e tem menor dependência de escolher uma única previsão correta. Sua utilização real exigiria dados negociáveis, limites de posição e validação futura.

Para hedge, a aplicação é escolher o risco residual de câmbio preservando o ativo, com atenção ao numerário e à covariância. BIL e SPY não representam duas versões equivalentes de uma posição comprada em dólar.

\textbf{A decisão que esta pesquisa justifica.} Congelar a regra simples e acompanhar sua capacidade de manter a relação entre retorno e risco em dados novos. O melhor backtest individual não é automaticamente a melhor proposta. O valor econômico está no desenho que explica de onde vem o ganho, quanto risco assume e em quais condições deixa de funcionar.
''')
page('21. Limitações e especificação pronta para reprodução',r'''
\textbf{Risco de modelo e dados.} Taxas oficiais aproximam remuneração e funding; o investidor pode enfrentar preços diferentes. Não há impostos individuais, impacto por volume, slippage intramensal, margem dinâmica, risco de contraparte ou limites de short. A baixa frequência não mede perdas intramês. As séries revisadas e a proxy alemã limitam reconstrução em tempo real e generalização.

\textbf{Risco de amostra.} A janela completa tem 101 meses, não 101 episódios independentes. Horizontes longos se sobrepõem e sinais anuais persistem. O painel não multiplica artificialmente a história. A fase de 2020--2022 responde por parte importante da vantagem e o carry supera a média em outros períodos.

\textbf{Especificação congelada.} Três módulos com pesos de um terço; tamanho limitado a um; filtro de 2\% a.a. suavizado por seis meses; percentil 80 somente do passado, mínimo 36 observações; coortes de 12 meses; alerta de risco positivo e orientado à posição. Sem selecionar parâmetros pelo desempenho final. Sinal em $t$, operação em $t+1$, retorno em $t+2$.

\textbf{Critérios para acompanhamento.} Comparar carry, média e carry com orçamento de risco reduzido; registrar exposição, giro, spread efetivo, retorno cambial e de juros, acurácia das probabilidades e perda no caminho. Mudança de parâmetro deve criar uma versão nova, preservando a anterior e sua data. Não usar um resultado futuro ruim como motivo para reescrever o passado.

\textbf{Auditoria.} '''+str(len(VAL))+r''' verificações passaram: reprodução de pesos e métricas, equivalência da previsão comercial ao terceiro estudo, causalidade temporal de sinais por perturbação do futuro, execução, funding, custos, atribuição, coortes, limites de hedge e preservação dos 306 arquivos congelados. A auditoria testa a implementação; não prova que o modelo econômico é verdadeiro.
''')
page('22. Fontes, arquivos e roteiro de leitura',r'''
\textbf{Referências principais.}
\begin{enumerate}
\item Eichenbaum, M. S.; Johannsen, B. K.; Rebelo, S. T. (2021). \emph{Monetary Policy and the Predictability of Nominal Exchange Rates}. Review of Economic Studies, 88, 192--228. \href{https://doi.org/10.1093/restud/rdaa024}{Artigo}. Material da aula 8 e PDF do curso preservados no projeto.
\item Brunnermeier, M.; Nagel, S.; Pedersen, L. (2008). \emph{Carry Trades and Currency Crashes}. \href{https://www.nber.org/papers/w14473}{NBER WP 14473}. Referência para prêmio, assimetria e risco de reversão de posições.
\item Gruss, B.; Kebhaj, S. (2019). \emph{Commodity Terms of Trade: A New Database}. \href{https://www.elibrary.imf.org/view/journals/001/2019/021/article-A001-en.xml}{IMF WP 19/21}. Referência metodológica; nossa proxy comercial de quatro grupos não replica integralmente a base.
\item Chen, Y.; Rogoff, K.; Rossi, B. (2010). \emph{Can Exchange Rates Forecast Commodity Prices?} QJE, 125, 1145--1194. \href{https://scholar.harvard.edu/sites/scholar.harvard.edu/files/rogoff/files/125-3-1145.pdf}{Versão dos autores}. Fundamenta a pergunta do terceiro estudo.
\item Banco Mundial: \href{https://www.worldbank.org/en/research/commodity-markets}{Pink Sheet}; \href{https://databank.worldbank.org/metadataglossary/world-development-indicators/series/TT.PRI.MRCH.XD.WD}{WDI/UNCTAD, termos de troca}. Demais provedores e URLs dos snapshots cambiais, juros, CPI e ETFs estão nos manifestos originais.
\end{enumerate}

\textbf{Reprodução.} Na raiz do projeto, executar \texttt{synthesis/run.ps1}. Python e Tectonic são os portáteis existentes. Nenhum dado novo é necessário. Fonte LaTeX, figuras vetoriais, scripts e saídas estão em \texttt{synthesis/}. Os estudos anteriores não foram alterados.

\textbf{Resultados auditáveis.} Métricas e retornos líquidos; atribuição; 390 linhas de sensibilidades; controles de exposição; seleção recursiva e auditoria; 48 combinações de ativo, hedge e custo; ajuste da busca; intervalos econômicos e de risco; refinamento da barreira de entrada; teste de risco conjunto dos pares. Todas as tentativas aparecem nos arquivos, inclusive as negativas.

\textbf{Leitura sugerida.} Para o argumento econômico, páginas 2--4 e 21. Para a decisão de carteira, páginas 5--13. Para não confundir seleção com aprendizado, páginas 14--16 e 20. Para a aplicação a ativos em dólar, páginas 18--19. A versão digital inclui os links das fontes; o pacote contém o mapa completo de reprodução.
''')
pre=r'''\documentclass[11pt,a4paper]{article}
\usepackage[T1]{fontenc}\usepackage[utf8]{inputenc}\usepackage[brazil]{babel}
\usepackage{lmodern,microtype,amsmath,booktabs,array,graphicx,float,caption,xcolor,enumitem,fancyhdr,hyperref}
\usepackage[margin=1.9cm,top=1.9cm,bottom=1.9cm]{geometry}
\definecolor{navy}{HTML}{164E63}\hypersetup{colorlinks=true,linkcolor=navy,urlcolor=navy,pdftitle={Prever menos, decidir melhor},pdfauthor={Macroeconomia Aplicada}}
\setlength{\parindent}{0pt}\setlength{\parskip}{6pt}\setlength{\emergencystretch}{3em}
\setlength{\tabcolsep}{5pt}\renewcommand{\arraystretch}{1.1}\setlength{\intextsep}{6pt}\setlength{\textfloatsep}{8pt}
\captionsetup{font=small,labelfont={bf,color=navy},skip=4pt}\setlist{nosep}
\pagestyle{fancy}\fancyhf{}\setlength{\headheight}{15pt}\fancyhead[L]{\small\color{navy}Prever menos, decidir melhor}\fancyhead[R]{\small Síntese econômica | Câmbio e carrego}\fancyfoot[C]{\thepage}
\begin{document}
'''
text=pre+'\n\\clearpage\n'.join(pages)+r'\end{document}';text=text.replace('Δ',r'$\Delta$').replace('γ',r'$\gamma$')
(H/'relatorio_sintese.tex').write_text(text,encoding='utf8');print('Designed pages',len(pages),'Figures',len(list(F.glob('*.pdf'))))
