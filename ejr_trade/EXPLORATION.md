# Registro de aprofundamento

Após executar as especificações fixadas em PROTOCOL.md, as duas extensões principais perderam do EJR no agregado em todos os oito horizontes. Para reconciliar a diferença em relação ao resultado antigo (RMSE relativo 0,890 em cinco anos), acrescentei um diagnóstico separado, sem redefinir os testes principais: EJR + fator global de preços reais; EJR + fator global + exposição líquida específica antiga; EJR + fator global + proxy nacional nova. Avaliar todos os horizontes, período recente e retirar BRL/EUR com reestimação. O modelo antigo inclui um fator global que não é termo de troca nacional. Comparação numérica independente contra third/engine.py em cinco anos.

Datas iniciais: preservei a convenção de src/models.py, que inicia o laço em h+61. Assim, a base EJR reproduz exatamente tanto a disponibilidade quanto os valores das previsões anteriores, inclusive 6–8 anos. Não escolhi datas para melhorar desempenho.
