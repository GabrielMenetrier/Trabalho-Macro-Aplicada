# Melhor adição onde o EJR funciona

Universo fixado antes das transformações: Brasil, euro e Canadá. EJR reestimado apenas no trio.

Em cinco anos: EJR 0,802; melhor TT (log nível + mudança anual em log) 0,628; melhor cesta (desvio nível + mudança percentual) 0,773. Ganhos respectivos de 21,7% e 3,7% no RMSE relativo ao EJR.

Ganho com TT concentrado no Brasil: 0,804 -> 0,544. Euro: 0,898 -> 0,998. Canadá: 0,719 -> 0,920. Cesta: Brasil 0,770; euro 0,911; Canadá 0,701.

Escolha temporal da forma TT, somente com previsões passadas encerradas: 1,273 contra EJR 1,484 na mesma janela de 56 meses. Melhora incremental de 14,2%, mas perde para nenhuma mudança nessa janela.

Na agregação que normaliza cada país pelo respectivo erro do passeio aleatório antes de dar peso igual, TT piora de 0,810 para 0,844. Portanto, o ganho agregado padrão não é generalizado entre países.

Log puro de desvio negativo não existe nos reais. Log(1+desvio) centralizado é exatamente igual ao log centralizado. Log com sinal foi testado separadamente.

Relatório: ../output/pdf/relatorio_ejr_paises_selecionados.pdf. Gráficos individuais: figures/comparacao_BRL.png, comparacao_CAD.png, comparacao_EUR.png.