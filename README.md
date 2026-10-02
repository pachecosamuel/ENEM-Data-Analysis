# ENEM — participação, desempenho e perfil socioeconômico

Projeto de análise dos microdados públicos do ENEM, com desenvolvimento incremental e resultados reproduzíveis. Atualizado em **02/10/2026**.

## Visão de negócio

O projeto transforma arquivos extensos do ENEM em informações compreensíveis sobre comparecimento às provas, distribuição das notas e diferenças entre os grupos disponíveis nos dados. A proposta é apoiar a discussão educacional com evidências, explicitar os limites de cada comparação e levantar perguntas para aprofundamento.

O trabalho começa pelas perguntas de análise: qual população estamos descrevendo, o que cada indicador mede e quais decisões de interpretação os dados permitem? A partir disso, são definidos os campos, critérios de inclusão, denominadores e verificações. A tecnologia sustenta esse processo; a entrega principal são análises que possam ser explicadas, conferidas e reproduzidas.

As conclusões são descritivas. Diferenças entre regiões, redes ou edições não demonstram, por si só, causas ou efeitos de políticas educacionais.

## Objetivos e perguntas

| Tema | Pergunta de análise | Entrega |
| --- | --- | --- |
| Desempenho por área | Como as notas se distribuem em Natureza, Humanas, Linguagens e Matemática? | Quantidade de notas elegíveis, médias, medianas, quartis e distribuição. |
| Participação entre dias | Quantos comparecem a cada dia e quantos permanecem nos dois? | Contagens, taxas, transições, retenção e situações de eliminação ou inconsistência. |
| Local de aplicação | Como presença e desempenho variam por região e UF da prova? | Indicadores territoriais com denominadores próprios e referência geográfica explícita. |
| Rede escolar | Como as notas variam entre redes, considerando a cobertura dessa informação? | Distribuições por rede e identificação dos registros sem informação escolar. |
| Redação | Qual é o panorama da nota final e das cinco competências? | Situações da redação, distribuição da nota e análise das competências com elegibilidade definida. |
| Perfil econômico | Como os inscritos divulgados se distribuem por renda familiar e declaração de renda própria? | Contagens e percentuais por categoria do questionário, independentes das notas em 2024–2025. |

O objetivo de longo prazo inclui comparações temporais até 2010 e a investigação de renda × desempenho em uma edição que permita associação individual validada. A expansão depende da compatibilidade de campos, conceitos, populações e faixas de renda.

## Estado atual

- **Fase 1 concluída:** primeira visão dos seis temas para 2025, com indicadores, gráficos e apresentação.
- **Fase 2 em andamento:** participação entre dias de 2024 implementada e comparada com 2025. Os outros cinco temas de 2024 ainda não foram iniciados.
- **Auditoria documental concluída:** esquemas e limitações das 16 edições de 2010–2025 examinados. Isso não significa que todas tenham sido processadas ou integradas.
- **Planejado:** completar 2024 incrementalmente, incorporar 2023, investigar renda × desempenho em 2023 e expandir a série histórica por grupos de edições compatíveis.

Detalhamento municipal e redação por local ou rede não fazem parte da primeira visão concluída de 2025.

## Por onde começar

| Material | Conteúdo |
| --- | --- |
| [Resumo de 2025](apresentacao/RESUMO_FASE_1_2025.md) | Visão informacional dos seis temas, resultados e limites. |
| [Apresentação de 2025](apresentacao/visao_geral_2025.ipynb) | Narrativa completa com tabelas e gráficos. |
| [Comparação de participação 2024–2025](apresentacao/participacao_2024_2025.ipynb) | Presença por dia, permanência e transições nas duas edições. |
| [Resumo do incremento 2024](apresentacao/RESUMO_PARTICIPACAO_2024_2025.md) | Resultados, arquivos, reprodução e verificações. |
| [Fluxograma do processo](apresentacao/graficos/fluxograma_fase_1_2025.svg) | Da descoberta e das perguntas aos indicadores e à apresentação. |
| [Roadmap da fase 2](docs/ROADMAP_FASE_2.md) | Próximos incrementos e critérios para avançar. |

Os notebooks executados contêm saídas para leitura. Para reexecutá-los, são necessários o ambiente e os arquivos locais referenciados.

## Dados e arquitetura

As fontes são os pacotes públicos de microdados do Inep, acompanhados de dicionários, LeiaMe e instruções de leitura. Os arquivos originais ficam em `raw/` e são preservados durante o processamento.

**RESULTADOS** contém as presenças por área e informações de provas, notas e escola. **PARTICIPANTES** contém características dos inscritos e respostas ao questionário socioeconômico. O nome PARTICIPANTES não significa que esse seja o arquivo usado para calcular comparecimento aos dias: as quatro presenças vêm de RESULTADOS.

O fluxo das análises de resultados é:

```text
raw/RESULTADOS → seleção e tratamento → trusted/*.parquet
                                             ↓
                                    indicadores em analitica/
                                             ↓
                                  tabelas, gráficos e narrativa
```

| Base tratada | Conteúdo e finalidade |
| --- | --- |
| `trusted/resultados_2025_base.parquet` | Base compartilhada de 2025, contrato v4 com 22 campos e 4.810.772 registros. Sustenta participação, notas, redação, local e rede. |
| `trusted/participacao_2024_base.parquet` | Recorte mínimo de 2024, com identificador, edição e quatro presenças: seis campos e 4.332.944 registros. Sustenta apenas o incremento de participação. |

Ambos os Parquets são derivados dos respectivos arquivos raw de RESULTADOS, sem excluir registros no preparo. Os nomes refletem o alcance de cada entrega. Não foi necessário criar outro Parquet de participação para 2025, pois seus campos já estão na base compartilhada.

Durante o cálculo dos indicadores de participação, **DuckDB consulta a trusted**, e não novamente o raw. Na comparação temporal, são consolidados indicadores com coluna de edição; não há ligação de pessoas entre anos nem exigência de uma tabela física unificada de registros.

O perfil econômico de 2025 segue um caminho independente: `raw/PARTICIPANTES → indicadores econômicos → apresentação`. Não passa pela trusted de resultados. Os notebooks de apresentação consomem agregados existentes; ajustes visuais não exigem refazer a carga ou o cálculo dos microdados.

## Tecnologias e responsabilidades

| Tecnologia | Papel no projeto |
| --- | --- |
| **Python** | Implementação das regras, organização da execução e verificações. |
| **DuckDB** | Leitura de CSV/Parquet, consultas SQL e agregações locais, dentro do processo Python e sem servidor dedicado. |
| **Parquet** | Armazenamento colunar das bases tratadas, com tipos explícitos. |
| **Pandas** | Organização de tabelas reduzidas para análise e apresentação. |
| **Matplotlib** | Geração dos gráficos em PNG a partir dos indicadores. |
| **Jupyter / IPython** | Exploração, execução dos incrementos e registro de resultados e narrativa. |
| **VS Code** | Ambiente de edição de código e notebooks. |
| **venv e pip** | Isolamento do ambiente e instalação das dependências fixadas. |
| **Git e unittest** | Versionamento e verificações automatizadas das regras e do processamento. |

O ambiente documentado usa Python 3.13 de 64 bits. As versões dos pacotes estão fixadas em [requirements.txt](requirements.txt). O processamento atual é local: Spark, serviços de nuvem e um banco persistente DuckDB não são requisitos desta implementação. Nas rotinas de preparação e participação, DuckDB é configurado com limite de 256 MB e uma thread; isso não representa o consumo total do processo.

## Organização do repositório

| Caminho | Responsabilidade |
| --- | --- |
| `raw/` | Microdados originais e documentação por edição. |
| `trusted/` | Parquets preparados e validados; dados locais, fora do versionamento. |
| `analitica/` | Indicadores em CSV, com contagens, percentuais e denominadores. |
| `src/` | Regras de cálculo, entrada/saída e gráficos separados por responsabilidade. |
| `notebooks/` | Execução e inspeção de cada incremento. |
| `apresentacao/` | Notebooks narrativos, resumos e gráficos finais. |
| `docs/` | Contratos, auditoria temporal, referências e roadmaps. |
| `reports/` | Evidências de validação e registros das entregas. |
| `tests/` | Testes das regras e dos pontos relevantes de integridade. |
| `scripts/executar_notebook.py` | Execução de um notebook em kernel novo, com salvamento das saídas. |
| `work/` | Temporários e backups de trabalho; fora do versionamento. |

O núcleo `src/participacao.py` é compartilhado entre 2024 e 2025. O preparo mínimo de 2024 fica em `participacao_entrada.py`; a leitura/publicação anual em `participacao_execucao.py`; a consolidação em `participacao_comparacao.py`. Os módulos de gráficos trabalham com indicadores, não com milhões de registros individuais.

## Executar o projeto

Os comandos abaixo são para PowerShell, a partir da raiz do repositório. Os pacotes de microdados devem estar extraídos nos caminhos definidos pelos contratos. O repositório não substitui o download e a organização dessas fontes.

### Preparação do ambiente

Se `.venv` já estiver configurada, use-a diretamente. Para criar um ambiente novo com Python 3.13 de 64 bits instalado:

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m ipykernel install --user --name enem-2025 --display-name 'ENEM 2025 (.venv)'
```

O executor usa o kernel `enem-2025`, também para o incremento de 2024; o nome do kernel identifica o ambiente, não restringe a edição analisada. No VS Code, selecione **ENEM 2025 (.venv)** para os notebooks. Os comandos usam o executável diretamente, dispensando ativação e alterações na política de execução do PowerShell.

### Atualizar somente as apresentações

Com os indicadores já disponíveis:

```powershell
.\.venv\Scripts\python.exe -X utf8 scripts\executar_notebook.py apresentacao\visao_geral_2025.ipynb
.\.venv\Scripts\python.exe -X utf8 scripts\executar_notebook.py apresentacao\participacao_2024_2025.ipynb
```

### Processar os incrementos

Para reconstruir 2025, execute os notebooks **01 → 02 → 03 → 04 → 05 → 06 → 07**, depois a apresentação de 2025. O 01 prepara a trusted; 02–06 usam essa base. O 07 calcula o perfil econômico a partir de PARTICIPANTES e pode ser executado independentemente. Use `scripts/executar_notebook.py` com o caminho do notebook desejado.

Para preparar a participação de 2024 e compará-la com os indicadores validados de 2025:

```powershell
.\.venv\Scripts\python.exe -X utf8 scripts\executar_notebook.py notebooks\08_participacao_2024.ipynb
.\.venv\Scripts\python.exe -X utf8 scripts\executar_notebook.py apresentacao\participacao_2024_2025.ipynb
```

O notebook 08 verifica os agregados e a validação preexistentes de 2025 antes de consolidar a comparação. A sequência não reconstrói os indicadores de 2025.

Para executar a suíte de testes, quando necessário:

```powershell
.\.venv\Scripts\python.exe -X utf8 -m unittest discover -s tests -v
```

## Qualidade e interpretação

- **Denominadores explícitos:** taxas de presença usam a base publicada da edição; retenção usa os presentes no primeiro dia. Diferenças de taxas entre edições são expressas em pontos percentuais.
- **Presenças e ausências:** em 2024–2025, presença completa no dia exige código 1 nas duas áreas correspondentes. Eliminações, pares mistos, nulos e códigos inválidos são tratados separadamente. Nota zero não é ausência.
- **Notas elegíveis:** as análises objetivas usam presentes com nota disponível, preservando zeros válidos. Redação final e competências têm recortes próprios. As quatro áreas não compõem um ranking de dificuldade nem uma nota global oficial.
- **Cobertura escolar:** a rede está informada em apenas parte da base de 2025, com seleção descrita na documentação. Comparações não demonstram qualidade ou efeito causal da escola.
- **Geografia:** local de prova não equivale a residência. A região é derivada de uma referência explícita de UF.
- **Renda e notas:** não foi identificado vínculo individual documentado e verificável entre PARTICIPANTES e RESULTADOS públicos de 2024–2025. Não são associados pela posição, contagem ou igualdade aparente de identificadores. Consulte a [nota técnica de vínculo](docs/NOTA_TECNICA_VINCULO_PARTICIPANTES_RESULTADOS_2024_2025.md).
- **Temporalidade:** identificadores não acompanham pessoas entre anos. Questionários, faixas monetárias, regras e cobertura podem mudar. A auditoria orienta adaptações por edição antes de qualquer comparação.
- **Integridade:** conforme o contrato de cada incremento, são conferidos tipos, códigos, chaves, nulos, totais, denominadores, releitura de Parquet e hashes. A publicação ocorre após as verificações previstas; gráficos são inspecionados visualmente.

## Documentação de referência

- [Contrato da trusted de 2025](docs/contrato_resultados_2025.md).
- [Contrato de participação de 2025](docs/contrato_analitico_participacao_2025.md) e [extensão 2024–2025](docs/contrato_participacao_2024_2025.md).
- [Auditoria de viabilidade temporal 2010–2025](docs/viabilidade_temporal_2010_2025.md).
- [Histórico da fase 1](docs/ROADMAP.md) e [planejamento e andamento da fase 2](docs/ROADMAP_FASE_2.md).

O histórico detalhado de versões, validações e entregas permanece nesses documentos. Este README descreve o estado atual e os caminhos para entender e executar o projeto.
