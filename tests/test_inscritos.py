import csv
from pathlib import Path
import tempfile
import unittest
import duckdb
from src.inscritos_execucao import contar_participantes


class InscritosTest(unittest.TestCase):
    def test_latin1_chave_ano_e_parser_estrito(self):
        with tempfile.TemporaryDirectory() as temp:
            p=Path(temp)/'participantes.csv'
            for corpo,erro in [('001;2025;São Luís\n002;2025;Açúcar\n',False),
                               ('001;2025;x\n001;2025;y\n',True),
                               (';2025;x\n',True),('001;2024;x\n',True),
                               ('001;2025\n',True)]:
                p.write_text('NU_INSCRICAO;NU_ANO;EXTRA\n'+corpo,encoding='latin-1')
                with duckdb.connect() as con:
                    if erro:
                        with self.assertRaises((ValueError,duckdb.Error)):
                            contar_participantes(con,p)
                    else:
                        self.assertEqual(contar_participantes(con,p)['registros'],2)
