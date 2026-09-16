# Material de apresentação em aula

## Revisão atual (v8)

Tabelas finais ordenadas por retorno anual composto, com uma linha por alternativa e colunas próprias para sinal, método, nova escolha, retorno, Sharpe e queda máxima. Removidos EJR controle e Combinado das comparações finais e dos gráficos correspondentes. Cores preservadas. Guia e notas explicam a diferença entre ranking, otimização com risco acumulado de 60 meses e intervalo entre escolhas. Backtests preservados.

- `../output/presentation/apresentacao_macro_aula_v8_final.pptx`
- `../output/pdf/apresentacao_macro_aula_v8.pdf`
- `../output/pdf/guia_apresentacao_macro_v8.pdf`

Fontes: `revise_v8.py` (parte dos dados e conteúdo v7), `build_builder_v8.py`, `build/new_slides_v8.mjs`, `build_pdfs_v8.py`. Validação: `check_v8.py`, `build/qa_v8/checks.json` (782 verificações) e `build/validation_v8_final.json`. Mantidos 25 slides e 30 páginas no guia. Slides alterados e páginas correspondentes do guia inspecionados no renderizador. Sem reestimação de modelos.

## Revisão anterior (v7)

Apresentação reorganizada em torno da extensão de previsão com termos de troca e dos backtests finais de março/2010–fevereiro/2025. 18 slides principais, roteiro de 17min15s e sete slides de apoio. Guia atualizado de 30 páginas, com conceitos, leitura dos gráficos, fala, calendários e limites.

- `../output/presentation/apresentacao_macro_aula_v7c_final.pptx`
- `../output/pdf/apresentacao_macro_aula_v7.pdf`
- `../output/pdf/guia_apresentacao_macro_v7.pdf`

Slides 7–11: termos de troca, erros por moeda, formas alternativas, ajuste histórico e previsão recursiva. Slides 12–17: desenho das carteiras, 32 curvas de patrimônio em oito painéis, duas tabelas com triplas retorno/Sharpe/queda máxima e estresse de custos. Separação explícita entre seis moedas e BRL/EUR/CAD. Removidos os resultados de otimização com risco mensal e a decomposição. Regras de exposição, sua trajetória positiva e sensibilidades ficam nos slides 21–25, após a conclusão.

As curvas usam cores constantes por sinal e base 100 antes do primeiro retorno comum. O EJR controle de seis moedas e a combinação por país do trio estão identificados separadamente. Todas as séries foram conferidas contra as respectivas tabelas, sem modificar os estudos anteriores. Os gráficos e tabelas no PPTX são nativos e editáveis; o PDF de projeção usa sua renderização. A revisão visual foi feita no renderizador Artifact Tool, não no PowerPoint nativo.

Fontes de edição: `prepare_v7.py`, `data_v7.json`, `content_v7.json`, `build/new_slides_v7.mjs`, `build_builder_v7.py`, `build/deck_v7.mjs`, `build_pdfs_v7.py`, `qa_v7.py`. Finalização: `build/validation_v7c_final.json`. Auditoria: `build/qa_v7/checks.json`, 735 verificações. Renderizações: `build/rendered_v7`. O sufixo v7c identifica o arquivo final após correções de legibilidade; as tentativas v7/v7a/v7b não são a entrega atual.

Para reeditar, executar preparação e geração do builder, depois `deck_v7.mjs` a partir de `presentation/build`, definindo `REVISION_TAG` com nome novo para respeitar o finalizador. Após conferir as renderizações, executar `build_pdfs_v7.py` e ajustar o nome do PPTX final no QA. Nenhum backtest deve ser reestimado para uma mudança apenas editorial.

## Revisão anterior (v6)

Retirado o bloco de previsão com commodities (antigos slides 8–9) e sua equação de extensão. Capa, transições, numeração e guia ajustados. Permanecem os filtros comerciais que fazem parte dos resultados exploratórios de carteira, sem alteração dos backtests.

- `../output/presentation/apresentacao_macro_aula_v6_final.pptx`
- `../output/pdf/apresentacao_macro_aula_v6.pdf`
- `../output/pdf/guia_apresentacao_macro_v6.pdf`

Fontes: `content_v6.json`, `data_v6.json`, `build/deck_v6.mjs`, `build_pdfs_v6.py`, `qa_v6.py`. 14 slides principais e dois de apoio, roteiro de 15min30s. Guia de 22 páginas. Slides preservados conferidos por comparação de pixels, exceto numeração. Capa, apoio de equações e páginas alteradas do guia inspecionados visualmente.

## Revisão anterior (v5)

Separação explícita entre previsão de longo prazo e aplicação mensal. Slides 10–14 mantidos como referências exploratórias. Slide 6 identifica previsão de 60 meses, revisão mensal e ausência de Markowitz; sua falha não rejeita a previsibilidade do artigo. Conclusão e guia ajustados. Nenhum novo resultado estimado.

- `../output/presentation/apresentacao_macro_aula_v5_final.pptx`
- `../output/pdf/apresentacao_macro_aula_v5.pdf`
- `../output/pdf/guia_apresentacao_macro_v5.pdf`

Fontes: `content_v5.json`, `data_v5.json`, `build/deck_v5.mjs`, `build_pdfs_v5.py`, `qa_v5.py`. 18 slides totais, 24 páginas no guia. Conferida a seção 3.3 do artigo local: melhora agregada acima de dois anos, com destaque para quatro e seis.

## Revisão anterior (v4)

Retirada a seção de previsão do próprio câmbio real (antigo slide 10). Guia, transições, conclusão e numeração ajustados. 16 slides principais, dois de apoio, roteiro de 17min55s e guia de 24 páginas. Conteúdo visual dos demais slides preservado.

- `../output/presentation/apresentacao_macro_aula_v4_final.pptx`
- `../output/pdf/apresentacao_macro_aula_v4.pdf`
- `../output/pdf/guia_apresentacao_macro_v4.pdf`

Fontes da revisão: `content_v4.json`, `data_v4.json`, `build/deck_v4.mjs`, `build_pdfs_v4.py` e `qa_v4.py`. Estudos e relatórios de pesquisa preservados.

## Revisão anterior (v3)

O slide 4 apresenta BRL, EUR, JPY, GBP, CAD, SEK e o agregado nos seis horizontes. Períodos de origem, treinamento e avaliação no rodapé. Os demais slides permanecem visualmente idênticos à v2.

- `../output/presentation/apresentacao_macro_aula_v3_final.pptx`
- `../output/pdf/apresentacao_macro_aula_v3.pdf`
- `../output/pdf/guia_apresentacao_macro_v3.pdf`

Fontes: `content_v3.json`, `data_v3.json`, `build/deck_v3.mjs`, `build_pdfs_v3.py` e `qa_v3.py`. 718 verificações, incluindo as 42 células numéricas da tabela. Guia de 25 páginas, com explicação do slide 4 atualizada. Roteiro e contagem de slides preservados.

## Revisão anterior (v2)

17 slides principais, 19 minutos de roteiro e dois slides de apoio. O guia tem 25 páginas, com uma página para cada slide. Versão anterior preservada abaixo e em `archive_v1`.

- `../output/presentation/apresentacao_macro_aula_v2_final.pptx`: apresentação editável, com cinco gráficos e nove tabelas nativos e notas de fala.
- `../output/pdf/apresentacao_macro_aula_v2.pdf`: projeção, 19 páginas.
- `../output/pdf/guia_apresentacao_macro_v2.pdf`: guia atualizado, 25 páginas.
- `guia_slides_v2.md`: explicações editáveis, incluindo calendários de treinamento.

Alterações: slide 4 com seis horizontes, Brasil e resultado agregado; slide 6 com ranking, custos e calendário; novo slide 7 com patrimônio; slide 9 define origens; slides 12 e 14 detalham o treino da combinação; novo slide 13 compara lotes de 6, 12 e 24 meses. Conclusão no slide 17; apoio nos slides 18–19. Nenhum modelo foi reestimado para esta revisão: os testes de prazo já constavam na síntese.

Fontes e reprodução: `revise_v2.py`, `content_v2.json`, `data_v2.json`, `build/deck_v2.mjs`, `build_pdfs_v2.py` e `qa_v2.py`. O finalizador exige nomes novos de PPTX e recibo a cada revisão. Validação: `build/validation_v2_final.json`, `build/qa_v2/checks.json` (675 verificações aprovadas), inspeção das renderizações dos 19 slides e das 25 páginas do guia. A inspeção usa o importador/renderizador Artifact Tool; não foi realizada em PowerPoint nativo.

## Versão anterior (v1)

Entrega em português, com prioridade para clareza. 15 slides principais, roteiro de 18 minutos e dois slides de apoio para perguntas.

- `../output/presentation/apresentacao_macro_aula.pptx`: apresentação editável, com notas de fala e fontes por slide. Quatro gráficos e oito tabelas nativos, com dados dos gráficos incorporados.
- `../output/pdf/apresentacao_macro_aula.pdf`: cópia para projeção, com 17 páginas e marcadores. A apresentação principal termina no slide 15. Os slides 16 e 17 são apoio.
- `../output/pdf/guia_apresentacao_macro.pdf`: guia de 23 páginas. Inclui roteiro com tempo acumulado, uma página por slide, explicações, fala sugerida, perguntas, glossário e referências.
- `guia_slides.md`: texto editável das explicações por slide.

## Sequência econômica

1. Artigo e replicação brasileira.
2. Previsão fora da amostra e fracasso do ranking de carry com previsão.
3. Extensões com commodities e comércio, avaliando somente previsão.
4. Regras de exposição, resultado comum, trajetória e atribuição.
5. Limites de seleção, exposição e dados. Conclusão.

Os resultados vêm dos estudos já existentes. Esta entrega não reestima modelos ou escolhe novos parâmetros. As comparações usam as respectivas janelas identificadas nos slides. A referência acadêmica é Eichenbaum, Johannsen e Rebelo (2021). A replicação é parcial: relação preditiva e exemplo da aula, sem o DSGE completo.

## Fontes e edição

`prepare.py` lê as tabelas e grava `data.json`, com os valores e hashes dos insumos. `content.json` contém as explicações, tempos e falas. `build/deck.mjs` cria o PPTX com o Artifact Tool do runtime instalado. `build_pdfs.py` cria a cópia PDF e o guia com ReportLab. `qa.py` verifica correspondência, números principais, integridade dos insumos e limites das páginas, além de renderizar todos os PDFs para inspeção.

Python dos estudos: `tools/python/python.exe`. Python do runtime de documentos: `C:/Users/Pichau/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe`. Node do runtime: `C:/Users/Pichau/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe`.

Para reeditar o deck, execute `deck.mjs` com diretório de trabalho `presentation/build`, escolhendo novo nome de arquivo final e novo recibo no script. O finalizador preserva saídas existentes. As tabelas dos estudos originais devem continuar intactas. O PDF dos slides é uma renderização do PPTX. A edição dos gráficos e tabelas deve ser feita no PPTX ou no código gerador.

## Orientação para estudar

Comece pela primeira página do guia e pelos slides 2 e 5. Eles explicam o câmbio real e o carry. Depois ensaie o roteiro da página 2 usando o relógio acumulado. Os detalhes de equações e custos podem ficar para perguntas. Os tempos são metas de ensaio e deixam dois minutos de margem para o limite de 20.
