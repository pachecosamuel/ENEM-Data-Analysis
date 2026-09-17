# Roadmap — ENEM 2025

Atualizado em 17/09/2026. Plano de trabalho incremental; caixas abertas representam trabalho futuro.

## Onde estamos e como retomar

- [x] Matriz das seis perguntas e regras iniciais documentadas no [README](../README.md).
- [x] Documentação e inspeção inicial realizadas: cabeçalhos e primeiras 10 mil linhas de RESULTADOS inspecionados.
- [x] Stack inicial escolhida e plano de continuidade registrado aqui.
- [x] Ambiente `.venv` preparado com Python 3.13.15 (64 bits), pip e kernel `ENEM 2025 (.venv)`; imports, dependências, consulta DuckDB e execução no kernel validados.
- [x] Contrato inicial de dez campos, funções reutilizáveis, testes e notebook raw → trusted executados em amostra e volume completo.
- [x] Parquet publicado com 4.810.772 registros, sem exclusões, após reconciliação exata e confirmação da integridade do raw.
- [x] Indicadores de desempenho por área, tabela e dois gráficos validados a partir da trusted.
- [ ] Demais requisitos e perfil dos demais campos ainda pendentes.

**Ponto de retomada:** definir o contrato da participação entre os dois dias e tratar combinações divergentes. O requisito de desempenho por área foi concluído; consultar o notebook 02 e o resumo em `reports/`. Não reprocessar raw para esta próxima análise de presença.

## Decisões tomadas

**Escopo:** POC de 2025, com seis requisitos: desempenho por área; participação entre dias; desempenho e presença por local de prova; notas por rede escolar; redação e competências; perfil econômico. Expandir para anos anteriores somente após validar a POC.

**Duas bases independentes:** RESULTADOS sustenta desempenho e presença. PARTICIPANTES descreve o perfil econômico dos inscritos divulgados: `Q007` é faixa de renda familiar; `Q006` indica se possui renda própria, sem informar seu valor. Não existe chave individual comum entre as bases: não cruzar renda e nota, associar por posição ou filtrar o perfil econômico por comparecimento.

| Ferramenta | Papel no projeto |
| --- | --- |
| Python + Jupyter no VS Code | Conduzir exploração, registrar decisões e executar o notebook. |
| DuckDB | Banco/motor SQL analítico embutido para processamento local. Instalado como pacote no ambiente Python do projeto e executado dentro do processo, sem servidor, interface web ou extensão de DuckDB para VS Code obrigatória. Pode consultar arquivos; um banco persistente `.duckdb` é opcional, não uma camada adicional obrigatória. Consulte a [API Python oficial](https://duckdb.org/docs/current/clients/python/overview). |
| Parquet | Formato dos dados tratados; DuckDB pode consultar e gravar esses arquivos. Consulte a [documentação oficial de Parquet](https://duckdb.org/docs/current/data/parquet/overview). |
| Pandas + biblioteca de gráficos | Pandas é uma biblioteca de DataFrames; será usada com resultados reduzidos para organizar tabelas e alimentar gráficos. Matplotlib foi instalado para os gráficos da POC. |
| Spark | Motor com capacidade de processamento distribuído, reservado a necessidade demonstrada ou objetivo explícito de aprendizado. Não faz parte da implementação inicial. |

**Camadas iniciais:** `raw` preservada → `trusted` com campos pertinentes, tipos e tratamento explícito de categorias/ausências em Parquet → `analitica` com indicadores para tabelas e gráficos. São nomes iniciais simples; nenhuma pasta será renomeada agora. As duas bases permanecem separadas nas camadas. A apresentação consome os indicadores.

## Fases e critérios de saída

### 1. Fechar o primeiro contrato analítico

- [x] Definir unidade de análise, campos `NU_NOTA_CN/CH/LC/MT` e `TP_PRESENCA_CN/CH/LC/MT`, filtros e denominadores.
- [x] Explicitar presença (`0` ausente, `1` presente, `2` eliminado), zeros válidos, notas faltantes e inconsistências; manter as regras por dia como decisão a validar.
- [x] Definir contagens, cobertura, média e mediana complementares, quartis e distribuição por área, sem criar nota global oficial.

**Entregável/saída:** contrato curto com cada métrica, população elegível, numerador/denominador e exclusões definidos, suficiente para reproduzir a primeira análise.

### 2. Preparar e verificar o ambiente

- [x] Medir recursos: Windows 64 bits, aproximadamente 7,87 GiB de RAM total, 1,60 GiB livre e 457,84 GiB livres no disco C na inspeção de 16/09/2026. Valores livres variam; medir novamente antes da carga.
- [x] Preparar ambiente Python do projeto, dependências e kernel Jupyter; versões fixadas em `requirements.txt` e instruções no README. Extensões Python e Jupyter disponíveis no VS Code; o usuário já executou `test_ambiente.ipynb` com sucesso; o notebook novo também foi executado integralmente em kernel novo.
- [x] Validar imports, `pip check`, consulta `SELECT 1 + 1` e inicialização/execução do kernel.
- [x] Executar com limite DuckDB de 256 MB, uma thread e até 10 GB para temporários em `work/`; medir recursos antes/depois e remover staging ao terminar.

**Entregável/saída:** ambiente reproduzível e consulta mínima funcionando. O tamanho dos CSVs, sozinho, não garante tempo de execução nem consumo de memória.

### 3. Validar uma POC pequena

- [x] Criar notebook 02 de desempenho/participação por área sobre a trusted; a leitura raw amostral já foi validada no incremento anterior.
- [x] Validar Latin-1 nativo no DuckDB, acentos em fixture, conversões e faltantes; amostra inicial de 10 mil registros, sem inferência populacional.
- [x] Reconciliar contagens de entrada/saída, categorias de presença e notas, sem exclusões; verificar combinações incompatíveis. Elegibilidade por área validada: presença=1 e nota não nula, incluindo zero.
- [x] Produzir uma tabela por área com contagens, cobertura e estatísticas; dois gráficos iniciais: situação de presença por área e distribuição das notas elegíveis por área.

**Entregável/saída:** notebook executável do início ao fim na amostra, com regras verificadas e tabela/gráficos identificados como amostrais. Qualquer divergência deve estar resolvida ou explicitamente contabilizada.

### 4. Ampliar e tornar reproduzível

- [x] Aplicar o contrato inicial ao volume completo; registrar duração e RAM/disco disponíveis antes/depois (não foi medido o pico de uso).
- [x] Gravar os dez campos em `trusted/resultados_2025_base.parquet`; Pandas recebe apenas o relatório reduzido no notebook.
- [x] Gravar quatro linhas de indicadores em `analitica/desempenho_2025.csv`.
- [x] Reconciliar novamente totais, presenças, notas, ausências e exclusões; atualizar a tabela e os dois gráficos para a base completa.
- [x] Executar notebook raw → trusted ponta a ponta em kernel novo; funções reutilizáveis implementam apenas o contrato inicial aprovado.

**Entregável/saída:** primeira análise completa reproduzível, Parquet validado, controles de qualidade e consumo de recursos registrados. Nenhum total da amostra deve ser apresentado como populacional.

### 5. Desenvolver os demais requisitos gradualmente

- [ ] Participação entre dias: validar combinações LC/CH no primeiro e CN/MT no segundo, tratando eliminações e divergências separadamente.
- [ ] Local de prova: analisar presença e desempenho; documentar mapeamento UF–região, sem confundir aplicação com residência.
- [ ] Rede escolar: explicitar cobertura e não informados; públicas = federal, estadual e municipal; evitar inferência causal.
- [ ] Redação: definir elegibilidade por status e conferir nota total e competências.
- [ ] Perfil econômico independente: quantidades e percentuais por `Q007`, complemento com/sem renda em `Q006`; preservar “nenhuma renda”, separar ausentes/inválidos e explicitar base total e, se usado, denominador de respostas válidas. Não estimar renda pessoal ou renda per capita exata de faixas.

**Entregável/saída por requisito:** contrato, tabela, visualização e controles de qualidade revisados antes de avançar; ao final, apresentação das seis análises com filtros, cobertura e limitações.

### 6. Avaliar expansão temporal até 2010

- [ ] Comparar esquemas, questionários, categorias, cobertura e regras das edições.
- [ ] Investigar edição compatível para associação renda–nota e comparabilidade monetária antes de retomar essa pergunta.

**Entregável/saída:** matriz de compatibilidade e recorte temporal justificado antes de integrar novos anos.

## Decisões ainda pendentes

Filtros e denominadores dos demais requisitos; tratamento das inconsistências de presença por dia; elegibilidade por status da redação; campos adicionais para os demais requisitos; revisar parâmetros de recursos se o escopo crescer. Resolver cada ponto na fase correspondente e atualizar este arquivo com o último passo validado e a próxima ação.

## Entrega validada em 16/09/2026

- [Contrato dos dez campos](../docs/contrato_resultados_2025.md), [módulo](trusted_resultados.py), [notebook executado](01_resultados_trusted.ipynb) e [relatório completo](../reports/validacao_resultados_2025_completo.json).
- Entrada = saída = 4.810.772 registros; todos de 2025. Chave, ano e presenças sem nulos; nenhuma duplicidade, falha de conversão ou categoria inválida. Nenhum achado nas regras de coerência presença/nota verificadas.
- Nulos de notas preservados: CN/MT 1.550.436 por área; CH/LC 1.353.217 por área. Zeros preservados: CN 775, CH 9.087, LC 2.361, MT 893.
- Parquet: 54.733.745 bytes; execução completa observada em 40,77 s, limite de 256 MB/uma thread, raw com SHA-256 idêntico antes/depois. Recursos disponíveis variam; não é benchmark nem medição de pico.
- Seis testes passaram, incluindo falha que preserva o Parquet anterior e comparação exata por chave. `test_ambiente.ipynb` permanece byte a byte igual. Os indicadores/gráficos previstos nas fases 3 e 4 ainda estão abertos.

## Entrega validada em 17/09/2026

[Contrato analítico](../docs/contrato_analitico_desempenho_2025.md), [notebook 02](02_desempenho_por_area.ipynb) e [resumo dos resultados/testes](../reports/resumo_desempenho_2025.md). Cálculo, I/O e gráficos separados em módulos simples, com funções reutilizáveis. Quatro testes novos e seis anteriores passaram. Notebook executado em kernel novo, gráficos inspecionados e hash da trusted preservado.

CN/MT: 3.260.336 elegíveis por área; CH/LC: 3.457.555. Medianas: CN 498,2; CH 513,0; LC 538,8; MT 500,0. CSV mantém precisão; apresentação arredonda. Nenhum ranking entre áreas. A entrega de 16/09 permanece como registro histórico; seus indicadores/gráficos pendentes foram concluídos neste incremento.
