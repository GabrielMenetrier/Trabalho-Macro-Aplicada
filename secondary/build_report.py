"""Render a separate LaTeX report and publication-quality vector figures."""
from pathlib import Path
import os,json
R=Path(__file__).resolve().parents[1]; H=R/'secondary'
os.environ['MPLCONFIGDIR']=str(R/'tmp/matplotlib')
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick

plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,'axes.spines.right':False,'axes.labelcolor':'#334155','text.color':'#163447','axes.titleweight':'bold','axes.grid':True,'grid.alpha':.18,'savefig.bbox':'tight','pdf.fonttype':42})
colors=['#156078','#dd8f28','#5d7d3a','#a5495a','#7969aa','#7c8893']
plt.rcParams['axes.prop_cycle']=matplotlib.cycler(color=colors)
def read(n):return pd.read_csv(H/'tables'/f'{n}.csv')
def figsave(name,fig):
    fig.savefig(H/'figures'/f'{name}.pdf');fig.savefig(H/'figures'/f'{name}.png',dpi=170);plt.close(fig)
def dates(x):return pd.PeriodIndex(x,freq='M').to_timestamp()
def pct(ax):ax.yaxis.set_major_formatter(mtick.PercentFormatter(1))
def path(r):return np.cumprod(1+np.asarray(r))
def draw(r):
    nav=path(r);return nav/np.maximum.accumulate(np.r_[1,nav])[1:]-1

sm=read('strategy_metrics'); vr=read('variation_metrics'); pm=read('prediction_metrics'); hm=read('hedge_metrics'); hv=read('hedge_variations')
hm['rule']=hm['rule'].fillna('None')
sr=read('strategy_returns').pivot(index='month',columns='strategy',values='net')
rr=read('variation_returns').set_index('month'); rr=rr.loc['2013-01':]
fig,axes=plt.subplots(2,1,figsize=(9,5.5),sharex=True,gridspec_kw={'height_ratios':[1.6,1]})
for name,label in [('Carry','Carry'),('Gate_total','Entrada por retorno total'),('Size_signal','Exposição gradual'),('Gate_FX','Entrada por câmbio')]:
    axes[0].plot(dates(sr.index),100*path(sr[name]),label=label,lw=1.7);axes[1].plot(dates(sr.index),draw(sr[name]),lw=1.3)
axes[0].set_ylabel('Patrimônio em USD · início = 100');axes[1].set_ylabel('Queda desde o pico');pct(axes[1]);axes[0].legend(loc='upper left',fontsize=8,ncol=2);fig.tight_layout();figsave('carry_paths',fig)

tim=vr[(vr.family=='timing')&(vr.period=='common')&(vr.cost==1)].copy()
tim['cutoff']=tim.name.str.extract(r'Gate_([^_]+)')[0].astype(float)*100;tim['ma']=tim.name.str.extract(r'ma(\d+)')[0].astype(int)
grid=tim.pivot(index='cutoff',columns='ma',values='sharpe')
fig,axes=plt.subplots(1,2,figsize=(9,3.4),gridspec_kw={'width_ratios':[1,1.45]})
im=axes[0].imshow(grid.to_numpy(),cmap='YlGnBu',vmin=0,vmax=1)
axes[0].set_xticks(range(3),grid.columns);axes[0].set_yticks(range(len(grid)),[f'{x:g}%' for x in grid.index]);axes[0].set_xlabel('Média do sinal (meses)');axes[0].set_ylabel('Retorno anual mínimo');axes[0].grid(False);axes[0].set_title('Sharpe por regra de entrada',fontsize=11)
for i in range(len(grid)):
    for j in range(3):
        val=grid.iloc[i,j];axes[0].text(j,i,'--' if not np.isfinite(val) else f'{val:.2f}',ha='center',va='center',color='white' if val>.65 else '#163447')
for name,label in [('Carry','Carry'),('Gate_0.02_ma6','Limiar 2%, média 6m'),('Size_hist24_cap1','Exposição gradual')]:axes[1].plot(dates(rr.index),100*path(rr[name]),label=label,lw=1.6)
axes[1].set_title('Mesmas datas: 2013-2026',fontsize=11);axes[1].set_ylabel('Patrimônio em USD');axes[1].legend(fontsize=8);fig.tight_layout();figsave('timing_grid',fig)

obs=read('prediction_observations'); fig,axes=plt.subplots(1,2,figsize=(9,3.2))
for model,label in [('base','Juros + vol. + momentum'),('ejr','Controles + EJR')]:
    a=obs[(obs.task=='04_carry_erased')&(obs.model==model)].copy();a['bin']=pd.cut(a.pred,np.linspace(0,1,6),include_lowest=True)
    g=a.groupby('bin',observed=True).agg(p=('pred','mean'),y=('actual','mean'),n=('actual','size'))
    axes[0].plot(g.p,g.y,'o-',label=label)
axes[0].plot([0,1],[0,1],':',color='#87929b');axes[0].set(xlim=(0,1),ylim=(0,1),xlabel='Probabilidade prevista',ylabel='Frequência realizada',title='Câmbio consumiu o carrego em 12m');axes[0].legend(fontsize=7)
sel=pm[(pm.period=='all')&(pm.model=='ejr')&pm.task.isin(['04_carry_erased','05_tail_1','05_tail_3'])]
axes[1].bar(['Carrego\nconsumido','Perda 1m\n> 2%','Perda 3m\n> 4%'],100*(sel.rmse_ratio.to_numpy()**2-1),color=colors[3]);axes[1].axhline(0,color='gray');axes[1].set(ylabel='Variação do Brier (%)',title='Adicionar EJR elevou o erro');fig.tight_layout();figsave('risk_forecasts',fig)

fig,axes=plt.subplots(1,2,figsize=(9,3))
for ax,target,title in zip(axes,['adverse','underwater'],['Maior perda antes do vencimento','Fração de meses abaixo da entrada']):
    for model,label in [('ejr','Controles + EJR'),('q','Controles + q')]:
        a=pm[(pm.model==model)&(pm.period=='all')&pm.task.str.startswith('06_'+target)].sort_values('h');ax.plot(a.h/12,a.rmse_ratio,'o-',label=label)
    ax.axhline(1,ls=':',color='gray');ax.set(xlabel='Horizonte (anos)',ylabel='RMSE / controles',title=title);ax.legend(fontsize=8)
fig.tight_layout();figsave('path_prediction',fig)

hedger=read('hedge_variation_returns').set_index('month').loc['2013-01':]
fig,axes=plt.subplots(1,2,figsize=(9,3.5))
for asset,ax in zip(['BIL','SPY'],axes):
    for rule,label in [('Fixed_0','Sem hedge'),('Fixed_0.5','Hedge fixo 50%'),('FX_ma1_b0','Hedge por câmbio'),('Smooth_FX','Hedge gradual')]:ax.plot(dates(hedger.index),100*path(hedger[f'{asset}:{rule}:2']),label=label,lw=1.5)
    ax.set(title=asset+' mantido integralmente',ylabel='Patrimônio em BRL · início = 100');ax.legend(fontsize=7)
fig.tight_layout();figsave('hedge_paths',fig)

fig,axes=plt.subplots(1,2,figsize=(9,3.3))
for ax,asset in zip(axes,['BIL','SPY']):
    a=hv[(hv.asset==asset)&(hv.period=='common')&(hv.cost==2)&hv.rule.str.startswith('Fixed_')].copy()
    ax.plot(a.vol,a.cagr,'o-',label='Hedge fixo')
    for _,row in a.iterrows():
        offset={'Fixed_0.5':(3,12),'Fixed_0.75':(-12,-12),'Fixed_1':(5,-9)}.get(row.rule,(4,4)) if asset=='SPY' else (4,4)
        ax.annotate(row.rule.split('_')[1],(row.vol,row.cagr),xytext=offset,textcoords='offset points',fontsize=8)
    for rule,label,color in [('FX_ma1_b0','Sinal cambial',colors[1]),('Smooth_FX','Sinal gradual',colors[2]),('Total_b0','Sinal com juros',colors[3])]:
        b=hv[(hv.asset==asset)&(hv.rule==rule)&(hv.period=='common')&(hv.cost==2)].iloc[0];ax.scatter(b.vol,b.cagr,color=color,label=label,s=40)
    ax.set(title=asset,xlabel='Volatilidade anual',ylabel='Retorno anual composto');pct(ax);ax.xaxis.set_major_locator(mtick.MaxNLocator(4));ax.xaxis.set_major_formatter(mtick.PercentFormatter(1,decimals=1));ax.legend(fontsize=7)
fig.tight_layout();figsave('hedge_frontier',fig)

fig,ax=plt.subplots(figsize=(9,3.4))
a=pm[(pm.period=='all')&(pm.model=='ejr')&((pm.task.str.startswith('11_'))|(pm.task.str.startswith('12_')))].copy()
labels={'11_inflation_12':'Inflação · 1 ano','11_inflation_36':'Inflação · 3 anos','11_inflation_60':'Inflação · 5 anos','12_bond_1':'IMAB11 · 1 mês','12_bond_12':'IMAB11 · 1 ano','12_exporter_bank_1':'VALE - Itaú · 1 mês','12_exporter_bank_12':'VALE - Itaú · 1 ano','12_exporter_bank_alt_1':'Suzano - BB · 1 mês','12_exporter_bank_alt_12':'Suzano - BB · 1 ano'}
ax.barh([labels[x] for x in a.task],a.rmse_ratio,color=[colors[2] if x<1 else colors[3] for x in a.rmse_ratio]);ax.axvline(1,color='#163447',ls=':');ax.set(xlim=(.9,1.4),xlabel='RMSE com EJR / RMSE com controles');ax.invert_yaxis();fig.tight_layout();figsave('other_targets',fig)

def esc(s):
    return str(s).replace('\\',r'\textbackslash{}').replace('&',r'\&').replace('%',r'\%').replace('_',r'\_').replace('#',r'\#')
def fmt(x,kind='pct'):
    if pd.isna(x):return '--'
    if kind=='pct':return f'{x*100:.2f}'.replace('.',',')
    if kind=='num':return f'{x:.3f}'.replace('.',',')
    if kind=='int':return str(int(x))
    return esc(x)
def table(headers,rows,align=None,size=r'\small'):
    if align is None:align='l'+'r'*(len(headers)-1)
    return size+r'\begin{center}\begin{tabular}{'+align+'}\\toprule\n'+' & '.join(headers)+r' \\ \midrule'+'\n'+'\n'.join(' & '.join(row)+r' \\' for row in rows)+'\n'+r'\bottomrule\end{tabular}\end{center}\normalsize'+'\n'
def tmet(df,namecol,labels=None):
    return table(['Regra','CAGR (\\%)','Vol. (\\%)','Sharpe','DD (\\%)','Exp. (\\%)'],[[esc(labels.get(row[namecol],row[namecol]) if labels else row[namecol]),fmt(row.cagr),fmt(row.vol),fmt(row.sharpe,'num'),fmt(row.maxdd),fmt(row.exposure)] for _,row in df.iterrows()])
def ptable(tasks):
    a=pm[(pm.period=='all')&(pm.model=='ejr')&pm.task.isin(tasks)];rows=[]
    for _,row in a.iterrows():
        raw=pm[(pm.task==row.task)&(pm.period=='all')&(pm.model=='q')].iloc[0]
        rows.append([esc(tasklabels[row.task]),fmt(row.n_dates,'int'),fmt(row.rmse_ratio,'num'),fmt(raw.rmse_ratio,'num'),fmt(row.p_holm,'num')])
    return table(['Alvo / horizonte','Datas','EJR / base','q / base','p Holm'],rows)
tasklabels={'04_carry_erased':'Carrego consumido / 12m','05_tail_1':'Perda >2\\% / 1m','05_tail_3':'Perda >4\\% / 3m',
 '06_adverse_12':'Perda no caminho / 12m','06_adverse_36':'Perda no caminho / 36m','06_adverse_60':'Perda no caminho / 60m',
 '06_underwater_12':'Tempo submerso / 12m','06_underwater_36':'Tempo submerso / 36m','06_underwater_60':'Tempo submerso / 60m',
 **labels}
# Labels stored as plain text; table escaping handles percent once.
tasklabels['05_tail_1']='Perda >2% / 1m';tasklabels['05_tail_3']='Perda >4% / 3m'
def figure(name,caption,width='.98'):
    return '\\begin{figure}[H]\\centering\\includegraphics[width='+width+'\\linewidth]{figures/'+name+'.pdf}\\caption{'+caption+'}\\end{figure}\n'
pages=[]
pages.append(r'''
\thispagestyle{empty}
{\large\color{navy}MACROECONOMIA APLICADA \quad | \quad ESTUDO SECUNDÁRIO}
\vspace{1cm}

{\Huge\bfseries\color{navy}Quando fazer carrego?}
\vspace{.35cm}

{\Large Doze testes sobre previsão cambial, risco e portfólio}
\vspace{.5cm}

Real, euro, iene, libra, dólar canadense e coroa sueca.\\
Resultados até agosto de 2026. Relatório preparado em 10 de setembro de 2026.
\vspace{.6cm}

\textbf{Resultado central.} A previsão tem algum potencial para regular a exposição ao carry e o hedge de ativos em dólar. Nesta amostra, ela não demonstrou capacidade adicional de antecipar perdas do carry, inflação ou retornos locais de ações. Uma previsão de valorização favorável não equivale a comprovar que o carrego ficou seguro.

\textbf{O que merece aprofundamento.} Em datas comuns, de janeiro de 2013 a agosto de 2026, dimensionar gradualmente o carry elevou o Sharpe de 0,661 para 0,728. Uma variação com retorno previsto mínimo de 2\% ao ano e média de seis meses alcançou Sharpe 0,883, com exposição em 35,4\% dos meses. Esses ganhos foram encontrados explorando a mesma história; não são validação independente.

\textbf{Hedge sem abandonar a bolsa.} Manter SPY e ajustar só sua proteção cambial preservou o retorno do ativo americano. Um hedge gradual teve CAGR em reais de 25,23\%, contra 23,45\% do hedge fixo de 50\%, mas o intervalo para a diferença de retorno médio inclui zero. O hedge fixo já explica boa parte da proteção.

\textbf{O que foi entregue.} Doze famílias de testes; 32 carteiras e controles na rodada principal; 43 especificações de carry e 62 combinações de ativo, hedge e custo na exploração; 18 alvos preditivos, cada um comparando controles, controles + EJR e controles + q. Resultados integrais em CSV, código, dados adicionais e auditoria acompanham este PDF.

\vfill
\colorbox{light}{\parbox{.94\linewidth}{\textbf{Documento separado.} O relatório principal, suas figuras, seus dados e seu pacote de entrega permanecem idênticos. Esta extensão é exploratória e não altera as conclusões originais.}}
''')
pages.append(r'''
\section*{Como os testes foram construídos}
O objeto é o valor da informação cambial em decisões de investimento, sem interpretação causal. A especificação principal reaproveita a previsão EJR de 60 meses, estimada em expansão. EJR refere-se a Eichenbaum, Johannsen e Rebelo; a versão da aula e as diferenças da replicação estão documentadas no relatório principal.

Se $S$ é a quantidade de moeda local por dólar, usamos $q=\log S+\log P_{US}-\log P_{local}$. A previsão $f_{t,60}$ é a variação esperada de $\log S$ em 60 meses. O componente cambial mensal para uma aplicação estrangeira avaliada em USD é $-f_{t,60}/60$. O escore de retorno esperado é
\[ a_{c,t}=\underbrace{\log(1+i^m_{c,t})-\log(1+i^m_{US,t})}_{k_{c,t}:\ \text{diferencial de juros}}-f_{c,t,60}/60. \]
Dividir a previsão longa por 60 é uma regra de alocação, não uma prova de previsibilidade mensal. Os juros anuais são convertidos geometricamente para o mês. A carteira carry compra as duas moedas de maior diferencial e vende as duas de menor diferencial, com pesos +25\%, +25\%, -25\%, -25\%.

\textbf{Contabilidade.} Todas as carteiras cambiais recebem caixa USD, resultado cambial, diferencial de juros e pagam custos. O retorno de um ativo estrangeiro em USD é $(1+i^m_c)S_{t-1}/S_t-1$; a posição tem funding em USD. O fator de interação entre câmbio e juros é mantido. Não há uma estratégia que receba somente a variação do spot.

\textbf{Relógio da informação.} Sinal no fechamento $t$, execução no fechamento $t+1$, primeiro retorno contabilizado em $t+2$. CPI tem dois meses de defasagem e preenchimento de, no máximo, uma referência ausente com o passado. No EJR, o último retorno utilizado na estimação termina até $t-1$. Novos modelos só aprendem alvos completamente realizados, também com margem de um mês; inflação recebe mais dois meses de divulgação. Normalizações, medianas e percentis são calculados com o passado.

\textbf{Custos e implementação.} Custos de câmbio de uma via: BRL 10 bps; SEK 3 bps; EUR, JPY, GBP e CAD 2 bps. Adicional de empréstimo nas posições vendidas: 50 bps anuais. Há ajuste pelo desvio dos pesos e liquidação final. No hedge, custo base de rolagem de 2 bps por mês de notional protegido, testado também a 5 e 10 bps. ETFs têm 12 bps na entrada e saída.

\textbf{Amostras e limitações.} Carteiras principais: março de 2010 a agosto de 2026, 198 meses. Variações: janeiro de 2013 a agosto de 2026, 164 meses, para evitar diferenças de aquecimento; subdivisões 2013--2018 e 2019--2026. Nenhuma é uma amostra histórica ainda não vista. Taxas oficiais são aproximações de aplicações/funding; forwards são sintéticos, sem base cambial observada. Não estão incluídos impostos, restrições de margem, limites de capital e taxas individuais de execução. As séries são snapshots atuais, não arquivos completos de vintages em tempo real.
''')
pages.append(r'''
\section*{O que cada uma das 12 ideias mostrou}
\begin{enumerate}[leftmargin=1.7em,itemsep=8pt]
\item \textbf{Quando fazer carrego.} Exigir retorno total previsto positivo melhorou modestamente o resultado, ao evitar só sete meses. Exigir valorização cambial favorável ficou em caixa a maior parte do tempo.
\item \textbf{Quais posições manter.} Filtrar pares pelo retorno total preservou neutralidade, mas teve CAGR menor que carry puro. A diferença frente a exposição equivalente não é conclusiva.
\item \textbf{Quanto carregar.} Exposição gradual mostrou melhora moderada de retorno por risco, inclusive na janela comum; é uma candidata mais interessante que a troca do ranking de moedas.
\item \textbf{O câmbio vai consumir os juros?} Adicionar EJR piorou ligeiramente o Brier. Não há evidência de que o sinal reconheça melhor esse evento.
\item \textbf{O carry vai sofrer perda extrema?} Não melhorou as previsões de perdas mensais ou trimestrais. Eventos raros limitam bastante a inferência.
\item \textbf{O que acontece antes do vencimento?} Não melhorou previsões da perda máxima no caminho nem do tempo abaixo do preço de entrada. Horizontes longos deixam pouquíssimos episódios independentes.
\item \textbf{Concordância entre horizontes.} Os sinais por moeda concordaram em 100\% das observações comuns de 1, 3, 5 e 8 anos. Não são quatro confirmações independentes.
\item \textbf{Quando sair.} Saídas por desaparecimento do retorno previsto tiveram ganho pequeno frente à mesma estrutura de coortes. Não impediram o pior drawdown.
\item \textbf{Extremos e assimetria.} Filtrar apenas a ponta comprada funcionou melhor que exigir moeda cara na ponta vendida. Exigir simultaneamente os dois extremos não gerou operações nesta amostra.
\item \textbf{Hedge do ativo em dólar.} É uma aplicação economicamente distinta e útil: preserva SPY/BIL. Há candidatos interessantes, mas a vantagem do sinal sobre hedge fixo não ficou estatisticamente estabelecida.
\item \textbf{Prever inflação.} O sinal não reduziu o erro da inflação relativa em nenhum dos três horizontes testados.
\item \textbf{Prever outros ativos.} Ações não mostraram melhora. IMAB11 teve redução ínfima do erro anual, baseada em apenas 14 origens sobrepostas; insuficiente para uma conclusão.
\end{enumerate}
''')
mainnames=['Carry','EJR_rank','Gate_FX','Gate_total','Pair_total','Pair_FX','Size_signal','Size_vol','Size_signal_vol']
mainlabels={'Carry':'Carry puro','EJR_rank':'Ranking por EJR + juros','Gate_FX':'Entrada por câmbio','Gate_total':'Entrada por retorno total','Pair_total':'Filtro por par: total','Pair_FX':'Filtro por par: câmbio','Size_signal':'Exposição gradual','Size_vol':'Exposição por volatilidade','Size_signal_vol':'Gradual + volatilidade'}
a=sm[(sm.period=='all')&sm.strategy.isin(mainnames)].set_index('strategy').loc[mainnames].reset_index()
pages.append(r'\section*{1--3. Entrada, seleção e tamanho do carry}'+tmet(a,'strategy',mainlabels)+r'''
CAGR e volatilidade anuais; drawdown (DD) desde o pico do patrimônio em USD; exposição bruta média. O Sharpe usa excesso sobre caixa USD. O filtro agregado aplica a previsão à carteira carry original: $A_t=\sum_c w^{carry}_{c,t}a_{c,t}$. Entrada por câmbio usa somente $\sum w(-f/60)>0$ para decidir a exposição, mas recebe juros no retorno realizado. Entrada total usa $A_t>0$.

O filtro por pares compara a moeda de maior juro com a de menor juro, depois a segunda com a segunda menor; cada par aprovado mantém suas pernas de 25\%. Não há concentração automática dos pesos restantes. Exposição gradual usa $\min(1,\max(0,A_t/\operatorname{mediana}_{u<t}A_u))$, após 24 observações. A regra de volatilidade limita a exposição para uma meta de 4\% anual, sem alavancar acima de 1.
'''+figure('carry_paths','Patrimônio com custos e quedas desde o pico. A exposição gradual passa inicialmente por aquecimento; a comparação em datas comuns aparece a seguir.')+r'''
\textbf{Leitura.} A entrada por câmbio reduz muito o drawdown porque praticamente não carrega: exposição de 14,1\%. Isso, isoladamente, não demonstra habilidade para antecipar perdas.
''')
cond=read('conditions')
ct=table(['Condição conhecida antes','Meses','Excesso a.a. (\\%)','Meses negativos (\\%)','Perda >2\\% (\\%)'],[[esc(x.condition),fmt(x.n,'int'),fmt(x.ann_mean_excess),fmt(x.loss_fraction),fmt(x.tail2_fraction)] for _,x in cond.iterrows()],size=r'\footnotesize')
pi=read('primary_intervals'); chosen=pi[(pi.strategy.isin(['Gate_FX','Gate_total','Size_signal']))&(pi.benchmark.isin(['Carry','Gate_FX_expost_exposure','Gate_total_expost_exposure','Size_signal_expost_exposure']))]
it=table(['Regra','Comparação','Diferença (p.p./ano)','IC 95\\%'],[[esc(mainlabels[x.strategy]),'Carry' if x.benchmark=='Carry' else 'Mesma exposição média',fmt(x.annual_difference),f'[{fmt(x.low)}; {fmt(x.high)}]'] for _,x in chosen.iterrows()],size=r'\footnotesize')
pages.append(r'\section*{1. O sinal reconhece um carrego mais seguro?}'+ct+r'''
As linhas descrevem o carry puro nos meses classificados por informação disponível antes da execução. ``Excesso'' é média aritmética anualizada sobre caixa, não CAGR de uma sequência interrompida. Volatilidade alta/baixa é definida pela volatilidade móvel de 12 meses em relação à mediana passada.

Nos 28 meses com previsão cambial favorável, o retorno médio do carry foi maior, mas a frequência de meses negativos foi \textbf{42,9\%, contra 38,8\%} nos demais meses. A frequência de perdas superiores a 2\% também não caiu. Esses números não sustentam a afirmação de que a previsão tornou o risco cambial pequeno.

O sinal de retorno total ficou negativo em apenas sete meses. Foram meses ruins para carry, em média, mas representam pouquíssimos episódios. Desde 2019 a regra ficou sempre ligada e teve exatamente o mesmo retorno do carry puro.
\subsection*{Controle para simplesmente carregar menos}
'''+it+r'''
Intervalos percentis de bootstrap conjunto em blocos circulares de 12 meses, 1.999 reamostragens. São condicionais às estratégias já estimadas e não corrigidos por seleção de regras. O benchmark de mesma exposição usa a média \emph{ex post}, por isso é um diagnóstico, não uma estratégia implantável. Também foi executado o controle com média de exposição conhecida até o mês anterior; todos os resultados constam em \texttt{primary\_intervals.csv}.

\textbf{Placebo temporal.} Deslocar circularmente a sequência de exposições mantém aproximadamente sua persistência, mas altera o alinhamento com os retornos. Frações de deslocamentos com retorno superior ao observado: 25,1\% para entrada por câmbio, 10,1\% para entrada total e 11,6\% para exposição gradual. Não são p-valores de um experimento aleatório; reforçam a cautela quanto ao timing.
''')
names=['Carry','Gate_0_ma1','Gate_0.02_ma6','Size_hist24_cap1','Size_fixed0.02','Rawq_coef0.5']
vl={'Carry':'Carry','Gate_0_ma1':'Total > 0','Gate_0.02_ma6':'Total > 2\\%, média 6m','Size_hist24_cap1':'Gradual, mediana passada','Size_fixed0.02':'Gradual, referência 2\\%','Rawq_coef0.5':'q bruto, coeficiente 0,5'}
vl={k:v.replace('\\%','%') for k,v in vl.items()}
vs=vr[(vr.period=='common')&vr.name.isin(names)].set_index('name').loc[names].reset_index()
pages.append(r'\section*{Variações de entrada e tamanho: onde há potencial}'+tmet(vs,'name',vl)+figure('timing_grid','Grade completa dos 15 filtros de entrada e patrimônio das regras centrais. Mesmas datas e custos. Célula sem Sharpe significa ausência de exposição.')+r'''
O melhor Sharpe da grade de entrada foi 0,883: limiar de 2\% e média de seis meses. A regra alcançou CAGR 4,32\%, abaixo dos 4,55\% do carry, mas com volatilidade de 2,91\% contra 4,23\%. Em 2013--2018, seu Sharpe foi 0,421, abaixo de 0,445 do carry; em 2019--2026, foi 1,385 contra 0,852. O ganho concentra-se no trecho recente. O IC de 95\% para a diferença de retorno médio anual frente ao carry é [-1,87; 1,39] p.p., em blocos de 12 meses. A regra também foi testada com custos duplicados, no apêndice.

A exposição gradual por mediana teve Sharpe 0,524 e 0,908 nas duas subdivisões, contra 0,445 e 0,852 do carry. Seu ganho é menor, porém aparece nos dois trechos. Uma regra simples com q bruto alcançou Sharpe 0,733: parte do resultado não depende da estimação EJR.

\textbf{Limite da descoberta.} Esses parâmetros foram examinados após a primeira rodada. Os apêndices incluem todos os resultados, inclusive regras que não operam e alavancagem de 1,5 vez, que ampliou perdas. Os intervalos de diferença de retorno médio frente ao carry, com blocos de 12 e 36 meses, estão em \texttt{variation\_intervals.csv}; não autorizam declarar a regra vencedora comprovada.
''')
pages.append(r'\section*{4--5. Antecipar perda de carrego e eventos extremos}'+ptable(['04_carry_erased','05_tail_1','05_tail_3'])+r'''
Números abaixo de 1 indicariam melhora da raiz do Brier; acima de 1 indicam piora. ``q / base'' acrescenta o desvio real bruto aos mesmos controles. P-valores bilaterais HAC com ajuste Holm na família de comparações preditivas, incluindo as duas janelas de avaliação.

\textbf{Teste 4.} Para cada moeda, fixa-se o sentido do carry contra USD no instante do sinal. O evento ocorre quando a variação cambial adversa supera o diferencial de juros efetivamente acumulado nos 12 meses seguintes. É um diagnóstico logarítmico antes de custos; o lado do trade não muda durante o horizonte. A amostra avaliada tem 138 datas e 828 pares moeda-data, de fevereiro de 2014 a julho de 2025.

\textbf{Teste 5.} Os eventos são perdas do excesso líquido da carteira carry maiores que 2\% em um mês ou 4\% em três meses. O horizonte trimestral acumula geometricamente o excesso mensal. Custos e funding estão presentes. Os limites são fixos. Há apenas cinco eventos avaliados em cada horizonte: uma classificação que sempre dissesse ``não haverá perda extrema'' já acertaria cerca de 97\% das datas.
'''+figure('risk_forecasts','Calibração em cinco faixas fixas de probabilidade (painel esquerdo). Erro relativo ao acrescentar EJR (direita); valores positivos são piora.')+r'''
\textbf{Modelos.} Probabilidade linear com ridge, limitada a [0,01; 0,99]. Controles: juros, volatilidade e momentum, orientados no sentido do carry; o painel tem interceptos por moeda. Penalização fixa 10, padronização somente no treino e mínimo de 36 datas/100 observações no painel. Não houve busca de hiperparâmetros. O modelo-base do teste 4 já apresenta discriminação fraca (AUC 0,484); EJR não a resgata (AUC 0,475).

\textbf{Conclusão.} Um sinal de retorno médio previsto não se transformou em um bom sinal de risco. A raridade e a concentração temporal das perdas extremas impedem tratar acurácia bruta elevada como evidência de sucesso.
''')
pages.append(r'\section*{6. Perdas no caminho e tempo de espera}'+ptable([x for x in tasklabels if x.startswith('06_')])+r'''
Para cada moeda, o sentido inicial do carry contra USD é mantido por 12, 36 ou 60 meses. O primeiro alvo é a maior perda acumulada em log-retorno relativo ao caixa desde a entrada; o segundo é a proporção de meses em que esse acumulado ficou negativo. Incluem juros realizados e câmbio, antes de custos de execução e spread adicional de empréstimo.

Esse teste responde a uma questão diferente da rentabilidade no vencimento: \emph{mesmo que a moeda se ajuste em cinco anos, o investidor teria suportado a trajetória?} Não se assume que ele teria liquidez ou margem ilimitadas para atravessá-la.
'''+figure('path_prediction','Adicionar EJR não reduziu os erros de trajetória. Previsões de perda são limitadas a valores não negativos e de tempo submerso a [0,1].')+r'''
Os modelos são regressões ridge em expansão, com os mesmos controles do teste 4. Na previsão de perda em 60 meses, EJR elevou o RMSE em aproximadamente 40,8\%; na fração submersa, em 40,2\%. Esses resultados são desfavoráveis, mas não devem receber precisão estatística artificial.

\textbf{Poucos episódios independentes.} Há 42 origens mensais para os alvos de cinco anos e 90 para três anos, com forte sobreposição. Um painel de seis moedas não transforma 42 datas em 252 episódios independentes. Por isso não reportamos p-valor HAC quando existem menos de três blocos do horizonte ou menos de 36 datas. Os resultados longos são descritivos.
''')
oth=['Carry','Agree_all','Agree_3of4','Exit_fixed','Exit_total','Exit_reversal','Extreme_both','Extreme_long','Extreme_short']
ol={'Agree_all':'Concordância 4/4','Agree_3of4':'Concordância 3/4','Exit_fixed':'Coortes: prazo fixo','Exit_total':'Coortes: sair se total < 0','Exit_reversal':'Coortes: reversão','Extreme_both':'Dois extremos','Extreme_long':'Extremo na comprada','Extreme_short':'Extremo na vendida','Carry':'Carry'}
oa=sm[(sm.period=='all')&sm.strategy.isin(oth)].set_index('strategy').loc[oth].reset_index()
pages.append(r'\section*{7--9. Horizontes, saída e assimetria}'+tmet(oa,'strategy',ol)+r'''
\textbf{Teste 7: concordância.} As regras 4/4 e 3/4 operam só a partir da disponibilidade dos quatro horizontes; a tabela usa janeiro de 2013 em diante para elas. O carry nas mesmas datas tem CAGR 4,55\%, Sharpe 0,661 e DD -9,09\%. Não comparar seus CAGR diretamente com os 4,11\% da linha carry, que começa em 2010.

No painel comum de 166 sinais mensais, as direções previstas por moeda nos horizontes 12, 36, 60 e 96 meses concordam em 100\% dos casos. Os horizontes compartilham o mesmo desvio $q_t-\bar q_t$ e as inclinações estimadas mantêm o mesmo sinal. A concordância não constitui uma nova fonte de informação; ambos os filtros geraram o mesmo portfólio. O filtro de câmbio agregado também foi idêntico ao filtro que usa o q bruto.

\textbf{Teste 8: saída.} Uma nova coorte recebe 1/12 do orçamento por mês e mantém as moedas escolhidas na entrada por até 12 meses. O orçamento e os pesos dentro das coortes são mantidos como fração do NAV, portanto não se trata de comprar e esquecer a quantidade física. Comparações: vencimento fixo, sair quando o retorno esperado da coorte deixa de ser positivo e sair quando ele inverte o sinal inicial. Coortes encerradas ficam em caixa até o prazo original; não há reinvestimento oportunista dentro da mesma coorte.

Sair por retorno total elevou o CAGR de 3,55\% para 3,66\%, mas manteve o drawdown de -9,92\%. Desde 2019, as três regras tiveram retornos iguais. Não apareceu uma regra robusta de saída antecipada.

\textbf{Teste 9: extremos.} Percentis de cada moeda são calculados usando apenas sua história disponível. Exige-se q acima do percentil 70 para a ponta comprada, abaixo do percentil 30 para a vendida, ou ambos; o par mantém financiamento coerente. Exigir ambos não aprovou nenhum par: o resultado é caixa USD, não sucesso de proteção. A ponta comprada produziu maior atividade e retorno; filtrar a vendida quase eliminou a exposição. A assimetria observada não prova um efeito estrutural, pois os países e seus regimes de juros diferem.
''')
ht=table(['Ativo / hedge','CAGR (\\%)','Vol. (\\%)','DD (\\%)','Hedge médio (\\%)'],[[esc(x.asset+' / '+{'None':'nenhum','Half':'50%','Full':'100%','FX':'sinal cambial','Total':'sinal com juros'}[x.rule]),fmt(x.cagr),fmt(x.vol),fmt(x.maxdd),fmt(x.mean_hedge)] for _,x in hm[hm.period=='all'].iterrows()])
pages.append(r'\section*{10. Proteger o câmbio mantendo o ativo em dólar}'+r'''
Aqui a carteira mantém 100\% de BIL ou SPY e escolhe a fração $H$ do notional inicial em USD que será vendida a termo por um mês. Não vende SPY para trocar por caixa. Os resultados são em reais, com dividendos reinvestidos nos preços ajustados.
\[ r^{BRL}_{t}=(1+r^{USD}_{A,t})\frac{S_t}{S_{t-1}}-1+H_{t-2}\left(\frac{F_{t-1,t}}{S_{t-1}}-\frac{S_t}{S_{t-1}}\right)-\text{custos}. \]
O forward sintético usa $F/S=(1+i^m_{BR})/(1+i^m_{US})$. O diferencial de juros entra no preço do hedge: não é proteção gratuita. ``Sinal cambial'' protege se $f_{BR,60}<0$; ``sinal com juros'' protege se $f_{BR,60}/60<k_{BR}$. Este último compara a valorização prevista do dólar com seu prêmio a termo.
'''+ht+r'''
Amostra de março de 2010 a agosto de 2026. DD é em reais. A proteção recai sobre o notional do ativo na abertura do mês, e não sobre seu valor final desconhecido; por isso resta a interação entre retorno do ativo e câmbio. Forwards efetivamente negociados, base cambial e margens não foram observados.

\textbf{Interpretação.} O hedge de SPY preserva a exposição à bolsa americana. A escolha entre fundos americanos e caixa brasileiro do relatório original misturava alocação de ativos e exposição cambial; esta extensão isola melhor a segunda decisão. Mesmo assim, um hedge fixo pode ser bastante competitivo: 50\% teve Sharpe 0,871 no período integral, acima de 0,812 do sinal cambial binário.

Para BIL totalmente protegido, o Sharpe contra caixa brasileiro fica muito negativo porque o excesso médio é ligeiramente negativo e sua volatilidade é minúscula. Não significa uma perda de patrimônio de magnitude comparável: o CAGR foi positivo e o drawdown mensal observado foi zero. Nesse caso, retorno excedente e custos são mais informativos que o Sharpe isolado.
''')
pages.append(r'\section*{10. Variações do hedge e risco do portfólio}'+figure('hedge_paths','Comparação com exposição permanente ao mesmo ETF, janeiro de 2013 a agosto de 2026.')+figure('hedge_frontier','Hedges fixos entre 0 e 1 versus regras condicionais. Cada ponto usa exatamente a mesma amostra; a curva conecta proporções fixas, não uma fronteira ótima estimada.')+r'''
O hedge gradual define $H_t=\operatorname{clip}(0,5-12f_{BR,60}/(60\times0,04),0,1)$: interpola entre proteção total para previsão anual de dólar menor que -2\% e nenhuma proteção acima de +2\%. Não foi calibrado para maximizar retorno.

Em SPY, a regra gradual teve CAGR 25,23\%, volatilidade 15,40\% e Sharpe 0,925, contra 23,45\%, 13,86\% e 0,901 para hedge fixo de 50\%. Em BIL, teve CAGR 11,34\%, contra 9,56\% com hedge total. Isso é potencial econômico, mas os intervalos ainda são largos. O sinal binário cambial ficou em proteção total desde 2019, sem acrescentar timing nesse trecho.
''')
hin=read('hedge_intervals');hh=hin[(hin.rule=='Smooth_FX')&(hin.benchmark.isin(['Fixed_0.5','Fixed_1','Matched_smooth']))]
hiT=table(['Ativo','Referência','Dif. média (p.p./ano)','IC 95\\%'],[[x.asset,esc({'Fixed_0.5':'Hedge 50%','Fixed_1':'Hedge 100%','Matched_smooth':'Hedge médio ex post'}[x.benchmark]),fmt(x.annual_difference),f'[{fmt(x.low)}; {fmt(x.high)}]'] for _,x in hh.iterrows()])
costT=table(['Ativo / regra','Custo (bps/mês)','CAGR (\\%)','Sharpe'],[[esc(x.asset+' / '+{'Fixed_0.5':'50%','FX_ma1_b0':'cambial','Smooth_FX':'gradual'}[x.rule]),fmt(x.cost,'int'),fmt(x.cagr),fmt(x.sharpe,'num')] for _,x in hv[(hv.period=='common')&hv.rule.isin(['Fixed_0.5','FX_ma1_b0','Smooth_FX'])].iterrows()],size=r'\footnotesize')
pages.append(r'\section*{10. Quanto da vantagem do hedge é confiável?}'+hiT+r'''
Diferença de médias aritméticas anuais do hedge gradual em relação à referência, com bootstrap em blocos de 12 meses. Não são diferenças de CAGR. O hedge médio ex post iguala a proporção média de proteção do próprio sinal gradual para um diagnóstico de exposição; não é uma regra ex ante.

Todos esses intervalos incluem zero. O maior CAGR observado não é prova de habilidade cambial. Como o hedge protege o mesmo notional inicial, a diferença aritmética entre duas regras de hedge é igual para BIL e SPY em cada mês; diferenças nos intervalos publicados refletem apenas sorteios bootstrap distintos. CAGR e risco total diferem porque o retorno do ativo é diferente.
\subsection*{Sensibilidade a custo de rolagem}
'''+costT+r'''
O custo é cobrado a cada mês sobre a fração protegida; há ainda os custos de entrada/saída do ETF. A persistência dos resultados frente a essa grade não resolve o risco de base cambial ou restrições de margem, que exigiriam preços e regras contratuais próprios.
''')
pages.append(r'\section*{11. O desvio cambial ajuda a prever inflação?}'+ptable(['11_inflation_12','11_inflation_36','11_inflation_60'])+r'''
O alvo é a inflação acumulada local menos americana entre a abertura do investimento e 12, 36 ou 60 meses depois, expressa em log anualizado. O treino respeita dois meses extras de divulgação do CPI. Os controles são inflação relativa passada de 12 meses (defasada), diferencial de juros e momentum cambial. O painel possui interceptos por moeda.

EJR não melhorou o RMSE: pioras de 11,7\%, 5,8\% e 32,0\%, aproximadamente, nos três horizontes. A versão com q bruto também é mostrada para evitar atribuir à transformação estimada uma informação que já estava no nível do câmbio real.

Este resultado é compatível, em direção, com a distinção feita por Eichenbaum, Johannsen e Rebelo entre previsibilidade de câmbio nominal e de inflação. Não é uma nova confirmação causal do mecanismo do artigo: a amostra, os alvos, os controles e a avaliação são diferentes. A revisão do working paper está disponível no NBER [1].
\section*{12. O sinal ajuda com títulos ou ações locais?}
'''+ptable([x for x in tasklabels if x.startswith('12_')])+r'''
IMAB11 representa títulos públicos brasileiros indexados à inflação [2]. O alvo é seu retorno em BRL acima do caixa brasileiro. Nos pares de ações, o alvo é o retorno ajustado em BRL de VALE3 menos ITUB4, ou SUZB3 menos BBAS3. Para 12 meses somam-se os spreads mensais; não se apresenta isso como patrimônio composto de uma carteira alavancada.

Controles: juros, inflação relativa passada, momentum do BOVA11 e momentum do próprio alvo. O uso de moeda local retira a conversão mecânica USD/BRL. Os pares têm fortes diferenças de setor, commodity, crédito e governança; não identificam um prêmio causal de ``exportadora versus empresa doméstica''.

EJR não ajudou os pares de ações. O RMSE anual de IMAB11 caiu somente 0,32\%, com \textbf{14 datas de avaliação sobrepostas}. Seu histórico começa em maio de 2019 e o aprendizado exige história adicional. Esse ganho é demasiado pequeno e a amostra demasiado curta para classificá-lo como oportunidade.
''')
pages.append(r'\section*{Outros alvos: visão conjunta e limites de inferência}'+figure('other_targets','Erro com a previsão EJR relativo ao modelo com controles. A única barra abaixo de 1, IMAB11 em 12 meses, corresponde a 14 origens sobrepostas.')+r'''
\textbf{O que ``não melhorou'' significa aqui.} As conclusões se referem aos modelos, às variáveis, aos horizontes e às amostras explicitamente testados. Não provam impossibilidade de prever inflação, crises ou retornos de ativos. Os modelos de novos alvos foram mantidos simples e com regularização fixa; não procuramos algoritmos sucessivamente até encontrar um resultado favorável.

\textbf{Revisões e disponibilidade.} Há controle de divulgação por defasagem, mas não uma base integral de vintages. Preços ajustados de ações/ETFs são usados somente em retornos e momentum: não entram como nível macroeconômico. Mudanças históricas de metodologia, ajustes por eventos e revisões ainda podem afetar a replicação em tempo real. A escolha de empresas que hoje existem também torna o teste setorial um estudo de casos, não uma carteira representativa de todo o universo histórico.

\textbf{Inferência dependente do tempo.} Os erros de previsão são agregados por data antes de calcular HAC. Isso evita contar seis moedas expostas ao mesmo choque como seis experiências independentes. Os p-valores disponíveis são ajustados por Holm sobre todas as comparações EJR/q versus base, nos períodos integral e recente. A diferença de erro pode ser negativa: um p pequeno também pode indicar piora, não sucesso.

\textbf{Exploração de estratégias.} Os intervalos de retorno não corrigem a busca de parâmetros, não reestimam o modelo EJR dentro de cada reamostragem e são condicionais ao conjunto de sinais produzido. Os 1.999 blocos de 12 meses e a sensibilidade de 36 meses medem incerteza histórica parcial. Selecionar o melhor Sharpe entre dezenas de regras infla a impressão de desempenho; as grades completas são preservadas justamente para tornar essa seleção visível.

\textbf{Decisão para o trabalho.} Os resultados justificam discutir o uso da previsão como modulador de exposição e de hedge, acompanhado de benchmarks simples. Não justificam substituir a conclusão central por uma alegação de arbitragem ou de carry seguro. Uma próxima validação teria de congelar a regra e observar dados novos ou uma amostra externa verdadeiramente não usada na seleção.
''')
# Complete grids: readable pages rather than hiding losing specifications.
allcarry=vr[vr.period=='common']
for i,chunk in enumerate([allcarry.iloc[:21],allcarry.iloc[21:]]):
    pages.append(r'\section*{Apêndice A'+str(i+1)+r'. Todas as variações de carry}'+r'Janeiro de 2013 a agosto de 2026. Nomes correspondem exatamente aos CSVs. CAGR, volatilidade, DD e exposição em porcentagem; Sharpe em unidade.\par '+tmet(chunk,'name')+r'''
\texttt{Gate\_x\_maN}: limiar $100x$\% ao ano e média de $N$ meses. \texttt{Size\_histN\_capC}: mediana histórica com mínimo $N$ e exposição máxima $C$. \texttt{Size\_fixedx}: sinal dividido por $x$ anual, limitado a 1. \texttt{Rawq\_coefx}: troca o EJR por $xq/60$. Sufixo \texttt{2cost}: custos de câmbio duplicados; spread de empréstimo mantido. Linhas de alavancagem não são recomendações de operação.

O arquivo \texttt{variation\_metrics.csv} contém os subperíodos; os intervalos de 12/36 meses estão em \texttt{variation\_intervals.csv}. As regras de histórico mínimo 6/12/24 meses coincidem na janela comum porque todas já passaram pelo aquecimento; não são evidências independentes de robustez.
''')
for asset in ['BIL','SPY']:
    a=hv[(hv.period=='common')&(hv.asset==asset)]
    t=table(['Regra','bps/mês','CAGR (\\%)','Vol. (\\%)','Sharpe','DD (\\%)'],[[esc(x.rule),fmt(x.cost,'int'),fmt(x.cagr),fmt(x.vol),fmt(x.sharpe,'num'),fmt(x.maxdd)] for _,x in a.iterrows()],size=r'\footnotesize')
    pages.append(r'\section*{Apêndice B. Todas as variações de hedge: '+asset+'}'+r'Janeiro de 2013 a agosto de 2026, retornos em reais.\par '+t+r'''
\texttt{Fixed\_x}: hedge fixo $x$. \texttt{FX\_maN\_bx}: média de $N$ meses e limiar anual $100x$\%. \texttt{Total\_bx}: compara a previsão com o diferencial de juros mais o limiar. \texttt{Smooth\_FX}: interpolação entre -2\% e +2\% anuais. \texttt{Matched\_expost/smooth/total}: hedge constante igual à proteção média observada do respectivo sinal binário/gradual/com juros, somente diagnóstico. Subperíodos em \texttt{hedge\_variations.csv}.
''')
aud=read('validation'); predau=read('prediction_audit'); metadata=json.loads((H/'data/manifest.json').read_text())
pages.append(r'''
\section*{Auditoria, fontes e reprodução}
\textbf{22 verificações de integridade passaram.} Foram checados: reprodução do carry original; invariância das previsões históricas ao truncar a amostra ou corromper o futuro; defasagem de execução; neutralidade long--short; disponibilidade estritamente anterior de todos os rótulos usados no treino; mínimo de datas; efeito da defasagem do CPI; probabilidades válidas; sinais e identidade contábil do forward; preços positivos; calendário sem duplicações; hashes de seis novas fontes e preservação dos 99 arquivos originais.

\textbf{Limite da auditoria.} Os testes verificam a implementação e a cronologia declarada; não substituem dados históricos de vintages ou forwards negociados. Os coeficientes de EJR usam médias reais estimadas com a informação disponível em cada origem. As novas regressões padronizam variáveis apenas dentro do treino. Não foram usados limiares calculados a partir dos retornos futuros para criar os sinais.

\textbf{Arquivos.} Todo o código novo está em \texttt{secondary/}. \texttt{PROTOCOL.md} registra a primeira grade; \texttt{EXPLORATION.md}, as variações após resultados. \texttt{tables/} contém métricas, retornos, previsões individuais e a trilha de disponibilidade dos rótulos. \texttt{data/manifest.json} registra URLs e SHA-256 das séries adicionais. \texttt{original\_hashes.json} permite verificar a preservação do material principal. O PDF é compilado de \texttt{secondary/relatorio\_secundario.tex}.

\textbf{Reprodução local.} Executar, na raiz, com o Python do projeto: \texttt{secondary/analyze.py}, \texttt{secondary/variations.py}, \texttt{secondary/validate.py} e \texttt{secondary/build\_report.py}; depois compilar a fonte LaTeX com Tectonic. Não é necessário baixar novamente os dados. \texttt{secondary/run.ps1} automatiza a sequência. As dependências do Python são as do \texttt{requirements-lock.txt} original.

\subsection*{Fontes e escopo dos dados}
\begin{enumerate}[leftmargin=1.7em,itemsep=5pt]
\item Eichenbaum, M.; Johannsen, B. K.; Rebelo, S. \emph{Monetary Policy and the Predictability of Nominal Exchange Rates}. NBER WP 23158, 2017, revisão de agosto de 2019. \href{https://www.nber.org/papers/w23158}{nber.org/papers/w23158}.
\item Itaú Asset / It Now. Características de IMAB11 e do índice de NTN-B IMA-B. \href{https://www.itnow.com.br/imab11/caracteristicas/}{Página oficial do fundo}.
\item State Street. SPY: exposição ao S\&P 500; BIL: títulos curtos do Tesouro americano. \href{https://www.ssga.com/us/en/individual/etfs/state-street-spdr-sp-500-etf-trust-spy}{Página oficial de SPY}. Descrições complementares e séries dos dois ETFs estão no material principal.
\item Câmbio, CPI e juros: snapshots BIS, BCB, BLS, ECB e BOJ reaproveitados do trabalho principal, com metadados em \texttt{data/}. Universo e ajustes não foram alterados.
\item Yahoo Finance, API Chart, preços ajustados diários agregados ao último fechamento mensal, até agosto de 2026. Seis downloads adicionais: IMAB11.SA (maio de 2019 em diante), VALE3.SA, ITUB4.SA, SUZB3.SA, BBAS3.SA (janeiro de 2007) e BOVA11.SA (novembro de 2008). URLs completas, arquivos brutos e hashes estão no manifesto secundário.
\end{enumerate}

\textbf{Próximo passo substantivo.} Congelar uma regra simples de exposição e uma de hedge, compará-las com controles fixos e observar dados novos. A contribuição acadêmica desta extensão é mostrar onde uma previsão macroeconômica pode informar uma decisão e onde a evidência disponível ainda não sustenta essa passagem.
''')

preamble=r'''\documentclass[11pt,a4paper]{article}
\usepackage[T1]{fontenc}\usepackage[utf8]{inputenc}\usepackage[brazil]{babel}
\usepackage{lmodern,microtype,amsmath,booktabs,array,graphicx,float,caption,xcolor,enumitem,fancyhdr,hyperref}
\usepackage[margin=1.9cm,top=1.9cm,bottom=1.9cm]{geometry}
\definecolor{navy}{HTML}{164E63}\definecolor{light}{HTML}{EDF4F6}
\hypersetup{colorlinks=true,linkcolor=navy,urlcolor=navy,pdftitle={Quando fazer carrego? Doze testes e extensões},pdfauthor={Macroeconomia Aplicada}}
\setlength{\parindent}{0pt}\setlength{\parskip}{5pt}\setlength{\emergencystretch}{3em}
\setlength{\tabcolsep}{5pt}\renewcommand{\arraystretch}{1.12}
\setlength{\intextsep}{6pt}\setlength{\textfloatsep}{8pt}
\captionsetup{font=small,labelfont={bf,color=navy},skip=4pt}
\setlist{nosep}\pagestyle{fancy}\fancyhf{}\setlength{\headheight}{14pt}
\fancyhead[L]{\small\color{navy}Quando fazer carrego?}\fancyhead[R]{\small Estudo secundário | 2026}
\fancyfoot[C]{\small\thepage}
\begin{document}
'''
(H/'relatorio_secundario.tex').write_text(preamble+'\n\\clearpage\n'.join(pages)+'\n\\end{document}\n',encoding='utf8')
print(f'Written {len(pages)} designed pages, 7 vector figures and LaTeX source.')
