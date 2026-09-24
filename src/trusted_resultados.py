"""Contrato v2 de RESULTADOS 2025: 17 campos, nenhuma exclusão de linhas."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
from pathlib import Path
import shutil
import tempfile
import time

import duckdb
import psutil

AREAS = ('CN', 'CH', 'LC', 'MT')
PRESENCAS = tuple(f'TP_PRESENCA_{a}' for a in AREAS)
NOTAS = tuple(f'NU_NOTA_{a}' for a in AREAS)
CAMPOS_LEGADOS = ('NU_SEQUENCIAL', 'NU_ANO', *PRESENCAS, *NOTAS)
NOTAS_REDACAO = ('NU_NOTA_REDACAO', *(f'NU_NOTA_COMP{i}' for i in range(1, 6)))
CAMPOS = (*CAMPOS_LEGADOS, 'TP_STATUS_REDACAO', *NOTAS_REDACAO)
TIPOS_LEGADOS = dict(zip(CAMPOS_LEGADOS, ('VARCHAR', 'INTEGER', *(['TINYINT'] * 4), *(['DECIMAL(10,1)'] * 4))))
TIPOS = {**TIPOS_LEGADOS, 'TP_STATUS_REDACAO': 'TINYINT', **dict.fromkeys(NOTAS_REDACAO, 'DECIMAL(10,1)')}
FONTE = Path('raw/microdados_enem_2025/microdados_enem_2025/DADOS/RESULTADOS_2025.csv')


class ErroContrato(ValueError):
    """Relatório permanece disponível mesmo quando a publicação é bloqueada."""

    def __init__(self, mensagem, relatorio):
        super().__init__(mensagem)
        self.relatorio = relatorio


def raiz_projeto(inicio=None):
    atual = Path(inicio or Path.cwd()).resolve()
    for candidato in (atual, *atual.parents):
        if (candidato / 'src/trusted_resultados.py').is_file() and (candidato / 'raw').is_dir():
            return candidato
    raise FileNotFoundError('Execute a partir da raiz do projeto ou de uma subpasta.')


def recursos(raiz):
    memoria = psutil.virtual_memory()
    return {'ram_total_bytes': memoria.total, 'ram_disponivel_bytes': memoria.available,
            'disco_livre_bytes': shutil.disk_usage(raiz).free}


def sha256(arquivo):
    with Path(arquivo).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def literal(valor):
    return "'" + str(valor).replace("'", "''") + "'"


def ler_selecionados(con, fonte, limite=None):
    """Lê em modo estrito; todos os campos entram como texto antes da conversão."""
    with Path(fonte).open(encoding='latin-1', newline='') as stream:
        nomes = next(csv.reader(stream, delimiter=';'))
    if len(nomes) != len(set(nomes)) or not set(CAMPOS).issubset(nomes):
        raise ValueError('Cabeçalho duplicado ou ausência de campos do contrato.')
    if limite is not None and (not isinstance(limite, int) or limite <= 0):
        raise ValueError('Limite amostral deve ser inteiro positivo.')
    esquema = '{' + ','.join(f'{literal(n)}: \'VARCHAR\'' for n in nomes) + '}'
    leitura = (f'read_csv({literal(Path(fonte).resolve().as_posix())}, '
               f"columns={esquema}, auto_detect=false, header=true, delim=';', "
               "encoding='latin-1', quote='\"', escape='\"', nullstr='', "
               'strict_mode=true, ignore_errors=false, null_padding=false, parallel=false)')
    sufixo = f' LIMIT {limite}' if limite else ''
    con.execute('CREATE TABLE entrada AS SELECT ' + ','.join(CAMPOS) + ' FROM ' + leitura + sufixo)
    # Contagem independente da projeção e da transformação, pelo mesmo parser estrito.
    total = con.execute(f'SELECT count(*) FROM (SELECT * FROM {leitura}{sufixo})').fetchone()[0]
    return total


def padronizar(con):
    """Não arredonda nem converte texto inválido silenciosamente em nulo."""
    con.execute('CREATE VIEW textos AS SELECT ' + ','.join(
        f"NULLIF(trim({c}), '') AS {c}" for c in CAMPOS) + ' FROM entrada')
    falhas = {}
    inesperadas = {}
    for campo in CAMPOS[1:]:
        padrao = r'[+-]?[0-9]+(\.[0-9])?' if campo in (*NOTAS, *NOTAS_REDACAO) else r'[0-9]+'
        condicao = (f'{campo} IS NOT NULL AND (NOT regexp_full_match({campo}, {literal(padrao)}) '
                    f'OR TRY_CAST({campo} AS {TIPOS[campo]}) IS NULL)')
        falhas[campo] = con.execute(f'SELECT count(*) FROM textos WHERE {condicao}').fetchone()[0]
    for campo in (*PRESENCAS, 'TP_STATUS_REDACAO'):
        codigos = "'1','2','3','4','6','7','8','9'" if campo == 'TP_STATUS_REDACAO' else "'0','1','2'"
        inesperadas[campo] = [dict(valor=v, quantidade=n) for v, n in con.execute(
            f"SELECT {campo}, count(*) FROM textos WHERE {campo} NOT IN ({codigos}) "
            f'GROUP BY {campo} ORDER BY {campo}').fetchall()]
    auditoria = {'falhas_conversao': falhas, 'categorias_inesperadas': inesperadas}
    if any(falhas.values()) or any(inesperadas.values()):
        raise ErroContrato('Conversões/categorias inválidas; nenhuma saída publicada.', auditoria)
    con.execute('CREATE TABLE padronizados AS SELECT NU_SEQUENCIAL,' + ','.join(
        f'CAST({c} AS {TIPOS[c]}) AS {c}' for c in CAMPOS[1:]) + ' FROM textos')
    return auditoria


def validar(con, tabela='padronizados'):
    if tabela not in ('padronizados', 'releitura'):
        raise ValueError('Tabela de validação não reconhecida.')
    total = con.execute(f'SELECT count(*) FROM {tabela}').fetchone()[0]
    nulos = dict(zip(CAMPOS, con.execute('SELECT ' + ','.join(
        f'count(*) FILTER (WHERE {c} IS NULL)' for c in CAMPOS) + f' FROM {tabela}').fetchone()))
    duplicados = con.execute(f'''SELECT count(*), coalesce(sum(n-1),0) FROM (
        SELECT count(*) n FROM {tabela} WHERE NU_SEQUENCIAL IS NOT NULL
        GROUP BY NU_SEQUENCIAL HAVING count(*) > 1)''').fetchone()
    anos = [{'ano': a, 'quantidade': n} for a, n in con.execute(
        f'SELECT NU_ANO, count(*) FROM {tabela} GROUP BY NU_ANO ORDER BY NU_ANO').fetchall()]
    areas = {}
    for area in AREAS:
        p, n = f'TP_PRESENCA_{area}', f'NU_NOTA_{area}'
        nomes = ('presente_sem_nota', 'ausente_com_nota', 'eliminado_com_nota',
                 'presenca_nula_com_nota', 'nota_zero', 'nota_negativa')
        condicoes = (f'{p}=1 AND {n} IS NULL', f'{p}=0 AND {n} IS NOT NULL',
                     f'{p}=2 AND {n} IS NOT NULL', f'{p} IS NULL AND {n} IS NOT NULL',
                     f'{n}=0', f'{n}<0')
        valores = con.execute('SELECT ' + ','.join(f'count(*) FILTER (WHERE {c})' for c in condicoes)
                              + f' FROM {tabela}').fetchone()
        areas[area] = dict(zip(nomes, valores))
        areas[area]['presencas'] = [{'codigo': v, 'quantidade': q} for v, q in con.execute(
            f'SELECT {p},count(*) FROM {tabela} GROUP BY {p} ORDER BY {p}').fetchall()]
    completas = ' AND '.join(f'{c} IS NOT NULL' for c in NOTAS_REDACAO)
    soma = '+'.join(NOTAS_REDACAO[1:])
    condicoes_redacao = {
        'nota_zero': 'NU_NOTA_REDACAO=0',
        'nota_sem_status': 'NU_NOTA_REDACAO IS NOT NULL AND TP_STATUS_REDACAO IS NULL',
        'status_sem_nota': 'TP_STATUS_REDACAO IS NOT NULL AND NU_NOTA_REDACAO IS NULL',
        'soma_comparavel': completas,
        'soma_divergente': f'{completas} AND NU_NOTA_REDACAO<>({soma})',
        'final_fora_escala': 'NU_NOTA_REDACAO<0 OR NU_NOTA_REDACAO>1000',
        'competencias_fora_escala': ' OR '.join(f'{c}<0 OR {c}>200' for c in NOTAS_REDACAO[1:])}
    redacao = dict(zip(condicoes_redacao, con.execute('SELECT '+','.join(
        f'count(*) FILTER(WHERE {c})' for c in condicoes_redacao.values())+f' FROM {tabela}').fetchone()))
    esquema = [list(r[:2]) for r in con.execute(f'DESCRIBE {tabela}').fetchall()]
    return {'registros': total, 'nulos': nulos, 'chaves_duplicadas': duplicados[0],
            'linhas_excedentes_chave': int(duplicados[1]), 'anos': anos,
            'por_area': areas, 'redacao': redacao, 'esquema': esquema}


def reconciliar(con, esperado, relatorio):
    """Verifica contagem, esquema e igualdade de todos os valores por chave."""
    obtido = validar(con, 'releitura')
    if obtido != esperado:
        raise ErroContrato('Releitura Parquet diverge da tabela padronizada.', relatorio)
    diferencas = ' OR '.join(f't.{c} IS DISTINCT FROM p.{c}' for c in CAMPOS[1:])
    n = con.execute(f'''SELECT count(*) FROM padronizados t FULL OUTER JOIN releitura p
        ON t.NU_SEQUENCIAL=p.NU_SEQUENCIAL
        WHERE t.NU_SEQUENCIAL IS NULL OR p.NU_SEQUENCIAL IS NULL OR {diferencas}''').fetchone()[0]
    if n:
        raise ErroContrato(f'{n} registros divergem na comparação exata do Parquet.', relatorio)
    return obtido


def conferir_esquema(esquema, exigir_redacao=False):
    """Aceita somente as duas versões completas conhecidas, sem ignorar colunas/tipos."""
    versoes = [[list(x) for x in TIPOS.items()]]
    if not exigir_redacao:
        versoes.append([list(x) for x in TIPOS_LEGADOS.items()])
    if esquema not in versoes:
        raise ValueError('Esquema incompatível com os contratos v1/v2 de RESULTADOS.')


def conferir_legado(con, destino, relatorio):
    """Bloqueia publicação caso qualquer linha ou valor legado mude por chave."""
    con.execute(f'CREATE VIEW anterior AS SELECT * FROM read_parquet({literal(destino.as_posix())})')
    esquema = [list(x[:2]) for x in con.execute('DESCRIBE anterior').fetchall()]
    conferir_esquema(esquema)
    chave_ruim = con.execute('''SELECT count(*)-count(DISTINCT NU_SEQUENCIAL),
        count(*) FILTER(WHERE NU_SEQUENCIAL IS NULL) FROM anterior''').fetchone()
    if any(chave_ruim):
        raise ErroContrato('Chave inválida na trusted anterior.', relatorio)
    diferencas = ' OR '.join(f'a.{c} IS DISTINCT FROM n.{c}' for c in CAMPOS_LEGADOS[1:])
    n = con.execute(f'''SELECT count(*) FROM anterior a FULL OUTER JOIN padronizados n
        ON a.NU_SEQUENCIAL=n.NU_SEQUENCIAL WHERE a.NU_SEQUENCIAL IS NULL
        OR n.NU_SEQUENCIAL IS NULL OR {diferencas}''').fetchone()[0]
    if n:
        raise ErroContrato(f'{n} divergências nos dez campos legados; publicação bloqueada.', relatorio)
    return {'campos': list(CAMPOS_LEGADOS), 'divergencias': n,
            'sha256_anterior': sha256(destino), 'esquema_anterior': esquema}


def executar(raiz=None, limite=None, memoria='256MB', threads=1):
    """Amostra só valida; execução completa publica Parquet após releitura exata."""
    raiz = raiz_projeto(raiz)
    fonte = raiz / FONTE
    destino = raiz / 'trusted/resultados_2025_base.parquet'
    trabalho = raiz / 'work'
    trabalho.mkdir(exist_ok=True)
    relatorios = raiz / 'reports'
    relatorios.mkdir(exist_ok=True)
    inicio = time.monotonic()
    modo = 'amostra' if limite is not None else 'completo'
    relatorio = {'modo': modo, 'limite': limite, 'fonte': FONTE.as_posix(),
                 'recursos_inicio': recursos(raiz), 'duckdb': duckdb.__version__,
                 'configuracao': {'memory_limit': memoria, 'threads': threads, 'max_temp_directory_size': '10GB'},
                 'publicado': False}
    estado_fonte = fonte.stat()
    if limite is None:
        relatorio['sha256_raw_antes'] = sha256(fonte)
    try:
        with tempfile.TemporaryDirectory(prefix='resultados_2025_', dir=trabalho) as temporario:
            pasta = Path(temporario).resolve()
            if not pasta.is_relative_to(trabalho.resolve()):
                raise ValueError('Diretório temporário fora do projeto.')
            with duckdb.connect(str(pasta / 'estagio.duckdb'), config={
                'memory_limit': memoria, 'threads': str(threads),
                'temp_directory': str(pasta / 'spill'), 'max_temp_directory_size': '10GB',
                'preserve_insertion_order': 'false'}) as con:
                relatorio['registros_entrada'] = ler_selecionados(con, fonte, limite)
                try:
                    relatorio.update(padronizar(con))
                except ErroContrato as erro:
                    relatorio.update(erro.relatorio)
                    raise ErroContrato(str(erro), relatorio) from erro
                validacao = validar(con)
                relatorio['validacao'] = validacao
                if (validacao['registros'] != relatorio['registros_entrada'] or
                    validacao['nulos']['NU_SEQUENCIAL'] or validacao['chaves_duplicadas'] or
                    validacao['nulos']['NU_ANO'] or
                    any(a['ano'] != 2025 for a in validacao['anos'])):
                    raise ErroContrato('Falha de contagem, chave ou ano; publicação bloqueada.', relatorio)
                if limite is None:
                    candidato = pasta / 'resultados_2025_base.parquet'
                    con.execute(f'COPY padronizados TO {literal(candidato.as_posix())} '
                                '(FORMAT PARQUET, COMPRESSION ZSTD, ROW_GROUP_SIZE 32768)')
                    con.execute(f'CREATE VIEW releitura AS SELECT * FROM read_parquet({literal(candidato.as_posix())})')
                    relatorio['releitura'] = reconciliar(con, validacao, relatorio)
                    if destino.exists():
                        relatorio['regressao_legado'] = conferir_legado(con, destino, relatorio)
                        # Cópia para rollback apenas na migração v1 -> v2, fora do staging descartável.
                        if len(relatorio['regressao_legado']['esquema_anterior']) == 10:
                            backup = trabalho / ('rollback_resultados_' + sha256(destino) + '.parquet')
                            if not backup.exists():
                                shutil.copy2(destino, backup)
                            if sha256(backup) != sha256(destino):
                                raise ErroContrato('Backup de rollback divergente.', relatorio)
                            relatorio['rollback_parquet'] = backup.relative_to(raiz).as_posix()
                    relatorio['sha256_raw_depois'] = sha256(fonte)
                    if relatorio['sha256_raw_antes'] != relatorio['sha256_raw_depois']:
                        raise ErroContrato('Fonte mudou durante execução; publicação bloqueada.', relatorio)
                    if fonte.stat().st_mtime_ns != estado_fonte.st_mtime_ns:
                        raise ErroContrato('Data da fonte mudou durante execução.', relatorio)
                    destino.parent.mkdir(exist_ok=True)
                    os.replace(candidato, destino)
                    relatorio.update(publicado=True, parquet=destino.relative_to(raiz).as_posix(),
                                     parquet_bytes=destino.stat().st_size, sha256_parquet=sha256(destino))
        return relatorio
    except Exception as erro:
        relatorio['erro'] = str(erro)
        raise
    finally:
        relatorio['segundos'] = round(time.monotonic() - inicio, 3)
        relatorio['recursos_fim'] = recursos(raiz)
        arquivo = relatorios / f'validacao_resultados_2025_{modo}.json'
        temporario_json = arquivo.with_suffix('.json.tmp')
        temporario_json.write_text(json.dumps(relatorio, indent=2, ensure_ascii=False), encoding='utf-8')
        os.replace(temporario_json, arquivo)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--amostra', type=int, default=None)
    args = parser.parse_args()
    print(json.dumps(executar(limite=args.amostra), indent=2, ensure_ascii=False))
