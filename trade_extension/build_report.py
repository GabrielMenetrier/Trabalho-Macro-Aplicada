"""Typeset a self-contained supplement to the second report."""
from pathlib import Path
import os,json
R=Path(__file__).resolve().parents[1];H=R/'trade_extension';F=H/'figures'
os.environ['MPLCONFIGDIR']=str(R/'tmp/matplotlib')
import numpy as np,pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
M=pd.read_csv(H/'tables/prediction_metrics.csv');S=pd.read_csv(H/'tables/strategy_metrics.csv');O=pd.read_csv(H/'tables/predictions.csv.gz');B=pd.read_csv(H/'tables/strategy_returns.csv.gz')
V=pd.read_csv(H/'tables/prediction_sensitivity.csv');PV=pd.read_csv(H/'tables/policy_sensitivity.csv');I=pd.read_csv(H/'tables/strategy_intervals.csv');RI=pd.read_csv(H/'tables/risk_intervals.csv');CV=pd.read_csv(H/'tables/cohort_variations.csv')
A=pd.read_csv(H/'tables/annual_metrics.csv');AT=pd.read_csv(H/'tables/annual_tot_metrics.csv');C=pd.read_csv(H/'tables/conditions.csv');Q=pd.read_csv(H/'tables/validation.csv')
names={'price_observed':'Piora de preços observada','price_forecast':'Piora de preços prevista','structure_observed':'Composição observada','structure_forecast':'Composição prevista','real_shift36':'Revisão real em 36m','real_shift60':'Revisão real em 60m','real_depreciation60':'Depreciação real em 60m','risk_increment':'Aumento da probabilidade de perda'}
short={'Base':'Base','fixed':'Preços / pesos fixos','dynamic':'Preços / pesos variáveis','annual':'Termos agregados anuais','structure':'Composição e previsão','All':'Todas as informações'}
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':9,'axes.spines.top':False,'axes.spines.right':False,'axes.grid':True,'grid.alpha':.18,'text.color':'#163447','axes.labelcolor':'#163447','pdf.fonttype':42,'savefig.bbox':'tight','axes.prop_cycle':matplotlib.cycler(color=['#156078','#d88927','#728b4e','#a65269','#807498'])})
def fs(name,f):f.savefig(F/(name+'.pdf'));f.savefig(F/(name+'.png'),dpi=160);plt.close(f)
def n(x,d=2):return '--' if pd.isna(x) else f'{float(x):.{d}f}'.replace('.',',')
def pct(x):return n(100*x)+r'\%'
def esc(x):return str(x).replace('_',r'\_').replace('%',r'\%').replace('&',r'\&')
def tab(head,rows,size=r'\small',align=None):
    return size+r'\begin{center}\begin{tabular}{'+(align or 'l'+'r'*(len(head)-1))+r'}\toprule '+' & '.join(head)+r'\\\midrule '+'\n'+'\n'.join(' & '.join(map(str,row))+r'\\' for row in rows)+r'\bottomrule\end{tabular}\end{center}\normalsize'+'\n'
def fig(name,caption,width='.98'):return r'\begin{figure}[H]\centering\includegraphics[width='+width+r'\linewidth]{figures/'+name+r'.pdf}\caption{'+caption+r'}\end{figure}'
def get(task,model,period='all',country='POOL'):return M[(M.task==task)&(M.model==model)&(M.period==period)&(M.country==country)].iloc[0]
def st(name,control='rule',period='all'):return S[(S.name==name)&(S.control==control)&(S.period==period)].iloc[0]
def path(name,control):
    a=B[(B.name==name)&(B.control==control)].sort_values('month');return pd.PeriodIndex(a.month,freq='M').to_timestamp(),a
fig1,ax=plt.subplots(1,2,figsize=(9,3.1))
for a,typ,title in zip(ax,['real','persistent'],['Câmbio real no mês final','Média real dos últimos 12 meses']):
    for mod,label in [('fixed','Pesos fixos'),('dynamic','Pesos variáveis')]:a.plot([12,36,60],[get(f'{typ}_{h}',mod).ratio for h in [12,36,60]],'o-',label=label)
    a.axhline(1,color='gray',ls=':');a.set(title=title,xlabel='Horizonte, meses',ylabel='RMSE / base com mesma história');a.set_xticks([12,36,60]);a.legend(fontsize=8)
fig1.tight_layout();fs('real_gain',fig1)
fig1,ax=plt.subplots(figsize=(9,3.1));mods=['Base','dynamic','annual','structure','All'];x=np.arange(len(mods))
ax.bar(x-.18,[get('persistent_36',m).ratio for m in mods],.36,label='Contra base pareada');ax.bar(x+.18,[get('persistent_36',m).rw for m in mods],.36,label='Contra nenhuma mudança');ax.axhline(1,color='gray',ls=':');ax.set_xticks(x,['Base','Preços','Termos anuais','Composição','Conjunto']);ax.set_ylabel('RMSE relativo, 36 meses');ax.legend(fontsize=8);fig1.tight_layout();fs('persistent_benchmarks',fig1)
fig1,axes=plt.subplots(2,1,figsize=(9,5),sharex=True)
for control,label in [('base','Carry'),('rule','Filtro de composição'),('expost_exposure','Mesma exposição média (ex post)')]:
    d,a=path('Carry__structure_observed',control);nav=np.cumprod(1+a.net.to_numpy());axes[0].plot(d,nav,label=label);axes[1].plot(d,a.exposure,label=label)
axes[0].set_ylabel('Patrimônio, início = 1');axes[0].legend(fontsize=8);axes[1].set(ylabel='Exposição bruta',xlabel='Mês do retorno');fig1.tight_layout();fs('structure_wealth',fig1)
fig1,axes=plt.subplots(2,1,figsize=(9,5),sharex=True)
for control,label in [('base','Coortes sem saída'),('rule','Saída por risco'),('expost_exposure','Mesma exposição média (ex post)')]:
    d,a=path('Cohort__risk_increment',control);nav=np.r_[1,np.cumprod(1+a.net.to_numpy())];dd=nav/np.maximum.accumulate(nav)-1;axes[0].plot(d,nav[1:],label=label);axes[1].plot(d,100*dd[1:],label=label)
axes[0].set_ylabel('Patrimônio, início = 1');axes[0].legend(fontsize=8);axes[1].set(ylabel='Queda desde o pico, %',xlabel='Mês do retorno');fig1.tight_layout();fs('cohort_risk',fig1)
fig1,ax=plt.subplots(figsize=(9,3.5));h=list(names);x=np.arange(len(h));delta=[100*(st('Carry__'+v).mean_excess-st('Carry__'+v,'base').mean_excess) for v in h]
ax.bar(x,delta,color=['#156078' if v>=0 else '#a65269' for v in delta]);ax.axhline(0,color='gray');ax.set_xticks(x,['Preços\nobservados','Preços\nprevistos','Composição\nobservada','Composição\nprevista','Revisão\nreal 36m','Revisão\nreal 60m','Depreciação\nreal 60m','Aumento\ndo risco']);ax.set_ylabel('Diferença de excesso médio, p.p. a.a.');fig1.tight_layout();fs('all_filters',fig1)
fig1,ax=plt.subplots(figsize=(9,3.2))
for hazard in ['structure_observed','structure_forecast']:
    vals=[]
    for q in [.7,.8,.9]:
        name='Carry__'+hazard+('' if q==.8 else f'__q{q}');vals.append(st(name).sharpe-st(name,'base').sharpe)
    ax.plot([70,80,90],vals,'o-',label=names[hazard])
ax.axhline(0,color='gray',ls=':');ax.set(xlabel='Percentil histórico do alerta',ylabel='Diferença de Sharpe frente ao carry');ax.set_xticks([70,80,90]);ax.legend();fig1.tight_layout();fs('thresholds',fig1)
fig1,axes=plt.subplots(1,2,figsize=(9,3.4))
for ax,measure,title in zip(axes,['mean_excess','maxdd'],['Excesso médio anual, %','Maior queda, %']):
    controls=['base','rule','expost_exposure','vol_control'];labels=['Base EJR','+ preços','Exposição\nex post','Volatilidade']
    ax.bar(range(4),[100*st('EJR_gate__price_observed',c)[measure] for c in controls]);ax.set_xticks(range(4),labels);ax.set_title(title)
fig1.tight_layout();fs('ejr_price',fig1)

pages=[]
def page(title,text):pages.append(r'\section*{'+title+'}\n'+text)
candidate=st('Carry__structure_observed');baseline=st('Carry__structure_observed','base');cr=st('Cohort__risk_increment');cb=st('Cohort__risk_increment','base')
page('Termos de troca, câmbio real e risco do carrego',r'''\begin{center}\large Complemento ao segundo relatório\\[5pt]\normalsize Testes de previsão, alertas e saída de posições\\11 de setembro de 2026\end{center}
\vspace{8pt}
\textbf{Pergunta.} Se as condições comerciais de um país mudam, a referência de longo prazo do câmbio real pode mudar também. Uma moeda aparentemente barata pode deixar de convergir ao patamar antigo. Conseguimos antecipar isso e evitar carregar uma posição mais arriscada?

\textbf{Resposta empírica.} Há sinais úteis para investigar, mas não encontramos uma cadeia robusta que permita concluir ``previ mudança estrutural, portanto devo sair''. A previsão da composição comercial perde para a persistência. Acrescentar preços comerciais melhora modestamente alguns modelos reais longos, mas eles continuam piores que nenhuma mudança. Na carteira, mudanças \emph{já observadas} na composição e saídas por probabilidade de perda foram mais interessantes que o simples alerta de mudança prevista.
'''+tab(['Teste','Resultado principal'],[
['Prever composição comercial','RMSE 1,20 vez a persistência'],['Prever termos agregados anuais','RMSE 0,86; somente seis anos avaliados'],['Prever perda do carrego','Brier relativo 0,93; sem significância após Holm'],['Filtro de composição observada','Melhora descritiva de retorno/risco'],['Saída de coortes por risco','Menor queda; ganho médio incerto']],align='ll')+r'''
\textbf{Escopo.} Reaplicamos os testes relevantes do segundo estudo: quando carregar, tamanho, saídas, câmbio consumir juros, perda no caminho e caudas. O terceiro estudo fornece os preços e a construção comercial inicial. Os três relatórios anteriores foram preservados.

\textbf{Como ler.} Resultados são fora da amostra de estimação a cada data, mas exploratórios dentro de uma história já examinada. Uma queda menor com menos exposição não prova capacidade de prever risco. Por isso incluímos controles de exposição e de volatilidade, custos e resultados desfavoráveis.
''')
page('1. O mecanismo econômico que estamos testando',r'''
Definimos $s$ como log de moeda local por dólar e $q=s+p_{US}-p_i$. Aumento de $q$ significa depreciação real da moeda local. O retorno cambial de uma posição comprada nessa moeda tem o sinal oposto à variação de $s$.

Uma melhora dos termos de troca pode alterar renda externa, demanda e preços relativos; uma deterioração pode alterar o caminho inverso. \textbf{O sinal e a persistência são hipóteses a testar}, sem impor que todo choque produza apreciação/depreciação permanente.

Distinguimos três objetos:
\begin{enumerate}
\item \textbf{Termos de troca agregados}: preço das exportações relativamente ao preço das importações, incluindo bens além das commodities.
\item \textbf{Exposição aos preços de commodities}: quanto movimentos em energia, alimentos, matérias-primas e metais afetam a cesta comercial aproximada do país.
\item \textbf{Composição comercial}: mudanças nas participações e na exposição líquida desses grupos. Usamos valores de comércio; suas mudanças também refletem preços. Não identificam, sozinhas, transformação produtiva ou quebra estrutural.
\end{enumerate}

O teste tem três etapas distintas: prever a informação comercial; acrescentá-la à previsão real/nominal ou à probabilidade de perda; usar somente a previsão disponível para decidir a posição. Sucesso numa etapa não garante sucesso na seguinte.

\textbf{Exemplo.} Se o país passa a exportar relativamente mais energia, sua sensibilidade ao petróleo pode mudar. Mas sair de uma posição comprada apenas por detectar essa mudança ignora se o petróleo vai subir ou cair, se o câmbio já incorporou a notícia e se o diferencial de juros compensa o risco. Os testes de sinal e de risco tentam separar essas possibilidades.

\textbf{Limite do exercício.} Chamamos de ``referência real persistente'' a média realizada de 12 meses ao final do horizonte. Ela é mensurável; não equivale a estimar um câmbio de equilíbrio estrutural permanente.
''')
page('2. Dados e relógio da informação',r'''
Mantemos BRL, EUR, JPY, GBP, CAD e SEK, com conta em USD. Para o comércio do euro, Alemanha é uma proxy imperfeita; há sensibilidade sem EUR. Câmbio, CPI e juros vêm dos estudos anteriores. Preços mensais são as cestas da Pink Sheet do Banco Mundial; não são retornos de futuros.

Baixamos 11 séries anuais WDI: valores totais exportados/importados, oito participações setoriais e o índice agregado UNCTAD de termos de troca. Fluxos/participações cobrem 1994--2024 de forma suficiente para os pesos usados. A edição obtida do índice agregado tem 2005--2024 para as seis economias.

Os pesos anuais líquidos são
\[
w_{i,k,y}=\frac{X_{i,y}a^X_{i,k,y}-M_{i,y}a^M_{i,k,y}}{X_{i,y}+M_{i,y}}.
\]
No ano $Y$, admitimos apenas dados até $Y-2$ e usamos média de três anos. A sensibilidade usa $Y-3$. É uma convenção conservadora, não a data de publicação efetivamente reconstruída de cada observação.

Com preços setoriais $b_{k,t}$ em log, encadeamos
\[
Z_{i,t}=Z_{i,t-1}+\sum_k \bar w_{i,k,Y(t)-2}\,(b_{k,t-1}-b_{k,t-2}).
\]
O índice não salta apenas porque os pesos mudaram ou porque uma commodity foi cotada em outra unidade. A versão fixa usa 1994--1996. $Z$ é uma proxy de exposição comercial a preços, não o índice oficial de termos de troca agregados.

CPI entra com dois meses de atraso, com preenchimento de no máximo um mês passado, conforme o estudo original. Preços mensais entram com um mês. Nenhuma interpolação usa anos futuros. Os arquivos brutos e hashes estão no pacote.

\textbf{Vintages.} As séries foram baixadas na edição atual. Atrasar sua entrada impede uso direto do futuro, mas não desfaz revisões históricas. Participações em valor e a proxy alemã limitam a interpretação econômica.
''')
page('3. Previsão real e comparação justa',r'''
Dois alvos são previstos diretamente para $h=12,36,60$ meses:
\[
Y^q_{i,t,h}=q_{i,t+h}-q_{i,t-2},\qquad
Y^{\bar q}_{i,t,h}=\frac1{12}\sum_{j=0}^{11}q_{i,t+h-j}-q_{i,t-2}.
\]
A base é o último câmbio real inteiramente conhecido, $t-2$. Assim, o endpoint está $h$ meses depois da origem, e $h+2$ depois da base. Prever nenhuma mudança significa zero para esses alvos.

O modelo base contém desvio histórico do câmbio real e sua mudança em 12 meses, interceptos de país e ridge fixa 10, padronizada apenas no treino. Acrescentamos separadamente:
\begin{itemize}
\item nível/desvio e momentum do índice comercial de pesos fixos;
\item os mesmos termos com pesos variáveis;
\item nível e mudança dos termos agregados anuais;
\item magnitude da mudança de composição observada, magnitude prevista e cenário de reprecificação dessa composição;
\item conjunto de informações variáveis, anuais e de composição.
\end{itemize}

O cenário de reprecificação multiplica a mudança prevista dos pesos pelos preços relativos às suas médias passadas de 36 meses. Sua unidade não depende do nível arbitrário dos preços; não é uma estimativa causal de equilíbrio.

\textbf{Mesma história para o benchmark.} Para cada modelo aumentado, reestimamos a base exatamente nas mesmas linhas de treino. Sem isso, descartar anos antigos por falta de dados comerciais poderia parecer ganho informacional. O calendário de previsão e a amostra de avaliação também são pareados por comparação.

Treino em expansão, mínimo de 60 datas por moeda. O alvo real só entra depois de realizado e publicado, com buffer adicional de um mês. Modelos com informações anuais/previsões recursivas começam mais tarde. As tabelas mostram esse custo de disponibilidade.
''')
page('4. Os preços comerciais preveem o câmbio real?',tab(['h','Informação adicional','Origens','RMSE/base','RMSE/zero'],[[h,short[m],int(get(f'real_{h}',m).n_dates),n(get(f'real_{h}',m).ratio,3),n(get(f'real_{h}',m).rw,3)] for h in [12,36,60] for m in ['fixed','dynamic']])+fig('real_gain','Pequenas melhoras sobre a regressão de reversão real em horizontes longos. As linhas não mostram vitória sobre nenhuma mudança.')+r'''
Em 60 meses, pesos variáveis reduzem o erro em cerca de 5\% frente à base pareada. Porém, o RMSE continua superior a duas vezes o de prever nenhuma mudança. A inclusão melhora um modelo que está falhando nesse benchmark mais exigente.

No horizonte de 12 meses, os preços comerciais pioram a base. Trocar pesos fixos por variáveis não produz melhora uniforme. Esses resultados não sustentam que a exposição comercial, sozinha, resolva a previsão do câmbio real de longo prazo.
''')
page('5. A referência real persistente muda de forma previsível?',tab(['h','Informação','Origens','RMSE/base','RMSE/zero'],[[h,short[m],int(get(f'persistent_{h}',m).n_dates),n(get(f'persistent_{h}',m).ratio,3),n(get(f'persistent_{h}',m).rw,3)] for h in [36,60] for m in ['dynamic','annual','structure','All']])+fig('persistent_benchmarks','Modelos de 36 meses usam 128, 90 ou 54 origens conforme disponibilidade. Cada razão contra a base usa a mesma história do modelo correspondente.')+r'''
A previsão conjunta da média real futura em 36 meses fica abaixo de nenhuma mudança na janela curta em que pode ser avaliada. Mas quase não melhora sua base reestimada na mesma história: a razão é aproximadamente 1,003. Logo, a aparente vitória não pode ser atribuída à informação comercial acrescentada.

Em 60 meses, o bloco de composição e o conjunto têm somente seis origens comuns avaliáveis, todas em 2021. Não há suporte para inferência. A disponibilidade tardia é um resultado de viabilidade relevante, e não deve ser escondida combinando moedas como se fossem décadas independentes.
''')
page('6. E o câmbio nominal previsto pelo EJR?',tab(['h','Modelo','Origens','RMSE/EJR','RMSE/zero'],[[h,m,int(get(f'nominal_{h}',m).n_dates),n(get(f'nominal_{h}',m).ratio,3),n(get(f'nominal_{h}',m).rw,3)] for h in [12,36,60] for m in ['EJR','Fixed','Dynamic']])+r'''
Aqui preservamos o EJR original como referência: inclinação agrupada, sem intercepto, desvios reais centralizados somente com informação disponível. As extensões acrescentam fator comum dos preços e a proxy comercial fixa ou variável, sob a mesma restrição de regressão.

Os resultados não mostram uma melhora generalizada. A versão variável apresenta ganho pequeno em cinco anos frente ao EJR, mas permanece pior que nenhuma mudança. Em 12 e 36 meses, as extensões pioram a previsão.

\textbf{Relação com o terceiro relatório.} O terceiro destacou um componente comercial específico em outra construção e janela. Este complemento começa a avaliação em 2013, usa índices comerciais encadeados, inclui pesos anuais variáveis e tem foco em risco. Não se deve transpor o ganho do terceiro relatório para estas carteiras como se fosse uma propriedade universal do sinal.

\textbf{Interpretação.} Um país mudar sua exposição comercial não basta para prever a direção do nominal. Política monetária, inflação relativa, preços já incorporados e outros fatores podem absorver o ajuste. A análise é preditiva e não identifica causalidade entre comércio e câmbio.
''')
page('7. Conseguimos antecipar as próprias condições comerciais?',tab(['Alvo e regra','Anos','RMSE/persistência'],[
['Composição: ridge',int(A[(A.period=='all')&(A.model=='ridge')].n_years.iloc[0]),n(A[(A.period=='all')&(A.model=='ridge')].ratio.iloc[0],3)],
['Composição: extrapolar tendência',int(A[(A.period=='all')&(A.model=='trend')].n_years.iloc[0]),n(A[(A.period=='all')&(A.model=='trend')].ratio.iloc[0],3)],
['Termos agregados: ridge',int(AT[AT.model=='forecast'].n_years.iloc[0]),n(AT[AT.model=='forecast'].ratio.iloc[0],3)],
['Termos agregados: tendência',int(AT[AT.model=='trend'].n_years.iloc[0]),n(AT[AT.model=='trend'].ratio.iloc[0],3)]])+r'''
\textbf{Composição.} Em cada ano $Y$, prevemos os pesos suavizados do ano $Y+1$ a partir dos últimos conhecidos, $Y-2$. O horizonte entre dados é de três anos. Entram níveis e mudanças passadas dos pesos; o treinamento usa anos completos, cada ano uma única vez por país. Ridge fixa e pelo menos oito anos de treino. Persistência é mudança prevista zero.

O erro da previsão de composição é cerca de 20\% maior que a persistência; extrapolar a tendência é ainda pior. Algumas economias têm resultados anuais de 2025 enquanto outras não; as métricas usam apenas células realizadas e mostram a contagem nos CSVs. Não há evidência agregada de que antecipamos bem a transformação da cesta.

\textbf{Termos agregados.} Um exercício anual adicional usa nível e última variação do índice, prevendo a mudança entre $Y-2$ e $Y+1$. A ridge supera a persistência na amostra disponível, mas só há seis origens anuais, 2018--2023, com alvos sobrepostos. Este resultado é um piloto e não foi usado como filtro de carteira validado.

\textbf{Exposição mensal aos preços.} Prevemos a mudança de $Z$ em 12 meses com nível e momentum históricos. A razão de RMSE contra zero é '''+n(get('trade12','Ridge').ratio,3)+r'''. O ganho de timing não pode ser presumido: o próprio primeiro estágio é fraco.

As previsões de composição e de $Z$ são geradas recursivamente antes de entrarem no modelo de risco. Nenhuma previsão ajustada com a amostra completa é usada como sinal histórico.
''')
tasks=[('erased_12','Juros consumidos, 12m'),('adverse_12','Perda adversa, 12m'),('adverse_36','Perda adversa, 36m'),('adverse_60','Perda adversa, 60m'),('underwater_12','Tempo negativo, 12m'),('underwater_36','Tempo negativo, 36m'),('underwater_60','Tempo negativo, 60m'),('tail_1','Cauda agregada, 1m'),('tail_3','Cauda agregada, 3m')]
page('8. Repetição dos testes de risco do segundo relatório',tab(['Alvo','Preços var.','Termos anuais','Composição','Conjunto'],[[label]+[n(get(task,m).ratio,3) for m in ['dynamic','annual','structure','All']] for task,label in tasks])+r'''
Cada célula é RMSE do modelo aumentado dividido pelo da base reestimada na mesma história. Para alvos binários, o quadrado dessa razão é a razão de Brier. A base contém diferencial de juros em valor absoluto, volatilidade, momentum e previsão EJR, orientados pelo sinal da posição. Interceptos de país não são penalizados; a ridge tem penalidade 10. Reaplicamos a família de testes, sem alterar os números antigos.

\textbf{Juros consumidos.} O bloco de composição reduz o Brier em aproximadamente 7,4\%, com AUC 0,600 em 126 origens mensais. O p-valor ajustado por Holm é '''+n(get('erased_12','structure').p_holm,3)+r'''. É um candidato exploratório, não uma melhora estatisticamente estabelecida.

\textbf{Perda no caminho.} O alvo é o pior retorno log acumulado, abaixo da entrada, mantendo a direção inicial da moeda e somando o diferencial de juros realizado. Não é o máximo drawdown desde um pico intermediário, nem inclui custos de carteira. O tempo negativo mede a fração do caminho abaixo da entrada.

\textbf{Caudas.} Repetimos perdas agregadas de excesso de retorno inferiores a 2\% em um mês e 4\% em três meses, com a contabilidade líquida da carteira original. As informações comerciais não melhoram essas previsões de forma consistente.

As janelas variam por informação e horizonte: em perdas de 60 meses, há apenas 30--42 origens. O conjunto mais rico frequentemente piora o resultado, mostrando o custo de acrescentar variáveis em uma amostra pequena.
''')
page('9. Do sinal à decisão de carregar ou sair',r'''
Os alertas são definidos antes da execução. O corte principal é o percentil 80 da história do próprio sinal em cada moeda, calculado apenas até o mês anterior, com no mínimo 36 observações. Também testamos 70/90 e retirada de metade da exposição.
'''+tab(['Alerta','Informação usada'],[
['Preços observados','Deterioração direcional de Z em 12 meses'],['Preços previstos','Deterioração direcional prevista de Z em 12 meses'],['Composição observada','Soma das mudanças absolutas dos pesos em três anos'],['Composição prevista','Soma das mudanças absolutas previstas dos pesos'],['Revisão real 36/60m','Previsão da média real com preços menos base pareada'],['Depreciação real 60m','Previsão direcional do câmbio real final'],['Aumento do risco','Probabilidade com composição menos base pareada']],align='ll',size=r'\footnotesize')+r'''
Nos sinais direcionais, o alerta é invertido para posições vendidas. Magnitudes de composição são alertas simétricos. Cada par carry tem 25\% comprado e 25\% vendido. Se uma perna aciona o alerta, retiramos o par inteiro, sem redistribuir seu risco aos outros pares.

Sobrepomos cada alerta a carry puro, ao filtro EJR de retorno total acima de 2\% a.a. suavizado em seis meses e ao dimensionamento gradual EJR do segundo estudo. Coortes abrem pequenas posições mensais, expiram em 12 meses e, quando fechadas por alerta, permanecem em caixa até sua expiração. A avaliação começa quando todos os sinais da comparação estão disponíveis.

\textbf{Execução e retorno.} Sinal no fechamento $t$, operação em $t+1$, primeiro retorno em $t+2$. Usamos o mesmo motor do segundo relatório: ativo estrangeiro convertido a USD, funding em USD, remuneração do caixa, spread de empréstimo nas pernas vendidas, giro, entrada e liquidação final. Custos cambiais em pontos-base: BRL 10; EUR/JPY/GBP/CAD 2; SEK 3. Spread anual de empréstimo 50 pontos-base. Há sensibilidade a custos duplicados.

O alerta estatístico acima do percentil é uma regra de ranking histórica. Ele não exige que uma revisão real seja positiva em nível absoluto. Portanto, testa deterioração relativa do sinal, e não um limite universal de risco.
''')
page('10. Todos os filtros sobre o carry puro',tab(['Filtro','Início','Exp.','Excesso a.a.','Vol.','Maior queda'],[[names[h],st('Carry__'+h)['first'],pct(st('Carry__'+h).exposure),pct(st('Carry__'+h).mean_excess),pct(st('Carry__'+h).vol),pct(st('Carry__'+h).maxdd)] for h in names],size=r'\footnotesize')+fig('all_filters','Cada diferença usa seu carry de referência nas mesmas datas. Os filtros têm inícios distintos por disponibilidade, sem escolher a janela pelo desempenho.')+r'''
A maioria dos filtros reduz o retorno médio. O alerta de composição observada é uma exceção nesta amostra. Preços previstos e composição prevista retiram exposição sem compensação clara. A revisão da referência real tampouco produz regra robusta de saída.

Uma estratégia ficar menos volátil após retirar posições é esperado. A tabela seguinte e os controles de exposição verificam se o resultado vai além desse efeito mecânico.
''')
page('11. Candidato: composição observada',fig('structure_wealth','Retornos líquidos e exposição desde março de 2013. O controle de mesma exposição média é calculado ex post e serve apenas como diagnóstico.')+tab(['Regra','Exp.','Excesso a.a.','Vol.','Sharpe','Maior queda'],[[label,pct(st('Carry__structure_observed',ctrl).exposure),pct(st('Carry__structure_observed',ctrl).mean_excess),pct(st('Carry__structure_observed',ctrl).vol),n(st('Carry__structure_observed',ctrl).sharpe),pct(st('Carry__structure_observed',ctrl).maxdd)] for ctrl,label in [('base','Carry'),('rule','Composição'),('past_exposure','Exposição passada'),('expost_exposure','Exposição ex post')]])+r'''
O filtro reduz a exposição média para cerca de 70\%. O excesso médio sobe de 2,55\% para 2,82\% a.a., e a volatilidade cai de 4,22\% para 3,53\%. Desde 2019, a maior queda cai de 9,09\% para 3,37\%. Sobre o dimensionamento EJR, o excesso sobe de 2,80\% para 3,11\% a.a.

Isso é compatível com evitar certas posições após mudança comercial, mas não prova previsão de quebra. Nos meses de alerta, o carry bruto da regra de saída teve retorno médio menor, sem uma frequência de cauda uniformemente maior. O canal pode ser seleção de retorno, não apenas identificação de risco extremo.

\textbf{Proteção à mesma exposição.} O filtro tem volatilidade e maior queda superiores ao controle de exposição média ex post. Seu atrativo é a relação entre retorno e risco nesta amostra; não é uma dominância de proteção sobre simplesmente carregar menos.
''')
page('12. Candidato: sair de coortes quando o risco sobe',fig('cohort_risk','Coortes de 12 meses, abril de 2018 a agosto de 2026. A saída responde ao acréscimo da probabilidade prevista de o câmbio consumir os juros.')+tab(['Regra','Exp.','Excesso a.a.','Vol.','Sharpe','Maior queda'],[[label,pct(st('Cohort__risk_increment',ctrl).exposure),pct(st('Cohort__risk_increment',ctrl).mean_excess),pct(st('Cohort__risk_increment',ctrl).vol),n(st('Cohort__risk_increment',ctrl).sharpe),pct(st('Cohort__risk_increment',ctrl).maxdd)] for ctrl,label in [('base','Manter coortes'),('rule','Sair por risco'),('expost_exposure','Exposição ex post')]])+r'''
Esta é a versão mais próxima da hipótese do usuário: a informação comercial muda a avaliação de risco e encerra a posição antes do vencimento. O maior drawdown passa de 9,92\% para 3,23\%, e o excesso médio de 2,78\% para 3,34\% a.a. A regra mensal sem coortes é menos convincente: reduz retorno e o ganho de Sharpe é pequeno.

O resultado usa apenas 101 meses e depende do desenho da saída. Cortes e custos adicionais aparecem nas sensibilidades. Redução observada de drawdown não demonstra que o próximo choque será evitado.

Contra a mesma exposição média ex post, a redução de drawdown é 4,26 pontos percentuais, com intervalo condicional de 95\% de $[-0,86;10,38]$ em blocos de 12 meses. A diferença de volatilidade é quase nula. Portanto, a melhora de proteção além da exposição não está estabelecida estatisticamente.
''')
page(r'13. Proteção sobre o filtro EJR de 2\% a.a.',fig('ejr_price','Acrescentar deterioração observada dos preços ao filtro EJR reduz risco e também retorno. Todos os controles usam março de 2013 a agosto de 2026.')+r'''
O filtro EJR original desta comparação tem excesso médio de 2,53\% a.a. e maior queda de 6,78\%. Acrescentar o alerta de preços observados leva o excesso a 2,02\% e a queda a 0,72\%, com exposição média próxima de 21\%.

Esse resultado parece forte como proteção, mas o controle com exposição reduzida também apresenta risco muito baixo. O controle de exposição calculado somente com o passado é operacional, porém não iguala exatamente a exposição média realizada. O controle ex post iguala a média, mas usa informação futura e não é uma estratégia implementável.

\textbf{Qual escolha este teste informa?} Um investidor disposto a sacrificar retorno para reduzir exposição em condições comerciais adversas pode preferir esse tipo de filtro. O exercício não demonstra que essa troca domina uma redução simples do orçamento de risco.

O objetivo foi separar três perguntas: o sinal melhora previsão? Ele seleciona retornos? Ele protege além do efeito de manter menos risco? Elas têm respostas diferentes. A melhora visual de uma curva de patrimônio não substitui as comparações preditivas e de exposição.
''')
pvrows=[]
for v in ['Base','Ridge1','Ridge100','Lag3','NoBRL','NoEUR']:
    row=[v]
    for h in ['structure_observed','structure_forecast']:
        a=PV[(PV.variant==v)&(PV.hazard==h)&(PV.period=='all')];r=a[a.control=='rule'].iloc[0];b=a[a.control=='base'].iloc[0];row += [n(r.sharpe-b.sharpe),n(100*(r.mean_excess-b.mean_excess))]
    pvrows.append(row)
page('14. Sensibilidade: o padrão permanece?',tab(['Variação','Obs.: ΔSharpe','Obs.: Δret.','Prev.: ΔSharpe','Prev.: Δret.'],pvrows)+fig('thresholds','Diferença de Sharpe para três cortes previamente definidos. Mudanças de corte não são testes independentes.')+r'''
Δret. está em pontos percentuais anuais contra o carry da mesma variante. Sem BRL/EUR, refazemos o ranking no universo restante; o benchmark muda junto. O atraso de três anos muda o momento do sinal e o horizonte da previsão anual para quatro anos.

\textbf{Fragilidade relevante.} Composição prevista tem resultado fraco na especificação principal, mas melhora bastante ao atrasar mais um ano. Isso merece investigação sobre atualização dos dados e defasagem econômica, não seleção automática da melhor versão. A sensibilidade é incompatível com uma regra já estável.

Os modelos reais também foram reestimados com ridge 1/100, janela 120 meses e exclusão de moedas. Os resultados completos estão nos CSVs. Para as políticas, ``Window120'' mantém o alerta anual original; a janela móvel pertence à regressão real, não altera artificialmente o sinal anual.
''')
cvrows=[]
for q in [.7,.8,.9]:
    for c in [1,2]:
        a=CV[(CV['quantile']==q)&(CV.cost==c)&(CV.control=='rule')&(CV.period=='all')].iloc[0];cvrows.append([int(q*100),c,pct(a.exposure),pct(a.mean_excess),n(a.sharpe),pct(a.maxdd)])
page('15. Variações da saída e incerteza dos ganhos',tab(['Percentil','Custo ×','Exp.','Excesso a.a.','Sharpe','Maior queda'],cvrows)+r'''
O filtro de coortes por risco foi aprofundado com percentis 70/80/90 e custos base/duplicados. Toda a grade é mostrada, inclusive resultados inferiores. São variações exploratórias da mesma amostra.
'''+tab(['Candidato','Δ excesso a.a.',r'IC 95\% em blocos 12m'],[[label,n(100*a.mean_difference)+' p.p.', '['+n(100*a.low)+'; '+n(100*a.high)+']'] for name,label in [('Carry__structure_observed','Composição observada'),('Cohort__risk_increment','Coortes / risco'),('EJR_gate__price_observed','EJR / preços')] for a in [I[(I.name==name)&(I.benchmark=='base')&(I.block==12)].iloc[0]]])+r'''
Os intervalos de diferença do retorno médio contra as respectivas bases incluem zero. Também calculamos blocos de 36 meses e intervalos para volatilidade, drawdown e perda média na cauda de 5\%, tanto contra a base quanto contra exposição média ex post. Estão no pacote para evitar resumir proteção apenas pelo melhor drawdown observado.

Esses bootstraps são condicionais aos sinais produzidos. Não reestimam toda a cadeia anual/mensal, não ajustam a seleção entre políticas e não constituem garantia de desempenho futuro. O bootstrap de drawdown reconstrói caminhos com blocos, alterando a ordem dos episódios.

Nos testes de previsão usamos perdas médias por mês, HAC e Holm por família macro/risco. A única melhora com Holm abaixo de 5\% é pequena e localizada: preços fixos no real BRL em 36 meses. Ela não implica vitória sobre nenhuma mudança. Nos horizontes longos, quando faltam três blocos, omitimos p-valores. Fases sem sobreposição e intervalos condicionais também foram salvos.
''')
page('16. O que aprendemos sobre a hipótese',r'''
\textbf{1. A referência histórica pode ser inadequada, mas não a corrigimos de forma confiável.} A informação comercial melhora modestamente algumas regressões reais longas, sem superar nenhuma mudança. Modelos mais ricos com história curta não devem ser confundidos com evidência de novo equilíbrio.

\textbf{2. Mudança de composição não equivale a risco previsto.} A composição prevista é difícil de acertar e não funciona bem como alerta principal. A composição observada é mais interessante na carteira. Isso sugere testar adaptação após a mudança, em vez de presumir capacidade de antecipar uma quebra produtiva.

\textbf{3. Prever perda é uma ponte mais direta para a decisão.} O pequeno ganho na probabilidade de o câmbio consumir o carrego motivou a saída de coortes. Esse desenho tem resultado descritivo promissor, embora a melhora preditiva não seja significativa após múltiplas comparações e o ganho médio da política seja incerto.

\textbf{4. Retorno e proteção precisam ser avaliados separadamente.} Alguns filtros reduzem risco à custa de retorno; outros eliminam meses favoráveis. Controlar exposição evita atribuir toda proteção ao sinal comercial.

\textbf{5. O próximo teste deve ter dados novos ou um desenho congelado.} Os candidatos a acompanhar são o alerta de composição observada e a saída de coortes por probabilidade de perda. Para estudar uma mudança estrutural de fato, seria necessário separar preços e quantidades, detalhar produtos, reconstruir vintages e obter uma história maior. O resultado favorável ao atraso adicional é uma pergunta sobre o mecanismo e a disponibilidade, não justificativa para escolher esse atraso retroativamente.

\textbf{Conclusão operacional deste estudo.} Não há fundamento aqui para sair automaticamente sempre que o modelo antecipa mudança comercial. Há evidência exploratória para condicionar a permanência à avaliação de perda e à adaptação comercial observada, com orçamento de risco explícito. As especificações ficam documentadas para avaliação futura sem nova escolha oportunista.
''')
page('17. Auditoria, fontes e reprodução',r'\textbf{'+str(len(Q))+r''' verificações de integridade passaram.} Incluem reprodução do EJR e das previsões salvas, igualdade das linhas de treino das regressões pareadas, execução com atraso, neutralidade long/short, limite de exposição, custos, unicidade de previsões, hashes e preservação dos 232 arquivos congelados antes deste complemento.

Testes de perturbação alteram informações anuais futuras, rótulos ainda indisponíveis e preditores futuros. As previsões e limiares antigos permanecem invariantes. Isso verifica a implementação temporal; não resolve revisões históricas dos provedores.

\textbf{Fontes primárias.}
\begin{enumerate}
\item Banco Mundial/UNCTAD. \href{https://databank.worldbank.org/metadataglossary/world-development-indicators/series/TT.PRI.MRCH.XD.WD}{Definição do índice agregado de termos de troca}. Razão entre índices de valor unitário de exportação e importação; dados anuais.
\item Banco Mundial. \href{https://www.worldbank.org/en/research/commodity-markets}{Commodity Markets / Pink Sheet}. As 12 séries setoriais brutas foram preservadas no terceiro estudo e reutilizadas aqui.
\item Banco Mundial, WDI. \href{https://api.worldbank.org/v2/}{API pública}. Séries TX/TM de valores totais e participações FUEL, FOOD, AGRI e MMTL. URLs completas, datas e hashes dos 11 novos downloads no manifesto.
\item Gruss e Kebhaj (2019), \href{https://www.elibrary.imf.org/view/journals/001/2019/021/article-A001-en.xml}{Commodity Terms of Trade: A New Database}. Referência para distinguir exposição de preços e pesos comerciais variáveis. Nossa proxy de quatro grupos não é uma réplica integral desse índice.
\item Eichenbaum, Johannsen e Rebelo, \href{https://www.nber.org/papers/w23158}{Monetary Policy and the Predictability of Nominal Exchange Rates}. Artigo e material da aula preservados no repositório; motor EJR e contabilidade do segundo estudo reutilizados.
\end{enumerate}

\textbf{Reprodução.} Executar \texttt{trade\_extension/run.ps1} na raiz do projeto. Dados novos estão salvos; baixar de novo não é necessário. Python e Tectonic portáteis são os do repositório. O pacote complementar acompanha fonte LaTeX, figuras vetoriais, scripts, previsões, auditoria e tabelas completas; requer os insumos originais e do terceiro estudo, já presentes no projeto.

\textbf{Inventário.} '''+str(len(M))+r''' linhas de métricas preditivas; '''+str(len(O))+r''' previsões avaliadas; 64 regras principais/variações de posição, cada uma com quatro controles; seis variações adicionais de saída. As contagens não representam observações macroeconômicas independentes.
''')
preamble=r'''\documentclass[11pt,a4paper]{article}
\usepackage[margin=1.9cm,top=1.8cm,bottom=1.9cm]{geometry}
\usepackage[T1]{fontenc}\usepackage[utf8]{inputenc}\usepackage[brazil]{babel}
\usepackage{lmodern,microtype,amsmath,booktabs,array,graphicx,float,caption,xcolor,enumitem,fancyhdr,hyperref}
\definecolor{ink}{HTML}{163447}\hypersetup{colorlinks=true,urlcolor=ink,linkcolor=ink}
\setlength{\parindent}{0pt}\setlength{\parskip}{6pt}\setlength{\headheight}{15pt}
\setlength{\tabcolsep}{5pt}\renewcommand{\arraystretch}{1.10}
\setlength{\intextsep}{6pt}\setlength{\textfloatsep}{8pt}\setlist{nosep}
\captionsetup{font=small,labelfont=bf,skip=4pt}
\pagestyle{fancy}\fancyhf{}\fancyhead[L]{\small Termos de troca e risco cambial}\fancyhead[R]{\small Complemento ao segundo estudo}\fancyfoot[C]{\thepage}
\renewcommand{\headrulewidth}{.3pt}\setlength{\emergencystretch}{2em}
\begin{document}
'''
(H/'relatorio_termos_troca.tex').write_text((preamble+'\n\\clearpage\n'.join(pages)+r'\end{document}').replace('Δ',r'$\Delta$').replace('×',r'$\times$'),encoding='utf8')
print('Designed pages',len(pages),'Figures',len(list(F.glob('*.pdf'))))
