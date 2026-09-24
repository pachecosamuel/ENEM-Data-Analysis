# Inscritos e primeira POC de redação — 22/09/2026

Implementado para revisão, sem avançar para região, rede, renda ou avaliações individuais.

## Inscritos e universos

- **4.811.338 inscrições confirmadas:** tabela do [balanço do Inep de 09/11/2025](https://download.inep.gov.br/enem/outros_documentos/enem_balanco_da_aplicacao_09_11_2025.pdf). A tabela foi recuperada pelo índice de busca em 22/09/2026; abertura/download direto falhou. O [texto oficial de 11/08/2025](https://www.gov.br/mulheres/pt-br/central-de-conteudos/noticias/2025/agosto/mulheres-lideram-inscricoes-no-enem-2025-e-somam-60-dos-participantes), com informações do MEC, corrobora explicitamente o total confirmado. Não usamos os percentuais preliminares de presença do balanço.
- **4.810.772 registros em PARTICIPANTES:** DuckDB, parser estrito Latin-1 e `;`, uma thread/256 MB, chave não nula/única e ano 2025. Nenhuma linha ignorada. Hash original preservado.
- **4.810.772 registros em RESULTADOS:** denominador das análises anteriores preservado. Mesma contagem não significa equivalência individual entre bases; nenhum join foi feito.
- **Diferença de 566** para o total oficial, sem causa estabelecida. Fonte, data, limitações e contagens em `validacao_inscritos_2025.json`.

## Resultados de redação

Nota final registrada, sem filtro de status/presença: **n=3.457.555**, incluindo **211.859 zeros**. Sem nota: **1.353.217**. Média **580,8038**, mediana **600**, Q1 **480**, Q3 **720**, mínimo/máximo observados **0/1000**. As estatísticas descritivas não tratam a escala de redação como equivalente à TRI.

| Situação | Registros |
| --- | ---: |
| Sem problemas | 3.245.696 |
| Anulada | 3.070 |
| Cópia Texto Motivador | 54.840 |
| Em Branco | 114.329 |
| Fuga ao tema | 13.576 |
| Não atendimento ao tipo textual | 5.661 |
| Texto insuficiente | 16.975 |
| Parte desconectada | 3.408 |
| Sem status registrado | 1.353.217 |

Status usa **toda a base: 4.810.772**. Nesta base, as situações problemáticas totalizam as 211.859 notas zero; nulos de status coincidem com nulos de nota. Não converter “Em Branco” ou falta de nota em ausência na prova. A conferência LC/CH mostra 1.348.087 ausentes e 5.130 eliminados entre os sem nota, sem usar essa concordância como filtro universal de redação.

Competências: **n comum=3.245.696**, status Sem problemas + final e cinco competências completas. Exclui situações problemáticas e sem status; nenhuma exclusão adicional por incompletude dentro de Sem problemas. Zeros de competência mantidos.

| Competência | Média | Mediana | Q1 | Q3 | Zeros |
| --- | ---: | ---: | ---: | ---: | ---: |
| C1 · Escrita formal | 120,62 | 120 | 100 | 140 | 589 |
| C2 · Tema e tipo textual | 136,97 | 120 | 120 | 160 | 0 |
| C3 · Defesa de ponto de vista | 119,63 | 120 | 100 | 140 | 1.072 |
| C4 · Mecanismos da argumentação | 127,35 | 120 | 100 | 160 | 1.199 |
| C5 · Proposta de intervenção | 114,15 | 120 | 80 | 160 | 305.510 |

Esses contrastes descrevem o recorte, sem diagnóstico causal. Soma das cinco competências igual à nota final nos **3.457.555 registros comparáveis**; nenhuma divergência ou nota fora de escala. Não reconstruímos notas por avaliador.

## Integridade, execução e arquivos

- Trusted v2 compartilhada, 17 campos e **4.810.772 linhas**, 69.145.333 bytes. Os dez campos legados foram comparados exatamente por chave, antes da publicação e novamente contra o backup: **zero divergências**. Raw RESULTADOS e PARTICIPANTES com hashes preservados.
- SHA-256 novo da trusted: `c63608b2a3019d31430454e4c325d6f1fcf623eb4fe79ab8ad2f977521978c2d`. Auditorias dependentes renovadas e coerentes; **seis CSVs anteriores e quatro PNGs anteriores byte a byte idênticos**. Mudança de hash deriva da ampliação do esquema.
- Backup pré-migração em `work/pre_redacao_2025/`; contém trusted anterior, agregados e auditorias para rollback conjunto. A migração em código também produz backup verificado quando encontra v1. `validacao_migracao_redacao_2025.json` registra a evidência compacta.
- **25 testes aprovados:** regressão anterior, zero/nulo/status, denominadores, competências incompletas, soma divergente sem correção, categorias/precisão inválidas, parser estrito, migração/rollback e bloqueio de mudança legada.
- Notebooks **01, 02, 03, 04 e apresentação executados em kernels novos**, sem saídas de erro. Dois PNGs novos inspecionados. `git diff --check` aprovado. Sem dependências novas e sem commit/push.

Código novo: `src/inscritos_execucao.py`, `src/redacao.py`, `src/redacao_execucao.py`, `src/redacao_graficos.py`. Contratos em `docs/`. Processamento em `notebooks/04_redacao.ipynb`. Cinco CSVs de redação em `analitica/` (final, status, competências, distribuição, presenças); auditoria em `validacao_redacao_2025.json`. A apresentação confere hashes e lê agregados, sem executar pipelines.

Revisão visual: `apresentacao/visao_geral_2025.ipynb`, `apresentacao/graficos/redacao_distribuicao_2025.png` e `apresentacao/graficos/redacao_competencias_2025.png`. Cópias externas preservam outputs, mas a execução do notebook depende deste projeto e do kernel ENEM 2025 (.venv).
