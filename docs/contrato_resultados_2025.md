# Contrato inicial — RESULTADOS 2025

16/09/2026 · versão 1 · raw → trusted, sem indicadores finais.

Uma linha representa um registro de RESULTADOS. A chave candidata `NU_SEQUENCIAL` deve ser não nula e única nesta edição; ela **não se relaciona a `NU_INSCRICAO`** de PARTICIPANTES. Manter todos os registros, incluindo ausentes e eliminados. Elegibilidade para análises será definida depois, por pergunta.

Fonte: `raw/microdados_enem_2025/microdados_enem_2025/DADOS/RESULTADOS_2025.csv`. Original imutável, separado por `;`, Latin-1. O DuckDB 1.5.5 lê essa codificação nativamente com `read_csv`, sem recodificar o original ou instalar extensão: [documentação oficial](https://duckdb.org/docs/current/data/csv/overview).

| Campos da saída (somente estes dez) | Tipo | Regra |
| --- | --- | --- |
| `NU_SEQUENCIAL` | VARCHAR | Identificador textual; preservar zeros à esquerda. Nulo/duplicado bloqueia publicação. |
| `NU_ANO` | INTEGER | Obrigatório e igual a 2025. |
| `TP_PRESENCA_CN`, `TP_PRESENCA_CH`, `TP_PRESENCA_LC`, `TP_PRESENCA_MT` | TINYINT | Códigos categóricos: 0 ausente, 1 presente, 2 eliminado. Nulos são mantidos e contados. Categoria inesperada bloqueia publicação. |
| `NU_NOTA_CN`, `NU_NOTA_CH`, `NU_NOTA_LC`, `NU_NOTA_MT` | DECIMAL(10,1) | Decimal com ponto e até uma casa, preservando a precisão desta edição; zero é valor, não ausência. Precisão diferente/overflow/texto inválido bloqueia, sem arredondamento. |

Espaços externos são removidos e vazios viram nulos; nenhum nulo vira zero. A leitura inicial usa texto explícito e parser estrito. Códigos e conversões são auditados antes dos casts. Erros estruturais interrompem a leitura: não ignorar linhas inválidas, deduplicar, imputar ou filtrar para passar validações.

## Validação e publicação

1. Amostra inicial de 10 mil registros para verificar o fluxo, sem inferência populacional e sem publicar trusted.
2. Base completa: contagem independente da leitura, contagem padronizada, nulos por campo, categorias inválidas, falhas de conversão, chave e ano. Contagens de entrada e saída devem ser iguais.
3. Reportar por área presente sem nota, ausente/eliminado com nota, presença nula com nota, zeros e notas negativas. Achados de coerência não são corrigidos nem excluídos automaticamente; ficam no relatório para decisão analítica posterior.
4. Gravar Parquet ZSTD temporário, reler, conferir esquema/contagens/validações e comparar exatamente todos os valores por chave. Conferir SHA-256 do raw antes/depois. Só então substituir atomicamente `trusted/resultados_2025_base.parquet` no mesmo volume.

Falhas de conversão/categoria, chave, ano, reconciliação ou mudança da fonte bloqueiam a publicação e preservam a saída anterior. Relatórios pequenos em `reports/validacao_resultados_2025_{amostra,completo}.json` registram sucesso ou falha da última tentativa. Verifique `publicado`, `erro` e hash antes de consumir uma saída preexistente. Reexecução substitui os mesmos artefatos; temporários de cada execução ficam em `work/` e são removidos ao encerrar normalmente.

## Execução e limites

Funções em `src/trusted_resultados.py`; acompanhamento em `src/01_resultados_trusted.ipynb`. DuckDB processa em SQL com staging em disco: nenhuma leitura integral em Pandas. Padrão conservador de **256 MB, uma thread e até 10 GB de temporários**, diante de aproximadamente 8 GiB de RAM total. O limite DuckDB não limita toda a memória do processo; o relatório registra RAM/disco disponíveis antes/depois, não pico de uso. Medir novamente e ajustar explicitamente se necessário.

Próximo incremento: definir filtros, denominadores e indicadores de presença/desempenho sobre esta trusted. Para novos anos, adaptar o esquema da edição ao modelo comum após verificar compatibilidade; nenhum outro ano ou framework genérico é implementado agora.
