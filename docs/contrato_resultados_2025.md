# Contrato técnico — RESULTADOS 2025

22/09/2026 · versão 2 · raw → trusted, sem filtro analítico. Amplia a versão 1 de 16/09/2026 com sete campos de redação; os dez campos anteriores mantêm tipos e valores.

Uma linha representa um registro de RESULTADOS. A chave candidata `NU_SEQUENCIAL` deve ser não nula e única nesta edição; ela **não se relaciona a `NU_INSCRICAO`** de PARTICIPANTES. Manter todos os registros, incluindo ausentes e eliminados. Elegibilidade para análises será definida depois, por pergunta.

Fonte: `raw/microdados_enem_2025/microdados_enem_2025/DADOS/RESULTADOS_2025.csv`. Original imutável, separado por `;`, Latin-1. O DuckDB 1.5.5 lê essa codificação nativamente com `read_csv`, sem recodificar o original ou instalar extensão: [documentação oficial](https://duckdb.org/docs/current/data/csv/overview).

| Campos da saída (17 campos) | Tipo | Regra |
| --- | --- | --- |
| `NU_SEQUENCIAL` | VARCHAR | Identificador textual; preservar zeros à esquerda. Nulo/duplicado bloqueia publicação. |
| `NU_ANO` | INTEGER | Obrigatório e igual a 2025. |
| `TP_PRESENCA_CN`, `TP_PRESENCA_CH`, `TP_PRESENCA_LC`, `TP_PRESENCA_MT` | TINYINT | Códigos categóricos: 0 ausente, 1 presente, 2 eliminado. Nulos são mantidos e contados. Categoria inesperada bloqueia publicação. |
| `NU_NOTA_CN`, `NU_NOTA_CH`, `NU_NOTA_LC`, `NU_NOTA_MT` | DECIMAL(10,1) | Decimal com ponto e até uma casa, preservando a precisão desta edição; zero é valor, não ausência. Precisão diferente/overflow/texto inválido bloqueia, sem arredondamento. |
| `TP_STATUS_REDACAO` | TINYINT | 1, 2, 3, 4, 6, 7, 8 ou 9 conforme dicionário; nulo preservado. Categoria inesperada bloqueia. |
| `NU_NOTA_REDACAO`, `NU_NOTA_COMP1` a `NU_NOTA_COMP5` | DECIMAL(10,1) | Nota final e médias publicadas por competência. Na inspeção completa desta edição, todos os valores disponíveis são inteiros; tipo decimal preserva o padrão do projeto sem arredondamento. Zero e nulo distintos; mesma validação lexical estrita das notas objetivas. |

Espaços externos são removidos e vazios viram nulos; nenhum nulo vira zero. A leitura inicial usa texto explícito e parser estrito. Códigos e conversões são auditados antes dos casts. Erros estruturais interrompem a leitura: não ignorar linhas inválidas, deduplicar, imputar ou filtrar para passar validações.

## Validação e publicação

1. Amostra inicial de 10 mil registros para verificar o fluxo, sem inferência populacional e sem publicar trusted.
2. Base completa: contagem independente da leitura, contagem padronizada, nulos por campo, categorias inválidas, falhas de conversão, chave e ano. Contagens de entrada e saída devem ser iguais.
3. Reportar por área presente sem nota, ausente/eliminado com nota, presença nula com nota, zeros e notas negativas. Achados de coerência não são corrigidos nem excluídos automaticamente; ficam no relatório para decisão analítica posterior.
4. Gravar Parquet ZSTD temporário, reler, conferir esquema/contagens/validações e comparar exatamente os 17 valores por chave. Reportar nulos/status, zeros, escalas e soma de competências versus final sem corrigir os achados. Se existe trusted anterior, comparar exatamente os dez campos legados por chave, incluindo linhas inseridas/removidas; qualquer divergência bloqueia. Conferir SHA-256 do raw antes/depois. Só então substituir atomicamente `trusted/resultados_2025_base.parquet` no mesmo volume.

Na migração v1→v2, guardar cópia verificada do Parquet anterior em `work/rollback_resultados_<sha>.parquet`. Nesta primeira execução, o backup completo anterior (Parquet, CSVs e relatórios) já foi salvo em `work/pre_redacao_2025/` antes da migração. Para rollback, restaurar juntos esse Parquet e suas auditorias/CSVs; hashes impedem consumir relatórios de outra versão. Manter backup até revisão da POC. Não restaurar o raw, que nunca é modificado.

Leitores de desempenho/participação aceitam apenas os esquemas completos v1 ou v2, verificando todos os nomes, tipos e ordem. Redação exige v2. Não se aceita extensão parcial nem se ignora coluna inesperada. Após ampliação legítima, renovar auditorias dependentes e comparar resultados anteriores; mudança do hash físico não significa mudança dos dez campos legados.

Falhas de conversão/categoria, chave, ano, reconciliação ou mudança da fonte bloqueiam a publicação e preservam a saída anterior. Relatórios pequenos em `reports/validacao_resultados_2025_{amostra,completo}.json` registram sucesso ou falha da última tentativa. Verifique `publicado`, `erro` e hash antes de consumir uma saída preexistente. Reexecução substitui os mesmos artefatos; temporários de cada execução ficam em `work/` e são removidos ao encerrar normalmente.

## Execução e limites

Funções em `src/trusted_resultados.py`; acompanhamento em `notebooks/01_resultados_trusted.ipynb`. DuckDB processa em SQL com staging em disco: nenhuma leitura integral em Pandas. Padrão conservador de **256 MB, uma thread e até 10 GB de temporários**, diante de aproximadamente 8 GiB de RAM total. O limite DuckDB não limita toda a memória do processo; o relatório registra RAM/disco disponíveis antes/depois, não pico de uso. Medir novamente e ajustar explicitamente se necessário.

Filtros e denominadores estão nos contratos analíticos de desempenho, participação e redação; não pertencem à carga da trusted. Para novos anos, adaptar o esquema da edição ao modelo comum após verificar compatibilidade; nenhum outro ano ou framework genérico é implementado agora.
