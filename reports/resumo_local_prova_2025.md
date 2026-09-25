# Local de prova — primeira visão validada em 24/09/2026

Pergunta: como presença e desempenho variam entre os lugares de aplicação? A análise usa RESULTADOS 2025, sem join com PARTICIPANTES e sem dados de residência/escola.

## Cobertura e fonte

**4.810.772 registros** com UF/região classificada: 27 UFs, cinco regiões e 1.805 códigos municipais. Zero campos locais nulos, códigos/siglas UF desconhecidos, pares UF discordantes, formato municipal inválido, prefixo municipal discordante ou código municipal com múltiplos nomes. Isso não certifica existência em cadastro municipal histórico; nenhum ranking/desempenho municipal foi produzido.

Campos confirmados no dicionário RESULTADOS_2025, linhas 81, 86, 87 e 114: CO_MUNICIPIO_PROVA, NO_MUNICIPIO_PROVA, CO_UF_PROVA e SG_UF_PROVA. Mantidos como texto, com zeros à esquerda e nulos preservados. Região derivada na análise pelo par código+sigla válido; casos não classificáveis seriam mantidos em grupo explícito.

[Referência oficial IBGE](https://servicodados.ibge.gov.br/api/v1/localidades/estados?orderBy=id), obtida diretamente em 24/09/2026; mapeamento completo congelado em `docs/uf_regiao_ibge.json`, com hash registrado na auditoria. Local de aplicação não equivale a residência nem rede escolar.

## Presença e permanência

| Região de aplicação | Base local | Presentes dia 1 | Dia 1 (%) | Presentes dia 2 | Dia 2 (%) | Permanência (%) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Norte | 560.912 | 377.494 | 67,30 | 351.465 | 62,66 | 92,51 |
| Nordeste | 1.737.630 | 1.285.359 | 73,97 | 1.225.462 | 70,52 | 94,90 |
| Sudeste | 1.631.402 | 1.168.120 | 71,60 | 1.102.581 | 67,58 | 93,94 |
| Sul | 492.798 | 354.680 | 71,97 | 327.669 | 66,49 | 92,02 |
| Centro-Oeste | 388.030 | 271.902 | 70,07 | 253.159 | 65,24 | 92,57 |

Taxa por dia = presentes completos / base local. Permanência = presentes completos nos dois dias / presentes completos no primeiro. Nordeste: 1.219.792 / 1.285.359 = 94,90%; Sul: 326.365 / 354.680 = 92,02%. Não inferir motivos de ausência. Pares LC/CH e CN/MT reutilizam a regra nacional; eliminações, mistos, nulos e inválidos permanecem separados nas tabelas.

**Top 3 UFs pela taxa de presença completa no dia 2**, sem arredondar para ordenar, desempate por sigla crescente:

| Grupo | UF | Presentes dia 2 | Base da UF | Taxa (%) |
| --- | --- | ---: | ---: | ---: |
| Maiores taxas | CE | 207.949 | 275.902 | 75,37 |
| Maiores taxas | SE | 57.044 | 78.341 | 72,82 |
| Maiores taxas | RN | 82.099 | 113.208 | 72,52 |
| Menores taxas | AM | 60.052 | 110.831 | 54,18 |
| Menores taxas | RR | 8.261 | 14.158 | 58,35 |
| Menores taxas | MT | 47.584 | 80.396 | 59,19 |

Trata-se de taxa, não volume. Não fizemos top 3 entre apenas cinco regiões nem ranking municipal.

## Notas por área e território

Presença=1 e nota disponível na própria área, incluindo zero. Médias e quantis calculados diretamente dos registros, sem médias não ponderadas de UFs ou medianas de medianas. Populações por área distintas, com n e cobertura exportados.

| Região | Mediana CN | Mediana CH | Mediana LC | Mediana MT |
| --- | ---: | ---: | ---: | ---: |
| Norte | 473,60 | 482,40 | 508,70 | 446,20 |
| Nordeste | 488,10 | 492,00 | 524,50 | 472,50 |
| Sudeste | 512,90 | 536,50 | 556,80 | 541,40 |
| Sul | 511,80 | 534,80 | 554,60 | 537,30 |
| Centro-Oeste | 502,70 | 517,10 | 541,20 | 504,20 |

As medianas do Sudeste foram as maiores nesta base nas quatro áreas. Em Matemática, Q1–Q3 do Sudeste (447,4–644,7) e do Norte (389,0–530,6) se sobrepõem parcialmente. Os contrastes descrevem a população elegível; não demonstram qualidade, renda ou efeito causal territorial. Médias, quartis e n para todas as regiões/UFs estão no CSV, sem criar nota global.

## Integridade e validação

- Trusted v3: **21 campos, 4.810.772 linhas, 91.755.509 bytes**. Todos os **17 campos anteriores** comparados exatamente por chave antes da troca e novamente contra o backup: **zero divergências**. Raw RESULTADOS e PARTICIPANTES mantêm seus hashes.
- SHA-256 trusted atual: `0732b7821e08e23601c7c9f309a7b9e088ad66fdd5c3e3fa5b3da744eb66a240`. Auditorias nacionais renovadas e coerentes com esse hash. **11 CSVs e seis PNGs anteriores byte a byte iguais**; narrativa anterior preservada.
- Backup completo v2: `work/pre_local_prova_2025/`. Backup Parquet automático: `work/rollback_resultados_c63608b2a3019d31430454e4c325d6f1fcf623eb4fe79ab8ad2f977521978c2d.parquet`. Backups de incrementos anteriores mantidos. Em rollback, restaurar conjuntamente Parquet e auditorias/CSVs correspondentes.
- Soma das UFs/regiões reconcilia totais nacionais, status/transições, n elegível, zeros e somas de notas; UFs também reconciliam dentro das regiões. Estatísticas nacionais territoriais coincidem com as já aprovadas.
- **31 testes passaram**, incluindo 27 UFs, casos ausentes/desconhecidos/discordantes, pesos desbalanceados, quantis diretos, zeros, área com nota ausente, status de presença, empate e denominador zero, exportação e bloqueio de mudança em campo legado de redação.
- Notebooks **01–05 e apresentação** executados em kernels novos, sem saídas de erro. Dois PNGs inspecionados. `git diff --check` aprovado. Sem dependências novas, commit ou push. DuckDB 256 MB/uma thread; limite não representa pico total do processo.

## Artefatos e limites do incremento

`notebooks/05_local_prova.ipynb`; contrato em `docs/contrato_analitico_local_prova_2025.md`; cálculo/I-O/figuras em `src/local_prova*.py`. Quatro CSVs `analitica/local_prova_2025_*`: participação (33 linhas), desempenho (132), transições (1.188) e top 3 UFs (6). Auditorias `validacao_local_prova_2025.json` e `validacao_migracao_local_prova_2025.json`.

Apresentação `apresentacao/visao_geral_2025.ipynb`, com dois PNGs novos: `local_prova_presenca_regioes_2025.png` e `local_prova_notas_regioes_2025.png`. Apresentação lê agregados/auditorias e verifica hashes, sem executar pipelines. Cópias externas preservam outputs, mas dependem do projeto para execução.

Granularidade inicial: regiões e UFs. Desempenho municipal, redação por local, rede escolar, perfil econômico e outros anos **não foram implementados**; ficam para próximos incrementos após revisão.
