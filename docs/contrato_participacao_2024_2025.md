# Participação entre dias — 2024 e comparação com 2025

01/10/2026 · etapa 2.1. Escopo exclusivo: participação, transições e permanência. As demais cinco análises de 2024 não estão implementadas.

## Fonte e entrada mínima

Origem: `raw/microdados_enem_2024/microdados_enem_2024/DADOS/RESULTADOS_2024.csv`. O dicionário do mesmo pacote, aba `RESULTADOS_2024`, define identificador/edição em A6:B7 e presenças em linhas 38–49: 0=faltou, 1=presente, 2=eliminado. O LeiaMe, página 6, confirma LC/CH no primeiro dia e CN/MT no segundo. Caminhos documentais completos constam na auditoria temporal.

Saída mínima: `trusted/participacao_2024_base.parquet`, com `NU_SEQUENCIAL` textual, `NU_ANO` inteiro e quatro campos `TP_PRESENCA_{CN,CH,LC,MT}` inteiros. Identificador textual preserva zeros iniciais; chave única apenas dentro desta edição. Não há filtro de presença nem exclusão de linhas. A fonte 2025 continua sendo `trusted/resultados_2025_base.parquet`, sem alteração.

O leitor estrito existente é reutilizado com projeção de seis campos. CSV com ponto e vírgula e Latin-1, vazio convertido em nulo; campos selecionados são lidos como texto antes da conversão. Texto não inteiro ou fora da capacidade do tipo bloqueia publicação, sem arredondar nem transformar erro em nulo. Presenças nulas ou códigos inteiros fora de 0/1/2 permanecem no preparo e geram classificação explícita no cálculo. Chave nula/duplicada, edição incorreta, contagem divergente ou releitura diferente bloqueiam publicação. Raw conferido por SHA-256 antes/depois.

## Regras reutilizadas

Aplicam-se a classificação, a matriz de 36 situações e as medidas do [contrato de participação](contrato_analitico_participacao_2025.md). `src/participacao.py` permanece sem alterações: pares (1,1), (0,0), (2,2) indicam presente, ausente e eliminado; demais pares válidos são mistos; inválido prevalece sobre nulo. Nenhuma categoria é silenciosamente incorporada a outra.

Percentuais diários e por célula da matriz usam todos os registros publicados da edição. Retenção/permanência = presentes completos nos dois dias / presentes completos no primeiro. Percentual por origem usa o total do status do primeiro dia. Denominador zero produz percentual nulo. Presente→ausente é ausência estrita, diferente do saldo líquido entre os dias.

## Comparação por edição

Consolidam-se **indicadores**, sem tabela física conjunta de pessoas e sem JOIN individual entre anos. Dias, transições e resumo recebem `edicao`. A tabela de comparação explicita contagem, denominador e taxa de cada ano, diferença de contagens e diferença de taxas em pontos percentuais (**2025 menos 2024**). Não é média de percentuais, variação percentual relativa nem acompanhamento das mesmas pessoas.

Os indicadores de 2025 são lidos da validação existente, conferidos contra os hashes de seus CSVs e da fonte. A apresentação confere a correspondência entre agregados anuais, consolidados e diferenças. Os universos publicados podem mudar: os números são descritivos e não identificam causas para ausência ou mudanças entre edições.

## Execução e responsabilidades

1. `notebooks/08_participacao_2024.ipynb`: `participacao_entrada.py` prepara seis campos; `participacao_execucao.py` reutiliza cálculo/publicação com parâmetro `ano`; `participacao_comparacao.py` confere e consolida indicadores. DuckDB limitado a 256 MB e uma thread; dados individuais não são carregados em Pandas.
2. `apresentacao/participacao_2024_2025.ipynb`: lê agregados, organiza tabelas e usa `participacao_comparacao_graficos.py`; não lê raw nem reexecuta ETL.

Saídas: cinco CSVs `analitica/participacao_2024_*`; quatro CSVs `analitica/participacao_2024_2025_*`; uma validação `reports/validacao_participacao_2024.json`, incluindo preparo e controles; dois PNGs comparativos/2024. Não se regravam saídas de 2025. Publicações usam temporários por arquivo, não uma transação multiarquivo; hashes e conferências bloqueiam o uso de derivados inconsistentes.

## Verificação desta entrega

4.332.944 entradas = 4.332.944 saídas; seis campos sem nulos; chave sem duplicidade; edição correta; nenhum código de presença inválido, par misto ou divergência de releitura. Eliminações continuam separadas: 5.658 no dia 1 e 2.303 no dia 2. Os 32 controles de agregação, marginais, denominadores e recontagem direta dos pares passaram.

Treze testes focalizados passaram (11 existentes e dois novos), cobrindo o leitor compartilhado, a participação, conversão estrita/preservação da saída anterior e diferenças com denominadores distintos. Regressão somente leitura na trusted real de 2025 reproduziu exatamente os agregados anteriores. Os 64 artefatos preexistentes acompanhados por SHA-256 permaneceram idênticos. Ambos os notebooks foram executados em kernel novo e os PNGs inspecionados. Detalhes numéricos estão no [resumo da entrega](../apresentacao/RESUMO_PARTICIPACAO_2024_2025.md).
