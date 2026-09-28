# Viabilidade temporal do ENEM 2010–2025

Auditoria exploratória — 28/09/2026 — inventário refeito após a reposição dos arquivos.

## Parecer

**É viável construir a série 2010–2025 para os seis temas, com adapters por edição e limites explícitos de comparação.** Todas as 16 edições estão presentes e foram examinadas por cabeçalho, dicionário e LeiaMe. Esta versão substitui integralmente a conclusão anterior sobre arquivos ausentes.

Participação, quatro notas objetivas, redação e local de aplicação têm campos em todos os anos. Rede escolar também tem campo, mas sua cobertura e origem não podem ser consideradas constantes. Renda familiar existe em todas as edições, com mudanças de pergunta, categorias e limites monetários. O indicador atual de possuir renda não tem equivalente direto identificado em 2012–2023; 2010–2011 possuem faixas de renda própria, uma medida diferente.

**Uma tabela única com filtros globais de renda sobre notas não é viável em 2024–2025.** PARTICIPANTES e RESULTADOS não possuem chave comum, conforme os LeiaMe, p. 7, e as notas dos dicionários RESULTADOS: linha 145 em 2024 e 313 em 2025. A proposta é manter fatos de resultados e de perfil independentes. Não relacionar por ordem, semelhança de identificadores ou atributos pessoais/geográficos.

A viabilidade estrutural tem confiança alta. A comparabilidade estatística é condicionada; esta auditoria não mediu cobertura integral, unicidade ou distribuições. Não houve implementação de ETL nem alteração dos contratos, dados ou apresentação da POC.

## Evidência física e documental

Foram inventariados 35 CSVs: 18 arquivos principais, 16 de itens e um questionário complementar de 2022. Leitura limitada ao cabeçalho e duas linhas por CSV: todos usam ponto e vírgula e as duas linhas têm a largura do cabeçalho. Foram lidos os 16 dicionários XLSX e os 16 LeiaMe; consultados INPUTS e documentos técnicos pertinentes. As amostras não foram exportadas.

De 2010 a 2023 há um arquivo principal por edição; em 2024–2025 há PARTICIPANTES e RESULTADOS. O arquivo de 2016 está em minúsculas. De 2023 a 2025 existe um nível adicional de pasta. Descobrir arquivos pelo inventário, sem construir caminhos rígidos a partir do ano.

| Ano | Campos principais | Dia 1 / dia 2 | Renda familiar (categorias) | Renda própria/possui renda | Linhas de status da redação |
|---|---|---|---|---|---|
| 2010 | 105 | CH+CN / LC+MT | Q04 (8) | Q05 | 138–142 |
| 2011 | 128 | CH+CN / LC+MT | Q004 (11) | Q005 | 139–142 |
| 2012 | 115 | CH+CN / LC+MT | Q003 (17) | — | 133–141 |
| 2013 | 130 | CH+CN / LC+MT | Q003 (17) | — | 136–145 |
| 2014 | 130 | CH+CN / LC+MT | Q003 (17) | — | 138–147 |
| 2015 | 105 | CH+CN / LC+MT | Q006 (17) | — | 168–177 |
| 2016 | 105 | CH+CN / LC+MT | Q006 (17) | — | 188–196 |
| 2017 | 78 | LC+CH / CN+MT | Q006 (17) | — | 166–173 |
| 2018 | 78 | LC+CH / CN+MT | Q006 (17) | — | 167–174 |
| 2019 | 76 | LC+CH / CN+MT | Q006 (17) | — | 171–178 |
| 2020 | 76 | LC+CH / CN+MT | Q006 (17) | — | 198–205 |
| 2021 | 76 | LC+CH / CN+MT | Q006 (17) | — | 214–221 |
| 2022 | 76 | LC+CH / CN+MT | Q006 (17) | — | 187–194 |
| 2023 | 76 | LC+CH / CN+MT | Q006 (17) | — | 184–191 |
| 2024 | 38 / 42 | LC+CH / CN+MT | Q007 (17) | Q006 | 131–138 |
| 2025 | 38 / 70 | LC+CH / CN+MT | Q007 (17) | Q006 | 243–250 |

As linhas são da aba principal até 2023 e de RESULTADOS em 2024–2025. Renda nas duas últimas edições vem de PARTICIPANTES. A tabela sintética deve ser lida com a [matriz por requisito](matriz_viabilidade_temporal_2010_2025.csv), o [crosswalk com 340 correspondências e referências de linhas](crosswalk_temporal_2010_2025.csv), as [categorias originais de renda](faixas_renda_temporal_2010_2025.csv) e os [códigos originais de redação](status_redacao_temporal_2010_2025.csv).

O [inventário JSON](inventario_temporal_2010_2025.json) registra caminhos, tamanhos, cabeçalhos, hashes dos cabeçalhos e documentos, delimitadores e metadados das amostras. Não contém hash integral dos CSVs. O encoding de leitura da amostra não certifica o encoding integral: Latin-1 aceita qualquer byte. Os INPUT_R de 2024–2025 declaram Latin-1; o de 2023 não declara encoding e sua amostra não é UTF-8 válida. Cada adapter deve validar encoding e ausência por edição, sem inferi-los de duas linhas. Preservar identificadores como texto e vazio como ausência, não como zero.

Os LeiaMe documentam republicações simplificadas, inclusive nas edições antigas: retirada de CO_ESCOLA e de informações de residência/nascimento e substituição de idade por faixa etária. Portanto, o schema auditado é o dos pacotes atuais no disco, não necessariamente o da publicação original de cada ano. Congelar a versão e os hashes documentais ao implementar.

## 1. Participação

TP_PRESENCA_CN, CH, LC e MT existem em todas as edições. Os dicionários registram 0=faltou, 1=presente e 2=eliminado. O crosswalk fornece a linha de cada campo por ano. Ausência e valor desconhecido devem continuar categorias de qualidade distintas.

Em **2010–2016**, dia 1 corresponde a CH+CN e dia 2 a LC+MT, com redação no segundo dia. Em **2017–2025**, dia 1 corresponde a LC+CH e dia 2 a CN+MT, com redação no primeiro. Evidência: LeiaMe 2010 p. 7; 2011 p. 6; 2012 p. 7; 2013–2016 p. 5; 2017 p. 6; 2018 p. 5; 2019–2025 p. 6. Alguns LeiaMe narram primeiro o arranjo histórico anterior: usar o parágrafo da edição, não a primeira ocorrência de “primeiro dia”.

A regra de combinação da POC pode ser preservada após selecionar os pares corretos: código inválido, ausência, par coincidente e par misto precisam ser distinguíveis. Não classificar presença diária por uma única área nem converter eliminado em faltoso. Comparar taxas com denominadores declarados: registros publicados, presenças por área e presenças em ambos os dias. A mudança da composição dos dias impede interpretar toda variação diária como mudança exclusiva de comportamento.

## 2. Notas objetivas

NU_NOTA_CN, CH, LC e MT estão disponíveis em todos os cabeçalhos e dicionários. A estrutura permite o mesmo conjunto de estatísticas por área, ano e recortes autorizados. A elegibilidade proposta mantém presença=1 e nota não nula; zero não é automaticamente dado ausente. Registrar perdas por presença, nota ausente e valor inválido separadamente.

As notas são proficiências estimadas pela TRI, não percentuais de acerto. O documento técnico `enem_procedimentos_de_analise.pdf`, p. 22, nos pacotes, descreve a transformação da escala. Não impor automaticamente limites 0–1000 às quatro provas nem compará-las como se representassem uma única competência. Manter unidade e área originais, sem normalização min–max anual que destrua a interpretação temporal.

A estrutura comum não garante equivalência de populações: inscrição, seleção para comparecimento, treineiros, aplicações especiais, pandemia e exclusões por anonimização mudam os grupos. Uma tendência descritiva dos participantes publicados não estima, por si só, evolução da aprendizagem de todos os estudantes. Exibir N elegível, ausências e distribuição, além da média. A edição 2020 ocorreu em 2021: o eixo principal deve ser edição, não ano civil da aplicação (LeiaMe 2020, p. 6).

## 3. Redação

Há nota final e cinco competências em todos os anos. Entretanto, **aplicar TP_STATUS_REDACAO=1 a toda a série estaria errado**:

| Período | Códigos e interpretação relevante |
|---|---|
| 2010 | B=branco, D=desconsiderada, F=faltou, N=anulada, P=presente |
| 2011 | B=branco, F=faltoso, N=anulada, P=presente |
| 2012 | P=presente, B=branco, T=fuga, N=anulada, I=insuficiente, A=tipo textual, H=direitos humanos, C=cópia, F=ausente |
| 2013–2014 | 1=branco; 7=presente e texto conforme; 6=ausente; demais motivos em códigos 2,3,4,5,9,10,11 |
| 2015 | 1=sem problemas; 2–9=motivos; inclui 5=direitos humanos e 98=regra específica do edital |
| 2016 | 1=sem problemas; motivos 2–9, inclusive 5 |
| 2017–2025 | 1=sem problemas; motivos 2,3,4,6,7,8,9; não há categoria 5 no dicionário |

Preservar código, rótulo e versão do dicionário. Construir categorias semânticas explícitas e manter “desconsiderada” e o código 98 separados, sem forçar equivalências. Nos anos 2010–2012, “presente” não tem exatamente o mesmo enunciado que “sem problemas”: eventual equivalência para elegibilidade das competências precisa de validação adicional. O CSV anexo traz todas as 129 categorias anuais e suas linhas.

A nota final e a análise das competências podem ter universos diferentes: reproduzir separadamente a regra da POC de nota final não nula e a regra de competências completas, associada ao status semanticamente elegível. Não tratar branco/anulação/ausência como um único zero.

Escalas e correção também merecem versionamento. O Edital 2011, p. 10, menciona escala total 0–1000 e discrepância de 300 pontos. O Edital 2012, p. 16, explicita total 0–1000, competências 0–200 e discrepância total superior a 200; o de 2013, p. 17, reduz esse critério para mais de 100. Isso já demonstra mudança do processo de correção. Os dicionários sozinhos não informam limites de escala para todos os anos. **A equivalência exata da escala armazenada das competências de 2010–2011 permanece pendente; não aplicar multiplicadores presumidos.** Uma implementação pode disponibilizar valores originais dessas edições e bloquear sua agregação temporal de competências até resolver essa pendência.

Em 2025, as competências finais são descritas como médias dos avaliadores válidos (D2025, RESULTADOS, linhas 251–255). As 28 colunas adicionais por avaliador não substituem os sete campos agregados usados pela POC. Não confundir ausência dessas colunas nos CSVs principais antigos com inexistência de suplementos oficiais: estes não foram auditados.

## 4. Local de aplicação

CO_MUNICIPIO_PROVA, NO_MUNICIPIO_PROVA, CO_UF_PROVA e SG_UF_PROVA existem em todas as edições. Usar exclusivamente essa família para localização da prova. CO_MUNICIPIO_ESC/UF_ESC descrevem a escola e não podem preencher local de prova ausente. Não reconstruir residência a partir de nenhum dos dois.

Guardar códigos como texto, validar correspondência UF–município com referência adequada à época e registrar códigos sem correspondência. A região pode ser derivada de UF válida. Mudanças territoriais e nomes exigem dimensão geográfica versionada; município com mesmo nome não é chave. Nos dois fatos de 2024–2025 existem campos geográficos próprios, permitindo recortes agregados independentes, sem criar ligação individual entre fatos.

## 5. Rede escolar

TP_DEPENDENCIA_ADM_ESC mantém categorias 1=federal, 2=estadual, 3=municipal e 4=privada nos 16 dicionários. Isso sustenta a segmentação estrutural. TP_ESCOLA e questões sobre trajetória pública/privada não são substitutos: têm categorias e conceitos diferentes.

Nos pacotes anteriores a 2024, os LeiaMe frequentemente descrevem a escola declarada pelo participante; essa descrição não comprova um procedimento homogêneo de preenchimento, vinculação ou cobertura. Não estender retroativamente a regra de 2024–2025 a todos os anos. A proporção de rede preenchida deve ser medida em cada edição e denominador de análise, incluindo “não informado”. Nunca interpretar rede ausente como privada ou escola inexistente.

Em 2024–2025, o LeiaMe p. 7–8 documenta vínculo por CPF ao Censo Escolar da edição para possíveis concluintes, com etapas 27,28,29,37,38,71,32,33,34; múltiplas matrículas recebem prioridades (pública, regular, maior duração e município). O código de escola é mascarado em escolas com menos de dez participantes. Isso não autoriza concluir que todos os campos de dependência desses registros estejam ausentes, nem gerar ranking escolar. A seleção deve constar na interpretação de qualquer tendência por rede. Cobertura anual integral não foi medida nesta auditoria.

## 6. Perfil econômico

O crosswalk familiar é Q04 em 2010, Q004 em 2011, Q003 em 2012–2014, Q006 em 2015–2023 e Q007 em 2024–2025. Em 2012, o dicionário escreve Q3, mas cabeçalho e INPUT_R/SAS/SPSS confirmam Q003 e a mesma pergunta de renda. As 280 linhas do anexo de renda incluem rótulo literal, pergunta, categoria, edição e fonte, inclusive renda própria onde disponível.

Em 2010 há oito categorias: H significa nenhuma renda; A é até um salário mínimo. Em 2011 há onze: A=nenhuma, B=até um mínimo; os demais intervalos são diferentes dos posteriores. De 2012 a 2025 há 17 categorias A–Q, mas valores nominais mudam anualmente. Os valores-base da faixa até um mínimo são: 510; 545; 622; 678; 724; 788; 880; 937; 954; 998; 1045; 1100; 1212; 1320; 1412; 1518 reais, respectivamente. São limites publicados nos questionários; não substituem uma série externa auditada do salário mínimo.

**Não unir apenas a letra da resposta.** Preservar edição, pergunta, código e limites publicados. Uma divisão comum “sem renda / até um mínimo / acima de um mínimo” é candidata a comparação agregada, após resolver fronteiras ambíguas dos primeiros anos. A categoria ampla de 2010 entre um e três mínimos não permite recuperar retrospectivamente renda até 1,5 mínimo. Não repartir uma faixa sem informação, nem atribuir ponto médio como renda individual observada. A categoria superior é aberta.

O texto também muda: 2010–2011 menciona pessoas que moram com o participante; 2012–2023 fala em somar familiares; 2024–2025 volta a explicitar pessoas que moram com ele. Conservar essa distinção de unidade de referência. Valores nominais, múltiplos do mínimo e poder de compra constante são três medidas diferentes. Deflação requer índice, período-base e regra para intervalos; não elimina a incerteza dentro de cada faixa nem torna os grupos automaticamente comparáveis.

Renda própria: Q05/Q005 em 2010–2011 informa faixas individuais. Pode-se propor um indicador derivado de renda positiva, identificando-o como derivado. Q006 em 2024–2025 pergunta diretamente se possui renda (A=não, B=sim). Não identificamos equivalente direto em 2012–2023; não inferir esse indicador de trabalho ou renda familiar. Particularmente, Q007 em 2023 é empregado doméstico, não renda familiar, e Q006 em 2023 é renda familiar, não possuir renda.

## Inconsistências documentais e decisões conservadoras

- D2010, faixa F de Q04/Q05, escreve 12–15 mínimos e R$ 6.210,00 como início; 12×510 seria 6.120. Guardar literal e marcar divergência.
- D2015, Q006, faixas D/E usam 1.572,00/1.572,01, embora 2×788 seja 1.576. Não gerar limites exclusivamente por multiplicação.
- D2013–2014, faixa superior de renda, têm redação de fronteira monetária que merece revisão; preservar rótulo original.
- D2010 e D2012, notas de faixa etária, citam 31/12/2020. É inconsistência documental fora do núcleo de seis requisitos, relevante se idade entrar no painel.
- L2022, p. 6, descreve a edição 2022 mas escreve “13 e 20 de novembro de 2021”. Não extrair calendário automaticamente desse trecho.
- D2025 apresenta remissão de rodapé pouco clara em CO_ESCOLA; adotar a descrição de origem no LeiaMe p. 7–8.

Essas ocorrências reduzem a confiança em automatizar a documentação sem revisão, mas não invalidam a existência dos campos.

## Modelo canônico e painel propostos

Criar `fato_resultado` com edição, identificador local textual, fonte/versão, quatro presenças, quatro notas, status bruto e harmonizado da redação, nota final, cinco competências, geografia de aplicação e dependência escolar. Criar `fato_perfil` com edição, identificador local, fonte/versão, renda familiar original e suas faixas, renda própria original/derivada quando suportada e geografia disponível. A chave técnica deve incluir **edição + entidade + identificador**; validar unicidade posteriormente. NU_INSCRICAO é mascarado e não acompanha a mesma pessoa entre edições (notas dos dicionários).

De 2010 a 2023, os dois conjuntos podem ser projetados do arquivo único, preservando a possibilidade de análises conjuntas específicas dessas edições. Em 2024–2025 permanecem independentes. Não somar suas contagens como pessoas distintas nem usar o mesmo identificador sintético para forçar uma dimensão compartilhada.

Usar **UNION ALL por entidade**, após selecionar, tipar e renomear explicitamente os campos em adapters anuais. Não usar SELECT * ou deduplicação implícita de UNION; não realizar JOIN entre anos para formar um painel longitudinal. Arquivos ITENS_PROVA são outra granularidade; QUEST_HAB_ESTUDO de 2022 é questionário facultativo sobre estudos na pandemia (L2022 p. 6–8), fora dos seis requisitos, e não deve aumentar o número de registros principais por junção automática.

Campos não publicados recebem NULL e uma flag de disponibilidade; distinguir não publicado, não aplicável, não respondido, inválido e valor observado. Carregar versões dos mapas de presença/dia, status, renda e geografia. Preservar a rastreabilidade até campo e documento de origem.

O filtro de edição deve alcançar ambos os fatos; filtros de renda afetam o perfil e só podem afetar notas em uma visão explicitamente restrita às edições vinculáveis. Rede escolar pertence ao universo de resultados com cobertura própria. Mostrar ao usuário quais gráficos recebem cada filtro, os anos suportados, denominadores, exclusões e dados ausentes. Para competências 2010–2011, indicar pendência de harmonização. Gráficos de renda devem usar faixas comparáveis aprovadas ou painéis por edição, sem rótulos monetários fixos para toda a série.

## Próximo incremento recomendado

Implementar primeiro, em etapa separada, o núcleo de resultados 2017–2025 e renda familiar 2012–2025 com mapas anuais, sem ligação indevida dos fatos. Em seguida incorporar participação/notas/local/rede de 2010–2016 e as categorias de redação históricas; resolver a escala das competências 2010–2011 antes de habilitar comparações desse indicador. Renda 2010–2011 entra com categorias próprias e somente recortes comuns demonstráveis. Essa ordem reduz risco de adaptação e não significa que as edições antigas estejam ausentes.

Na implementação, realizar perfil de dados limitado e depois validação integral planejada: tipos, unicidade da chave, ano, códigos, ausências, consistência de pares e notas, cobertura por rede e geografia, e totais por denominador. A aprovação desta auditoria não equivale à aprovação dessas verificações. Não houve ETL, agregação histórica, varredura integral dos CSVs, instalação de dependências, commit ou push.

## Referências locais por edição

D = dicionário XLSX; L = LeiaMe PDF. O crosswalk e os anexos apontam aba e linha; as referências de páginas neste documento são páginas físicas do PDF. Os caminhos abaixo são relativos ao repositório; o inventário contém também os hashes documentais.

- **2010** — D: `raw/microdados_enem_2010/DICIONÁRIO/Dicionário_Microdados_Enem_2010.xlsx`; L: `raw/microdados_enem_2010/LEIA-ME E DOCUMENTOS TÉCNICOS/Leia-me_ENEM_2010.pdf`.
- **2011** — D: `raw/microdados_enem_2011/DICIONÁRIO/Dicionário_Microdados_Enem_2011.xlsx`; L: `raw/microdados_enem_2011/LEIA-ME E DOCUMENTOS TÉCNICOS/Leia_Me_Enem_2011.pdf`.
- **2012** — D: `raw/microdados_enem_2012/DICIONÁRIO/Dicionário_Microdados_Enem_2012.xlsx`; L: `raw/microdados_enem_2012/LEIA-ME E DOCUMENTOS TÉCNICOS/Leia_Me_Enem_2012.pdf`.
- **2013** — D: `raw/microdados_enem_2013/DICIONÁRIO/Dicionário_Microdados_Enem_2013.xlsx`; L: `raw/microdados_enem_2013/LEIA-ME e DOCUMENTOS TÉCNICOS/Leia_Me_Enem_2013.pdf`.
- **2014** — D: `raw/microdados_enem_2014/DICIONÁRIO/Dicionário_Microdados_Enem_2014.xlsx`; L: `raw/microdados_enem_2014/LEIA-ME e DOCUMENTOS TÉCNICOS/Leia_Me_Enem_2014.pdf`.
- **2015** — D: `raw/microdados_enem_2015/DICIONÁRIO/Dicionário_Microdados_Enem_2015.xlsx`; L: `raw/microdados_enem_2015/LEIA-ME e DOCUMENTOS TÉCNICOS/Leia_Me_Enem_2015.pdf`.
- **2016** — D: `raw/microdados_enem_2016/DICIONÁRIO/Dicionário_Microdados_Enem_2016.xlsx`; L: `raw/microdados_enem_2016/LEIA-ME e DOCUMENTOS TÉCNICOS/Leia-me_Enem_2016.pdf`.
- **2017** — D: `raw/microdados_enem_2017/DICIONÁRIO/Dicionário_Microdados_Enem_2017.xlsx`; L: `raw/microdados_enem_2017/LEIA-ME e DOCUMENTOS TÉCNICOS/Leia_Me_Enem_2017.pdf`.
- **2018** — D: `raw/microdados_enem_2018/DICIONÁRIO/Dicionário_Microdados_Enem_2018.xlsx`; L: `raw/microdados_enem_2018/LEIA-ME E DOCUMENTOS TÉCNICOS/Leia_Me_Enem_2018.pdf`.
- **2019** — D: `raw/microdados_enem_2019/DICIONÁRIO/Dicionário_Microdados_Enem_2019.xlsx`; L: `raw/microdados_enem_2019/LEIA-ME E DOCUMENTOS TÉCNICOS/Leia_Me_Enem_2019.pdf`.
- **2020** — D: `raw/microdados_enem_2020/DICIONÁRIO/Dicionário_Microdados_Enem_2020.xlsx`; L: `raw/microdados_enem_2020/LEIA-ME E DOCUMENTOS TÉCNICOS/Leia_Me_Enem_2020.pdf`.
- **2021** — D: `raw/microdados_enem_2021/DICIONÁRIO/Dicionário_Microdados_Enem_2021.xlsx`; L: `raw/microdados_enem_2021/LEIA-ME E DOCUMENTOS TÉCNICOS/Leia_Me_Enem_2021.pdf`.
- **2022** — D: `raw/microdados_enem_2022/DICIONÁRIO/Dicionário_Microdados_Enem_2022.xlsx`; L: `raw/microdados_enem_2022/LEIA-ME E DOCUMENTOS TÉCNICOS/Leia_Me_Enem_2022.pdf`.
- **2023** — D: `raw/microdados_enem_2023/microdados_enem_2023/DICIONÁRIO/Dicionário_Microdados_Enem_2023.xlsx`; L: `raw/microdados_enem_2023/microdados_enem_2023/LEIA-ME E DOCUMENTOS TÉCNICOS/Leia_Me_Enem_2023.pdf`.
- **2024** — D: `raw/microdados_enem_2024/microdados_enem_2024/DICIONÁRIO/Dicionário_Microdados_Enem_2024.xlsx`; L: `raw/microdados_enem_2024/microdados_enem_2024/LEIA-ME E DOCUMENTOS TÉCNICOS/Leia_Me_Enem_2024.pdf`.
- **2025** — D: `raw/microdados_enem_2025/microdados_enem_2025/DICIONÁRIO/Dicionário_Microdados_Enem_2025.xlsx`; L: `raw/microdados_enem_2025/microdados_enem_2025/LEIA-ME E DOCUMENTOS TÉCNICOS/Leia_Me_Enem_2025.pdf`.
