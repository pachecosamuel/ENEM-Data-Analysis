# Rede escolar — contrato analítico 2025

24/09/2026. Pergunta: **entre os registros com informação escolar, como as distribuições variam por rede?** Unidade: registro de RESULTADOS, com chave NU_SEQUENCIAL; não há join com PARTICIPANTES, renda, escolas individuais ou outras edições.

## Fonte, campo e cobertura

Trusted v4: acrescenta somente `TP_DEPENDENCIA_ADM_ESC` (TINYINT) aos 21 campos anteriores. Dicionário local `raw/microdados_enem_2025/microdados_enem_2025/DICIONÁRIO/Dicionário_Microdados_Enem_2025.xlsx`, aba RESULTADOS_2025, linhas 70–73: 1 Federal, 2 Estadual, 3 Municipal, 4 Privada. Federal é pública; nesta entrega as quatro categorias permanecem separadas, sem agregado pública/privada. Nulo significa informação indisponível, sem imputação; qualquer código fora de 1–4 bloqueia trusted e análise.

O `LEIA-ME E DOCUMENTOS TÉCNICOS/Leia_Me_Enem_2025.docx`, de abril/2026, descreve obtenção do código escolar no Censo Escolar 2025 pelo CPF, selecionando etapas de **possíveis concluintes**: 27, 28, 29, 32, 33, 34, 37, 38 e 71 (ensino médio regular, integrado, normal/magistério e EJA). Em múltiplas matrículas em escolas distintas, há preferência por rede pública, ensino regular, maior carga horária e mesmo município de residência declarado. Essa seleção limita a representatividade. Não significa que todos concluíram o ensino médio, nem que os registros sem rede pertencem à rede privada ou pública.

O mesmo Leia_Me descreve mascaramento do código de escolas com menos de dez participantes e desaconselha rankings de escolas. `CO_ESCOLA` não foi incorporado: não é necessário para comparar dependência administrativa. A descrição do vínculo ao Censo vem do Leia_Me, não da nota de rodapé numerada do campo CO_ESCOLA no dicionário, cujo texto nesta edição trata da aplicação BAM/COP30.

A leitura estrita integral do raw encontrou 4.810.772 registros: 1.739.028 com rede válida (36,148626%) e 3.071.744 nulos (63,851374%); zero inválidos. Contagens: Federal 74.649, Estadual 1.382.565, Municipal 9.015, Privada 272.799. A cobertura publicada sempre usa a base inteira como denominador. Trata-se de uma subpopulação selecionada, não de todos os inscritos ou de todos os alunos de cada rede.

## Elegibilidade, medidas e denominadores

Em cada rede e área (CN, CH, LC, MT), aplicar exatamente `TP_PRESENCA_{area}=1 AND NU_NOTA_{area} IS NOT NULL`. Zero é nota válida. Ausentes, eliminados e presentes sem nota não entram nos quantis/médias; continuam na contagem de base da rede e nos diagnósticos. Não se exige presença nas demais áreas. Registros sem rede integram a cobertura, mas não as quatro distribuições comparadas.

Reutilizar `calcular_desempenho` nacional sobre uma view filtrada por rede: n, zeros, média, mínimo/máximo observados, Q1, mediana e Q3. Quantis contínuos sobre DOUBLE, tipo 7: h=(n−1)p, interpolação linear. Não calcular média de médias/medianas. Base vazia: contagens zero, medidas nulas. A soma das quatro bases de rede mais nulos deve coincidir com a base total. Os mesmos controles nacionais reconciliam categorias, notas e elegíveis em cada recorte.

## Saídas e leitura

- `analitica/rede_escolar_2025_cobertura.csv`: cinco linhas (quatro redes e sem informação), n e percentual da base total.
- `analitica/rede_escolar_2025_desempenho.csv`: 16 linhas, uma por rede/área, n e estatísticas sem arredondamento editorial.
- `reports/validacao_rede_escolar_2025.json`: esquema, hash trusted antes/depois, hashes CSV, cobertura, controles e resultados.
- `apresentacao/graficos/rede_escolar_notas_2025.png`: um gráfico com quatro painéis; Q1–Q3, mediana e n elegível em ordem dos códigos, sem ordenar por nota.
- `notebooks/06_rede_escolar.ipynb`: processamento; `apresentacao/visao_geral_2025.ipynb`: capítulo após local, lê saídas auditadas e confere hashes, sem ETL.

Execução limitada a 256 MB/uma thread no DuckDB. Pandas recebe só agregados. A migração compara os 21 campos anteriores por chave em toda a base, preserva backup e renova as auditorias anteriores; CSVs/PNGs antigos devem permanecer idênticos. Três testes novos cobrem nulos/inválidos, zero/ausência, n/quartis manuais e proteção dos 21 campos. A suíte anterior continua obrigatória.

## Interpretação e próximo passo

Começar pela cobertura. Comparar distribuições descritivamente, com sobreposição dos quartis e tamanhos de base visíveis. A rede municipal tem base muito menor; diferenças não identificam efeito da escola, qualidade, desempenho de uma escola individual ou causas. Rede não é proxy de renda. Não há ajuste de composição, seleção ou participação. Redação por rede e agregação pública/privada ficam fora deste incremento.

Próximo passo independente: perfil de renda em PARTICIPANTES. Não cruzar renda com notas individuais de RESULTADOS sem chave comum válida.
