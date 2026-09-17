import unittest
import duckdb
from src.desempenho import AREAS, calcular_desempenho


def conexao_fixture(linhas):
    con = duckdb.connect()
    campos = [f'TP_PRESENCA_{a} INTEGER' for a in AREAS] + [f'NU_NOTA_{a} DECIMAL(10,1)' for a in AREAS]
    con.execute('CREATE TABLE base (' + ','.join(campos) + ')')
    if linhas:
        con.executemany('INSERT INTO base VALUES (?,?,?,?,?,?,?,?)', linhas)
    return con


class DesempenhoTest(unittest.TestCase):
    def test_fixture_manual_e_ordem(self):
        linhas = [
            (1,1,1,0, 0,10,None,None),
            (1,1,0,1, 10,20,99,1001),
            (1,0,2,2, 20,None,None,None),
            (1,2,1,0, 30,77,12.5,None),
            (1,1,0,0, None,40,None,None),
            (0,1,0,0, 900,80,None,None),
            (2,1,0,0, 800,None,None,None),
        ]
        with conexao_fixture(linhas) as con:
            resultados, _ = calcular_desempenho(con)
        with conexao_fixture(list(reversed(linhas))) as con:
            invertidos, _ = calcular_desempenho(con)
        self.assertEqual(resultados, invertidos)
        cn,ch,lc,mt = resultados
        for campo, esperado in {'elegiveis':4,'presentes':5,'presentes_sem_nota':1,
                                'zeros_elegiveis':1,'media':15,'q1':7.5,'mediana':15,'q3':22.5,
                                'notas_fora_presentes':2}.items():
            self.assertEqual(cn[campo],esperado)
        for campo, esperado in {'elegiveis':4,'media':37.5,'q1':17.5,'mediana':30,'q3':50}.items():
            self.assertEqual(ch[campo],esperado)
        self.assertEqual(lc['elegiveis'],1)
        self.assertEqual(lc['mediana'],12.5)
        self.assertEqual(mt['elegiveis'],1)
        self.assertEqual(mt['q3'],1001)
        self.assertAlmostEqual(cn['pct_completude_presentes'],80)
        self.assertAlmostEqual(cn['pct_elegiveis_base'],400/7)

    def test_interpolacao_nao_trunca_decimal(self):
        with conexao_fixture([(1,1,1,1,0,0,0,0),(1,1,1,1,0.1,0.1,0.1,0.1)]) as con:
            resultados,_=calcular_desempenho(con)
        self.assertAlmostEqual(resultados[0]['q1'],.025)
        self.assertAlmostEqual(resultados[0]['mediana'],.05)
        self.assertAlmostEqual(resultados[0]['q3'],.075)

    def test_vazio_e_sem_elegiveis(self):
        for linhas in ([],[(None,0,2,1,None,None,None,None)]):
            with conexao_fixture(linhas) as con:
                resultados,_=calcular_desempenho(con)
            for r in resultados:
                self.assertEqual(r['elegiveis'],0)
                self.assertIsNone(r['media'])
                self.assertIsNone(r['mediana'])
            if not linhas:
                self.assertIsNone(resultados[0]['pct_completude_base'])

    def test_categoria_invalida_bloqueia(self):
        with conexao_fixture([(9,0,0,0,10,None,None,None)]) as con:
            with self.assertRaises(ValueError):
                calcular_desempenho(con)
