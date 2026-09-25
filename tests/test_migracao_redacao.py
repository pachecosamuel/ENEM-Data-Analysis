import csv
from pathlib import Path
import tempfile
import unittest
import duckdb
from src.trusted_resultados import (CAMPOS, TIPOS_LEGADOS, FONTE, executar,
                                    conferir_esquema, ErroContrato, sha256, TIPOS)
from src.redacao_execucao import executar_redacao


class MigracaoTest(unittest.TestCase):
    def test_migracao_exata_rollback_e_bloqueio_de_valor_legado(self):
        with tempfile.TemporaryDirectory() as temp:
            raiz=Path(temp)
            (raiz/'src').mkdir(); (raiz/'src/trusted_resultados.py').touch()
            (raiz/'trusted').mkdir()
            p=raiz/'trusted/resultados_2025_base.parquet'
            with duckdb.connect() as con:
                con.execute('CREATE TABLE t('+','.join(f'{k} {v}' for k,v in TIPOS_LEGADOS.items())+')')
                con.execute("INSERT INTO t VALUES ('001',2025,1,1,1,1,500,500,500,500)")
                con.execute('COPY t TO ? (FORMAT PARQUET)',[str(p)])
            antes=sha256(p)
            raw=raiz/FONTE; raw.parent.mkdir(parents=True)
            linha=['001','2025',*(['1']*4),*(['500']*4),'1','500',*(['100']*5),'3550308','São Paulo','35','SP','2']
            def gravar():
                with raw.open('w',encoding='latin-1',newline='') as f:
                    w=csv.writer(f,delimiter=';'); w.writerow(CAMPOS); w.writerow(linha)
            gravar()
            report=executar(raiz)
            self.assertEqual(report['regressao_legado']['divergencias'],0)
            self.assertEqual(sha256(raiz/report['rollback_parquet']),antes)
            atual=sha256(p)
            resultado,auditoria=executar_redacao(raiz)
            self.assertEqual(resultado['final'][0]['n'],1)
            self.assertEqual(auditoria['sha256_depois'],atual)
            self.assertTrue(all(sha256(raiz/'analitica'/n)==h for n,h in auditoria['hashes_csv'].items()))
            linha[6]='501'; gravar()
            with self.assertRaisesRegex(ErroContrato,'campos legados'):
                executar(raiz)
            self.assertEqual(sha256(p),atual)

    def test_esquema_nao_aceita_extensao_parcial_ou_tipo_trocado(self):
        completo=[list(x) for x in TIPOS.items()]
        conferir_esquema(completo,exigir_redacao=True)
        for esquema in (completo[:-2], [*completo[:-1],['NU_NOTA_COMP5','DOUBLE']]):
            with self.assertRaises(ValueError):conferir_esquema(esquema)

    def test_status_e_precisao_redacao_invalidos_bloqueiam(self):
        from src.trusted_resultados import padronizar
        for campo,valor in [('TP_STATUS_REDACAO','5'),('NU_NOTA_COMP1','10.33'),('NU_NOTA_REDACAO','abc')]:
            with duckdb.connect() as con:
                con.execute('CREATE TABLE entrada('+','.join(f'{c} VARCHAR' for c in CAMPOS)+')')
                linha=['001','2025',*(['1']*4),*(['500']*4),'1','500',*(['100']*5),'3550308','São Paulo','35','SP','2']
                linha[CAMPOS.index(campo)]=valor
                con.executemany('INSERT INTO entrada VALUES ('+','.join('?' for c in CAMPOS)+')',[linha])
                with self.assertRaises(ErroContrato):padronizar(con)
