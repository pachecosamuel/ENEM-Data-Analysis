# Desempenho por área — resultados e validação

17/09/2026 · POC 2025 · fonte: trusted local, sem alterações.

| Área | Elegíveis | Média | Q1 | Mediana | Q3 |
| --- | ---: | ---: | ---: | ---: | ---: |
| CN | 3.260.336 | 499,97 | 443,5 | 498,2 | 550,9 |
| CH | 3.457.555 | 511,19 | 446,6 | 513,0 | 574,0 |
| LC | 3.457.555 | 532,12 | 490,3 | 538,8 | 581,6 |
| MT | 3.260.336 | 519,98 | 416,5 | 500,0 | 606,8 |

Elegíveis são presentes com nota na própria área, incluindo zero. CN/MT têm 197.219 registros elegíveis a menos que CH/LC. Todos os presentes têm nota nesta base (completude dos presentes = 100% nas quatro áreas); isso não significa completude de 100% entre todos os registros. Presença sobre 4.810.772 registros: CN/MT 67,77%; CH/LC 71,87%.

Os 50% centrais de CN vão de 443,5 a 550,9; em CH, de 446,6 a 574,0; em LC, de 490,3 a 581,6; em MT, de 416,5 a 606,8. Média e mediana de MT diferem em aproximadamente 19,98 pontos. Estas descrições não estabelecem dificuldade relativa, causalidade ou nota global; quartis não descrevem caudas ou toda a forma da distribuição. As populações por área diferem.

## Evidências de validação

- [Auditoria reproduzível](validacao_desempenho_2025.json): fonte/hash/esquema, filtros, contagens, quantis contínuos tipo 7 e reconciliações aprovadas; o hash do CSV também está registrado.
- [Testes](../tests/test_desempenho.py): quatro testes novos passaram (fixture manual e inversão de ordem, interpolação fracionária, vazio/sem elegíveis e categoria inválida). Fixture cobre zero, ausência, eliminação, nulos, populações por área diferentes, caso unitário e nota acima de 1000. Os seis testes anteriores também passaram: dez no total.
- Notebook executado integralmente em kernel novo; os dois gráficos foram inspecionados visualmente. O preparo dos caminhos também foi verificado na raiz do projeto.
- Nenhum presente sem nota, nenhuma nota fora dos presentes ou categoria inválida. Zeros elegíveis mantidos: CN 775, CH 9.087, LC 2.361, MT 893.
- DuckDB: 256 MB, uma thread; somente quatro agregados chegam ao Pandas. Tempo observado de cálculo/gravação: 2.908 s; não é benchmark. Memória disponível antes/depois consta na auditoria, sem medição do pico.
- Não reprocessamos raw; trusted preservada por hash. Escala original DECIMAL(10,1) mantida; DOUBLE é usado apenas nos agregados para permitir interpolação fracionária.

## Artefatos

- [Tabela completa de quatro linhas](../analitica/desempenho_2025.csv), com denominadores, completude e auditoria.
- [Notebook executado](../src/02_desempenho_por_area.ipynb).
- [Participação por área](graficos/participacao_por_area_2025.png).
- [Intervalo interquartil e mediana](graficos/quartis_por_area_2025.png).

Próximo passo: participação entre os dois dias, definindo regras próprias para combinações de presença. Local de prova, rede escolar, redação, perfil econômico e expansão temporal continuam pendentes.
