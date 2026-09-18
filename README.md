# ENEM — Análise de dados

Documento de trabalho · 16/09/2026


## Por onde começar

Para ler os resultados, abra [a apresentação](apresentacao/visao_geral_2025.ipynb). Para acompanhar o cálculo, abra [o notebook 02](notebooks/02_desempenho_por_area.ipynb). O [roadmap](docs/ROADMAP.md) registra a próxima decisão.

| Diretório | Responsabilidade |
| --- | --- |
| `src/` | Funções reutilizáveis: transformação, cálculo, I/O e gráficos em módulos separados. |
| `notebooks/` | Acompanhamento do processamento; 01 gera trusted, 02 calcula agregados. |
| `apresentacao/` | Narrativa para leitura e PNG separados em `graficos/`. |
| `docs/` | Contratos e roadmap. |
| `reports/` | Auditorias e relatos de validação. |
| `raw/`, `trusted/`, `analitica/` | Originais, base padronizada e indicadores compactos, respectivamente. |
| `tests/` | Testes pequenos e integração com dados artificiais. |
| `scripts/` | Executor de notebooks; aceita o caminho como argumento. |
| `work/` | Temporários ignorados pelo Git. |

O Git existente foi mantido. `src/__init__.py` identifica o pacote de funções; pastas de dados e documentos não são pacotes Python. Evolução em incrementos pequenos: contrato → cálculo verificado → narrativa factual → revisão.

## Objetivo e escopo

Investigar participação, desempenho e perfil econômico dos inscritos divulgados no ENEM, com perguntas de negócio claras e evolução iterativa, incremental e validativa. A trusted e os indicadores de desempenho por área de 2025 estão implementados e validados. O próximo requisito é analisar participação entre os dois dias.

O desafio original contempla análise temporal retrocedendo até 2010 e a relação entre renda familiar e desempenho. A prova de conceito (POC) fica limitada à edição de 2025, começando por presença e desempenho por área e contemplando seis perguntas. A leitura econômica será independente das notas. As métricas abaixo são propostas, não resultados calculados.

## Dados disponíveis

Materiais em `raw/microdados_enem_2025/microdados_enem_2025/`: `DADOS`, `DICIONÁRIO`, `INPUTS` e `LEIA-ME E DOCUMENTOS TÉCNICOS`.

- `RESULTADOS_2025.csv`: 70 colunas, aproximadamente 2,12 GB; base das cinco perguntas iniciais.
- `PARTICIPANTES_2025.csv`: aproximadamente 513 MB; contém informações dos participantes e o questionário socioeconômico; base da sexta pergunta, sobre o perfil dos inscritos divulgados, sem pressupor comparecimento.
- A inspeção inicial cobriu 10 mil linhas; agora os dez campos do contrato inicial foram validados em todos os 4.810.772 registros de RESULTADOS. Essa validação de qualidade não substitui as análises finais.

Conforme o leia-me (página 7), PARTICIPANTES e RESULTADOS não possuem chave comum. O dicionário distingue `NU_SEQUENCIAL` de `NU_INSCRICAO`. A renda familiar (`Q007`) está somente em PARTICIPANTES: não é possível prometer seu cruzamento individual com notas, nem associar registros pela posição. A pergunta renda × desempenho permanece no escopo futuro, a investigar em edição compatível, sem mudar o ano da POC agora.

## Seis perguntas norteadoras

| Pergunta | Campos principais | Métricas iniciais propostas |
| --- | --- | --- |
| 1. Como o desempenho se distribui por área? | `NU_NOTA_CN`, `NU_NOTA_CH`, `NU_NOTA_LC`, `NU_NOTA_MT` e respectivas `TP_PRESENCA_*` | Contagem de notas elegíveis, cobertura, média e mediana complementares, quartis e distribuição por área. |
| 2. Como a participação varia entre os dois dias? | `TP_PRESENCA_LC`, `TP_PRESENCA_CH`, `TP_PRESENCA_CN`, `TP_PRESENCA_MT`; `TP_STATUS_REDACAO` como verificação complementar | Contagens e proporções por situação e dia; participação em ambos, somente no primeiro ou segundo, e em nenhum; inconsistências separadas. |
| 3. Como desempenho e presença variam por local de aplicação? | `CO_MUNICIPIO_PROVA`, `NO_MUNICIPIO_PROVA`, `SG_UF_PROVA`, notas e presenças por área | Volume e taxas de presença por local; cobertura das notas, média, mediana e quartis por área. Região poderá ser derivada de UF com mapeamento explícito. |
| 4. Como as notas variam por rede escolar, incluindo pública × privada? | `TP_DEPENDENCIA_ADM_ESC`, notas e presenças por área | Contagens e cobertura da informação escolar; média, mediana e quartis por rede e agrupamento público/privado. |
| 5. Qual o panorama da redação e de suas competências? | `NU_NOTA_REDACAO`, `NU_NOTA_COMP1` a `NU_NOTA_COMP5`, `TP_STATUS_REDACAO` | Contagens e proporções por status; cobertura, média, mediana, quartis e distribuição da nota total e de cada competência. |
| 6. Como os inscritos divulgados se distribuem por faixa de renda familiar? | `Q007` (principal), `Q006` (complemento); `Q005` para contexto do número de moradores | Quantidades e percentuais por faixa de renda mensal familiar; complemento com percentuais com/sem renda própria. Denominador principal: todos os registros de PARTICIPANTES; se houver percentual entre respostas válidas, identificá-lo separadamente para cada campo. |

Toda proporção deve informar numerador, denominador e recorte. Para notas, apresentar também quantidade elegível e valores ausentes. Moda não é prioridade inicial.

## Regras de interpretação e validação

- **Áreas:** CN, CH, LC e MT são áreas de conhecimento, não notas isoladas de física, química, história etc. Redação será analisada separadamente; não há proposta de uma nota global oficial.
- **Presença:** `0` = ausente, `1` = presente e `2` = eliminado. Nota zero não significa ausência. Primeiro dia: LC, CH e redação; segundo: CN e MT. Regra inicial proposta: presença no dia exige código `1` nas duas áreas objetivas correspondentes. Ausência nas duas indica ausência no dia; eliminações e combinações divergentes devem ser discriminadas e verificadas antes de consolidar indicadores. O status da redação exige interpretação própria pelo dicionário.
- **Elegibilidade:** definir por área e status quais notas entram em cada métrica; manter zeros válidos, distinguir ausências de valores faltantes e publicar exclusões. Na redação, explicitar o tratamento de cada status e validar a relação entre total e competências conforme documentação.
- **Rede escolar:** `TP_DEPENDENCIA_ADM_ESC`: `1` federal, `2` estadual, `3` municipal e `4` privada. Públicas = `1`, `2` e `3`. A informação escolar é incompleta/selecionada: informar cobertura sobre a base e o recorte elegível, mantendo não informados separados. Diferenças observadas não demonstram causalidade nem permitem inferir renda.
- **Geografia:** local de prova não equivale à residência. `TP_LOCALIZACAO_ESC` indica escola urbana/rural, não urbanização ou residência do candidato. Expectativas de desempenho regional ou por rede são hipóteses a testar.
- **Perfil econômico:** `Q007` informa a faixa de renda mensal familiar, incluindo o respondente e os moradores. `Q006` indica apenas se possui renda própria (`A` = não; `B` = sim), sem valor ou faixa de renda pessoal. `Q005` informa o número de moradores; não permite obter renda per capita exata a partir de faixas. A análise descreve os inscritos divulgados em PARTICIPANTES e não deve ser filtrada por presença: não há ligação com RESULTADOS, e o cruzamento individual renda–nota continua inviável em 2025.
- **Qualidade econômica:** aplicar categorias e limites de `Q007` conforme o dicionário de 2025, preservando “nenhuma renda” como resposta válida. Separar respostas ausentes e códigos inválidos, com contagens e percentuais sobre todos os registros de PARTICIPANTES. Para cada campo, calcular percentual principal como contagem da categoria dividida pelo total da base; se apresentado, o percentual entre respostas válidas usa somente as respostas válidas daquele campo como denominador. Reconciliar categorias válidas, ausentes e inválidas com o total, admitindo diferenças de arredondamento nos percentuais.
- **Qualidade:** conferir esquema, tipos, códigos e faixas no dicionário; investigar duplicidades, faltantes e incompatibilidades entre presença, nota e status. Reconciliar totais e denominadores. Validar a POC pequena antes de ampliar para a base completa; registrar filtros e limitações para reprodução.

## Roadmap

Plano detalhado, stack escolhida e ponto de retomada: [ROADMAP.md](docs/ROADMAP.md).

1. Consolidar visão de negócio e as seis perguntas.
2. Definir o contrato analítico: população, unidade de análise, elegibilidade, regras por dia, métricas e denominadores.
3. Validar uma POC pequena de presença e desempenho por área.
4. Estruturar tratamento reproduzível após validar as regras.
5. Desenvolver gradualmente as seis análises, incluindo a leitura econômica independente em PARTICIPANTES, conferindo cobertura e consistência em cada entrega.
6. Preparar apresentação com resultados, hipóteses e limitações.
7. Expandir a série temporal até 2010 somente após avaliar compatibilidade de questionários, cobertura e disponibilidade de renda e notas associáveis.

Camadas lógicas propostas: `raw` → padronizados → analíticos → apresentação. Os originais serão preservados; a stack inicial e as camadas propostas estão detalhadas no ROADMAP.

## Ambiente de desenvolvimento

Preparado em 16/09/2026 com **Python 3.13.15 de 64 bits**, `venv` padrão e pip. Pacotes principais: DuckDB 1.5.5, Pandas 3.0.5, Matplotlib 3.11.2 e ipykernel 7.3.0. O [requirements.txt](requirements.txt) fixa também as dependências transitivas desta instalação Windows/Python 3.13.

O Python 3.13 foi instalado para o usuário em `%LOCALAPPDATA%\Programs\Python\Python313`, preservando o Python 3.14 de 32 bits existente, sem adicioná-lo ao PATH. `.venv` já estava ignorada pelo Git. O kernel **ENEM 2025 (.venv)** foi registrado no próprio ambiente e no escopo do usuário, sem configuração de sistema. As extensões Python e Jupyter estão disponíveis no VS Code.

No PowerShell, abra a pasta e ative o ambiente:

```powershell
Set-Location 'C:\Users\SamuelCaetanoPacheco\Desktop\ENEM-Data-Analysis'
.\.venv\Scripts\Activate.ps1
python --version
```

Se a ativação for bloqueada, use diretamente `.\.venv\Scripts\python.exe`, sem alterar a política de execução. Para sair de um ambiente ativado, execute `deactivate`.

No VS Code, abra essa pasta. Ao criar ou abrir um notebook, clique em **Select Kernel / Selecionar Kernel → Select Another Kernel / Selecionar Outro Kernel → Jupyter Kernel → ENEM 2025 (.venv)**. Se a lista ainda não atualizar, recarregue a janela; a alternativa é **Python Environments / Ambientes Python** e selecionar `.venv\Scripts\python.exe` deste projeto. Para scripts, use **Python: Select Interpreter** na paleta de comandos e escolha esse mesmo executável.

Para recriar o ambiente, com Python 3.13 de 64 bits disponível e sem um `.venv` existente:

```powershell
& "$env:LOCALAPPDATA\Programs\Python\Python313\python.exe" -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m ipykernel install --sys-prefix --name python3 --display-name 'ENEM 2025 (.venv)'
.\.venv\Scripts\python.exe -m ipykernel install --user --name enem-2025 --display-name 'ENEM 2025 (.venv)'
.\.venv\Scripts\python.exe -m pip check
```

Validação realizada: imports dos quatro pacotes, versões, dependências sem conflitos, consulta DuckDB trivial e execução no kernel. O teste inicial de ambiente foi executado pelo usuário; a organização atual preserva o estado versionado por ele. A preparação do ambiente não processou CSVs; o incremento raw → trusted descrito abaixo já foi concluído.

## Primeiro incremento raw → trusted

Contrato em [docs/contrato_resultados_2025.md](docs/contrato_resultados_2025.md), funções em [src/trusted_resultados.py](src/trusted_resultados.py) e notebook executado em [notebooks/01_resultados_trusted.ipynb](notebooks/01_resultados_trusted.ipynb). O notebook funciona a partir da raiz ou de `notebooks/`, com kernel reiniciado.

A saída local `trusted/resultados_2025_base.parquet` contém **4.810.772 registros e dez campos**, sem filtro de presença, com 54.733.745 bytes (aproximadamente 54,73 MB). O CSV original permaneceu intacto por SHA-256. Os [relatórios de validação](reports/validacao_resultados_2025_completo.json) registram tipos, contagens, nulos, coerência, hashes e recursos.

| Área | Notas nulas preservadas | Notas zero preservadas |
| --- | ---: | ---: |
| CN | 1.550.436 | 775 |
| CH | 1.353.217 | 9.087 |
| LC | 1.353.217 | 2.361 |
| MT | 1.550.436 | 893 |

Identificador, ano e presenças: nenhum nulo. Nenhuma chave duplicada, falha de conversão, categoria inesperada, ano diferente de 2025, nota negativa ou incoerência presença/nota nas regras verificadas. Isso se refere somente aos dez campos e aos controles do contrato; os demais campos ainda não foram perfilados.

Para reproduzir na raiz do projeto:

```powershell
.\.venv\Scripts\python.exe -X utf8 -m unittest discover -s tests -v
.\.venv\Scripts\python.exe -X utf8 src\trusted_resultados.py --amostra 10000
.\.venv\Scripts\python.exe -X utf8 src\trusted_resultados.py
```

Alternativamente, execute todas as células do notebook. O fluxo usa DuckDB com 256 MB e uma thread; staging e spill ficam em `work/`. Só publica após conferir o Parquet temporário; uma falha preserva a saída anterior. `trusted/` e `work/` são ignorados pelo Git. Os seis testes cobrem nulos/zero, conversões, categorias, chave/ano, Latin-1/CSV inválido, reconciliação e reexecução/publicação segura. A execução completa observada levou 40,77 segundos, sem promessa para outras execuções ou máquinas.

O primeiro incremento foi seguido pelos indicadores de desempenho por área abaixo. PARTICIPANTES permanece independente de RESULTADOS.

## Desempenho por área — concluído em 17/09/2026

[Contrato analítico](docs/contrato_analitico_desempenho_2025.md) · [Notebook 02](notebooks/02_desempenho_por_area.ipynb) · [Resultados e validação](reports/resumo_desempenho_2025.md).

| Área | Elegíveis | Média | Q1 | Mediana | Q3 |
| --- | ---: | ---: | ---: | ---: | ---: |
| CN | 3.260.336 | 499,97 | 443,5 | 498,2 | 550,9 |
| CH | 3.457.555 | 511,19 | 446,6 | 513,0 | 574,0 |
| LC | 3.457.555 | 532,12 | 490,3 | 538,8 | 581,6 |
| MT | 3.260.336 | 519,98 | 416,5 | 500,0 | 606,8 |

Cada área inclui somente presentes com nota naquela área; zero é válido. Quartis contínuos com interpolação linear descrevem os 50% centrais. Populações diferentes e escalas por área impedem interpretar a tabela como ranking de dificuldade. Não calculamos nota global nem inferimos causalidade.

Código separado por responsabilidade: `src/desempenho.py` contém definições/cálculo/validação; `src/desempenho_execucao.py`, leitura/gravação; `src/desempenho_graficos.py`, apresentação. Sem classes ou framework adicional. CSV compacto em `analitica/`, auditoria em `reports/` e PNG em `apresentacao/graficos/`. A trusted não foi modificada; raw não foi reprocessado.

Na raiz, rode `.\.venv\Scripts\python.exe -X utf8 -m src.desempenho_execucao` para atualizar os indicadores ou execute o notebook de apresentação para gerar também os gráficos. Testes: `.\.venv\Scripts\python.exe -X utf8 -m unittest discover -s tests -v` (dez aprovados). O notebook foi executado em kernel novo e os gráficos foram verificados visualmente.

Próximo incremento: contrato e análise de participação entre os dois dias. Os demais requisitos continuam no [roadmap](docs/ROADMAP.md).

### Apresentação revisada

O gráfico usa áreas por extenso e escala comum com mínimos/máximos **observados**: Natureza 0–858,7; Humanas 0–856,4; Linguagens 0–794,5; Matemática 0–980,3. A linha fina mostra a amplitude, a faixa colorida os 50% centrais e o ponto a mediana. Contagens e detalhes ficam na tabela do notebook narrativo. Esses extremos não são limites teóricos da TRI.

Reexecutar somente a apresentação: `.\.venv\Scripts\python.exe -X utf8 scripts\executar_notebook.py apresentacao\visao_geral_2025.ipynb`. O fluxo consulta trusted; não refaz raw → trusted. [Relato da reorganização](reports/revisao_apresentacao_2025.md).
