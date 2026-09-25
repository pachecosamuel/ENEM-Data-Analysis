# Contrato analítico — local de prova 2025

24/09/2026. Pergunta: como presença e desempenho variam entre os lugares de aplicação?

## Unidade, fonte e cobertura

Um registro de RESULTADOS 2025; todos os registros da trusted v3. Aplicação da prova, **não residência ou escola**. Dicionário local, aba RESULTADOS_2025: CO_MUNICIPIO_PROVA (linha 81), NO_MUNICIPIO_PROVA (86), CO_UF_PROVA (87) e SG_UF_PROVA (114). Os quatro campos são VARCHAR na trusted, sem perder zeros à esquerda; vazios viram nulos e espaços externos são removidos, como no contrato técnico. Não converter código para número ou normalizar sigla para esconder problemas.

UF e Grande Região vêm da [API oficial de localidades do IBGE](https://servicodados.ibge.gov.br/api/v1/localidades/estados?orderBy=id), obtida diretamente em 24/09/2026 e congelada em `uf_regiao_ibge.json`. São 27 UFs e cinco regiões. O processamento é offline/reproduzível; auditoria registra a fonte, a consulta, o mapeamento e seu hash. Região é derivada na análise, não adicionada ao raw/trusted.

Só atribuir UF/região quando **código e sigla existem na referência e concordam**. Campo faltante, código/sigla desconhecido ou discordância permanecem na fonte, são contados por motivo e integram o grupo **Não classificada** em ambas as granularidades; nada é excluído do nacional. Preservar pares originais na auditoria. Não inferir UF por sigla isolada, município, residência ou escola. Município: auditar código/nome nulo, formato diferente de sete dígitos, prefixo divergente do código UF e múltiplos nomes para mesmo código. Isso não certifica existência em cadastro municipal histórico; indicadores e rankings municipais ficam para incremento posterior.

## Presença e permanência

Reutilizar `participacao.agregar_combinacoes` e sua validação. Dia 1 LC/CH, dia 2 CN/MT. Presença completa exige ambos=1; ausência completa ambos=0; eliminação completa ambos=2; mistos, nulos e inválidos separados. Sem nota não determina presença.

Em cada região/UF: total de registros local; contagens das seis situações por dia; presença completa/total local ×100; presença nos dois dias/presentes completos no dia 1 ×100 (permanência); transições completas 6×6 com contagens e denominadores local e de origem. Denominador zero retorna nulo. Volume, taxa de presença e permanência respondem perguntas distintas.

Top 3 somente de **UFs por taxa de presença completa no dia 2**, com numerador e total próprio visíveis. UFs reconhecidas com total>0; excluir Não classificada do ranking, mantendo-a nos totais. Ordenar a fração exata, sem arredondamento; empate por sigla crescente. Mostrar três maiores e três menores. Não fazer top 3 das cinco regiões nem ranking municipal sem controle de tamanho. O ranking de notas fica fora desta primeira visão; comparar distribuições regionais separadamente em cada área.

## Desempenho

Para cada uma das quatro áreas, reutilizar o filtro nacional **presença=1 e nota não nula naquela área**, incluindo zero, sem exigir presença em outra área. Exportar total local, n elegível, cobertura, zeros, soma das notas, média, mediana, Q1/Q3 e extremos observados; presentes sem nota e notas fora dos presentes auditados. Quantil contínuo DOUBLE tipo 7, igual ao nacional.

Regiões, UFs e Brasil são calculados **diretamente sobre registros individuais no DuckDB**, uma área por vez. Nunca média não ponderada das médias das UFs ou mediana das medianas. Quantis regionais não podem ser reconstruídos a partir de quartis das UFs. Populações elegíveis diferem por área. Dispersão não equivale a qualidade educacional, dificuldade ou efeito causal do território. Nenhuma nota global, imputação, comparação equivalente de escalas TRI, join com PARTICIPANTES, renda ou escola.

## Reconciliação e entrega

- Soma regiões e UFs (inclui Não classificada) = Brasil para totais, seis status por dia, transições, n elegível, zeros e somas de notas. Conferir UFs dentro de cada região. Médias compatíveis com soma/n, quantis ordenados e vazios nulos.
- Comparar nacional territorial aos indicadores nacionais já aprovados; comparar os 17 campos anteriores da trusted exatamente por chave e os CSVs/PNGs anteriores por hash após renovar auditorias.
- Esquema v3 completo, chave/ano válidos, hashes da fonte antes/depois, raw imutável; backup antes da troca validada e atômica.
- `local_prova_referencia.py` cobre referência/cobertura; `local_prova.py` cálculo; `local_prova_execucao.py` I/O; `local_prova_graficos.py` gera somente o PNG de notas regionais; n elegível permanece nas tabelas. O visual de presença regional foi retirado, sem excluir cálculos ou agregados de participação. DuckDB 256 MB/uma thread, apenas agregados para Pandas. Sem dependências adicionais.
- `notebooks/05_local_prova.ipynb` executa e audita. Quatro CSVs compactos em analitica, auditoria/resumo em reports; apresentação lê agregados e verifica hashes, sem ETL. Primeira visão: cinco regiões, UFs e top 3 de taxa do dia 2 em tabela. Redação por local e detalhamento de desempenho municipal ficam no backlog.
