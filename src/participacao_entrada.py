"""Entrada mínima de participação: seis campos, sem excluir registros."""
from pathlib import Path
import os
import tempfile

import duckdb
from src.trusted_resultados import ler_selecionados, literal, sha256, raiz_projeto

TIPOS_PARTICIPACAO = {'NU_SEQUENCIAL': 'VARCHAR', 'NU_ANO': 'INTEGER',
                      **{f'TP_PRESENCA_{a}': 'INTEGER' for a in ('CN', 'CH', 'LC', 'MT')}}


def preparar_participacao(raiz=None, ano=2024):
    """Publica somente após conferir tipos, chave, contagem, releitura e raw."""
    if ano != 2024:
        raise ValueError('Esta entrada mínima foi documentada para 2024; 2025 usa a trusted existente.')
    raiz = raiz_projeto(raiz)
    fonte = raiz / f'raw/microdados_enem_{ano}/microdados_enem_{ano}/DADOS/RESULTADOS_{ano}.csv'
    destino = raiz / f'trusted/participacao_{ano}_base.parquet'
    campos = tuple(TIPOS_PARTICIPACAO)
    antes = sha256(fonte)
    trabalho = raiz / 'work'
    trabalho.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='participacao_entrada_', dir=trabalho) as temp:
        pasta = Path(temp)
        with duckdb.connect(str(pasta/'estagio.duckdb'), config={
            'memory_limit': '256MB', 'threads': '1', 'temp_directory': str(pasta/'spill'),
            'max_temp_directory_size': '4GB', 'preserve_insertion_order': 'false'}) as con:
            total = ler_selecionados(con, fonte, campos=campos)
            con.execute('CREATE VIEW textos AS SELECT ' + ','.join(
                f"NULLIF(trim({c}), '') AS {c}" for c in campos) + ' FROM entrada')
            for c in campos[1:]:
                falhas = con.execute(f"""SELECT count(*) FROM textos WHERE {c} IS NOT NULL
                    AND (NOT regexp_full_match({c}, '[+-]?[0-9]+')
                    OR TRY_CAST({c} AS INTEGER) IS NULL)""").fetchone()[0]
                if falhas:
                    raise ValueError(f'{c}: {falhas} falhas de conversão; publicação bloqueada.')
            con.execute('CREATE TABLE base AS SELECT NU_SEQUENCIAL,' + ','.join(
                f'CAST({c} AS INTEGER) AS {c}' for c in campos[1:]) + ' FROM textos')
            n, chave_nula, duplicadas, ano_invalido = con.execute(f'''SELECT count(*),
                count(*) FILTER(WHERE NU_SEQUENCIAL IS NULL),
                count(NU_SEQUENCIAL)-count(DISTINCT NU_SEQUENCIAL),
                count(*) FILTER(WHERE NU_ANO IS DISTINCT FROM {ano}) FROM base''').fetchone()
            if n != total or not n or chave_nula or duplicadas or ano_invalido:
                raise ValueError('Contagem, chave ou edição inválida; publicação bloqueada.')
            nulos = dict(zip(campos, con.execute('SELECT ' + ','.join(
                f'count(*) FILTER(WHERE {c} IS NULL)' for c in campos) + ' FROM base').fetchone()))
            # Códigos numéricos inesperados e nulos permanecem: o cálculo os classifica explicitamente.
            invalidos = {c: con.execute(f'SELECT count(*) FROM base WHERE {c} NOT IN (0,1,2)').fetchone()[0]
                         for c in campos[2:]}
            candidato = pasta/'candidato.parquet'
            con.execute(f'COPY base TO {literal(candidato.as_posix())} (FORMAT PARQUET, COMPRESSION ZSTD)')
            con.read_parquet(str(candidato)).create_view('releitura')
            esquema = [tuple(x[:2]) for x in con.execute('DESCRIBE releitura').fetchall()]
            if esquema != list(TIPOS_PARTICIPACAO.items()):
                raise ValueError('Tipos divergentes na releitura.')
            diferencas = con.execute('''SELECT count(*) FROM (
                (SELECT * FROM base EXCEPT ALL SELECT * FROM releitura)
                UNION ALL (SELECT * FROM releitura EXCEPT ALL SELECT * FROM base))''').fetchone()[0]
            if diferencas:
                raise ValueError('Releitura diverge; publicação bloqueada.')
        depois = sha256(fonte)
        if depois != antes:
            raise ValueError('Raw alterado durante leitura; publicação bloqueada.')
        destino.parent.mkdir(exist_ok=True)
        os.replace(candidato, destino)
    return {'edicao': ano, 'total_entrada': total, 'total_saida': n, 'nulos': nulos,
            'codigos_invalidos': invalidos, 'chaves_nulas': chave_nula, 'duplicadas': duplicadas,
            'anos_invalidos': ano_invalido, 'divergencias_releitura': diferencas,
            'sha256_raw_antes': antes, 'sha256_raw_depois': depois,
            'parquet': destino.relative_to(raiz).as_posix(), 'sha256_parquet': sha256(destino)}
