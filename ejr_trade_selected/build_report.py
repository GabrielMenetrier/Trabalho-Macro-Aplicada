from pathlib import Path
import pandas as pd,numpy as np
H=Path(__file__).resolve().parent;R=H.parent
m=pd.read_csv(H/'tables/metrics.csv');w=pd.read_csv(H/'tables/winners.csv');ins=pd.read_csv(H/'tables/in_sample.csv');a=pd.read_csv(H/'tables/audit.csv');pool=pd.read_csv(H/'tables/pooling_diagnostics.csv')
CC=['BRL','EUR','CAD'];HH=[12,24,36,48,60,72,84,96];MODELS=['EJR','TOT_LOG_LD','COM_DEV_LD']
def num(x,n=3):return '--' if pd.isna(x) else f'{x:.{n}f}'.replace('.',',')
def esc(x):return str(x).replace('&',r'\&').replace('%',r'\%').replace('_',r'\_')
def tab(head,rows,small=True):
 return ('{\\footnotesize\n' if small else '{\\small\n')+r'\begin{center}\begin{tabular}{'+'l'+'r'*(len(head)-1)+r'}\toprule'+'\n'+' & '.join(map(esc,head))+r' \\ \midrule'+'\n'+'\n'.join(' & '.join(map(esc,row))+r' \\' for row in rows)+r'\bottomrule\end{tabular}\end{center}}'+'\n'
def metric(h,country,model,scenario='fixed'):
 return m[(m.h==h)&(m.country==country)&(m.model==model)&(m.scenario==scenario)].iloc[0]
def label(model):
 if model=='EJR':return 'EJR'
 if model.startswith('JOINT'):return 'Conjunta: '+model[6:].replace('_',' / ')
 fam,form,content=model.split('_');return {'LOG':'Log','DEV':'Desvio','SLOG':'Log com sinal'}[form]+' '+{'L':'nível','D':'mudança','LD':'nível+mudança'}[content]
p=[r'''\documentclass[10pt,a4paper]{article}
\usepackage[margin=1.8cm]{geometry}\usepackage{fontspec}\setmainfont{Arial}
\usepackage[brazil]{babel}\usepackage{amsmath,booktabs,graphicx,xcolor,fancyhdr,hyperref}
\definecolor{navy}{HTML}{15354D}\definecolor{teal}{HTML}{007F7B}
\hypersetup{colorlinks=true,urlcolor=teal,linkcolor=navy,pdftitle={Termos de troca onde o EJR funciona}}
\pagestyle{fancy}\fancyhf{}\fancyhead[L]{\small Termos de troca onde o EJR funciona}\fancyhead[R]{\small Setembro de 2026}\fancyfoot[C]{\thepage}
\setlength{\headheight}{14pt}\setlength{\parindent}{0pt}\setlength{\parskip}{6pt}\setlength{\emergencystretch}{3em}
\renewcommand{\arraystretch}{1.15}
\newcommand{\pagina}[1]{\clearpage{\Large\bfseries\color{navy} #1}\par\vspace{6pt}}
\begin{document}
{\LARGE\bfseries\color{navy} Termos de troca onde o EJR funciona}\par
{\large Brasil, euro e Canadá: transformações, regressões e previsão}\par
\textbf{O resultado muda quando a referência funciona.} No trio em que o EJR já superava nenhuma mudança em cinco anos, a melhor adição de termos de troca reduz o erro agregado em \textbf{21,7\%} frente à base. O RMSE relativo a nenhuma mudança cai de \textbf{0,802 para 0,628}. A melhor cesta de commodities chega a \textbf{0,773}, uma redução de \textbf{3,7\%} frente ao EJR.

\textbf{Melhores formas em cinco anos.} Termos de troca: \textbf{log do índice + mudança anual em log}. Cesta de commodities: \textbf{desvio proporcional do índice + mudança percentual anual}. A diferença entre formas da cesta é muito pequena; a escolha do regressor e do país é mais importante do que a diferença entre log e desvio.
''']
rows=[]
for c in ['POOL']+CC:
 rows.append([{'POOL':'Agregado','BRL':'Brasil','EUR':'Euro','CAD':'Canadá'}[c]]+[num(metric(60,c,k).rmse_rw) for k in MODELS])
p.append(tab(['Cinco anos','EJR','+ termos de troca','+ cesta'],rows,False))
p.append(r'''A mesma especificação vencedora do agregado é aplicada aos três países. \textbf{O ganho com termos de troca concentra-se no Brasil}: 0,804 para 0,544, redução de 32,4\%. Euro e Canadá pioram com essa adição. A cesta melhora o Brasil e o Canadá, mas piora ligeiramente o euro.

\textbf{Melhor resultado encontrado em cada horizonte.} A tabela revela todas as escolhas retrospectivas, sem transformar o melhor de cada prazo numa regra já conhecida antecipadamente.
''')
rows=[]
for h in HH:
 tt=w[(w.h==h)&(w.country=='POOL')&(w.family=='TOT')].iloc[0];co=w[(w.h==h)&(w.country=='POOL')&(w.family=='COM')].iloc[0]
 rows.append([h//12,num(metric(h,'POOL','EJR').rmse_rw),label(tt.model),num(tt.rmse_rw),label(co.model),num(co.rmse_rw)])
p.append(tab(['Anos','EJR','Melhor TT','Erro TT','Melhor cesta','Erro cesta'],rows))
p.append(r'''\textbf{O que esses números significam.} São erros fora da amostra dos modelos, com coeficientes estimados recursivamente. A escolha do melhor modelo entre as variantes, porém, usa o resultado completo dessa avaliação e é retrospectiva. O relatório inclui uma escolha temporal baseada somente em previsões já encerradas para avaliar essa limitação.

\textbf{Escopo.} Mantivemos a equação preditiva EJR e a base do projeto, reestimando a inclinação comum somente para BRL, EUR e CAD. Não é a reprodução integral da amostra original do artigo. Não há carteiras ou alterações nos slides.
''')
p.append(r'''\pagina{1. O que significa log, desvio e log do desvio}
Seja $Z_{i,t}>0$ o índice de termos de troca ou da cesta de commodities, e $A_{i,t}$ sua média aritmética usando somente informação disponível até a origem $t$. Com $d_{i,j}^{(t)}=Z_{i,j}/A_{i,t}-1$, comparamos:
\begin{align*}
\text{Log:}\quad &\log Z_{i,j}-\overline{\log Z}_{i,\leq t};\\
\text{Desvio:}\quad &d_{i,j}^{(t)};\\
\text{Log com sinal:}\quad &\operatorname{sign}(d_{i,j}^{(t)})\log(1+|d_{i,j}^{(t)}|),
\end{align*}
centralizando também a última transformação pela sua média disponível. O log trabalha com distâncias multiplicativas; o desvio mede a distância proporcional da média; o log com sinal comprime desvios maiores preservando se o índice está acima ou abaixo da referência.

\textbf{Log puro do desvio tem um problema de domínio.} Quando $d\leq0$, $\log d$ não é real e finito. Descartar esses casos excluiria exatamente as observações abaixo da média. Não descartamos meses nem adicionamos uma constante escolhida pelo mínimo futuro da série.

\textbf{Uma alternativa muito natural é equivalente ao log já testado.} Como $1+d=Z/A>0$,
\[\log(1+d_{i,j}^{(t)})=\log Z_{i,j}-\log A_{i,t}.\]
Depois de centralizar, a constante $\log A_{i,t}$ desaparece e obtemos exatamente o regressor de log centralizado. Verificamos a identidade numericamente. Portanto, \textbf{log(1+desvio) não cria um quarto modelo distinto} neste desenho. O log com sinal é uma alternativa diferente e válida para desvios positivos e negativos.

\textbf{Mudanças.} Para uma log-variação anual $g$, a forma LOG usa $g$; DEV usa $e^g-1$; SLOG usa $\operatorname{sign}(e^g-1)\log(1+|e^g-1|)$. As três são centralizadas apenas com informação disponível. Na série anual de termos de troca, usamos a mudança entre os dois últimos anos admissíveis; na cesta mensal, a mudança em 12 meses.

\textbf{Equação prevista.} O alvo é sempre $s_{i,t+h}-s_{i,t}$, mudança futura do log do câmbio nominal local/USD. A base usa $q_{i,t}-\bar q_{i,\leq t}$, desvio do log câmbio real. À mesma base acrescentamos as transformações acima, com todos os coeficientes reestimados em cada origem. Nenhuma adição usa termos de troca futuros realizados.

\textbf{Grade completa.} São 27 extensões: nove para termos de troca (três formas, cada uma com nível, mudança ou ambos); nove para a cesta; nove combinações conjuntas com nível e mudança das duas famílias. O EJR é a referência adicional. Todas as variantes permanecem nas tabelas, inclusive as que pioram.
''')
p.append(r'''\pagina{2. A relação de regressão que motivou o estudo}
Estas são regressões descritivas do tipo apresentado no artigo: no eixo horizontal, desvio do log câmbio real; no vertical, mudança futura do log câmbio nominal. Cada país tem intercepto e inclinação próprios estimados com a amostra completa. O $R^2$ é histórico, não uma medida fora da amostra.
\begin{center}\includegraphics[width=\textwidth]{figures/relacao_ejr.pdf}\end{center}
\textbf{Prazos e dados.} Linha superior: cinco anos, origens outubro/1999--agosto/2021, alvos até agosto/2026. Linha inferior: oito anos, origens outubro/1999--agosto/2018, alvos até agosto/2026. Cada ponto corresponde a uma origem mensal; os alvos de meses adjacentes se sobrepõem.

\textbf{Como comparar regressões com mais de um regressor.} Não existe uma única reta entre câmbio real e câmbio nominal que mostre toda a previsão de uma regressão com termos de troca adicionais. Por isso, nas próximas páginas usamos \textbf{valor ajustado ou previsto no eixo horizontal e valor realizado no vertical}. Isso permite comparar a base e as extensões na mesma escala. A diagonal pontilhada representa igualdade perfeita, não uma reta estimada para embelezar o resultado.

\textbf{Dois exercícios separados.} Na linha superior dos próximos gráficos, fazemos OLS por país com intercepto e usamos toda a amostra, apresentando $R^2$ ajustado. Na inferior, mostramos previsões genuinamente recursivas do painel de três moedas, sem intercepto adicional, como na equação preditiva EJR. Os gráficos distinguem ajuste descritivo de capacidade preditiva.
''')
notes={
'BRL':r'''\textbf{Brasil é o principal resultado favorável.} Na regressão histórica de cinco anos, o $R^2$ ajustado sobe de 0,557 para 0,858 com termos de troca. Na previsão recursiva do painel, o erro relativo cai de 0,804 para 0,544. A cesta melhora menos: 0,770. Os pontos ficam mais próximos da diagonal, mas persistem erros sistemáticos em vários episódios.

\textbf{Checagem com coeficientes só do Brasil.} Reestimar o mesmo modelo de forma individual mantém o resultado: EJR 0,826; termos de troca 0,541; cesta 0,678. O ganho dos termos de troca não depende apenas de transferir coeficientes do Canadá e do euro para o Brasil.''',
'EUR':r'''\textbf{Euro mostra o limite da generalização.} O $R^2$ ajustado histórico aumenta ligeiramente com as adições. Fora da amostra, porém, o EJR já tem erro 0,898 e as extensões apresentam 0,998 e 0,911. O modelo de termos de troca que venceu no agregado não é o melhor para o euro.

Se escolhermos retrospectivamente uma variante específica para o euro, a cesta em desvio, somente em nível, chega a 0,868. Esse número é uma seleção adicional por país e não substitui a comparação principal, que preserva o mesmo modelo nos três países. Alemanha representa apenas os dados comerciais do euro.''',
'CAD':r'''\textbf{Canadá diferencia ajuste histórico de previsão.} Os termos de troca elevam o $R^2$ ajustado de 0,524 para 0,774, mas pioram o erro fora da amostra de 0,719 para 0,920. A cesta tem ganho menor no ajuste histórico, mas melhora a previsão para 0,701.

O melhor resultado individual retrospectivo do Canadá é a mudança anual da cesta em log com sinal: 0,670. Ele difere do modelo vencedor do agregado. Estimar separadamente o mesmo modelo de cesta usado na comparação principal mantém uma pequena melhora: EJR 0,733; cesta 0,703.'''}
for c,title in [('BRL','Brasil'),('CAD','Canadá'),('EUR','Euro')]:
 p.append(r'\pagina{3'+{'BRL':'a','CAD':'b','EUR':'c'}[c]+'. Comparação das regressões: '+title+'}\n')
 p.append(r'\begin{center}\includegraphics[width=\textwidth]{figures/comparacao_'+c+r'.pdf}\end{center}'+'\n')
 p.append(notes[c])
 p.append(r'''
\textbf{Calendário dos gráficos.} Ajuste histórico: origens outubro/1999--agosto/2021, 263 observações. Fora da amostra: 140 origens janeiro/2010--agosto/2021 e alvos janeiro/2015--agosto/2026. No primeiro teste, treino outubro/1999--dezembro/2004, com alvos encerrados até dezembro/2009; depois, expansão mensal. CPI e preços da cesta defasados dois meses; termos anuais usam $Y-2$.

\textbf{Unidades.} Os eixos multiplicam a variação logarítmica por 100 para leitura. Não são variações percentuais exatas. A mesma escala horizontal e vertical vale para os seis painéis de cada país. A forma da adição é log + mudança em log para termos de troca; desvio + mudança percentual para a cesta. São os vencedores das famílias no agregado em cinco anos.
''')
p.append(r'''\pagina{4. Qual transformação venceu e por quanto}
Cinco anos, agregado BRL/EUR/CAD. RMSE relativo a nenhuma mudança. Abaixo de 0,802 supera também o EJR deste grupo. A seleção da melhor forma usa retrospectivamente os resultados completos.
''')
rows=[]
for f,label_ in [('LOG','Log'),('DEV','Desvio'),('SLOG','Log com sinal')]:
 for content,labelc in [('L','Nível'),('D','Mudança'),('LD','Nível + mudança')]:
  rows.append([label_,labelc,num(metric(60,'POOL',f'TOT_{f}_{content}').rmse_rw),num(metric(60,'POOL',f'COM_{f}_{content}').rmse_rw)])
p.append(tab(['Forma','Conteúdo','Termos de troca','Cesta'],rows,False))
p.append(r'''\begin{center}\includegraphics[width=\textwidth]{figures/transformacoes.pdf}\end{center}
\textbf{A informação em nível é central.} A mudança dos termos de troca sozinha não melhora o EJR: erro próximo de 0,815. O nível em log chega a 0,651, e nível mais mudança chega a 0,628. A melhora não depende de achar uma transformação exótica: desvio e log com sinal, com os mesmos dois componentes, também melhoram bastante, para 0,638 e 0,634.

\textbf{Na cesta, a diferença entre formas é mínima.} Com nível e mudança, log, desvio e log com sinal produzem erros 0,7731, 0,7726 e 0,7737. O desvio tem o menor erro por uma margem muito pequena. Não há base para afirmar superioridade econômica ou estatística dessa forma frente ao log.

\textbf{Mais regressores não venceram o modelo simples.} A melhor combinação das duas famílias chega a 0,632, ainda acima de 0,628 do modelo de termos de troca sozinho. Os nove modelos conjuntos constam na última tabela.
''')
p.append(r'''\pagina{5. De onde vem o ganho agregado}
\textbf{A escala de variação do Brasil importa.} O RMSE agregado padrão soma erros quadráticos das três moedas e depois extrai a raiz. Assim, países com maiores variações cambiais têm maior influência no resultado. Uma segunda medida normaliza primeiro o erro pelo passeio aleatório de cada país e depois agrega com pesos iguais entre moedas.
''')
z=pool[pool.training=='panel_3'].set_index('model')
p.append(tab(['Modelo','RMSE agregado padrão','Agregação normalizada por país'],[[{'EJR':'EJR','TOT_LOG_LD':'+ termos de troca','COM_DEV_LD':'+ cesta'}[k],num(z.loc[k,'rmse_rw']),num(z.loc[k,'equal_country_rmse'])] for k in MODELS],False))
p.append(r'''Nessa agregação alternativa, termos de troca \textbf{pioram} a comparação: 0,810 para 0,844. A cesta melhora ligeiramente, para 0,799. Portanto, a conclusão defensável é um ganho forte para o Brasil e para o agregado que dá maior influência às maiores variações; não um ganho generalizado igualmente entre países.

\textbf{Retirando o Brasil e reestimando.} Com apenas euro e Canadá, o EJR tem erro 0,773; termos de troca 0,856; cesta 0,775. O principal ganho desaparece. Esse diagnóstico foi feito depois de observar a concentração no Brasil e não redefine os países da tabela principal.

\textbf{Por que a comparação anterior era diferente?} A regressão impõe inclinações comuns. Estimar com seis moedas e avaliar no mesmo trio dá EJR 0,791 e termos de troca 0,797. Estimar somente no trio dá 0,802 e 0,628. Logo, o resultado muda por \textbf{quais países determinam os coeficientes}, e não apenas por retirar erros ruins da tabela de avaliação. A restrição de homogeneidade dos efeitos comerciais é importante.

\textbf{Melhor ajuste histórico não coincide com melhor previsão.} Abaixo estão as extensões com maior $R^2$ ajustado histórico em cada país, dentre as 27 testadas, e seu erro fora da amostra no painel. É uma escolha retrospectiva diferente daquela que minimiza o RMSE.
''')
rows=[]
for c in CC:
 b=ins[(ins.h==60)&(ins.country==c)&(ins.model!='EJR')].sort_values('adjusted_r2').iloc[-1]
 rows.append([c,b.model,num(b.adjusted_r2),num(metric(60,c,b.model).rmse_rw)])
p.append(tab(['País','Maior ajuste histórico','R² ajustado','Erro fora da amostra'],rows))
p.append(r'''Nomes conjuntos indicam a forma dos termos de troca e da cesta, nessa ordem, ambas com nível e mudança. O histórico favorece modelos mais flexíveis, mas isso não os torna melhores previsores. A evidência econômica mais útil é que a informação comercial parece relevante de forma heterogênea entre países, especialmente no Brasil.
''')
p.append(r'''\pagina{6. A forma poderia ter sido escolhida antes?}
Para separar seleção retrospectiva de uma regra temporal, em cada mês escolhemos entre EJR e as nove formas da família usando somente erros de previsões \textbf{já encerradas}. A escolha exige 24 origens passadas avaliáveis. Para um horizonte de cinco anos, a regra começa a ser avaliável em janeiro/2017.

\textbf{Mesmas 56 origens, janeiro/2017--agosto/2021.} Alvos janeiro/2022--agosto/2026. Os números desta página não devem ser comparados diretamente à janela completa 2010--2021, porque incluem um conjunto diferente de episódios.
''')
rows=[]
for k,label_ in [('EJR','EJR'),('TOT_LOG_LD','Termos de troca: melhor fixo'),('ADAPTIVE_TOT','Termos de troca: escolha temporal'),('COM_DEV_LD','Cesta: melhor fixo'),('ADAPTIVE_COM','Cesta: escolha temporal'),('ADAPTIVE_ALL','Escolha temporal entre todos')]:
 sc='adaptive_COM' if k=='ADAPTIVE_COM' else ('adaptive_ALL' if k=='ADAPTIVE_ALL' else 'adaptive_TOT');b=metric(60,'POOL',k,sc);rows.append([label_,num(b.rmse_rw),num(b.rmse_ejr)])
p.append(tab(['Modelo ou regra','Erro / nenhuma mudança','Erro / EJR'],rows,False))
p.append(r'''A escolha temporal dos termos de troca reduz o erro em \textbf{14,2\%} frente ao EJR nessa janela, mas ainda perde para nenhuma mudança: 1,273. A variante fixa escolhida retrospectivamente chega a 1,203, melhor que a escolha temporal. A seleção temporal não apaga a escolha prévia de países e a exploração da mesma história.

\textbf{Origens mais recentes, 2019--2021.} Com os modelos fixos da comparação principal, EJR resulta em 2,208; termos de troca em 1,766; cesta em 2,140. A melhora incremental de termos de troca persiste, mas nenhuma dessas previsões supera a referência de nenhuma mudança nesse recorte. São apenas 32 origens mensais sobrepostas.

\textbf{Interpretação correta do melhor resultado.} O número 0,628 identifica uma melhora preditiva histórica relevante no universo solicitado, especialmente para o Brasil. Ele não demonstra uma regularidade já confirmada em dados independentes. Testamos 27 extensões, oito horizontes e recortes por país. Além disso, 140 origens de cinco anos correspondem a apenas 2,3 horizontes em extensão temporal. Não atribuímos ao vencedor um p-valor convencional como se a escolha não tivesse ocorrido.

\textbf{Aprendizado.} Há informação nos termos de troca que a regressão cambial base não resume no Brasil. A vantagem não aparece igualmente em todos os países e depende da composição do painel. A alternativa em log é simples e teve desempenho próximo das outras transformações, o que é mais interessante que um resultado obtido apenas com uma forma muito específica.
''')
p.append(r'''\pagina{7. Calendário, dados e integridade}
O universo BRL/EUR/CAD foi fixado a partir do resultado anterior em cinco anos, antes de estimar as novas transformações. A base foi reestimada no trio e confirmada numericamente contra o código anterior. O treino usa alvos completos até $t-1$, e o início do laço preserva $h+61$. As primeiras datas de avaliação dependem do horizonte.
''')
rows=[]
for h in HH:
 b=metric(h,'POOL','EJR');aa=a[(a.h==h)&(a.origin==b['first'])].iloc[0]
 rows.append([h//12,aa.first_train+' a '+aa.last_train,b['first']+' a '+b['last'],b.first_target+' a '+b.last_target,int(b.n_dates)])
p.append(tab(['Anos','Treino no primeiro teste','Origens avaliadas','Alvos avaliados','Meses'],rows))
p.append(r'''\textbf{Termos de troca observados.} Reutilizamos a razão dos deflatores de exportação e importação das contas nacionais, bens e serviços, construída com valores correntes e constantes em moeda local do Banco Mundial. Em ano $Y$, a informação é de $Y-2$ e sua mudança frente a $Y-3$. Não usamos o índice curto de mercadorias como substituto sem histórico suficiente.

\textbf{Cesta.} Quatro grupos de preços reais de commodities, ponderados pelas diferenças entre participações nas exportações e importações totais, médias 1994--1996. Energia, alimentos, matérias-primas agrícolas e metais. Os preços e o CPI entram com dois meses de atraso. A cesta é proxy parcial: presume que o restante do comércio acompanha o CPI americano. Alemanha aproxima os dados comerciais do euro.

\textbf{Auditoria.} Foram aprovadas 359 verificações principais e três reproduções independentes em statsmodels. Incluem correspondência da base, invariância à unidade do índice, identidade entre log(1+desvio) centralizado e log centralizado, truncamento da base, perturbações em dados futuros, mesmas origens por comparação e maturidade dos erros usados para selecionar modelos. O código salva todas as previsões, escolhas temporais, coeficientes e métricas.

\textbf{Limites.} Os dados são revisados, sem vintages completos. A avaliação é pseudo fora da amostra com calendário controlado. Ela não elimina revisões históricas, dependência temporal, seleção de países, seleção de forma funcional ou investigação repetida. O estudo replica a equação preditiva EJR na base do projeto e não o DSGE, o bootstrap ou a amostra integral do artigo.

\textbf{Fontes.} Eichenbaum, Johannsen e Rebelo (2021), equações (3.2) e (3.4), \href{https://doi.org/10.1093/restud/rdaa024}{Monetary Policy and the Predictability of Nominal Exchange Rates}. Dados e definições: \href{https://databank.worldbank.org/metadataglossary/world-development-indicators/series/NE.TRM.TRAD.XU}{termos de troca de bens e serviços}; WDI, valores correntes e constantes de exportações/importações; Pink Sheet; dados de câmbio e CPI já congelados no projeto. A pasta \texttt{ejr\_trade} documenta a coleta das contas nacionais, em 15/09/2026.

\textbf{Reprodução.} Pasta \texttt{ejr\_trade\_selected}, protocolo, código, tabelas, gráficos vetoriais e manifesto de entradas. Os estudos anteriores e a apresentação permanecem preservados.
''')
p.append(r'''\pagina{Apêndice. Combinações e melhores variantes individuais}
\textbf{As nove combinações conjuntas, cinco anos.} Cada família entra com nível e mudança. Primeiro nome: forma dos termos de troca. Segundo: forma da cesta. Erro relativo a nenhuma mudança, agregado do trio.
''')
rows=[]
for f in ['LOG','DEV','SLOG']:
 for k in ['LOG','DEV','SLOG']:rows.append([f,k,num(metric(60,'POOL',f'JOINT_{f}_{k}').rmse_rw),num(metric(60,'POOL',f'JOINT_{f}_{k}').rmse_ejr)])
p.append(tab(['Forma TT','Forma cesta','Erro / nenhuma mudança','Erro / EJR'],rows,False))
p.append(r'''\textbf{Melhores adições por país e família, cinco anos.} Esta tabela permite escolher uma variante para cada moeda, o que acrescenta seleção em relação ao modelo único do painel. Não é a especificação usada nos gráficos principais.
''')
rows=[]
for c in CC:
 for fam in ['TOT','COM']:
  b=w[(w.h==60)&(w.country==c)&(w.family==fam)].iloc[0];rows.append([c,fam,label(b.model),num(metric(60,c,'EJR').rmse_rw),num(b.rmse_rw)])
p.append(tab(['País','Família','Melhor forma','EJR','Extensão'],rows))
p.append(r'''Mesmo escolhendo a melhor adição de termos de troca para euro e Canadá, o erro não melhora frente ao EJR nesses países na janela completa de cinco anos. Esse resultado reforça que o ganho principal dos termos de troca está no Brasil. As melhores cestas individuais são diferentes e têm ganhos menores.

\textbf{Tabelas completas.} \path{tables/metrics.csv} registra todos os horizontes, países e modelos, inclusive comparações na janela recente e da seleção temporal. \path{tables/winners.csv} identifica explicitamente os vencedores retrospectivos. \path{tables/predictions.csv.gz} contém os valores realizados e as 28 previsões fixas por origem. \path{tables/selection.csv} identifica, em cada origem, o candidato escolhido somente com alvos já conhecidos. \path{tables/in_sample.csv} separa os ajustes históricos por país.

\textbf{Gráficos.} A pasta \texttt{figures} contém as comparações individuais em PNG e PDF vetorial, além das relações EJR de cinco e oito anos e da comparação entre transformações. A fonte LaTeX acompanha o relatório.
\end{document}
''')
(H/'relatorio_ejr_paises_selecionados.tex').write_text('\n'.join(p),encoding='utf-8')
md=['# Melhor adição onde o EJR funciona','',
'Universo fixado antes das transformações: Brasil, euro e Canadá. EJR reestimado apenas no trio.','',
'Em cinco anos: EJR 0,802; melhor TT (log nível + mudança anual em log) 0,628; melhor cesta (desvio nível + mudança percentual) 0,773. Ganhos respectivos de 21,7% e 3,7% no RMSE relativo ao EJR.','',
'Ganho com TT concentrado no Brasil: 0,804 -> 0,544. Euro: 0,898 -> 0,998. Canadá: 0,719 -> 0,920. Cesta: Brasil 0,770; euro 0,911; Canadá 0,701.','',
'Escolha temporal da forma TT, somente com previsões passadas encerradas: 1,273 contra EJR 1,484 na mesma janela de 56 meses. Melhora incremental de 14,2%, mas perde para nenhuma mudança nessa janela.','',
'Na agregação que normaliza cada país pelo respectivo erro do passeio aleatório antes de dar peso igual, TT piora de 0,810 para 0,844. Portanto, o ganho agregado padrão não é generalizado entre países.','',
'Log puro de desvio negativo não existe nos reais. Log(1+desvio) centralizado é exatamente igual ao log centralizado. Log com sinal foi testado separadamente.','',
'Relatório: ../output/pdf/relatorio_ejr_paises_selecionados.pdf. Gráficos individuais: figures/comparacao_BRL.png, comparacao_CAD.png, comparacao_EUR.png.']
(H/'RESULTADOS.md').write_text('\n'.join(md),encoding='utf-8')
print('LaTeX report and results written')
