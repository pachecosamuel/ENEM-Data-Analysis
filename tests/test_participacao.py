from itertools import product
import unittest
import duckdb
from src.participacao import (STATUS,classificar_par,agregar_combinacoes,validar_participacao,calcular_participacao)
from src.participacao_graficos import porcentagem


class ParticipacaoTest(unittest.TestCase):
    def test_todas_transicoes_e_ordem(self):
        pares=[(1,1),(0,0),(2,2),(1,0),(None,1),(9,0)]
        grupos=[(*a,*b,1) for a,b in product(pares,repeat=2)]
        r=agregar_combinacoes(grupos)
        self.assertEqual(r,agregar_combinacoes(list(reversed(grupos))))
        self.assertTrue(all(validar_participacao(r).values()))
        self.assertEqual(len(r['transicoes']),36)
        self.assertTrue(all(x['quantidade']==1 for x in r['transicoes']))
        self.assertEqual(r['resumo']['total_base'],36)
        self.assertEqual(r['resumo']['demais_situacoes'],32)
        self.assertAlmostEqual(r['resumo']['retencao_percentual'],100/6)
        self.assertEqual(classificar_par(9,None),'codigo_invalido')
        self.assertEqual(classificar_par(1,2),'misto')
        self.assertEqual(classificar_par(0,1),'misto')
        extras=[(None,1,1,1,1),(-1,1,1,1,1)]
        self.assertEqual(agregar_combinacoes(extras),agregar_combinacoes(list(reversed(extras))))

    def test_retencao_e_diferenca_nao_sao_faltas(self):
        grupos=[(1,1,1,1,10),(1,1,0,0,3),(0,0,1,1,2),(1,1,2,2,1),
                (2,2,1,1,4),(0,0,0,0,5),(1,0,0,1,2)]
        r=agregar_combinacoes(grupos)['resumo']
        self.assertEqual(r['presentes_dia1'],14)
        self.assertEqual(r['presentes_dia2'],16)
        self.assertEqual(r['somente_primeiro_ausente_segundo'],3)
        self.assertEqual(r['somente_segundo_ausente_primeiro'],2)
        self.assertEqual(r['demais_situacoes'],7)
        self.assertEqual(r['diferenca_liquida_dia2_menos_dia1'],2)
        self.assertAlmostEqual(r['retencao_percentual'],1000/14)

    def test_vazio_sem_presentes_e_percentual_pequeno(self):
        for grupos in ([],[(0,0,0,0,2)]):
            r=agregar_combinacoes(grupos)
            self.assertTrue(all(validar_participacao(r).values()))
            self.assertIsNone(r['resumo']['retencao_percentual'])
        self.assertEqual(porcentagem(0),'0%')
        self.assertEqual(porcentagem(.0001),'<0,01%')
        self.assertEqual(porcentagem(None),'não se aplica')

    def test_sql_recontagem_com_nulos_e_mistos(self):
        with duckdb.connect() as con:
            con.execute('CREATE TABLE base(TP_PRESENCA_LC INTEGER, TP_PRESENCA_CH INTEGER, TP_PRESENCA_CN INTEGER, TP_PRESENCA_MT INTEGER)')
            con.execute('INSERT INTO base VALUES (1,1,1,1),(1,0,2,2),(NULL,1,0,0),(9,0,1,1)')
            r,controles=calcular_participacao(con)
        self.assertTrue(all(controles.values()))
        self.assertEqual(r['resumo']['total_base'],4)
        self.assertEqual(sum(x['quantidade'] for x in r['pares'] if x['dia']==1 and x['status']=='misto'),1)
