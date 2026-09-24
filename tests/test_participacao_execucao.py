"""Valida alertas, exportação e bloqueio de chave sem usar a base real."""
import csv
import json
from pathlib import Path
import tempfile
import unittest
import duckdb
from src.trusted_resultados import TIPOS_LEGADOS as TIPOS
from src.participacao_execucao import executar_participacao
from src.desempenho_execucao import hash_arquivo


class ParticipacaoExportacaoTest(unittest.TestCase):
    def test_alertas_exports_e_chave_duplicada(self):
        with tempfile.TemporaryDirectory() as temp:
            raiz=Path(temp).resolve()
            (raiz/'src').mkdir(); (raiz/'src/desempenho.py').touch()
            (raiz/'trusted').mkdir()
            fonte=raiz/'trusted/resultados_2025_base.parquet'
            with duckdb.connect() as con:
                con.execute('CREATE TABLE dados('+','.join(f'{k} {v}' for k,v in TIPOS.items())+')')
                con.execute('''INSERT INTO dados VALUES
                    ('1',2025,1,1,1,1,NULL,NULL,NULL,NULL),
                    ('2',2025,2,0,1,2,NULL,NULL,NULL,NULL),
                    ('3',2025,0,1,NULL,0,NULL,NULL,NULL,NULL),
                    ('4',2025,1,0,9,1,NULL,NULL,NULL,NULL)''')
                con.execute('COPY dados TO ? (FORMAT PARQUET)',[str(fonte)])
                original=hash_arquivo(fonte)
                resultado,report=executar_participacao(raiz)
                self.assertEqual(report['validacao'],'aprovada_com_alertas')
                self.assertEqual(len(report['alertas_pares']),3)
                self.assertEqual(resultado['resumo']['retencao_percentual'],100)
                self.assertEqual(hash_arquivo(fonte),original)
                self.assertTrue(all(report['controles'].values()))
                for nome,h in report['hashes_csv'].items():
                    self.assertEqual(hash_arquivo(raiz/'analitica'/nome),h)
                with (raiz/'analitica/participacao_2025_transicoes.csv').open(encoding='utf-8') as f:
                    self.assertEqual(len(list(csv.DictReader(f))),36)
                auditoria=raiz/'reports/validacao_participacao_2025.json'
                self.assertEqual(json.loads(auditoria.read_text(encoding='utf-8'))['resultado'],resultado)
                anterior=hash_arquivo(auditoria)
                con.execute("INSERT INTO dados SELECT * FROM dados WHERE NU_SEQUENCIAL='1'")
                con.execute('COPY dados TO ? (FORMAT PARQUET)',[str(raiz/'duplicada.parquet')])
                (raiz/'duplicada.parquet').replace(fonte)
                with self.assertRaisesRegex(ValueError,'duplicadas=1'):
                    executar_participacao(raiz)
                self.assertEqual(hash_arquivo(auditoria),anterior)
