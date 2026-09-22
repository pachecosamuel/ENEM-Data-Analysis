# Participação entre dias — contrato analítico

18/09/2026 · segunda pergunta da POC: como a participação muda entre os dois dias?

Fonte: `trusted/resultados_2025_base.parquet`. Unidade: registro único de RESULTADOS 2025, identificado por `NU_SEQUENCIAL`. Universo: todos os registros divulgados nesta base, não uma afirmação sobre todos os inscritos do país. Não lemos raw, não alteramos trusted e não usamos notas para inferir presença. Os códigos descrevem as áreas; não informam horários, sessões ou causas de ausência.

## Classificação por dia

Primeiro dia: par **LC/CH**. Segundo: **CN/MT**. Cada código vale 0 ausente, 1 presente, 2 eliminado, conforme o contrato técnico e o dicionário usados na primeira etapa. Classificar os pares sem presumir igualdade:

| Par | Status no cálculo | Leitura |
| --- | --- | --- |
| (1,1) | presente | Presença nas duas áreas do dia (presença completa). |
| (0,0) | ausente | Ausência nas duas áreas (ausência completa). |
| (2,2) | eliminado | Eliminação nas duas áreas; não é ausência. |
| Demais pares de 0/1/2 | misto | Situações diferentes nas duas áreas, sem reduzir a presente/ausente. |
| Um ou dois nulos, sem inválido | dados_ausentes | Não é possível classificar integralmente o dia. |
| Algum código fora de 0/1/2 | codigo_invalido | Sinalizar; prevalece sobre nulo, se coexistirem. |

Os códigos originais ficam no detalhamento, inclusive se houver nulo junto com inválido. Exportar as nove combinações válidas de cada dia, mesmo com contagem zero, e todas as combinações adicionais observadas. Exportar também as combinações conjuntas LC/CH/CN/MT, sem corrigir, eliminar ou juntar divergências silenciosamente. Mistos, nulos e inválidos geram alertas; permanecem na base dos percentuais. A matriz completa tem 36 células (seis status × seis status), incluindo zeros.

## Medidas e denominadores

- Contagem e percentual por status/dia e por célula da matriz: **total da base** no denominador.
- Percentual de transição dentro da origem: total do status do primeiro dia no denominador; coluna explícita `denominador_origem`.
- Presença completa nos dois dias: presente → presente.
- Presença só no primeiro e ausência no segundo: **presente → ausente**, estritamente (1,1) → (0,0). O inverso define presença só no segundo e ausência no primeiro. Eliminações, mistos e dados incompletos não entram nessas duas categorias.
- Ausência completa nos dois: ausente → ausente. Demais situações: complemento dos quatro grupos acima, mantido com detalhes na matriz.
- Retenção: presentes completos nos dois dias / presentes completos no primeiro × 100. Não requer nota disponível.
- Diferença líquida: total presente no segundo menos total presente no primeiro. Reconcilia com entradas em presença completa (origem não presente → presente) menos saídas da presença completa (presente → destino não presente). **Não é o número de pessoas que faltou após participar do primeiro.** As saídas incluem eliminações e outras situações; ausência estrita é uma célula específica.
- Denominador zero produz percentual nulo. CSV/JSON mantêm precisão. Na apresentação, arredondar a duas casas; percentual positivo menor que 0,01% aparece como `<0,01%`, e zero real como `0%`. Contagens exatas sempre acompanham a matriz.

## Validação e implementação

DuckDB consulta a trusted com 256 MB e uma thread; somente combinações e tabelas pequenas saem para Python/Pandas. Reutilizar localização do projeto/hash de `desempenho_execucao`, esquema `TIPOS` do contrato técnico e função de percentual existente. `participacao.py` classifica/calcula/reconcilia; `participacao_execucao.py` trata leitura e gravação; `participacao_graficos.py` apresenta agregados.

Conferir esquema, ano 2025, chave não nula/não vazia e sem duplicidade, total da fonte, total por dia, pares, matriz, marginais, grupos-resumo, percentuais e identidade da diferença líquida. Recontar pares diretamente no SQL. Confirmar hash da fonte antes/depois. Testes artificiais cobrem as 36 transições de status, eliminação, pares mistos/nulos/inválidos, prioridade inválido+nulo, retenção, denominador zero e invariância à ordem. Não são inferências sobre casos ausentes na base real.

Saídas: cinco CSV `analitica/participacao_2025_{dias,pares,transicoes,combinacoes_conjuntas,resumo}.csv`, auditoria `reports/validacao_participacao_2025.json`, resumo em PT-BR e PNGs em `apresentacao/graficos/`. Publicar derivados após validação, via temporários; cada arquivo é substituído individualmente (não há transação multiarquivo). Hashes dos CSV no relatório verificam correspondência. Uma falha anterior à publicação preserva os derivados anteriores. Notebook 03 acompanha o cálculo; a apresentação mantém a primeira pergunta e acrescenta a segunda.
