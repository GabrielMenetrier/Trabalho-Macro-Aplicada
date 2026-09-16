# Quando fazer carrego? Extensão secundária

O relatório principal e seus 99 arquivos de dados/resultados/código foram preservados por comparação SHA-256. O novo PDF está em `output/pdf/relatorio_secundario.pdf`, compilado da fonte `secondary/relatorio_secundario.tex`.

## Conteúdo

- 12 famílias de testes, 32 carteiras/controles principais.
- 43 especificações de carry e 62 combinações de ativo/hedge/custo na exploração adicional.
- 18 novos alvos preditivos: 3 modelos (controles, controles + EJR e controles + q), duas janelas de avaliação. 19.725 previsões individuais avaliadas.
- 7 gráficos vetoriais com cópias PNG e tabelas completas em CSV.
- 22 verificações de integridade, incluindo cronologia, prefixo temporal, sinais de forward e preservação do trabalho original.

`PROTOCOL.md` registra o desenho anterior aos resultados da extensão; `EXPLORATION.md`, a escolha das famílias aprofundadas. Não são pré-registro público nem validação sobre dados históricos ainda não vistos. A separação recente/antiga é diagnóstico de estabilidade.

## Reprodução

Na raiz do repositório, executar `./secondary/run.ps1`. Os dados adicionais já estão salvos; não é necessário download para reproduzir resultados. `download_extra.py` permite refazer a coleta pública, mas preserva arquivos já presentes. Python e Tectonic são os executáveis portáteis do projeto em `tools/`; as bibliotecas seguem `requirements-lock.txt`.

Ordem: `analyze.py`, `variations.py`, `validate.py`, `build_report.py`, compilação LaTeX. `qa_pdf.py` renderiza todas as páginas para inspeção visual em `tmp/pdfs/secondary/`. `freeze.py` confere novamente os hashes originais. O teste de preservação exige o repositório original completo; o pacote secundário deve ser extraído junto dele, não tratado como substituto.

## Onde procurar resultados

| Arquivo em `tables/` | Conteúdo |
|---|---|
| `strategy_metrics.csv`, `strategy_returns.csv` | 32 carteiras/controles principais, custos e exposição |
| `conditions.csv`, `timing_placebo.csv` | quando o carry funcionou e diagnóstico de alinhamento temporal |
| `primary_intervals.csv` | controles de exposição e intervalos principais |
| `variation_metrics.csv`, `variation_intervals.csv` | todas as variantes de carry, subperíodos e intervalos |
| `prediction_metrics.csv`, `prediction_observations.csv` | resultados e previsões de todos os 18 alvos |
| `prediction_audit.csv`, `ejr_audit.csv` | última informação admitida em cada estimação |
| `horizon_agreement.csv` | redundância dos sinais de 1/3/5/8 anos |
| `hedge_metrics.csv`, `hedge_returns.csv` | hedge preservando BIL/SPY desde 2010 |
| `hedge_variations.csv`, `hedge_intervals.csv` | grades, custos, datas comuns e controles de hedge |
| `validation.csv` | verificações de integridade |

RMSE relativo menor que 1 significa melhora. Para probabilidades, o quadrado dessa razão é o Brier relativo. O p-valor é bilateral: pode refletir piora; não é reportado com menos de 36 datas ou três blocos do horizonte. Holm inclui EJR/q e períodos integral/recente. Intervalos bootstrap das estratégias são condicionais aos sinais, não ajustados por seleção de parâmetros.

Os resultados econômicos mais interessantes foram dimensionamento gradual, filtro de retorno previsto acima de 2% a.a. com média de seis meses e hedge gradual de ativos americanos. Nenhum constitui comprovação de arbitragem ou de proteção cambial confiável fora desta amostra. O PDF detalha amostras curtas, diferença entre retorno e risco, custos, proxy de funding, forward sintético e ausência de vintages integrais.
