# Contrato técnico — RESULTADOS 2025

24/09/2026 · versão 4 · raw → trusted, sem filtro analítico. Acrescenta TP_DEPENDENCIA_ADM_ESC à versão 3, mantendo todos os 21 campos anteriores com tipos e valores idênticos por chave.

Uma linha representa um registro de RESULTADOS. A chave candidata `NU_SEQUENCIAL` deve ser não nula e única nesta edição; ela **não se relaciona a `NU_INSCRICAO`** de PARTICIPANTES. Manter todos os registros, incluindo ausentes e eliminados. Elegibilidade para análises será definida depois, por pergunta.

Fonte: `raw/microdados_enem_2025/microdados_enem_2025/DADOS/RESULTADOS_2025.csv`. Original imutável, separado por `;`, Latin-1. O DuckDB 1.5.5 lê essa codificação nativamente com `read_csv`, sem recodificar o original ou instalar extensão: [documentação oficial](https://duckdb.org/docs/current/data/csv/overview).

| Campos da saída (22 campos) | Tipo | Regra |
| --- | --- | --- |
| `NU_SEQUENCIAL` | VARCHAR | Identificador textual; preservar zeros à esquerda. Nulo/duplicado bloqueia publicação. |
| `NU_ANO` | INTEGER | Obrigatório e igual a 2025. |
| `TP_PRESENCA_CN`, `TP_PRESENCA_CH`, `TP_PRESENCA_LC`, `TP_PRESENCA_MT` | TINYINT | Códigos categóricos: 0 ausente, 1 presente, 2 eliminado. Nulos são mantidos e contados. Categoria inesperada bloqueia publicação. |
| `NU_NOTA_CN`, `NU_NOTA_CH`, `NU_NOTA_LC`, `NU_NOTA_MT` | DECIMAL(10,1) | Decimal com ponto e até uma casa, preservando a precisão desta edição; zero é valor, não ausência. Precisão diferente/overflow/texto inválido bloqueia, sem arredondamento. |
| `TP_STATUS_REDACAO` | TINYINT | 1, 2, 3, 4, 6, 7, 8 ou 9 conforme dicionário; nulo preservado. Categoria inesperada bloqueia. |
| `NU_NOTA_REDACAO`, `NU_NOTA_COMP1` a `NU_NOTA_COMP5` | DECIMAL(10,1) | Nota final e médias publicadas por competência. Na inspeção completa desta edição, todos os valores disponíveis são inteiros; tipo decimal preserva o padrão do projeto sem arredondamento. Zero e nulo distintos; mesma validação lexical estrita das notas objetivas. |
| `CO_MUNICIPIO_PROVA`, `NO_MUNICIPIO_PROVA`, `CO_UF_PROVA`, `SG_UF_PROVA` | VARCHAR | Código/nome de município e código/sigla de UF de aplicação. Códigos como texto; nulos, categorias desconhecidas e discordantes preservados e reportados, sem correção silenciosa. Dicionário RESULTADOS_2025, linhas 81, 86, 87 e 114. |
| `TP_DEPENDENCIA_ADM_ESC` | TINYINT | 1 Federal, 2 Estadual, 3 Municipal, 4 Privada. Nulo preservado; categoria inesperada bloqueia publicação. |

Espaços externos são removidos e vazios viram nulos; nenhum nulo vira zero. A leitura inicial usa texto explícito e parser estrito. Códigos e conversões são auditados antes dos casts. Erros estruturais interrompem a leitura: não ignorar linhas inválidas, deduplicar, imputar ou filtrar para passar validações.

## Validação e publicação

1. Amostra inicial de 10 mil registros para verificar o fluxo, sem inferência populacional e sem publicar trusted.
2. Base completa: contagem independente da leitura, contagem padronizada, nulos por campo, categorias inválidas, falhas de conversão, chave e ano. Contagens de entrada e saída devem ser iguais.
3. Reportar por área presente sem nota, ausente/eliminado com nota, presença nula com nota, zeros e notas negativas. Achados de coerência não são corrigidos nem excluídos automaticamente; ficam no relatório para decisão analítica posterior.
4. Gravar Parquet ZSTD temporário, reler, conferir esquema/contagens/validações e comparar exatamente os 22 valores por chave. Reportar nulos/status, zeros, escalas e soma de competências versus final sem corrigir os achados. Se existe trusted anterior, comparar exatamente todos os campos existentes no esquema anterior por chave, incluindo linhas inseridas/removidas; qualquer divergência bloqueia. Conferir SHA-256 do raw antes/depois. Só então substituir atomicamente `trusted/resultados_2025_base.parquet` no mesmo volume.

Nas migrações que ampliam v1, v2 ou v3, guardar cópia verificada do Parquet anterior em `work/rollback_resultados_<sha>.parquet`. Backups completos anteriores: `work/pre_redacao_2025/` (v1) e `work/pre_local_prova_2025/` (v2), incluindo Parquet, CSVs, relatórios e gráficos. A versão 3 e suas saídas foram preservadas em `work/pre_rede_escolar_2025/`. Backups anteriores não são sobrescritos. Para rollback, restaurar juntos esse Parquet e suas auditorias/CSVs; hashes impedem consumir relatórios de outra versão. Manter backup até revisão da POC. Não restaurar o raw, que nunca é modificado.

Leitores de desempenho/participação aceitam apenas os esquemas completos v1, v2, v3 ou v4, verificando todos os nomes, tipos e ordem. Redação exige v2 ou posterior; análise territorial exige v3 ou posterior; rede escolar exige v4. Não se aceita extensão parcial nem se ignora coluna inesperada. Após ampliação legítima, renovar auditorias dependentes e comparar resultados anteriores; mudança do hash físico não significa mudança dos campos legados.

Falhas de conversão/categoria, chave, ano, reconciliação ou mudança da fonte bloqueiam a publicação e preservam a saída anterior. Relatórios pequenos em `reports/validacao_resultados_2025_{amostra,completo}.json` registram sucesso ou falha da última tentativa. Verifique `publicado`, `erro` e hash antes de consumir uma saída preexistente. Reexecução substitui os mesmos artefatos; temporários de cada execução ficam em `work/` e são removidos ao encerrar normalmente.

## Execução e limites

Funções em `src/trusted_resultados.py`; acompanhamento em `notebooks/01_resultados_trusted.ipynb`. DuckDB processa em SQL com staging em disco: nenhuma leitura integral em Pandas. Padrão conservador de **256 MB, uma thread e até 10 GB de temporários**, diante de aproximadamente 8 GiB de RAM total. O limite DuckDB não limita toda a memória do processo; o relatório registra RAM/disco disponíveis antes/depois, não pico de uso. Medir novamente e ajustar explicitamente se necessário.

Filtros e denominadores estão nos contratos analíticos de desempenho, participação e redação; não pertencem à carga da trusted. Para novos anos, adaptar o esquema da edição ao modelo comum após verificar compatibilidade; nenhum outro ano ou framework genérico é implementado agora.


## Cobertura territorial da versão 3

A validação antes da publicação conta campos nulos, códigos/siglas UF desconhecidos, pares discordantes, formato municipal e prefixo UF, além de códigos municipais com nomes conflitantes. A referência oficial IBGE congelada em `uf_regiao_ibge.json` contém 27 UFs. Nenhum achado territorial exclui registros ou repara a fonte. Região é derivada somente na camada analítica para pares UF válidos; casos não classificáveis ficam em grupo explícito. Veja `contrato_analitico_local_prova_2025.md`.

## Cobertura escolar da versão 4

Apenas a dependência administrativa é acrescentada: CO_ESCOLA não é necessário. A carga conserva os 4.810.772 registros; o recorte com rede informada é feito na análise. Nulos são contados; códigos inesperados bloqueiam, sem imputação. Fonte e limites em `contrato_analitico_rede_escolar_2025.md`.
