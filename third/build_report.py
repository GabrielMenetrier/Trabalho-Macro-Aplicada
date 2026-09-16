"""Standalone third report: reproducible numeric tables, vector plots, LaTeX."""
from pathlib import Path
import os,json
R=Path(__file__).resolve().parents[1];H=R/'third';F=H/'figures';F.mkdir(exist_ok=True)
os.environ['MPLCONFIGDIR']=str(R/'tmp/matplotlib')
import numpy as np,pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as tick

M=pd.read_csv(H/'tables/metrics.csv');S=pd.read_csv(H/'tables/sensitivity.csv');O=pd.read_csv(H/'tables/predictions.csv.gz')
I=pd.read_csv(H/'tables/candidate_intervals.csv');PH=pd.read_csv(H/'tables/nonoverlap_phases.csv');W=pd.read_csv(H/'data/trade_weights.csv')
CC=['BRL','EUR','JPY','GBP','CAD','SEK'];COM=['oil','gas','copper','iron','soy','corn','wheat','gold'];HH=[3,12,36,60]
names={'oil':'Petróleo','gas':'Gás EUA','copper':'Cobre','iron':'Ferro','soy':'Soja','corn':'Milho','wheat':'Trigo','gold':'Ouro'}
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,'axes.spines.right':False,'axes.grid':True,'grid.alpha':.18,'axes.labelcolor':'#334155','text.color':'#163447','axes.titleweight':'bold','pdf.fonttype':42,'savefig.bbox':'tight'})
colors=['#156078','#d88927','#63833b','#aa4c63','#7d6b9f'];plt.rcParams['axes.prop_cycle']=matplotlib.cycler(color=colors)
def fs(name,fig):fig.savefig(F/(name+'.pdf'));fig.savefig(F/(name+'.png'),dpi=165);plt.close(fig)
def num(x,d=3):return '--' if pd.isna(x) else f'{float(x):.{d}f}'.replace('.',',')
def esc(x):return str(x).replace('&',r'\&').replace('%',r'\%').replace('_',r'\_').replace('#',r'\#')
def tab(headers,rows,size=r'\small',align=None):
    align=align or 'l'+'r'*(len(headers)-1)
    return size+r'\begin{center}\begin{tabular}{'+align+r'}\toprule'+'\n'+' & '.join(headers)+r' \\ \midrule'+'\n'+'\n'.join(' & '.join(str(x) for x in row)+r' \\' for row in rows)+'\n'+r'\bottomrule\end{tabular}\end{center}\normalsize'+'\n'
def fig(name,caption,width='.98'):return r'\begin{figure}[H]\centering\includegraphics[width='+width+r'\linewidth]{figures/'+name+'.pdf}\\caption{'+caption+r'}\end{figure}'+'\n'
def get(task,model,benchmark='history',country='POOL',period='all'):
    return M[(M.task==task)&(M.model==model)&(M.benchmark==benchmark)&(M.country==country)&(M.period==period)].iloc[0]
A=M[(M.block=='A')&(M.period=='all')&(M.benchmark=='history')].copy();A['commodity']=A.task.str.split('_').str[1];A['unit']=A.task.str.split('_').str[2]
agg=A.groupby(['unit','h','model']).agg(ratio=('rmse_ratio','median'),rw=('rmse_rw','median'),wins=('rmse_ratio',lambda x:int((x<1).sum())),wins_rw=('rmse_rw',lambda x:int((x<1).sum())))
agg.reset_index().to_csv(H/'tables/commodity_summary.csv',index=False)

# Single-currency matrix at the pre-specified 12-month horizon.
fig1,axes=plt.subplots(1,2,figsize=(9.2,4.2))
for ax,col,title in zip(axes,['rmse_ratio','rmse_rw'],['Contra a história da commodity','Contra nenhuma mudança']):
    vals=np.array([[get(f'A_{c}_nominal_12','Q_'+cc)[col] for cc in CC] for c in COM]);im=ax.imshow(vals,vmin=.8,vmax=1.3,cmap='RdYlBu_r');ax.set_xticks(range(6),CC);ax.set_yticks(range(8),[names[c] for c in COM]);ax.set_title(title,fontsize=11);ax.grid(False)
    for i in range(8):
        for j in range(6):ax.text(j,i,f'{vals[i,j]:.2f}',ha='center',va='center',fontsize=8,color='white' if vals[i,j]>1.23 else '#163447')
fig1.tight_layout();fs('single_currency',fig1)

fig1,axes=plt.subplots(1,2,figsize=(9.2,3.2),sharey=True)
for ax,unit,title in zip(axes,['nominal','real'],['Preços nominais em USD','Preços reais']):
    for model,label in [('Q_all','Seis câmbios juntos'),('Q_average','Média de seis previsões'),('Q_factor','Fator de câmbios')]:
        ax.plot(HH,[agg.loc[(unit,h,model),'rw'] for h in HH],'o-',label=label)
    ax.axhline(1,color='gray',ls=':');ax.set(xlabel='Meses à frente da origem',ylabel='Mediana RMSE / nenhuma mudança',title=title);ax.set_xticks(HH);ax.legend(fontsize=7)
fig1.tight_layout();fs('commodity_horizons',fig1)

fig1,axes=plt.subplots(1,2,figsize=(9.2,3.2),sharey=True)
for ax,unit in zip(axes,['nominal','real']):
    for model,label in [('Q_all','Conjunto Q / história'),('Q_average','Média Q / história')]:ax.plot(HH,[agg.loc[(unit,h,model),'ratio'] for h in HH],'o-',label=label)
    ax.axhline(1,color='gray',ls=':');ax.set(xlabel='Horizonte (meses)',ylabel='Mediana do RMSE relativo',title='Nominal' if unit=='nominal' else 'Real');ax.set_xticks(HH);ax.legend(fontsize=8)
fig1.tight_layout();fs('weak_benchmark',fig1)

fig1,axes=plt.subplots(1,2,figsize=(9.2,3.3))
for ax,h in zip(axes,[36,60]):
    vals=np.array([[get(f'B_FX_{h}',mod,'EJR',cc).rmse_rw for mod in ['REJR_Global','REJR_Trade','REJR_Specific']] for cc in CC])
    ax.imshow(vals,vmin=.5,vmax=1.6,cmap='RdYlBu_r',aspect='auto');ax.set_xticks(range(3),['Global','Comercial','Específico']);ax.set_yticks(range(6),CC);ax.grid(False);ax.set_title(f'{h} meses: RMSE / nenhuma mudança',fontsize=10)
    for i in range(6):
        for j in range(3):ax.text(j,i,f'{vals[i,j]:.2f}',ha='center',va='center',fontsize=9,color='white' if vals[i,j]>1.4 else '#163447')
fig1.tight_layout();fs('fx_countries',fig1)

fig1,axes=plt.subplots(2,1,figsize=(9,5),sharex=True)
for ax,cc in zip(axes,['BRL','JPY']):
    z=O[(O.task=='B_FX_60')&(O.unit==cc)];p=z.pivot(index='origin',columns='model',values='pred');y=z.groupby('origin').actual.first();d=pd.PeriodIndex(p.index,freq='M').to_timestamp()
    ax.plot(d,100*y.reindex(p.index),color='#253d4b',lw=1.8,label='Realizado');ax.plot(d,100*p.EJR,label='EJR');ax.plot(d,100*p.REJR_Specific,label='EJR + específico');ax.axhline(0,color='gray',ls=':',lw=.7);ax.set(ylabel='Variação em log × 100',title=cc);ax.legend(fontsize=8,ncol=3)
axes[-1].set_xlabel('Data da previsão; o resultado é observado cinco anos depois');fig1.tight_layout();fs('forecast_examples',fig1)

fig1,ax=plt.subplots(figsize=(9.2,3.3));v=S[(S.family=='FX')&(S.spec=='Specific')&(S.h==60)&(S.period=='all')]
x=np.arange(len(v));ax.bar(x-.18,v.rmse_ratio,.36,label='Contra EJR comparável');ax.bar(x+.18,v.rmse_rw,.36,label='Contra nenhuma mudança');ax.axhline(1,color='#263f4e',ls=':');ax.set_xticks(x,['Base','Ridge 1','Ridge 10','Ridge 100','Janela 120m','Atraso +1m','Sem EUR','Sem BRL'],rotation=20,ha='right');ax.set_ylabel('RMSE relativo');ax.legend(fontsize=8);fig1.tight_layout();fs('specific_robustness',fig1)

fig1,axes=plt.subplots(1,2,figsize=(9.2,3.2))
for ax,h in zip(axes,[36,60]):
    vals=[PH[(PH.task==f'B_FX_{h}')&(PH.benchmark==b)].rmse_ratio.to_numpy() for b in ['EJR','RW']]
    ax.boxplot(vals,tick_labels=['EJR','Nenhuma mudança'],showfliers=True,widths=.5);ax.axhline(1,color='gray',ls=':');ax.set(title=f'Fases não sobrepostas · {h} meses',ylabel='RMSE relativo do componente específico')
fig1.tight_layout();fs('nonoverlap',fig1)

fig1,axes=plt.subplots(1,2,figsize=(9.2,3.2))
for ax,h in zip(axes,[12,60]):
    mods=['history','Commodity','Q','Q_Global','Q_Trade','Interaction'];vals=[get(f'C_inflation_{h}',x).rmse_ratio for x in mods]
    ax.bar(range(len(mods)),vals,color=[colors[0] if x<1 else colors[3] for x in vals]);ax.axhline(1,color='gray',ls=':');ax.set_xticks(range(len(mods)),['História','+ comm.','+ Q','+ Q/global','+ Q/comércio','Interação'],rotation=25,ha='right');ax.set(title=f'Inflação relativa · {h} meses',ylabel='RMSE / história da inflação')
fig1.tight_layout();fs('inflation',fig1)

pages=[]
pages.append(r'''
\thispagestyle{empty}
{\large\color{navy}MACROECONOMIA APLICADA \quad | \quad TERCEIRO ESTUDO}
\vspace{1cm}

{\Huge\bfseries\color{navy}Quem antecipa quem?}
\vspace{.4cm}

{\Large Câmbio real, commodities e câmbio nominal futuro}
\vspace{.5cm}

Quinze ideias testadas. Previsões de preços e variáveis macroeconômicas.\\
Dados até agosto de 2026. Preparado em 11 de setembro de 2026.
\vspace{.5cm}

\textbf{1. Câmbio real ajuda a prever commodities?} Há ganhos pontuais frente a uma regressão com a história da própria commodity, principalmente em horizontes longos. A comparação com nenhuma mudança é muito mais difícil. Em 12 meses, o modelo conjunto de seis câmbios reais não superou esse benchmark em nenhuma das oito commodities nominais.

\textbf{2. Commodities ajudam a prever o câmbio nominal?} Acrescentar somente o preço global ou uma cesta comercial ao EJR não produziu melhora geral. O candidato mais interessante é o componente comercial específico de cada país, descontado o movimento global: em cinco anos, seu RMSE agregado foi 14,2\% menor que o EJR e 11,0\% menor que nenhuma mudança.

\textbf{3. O resultado é robusto?} A melhora frente ao EJR persiste em várias especificações. A superioridade frente a nenhuma mudança, porém, desaparece ao retirar o Brasil e na janela de origens desde 2019. Há apenas 140 origens mensais sobrepostas para o horizonte de cinco anos; isso equivale a pouco mais de dois blocos longos, não a 140 episódios independentes.

\textbf{Conclusão.} A extensão mais promissora é distinguir movimentos globais de commodities dos movimentos relevantes para a pauta comercial nacional. A evidência disponível ainda não estabelece superioridade preditiva geral. Interações e referências de equilíbrio mais flexíveis não resolveram o problema, e o ganho adicional para inflação foi pequeno.

\vfill
\colorbox{light}{\parbox{.94\linewidth}{\textbf{Escopo.} Este documento contém modelos e avaliação de previsões, sem carteiras. Os dois relatórios anteriores foram preservados. Código, dados, resultados completos e auditoria acompanham o PDF.}}
''')
pages.append(r'''
\section*{A pergunta econômica e a relação com os artigos}
A pergunta é se câmbio real e commodities contêm informações complementares sobre preços futuros. O ponto de partida é a replicação de Eichenbaum, Johannsen e Rebelo (EJR), que relaciona o câmbio real à evolução posterior do câmbio nominal e discute o papel do regime monetário [1].

Chen, Rogoff e Rossi estudam a direção moedas $\rightarrow$ commodities e também a direção inversa [2]. Seu universo de moedas, frequência, modelos e amostra são diferentes. A atualização de 2014 distingue resultados dentro da amostra e fora dela [3]. Nosso exercício conecta essas perguntas à replicação da aula; não é reprodução exata das tabelas ou da inferência dos dois artigos.

\textbf{Três hipóteses distintas.}
\begin{enumerate}[itemsep=6pt]
\item O câmbio real antecipa preços de commodities porque incorpora informação sobre condições futuras relevantes para o país.
\item As commodities antecipam câmbio nominal porque afetam fundamentos externos ou contêm informação adicional àquela já refletida no câmbio real.
\item As commodities modificam a relação entre desvio cambial e ajuste posterior: o mesmo desvio real pode ter implicações diferentes em estados distintos dos fundamentos.
\end{enumerate}

\textbf{O que identificamos.} A variação usada é temporal e entre países: movimentos de câmbio real, preços internacionais e exposições comerciais anteriores à amostra. Não há instrumento, experimento ou hipótese defendida de exogeneidade dos choques de commodities. Informação comum sobre atividade, dólar, política monetária e oferta pode mover todas essas variáveis. Portanto, identificamos desempenho preditivo condicional às especificações, não efeitos causais.

Essa distinção responde à orientação do professor de explicar de onde vem a variação e o que ela permite concluir. O caráter anterior dos pesos comerciais evita parte da endogeneidade da construção do índice, mas não transforma os movimentos de preços internacionais em choques exógenos.

\textbf{Critério de sucesso.} Uma relação economicamente plausível ou um coeficiente significativo não basta. A previsão precisa reduzir erros em observações que não entraram no treino, contra benchmarks claramente definidos. Uma melhora frente a um modelo ruim também não basta para estabelecer utilidade: por isso cada resultado é comparado à previsão de nenhuma mudança.

\textbf{Natureza exploratória.} A grade inicial foi registrada antes dos resultados deste estudo, mas não é pré-registro público. Os dados cambiais já haviam sido examinados nos trabalhos anteriores. A família EJR estritamente aninhada e o benchmark de variação nominal foram acrescentados após a primeira rodada para corrigir limitações do desenho; essa ampliação está registrada.
''')
wt=W.pivot(index='currency',columns='sector',values='net_weight').reindex(CC)
pages.append(r'\section*{Dados e construção das exposições comerciais}'+r'''
Oito alvos: petróleo médio, gás natural americano, cobre, minério de ferro, soja, milho, trigo HRW e ouro. Os preços são médias mensais de referência em dólares da Pink Sheet do Banco Mundial [4]. Há 12 séries completas de janeiro de 1994 a agosto de 2026: quatro adicionais compõem as cestas abaixo. Não são séries de retorno de contratos futuros.

\begin{itemize}[itemsep=4pt]
\item Energia: média geométrica de petróleo e gás americano.
\item Alimentos: soja, milho e trigo; matérias-primas agrícolas: algodão e borracha RSS3.
\item Metais: cobre, ferro, alumínio e níquel.
\end{itemize}

Dentro de cada cesta, pesos iguais fixos. A cesta global é a média dos quatro log-preços setoriais. Os índices oficiais WB não são usados, pois seus pesos divulgados são baseados no comércio de 2002--2004, posterior ao começo da estimação.

Os pesos nacionais usam WDI de 1994--1996 [5]. Para grupo $k$ e país $i$:
\[ w_{ik}=\frac{1}{3}\sum_{y=1994}^{1996}\frac{X_{iy}a^X_{iky}-M_{iy}a^M_{iky}}{X_{iy}+M_{iy}}. \]
$X,M$ são comércio de mercadorias; $a^X,a^M$ são participações de cada grupo. Peso positivo significa exposição exportadora líquida nesse grupo, na janela histórica. A proxy comercial em log é a soma dos log-preços reais setoriais multiplicados por esses pesos.
'''+tab(['Moeda','Energia','Alimentos','Mat. primas','Metais'],[[cc]+[num(100*wt.loc[cc,k],2) for k in ['energy','food','raw','metals']] for cc in CC])+r'''
Pesos em pontos percentuais do comércio total. EUR usa Alemanha como proxy, não a área do euro inteira; há teste sem EUR. O índice não mede os termos de troca completos nem um choque de renda em porcentagem do PIB. A cobertura por poucas commodities e a manutenção de pesos antigos são aproximações deliberadas.

FMI/Gruss--Kebhaj oferecem índices mais abrangentes [6], mas a versão com pesos fixos de várias décadas contém comércio futuro em relação a 1999. Não a utilizamos nesta avaliação. Câmbio e CPI dos seis países são os mesmos snapshots BIS/BCB/BLS/ECB/BOJ dos relatórios anteriores, preservados.
''')
pages.append(r'''
\section*{Relógio da informação e modelos comparáveis}
Origem $t$: fechamento mensal. $s_t$ é log de moeda local por USD; aumento significa depreciação da moeda local. O sinal real é $q_t=s_t+\log CPI_{US,t-2}-\log CPI_{i,t-2}$, com a regra de preenchimento limitado do trabalho original. A estimação começa em outubro de 1999; avaliação desde janeiro de 2010, com pelo menos 60 observações maduras por unidade.

\textbf{Câmbio nominal.} Alvo $s_{t+h}-s_t$, com $h=3,12,36,60$. O último alvo admitido no treino termina até $t-1$. EJR é reproduzido com inclinação agrupada, ausência de intercepto e centralização pela média de $q$ conhecida na origem. A família restrita acrescenta commodities mantendo essas escolhas.

\textbf{Commodity nominal.} O preço médio do mês $t$ só entra no mês seguinte. O alvo é $p_{t+h}-p_{t-1}$: preço futuro comparado ao último preço mensal conhecido. Logo, a distância desde o preço-base é $h+1$ meses; $h$ conta meses à frente da origem. O benchmark de nenhuma mudança prevê zero para esse alvo.

\textbf{Commodity real.} Deflacionamos pelo CPI americano. O último preço real integralmente observável é $t-2$, e o alvo é $(p-CPI_{US})_{t+h}-(p-CPI_{US})_{t-2}$. A distância é $h+2$. Há sensibilidade adicional que atrasa também o nominal em dois meses para separar deflação de disponibilidade.

\textbf{Inflação.} Alvo: variação de log CPI local menos americano entre $t$ e $t+h$. A base $t$ ainda não foi divulgada na origem; o exercício prevê a variação que será publicada posteriormente. Os rótulos só entram no treino após a divulgação do ponto final, com dois meses extras e margem de um mês.

\textbf{Modelo de história própria.} Para commodities: desvio do log-preço em relação à média passada e variações de 3/12 meses. Para inflação: inflação relativa passada de 12 meses. Regressões diretas com ridge fixa 10; padronização exclusivamente no treino. O painel flexível inclui interceptos por país não penalizados. PCA é estimado somente no treino. Não se usa divisão aleatória de observações.

\textbf{Por que duas famílias cambiais?} Acrescentar interceptos por país ao EJR pode mudar muito o desempenho sem que commodities tenham contribuído. Reportamos tanto regressões flexíveis comparadas com sua própria base Q quanto extensões estritas comparadas com EJR. Ganhos por troca de estimador não são atribuídos às novas variáveis.
''')
pages.append(r'''
\section*{As 15 ideias e o que foi efetivamente testado}
\begin{enumerate}[leftmargin=1.7em,itemsep=5pt]
\item \textbf{Q de cada país prevê commodity:} oito preços, seis câmbios, duas definições de preço e quatro horizontes.
\item \textbf{Ligação comercial:} média das previsões das duas moedas com maior exposição absoluta ao setor versus as quatro demais. Para ouro, metais é apenas proxy imperfeita; a leitura econômica do vínculo exclui ouro.
\item \textbf{Informação conjunta:} seis Q na regressão, fator principal, média dos Q e média de seis previsões individuais.
\item \textbf{Real versus nominal:} Q, nível nominal, variação nominal de 12 meses, inflação relativa e Q condicionado ao fator comum das moedas contra USD.
\item \textbf{Preço nominal versus real:} previsão dos dois alvos, incluindo comparação de disponibilidade igualada.
\item \textbf{Commodities sozinhas preveem câmbio:} nível/momentum global e nível/momentum comercial, sem Q.
\item \textbf{EJR acrescido de commodities:} mesma restrição de intercepto e mesma centralização da replicação.
\item \textbf{Índice específico do país:} pesos comerciais anteriores à estimação, contrastados com cesta global.
\item \textbf{Nível versus variação:} estado do preço real global, sua variação de 12 meses e ambos juntos.
\item \textbf{Global versus específico:} retirar do índice comercial a parcela atribuível ao movimento comum dos setores.
\item \textbf{Velocidade de ajuste condicional:} interação Q $\times$ preço global e Q $\times$ proxy comercial.
\item \textbf{Referência de equilíbrio condicional:} retirar de Q sua projeção em commodities e interceptos, estimada no treino; prever câmbio com o resíduo.
\item \textbf{Exportadores versus importadores:} permitir que exposição líquida histórica modifique coeficientes do preço global e, na família flexível, de Q.
\item \textbf{Canal nominal versus inflação:} estimar previsões de inflação relativa e compará-las à sua história própria.
\item \textbf{Direção e horizonte:} confrontar os quatro horizontes e as duas direções de previsão, sem confundir correlação preditiva com causalidade.
\end{enumerate}

Todos os resultados individuais, inclusive desfavoráveis, estão nos CSVs. O PDF apresenta os contrastes principais e grades agregadas; não escolhe silenciosamente a melhor moeda, commodity ou janela para representar a família inteira.
''')
examples=[('oil','CAD'),('gas','GBP'),('corn','CAD'),('soy','CAD')]
pages.append(r'\section*{1. Câmbio real individual prevê commodities?}'+fig('single_currency','Preços nominais, horizonte de 12 meses à frente da origem. Cada célula é uma regressão própria; valores abaixo de 1 são melhora. O preço global de uma commodity não é replicado como seis realizações independentes.')+tab(['Commodity / moeda','RMSE / história','RMSE / sem mudança'],[[esc(names[c]+' / '+cc),num(get(f'A_{c}_nominal_12','Q_'+cc).rmse_ratio),num(get(f'A_{c}_nominal_12','Q_'+cc).rmse_rw)] for c,cc in examples])+r'''
O caso CAD $\rightarrow$ petróleo melhora o erro da regressão histórica em 7,2\%, mas fica ligeiramente pior que nenhuma mudança. Isso ilustra por que a escolha do benchmark altera a interpretação. Milho/CAD e soja/CAD têm ganhos pontuais frente a nenhuma mudança, sem evidência robusta após as correções de multiplicidade.

Não apareceu um padrão de superioridade geral do câmbio real individual no horizonte de um ano. A presença de relações econômicas entre países e commodities não dispensa a avaliação fora da amostra.
''')
rows=[]
for unit in ['nominal','real']:
    for h in HH:
        v=agg.loc[(unit,h,'Q_all')];rows.append(['Nominal' if unit=='nominal' else 'Real',str(h),num(v.ratio),num(v.rw),f'{int(v.wins_rw)}/8'])
pages.append(r'\section*{3. Combinar câmbios melhora a informação?}'+fig('commodity_horizons','Mediana entre as oito commodities. A mediana é resumo descritivo, não erro de uma nona commodity nem teste com oito amostras independentes.')+tab(['Preço','h','RMSE / história','RMSE / sem mudança','Vitórias / 8'],rows)+r'''
A regressão conjunta tem mais parâmetros e pode piorar a previsão, especialmente em horizontes curtos. A média simples de previsões costuma ser menos instável. No nominal, aos 12 meses, a regressão conjunta não supera nenhuma mudança em qualquer uma das oito commodities.

Em 36 meses, o modelo conjunto melhora a história própria em sete commodities nominais e nas oito reais. Porém supera nenhuma mudança em apenas duas de cada conjunto. Uma melhora relativa grande pode ser, em parte, a correção de extrapolações ruins do benchmark histórico.
''')
ab=[]
for h in [12,36]:
    for prefix,label in [('Q_','Câmbio real'),('S_','Nível nominal'),('DS_','Variação nominal'),('PI_','Inflação relativa')]:
        b=A[(A.h==h)&(A.unit=='nominal')&A.model.isin([prefix+c for c in CC])];ab.append([str(h),label,num(b.rmse_ratio.median()),num(b.rmse_rw.median())])
pages.append(r'\section*{4--5. O componente real faz diferença?}'+tab(['h','Informação acrescentada','Mediana / história','Mediana / sem mudança'],ab)+r'''
O nível nominal é centralizado com sua média passada; a variação nominal usa 12 meses. O componente de preços é a diferença entre Q e o log-câmbio nominal, centralizada da mesma forma. Não incluímos simultaneamente Q, nominal e preços relativos como três variáveis independentes, pois existe identidade linear entre eles.

Também estimamos história da commodity + fator comum nominal das seis moedas contra USD e, depois, acrescentamos Q individual. Esse fator é um controle empírico simples, não DXY nem um choque estrutural do dólar. A pergunta é se Q acrescenta informação além do movimento compartilhado das moedas.
'''+fig('weak_benchmark','Trocar a referência para a história própria produz uma impressão mais favorável em horizontes longos. Compare com a figura anterior, cujo benchmark é nenhuma mudança.')+r'''
\textbf{Deflação e disponibilidade.} No horizonte de 36 meses, a mediana do RMSE relativo à história é 0,757 para preços reais e 0,816 para nominais. Ao igualar o atraso nominal em dois meses, a mediana nominal é 0,811: a diferença não vem apenas do mês extra de disponibilidade. Isso continua sendo uma comparação descritiva entre alvos diferentes; não demonstra que o componente real ganhou conteúdo causal.
''')
linked=[]
for unit in ['nominal','real']:
    for h in [12,36]:
        for mod,label in [('Q_linked','Mais expostos'),('Q_other','Demais moedas')]:
            b=A[(A.unit==unit)&(A.h==h)&(A.model==mod)&(A.commodity!='gold')];linked.append(['Nominal' if unit=='nominal' else 'Real',str(h),label,num(b.rmse_ratio.median()),num(b.rmse_rw.median())])
pages.append(r'\section*{2 e 8. A pauta comercial organiza a previsibilidade?}'+tab(['Preço','h','Grupo','RMSE / história','RMSE / sem mudança'],linked)+r'''
Para cada grupo de commodities, as duas moedas com maior peso comercial absoluto em 1994--1996 são consideradas mais expostas. Exposição importadora também pode ser informativa: não se restringe o grupo a exportadores. As previsões individuais recebem pesos iguais dentro de cada grupo. A regra de seleção não depende dos resultados de previsão.

O grupo mais exposto não domina os demais. Isso enfraquece uma interpretação simples segundo a qual o país mais ligado comercialmente a uma commodity necessariamente a antecipa melhor. O grupo pode conter um grande importador cuja moeda incorpora muitos outros determinantes.

\textbf{Limitações concretas.} Os pesos são antigos, os quatro grupos são amplos e poucas cotações representam cada cesta. O Brasil, por exemplo, apresenta peso negativo em energia na janela histórica, o que não pretende descrever sua pauta atual. Alemanha é somente uma aproximação para EUR. Ouro não tem cobertura adequada pela participação de minérios/metais usada aqui; por isso foi excluído desta comparação econômica de grupos, embora suas previsões permaneçam na grade geral.

\textbf{Na direção inversa.} Substituir uma cesta global pela proxy comercial nacional, sem Q, reduziu parte do erro em horizontes longos em relação ao modelo global, mas não estabeleceu superioridade sobre nenhuma mudança. O maior interesse aparece ao decompor a proxy comercial em movimento global e específico, discutido a seguir.

\textbf{O que este teste não faz.} Não estima elasticidade de exportação, não usa os pesos como instrumento e não mede renda gerada por um choque. A associação entre preços internacionais e câmbio pode continuar refletindo atividade e condições financeiras comuns.
''')
rmods=['REJR_Global','REJR_Trade','REJR_GlobalMom','REJR_Interaction','REJR_TradeInteraction','REJR_Exposure','REJR_Specific']
rl={'REJR_Global':'EJR + preço global','REJR_Trade':'EJR + cesta comercial','REJR_GlobalMom':'EJR + global e variação','REJR_Interaction':'EJR + interação global','REJR_TradeInteraction':'EJR + interação comercial','REJR_Exposure':'EJR + exposição heterogênea','REJR_Specific':'EJR + componente específico'}
rows=[[rl[mod]]+[num(get(f'B_FX_{h}',mod,'EJR').rmse_ratio) for h in HH] for mod in rmods]
rwrows=[['EJR original']+[num(get(f'B_FX_{h}','EJR','Q').rmse_rw) for h in HH],['EJR + específico']+[num(get(f'B_FX_{h}','REJR_Specific','EJR').rmse_rw) for h in HH]]
pages.append(r'\section*{6--7. Commodities acrescentam informação ao EJR?}'+tab(['Extensão / EJR','3m','12m','36m','60m'],rows)+r'''
Razão entre RMSE da extensão e RMSE de EJR, nas mesmas origens. As extensões mantêm a restrição de intercepto do modelo original. Os preços entram deflacionados e conhecidos com dois meses de atraso. Momentum é a variação de 12 meses. O h de 60 meses do modelo com momentum tem início mais tardio por necessidade de treino; a comparação permanece pareada.

Nos horizontes curtos, a maior parte das inclusões piora ou altera muito pouco o resultado. Preço global e cesta comercial isolados não resolvem a previsibilidade cambial. O componente específico se destaca em 36 e 60 meses, mas não nos horizontes curtos.
\subsection*{Comparação com nenhuma mudança}
'''+tab(['Modelo / sem mudança','3m','12m','36m','60m'],rwrows)+r'''
Em 36 meses, a extensão específica melhora EJR, mas ainda tem erro agregado ligeiramente maior que nenhuma mudança. Em 60 meses, supera ambos na amostra integral. Essa é a principal descoberta exploratória deste estudo.

\textbf{Teste comparável.} A extensão restrita é $\widehat{\Delta_h s}_{i,t}=\beta_h Q_{i,t}+\gamma_h Z_{i,t}$, ou sua versão com mais componentes. As médias para centralizar níveis são estimadas com a informação disponível até $t$, como no EJR. Nenhum intercepto adicional é introduzido. A auditoria reproduz numericamente EJR quando as colunas de commodities são removidas.

\textbf{Commodities sozinhas.} Nos modelos flexíveis, nível e variação global sem Q tiveram RMSE sobre nenhuma mudança de 1,031; 1,102; 1,515; 1,753 nos quatro horizontes. A cesta comercial isolada ficou em 1,012; 1,057; 1,275; 1,371. São resultados desfavoráveis, não evidência de uma alternativa autossuficiente ao sinal real.
''')
pages.append(r'''
\section*{10. O que significa o componente específico?}
Seja $b_{k,t}$ o log-preço real conhecido do setor $k$. Definimos
\[ G_t=\frac{1}{4}\sum_k b_{k,t},\qquad Z_{i,t}=\sum_k w_{ik}b_{k,t},\qquad e_i=\sum_k w_{ik}. \]
O componente específico é
\[ Z^{esp}_{i,t}=Z_{i,t}-e_iG_t=\sum_k w_{ik}(b_{k,t}-G_t). \]
Ele distingue, por exemplo, um movimento concentrado em metais de uma alta comum a todas as cestas. A regressão inclui Q, o componente global e o específico. Todos os níveis são centralizados com médias disponíveis na origem.

Essa decomposição não extrai um choque estrutural. É uma forma transparente de separar informação comum e composição comercial. Seus pesos não são escolhidos para maximizar a previsão.
'''+fig('fx_countries','RMSE sobre nenhuma mudança por moeda. O ganho agregado em cinco anos não é uniforme: BRL, EUR e CAD ficam abaixo de 1; JPY, GBP e SEK ficam acima.')+r'''
CAD já era bem previsto pelo EJR nesta janela: acrescentar o específico piora seu erro relativo a EJR, embora continue melhor que nenhuma mudança. Já BRL apresenta melhora relevante nas duas comparações. Assim, ``melhor que nenhuma mudança'' e ``commodities acrescentaram valor ao EJR'' são perguntas diferentes também dentro de cada país.
''')
countryrows=[[cc]+[num(get('B_FX_60','REJR_Specific','EJR',cc)[col]) for col in ['rmse_ratio','rmse_rw']] for cc in CC]
pages.append(r'\section*{Onde está a melhora e onde o modelo erra}'+tab(['Moeda, horizonte 60m','RMSE / EJR','RMSE / sem mudança'],countryrows)+fig('forecast_examples','Exemplos escolhidos para mostrar heterogeneidade: BRL, com melhora, e JPY, com erro persistente. O eixo horizontal é a origem, não o mês de realização. Cada ponto usa uma previsão distinta de cinco anos; as janelas se sobrepõem.')+r'''
O erro agregado é calculado agrupando previsões em log, sem padronizar cada moeda pela sua volatilidade. Portanto moedas com variações maiores, como BRL nesta amostra, têm influência maior sobre o RMSE agregado. A exclusão de BRL é essencial para interpretar a descoberta; não basta contar quantos países tiveram melhora.
''')
v=S[(S.family=='FX')&(S.spec=='Specific')&(S.h==60)&(S.period=='all')]
pages.append(r'\section*{A descoberta sobrevive a variações razoáveis?}'+fig('specific_robustness','Extensão específica em 60 meses. Nos testes de penalização/janela/universo, o EJR de referência recebe a mesma alteração; o benchmark de nenhuma mudança permanece explícito.')+tab(['Variação','RMSE / EJR comparável','RMSE / sem mudança'],[[esc(x.variant),num(x.rmse_ratio),num(x.rmse_rw)] for _,x in v.iterrows()])+r'''
A melhora frente a EJR persiste com penalizações 1/10/100, janela móvel de 120 meses, atraso adicional das commodities e retirada de EUR ou BRL. Mas, sem BRL, o RMSE passa a 1,147 vezes o de nenhuma mudança. O resultado agregado não é transferível automaticamente ao conjunto dos demais países.

\textbf{Estabilidade temporal.} Nas origens desde 2019, restam apenas 32 previsões de cinco anos, realizadas até agosto de 2026. A razão contra EJR é 0,825, mas contra nenhuma mudança é 1,630. A extensão corrige parte de um modelo-base ruim nesse trecho; não supera uma referência simples.

Excluir alvos que atravessam 2020--2021 deixa somente 60 origens de cinco anos. Esse diagnóstico tem forte seleção de períodos e não substitui uma validação externa. Todas as sensibilidades dos demais modelos e commodities permanecem nos arquivos completos.
''')
introws=[]
for h in [36,60]:
    b=I[(I.task==f'B_FX_{h}')&(I.block==h+2)]
    for _,x in b.iterrows():introws.append([str(h),x.benchmark,num(x.mean_loss_gain,4),f'[{num(x.low,4)}; {num(x.high,4)}]'])
pages.append(r'\section*{O que os intervalos e a sobreposição permitem dizer}'+tab(['h','Referência','Ganho médio de perda',r'IC bootstrap 95\%'],introws)+r'''
Ganho positivo significa redução da perda quadrática média, em unidades de log ao quadrado. Bootstrap por datas, mantendo os choques comuns entre moedas, com 1.999 reamostragens e blocos de $h+2$ meses. Também calculamos blocos de 12 meses. Os intervalos são condicionais às previsões estimadas e não corrigem a seleção posterior do candidato.

Frente a EJR, os intervalos são favoráveis. Frente a nenhuma mudança, incluem zero. No horizonte de cinco anos há somente 140 datas sobrepostas, cerca de 2,3 blocos de 62 meses; nem um intervalo bootstrap estreito transformaria esse histórico em muitas experiências independentes.
'''+fig('nonoverlap','Todas as fases de seleção de origens espaçadas por h+2 meses. Cada fase contém apenas 4--5 datas para 36m e 2--3 para 60m. Não escolhemos a fase mais favorável.')+r'''
Em cinco anos, as razões contra nenhuma mudança variam de aproximadamente 0,47 a 1,50 conforme a fase; contra EJR, de 0,71 a 0,97. Há evidência descritiva consistente de melhora relativa a EJR, mas a superioridade contra nenhuma mudança é muito menos estável.

\textbf{P-valores.} Diferenças de perda são agregadas por data antes do HAC, com $h+2$ defasagens. Não emitimos p-valor com menos de 36 datas ou três blocos do horizonte. Holm inclui os testes contra a base e contra nenhuma mudança, nos três blocos de hipóteses. Os resultados de cinco anos permanecem descritivos.
''')
interrows=[]
for mod,label,bm in [('REJR_Interaction','Interação global, restrita','EJR'),('REJR_TradeInteraction','Interação comercial, restrita','EJR'),('REJR_Exposure','Exposição heterogênea, restrita','EJR'),('Q_Equilibrium','Referência condicional, flexível','Q'),('Q_Exposure','Exposição heterogênea, flexível','Q')]:
    interrows.append([label]+[num(get(f'B_FX_{h}',mod,bm).rmse_ratio) for h in [12,36,60]])
pages.append(r'\section*{11--13. Interações, referência de equilíbrio e heterogeneidade}'+tab(['Especificação / sua base','12m','36m','60m'],interrows,size=r'\footnotesize')+r'''
\textbf{Interação.} O modelo contém $Q$, o preço global $G$ e $QG$, centralizados de acordo com a informação disponível. Isso permite que a inclinação preditiva em Q dependa do estado das commodities. Outra versão troca G pela proxy comercial. A melhora preditiva não foi geral: a interação comercial piorou EJR nos quatro horizontes, e a global permaneceu pior que nenhuma mudança.

Um coeficiente de interação não identifica a velocidade causal de convergência. Ele apenas permite uma relação condicional diferente e pergunta se essa flexibilidade prevê melhor. Nesta implementação, a complexidade adicional não foi recompensada de maneira consistente.

\textbf{Referência de equilíbrio condicional.} Primeiro projetamos Q no índice comercial e nos interceptos de país usando somente a amostra de treino; depois usamos o resíduo para prever câmbio. A hipótese é que uma parcela do desvio real possa acompanhar fundamentos de commodities. Esse procedimento impõe uma restrição de previsão; não estima um equilíbrio estrutural nem prova cointegração.

Comparado à regressão Q com os mesmos interceptos e regularização, o resíduo teve mudanças mínimas em 12 meses e piora em 36/60 meses. Acrescentar a proxy disponível não resolveu a dificuldade de distinguir desalinhamento de mudança de fundamentos.

\textbf{Exportadores e importadores.} A exposição líquida $e_i$ modifica a resposta ao global; na família flexível também modifica a inclinação em Q. Trata-se de heterogeneidade contínua, sem separar retrospectivamente países pelos resultados. A família não superou a referência simples de forma geral.

\textbf{Limite econômico.} Pesos fixos de três anos antigos, quatro cestas e seis moedas podem ser insuficientes para descrever mudanças estruturais de comércio. A ausência de ganho neste exercício não rejeita a hipótese de que fundamentos alterem o câmbio de equilíbrio; rejeita apenas a ideia de que estas especificações entregaram melhora preditiva robusta.
''')
inflrows=[]
for h in HH:
    for mod,label in [('history','História própria'),('Commodity','História + commodities'),('Q_Global','História + Q + global')]:
        x=get(f'C_inflation_{h}',mod);inflrows.append([str(h),label,num(x.rmse_ratio),num(x.rmse_rw)])
pages.append(r'\section*{14. O ajuste aparece no câmbio ou na inflação?}'+fig('inflation','A história própria é a referência exigente para inflação. Nenhuma mudança é mais fácil de superar quando diferenças de inflação são persistentes.')+tab(['h','Modelo','RMSE / história','RMSE / inflação zero'],inflrows)+r'''
Commodities acrescentadas à inflação passada reduziram o erro agregado em aproximadamente 1,2\% em 12 meses, quase não alteraram 3/36 meses e pioraram ligeiramente 60 meses. O ganho incremental não se mostrou robusto após multiplicidade. Superar inflação zero é sobretudo mérito da história própria, não da commodity.

Os resultados não permitem concluir causalmente por qual canal o câmbio real se ajusta. A identidade entre câmbio nominal, preços relativos e câmbio real não identifica choques. A evidência preditiva desta extensão é mais interessante no câmbio nominal de alguns países e horizontes do que no incremento de previsão da inflação.
''')
pages.append(r'''
\section*{15. Direção, horizonte e interpretação da descoberta}
\textbf{Nos horizontes curtos,} de três e doze meses, os seis câmbios reais não produziram uma melhora geral nas previsões de commodities. Adicionar commodities ao EJR também não resolveu a previsão cambial. São resultados compatíveis com pouca informação incremental útil nestas especificações, não uma demonstração universal de imprevisibilidade.

\textbf{Em três anos,} câmbios conjuntos frequentemente corrigem erros da regressão baseada na história da commodity, mas raramente superam nenhuma mudança. Na direção commodities $\rightarrow$ câmbio, o componente específico melhora EJR, porém o RMSE agregado ainda fica ligeiramente acima da referência simples.

\textbf{Em cinco anos,} o componente específico é o candidato mais interessante. Ele melhora o EJR e, na amostra integral, supera nenhuma mudança. A falta de estabilidade sem BRL e nas origens recentes, além do reduzido número de episódios independentes, impede declarar previsibilidade geral comprovada.

\textbf{Não há simetria automática.} Uma variável ajudar a prever outra em determinada especificação não implica a relação inversa, nem uma cadeia causal. Commodities são médias mensais com atraso de divulgação, enquanto o câmbio é fechamento mensal. Os alvos de commodities também têm bases conhecidas em $t-1$ ou $t-2$; os h não são intervalos idênticos desde o último preço observado.

\textbf{A contribuição mais defensável para o trabalho.} Mostrar que decompor a informação de commodities em global e composição comercial pode melhorar uma previsão EJR específica, sem confundir isso com superar todos os benchmarks. Essa pergunta é menor e mais precisa do que afirmar que commodities e câmbio se antecipam de forma generalizada.

\textbf{Próxima hipótese a congelar.} Manter Q, fator global e componente comercial específico, com a mesma definição de dados e pesos, e avaliar em dados novos ou em outro universo de países escolhido previamente. Uma ampliação para as moedas exportadoras estudadas por Chen--Rogoff--Rossi seria uma validação externa relevante; ela não foi simulada como se já tivesse sido executada neste relatório.

O presente estudo inclui seis moedas da replicação anterior, não o universo completo do artigo de commodities. A unidade do trabalho continua sendo a previsão macroeconômica, sem conversão dos resultados em recomendação financeira.
''')
validation=pd.read_csv(H/'tables/validation.csv');aud=pd.read_csv(H/'tables/audit.csv')
pages.append(r'\section*{Auditoria, disponibilidade e limites dos dados}'+fr'\textbf{{{len(validation)} verificações de integridade passaram.}} '+r'''
Foram conferidos: equivalência do EJR restrito ao original; invariância ao truncar o futuro nos modelos regular, PCA, interação e referência condicional; invariância das previsões antigas ao corromper rótulos e preditores futuros; identidade do câmbio real; calendário e preços; pesos anteriores à estimação; ausência de índices oficiais com pesos futuros; hashes de fontes; unicidade das previsões e preservação dos dois estudos anteriores.

\textbf{Disponibilidade.} A trilha registra o primeiro e último mês de treino e quando o último alvo ficou disponível. Todas as datas admitidas são anteriores à origem. Commodity nominal usa um mês de atraso e real usa dois; CPI tem dois meses. Isso disciplina a cronologia, mas não reconstrói todos os vintages históricos. Revisões nas séries e nos dados comerciais ainda podem afetar o que um pesquisador realmente teria observado.

\textbf{Uma inconsistência documental foi examinada.} O XLSX contém uma aba de diferenças, incluindo soja de julho de 2026 com dois valores. Usamos 478 USD/t da aba Monthly Prices, confirmado no PDF oficial da Pink Sheet de setembro de 2026 [4]. Os arquivos brutos são preservados. As demais cotações selecionadas não apareceram nessa lista de diferenças.

\textbf{Mudanças de definição.} As descrições da própria fonte registram alterações de qualidade/local de entrega e de tipo de cotação, inclusive em soja, trigo e ferro. O passado do ferro contém referências contratuais e a série selecionada é apresentada como cfr spot; isso exige cautela com a homogeneidade do histórico. A fonte não foi tratada como um contrato financeiro imutável.

\textbf{Quantidade não é identificação.} O arquivo tem muitas previsões porque cruza modelos, moedas, commodities e horizontes. Isso não cria novas realizações macroeconômicas. A análise de uma commodity não repete o mesmo alvo em seis linhas para inflar o tamanho da amostra. No painel cambial, as perdas são agregadas por data antes da inferência.

\textbf{Comparações múltiplas.} Só um ganho incremental com p Holm abaixo de 5\% permaneceu na grade principal: Q do euro condicionado ao fator nominal comum, para milho real em 36 meses, contra o benchmark que já contém o fator dólar. Seu RMSE foi 1,124 vezes o de nenhuma mudança, e não o superou estatisticamente. Um p pequeno relativo a uma base específica não equivale a sucesso geral de previsão.

Os intervalos dos candidatos são pós-seleção, condicionais às previsões e não constituem inferência de uma réplica exata do bootstrap dos artigos. Resultados longos são apresentados como evidência exploratória, com suas limitações efetivas.
''')
for unit in ['nominal','real']:
    rows=[]
    for c in COM:
        for h in HH:
            x=get(f'A_{c}_{unit}_{h}','Q_all');y=get(f'A_{c}_{unit}_{h}','Q_average')
            rows.append([names[c],str(h),str(int(x.n_dates)),num(x.rmse_ratio),num(x.rmse_rw),num(y.rmse_ratio),num(y.rmse_rw)])
    pages.append(r'\section*{Apêndice A. Grade de commodities: '+('nominal' if unit=='nominal' else 'real')+'}'+r'Conjunto = seis Q na regressão; média = seis previsões individuais.\par '+tab(['Alvo','h','Datas','Conj./hist.','Conj./RW','Média/hist.','Média/RW'],rows,size=r'\footnotesize')+r'''
Valores menores que 1 indicam melhora. Datas são origens com alvo realizado e modelos pareados; não são episódios independentes. O arquivo completo inclui Q individual, nominal em nível/variação, preços relativos, controle dólar, fatores e grupos comerciais, além do período recente. Não há ajuste de uma estratégia financeira.
''')
bm=M[(M.block=='B')&(M.country=='POOL')&(M.period=='all')&(M.benchmark=='Q')].model.unique()
rows=[[esc(mod)]+[num(get(f'B_FX_{h}',mod,'Q').rmse_rw) for h in HH] for mod in bm]
pages.append(r'\section*{Apêndice B. Toda a grade cambial contra nenhuma mudança}'+tab(['Modelo / RW','3m','12m','36m','60m'],rows,size=r'\footnotesize')+r'''
\texttt{REJR}: extensão estrita da replicação sem intercepto; \texttt{Q}: regressão flexível com efeitos por país e ridge. \texttt{Global}: cesta global real; \texttt{Trade}: proxy comercial; \texttt{Specific}: componente comercial líquido do global. \texttt{Mom}: variação de 12 meses; \texttt{Interaction}: produto com Q; \texttt{Exposure}: heterogeneidade pela exposição; \texttt{Equilibrium}: resíduo da projeção condicional. \texttt{AR} usa variação cambial passada. As datas podem diferir entre especificações devido ao treino, mas cada razão tem benchmark pareado.

Os p-valores completos, comparações adicionais contra EJR/Q, países individuais, datas iniciais/finais e janela recente estão em \texttt{tables/metrics.csv}. Todos os modelos da grade inicial foram mantidos, inclusive os que pioram fortemente os erros.
''')
pages.append(r'''
\section*{Fontes e reprodução}
\begin{enumerate}[leftmargin=1.7em,itemsep=7pt]
\item Eichenbaum, M.; Johannsen, B. K.; Rebelo, S. \emph{Monetary Policy and the Predictability of Nominal Exchange Rates}. NBER WP 23158, revisão de 2019; artigo e slides da aula 8 já presentes no repositório. \href{https://www.nber.org/papers/w23158}{Página do trabalho}.
\item Chen, Y.; Rogoff, K.; Rossi, B. \emph{Can Exchange Rates Forecast Commodity Prices?} Quarterly Journal of Economics, 125(3), 1145--1194, 2010. \href{https://scholar.harvard.edu/sites/scholar.harvard.edu/files/rogoff/files/125-3-1145.pdf}{Texto disponibilizado pelos autores}.
\item Chen, Rogoff e Rossi. \emph{Can Exchange Rates Forecast Commodity Prices? An Update}, fevereiro de 2014. \href{https://scholar.harvard.edu/files/rogoff/files/crr2014a.pdf}{Atualização dos autores}.
\item Banco Mundial, Commodity Markets / Pink Sheet. XLSX histórico e PDF de setembro de 2026. \href{https://www.worldbank.org/en/research/commodity-markets}{Página oficial}; \href{https://thedocs.worldbank.org/en/doc/74e8be41ceb20fa0da750cda2f6b9e4e-0050012026/related/CMO-Pink-Sheet-September-2026.pdf}{PDF conferido}. Descrições e pesos oficiais constam no próprio XLSX.
\item Banco Mundial, World Development Indicators, API pública. Participações de combustíveis, alimentos, matérias-primas agrícolas e minérios/metais nas exportações/importações, e valores totais de comércio, 1994--1996. Indicadores TX/TM.VAL.FUEL.ZS.UN, FOOD.ZS.UN, AGRI.ZS.UN, MMTL.ZS.UN e MRCH.CD.WT. \href{https://api.worldbank.org/v2/indicator/TX.VAL.FUEL.ZS.UN?format=json}{Exemplo de metadados}; URLs completas dos dez downloads no manifesto.
\item Gruss, B.; Kebhaj, S. \emph{Commodity Terms of Trade: A New Database}. IMF WP/19/21, 2019. \href{https://www.imf.org/-/media/files/publications/wp/2019/wp1921.pdf}{Metodologia}; \href{https://data.imf.org/en/datasets/IMF.RES:CTOT}{Base CTOT}. Referência metodológica; seus índices não foram usados como entradas.
\end{enumerate}

\textbf{Reprodução.} Pasta \texttt{third/}. Executar \texttt{run.ps1} na raiz do repositório para preparar os dados salvos, estimar a grade principal, rodar sensibilidades, validar e gerar a fonte/PDF. Não é necessário novo download. O Python e o Tectonic são os executáveis do projeto; não foi adicionada dependência. XLSX é lido como XML sem modificar o arquivo.

\textbf{Resultados auditáveis.} \texttt{metrics.csv} contém todas as comparações; \texttt{predictions.csv.gz}, as previsões individuais; \texttt{audit.csv}, o relógio de cada ajuste. \texttt{sensitivity.csv} e os arquivos de intervalos/fases guardam a exploração completa. \texttt{data/manifest.json} registra URLs, hashes e falhas de download dos PDFs externos, consultados na web. Dados usados na estimação foram todos baixados e preservados.

\textbf{Preservação.} Os 166 arquivos anteriores congelados no início permanecem idênticos. Os hashes, o protocolo e o registro de exploração documentam o escopo. A fonte LaTeX está incluída no pacote; as oito figuras têm versões vetoriais PDF e PNG.
''')

pre=r'''\documentclass[11pt,a4paper]{article}
\usepackage[T1]{fontenc}\usepackage[utf8]{inputenc}\usepackage[brazil]{babel}
\usepackage{lmodern,microtype,amsmath,booktabs,array,graphicx,float,caption,xcolor,enumitem,fancyhdr,hyperref}
\usepackage[margin=1.9cm,top=1.9cm,bottom=1.9cm]{geometry}
\definecolor{navy}{HTML}{164E63}\definecolor{light}{HTML}{EDF4F6}
\hypersetup{colorlinks=true,linkcolor=navy,urlcolor=navy,pdftitle={Quem antecipa quem? Câmbio e commodities},pdfauthor={Macroeconomia Aplicada}}
\setlength{\parindent}{0pt}\setlength{\parskip}{5pt}\setlength{\emergencystretch}{3em}
\setlength{\tabcolsep}{5pt}\renewcommand{\arraystretch}{1.12}
\setlength{\intextsep}{6pt}\setlength{\textfloatsep}{8pt}
\captionsetup{font=small,labelfont={bf,color=navy},skip=4pt}
\setlist{nosep}\pagestyle{fancy}\fancyhf{}\setlength{\headheight}{14pt}
\fancyhead[L]{\small\color{navy}Quem antecipa quem?}\fancyhead[R]{\small Câmbio e commodities | Terceiro estudo}
\fancyfoot[C]{\small\thepage}\begin{document}
'''
(H/'relatorio_terciario.tex').write_text(pre+'\n\\clearpage\n'.join(pages)+'\n\\end{document}\n',encoding='utf8')
print('Designed pages:',len(pages),'Figures: 8','Metrics:',len(M),'Predictions:',len(O),'Audit fits:',len(aud))
