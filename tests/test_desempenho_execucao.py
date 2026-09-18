"""Integração pequena: exportação de extremos e imports após reorganização."""
import csv
import json
from pathlib import Path
import tempfile
import unittest

import duckdb
from src.desempenho import AREAS
from src.desempenho_execucao import executar_desempenho, hash_arquivo, raiz_projeto


class ExportacaoTest(unittest.TestCase):
    def test_exporta_extremos_e_preserva_fonte(self):
        with tempfile.TemporaryDirectory() as temp:
            raiz = Path(temp).resolve()
            (raiz/'src').mkdir()
            (raiz/'src/desempenho.py').touch()
            (raiz/'trusted').mkdir()
            (raiz/'notebooks').mkdir()
            (raiz/'apresentacao').mkdir()
            fonte = raiz/'trusted/resultados_2025_base.parquet'
            campos = ['NU_SEQUENCIAL VARCHAR', 'NU_ANO INTEGER']
            campos += [f'TP_PRESENCA_{a} TINYINT' for a in AREAS]
            campos += [f'NU_NOTA_{a} DECIMAL(10,1)' for a in AREAS]
            with duckdb.connect() as con:
                con.execute('CREATE TABLE dados (' + ','.join(campos) + ')')
                con.execute("INSERT INTO dados VALUES ('1',2025,1,1,1,1,0,0,0,0), ('2',2025,1,1,1,1,1200.1,1200.1,1200.1,1200.1)")
                con.execute('COPY dados TO ? (FORMAT PARQUET)', [str(fonte)])
            antes = hash_arquivo(fonte)
            for pasta in ('notebooks','apresentacao'):
                self.assertEqual(raiz_projeto(raiz/pasta), raiz)
            resultados, relatorio = executar_desempenho(raiz)
            self.assertEqual(hash_arquivo(fonte), antes)
            with (raiz/'analitica/desempenho_2025.csv').open(encoding='utf-8', newline='') as f:
                linhas = list(csv.DictReader(f))
            self.assertEqual(len(linhas),4)
            self.assertEqual(float(linhas[0]['minimo_observado']),0)
            self.assertEqual(float(linhas[0]['maximo_observado']),1200.1)
            salvo=json.loads((raiz/'reports/validacao_desempenho_2025.json').read_text(encoding='utf-8'))
            self.assertEqual(salvo['indicadores'], resultados)
            self.assertEqual(relatorio['sha256_indicadores_csv'],hash_arquivo(raiz/'analitica/desempenho_2025.csv'))
