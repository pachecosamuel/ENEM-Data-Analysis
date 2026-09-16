# Roadmap — ENEM 2025

Atualizado em 16/09/2026. Plano de trabalho incremental; caixas abertas representam trabalho futuro.

## Onde estamos e como retomar

- [x] Matriz das seis perguntas e regras iniciais documentadas no [README](README.md).
- [x] Documentação e inspeção inicial realizadas: cabeçalhos e primeiras 10 mil linhas de RESULTADOS inspecionados.
- [x] Stack inicial escolhida e plano de continuidade registrado aqui.
- [ ] Perfil completo dos dados, ETL, notebook e instalação do ambiente ainda não validados.

**Ponto de retomada:** começar pela fase 1, fechando o contrato analítico de desempenho por área e suas regras de presença. Em seguida, preparar e verificar o ambiente. Ainda não há resultados populacionais calculados. Este documento atualiza a definição de ferramentas que estava pendente no README.

## Decisões tomadas

**Escopo:** POC de 2025, com seis requisitos: desempenho por área; participação entre dias; desempenho e presença por local de prova; notas por rede escolar; redação e competências; perfil econômico. Expandir para anos anteriores somente após validar a POC.

**Duas bases independentes:** RESULTADOS sustenta desempenho e presença. PARTICIPANTES descreve o perfil econômico dos inscritos divulgados: `Q007` é faixa de renda familiar; `Q006` indica se possui renda própria, sem informar seu valor. Não existe chave individual comum entre as bases: não cruzar renda e nota, associar por posição ou filtrar o perfil econômico por comparecimento.

| Ferramenta | Papel no projeto |
| --- | --- |
| Python + Jupyter no VS Code | Conduzir exploração, registrar decisões e executar o notebook. |
| DuckDB | Banco/motor SQL analítico embutido para processamento local. Será instalado como pacote no ambiente Python do projeto e executado dentro do processo, sem servidor, interface web ou extensão de DuckDB para VS Code obrigatória. Pode consultar arquivos; um banco persistente `.duckdb` é opcional, não uma camada adicional obrigatória. Consulte a [API Python oficial](https://duckdb.org/docs/current/clients/python/overview). |
| Parquet | Formato dos dados tratados; DuckDB pode consultar e gravar esses arquivos. Consulte a [documentação oficial de Parquet](https://duckdb.org/docs/current/data/parquet/overview). |
| Pandas + biblioteca de gráficos | Pandas é uma biblioteca de DataFrames; será usada com resultados reduzidos para organizar tabelas e alimentar gráficos. A biblioteca de visualização será escolhida na POC. |
| Spark | Motor com capacidade de processamento distribuído, reservado a necessidade demonstrada ou objetivo explícito de aprendizado. Não faz parte da implementação inicial. |

**Camadas iniciais:** `raw` preservada → `trusted` com campos pertinentes, tipos e tratamento explícito de categorias/ausências em Parquet → `analitica` com indicadores para tabelas e gráficos. São nomes iniciais simples; nenhuma pasta será renomeada agora. As duas bases permanecem separadas nas camadas. A apresentação consome os indicadores.

## Fases e critérios de saída

### 1. Fechar o primeiro contrato analítico

- [ ] Definir unidade de análise, campos `NU_NOTA_CN/CH/LC/MT` e `TP_PRESENCA_CN/CH/LC/MT`, filtros e denominadores.
- [ ] Explicitar presença (`0` ausente, `1` presente, `2` eliminado), zeros válidos, notas faltantes e inconsistências; manter as regras por dia como decisão a validar.
- [ ] Definir contagens, cobertura, média e mediana complementares, quartis e distribuição por área, sem criar nota global oficial.

**Entregável/saída:** contrato curto com cada métrica, população elegível, numerador/denominador e exclusões definidos, suficiente para reproduzir a primeira análise.

### 2. Preparar e verificar o ambiente

- [ ] Medir RAM disponível e espaço em disco, incluindo margem para temporários e Parquet; registrar características da máquina.
- [ ] Preparar ambiente Python do projeto, dependências e kernel Jupyter no VS Code; registrar versões.
- [ ] Validar importação do DuckDB e uma consulta pequena; definir limites de memória, paralelismo e diretório temporário conforme medições.

**Entregável/saída:** ambiente reproduzível e consulta mínima funcionando. O tamanho dos CSVs, sozinho, não garante tempo de execução nem consumo de memória.

### 3. Validar uma POC pequena

- [ ] Criar notebook de participação e desempenho por área, começando por leitura amostral com separador `;`, codificação Latin-1 e tipos explícitos conforme dicionário.
- [ ] Validar a estratégia de leitura da codificação no leitor escolhido, acentos, conversões e faltantes; registrar como a amostra foi obtida, sem tratá-la como representativa da população.
- [ ] Reconciliar contagens de entrada, categorias de presença, notas elegíveis e exclusões; investigar combinações incompatíveis.
- [ ] Produzir uma tabela por área com contagens, cobertura e estatísticas; dois gráficos iniciais: situação de presença por área e distribuição das notas elegíveis por área.

**Entregável/saída:** notebook executável do início ao fim na amostra, com regras verificadas e tabela/gráficos identificados como amostrais. Qualquer divergência deve estar resolvida ou explicitamente contabilizada.

### 4. Ampliar e tornar reproduzível

- [ ] Aplicar as regras validadas ao volume completo, medindo tempo, memória e uso de disco.
- [ ] Gravar os campos pertinentes em `trusted`/Parquet e os indicadores em `analitica`; levar ao Pandas apenas resultados reduzidos.
- [ ] Reconciliar novamente totais, presenças, notas, ausências e exclusões; atualizar a tabela e os dois gráficos para a base completa.
- [ ] Reiniciar o kernel e executar ponta a ponta a partir dos originais, conferindo resultados; extrair funções reutilizáveis somente quando as regras estabilizarem.

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

Filtros finais e denominadores das análises de desempenho; tratamento das inconsistências de presença por dia; elegibilidade por status da redação; tipos e categorias efetivos no contrato; parâmetros de memória/paralelismo e temporários; biblioteca de gráficos e organização física final. Resolver cada ponto na fase correspondente e atualizar este arquivo com o último passo validado e a próxima ação.
