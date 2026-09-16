# Quem antecipa quem? Câmbio e commodities

Terceiro estudo, separado dos dois relatórios anteriores. O PDF tem 22 páginas e testa as 15 ideias discutidas: câmbio real para commodities, commodities para câmbio nominal e extensões/interações do modelo EJR. Não há carteiras ou retornos de estratégias.

## Reprodução

Na raiz do repositório, executar `./third/run.ps1`. O script usa os dados salvos, o Python em `tools/python/python.exe` e o Tectonic do projeto. As dependências são as já presentes em `requirements-lock.txt`; não houve instalação adicional. Não é necessário novo download. Para recolher fontes públicas, `third/download.py` preserva snapshots existentes e registra erros dos artigos externos separadamente dos dados usados na estimação.

A sequência é `prepare.py`, `analyze.py`, `sensitivity.py`, `validate.py`, `build_report.py`, compilação e revisão do PDF. `rescore.py` foi um auxiliar de desenvolvimento; a referência de reprodução é `analyze.py`, que estima todos os modelos diretamente da história completa, sem depender de previsões salvas de uma rodada anterior.

## Resultados e leitura

- `tables/metrics.csv`: grade completa de modelos, benchmarks, países, horizontes e períodos. RMSE relativo menor que 1 indica melhora; `rmse_rw` compara com nenhuma mudança.
- `tables/predictions.csv.gz`: uma linha por previsão/modelo/alvo/origem, sem repetir o mesmo preço mundial como se fossem observações independentes por país.
- `tables/audit.csv`: primeiro/último mês de treino, data em que o último alvo ficou disponível e tamanho do treino.
- `tables/sensitivity.csv`: penalização, janela, atrasos, países e períodos; `candidate_intervals.csv` e `nonoverlap_phases.csv` documentam candidatos escolhidos após a primeira rodada.
- `data/`: preços, pesos comerciais de 1994–1996, entradas WDI, construção das cestas, arquivos brutos, URLs e SHA-256.
- `PROTOCOL.md`, `EXPLORATION.md`: desenho inicial e mudanças declaradas após a primeira rodada.
- `tables/validation.csv`: verificações de integridade e reprodução.
- `relatorio_terciario.tex`, `figures/`: fonte LaTeX e oito figuras vetoriais/PNG.

O PDF está em `output/pdf/relatorio_terciario.pdf`. A revisão visual gera imagens temporárias em `tmp/pdfs/third/`.

## Interpretação principal

A extensão EJR com componente comercial específico, descontando o fator global, é a candidata mais interessante em cinco anos. A melhora contra EJR aparece em várias sensibilidades; a superioridade contra nenhuma mudança desaparece sem Brasil e nas origens recentes. O histórico de cinco anos contém só cerca de dois blocos efetivamente independentes. As previsões de commodities frequentemente melhoram um benchmark de história própria sem superar nenhuma mudança.

As extensões `REJR` mantêm o intercepto restrito e a centralização do EJR original. As extensões `Q` têm efeitos de país e ridge; comparar cada uma com sua base evita atribuir às commodities uma melhora que decorre de trocar o estimador. P-valores são bilaterais e ajustados por Holm, incluindo comparações contra base e nenhuma mudança; p baixo também pode indicar piora. Inferência é suprimida com menos de 36 datas ou três blocos do horizonte. Intervalos de candidatos são pós-seleção e condicionais às previsões.

As médias mensais de commodities entram com atraso: nominal um mês, real dois. O alvo nominal é `p[t+h]-p[t-1]`, o real é `r[t+h]-r[t-2]`, enquanto o alvo cambial é `s[t+h]-s[t]`. O relatório explicita as diferenças. Pesos comerciais antigos evitam usar composição futura, mas não são vintages completos e podem representar mal pautas posteriores. EUR usa Alemanha como proxy.

## Preservação

166 arquivos dos estudos anteriores foram congelados em `previous_hashes.json`. `third/freeze.py` confere que permanecem idênticos. O pacote terceiro deve ser extraído junto do repositório existente; ele não substitui os anteriores e não inclui novamente o runtime portátil.
