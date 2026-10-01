# ENEM 2025: o que a primeira fase mostrou

Fechamento da prova de conceito (POC) · 30/09/2026

A primeira fase está concluída no escopo atual: seis análises sobre participação, notas, local de prova, rede escolar, redação e perfil econômico. A base publicada contém **4.810.772 registros em cada um dos dois arquivos analisados**. Esses totais não devem ser somados: os arquivos descrevem aspectos distintos da edição e não podem ser ligados individualmente.

## A pergunta que orientou o trabalho

Como transformar os microdados do ENEM em uma leitura compreensível de quem participa, como as notas se distribuem e quais diferenças aparecem nos recortes disponíveis?

Começamos por 2025 para construir e conferir uma primeira visão antes de ampliar a série histórica. A exploração da documentação e de uma amostra ajudou a transformar perguntas em regras claras: quem entra em cada análise, o que conta como presença, como tratar notas ausentes e qual é a base de cada percentual. Cada tema foi desenvolvido e validado em um incremento, até chegar às tabelas, gráficos e narrativa da apresentação.

Python, DuckDB e notebooks Jupyter apoiaram o tratamento e a análise; Pandas organizou tabelas reduzidas e Matplotlib produziu os gráficos. Os arquivos originais foram preservados. A apresentação utiliza os indicadores já preparados.

![Da exploração à apresentação](graficos/fluxograma_fase_1_2025.png)

## As seis análises e seus resultados

| Pergunta | O que encontramos em 2025 | Como interpretar |
| --- | --- | --- |
| **1. Como as notas se distribuem por área?** | Medianas: Natureza **498,2**; Humanas **513,0**; Linguagens **538,8**; Matemática **500,0**. Natureza e Matemática têm **3.260.336** notas elegíveis por área; Humanas e Linguagens, **3.457.555**. | Entram participantes presentes com nota disponível; zeros válidos são mantidos. As quatro áreas medem conhecimentos diferentes, sem ranking de dificuldade entre elas. |
| **2. Como a participação muda entre os dias?** | Primeiro dia: **3.457.555 presentes (71,87%)**. Segundo: **3.260.336 (67,77%)**. **3.244.348** compareceram aos dois dias: **93,83%** dos presentes no primeiro. | Percentuais diários usam os **4.810.772 registros de RESULTADOS**. A retenção usa os presentes no primeiro dia. **211.292** passaram de presente a ausente; isso difere da redução líquida de **197.219** presentes. |
| **3. O que muda por local de prova?** | Entre as cinco regiões, o Nordeste teve a maior presença no segundo dia: **70,52%**, ou **1.225.462 de 1.737.630** registros da região. O Sudeste apresentou as maiores medianas nas quatro áreas: **512,9; 536,5; 556,8; 541,4**, respectivamente. | O recorte é o **local de aplicação**, não a residência. As medianas usam presentes com nota em cada área; no Sudeste são **1.102.581** em Natureza/Matemática e **1.168.120** em Humanas/Linguagens. |
| **4. Como as notas variam por rede escolar?** | A rede está informada em **1.739.028 registros (36,15%)**; **3.071.744** não têm essa informação. Como exemplo, a mediana em Matemática foi **588,5** na federal, **462,3** na estadual, **528,1** na municipal e **627,4** na privada. | As bases elegíveis desse exemplo são **68.618; 964.885; 6.619; 252.481**, respectivamente. A cobertura é selecionada e a rede municipal tem base menor. Essas diferenças não medem o efeito causal ou a qualidade das escolas. |
| **5. Qual é o panorama da redação?** | **3.457.555** notas registradas; média **580,80**, mediana **600** e metade central entre **480 e 720**. Há **211.859** notas zero. Nas cinco competências, todas as medianas são **120**. | A nota final mantém os zeros registrados. Competências usam outro recorte: **3.245.696** redações com status “Sem problemas” e notas completas. Não confundir os dois universos. |
| **6. Qual é o perfil econômico dos inscritos divulgados?** | **3.424.548 (71,18%)** declaram renda familiar mensal de até **R$ 3.036**, incluindo nenhuma renda. **3.454.810 (71,81%)** declaram não possuir renda própria. | Ambos os percentuais usam **4.810.772 registros de PARTICIPANTES**, com respostas válidas em todos eles. São inscritos, não famílias únicas nem somente pessoas que compareceram. |

## O que podemos concluir

A participação diminui no segundo dia, embora a maior parte dos presentes no primeiro retorne. As notas apresentam distribuições diferentes por área, região e rede, que precisam ser lidas com seus tamanhos de grupo e critérios de inclusão. O perfil econômico mostra concentração nas faixas inferiores de renda familiar entre os inscritos divulgados.

Essas são descrições da base publicada. Elas não demonstram causas para ausência ou diferenças de desempenho. A informação escolar cobre apenas parte dos registros. E **não é possível cruzar renda e nota individualmente em 2025**: PARTICIPANTES e RESULTADOS não têm chave comum. Portanto, a análise econômica permanece independente.

O fechamento cobre a primeira visão de cada tema. Detalhamento municipal e redação por local ou rede não fazem parte desta entrega. A expansão temporal está planejada para começar por 2024 e depois 2023; a relação renda × desempenho será investigada em 2023, cuja estrutura permite essa análise, após validar suas regras.

## Materiais e origem dos números

- [Apresentação completa](visao_geral_2025.ipynb), com tabelas e gráficos.
- [Roadmap da fase 2](../docs/ROADMAP_FASE_2.md) e [auditoria temporal](../docs/viabilidade_temporal_2010_2025.md).
- [Fluxograma editável em SVG](graficos/fluxograma_fase_1_2025.svg) e [origem dos assets](assets/fluxograma/FONTES.md).

Números conferidos em 30/09/2026 nos agregados existentes, sem reprocessar microdados: `desempenho_2025.csv`; `participacao_2025_dias.csv` e `participacao_2025_transicoes.csv`; `local_prova_2025_participacao.csv` e `local_prova_2025_desempenho.csv`; `rede_escolar_2025_cobertura.csv` e `rede_escolar_2025_desempenho.csv`; `redacao_2025_final.csv` e `redacao_2025_competencias.csv`; `perfil_economico_2025.csv`, todos em `analitica/`. Renda até R$ 3.036 corresponde às categorias A–D; cobertura de rede soma as quatro categorias válidas. Percentuais foram arredondados para duas casas e medianas por área para uma.
