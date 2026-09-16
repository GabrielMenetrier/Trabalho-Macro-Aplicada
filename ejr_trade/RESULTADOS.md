# EJR com termos de troca e cesta de commodities

Réplica da equação preditiva (3.4) na base do projeto. Sem carteiras ou alteração de slides.

RMSE relativo a nenhuma mudança. Abaixo de 1 melhora. Extensões com nível e mudança.

| Horizonte | EJR | + termos de troca | + cesta |
|---|---:|---:|---:|
| 1 anos | 1,039 | 1,119 | 1,048 |
| 2 anos | 1,076 | 1,229 | 1,086 |
| 3 anos | 1,096 | 1,236 | 1,109 |
| 4 anos | 1,084 | 1,185 | 1,098 |
| 5 anos | 1,037 | 1,092 | 1,060 |
| 6 anos | 1,048 | 1,075 | 1,088 |
| 7 anos | 1,072 | 1,115 | 1,161 |
| 8 anos | 1,115 | 1,188 | 1,247 |

As duas extensões perdem do EJR no agregado nos oito horizontes. Em cinco anos, termos de troca pioram o RMSE em 5,3%, e a cesta em 2,2%. Ganhos individuais: Brasil -2,3% com termos de troca; Canadá -1,2% com a cesta.

O teste principal de termos de troca usa deflatores de bens e serviços, construídos com contas nacionais WDI. A proxy usa diferenças de participações exportadas/importadas em quatro grupos de commodities, pesos 1994–1996. Índice de mercadorias UNCTAD/WDI testado separadamente por ter série curta.

Em cinco anos: treino no primeiro teste out/1999–dez/2004, alvos de treino até dez/2009; origens avaliadas jan/2010–ago/2021; alvos jan/2015–ago/2026. Termos anuais disponíveis Y−2 e preços/CPI t−2. Séries revisadas: pseudo fora da amostra, sem vintages completos.

O resultado antigo 0,890 foi reproduzido, mas requer fator global + exposição líquida específica antiga. Na janela recente resulta 1,630; sem Brasil, 1,147. Isso não demonstra que a cesta de termos de troca melhora de modo geral.

Relatório: ../output/pdf/relatorio_ejr_termos_troca.pdf

Código: run.py; diagnostics.py; validate_extra.py; figures.py; build_report.py. Dados e resultados em data/ e tables/. Todas as especificações testadas são salvas, inclusive as desfavoráveis.