# Participação entre dias — ENEM 2025

18/09/2026 · segunda pergunta concluída.

A base tem **4.810.772 registros divulgados**. Presença completa significa presença nas duas áreas do dia: LC/CH no primeiro, CN/MT no segundo. Não generalizamos a todos os inscritos do país nem inferimos motivos de ausência.

## De um dia para o outro

| Situação | 1º dia | 2º dia |
| --- | ---: | ---: |
| Presença completa | 3.457.555 (71,87%) | 3.260.336 (67,77%) |
| Ausência completa | 1.348.087 (28,02%) | 1.548.487 (32,19%) |
| Eliminação completa | 5.130 (0,11%) | 1.949 (0,04%) |
| Situação mista | 0 (0%) | 0 (0%) |
| Dados ausentes | 0 (0%) | 0 (0%) |
| Código inválido | 0 (0%) | 0 (0%) |

Percentuais acima usam o total da base. **Retenção: 3.244.348 / 3.457.555 = 93,83%**, com presentes completos do primeiro dia no denominador.

## Todas as transições observadas

| 1º dia | 2º dia | Registros | % da base |
| --- | --- | ---: | ---: |
| Presença completa | Presença completa | 3.244.348 | 67,44% |
| Presença completa | Ausência completa | 211.292 | 4,39% |
| Presença completa | Eliminação completa | 1.915 | 0,04% |
| Ausência completa | Presença completa | 15.146 | 0,31% |
| Ausência completa | Ausência completa | 1.332.913 | 27,71% |
| Ausência completa | Eliminação completa | 28 | <0,01% |
| Eliminação completa | Presença completa | 842 | 0,02% |
| Eliminação completa | Ausência completa | 4.282 | 0,09% |
| Eliminação completa | Eliminação completa | 6 | <0,01% |

A matriz completa exportada inclui também os zeros. Percentual `<0,01%` é positivo; `0%` representa zero registros. Os valores apresentados são arredondados; CSV/JSON mantêm precisão.

A presença completa nos dois dias soma 3.244.348 registros. Presença no primeiro e ausência no segundo: 211.292; ausência no primeiro e presença no segundo: 15.146; ausência completa nos dois: 1.332.913. As demais situações somam **7.073**, todas detalhadas acima (envolvem eliminação nesta base).

A diferença líquida de **−197.219** não é a contagem de quem passou de presente a ausente. A identidade é **(15.146 + 842) − (211.292 + 1.915) = −197.219**. Há 213.207 presentes completos do primeiro sem presença completa no segundo; esse grupo inclui 211.292 ausentes e 1.915 eliminados no segundo. Eliminação não foi chamada de falta.

## Conferência dos pares

| Código A/B | LC/CH (dia 1) | CN/MT (dia 2) |
| --- | ---: | ---: |
| 0/0 | 1.348.087 | 1.548.487 |
| 0/1 | 0 | 0 |
| 0/2 | 0 | 0 |
| 1/0 | 0 | 0 |
| 1/1 | 3.457.555 | 3.260.336 |
| 1/2 | 0 | 0 |
| 2/0 | 0 | 0 |
| 2/1 | 0 | 0 |
| 2/2 | 5.130 | 1.949 |

Nenhum par misto, nulo ou código inesperado foi encontrado em qualquer dia. Isso foi verificado por agrupamento completo e recontagem direta, não presumido. O código preserva e sinaliza essas situações se aparecerem em uma execução futura. Os testes artificiais cobrem essas possibilidades.

## Evidências e reprodução

- [Contrato](../docs/contrato_analitico_participacao_2025.md), [notebook 03](../notebooks/03_participacao_entre_dias.ipynb), [apresentação executada](../apresentacao/visao_geral_2025.ipynb).
- [Auditoria JSON](validacao_participacao_2025.json): esquema, ano, chave, hashes da trusted, filtros via contrato, totais, marginais, pares, matriz, percentuais e reconciliação da diferença líquida. Zero chaves nulas/duplicadas e anos inválidos.
- Cinco CSV compactos em `analitica/participacao_2025_*.csv`: dias, pares, transições, combinações conjuntas e resumo. Os hashes estão na auditoria. Nenhuma cópia da base individual foi criada.
- PNG separados: [por dia](../apresentacao/graficos/participacao_por_dia_2025.png) e [transições](../apresentacao/graficos/transicoes_entre_dias_2025.png). Inspecionados visualmente; texto e contagens não dependem apenas de cores.
- Dezesseis testes passaram: onze anteriores e cinco novos. Novos testes cobrem todas as 36 transições, mistos/nulos/inválidos, denominador zero, ordem invariável, retenção versus saldo, exportação/alertas e bloqueio de chave duplicada preservando saída anterior.
- Notebook 03 e apresentação executados em kernels novos. Primeira história preservada; trusted com hash igual antes/depois. DuckDB com 256 MB/uma thread; apenas agregados no Pandas. Nenhum raw ETL, instalação, commit ou push.

## O próximo passo

Preparar o contrato e a ampliação da trusted para local de aplicação/região, com denominadores e cobertura explícitos. Local de prova não é residência. Rede escolar, redação e perfil econômico continuam pendentes. Renda permanece independente das notas em 2025. Os códigos de presença não explicam horários, sessões, causas ou evasão causal.
