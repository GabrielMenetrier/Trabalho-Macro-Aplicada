# Termos de troca onde o EJR já funciona

Estudo solicitado após a comparação de seis moedas. Universo principal BRL, EUR e CAD, fixado pelos resultados conhecidos em cinco anos antes de estimar as novas transformações. O EJR é reestimado no trio; não se trata da amostra original integral do artigo.

- [Relatório PDF](../output/pdf/relatorio_ejr_paises_selecionados.pdf)
- [Resultado resumido](RESULTADOS.md)
- [Fonte LaTeX](relatorio_ejr_paises_selecionados.tex)
- [Comparação Brasil](figures/comparacao_BRL.png)
- [Comparação Canadá](figures/comparacao_CAD.png)
- [Comparação euro](figures/comparacao_EUR.png)

## Reprodução

A partir da raiz, com o ambiente já instalado no projeto:

```powershell
.\tools\python\python.exe ejr_trade_selected/run.py
.\tools\python\python.exe ejr_trade_selected/diagnostics.py
.\tools\python\python.exe ejr_trade_selected/figures.py
.\tools\python\python.exe ejr_trade_selected/build_report.py
.\tools\tectonic.exe ejr_trade_selected/relatorio_ejr_paises_selecionados.tex --outdir output/pdf --keep-logs
.\tools\python\python.exe ejr_trade_selected/qa_pdf.py
```

Reutiliza dados e código de `ejr_trade`, `third` e `src`. Os hashes das entradas estão em `input_hashes.json`. Nenhum download novo é necessário. Gráficos também estão em PDF vetorial. Relatório usa Arial e Tectonic, cujos pacotes já estão no cache local.

## Desenho e arquivos

`PROTOCOL.md` define a grade anterior aos resultados; `EXPLORATION.md` registra os diagnósticos posteriores de heterogeneidade. São 27 extensões + EJR, oito horizontes, mesmos dados de treino e avaliação dentro de cada comparação. A transformação de log(1+desvio) centralizado é igual ao log centralizado e não é contada como candidato adicional. Log puro do desvio não é definido para desvios negativos. Log com sinal é uma transformação distinta e foi testada.

`tables/metrics.csv` tem todas as métricas, não só vencedores. `tables/winners.csv` identifica vencedores retrospectivos por família, país e horizonte. `tables/predictions.csv.gz` contém as 28 previsões fixas e o realizado por origem; `selection.csv` registra a escolha temporal com validações maduras; `coefficients.csv` os coeficientes recursivos; `audit.csv` o calendário; `in_sample.csv` as regressões históricas com intercepto por país; `pooling_diagnostics.csv` os efeitos de composição da amostra e normalização por país; `graph_values.csv` permite conferir os rótulos dos gráficos.

`fixed`: amostra completa disponível por horizonte, origens desde janeiro/2010. `recent`: origens 2019+. `adaptive_TOT/COM/JOINT/ALL`: todas as estratégias fixas e o seletor são avaliados na mesma janela em que o seletor daquela família dispõe de pelo menos 24 origens já encerradas. A seleção inclui a possibilidade EJR sem adições. São regras de escolha de **modelo de previsão**, não carteiras.

Os gráficos de comparação mantêm os campeões de cada família no agregado de cinco anos para todos os países: TOT_LOG_LD e COM_DEV_LD. Linha superior: ajuste histórico OLS por país com intercepto, origens out/1999–ago/2021, R² ajustado. Linha inferior: previsão OOS do painel de três países, origens jan/2010–ago/2021, RMSE/RW. Essas duas linhas são exercícios diferentes, explicitamente identificados. As escalas são iguais nos seis painéis de cada país.

359 verificações principais e três reproduções independentes em statsmodels. QA do PDF em `qa/checks.json`, incluindo rótulos de gráficos, limites de página, falta de glifos e preservação das entradas. Estudos anteriores e slides não foram alterados.

Os ganhos são exploratórios: países escolhidos por evidência prévia na mesma história; modelo vencedor escolhido retrospectivamente; dados revisados sem vintages completos; poucos episódios longos. Termos de troca melhoram sobretudo Brasil. Com normalização por país, a vantagem agregada dos termos de troca desaparece. A seleção temporal conserva parte do ganho incremental em outra janela, mas nela não supera nenhuma mudança.
