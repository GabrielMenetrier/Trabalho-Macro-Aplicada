# Câmbio previsível, retorno incerto

Trabalho de Macroeconomia Aplicada (EPGE/FGV, 2026.2), baseado na aula 8 de Marcos Sonnervig e em Eichenbaum, Johannsen e Rebelo (2021).

## Entrega

- **Relatório:** `output/pdf/relatorio.pdf`.
- **Fonte LaTeX:** `report/relatorio.tex`; compile a partir da raiz do projeto.
- **Gráficos:** `output/figures/`, em PDF vetorial e PNG.
- **Resultados completos:** `output/tables/`, incluindo todas as previsões, retornos, pesos e variações testadas.
- **Dados públicos congelados:** `data/raw/`; URLs, data de coleta e hashes em `manifest.json`.
- **Revisão de vazamento e contabilidade:** `AUDITORIA.md`.
- **Apresentação:** `ROTEIRO_APRESENTACAO.md` (roteiro de exposição, não um slide deck).

Pergunta: a previsibilidade cambial de longo prazo melhora o retorno de uma carteira após juros e custos, em comparação com carry puro?

## Resultados principais

O resultado brasileiro dos slides foi recuperado: beta de oito anos -1,808 e R² de 0,883. No painel de BRL, EUR, JPY, GBP, CAD e SEK, o EJR não bate o passeio aleatório no agregado nas janelas disponíveis por horizonte. Em cinco anos, a razão de RMSE é 1,037; Brasil, Canadá e euro têm resultados individuais melhores que o benchmark.

Entre março de 2010 e agosto de 2026, a estratégia principal EJR + carry rende 2,73% a.a. em USD, contra 4,11% do carry simples. Volatilidade 4,16%, Sharpe excedente 0,31, queda máxima 7,01%. A evidência não sustenta arbitragem nem alfa incremental robusto. Essas conclusões são mantidas no relatório mesmo quando desfavoráveis à proposta inicial.

## Execução local

Na pasta de trabalho atual há um Python portátil em `tools/python/python.exe`. Ele foi instalado dentro do projeto, sem substituir o Python do sistema.

```powershell
.\run.ps1
.\run.ps1 -Compile
```

Em outro computador, instale Python 3.12, crie um ambiente isolado e execute, a partir da raiz:

```text
python -m pip install -r requirements-lock.txt
python src/prepare_data.py
python src/analyze.py
python -m pytest -q tests
python src/make_figures.py
python src/make_report_tables.py
tectonic report/relatorio.tex --outdir output/pdf --keep-logs
python src/qa_pdf.py
```

O Tectonic baixa os pacotes TeX na primeira compilação. A fonte também pode ser compilada com XeLaTeX instalado: `xelatex -output-directory=output/pdf report/relatorio.tex`, duas vezes, na raiz. O arquivo `main.tex` é uma entrada alternativa para serviços como Overleaf, preservando a estrutura de pastas.

Os dados brutos já estão incluídos: **nenhuma rede é necessária para repetir a análise**. O download é uma etapa separada:

```text
python src/download_data.py
```

O downloader reutiliza arquivos existentes e só baixa ausentes. Para uma coleta nova, use outra cópia do projeto com `data/raw/` vazio, atualize explicitamente as datas de corte em `download_data.py` e `prepare_data.py`, execute a cadeia completa e confira cobertura e alterações de metodologia. Não sobrescreva o snapshot da entrega para tentar reproduzi-la. Não há credenciais ou chaves de API no projeto.

## Desenho previamente fixado para esta execução

- Universo: seis moedas, ordem BRL, EUR, JPY, GBP, CAD, SEK.
- Base mensal: out/1999 a ago/2026; câmbio de fim de mês.
- Modelo principal: painel EJR sem intercepto, média de cada moeda calculada com dados até a origem.
- CPI defasado dois meses; ausência isolada do CPI de out/2025 usa a última referência passada para o sinal, nunca interpolação futura.
- Treinamento: pelo menos 60 origens maduras por moeda; nenhum alvo termina depois de `origem - 1 mês`.
- Horizonte principal: 60 meses. Demais horizontes: 12, 24, 36, 84 e 96, divulgados sem seleção do melhor.
- Sinal: apreciação esperada da moeda estrangeira em USD, dividida pelo horizonte, mais diferencial de juros mensais.
- Ranking: duas compras de 25% e duas vendas de 25%; caixa USD de colateral.
- Sinal em t, execução no fim de t+1, primeiro resultado em t+2.
- Custos por ponta: BRL 10 pb, SEK 3 pb e demais 2 pb; spread de captação de 50 pb a.a. sobre vendas.
- Incluídos giro por mudança de preços, entrada e liquidação final. Não incluídos impostos individuais, crédito, restrições de short e impacto por volume.
- Coortes: sinais guardados por 60 meses, peso 1/60 por coorte, posições opostas compensadas, orçamento sem multiplicação por horizonte.

## Natureza dos ativos

O painel multimoedas é uma **simulação de depósitos/passivos curtos com proxies de taxas oficiais**. Ele não usa retornos históricos de contratos a termo negociáveis. Taxas de política não são yields garantidos ao investidor e não representam retorno total de títulos longos.

Para tornar explícita a escolha de ativo em dólar, há testes adicionais com BIL (Treasury bills de 1 a 3 meses) e SPY (S&P 500), a partir de fechamentos ajustados do Yahoo Finance. Esses retornos de mercado são convertidos em BRL e comparados entre manter continuamente e alternar com caixa BRL usando o mesmo sinal cambial. O modelo não prevê o prêmio acionário. O custo total assumido por ponta é de 12 pb. Os ajustes de dividendos entram apenas nos resultados realizados; nunca nos preditores.

## Mapa dos resultados

| Arquivo em `output/tables/` | Conteúdo |
|---|---|
| `classroom_replication.csv` | Brasil 1995–abr/2026, versões CPI SA e NSA, comparação com slides |
| `horizon_regressions.csv` | Regressões nominais e de preços relativos por moeda/horizonte |
| `forecast_observations.csv` | Cada previsão, origem, data de maturação e realização |
| `forecast_accuracy.csv` | RMSE/RW, R² OOS, acerto direcional e CW/Holm |
| `forecast_common_origins.csv` | Comparação dos horizontes sobre origens idênticas |
| `bootstrap_null.csv` | Testes sob nominal imprevisível, real AR(1) e raiz unitária |
| `timing_audit.csv` | Último alvo e última origem de treinamento, referência máxima do CPI |
| `portfolio_returns.csv` | Retorno, custos, spread, caixa, giro e NAV mensal |
| `portfolio_metrics.csv` | CAGR, risco, Sharpe, quedas e intervalos bootstrap |
| `weights_main.csv` | Posições efetivamente carregadas no mês do retorno |
| `contributions_main.csv` | Contribuição mensal por moeda, antes do custo de giro |
| `robustness.csv` | Custos, lags, janela móvel e exclusões de países |
| `portfolio_horizons.csv` | Horizontes em janela financeira comum desde jan/2013 |
| `subperiods.csv`, `regimes.csv` | Episódios históricos e condições conhecidas antes da posição |
| `short_training_stress.csv` | Treinamento mínimo de 36 origens, incluindo negociação em 2008 |
| `incremental_value.csv` | Diferença frente a carry, CI e alfa condicional a carry/momentum |
| `return_bootstrap_ci.csv` | Intervalos com blocos de 12 e 60 meses |
| `brl_metrics.csv`, `brl_returns.csv` | Caixa e alocação USD/BRL, com numerário brasileiro |
| `etf_metrics.csv`, `etf_returns.csv` | Implementação BIL/SPY em reais |
| `latest_scenarios.csv` | Cenários ainda não realizáveis, sem avaliar futuro não observado |

**Atenção ao POOL:** `forecast_observations.csv` contém duplicatas identificadas como `country=POOL` para cálculo agregado. Filtre POOL ou moedas individuais, nunca some ambos. O número de moedas não torna independentes os choques comuns.

## Reprodutibilidade e limites

Semente: 20260910; bootstrap nominal: 999 repetições por DGP; bootstrap de retornos: 4.999. O primeiro tem AR(1) com persistência limitada a 0,995 e 300 meses de aquecimento ou raiz unitária. É uma extensão ao artigo, não sua réplica exata.

As séries macroeconômicas são vintages atuais. Os testes confirmam cronologia do algoritmo; não certificam eliminação integral de revisões históricas. A descrição correta é **pseudo fora da amostra com defasagens conservadoras**. A auditoria explica o risco residual.

O material original da disciplina é preservado em `Macro_Aplicada_2026_shared/`. A pasta recebida continha os PDFs, mas não o código da nota de replicação. Não houve acesso a outro repositório remoto, envio por e-mail nem submissão do trabalho.

As orientações registram apresentação em 14 ou 16 de setembro e relatório até 25 de setembro; tema exige aprovação prévia. Autoria e aprovação do tema continuam sendo informações administrativas do aluno. A entrega técnica está pronta para revisão; o roteiro ajuda a defender os resultados e as limitações em sala.
