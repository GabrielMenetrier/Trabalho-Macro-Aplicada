# Adições onde o EJR já funciona

15/09/2026, antes de estimar as novas transformações. Sem alterar slides ou estudos anteriores.

Universo principal: BRL, EUR e CAD, escolhido porque o EJR já superou nenhuma mudança em cinco anos no estudo anterior. Reestimar a inclinação comum apenas nesse grupo. A verificação anterior às adições confirmou RMSE relativo 0,802 no agregado. A escolha de países é informada pela mesma história; resultados continuam exploratórios. Não chamar esse trio de amostra original do artigo. Canadá e Alemanha são países de referência do paper, enquanto Brasil foi examinado na extensão de regimes. Aqui EUR usa a Alemanha apenas nos dados comerciais.

Alvo: mudança futura do log câmbio nominal local/USD em 1–8 anos, 60 meses como comparação principal. Amostra outubro/1999–agosto/2026; origens avaliadas desde janeiro/2010 ou primeira disponibilidade. Treino expansivo com mínimo de 60 origens completas por moeda, preservando início h+61 do código anterior, alvos j+h <= t−1. Mesmas linhas para base e extensões. Níveis de termos de troca anuais Y−2 e variação anual conhecida. Preços reais da cesta disponíveis t−2 e mudança de 12 meses. Reutilizar dados congelados e construção do estudo ejr_trade.

## Transformações

Para índice positivo Z e média aritmética disponível A_t:
- LOG: log Z menos sua média histórica de logs disponível em t.
- DEV: Z/A_t−1, desvio proporcional da média aritmética.
- SLOG: sinal(DEV)*log(1+abs(DEV)), depois centralizado pela média até t.
- Log do desvio puro não é definido se DEV<=0. Não descartar esses meses nem somar uma constante arbitrária baseada em mínimos futuros.
- LOG1P: log(1+DEV), centralizado. É algebricamente igual ao LOG; verificar numericamente e não contar como candidato adicional.

Mudanças anuais: log-variação centrada para LOG; taxa simples exp(log-variação)−1 centrada para DEV; log com sinal dessa taxa simples para SLOG. Todos os centramentos são recalculados com dados até a origem, inclusive para linhas de treinamento.

Grade de 27 extensões distintas: 2 famílias (termos de troca/cesta) ×3 transformações ×3 conteúdos (nível/mudança/ambos) =18. Mais 9 combinações conjuntas de nível+mudança das duas famílias, com 3×3 formas. Base EJR sem adições. Nenhum fator global extra neste exercício.

## Seleção e gráficos

Mostrar o menor RMSE fora da amostra encontrado por família e horizonte, rotulado melhor retrospectivo. Mostrar todas as variantes, não somente vencedoras. Não escolher país/horizonte novamente para a tabela principal. Vencedor geral em cinco anos do painel é único para os gráficos comparáveis por país; tabela separada permite ver os melhores individuais. Não chamar o maior R² histórico de melhor previsão.

Seleção temporal adicional: em cada origem t, escolher entre EJR e candidatos da família usando apenas erros das previsões feitas desde 2010 cujos alvos terminaram até t−1, mínimo 24 origens mensais completas. Comparar com base e campeão fixo nas mesmas origens da seleção. Esta checagem respeita calendário, mas não desfaz a seleção prévia de países e especificações.

Gráficos: dispersão EJR de câmbio real versus mudança futura nominal; lado a lado ajuste realizado/estimado para EJR e extensão, com intercepto e regressão por país, como descrição histórica; previsões fora da amostra versus realizado para o mesmo horizonte e modelos do painel. Usar escalas iguais e indicar treino, origens, alvos, R² histórico e RMSE fora da amostra. Incluir evolução de erro e diferenças entre transformações.

Auditoria: identidade LOG1P/LOG, invariância à unidade do índice, truncamento e perturbação futura, correspondência EJR, manual/statsmodels independente, maturidade do seletor, mesmas amostras. Não afirmar confirmação estatística a partir do vencedor dentre 27 extensões e muitos horizontes. Poucos episódios de cinco a oito anos. Relatório separado com todos os resultados, gráficos em PDF/PNG, código e dados de previsões.
