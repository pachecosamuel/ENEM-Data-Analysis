# Rede escolar — entrega de 24/09/2026

Capítulo acrescentado após local de prova na apresentação, com a transição “Além do lugar de aplicação, o que muda quando observamos a rede da escola informada?”. A cobertura precede a comparação; um PNG mostra Q1–Q3, mediana e n nas quatro áreas. Duas tabelas CSV, notebook 06 e módulos de cálculo/I-O/gráfico separados.

## Cobertura e resultados

Base total: **4.810.772**. Rede válida: **1.739.028 (36,15%)**; sem informação: **3.071.744 (63,85%)**; inválidos: **0**. Federal 74.649, Estadual 1.382.565, Municipal 9.015, Privada 272.799. Federal é pública; nulos não são classificados nem imputados.

| Rede | n CN/MT | n CH/LC | Mediana CN | Mediana CH | Mediana LC | Mediana MT |
|---|---:|---:|---:|---:|---:|---:|
| Federal | 68.618 | 70.097 | 538,5 | 558,4 | 569,5 | 588,5 |
| Estadual | 964.885 | 1.018.248 | 472,7 | 482,6 | 516,2 | 462,3 |
| Municipal | 6.619 | 6.952 | 503,5 | 525,25 | 550,0 | 528,1 |
| Privada | 252.481 | 257.265 | 554,1 | 576,6 | 583,5 | 627,4 |

Filtro nacional reutilizado: presença=1 e nota disponível na própria área, mantendo zero. Quartis tipo 7, sem média de médias. Em Matemática, a faixa Q1–Q3 é 489,4–680,4 na Federal e 525,9–715,4 na Privada: os centros diferem, mas as distribuições se sobrepõem. Bases e seleção precisam acompanhar a leitura; não é medida de qualidade ou efeito causal.

## Integridade e verificação

Trusted v4 contém 22 campos: somente TP_DEPENDENCIA_ADM_ESC foi acrescentado. Todos os **21 campos anteriores** foram comparados exatamente por chave em toda a base, sem divergências, inclusões ou exclusões. Comparação integral candidato/releitura em 22 campos; hash do raw idêntico antes/depois. Backup v3 e manifesto em `work/pre_rede_escolar_2025/`; rollback por hash preservado.

**15 CSVs e oito PNGs anteriores idênticos byte a byte**. As células anteriores da apresentação foram preservadas, exceto setup para a nova auditoria e atualização da próxima pergunta no encerramento. Auditorias 02–05 renovadas contra o novo hash de trusted. Notebooks 01–06 e apresentação executados em kernels novos; nenhum erro final. Gráfico novo inspecionado: sem cortes/sobreposição de textos. `git diff --check` aprovado.

**34 testes aprovados: 31 anteriores e três novos.** Os novos cobrem nulos/inválidos, zeros/ausência, n/quartis manuais e proteção dos 21 campos. A tabela da apresentação foi ajustada para não exigir Jinja2; nenhuma dependência foi instalada. Nenhum commit/push.

## Limites e próximo passo

O Leia_Me descreve origem no Censo Escolar 2025, seleção de etapas de possíveis concluintes e critérios para múltiplas matrículas, incluindo preferência por rede pública. A cobertura de 36,15% não representa todos os participantes nem todos os estudantes de cada rede. Municipal tem base muito menor. Não houve análise por escola individual, redação por rede ou associação de rede com renda.

Próximo passo: **perfil de renda em PARTICIPANTES, independente de RESULTADOS**. Não há chave comum para renda × nota individual em 2025.

Artefatos: `notebooks/06_rede_escolar.ipynb`, `docs/contrato_analitico_rede_escolar_2025.md`, `reports/validacao_rede_escolar_2025.json`, `reports/validacao_migracao_rede_escolar_2025.json`, `analitica/rede_escolar_2025_{cobertura,desempenho}.csv` e `apresentacao/graficos/rede_escolar_notas_2025.png`.
