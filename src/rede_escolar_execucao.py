"""Leitura auditada da trusted e publicação dos agregados escolares."""
import csv
import json
import os
from pathlib import Path
import tempfile
import time
from datetime import datetime, timezone

import duckdb
from src.trusted_resultados import raiz_projeto, sha256, conferir_esquema
from src.rede_escolar import calcular_rede_escolar


def executar_rede_escolar(raiz=None):
    raiz=raiz_projeto(raiz)
    fonte=raiz/'trusted/resultados_2025_base.parquet'
    inicio=time.monotonic()
    antes=sha256(fonte)
    (raiz/'work').mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='rede_escolar_',dir=raiz/'work') as temp:
        pasta=Path(temp)
        with duckdb.connect(config={'memory_limit':'256MB','threads':'1','temp_directory':str(pasta/'spill'),
                                    'max_temp_directory_size':'4GB'}) as con:
            con.read_parquet(str(fonte)).create_view('base')
            esquema=[list(x[:2]) for x in con.execute('DESCRIBE base').fetchall()]
            conferir_esquema(esquema,exigir_rede=True)
            ruins=con.execute('''SELECT count(*) FILTER(WHERE NU_SEQUENCIAL IS NULL OR trim(NU_SEQUENCIAL)=''
                OR NU_ANO IS DISTINCT FROM 2025),count(*)-count(DISTINCT NU_SEQUENCIAL) FROM base''').fetchone()
            if any(ruins):
                raise ValueError('Chave/ano inválidos na trusted.')
            resultado,controles=calcular_rede_escolar(con)
        depois=sha256(fonte)
        if antes!=depois:
            raise ValueError('Trusted alterada durante a análise escolar.')
        report=dict(data_utc=datetime.now(timezone.utc).isoformat(),fonte=fonte.relative_to(raiz).as_posix(),
            sha256_antes=antes,sha256_depois=depois,esquema=esquema,duckdb=duckdb.__version__,
            memory_limit='256MB',threads=1,contrato='docs/contrato_analitico_rede_escolar_2025.md',
            controles=controles,validacao='aprovada',
            resultado=resultado,hashes_csv={})
        saidas=[]
        for nome,linhas in resultado.items():
            arquivo=pasta/f'rede_escolar_2025_{nome}.csv'
            campos=list(linhas[0])
            with arquivo.open('w',encoding='utf-8',newline='') as f:
                w=csv.DictWriter(f,fieldnames=campos);w.writeheader();w.writerows(linhas)
            report['hashes_csv'][arquivo.name]=sha256(arquivo)
            saidas.append(arquivo)
        report['segundos']=round(time.monotonic()-inicio,3)
        auditoria=pasta/'validacao_rede_escolar_2025.json'
        auditoria.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
        (raiz/'analitica').mkdir(exist_ok=True);(raiz/'reports').mkdir(exist_ok=True)
        for arquivo in saidas:
            os.replace(arquivo,raiz/'analitica'/arquivo.name)
        os.replace(auditoria,raiz/'reports'/auditoria.name)
    return resultado,report


if __name__=='__main__':
    resultado,report=executar_rede_escolar()
    print(json.dumps(report['controles'],ensure_ascii=False,indent=2))
