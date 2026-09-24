"""Conta o universo divulgado de PARTICIPANTES, sem cruzar bases ou perfis."""
import csv
import json
import os
import tempfile
from datetime import datetime, timezone

import duckdb
from src.trusted_resultados import raiz_projeto, literal, sha256

OFICIAL = {
    'inscricoes_confirmadas': 4811338,
    'instituicao': 'Inep',
    'documento': 'Balanço da aplicação do 1º dia — 09/11/2025',
    'data_documento': '2025-11-09',
    'url': 'https://download.inep.gov.br/enem/outros_documentos/enem_balanco_da_aplicacao_09_11_2025.pdf',
    'consulta': '2026-09-22',
    'observacao': 'Tabela Inscrições confirmadas. Presença/ausência do balanço são preliminares e não são utilizadas aqui.',
    'acesso': 'Conteúdo da tabela recuperado pelo índice de busca; abertura/download direto indisponível na consulta.'
}
OFICIAL['corroboracao'] = {
    'instituicao': 'Ministério das Mulheres, com informações do MEC',
    'data': '2025-08-11',
    'url': 'https://www.gov.br/mulheres/pt-br/central-de-conteudos/noticias/2025/agosto/mulheres-lideram-inscricoes-no-enem-2025-e-somam-60-dos-participantes',
    'acesso': 'Texto oficial acessível na consulta; confirma explicitamente inscrições confirmadas.'}


def contar_participantes(con, fonte):
    with fonte.open(encoding='latin-1', newline='') as f:
        nomes = next(csv.reader(f, delimiter=';'))
    if len(nomes) != len(set(nomes)) or not {'NU_INSCRICAO', 'NU_ANO'}.issubset(nomes):
        raise ValueError('Cabeçalho inválido de PARTICIPANTES.')
    esquema = '{' + ','.join(f"{literal(n)}:'VARCHAR'" for n in nomes) + '}'
    leitura = (f'read_csv({literal(fonte.as_posix())}, columns={esquema}, '
               'auto_detect=false, header=true, delim=\';\', encoding=\'latin-1\', '
               'quote=\'"\', escape=\'"\', nullstr=\'\', strict_mode=true, '
               'ignore_errors=false, null_padding=false, parallel=false)')
    con.execute('CREATE TABLE participantes AS SELECT '
                "NULLIF(trim(NU_INSCRICAO),'') chave, NULLIF(trim(NU_ANO),'') ano FROM " + leitura)
    total, nulos, anos = con.execute('''SELECT count(*), count(*) FILTER(WHERE chave IS NULL),
        count(*) FILTER(WHERE ano IS DISTINCT FROM '2025') FROM participantes''').fetchone()
    duplicadas = con.execute('''SELECT count(*) FROM (SELECT chave FROM participantes
        WHERE chave IS NOT NULL GROUP BY chave HAVING count(*)>1)''').fetchone()[0]
    resultado = dict(registros=total, chaves_nulas=nulos, chaves_duplicadas=duplicadas,
                     anos_invalidos=anos, ano=2025)
    if nulos or duplicadas or anos:
        raise ValueError(f'Chave/ano inválidos em PARTICIPANTES: {resultado}')
    return resultado


def executar_inscritos(raiz=None):
    raiz = raiz_projeto(raiz)
    fonte = raiz/'raw/microdados_enem_2025/microdados_enem_2025/DADOS/PARTICIPANTES_2025.csv'
    antes = sha256(fonte)
    trusted = raiz/'trusted/resultados_2025_base.parquet'
    hash_trusted = sha256(trusted)
    (raiz/'work').mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='inscritos_', dir=raiz/'work') as temp:
        with duckdb.connect(str(temp)+'/contagem.duckdb', config={
            'memory_limit':'256MB', 'threads':'1', 'temp_directory':str(temp)+'/spill',
            'max_temp_directory_size':'2GB'}) as con:
            contagem = contar_participantes(con, fonte)
            total_resultados = con.execute('SELECT count(*) FROM read_parquet(?)',
                [str(raiz/'trusted/resultados_2025_base.parquet')]).fetchone()[0]
    depois = sha256(fonte)
    if antes != depois or sha256(trusted) != hash_trusted:
        raise ValueError('Fonte mudou durante a leitura.')
    report = dict(data_utc=datetime.now(timezone.utc).isoformat(), fonte=fonte.relative_to(raiz).as_posix(),
                  sha256_antes=antes, sha256_depois=depois, oficial=OFICIAL,
                  participantes=contagem, registros_resultados=total_resultados, sha256_resultados=hash_trusted,
                  diferenca_oficial_participantes=OFICIAL['inscricoes_confirmadas']-contagem['registros'],
                  diferenca_participantes_resultados=contagem['registros']-total_resultados,
                  interpretacao='Universos distintos; diferença sem causa estabelecida. Nenhum join entre bases.',
                  duckdb=duckdb.__version__, memory_limit='256MB', threads=1, validacao='aprovada')
    destino = raiz/'reports/validacao_inscritos_2025.json'
    destino.parent.mkdir(exist_ok=True)
    temp = destino.with_suffix('.json.tmp')
    temp.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    os.replace(temp, destino)
    return report


if __name__ == '__main__':
    print(json.dumps(executar_inscritos(), ensure_ascii=False, indent=2))
