# Termos de troca, câmbio real e risco do carrego

Complemento independente ao segundo relatório. Os três estudos anteriores e os 232 arquivos congelados permanecem intactos. PDF: `output/pdf/relatorio_termos_troca.pdf`.

Reprodução: executar `trade_extension/run.ps1` na raiz do projeto. Os dados estão salvos. Não é necessário novo download. O pacote é complementar ao repositório original: reutiliza `src/models.py`, `third/engine.py`, `data/processed`, `secondary/cache/core.npz` e os preços/pesos em `third/data`. O teste de preservação requer o projeto anterior completo. Python e Tectonic são os portáteis existentes.

## Desenho

- Previsão real e da média real persistente em 12/36/60 meses; nominal EJR; composição anual; termos agregados anuais; exposição aos preços em 12 meses.
- Repetição de perda do carrego, perda adversa e tempo negativo no caminho, caudas da carteira.
- 64 regras/variações de posição, quatro controles para cada regra, seis aprofundamentos de saída de coortes.
- 44 verificações de integridade e sete figuras vetoriais PDF/PNG.
- Benchmarks reestimados nas mesmas linhas de treino das extensões. Valores de `base_pred` acompanham cada previsão avaliada.
- Avaliação pareada por modelo, com origens explicitadas. Modelos com sinais anuais/previsões recursivas têm história menor. Não há correção completa de vintages.

`PROTOCOL.md` documenta o desenho inicial; `EXPLORATION.md` registra decisões de amostra e aprofundamentos. Não constituem pré-registro público nem teste sobre dados históricos desconhecidos.

## Arquivos principais em tables/

| Arquivo | Conteúdo |
|---|---|
| prediction_metrics.csv, predictions.csv.gz | Todas as métricas e previsões pareadas |
| audit.csv | Calendário de disponibilidade de cada estimação |
| annual_predictions.csv, annual_metrics.csv | Primeiro estágio de composição anual |
| annual_tot_predictions.csv, annual_tot_metrics.csv | Piloto de previsão dos termos agregados |
| strategy_metrics.csv, strategy_returns.csv.gz | Políticas, custos, controles e trajetórias |
| conditions.csv, conditional_targets.csv | Resultados condicionais a alertas históricos |
| prediction_sensitivity.csv, policy_sensitivity.csv | Defasagens, penalidades, janelas e países |
| cohort_variations.csv | Cortes e custos da saída por risco |
| strategy_intervals.csv, risk_intervals.csv | Intervalos condicionais de retorno, volatilidade, drawdown e cauda |
| prediction_intervals.csv, nonoverlap.csv | Diagnósticos de horizontes longos |
| validation.csv | Auditoria automatizada |

`expost_exposure` é controle descritivo que usa exposição média futura; nunca apresentado como estratégia implementável. `past_exposure` usa somente histórico, mas não iguala exatamente a média realizada. A comparação de proteção precisa distinguir os dois.

O campo `h` dos alvos de risco inclui o mês adicional entre sinal e entrada; o nome da tarefa contém o horizonte efetivo do caminho (por exemplo, `adverse_12`). Retornos de carteira incluem juros, câmbio, funding e custos; perda adversa por moeda é uma aproximação em log sem custos de negociação. Termos de troca em preços não equivalem a composição ou a uma quebra estrutural identificada.

Todos os resultados são exploratórios. Intervalos em blocos são condicionais aos sinais e não corrigem seleção de políticas. O resultado principal é uma distinção entre adaptação a mudança observada e capacidade de antecipar mudança, com resultados promissores e falhas documentados no PDF.
