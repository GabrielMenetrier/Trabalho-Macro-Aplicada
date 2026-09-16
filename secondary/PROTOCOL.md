# Extensão exploratória - protocolo antes da execução

Data: 2026-09-10. Não é pré-registro público nem amostra histórica intocada: o relatório original já examinou os dados. Toda conclusão desta extensão é exploratória.

Universo cambial fixo: BRL, EUR, JPY, GBP, CAD, SEK; base USD; mesmos dados, defasagens e custos do trabalho original. Nenhum arquivo original será sobrescrito. EJR de 60 meses é a especificação principal. Sinal no fechamento t, execução no fechamento t+1, primeiro retorno em t+2. Juros de funding entram em todas as posições; caixa recebe USD. Não confundir melhora da média condicional com redução de risco.

Famílias planejadas: (1) ligar/desligar carry agregado; (2) filtrar pares de carry; (3) exposição contínua; (4) probabilidade de câmbio consumir juros em 12 meses; (5) perdas extremas do carry em 1/3 meses; (6) perda máxima no caminho em 12/36/60 meses; (7) concordância 12/36/60/96 meses; (8) saída de coortes; (9) extremos e assimetria; (10) hedge cambial mantendo BIL/SPY; (11) inflação relativa; (12) retornos locais de títulos e ações brasileiras.

Estratégias: comparar carry puro, regra por previsão e controles simples (volatilidade, q sem transformação, momentum). Reportar período integral disponível e 2019 em diante. Ajustes de exposição fixados usando passado; médias de exposição ex post somente como diagnóstico explicitamente rotulado. Custos base e duplicados. Não selecionar moedas/períodos com base no resultado.

Predição de novos alvos: regressão ridge e modelo de probabilidade linear ridge limitado a [0,01;0,99], padronização somente na amostra de treino; penalidade fixa. Treino em expansão, mínimo 36 datas e 100 observações para painel (36 para uma série). Rótulos futuros entram apenas depois de realizados, com margem de um mês e dois meses adicionais para divulgação do CPI. Comparar informações básicas (juros, volatilidade e momentum/inflação) com acréscimo da previsão, e com acréscimo do q. Não interpretar painel como observações independentes.

Inferência: perdas de previsão médias por data, HAC com defasagem pelo menos igual ao horizonte; p-valores exploratórios bilaterais e ajuste Holm em toda a família de comparações preditivas. Estratégias: intervalos bootstrap em blocos de 12 meses para diferenças de excesso de retorno, diagnóstico em blocos de 36. Janelas longas têm poucas observações efetivamente independentes. Toda variação executada aparecerá nos CSVs e sua família no relatório.

Teste 12 é uma extensão piloto brasileira: IMAB11 (títulos públicos indexados à inflação), VALE3 versus ITUB4 (mineração versus banco). SUZB3 versus BBAS3 é uma segunda dupla de sensibilidade; não identifica efeito causal de exportação e está sujeita a diferenças setoriais. BOVA11 é controle de mercado. Dados ajustados de ações/ETFs usados apenas para calcular retornos e momentum, sem usar níveis ajustados como sinal econômico.

Variações após resultados: aprofundar no máximo três famílias com benefício aparente de retorno ou proteção, registrar justificativa e todas as variantes; jamais tratá-las como confirmação fora da amostra de seleção.
