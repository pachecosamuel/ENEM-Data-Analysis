# Nota técnica: vínculo entre PARTICIPANTES e RESULTADOS do ENEM 2024–2025

Data: 01/10/2026. Finalidade: apoiar discussão técnica com especialista sobre a possibilidade de associação individual nas versões públicas analisadas.

## Conclusão e alcance

**Não foi identificada uma chave ou correspondência individual documentada e verificável entre PARTICIPANTES e RESULTADOS nos pacotes públicos de 2024 e 2025 analisados neste projeto.** Os LeiaMe afirmam que não há chave de ligação comum; os dicionários explicitam que NU_SEQUENCIAL não permite relacionar as duas bases.

Assim, os arquivos não sustentam, por si só, um vínculo 1:1 validado para cruzar renda familiar e notas de uma mesma pessoa. Esta é uma conclusão sobre as fontes e evidências disponíveis, **não uma prova de impossibilidade matemática universal**, nem uma afirmação de que nenhum método ou fonte externa possa estabelecer correspondências. A conclusão pode ser revista mediante evidência de ligação válida e validação independente.

## Evidência documental conferida

A conferência foi feita diretamente nos dois PDFs e nas células dos dois arquivos XLSX locais em 01/10/2026. As páginas abaixo são páginas físicas dos PDFs, também numeradas como 7 nos documentos. As citações preservam as palavras e a pontuação dos trechos, com quebras de linha reunidas.

| Fonte | Localização verificada | Trecho literal curto |
| --- | --- | --- |
| L2024 | Página 7, parágrafo que descreve a divisão em PARTICIPANTES_2024 e RESULTADOS_2024 | “as duas bases não possuem chave de ligação em comum” |
| L2025 | Página 7, seção “3- MICRODADOS DO ENEM”, primeiro parágrafo | “os arquivos PARTICIPANTES_2025.csv e RESULTADOS_2025.csv não possuem chave de ligação em comum.” |
| D2024 | Aba `RESULTADOS_2024`, célula **B6**, definição do campo em A6 | “Número sequencial da linha de resultados¹” |
| D2024 | Aba `RESULTADOS_2024`, célula **A145**, nota 1 | “não é possível utilizá-la para relacionar as duas bases.” |
| D2025 | Aba `RESULTADOS_2025`, célula **B6**, definição do campo em A6 | “Número sequencial da linha de resultados¹” |
| D2025 | Aba `RESULTADOS_2025`, célula **A313**, nota 1 | “não é possível utilizá-la para relacionar as duas bases.” |

As notas A145/A313 identificam NU_SEQUENCIAL como número que distingue linhas de RESULTADOS e afirmam que é uma variável distinta de NU_INSCRICAO, disponível em PARTICIPANTES. Portanto, valores eventualmente iguais nos dois campos não documentam identidade de pessoa.

Em `PARTICIPANTES_2024` e `PARTICIPANTES_2025`, **A6** contém NU_INSCRICAO e **B6** o descreve como número de inscrição, com remissão à nota 1. As notas **A207 (2024)** e **A259 (2025)** esclarecem que se trata de uma máscara, não do número original de inscrição. Também informam que o mesmo valor em anos diferentes não identifica o mesmo participante. Não se deve tratar esse campo como identificador pessoal persistente.

### Arquivos consultados

Caminhos relativos à raiz do repositório `ENEM-Data-Analysis`:

- **L2024:** `raw/microdados_enem_2024/microdados_enem_2024/LEIA-ME E DOCUMENTOS TÉCNICOS/Leia_Me_Enem_2024.pdf`
- **D2024:** `raw/microdados_enem_2024/microdados_enem_2024/DICIONÁRIO/Dicionário_Microdados_Enem_2024.xlsx`
- **L2025:** `raw/microdados_enem_2025/microdados_enem_2025/LEIA-ME E DOCUMENTOS TÉCNICOS/Leia_Me_Enem_2025.pdf`
- **D2025:** `raw/microdados_enem_2025/microdados_enem_2025/DICIONÁRIO/Dicionário_Microdados_Enem_2025.xlsx`

O alcance desta nota é dessas versões locais. Uma tabela adicional ou uma versão de dados com outro mecanismo de ligação exigiria nova avaliação.

## O que uma junção permite — e o que não demonstra

**Ano, UF e município não são, por si só, identificadores individuais.** Quando há vários registros com a mesma combinação em cada arquivo, a junção gera uma relação muitos para muitos: cada linha de um grupo encontra todas as linhas compatíveis do outro. Um grupo com *n* registros em PARTICIPANTES e *m* em RESULTADOS produz *n × m* combinações, sem demonstrar quais pares correspondem à mesma pessoa. Mesmo uma combinação que apareça uma única vez em cada lado requer evidência de que os atributos têm o mesmo significado e identificam o mesmo indivíduo.

**A agregação separada pode sustentar comparações de grupos.** É possível resumir cada base por edição e local de aplicação e então combinar as tabelas agregadas, desde que as chaves sejam únicas nesse nível e conceitos, cobertura e denominadores sejam compatíveis. Isso compara, por exemplo, perfil de renda dos inscritos divulgados e desempenho dos participantes elegíveis naquele local. Não revela a nota de cada faixa de renda individualmente. Inferir uma relação entre pessoas a partir de uma associação entre grupos incorre no risco de falácia ecológica. Local de prova tampouco equivale à residência.

**Ordenação e propriedades de contagem não comprovam identidade.** Igual quantidade de linhas, unicidade de cada identificador, criação de índices sequenciais ou alinhamento pela posição podem produzir tecnicamente uma tabela 1:1. Nenhuma dessas propriedades demonstra que o pareamento representa as mesmas pessoas. Seria necessária uma regra de correspondência comprovada; ordenar ambos os arquivos não cria essa regra.

**Matching probabilístico produz candidatos, não confirmação automática.** Um método pode atribuir probabilidades ou pontuações de semelhança a pares. Isso, sozinho, não prova identidade nem elimina falsos vínculos. Sua utilização exigiria fonte de referência independente, avaliação de falsos positivos e falsos negativos, cobertura e incerteza, além de demonstrar como erros de ligação afetam a análise pretendida.

## Perguntas para a discussão com o especialista

1. Qual campo, combinação de campos ou regra estabelece a correspondência individual? Em qual edição e versão dos arquivos?
2. Existe uma fonte adicional ou tabela de correspondência? Qual sua origem e qual documentação explica a ligação entre os identificadores?
3. O método proposto relaciona indivíduos ou apenas grupos? Como trata duplicidades, múltiplos candidatos e registros sem correspondência?
4. Qual evidência independente confirma que os pares representam a mesma pessoa, além de igualdade de valores, posição ou contagem?
5. Qual a cobertura do vínculo e como foram medidos os erros? Os registros não vinculados diferem dos vinculados?
6. Como a evidência proposta se concilia com as notas dos dicionários e com a ausência de chave comum declarada nos LeiaMe?

Uma resposta acompanhada de documentação e validação independente pode justificar a revisão do entendimento atual. Até que essa evidência esteja disponível, o projeto mantém **perfil econômico e desempenho como análises independentes em 2024–2025**, sem apresentar cruzamentos individuais renda–nota como observados.

Esta nota não executa junções, matching ou novos cálculos e não altera as análises existentes.
