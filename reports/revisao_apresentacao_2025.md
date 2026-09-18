# Revisão de organização e apresentação

17/09/2026 · primeira sprint da POC · sem nova análise entre dias ou geográfica.

## O que mudou

Antes, `src/` reunia funções, notebooks e roadmap; gráficos ficavam em `reports/graficos/`. Agora:

- `src/`: código reutilizável, com `__init__.py` apenas para identificar o pacote. Cálculo, I/O e gráficos continuam em módulos separados.
- `notebooks/`: notebooks 01 (carga) e 02 (indicadores).
- `docs/`: contratos e ROADMAP.
- `apresentacao/`: [notebook narrativo](../apresentacao/visao_geral_2025.ipynb), orientação de leitura e [PNG](../apresentacao/graficos/).
- `reports/`: evidências de validação e resultados; `scripts/`: executor de notebooks.
- `raw/`, `trusted/`, `analitica/`, `.venv`, `.env` e Git permanecem nos mesmos locais.

Mapa na raiz e dois README de orientação (processamento e apresentação) evitam repetir documentação em todas as pastas. Não houve git init, repositório aninhado, instalação de dependências, commit ou push.

## Escolha de escala

A escala compartilhada cobre todos os mínimos e máximos **observados entre presentes com nota na própria área**, com pequena margem visual. As contagens saíram do eixo Y e permanecem na tabela. Áreas por extenso, três elementos de legenda: mínimo–máximo observado, 50% centrais e mediana. O gráfico mostra valores apenas dos extremos e da mediana; Q1/Q3 e média ficam disponíveis na tabela. Não usa bigodes de Tukey.

| Área | Mínimo observado | Máximo observado |
| --- | ---: | ---: |
| Ciências da Natureza | 0,0 | 858,7 |
| Ciências Humanas | 0,0 | 856,4 |
| Linguagens e Códigos | 0,0 | 794,5 |
| Matemática | 0,0 | 980,3 |

Zeros válidos foram mantidos e nenhuma nota foi dividida por dez. Média, mediana, Q1/Q3 e populações permanecem iguais à entrega anterior. Esses extremos descrevem a base divulgada; não são os limites teóricos das provas. A TRI não impõe faixa universal 0–1000: os limites dependem dos itens. Esta base não permite estimá-los, e a origem dos zeros não foi investigada. [Guia oficial do Inep](https://www.gov.br/inep/pt-br/centrais-de-conteudo/acervo-linha-editorial/publicacoes-institucionais/avaliacoes-e-exames-da-educacao-basica/entenda-a-sua-nota-no-enem-guia-do-participante).

## Validação

Onze testes passaram, incluindo extremos dentro da população elegível (nota 900 fora dos presentes não entra no máximo), zero, nota acima de 1000 em fixture, caso vazio/unitário, ordem, interpolação e exportação CSV/JSON. O teste de integração confere caminhos em notebooks/apresentacao e integridade da fonte.

Notebook 02 e apresentação executados inteiros em kernels novos. Notebook 01: apenas preparação/imports/caminhos verificados após movimento; carga completa não repetida. PNGs inspecionados visualmente, sem sobreposição de rótulos. Links locais conferidos. SHA-256 da trusted permanece `e62b1cb8eedb9dac27d457fcc03c8f7479faacf1ec4b4ecb8011be28613981f3`; `.env` também intacto. O Git estava limpo no diagnóstico. Movimentos limitados a notebooks, roadmap e PNGs; não houve remoção de trabalho do usuário.

## Retomada

[Roadmap](../docs/ROADMAP.md): esboçar e validar contrato da participação entre dias antes de calcular a segunda pergunta. Backlog registra top 3 por presença regional (definir taxa versus volume), notas por região de aplicação e renda independente. Sem cruzamento individual renda–nota em 2025. Narrativa factual, pequenas representações visuais e evolução controlável orientam as próximas iterações.

A cópia externa de apresentação contém notebook com saídas e PNGs finais; para reexecutar, usar o notebook canônico no projeto com sua `.venv`.
