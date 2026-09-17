# Desempenho por área — contrato analítico

17/09/2026 · versão 1 · pergunta: como se distribui o desempenho por área?

Fonte única: `trusted/resultados_2025_base.parquet`, dez campos já validados. Unidade: registro identificado por `NU_SEQUENCIAL`, ano 2025. O processamento não modifica a trusted, não reabre raw e não associa PARTICIPANTES. A auditoria registra hash antes/depois e esquema. As notas DECIMAL(10,1) são lidas em sua escala original: não dividir por dez para compensar exibição de extensões.

## População e denominadores

Para cada área CN, CH, LC e MT, incluir **presença = 1 e nota não nula naquela área**. Não exigir presença ou nota nas outras áreas. Zero é nota válida. Notas nulas não são imputadas. A contagem elegível é o denominador da média e define a população dos quantis.

- Presença: 0 ausente, 1 presente, 2 eliminado. Contar cada categoria, nulos e inválidos sobre o total da trusted, antes do filtro. Categorias inválidas bloqueiam a análise.
- Percentuais de presença, ausência, eliminação, presença nula e elegibilidade: contagem correspondente / total da base × 100.
- Completude da base: notas não nulas / total da base × 100, independentemente da presença. Completude dos presentes: elegíveis / presentes × 100. São denominadores diferentes, explicitados nos nomes das colunas.
- Auditar presentes sem nota, notas fora dos presentes, notas nulas e zeros elegíveis. Reconciliar categorias = total; presentes = elegíveis + presentes sem nota; notas disponíveis = elegíveis + notas fora dos presentes.
- Denominador zero produz percentual nulo, não zero. Sem elegíveis, média e quantis são nulos; com um elegível, os três quantis coincidem com a nota.

## Medidas e interpretação

Média aritmética e mediana são complementares. Q1 e Q3 descrevem os 50% centrais junto à mediana. Usar [`quantile_cont` exato do DuckDB](https://duckdb.org/docs/current/sql/functions/aggregates#quantile_contx-pos), com interpolação linear (tipo 7): para n notas ordenadas e probabilidade p, posição zero-based h=(n−1)p; interpolar entre floor(h) e ceil(h). p=0,25/0,50/0,75. Os agregados operam em DOUBLE para não truncar quantis interpolados à escala decimal de uma casa; conservar precisão no CSV e arredondar apenas na apresentação.

Moda é omitida neste incremento: o foco é localização e dispersão por medidas robustas/complementares, sem depender da frequência de valores individuais arredondados. Não há nota global, ranking de dificuldade entre áreas, inferência causal ou limite artificial de 0–1000 para notas TRI. Populações por área podem diferir. Q1–Q3 não descreve caudas, extremos ou toda a forma da distribuição.

## Implementação e validação

`src/desempenho.py`: definições/cálculo/reconciliação; `src/desempenho_execucao.py`: fonte, recursos e saídas; `src/desempenho_graficos.py`: gráficos dos agregados. Sem classes ou interfaces adicionais. DuckDB limitado a 256 MB e uma thread; processa uma área por vez. Pandas recebe quatro linhas. O limite DuckDB não é teto de RAM de todo o processo.

Validar esquema, ano, categorias, contagem elegível em consulta separada, identidades de completude e Q1 ≤ mediana ≤ Q3. Testes manuais incluem zero, ausente, eliminado, nulo, populações distintas, interpolação fracionária, ordem invertida, conjunto vazio, caso unitário e nota acima de 1000. Esta etapa confia na granularidade/chave já validada na trusted; não refaz a carga.

Saídas: `analitica/desempenho_2025.csv` (quatro linhas), `reports/validacao_desempenho_2025.json` e dois PNG em `reports/graficos/`: participação e intervalo Q1–Q3 com mediana. O segundo não é boxplot completo (sem bigodes/extremos). O notebook `src/02_desempenho_por_area.ipynb` executa tudo em kernel novo. Reexecuções substituem apenas esses derivados compactos. CSV e auditoria são publicados após validação; o hash do CSV no relatório permite verificar correspondência (substituições individuais, não transação multiarquivo).
