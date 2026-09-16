# Aprofundamentos após a primeira rodada

O desenho principal é a média de três módulos, sem pesos otimizados. A rodada inicial encontrou: (1) a interseção de todos os filtros elimina retorno; (2) a média preserva retorno e reduz risco na janela comum; (3) retirar BRL reduz fortemente o prêmio esperado e faz o limite absoluto de 2% a.a. quase desligar um módulo; (4) o seletor que escolhe o vencedor recente perde para médias fixas.

Para entender a terceira observação, e não substituir silenciosamente o desenho principal, testamos dois limites adicionais: zero e metade da mediana histórica do retorno previsto. Repetimos os casos completo, sem BRL e sem EUR. Estes testes são pós-seleção e aparecem separadamente. Nenhuma nova regra com melhor resultado será vendida como confirmação independente.

O módulo de coortes respeita a orientação da posição aberta. O aumento da probabilidade de perda é convertido em risco da perna comprada/vendida, independentemente do diferencial de juros atual. Exigimos aumento positivo além do percentil passado. Essa política é uma nova especificação, não uma reprodução numérica do drawdown de 3,23% do complemento anterior. A comparação base usa as mesmas datas de formação das coortes.

Outra extensão pós-rodada estima o risco conjunto de 15 pares, com volatilidade e informações comerciais do par. Avaliamos somente os dois pares carry de cada origem e agregamos perdas por data. Essa tentativa econômica mais direta falha na amostra e é divulgada. Não é incorporada à combinação principal. Seu p-valor isolado é apenas descritivo, sem correção da busca histórica.
