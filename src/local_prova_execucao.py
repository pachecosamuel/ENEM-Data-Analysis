"""Leitura auditada da trusted e publicação dos agregados territoriais."""
import csv
import json
import os
from pathlib import Path
import tempfile
import time
from datetime import datetime, timezone

import duckdb
from src.trusted_resultados import raiz_projeto, sha256, conferir_esquema
from src.local_prova import calcular_local_prova
from src.local_prova_referencia import REFERENCIA, ARQUIVO_REFERENCIA


def executar_local_prova(raiz=None):
    raiz=raiz_projeto(raiz)
    fonte=raiz/'trusted/resultados_2025_base.parquet'
    inicio=time.monotonic()
    antes=sha256(fonte)
    (raiz/'work').mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='local_prova_',dir=raiz/'work') as temp:
        pasta=Path(temp)
        with duckdb.connect(config={'memory_limit':'256MB','threads':'1','temp_directory':str(pasta/'spill'),
                                    'max_temp_directory_size':'4GB'}) as con:
            con.read_parquet(str(fonte)).create_view('base')
            esquema=[list(x[:2]) for x in con.execute('DESCRIBE base').fetchall()]
            conferir_esquema(esquema,exigir_local=True)
            ruins=con.execute('''SELECT count(*) FILTER(WHERE NU_SEQUENCIAL IS NULL OR trim(NU_SEQUENCIAL)=''
                OR NU_ANO IS DISTINCT FROM 2025),count(*)-count(DISTINCT NU_SEQUENCIAL) FROM base''').fetchone()
            if any(ruins):
                raise ValueError('Chave/ano inválidos na trusted.')
            resultado,controles=calcular_local_prova(con)
        depois=sha256(fonte)
        if antes!=depois:
            raise ValueError('Trusted alterada durante a análise territorial.')
        cobertura=controles['cobertura']
        alerta_local=cobertura['registros_nao_classificados'] or any(cobertura['achados'].values())
        nacional=next(r for r in resultado['participacao'] if r['nivel']=='Brasil')
        alerta_presenca=any(nacional[f'{s}_dia{d}'] for s in ('misto','dados_ausentes','codigo_invalido') for d in (1,2))
        report=dict(data_utc=datetime.now(timezone.utc).isoformat(),fonte=fonte.relative_to(raiz).as_posix(),
            sha256_antes=antes,sha256_depois=depois,esquema=esquema,duckdb=duckdb.__version__,
            memory_limit='256MB',threads=1,contrato='docs/contrato_analitico_local_prova_2025.md',
            referencia_ibge=REFERENCIA,sha256_referencia=sha256(ARQUIVO_REFERENCIA),
            controles=controles,validacao='aprovada_com_alertas' if alerta_local or alerta_presenca else 'aprovada',
            resultado=resultado,hashes_csv={})
        saidas=[]
        for nome,linhas in resultado.items():
            arquivo=pasta/f'local_prova_2025_{nome}.csv'
            campos=list(linhas[0]) if linhas else ['grupo','posicao','uf','presentes_dia2','total_base','taxa_presenca_dia2']
            with arquivo.open('w',encoding='utf-8',newline='') as f:
                w=csv.DictWriter(f,fieldnames=campos);w.writeheader();w.writerows(linhas)
            report['hashes_csv'][arquivo.name]=sha256(arquivo)
            saidas.append(arquivo)
        report['segundos']=round(time.monotonic()-inicio,3)
        auditoria=pasta/'validacao_local_prova_2025.json'
        auditoria.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
        (raiz/'analitica').mkdir(exist_ok=True);(raiz/'reports').mkdir(exist_ok=True)
        for arquivo in saidas:
            os.replace(arquivo,raiz/'analitica'/arquivo.name)
        os.replace(auditoria,raiz/'reports'/auditoria.name)
    return resultado,report


if __name__=='__main__':
    resultado,report=executar_local_prova()
    print(json.dumps({'cobertura':report['controles']['cobertura'],
        'regioes':[r for r in resultado['participacao'] if r['nivel']=='Região'],
        'top3':resultado['top3_ufs']},ensure_ascii=False,indent=2))
