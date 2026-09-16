# ENEM — Análise de dados

Documento de trabalho · 16/09/2026

## Objetivo e escopo

Investigar participação, desempenho e perfil econômico dos inscritos divulgados no ENEM, com perguntas de negócio claras e evolução iterativa, incremental e validativa. A etapa atual é a definição do contrato analítico; a stack inicial e o ambiente estão preparados, e a implementação analítica ainda será iniciada.

O desafio original contempla análise temporal retrocedendo até 2010 e a relação entre renda familiar e desempenho. A prova de conceito (POC) fica limitada à edição de 2025, começando por presença e desempenho por área e contemplando seis perguntas. A leitura econômica será independente das notas. As métricas abaixo são propostas, não resultados calculados.

## Dados disponíveis

Materiais em `raw/microdados_enem_2025/microdados_enem_2025/`: `DADOS`, `DICIONÁRIO`, `INPUTS` e `LEIA-ME E DOCUMENTOS TÉCNICOS`.

- `RESULTADOS_2025.csv`: 70 colunas, aproximadamente 2,12 GB; base das cinco perguntas iniciais.
- `PARTICIPANTES_2025.csv`: aproximadamente 513 MB; contém informações dos participantes e o questionário socioeconômico; base da sexta pergunta, sobre o perfil dos inscritos divulgados, sem pressupor comparecimento.
- A inspeção anterior cobriu apenas as primeiras 10 mil linhas; não produz estatísticas populacionais.

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

Plano detalhado, stack escolhida e ponto de retomada: [ROADMAP.md](ROADMAP.md).

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

Validação realizada: imports dos quatro pacotes, versões, dependências sem conflitos, consulta DuckDB trivial e execução no kernel. A seleção pela interface do VS Code ainda deve ser feita ao abrir o notebook. Nenhum CSV foi processado nesta preparação; filtros e contratos analíticos continuam pendentes.
