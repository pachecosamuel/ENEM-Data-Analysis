"""Lê a trusted, valida e publica somente agregados da POC de redação."""
import csv
import json
import os
import tempfile
from pathlib import Path
from datetime import datetime, timezone

import duckdb
from src.trusted_resultados import raiz_projeto, sha256, conferir_esquema
from src.redacao import calcular_redacao, FILTRO_FINAL, FILTRO_COMP


def executar_redacao(raiz=None):
    raiz = raiz_projeto(raiz)
    fonte = raiz/'trusted/resultados_2025_base.parquet'
    antes = sha256(fonte)
    (raiz/'work').mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='redacao_', dir=raiz/'work') as temp:
        pasta = Path(temp)
        with duckdb.connect(config={'memory_limit':'256MB', 'threads':'1',
            'temp_directory':str(pasta/'spill'), 'max_temp_directory_size':'2GB'}) as con:
            con.read_parquet(str(fonte)).create_view('base')
            esquema = [list(x[:2]) for x in con.execute('DESCRIBE base').fetchall()]
            conferir_esquema(esquema, exigir_redacao=True)
            ruins = con.execute('''SELECT count(*) FILTER(WHERE NU_SEQUENCIAL IS NULL
                OR trim(NU_SEQUENCIAL)='' OR NU_ANO IS DISTINCT FROM 2025),
                count(*)-count(DISTINCT NU_SEQUENCIAL) FROM base''').fetchone()
            if any(ruins):
                raise ValueError('Chave ou ano inválido na trusted.')
            resultado, controles = calcular_redacao(con)
        depois = sha256(fonte)
        if antes != depois:
            raise ValueError('Trusted mudou durante a análise.')
        nomes_alertas = ('soma_divergente','nota_sem_status','status_sem_nota',
                        'positivas_status_problematico','final_fora_escala','competencias_fora_escala')
        alertas = {k:controles[k] for k in nomes_alertas if controles[k]}
        report = dict(data_utc=datetime.now(timezone.utc).isoformat(), fonte=fonte.relative_to(raiz).as_posix(),
            sha256_antes=antes, sha256_depois=depois, esquema=esquema, duckdb=duckdb.__version__,
            memory_limit='256MB', threads=1, contrato='docs/contrato_analitico_redacao_2025.md',
            filtros={'final':FILTRO_FINAL, 'competencias':FILTRO_COMP},
            quantil='quantile_cont DOUBLE, tipo 7', controles=controles, alertas=alertas,
            validacao='aprovada_com_alertas' if alertas else 'aprovada', hashes_csv={}, resultado=resultado)
        saidas=[]
        for nome,linhas in resultado.items():
            if not linhas:
                raise ValueError(f'Agregado vazio: {nome}; publicação não realizada.')
            arquivo=pasta/f'redacao_2025_{nome}.csv'
            with arquivo.open('w',encoding='utf-8',newline='') as f:
                writer=csv.DictWriter(f,fieldnames=list(linhas[0]))
                writer.writeheader(); writer.writerows(linhas)
            report['hashes_csv'][arquivo.name]=sha256(arquivo)
            saidas.append(arquivo)
        auditoria=pasta/'validacao_redacao_2025.json'
        auditoria.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
        (raiz/'analitica').mkdir(exist_ok=True)
        (raiz/'reports').mkdir(exist_ok=True)
        for arquivo in saidas:
            os.replace(arquivo,raiz/'analitica'/arquivo.name)
        os.replace(auditoria,raiz/'reports'/auditoria.name)
    return resultado,report


if __name__ == '__main__':
    resultado,report=executar_redacao()
    print(json.dumps(dict(final=resultado['final'],competencias=resultado['competencias'],
                         controles=report['controles']),ensure_ascii=False,indent=2))
