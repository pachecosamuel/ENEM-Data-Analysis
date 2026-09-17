"""Coordena leitura da trusted e publicação de quatro linhas analíticas auditadas."""
import csv
import hashlib
import json
import os
from pathlib import Path
import tempfile
import time
from datetime import datetime, timezone

import duckdb
import psutil

from src.desempenho import AREAS, FILTRO, METODO_QUANTIL, calcular_desempenho


def raiz_projeto(inicio=None):
    atual = Path(inicio or Path.cwd()).resolve()
    return next(p for p in (atual, *atual.parents) if (p / 'src/desempenho.py').is_file())


def hash_arquivo(arquivo):
    with Path(arquivo).open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()


def executar_desempenho(raiz=None):
    raiz = raiz_projeto(raiz)
    fonte = raiz / 'trusted/resultados_2025_base.parquet'
    trabalho = raiz / 'work'
    trabalho.mkdir(exist_ok=True)
    inicio = time.monotonic()
    hash_antes = hash_arquivo(fonte)
    relatorio = {'data_utc': datetime.now(timezone.utc).isoformat(), 'fonte': str(fonte.relative_to(raiz)),
                 'sha256_fonte_antes': hash_antes, 'fonte_bytes': fonte.stat().st_size,
                 'duckdb': duckdb.__version__, 'memory_limit': '256MB', 'threads': 1,
                 'ram_disponivel_inicio_bytes': psutil.virtual_memory().available,
                 'filtros': {a: FILTRO.format(area=a) for a in AREAS}, 'quantil': METODO_QUANTIL}
    with tempfile.TemporaryDirectory(prefix='desempenho_', dir=trabalho) as temp:
        pasta = Path(temp).resolve()
        if not pasta.is_relative_to(trabalho.resolve()):
            raise ValueError('Temporário fora do projeto.')
        with duckdb.connect(config={'memory_limit': '256MB', 'threads': '1',
                                    'temp_directory': str(pasta/'spill'), 'max_temp_directory_size': '2GB'}) as con:
            con.read_parquet(str(fonte)).create_view('base')
            esquema = [list(row[:2]) for row in con.execute('DESCRIBE base').fetchall()]
            esperado = [['NU_SEQUENCIAL', 'VARCHAR'], ['NU_ANO', 'INTEGER']]
            esperado += [[f'TP_PRESENCA_{a}', 'TINYINT'] for a in AREAS]
            esperado += [[f'NU_NOTA_{a}', 'DECIMAL(10,1)'] for a in AREAS]
            if esquema != esperado:
                raise ValueError(f'Esquema da trusted diverge do contrato: {esquema}')
            if con.execute('SELECT count(*) FROM base WHERE NU_ANO IS DISTINCT FROM 2025').fetchone()[0]:
                raise ValueError('Ano inválido na fonte.')
            resultados, controles = calcular_desempenho(con)
            relatorio.update(esquema=esquema, controles=controles, indicadores=resultados)
        hash_depois = hash_arquivo(fonte)
        if hash_antes != hash_depois:
            raise ValueError('Fonte mudou durante a análise; publicação bloqueada.')
        relatorio.update(sha256_fonte_depois=hash_depois, segundos=round(time.monotonic()-inicio, 3),
                         ram_disponivel_fim_bytes=psutil.virtual_memory().available,
                         validacao='aprovada', total_base=resultados[0]['total_base'])
        saida = pasta/'desempenho_2025.csv'
        with saida.open('w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=list(resultados[0]))
            writer.writeheader()
            writer.writerows(resultados)
        relatorio['sha256_indicadores_csv'] = hash_arquivo(saida)
        auditoria = pasta/'validacao_desempenho_2025.json'
        auditoria.write_text(json.dumps(relatorio, ensure_ascii=False, indent=2), encoding='utf-8')
        (raiz/'analitica').mkdir(exist_ok=True)
        (raiz/'reports').mkdir(exist_ok=True)
        os.replace(saida, raiz/'analitica/desempenho_2025.csv')
        os.replace(auditoria, raiz/'reports/validacao_desempenho_2025.json')
    return resultados, relatorio


if __name__ == '__main__':
    resultados, _ = executar_desempenho()
    print(json.dumps(resultados, indent=2, ensure_ascii=False))
