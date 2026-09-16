# Prever menos, decidir melhor

Síntese final de macroeconomia aplicada: uma política com módulos de dimensionamento EJR, adaptação comercial observada e permanência por risco. Relatório independente: `output/pdf/relatorio_sintese.pdf`. Os 306 arquivos congelados dos estudos anteriores permanecem intactos.

## O que foi entregue

- 23 páginas, nove gráficos em PDF vetorial/PNG, discussão acadêmica e aplicação a carry/hedge.
- 16 políticas principais e controles, comparação em datas iguais; 390 linhas de sensibilidades.
- 48 combinações de BIL/SPY, hedge e custo; numerário BRL separado do carry USD.
- Seleção anual por desempenho passado, atribuição contábil, controle max-t na grade principal e intervalos condicionais de valor econômico e risco.
- Refinamento explícito da barreira de entrada e tentativa de prever risco conjunto dos pares, com resultado negativo divulgado.
- 46 verificações de integridade.

O relatório não prova alfa universal ou causalidade. A média de módulos foi definida antes dos novos resultados, mas seus componentes foram escolhidos a partir de história já examinada. Os intervalos não corrigem toda seleção histórica do projeto. `PROTOCOL.md` e `EXPLORATION.md` documentam essas escolhas.

## Reprodução

Executar `synthesis/run.ps1` na raiz do repositório. Usa Python e Tectonic portáteis em `tools/`. Os snapshots anteriores são os insumos; não há novo download ou credencial. O pacote contém os arquivos novos e insumos mínimos de reprodução. A verificação de preservação e a reprodução integral exigem o repositório anterior completo, incluindo os binários portáteis.

Se o Windows bloquear scripts PowerShell, usar `./tools/python/python.exe synthesis/reproduce.py`. Essa alternativa executa a mesma cadeia sem mudar a política de execução do sistema.

Ordem: `analyze.py`, `robustness.py`, `selection.py`, `inference.py`, `hedge.py`, `refinement.py`, `pair_risk.py`, `validate.py`, `build_report.py`, compilação LaTeX, `qa_pdf.py`. O script interrompe ao primeiro erro. `package.py` monta a entrega após validação e QA.

| Arquivo em tables/ | Conteúdo |
|---|---|
| metrics.csv, returns.csv.gz | Datas, métricas e trajetórias de todas as políticas |
| attribution.csv, netting.csv | Juros, câmbio, interação, custos, países e compensação de ordens |
| robustness.csv, exposure_controls.csv, episodes.csv | Parâmetros, universos, custos, funding, atraso, risco e episódios |
| selection_metrics.csv, selection_audit.csv | Escolha anual usando somente retornos anteriores |
| economic_intervals.csv, risk_intervals.csv | Certeza equivalente, volatilidade e drawdown, blocos 12/36 |
| search_adjustment.csv | Max-t de 14 alternativas versus carry, somente grade principal |
| hedge_metrics.csv, hedge_returns.csv, hedge_intervals.csv | Aplicação aos ativos, com posição mantida |
| hurdle_refinement.csv | Limite absoluto, relativo e zero; completo/sem BRL/sem EUR |
| pair_prediction_metrics.csv, pair_strategy_metrics.csv | Tentativa de risco conjunto dos pares |
| commodity_audit.csv, pair_audit.csv, validation.csv | Calendários e integridade |

## Convenções

Retorno principal em USD, colateral em caixa USD, posições brutas até 1 e líquidas zero. Sinal t, execução t+1, retorno t+2. Julgamento do risco de uma coorte respeita as pernas originais; previsão de aumento de risco precisa ser positiva. Coortes duram 12 meses, com formação gradual e sem duplicar o orçamento. A média combina pesos antes de custos.

Certeza equivalente é uma aproximação média-variância dos excessos, anualizada, com gamma 3/5/10. Não é utilidade exata de caudas. `expost` usa exposição média futura e é diagnóstico; `past` só usa história admissível, sem igualar a média realizada. Exclusões de moedas mudam o universo de posições, não reestimam todos os modelos de risco sem aquele país.

O hedge usa forward sintético derivado das taxas oficiais. O mesmo notional de hedge produz a mesma adição aritmética em BIL/SPY, mas não o mesmo CAGR ou risco. Taxas oficiais, séries revisadas e ausência de cotações executáveis limitam a interpretação de mercado.
