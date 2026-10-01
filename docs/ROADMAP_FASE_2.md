# Roadmap fase 2

Planejamento · atualizado em 01/10/2026. A fase 1 (POC 2025) está concluída no escopo atual. A fase 2 foi iniciada: **participação entre dias de 2024 implementada e comparada com 2025**; os outros cinco temas de 2024 não foram iniciados. A sequência abaixo não estabelece prazos.

| Etapa | Entrega esperada | Critério para avançar | Situação |
| --- | --- | --- | --- |
| 1. Fechar 2025 | Resumo dos seis temas, apresentação e fluxograma do processo. | Resultados e limites documentados com os agregados existentes. | Concluída no escopo atual |
| 2. Incorporar 2024 primeiro | Reproduzir os seis temas de 2024 e consolidar a comparação com 2025, começando pela POC 2.1 de participação entre dias. | Validar cabeçalhos, dicionário, tipos, status, renda, cobertura e denominadores. A estrutura é semelhante à de 2025, mas não se presume compatibilidade total. | Em andamento — etapa 2.1 concluída; cinco temas não iniciados |
| 3. Incorporar 2023 | Adaptar o arquivo integrado ao conjunto de indicadores. | Validar unidade de análise, chave, elegibilidade e mudanças do questionário; renda familiar é Q006, não Q007. | Planejada |
| 4. Explorar renda × desempenho em 2023 | Comparação descritiva das notas por faixa de renda familiar. | Definir presentes/notas elegíveis, categorias, ausências e tamanho dos grupos; sem inferência causal. | Planejada — depende da etapa 3 |
| 5. Reutilizar e comparar edições | Componentes comuns e comparações de 2023–2025 justificadas. | Manter regras específicas por edição e comparar somente conceitos/populações compatíveis. Não reunir pessoas pelo identificador entre anos. | Planejada |
| 6. Expandir a história por regimes | Incluir edições anteriores em grupos documentados na auditoria. | Tratar mudanças de dias em 2017, status de redação, renda e cobertura; resolver a escala das competências 2010–2011 antes de compará-las. | Planejada |
| 7. Consolidar o case e a apresentação | Narrativa do problema, decisões, evidências e evolução do projeto. | Conectar resultados às perguntas e explicitar o alcance das comparações. | Planejada |

## Etapa 2.1 — POC de participação entre dias em 2024

**Situação: concluída em 01/10/2026.** O objetivo completo da etapa 2 é reproduzir os seis temas de 2024 e consolidar sua comparação com 2025. Começar pela participação entre dias permite conferir a reutilização em um recorte pequeno.

| Passo | Trabalho realizado na etapa 2.1 |
| --- | --- |
| Confirmar campos e regras | Usar a auditoria temporal e a documentação de 2024 para confirmar identificador, quatro presenças e pares por dia. |
| Preparar a entrada mínima | Edição, identificador e quatro presenças; preservar os arquivos raw. |
| Reutilizar o cálculo | Parametrizar ano e caminhos somente onde necessário, mantendo as regras confirmadas. |
| Conferir consistência | Verificar totais, códigos, pares e nulos; reconciliar contagens e preservar os resultados de 2025. |
| Organizar indicadores | Reunir indicadores de 2024 e 2025 com coluna de edição, sem exigir uma tabela física com todos os registros individuais. |
| Apresentar e comparar | Visão simples de 2024 e comparação com 2025: contagens, taxas por dia, permanência e diferenças em pontos percentuais, com denominadores explícitos. |

**Critério de conclusão:** POC de 2024 reprodutível, contagens reconciliadas, resultados de 2025 inalterados e visual comparativo conferido. Os outros cinco temas de 2024 serão incrementos posteriores e não foram iniciados. Critério atendido neste incremento: 4.332.944 registros preservados, 32 controles aprovados, regressão de 2025 sem divergência e gráficos conferidos. [Execução](../notebooks/08_participacao_2024.ipynb), [apresentação comparativa](../apresentacao/participacao_2024_2025.ipynb) e [resumo da entrega](../apresentacao/RESUMO_PARTICIPACAO_2024_2025.md).

## Dois caminhos de análise

**2024–2025:** resultados e perfil econômico permanecem independentes. Não há chave individual comum entre PARTICIPANTES e RESULTADOS. Uma comparação temporal pode apresentar ambos os temas, mas filtros de renda não devem ser aplicados às notas dessas edições.

**2023:** o arquivo principal reúne resultados e questionário. Isso permite investigar renda × desempenho após validar os campos e o recorte. Essa possibilidade não cria uma ligação individual com 2024 ou 2025.

## Como evoluir

Reutilizar a abordagem incremental da fase 1: confirmar a pergunta, ajustar o contrato, validar em recorte pequeno e só depois ampliar. Preservar os dados originais e os indicadores de 2025 como referência. Unir edições por entidade e por campos explicitamente harmonizados, mantendo o ano e a origem.

A expansão histórica seguirá a [auditoria de 2010–2025](viabilidade_temporal_2010_2025.md), em vez de supor que todos os arquivos têm o mesmo significado. Faixas monetárias mudam por ano; renda nominal, múltiplos do salário mínimo e poder de compra não são medidas equivalentes.

O próximo trabalho é acordar o próximo dos cinco temas restantes de **2024**, após a participação entre dias concluída. Nenhum outro tema foi iniciado automaticamente. Aprofundamentos adicionais serão decididos quando necessários, sem ampliar agora o escopo.

Referências: [fechamento de 2025](../apresentacao/RESUMO_FASE_1_2025.md), [roadmap e histórico da fase 1](ROADMAP.md) e [apresentação atual](../apresentacao/visao_geral_2025.ipynb).
