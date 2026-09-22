"""I/O da segunda história; fonte read-only e saídas agregadas compactas."""
import csv
import json
import os
from pathlib import Path
import tempfile
import time
from datetime import datetime, timezone

import duckdb
from src.desempenho_execucao import raiz_projeto, hash_arquivo
from src.trusted_resultados import TIPOS
from src.participacao import calcular_participacao


def executar_participacao(raiz=None):
    raiz = raiz_projeto(raiz)
    fonte = raiz/'trusted/resultados_2025_base.parquet'
    inicio = time.monotonic()
    hash_antes = hash_arquivo(fonte)
    trabalho = raiz/'work'
    trabalho.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='participacao_', dir=trabalho) as temp:
        pasta = Path(temp).resolve()
        if not pasta.is_relative_to(trabalho.resolve()):
            raise ValueError('Temporário fora do projeto.')
        with duckdb.connect(config={'memory_limit':'256MB','threads':'1','temp_directory':str(pasta/'spill'),
                                    'max_temp_directory_size':'2GB'}) as con:
            con.read_parquet(str(fonte)).create_view('base')
            esquema = [list(x[:2]) for x in con.execute('DESCRIBE base').fetchall()]
            if esquema != [list(x) for x in TIPOS.items()]:
                raise ValueError('Esquema incompatível com a trusted contratada.')
            total, nulos, ano_invalido = con.execute('''SELECT count(*),
                count(*) FILTER(WHERE NU_SEQUENCIAL IS NULL OR trim(NU_SEQUENCIAL)=''),
                count(*) FILTER(WHERE NU_ANO IS DISTINCT FROM 2025) FROM base''').fetchone()
            duplicadas = con.execute('''SELECT count(*) FROM (SELECT NU_SEQUENCIAL FROM base
                GROUP BY NU_SEQUENCIAL HAVING count(*)>1)''').fetchone()[0]
            if nulos or duplicadas or ano_invalido:
                raise ValueError(f'Chave/ano inválidos: nulos={nulos}, duplicadas={duplicadas}, ano={ano_invalido}')
            resultado, controles = calcular_participacao(con)
            if resultado['resumo']['total_base'] != total:
                raise ValueError('Total agregado diverge da fonte.')
        hash_depois = hash_arquivo(fonte)
        if hash_depois != hash_antes:
            raise ValueError('Fonte alterada durante a leitura.')
        alertas = [x for x in resultado['pares'] if x['quantidade'] and x['status'] in ('misto','dados_ausentes','codigo_invalido')]
        report = {'data_utc':datetime.now(timezone.utc).isoformat(), 'fonte':fonte.relative_to(raiz).as_posix(),
                  'sha256_antes':hash_antes,'sha256_depois':hash_depois,'esquema':esquema,
                  'total_base':total,'chaves_nulas':nulos,'chaves_duplicadas':duplicadas,'anos_invalidos':ano_invalido,
                  'duckdb':duckdb.__version__,'memory_limit':'256MB','threads':1,
                  'contrato':'docs/contrato_analitico_participacao_2025.md',
                  'validacao':'aprovada_com_alertas' if alertas else 'aprovada', 'alertas_pares':alertas,
                  'controles':controles, 'resultado':resultado,'hashes_csv':{}}
        (raiz/'analitica').mkdir(exist_ok=True)
        (raiz/'reports').mkdir(exist_ok=True)
        saidas=[]
        for nome in ('dias','pares','transicoes','combinacoes_conjuntas','resumo'):
            linhas = [resultado[nome]] if nome=='resumo' else resultado[nome]
            # Matriz e pares incluem zeros explícitos; cabeçalho de conjuntos vazios é definido.
            campos = list(linhas[0]) if linhas else ['LC','CH','CN','MT','quantidade']
            arquivo=pasta/f'participacao_2025_{nome}.csv'
            with arquivo.open('w',encoding='utf-8',newline='') as f:
                writer=csv.DictWriter(f,fieldnames=campos); writer.writeheader(); writer.writerows(linhas)
            report['hashes_csv'][arquivo.name]=hash_arquivo(arquivo)
            saidas.append(arquivo)
        report['segundos']=round(time.monotonic()-inicio,3)
        auditoria=pasta/'validacao_participacao_2025.json'
        auditoria.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
        for arquivo in saidas:
            os.replace(arquivo,raiz/'analitica'/arquivo.name)
        os.replace(auditoria,raiz/'reports'/auditoria.name)
    return resultado,report


if __name__=='__main__':
    resultado,_=executar_participacao()
    print(json.dumps(resultado['resumo'],ensure_ascii=False,indent=2))
