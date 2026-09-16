# EJR com termos de troca

Estudo separado solicitado em 15/09/2026. Replicação da equação preditiva agrupada (3.4), usando a base de seis moedas do projeto, e extensões com termos de troca observados e proxy nacional de commodities. Sem carteiras e sem alterações nos slides.

- [Relatório PDF](../output/pdf/relatorio_ejr_termos_troca.pdf)
- [Resultados resumidos](RESULTADOS.md)
- [Fonte LaTeX](relatorio_ejr_termos_troca.tex)
- [Protocolo anterior à estimação](PROTOCOL.md)
- [Aprofundamento e reconciliação com o resultado antigo](EXPLORATION.md)

## Reprodução a partir da raiz

```powershell
.\tools\python\python.exe ejr_trade/run.py
.\tools\python\python.exe ejr_trade/diagnostics.py
.\tools\python\python.exe ejr_trade/validate_extra.py
.\tools\python\python.exe ejr_trade/figures.py
.\tools\python\python.exe ejr_trade/build_report.py
.\tools\tectonic.exe ejr_trade/relatorio_ejr_termos_troca.tex --outdir output/pdf --keep-logs
.\tools\python\python.exe ejr_trade/qa_pdf.py
```

Os dados novos estão em `data/` e os anteriores permanecem nas pastas originais. Download separado: `download.py`. Não é preciso rede para repetir as regressões. O Tectonic pode precisar baixar pacotes na primeira compilação, e o relatório usa a fonte Arial. Requer o ambiente do projeto com numpy, pandas, scipy, statsmodels, matplotlib e PyMuPDF. O teste de independência temporal é executado por `run.py` e `validate_extra.py`.

## Resultados completos

| Arquivo | Conteúdo |
|---|---|
| tables/metrics.csv | Todos os modelos, horizontes, países, recortes e sensibilidades fixados |
| tables/predictions.csv.gz | Todas as previsões principais, por origem, país e horizonte |
| tables/audit.csv | Janelas de treinamento, último alvo e número de datas |
| tables/coefficients.csv | Coeficientes recursivos de todos os modelos principais |
| tables/available_inputs.csv | Valores conhecidos e anos/meses de origem das informações |
| tables/basket_weights.csv | Pesos da cesta de termos de troca e exposição líquida antiga |
| tables/in_sample.csv | Regressões históricas por moeda com intercepto, R² ajustado |
| tables/nonoverlap.csv | Avaliação em sequências sem sobreposição para todos os offsets |
| tables/global_diagnostics.csv | Reconciliação da especificação antiga 0,890, fator global e proxy nova |
| tables/validation.csv | 527 verificações de pares, datas, preservação e invariância temporal |
| tables/extra_validation.csv | 19 verificações adicionais e estimação independente em statsmodels |
| tables/global_validation.csv | Correspondência numérica com third/engine.py em cinco anos |

EJR base e extensões são reestimados nas mesmas observações dentro de cada cenário. O cenário `merchandise` usa história mais curta e sua base não deve ser comparada diretamente à do cenário `main` como efeito puro do regressor. `late` restringe origens a 2019 em diante. `same_origins` usa novembro/2012–agosto/2018. `quarterly` seleciona fins de trimestre, com treino também trimestral; não reconstrói a amostra trimestral do artigo.

`rmse_rw` é RMSE/modelo de nenhuma mudança; `rmse_ejr` é RMSE/EJR pareado. Abaixo de 1 significa melhora. `p_hac` é um teste bilateral da diferença de perda e não deve ser interpretado sem o sinal da diferença; `p_holm` existe somente na família principal. Horizontes sem extensão temporal suficiente não recebem p-valor. Resultados continuam exploratórios, sem validação em história intocada e sem vintages completos.

Termos de troca principais são construídos pelos deflatores das contas nacionais de bens e serviços, não pelo índice curto de mercadorias. A proxy de commodities usa diferenças entre participações exportadas e importadas com preços reais e hipótese explícita para o restante do comércio. O resultado antigo favorável é outra especificação, com fator global e exposição líquida específica.
