# Contrato analítico — primeira POC de redação 2025

22/09/2026. Unidade: registro divulgado de RESULTADOS. Fonte: trusted v2 ou v3, sem exclusão na preparação.

## Fontes e significado

Dicionário local `raw/microdados_enem_2025/microdados_enem_2025/DICIONÁRIO/Dicionário_Microdados_Enem_2025.xlsx`, aba RESULTADOS_2025, linhas 243–256. Status: 1 Sem problemas; 2 Anulada; 3 Cópia Texto Motivador; 4 Em Branco; 6 Fuga ao tema; 7 Não atendimento ao tipo textual; 8 Texto insuficiente; 9 Parte desconectada. Nulo é **sem status registrado**, não um código de ausência. Código inesperado bloqueia o cálculo.

As cinco competências são notas médias dos avaliadores considerados válidos pelo edital; a nota final é fornecida pelo Inep. A cartilha local `LEIA-ME E DOCUMENTOS TÉCNICOS/A_Redacao_no_ENEM_2025_Cartilha_do_Participante.pdf`, páginas impressas 6–8 (PDF 8–10), explica pontuação, médias e situações de zero. Cada competência usa 0–200; a redação, 0–1000. Não reconstruímos avaliações individuais. O leia-me, abril/2026, seção 3, e a nota 1 do dicionário de RESULTADOS vedam vincular NU_SEQUENCIAL a NU_INSCRICAO de PARTICIPANTES.

## Três recortes diferentes

| Visão | Filtro / denominador | Tratamento |
| --- | --- | --- |
| Nota final | NU_NOTA_REDACAO não nula; n de notas registradas | Inclui zero, todos os status, inclusive problemáticos ou nulos. Não exige presença de LC/CH. Ausência de nota não vira zero. |
| Situação da redação | Todos os registros de RESULTADOS | Quantidade e percentual da base; contagens de notas registradas, nulas, zero e positivas por status. “Em Branco” é situação da redação, distinta de nota nula. |
| Cinco competências | Status=1, nota final e cinco competências não nulas | Denominador comum às cinco competências; inclui zeros. Exclui status problemáticos porque zeros por invalidação não descrevem separadamente as habilidades. Exibe n e exclusões; não representa todas as notas finais. |

Final e competências: n, zeros, média, mediana, Q1, Q3, mínimo e máximo observados. Quantis contínuos tipo 7 sobre DOUBLE, mesma convenção das áreas. Distribuição final exportada por nota exata; gráfico em faixas [0,100), …, [900,1000], preservando zero e máximo.

## Controles

- Fonte sem mutação (SHA-256 antes/depois), esquema v2 ou v3 completo e exato, chave única/não nula e ano 2025.
- Nulos e categorias; cobertura de final e competências; soma dos status, notas, zeros e distribuição reconciliada. Mesmo denominador nas cinco competências.
- Comparar soma das cinco notas publicadas à final quando todas existem, separando o recorte status=1; comparação decimal exata, sem imputar nem ajustar. Diferenças são achados reportados, não correção automática.
- Relatar fora de escala, nota sem status, status sem nota e positivas em status problemáticos. Cruzar cobertura com presenças LC/CH apenas como controle dentro de RESULTADOS, sem inferir presença na redação a partir dessas áreas.
- Notas ausentes são indisponibilidade, sem causa presumida. Média/mediana menor em competência não demonstra causa ou deficiência individual. Redação e TRI não são escalas equivalentes.

## Execução e entrega

`notebooks/04_redacao.ipynb`: auditoria de inscritos e redação; módulos `redacao.py` (SQL), `redacao_execucao.py` (I/O) e `redacao_graficos.py` (dois PNG). DuckDB 256 MB/uma thread, temporários em work; Pandas só recebe agregados. CSVs em analitica e auditorias em reports. Apresentação lê agregados/auditorias e confere hashes; não dispara pipelines.

Inscritos: `inscritos_execucao.py` conta estritamente PARTICIPANTES em Latin-1 com `;`, validando NU_INSCRICAO e NU_ANO. Total oficial e metadados em `reports/validacao_inscritos_2025.json`; total confirmado distingue-se dos registros divulgados. Contagens iguais entre bases não autorizam equivalência ou join. Não explicar diferenças sem fonte. Região, rede, perfil econômico e avaliadores ficam fora desta POC.
