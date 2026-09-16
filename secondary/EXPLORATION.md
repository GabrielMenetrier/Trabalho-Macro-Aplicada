# Registro das variações após a primeira rodada

Três famílias escolhidas para aprofundamento: entrada no carry (ganho pequeno do filtro de retorno total), dimensionamento contínuo (Sharpe inicialmente superior) e hedge do ativo americano (retorno e risco mudam sem vender SPY/BIL). Não são testes confirmatórios: a escolha ocorreu após observar os resultados da rodada principal.

- Entrada: retorno esperado anual mínimo 0%, 0,5%, 1%, 2%, 4%; média do sinal de 1, 3, 6 meses.
- Tamanho: normalização pela mediana histórica com pelo menos 6, 12, 24, 36 observações; teto de exposição 0,5, 1 ou 1,5. Normalizações fixas de 1%, 2%, 4% ao ano. Comparar q bruto com coeficientes 0, 0,25, 0,5, 1 e 2.
- Hedge: proporções fixas 0%, 25%, 50%, 75%, 100%; sinais cambiais suavizados em 1/3/6 meses, limiares anuais -1/0/+1%; sinal com juros e hedge contínuo. Custos de rolagem de 2/5/10 bps para regras centrais.
- Datas comuns: janeiro de 2013 a agosto de 2026; subdivisões 2013-2018 e 2019-2026. Comparações de exposição média ex post e deslocamento circular de sinais são apenas diagnósticos.

Correções de auditoria antes da entrega: orientação do hedge total verificada pela identidade F/S=(1+iBR)/(1+iUSD); previsão de depreciação USD inferior ao diferencial BR-US implica hedge. Não emitir p-valor HAC quando há menos de três blocos do horizonte ou 36 datas. Previsões de perda máxima limitadas a valores não negativos, fração submersa limitada a [0,1].
