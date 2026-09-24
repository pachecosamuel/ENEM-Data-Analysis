"""Fixtures com zeros, nulos, status e denominadores diferentes."""
import unittest
import duckdb
from src.redacao import calcular_redacao


class RedacaoTest(unittest.TestCase):
    def base(self, linhas):
        con=duckdb.connect()
        self.addCleanup(con.close)
        con.execute('CREATE TABLE base(TP_STATUS_REDACAO TINYINT, NU_NOTA_REDACAO DECIMAL(10,1),'
                    + ','.join(f'NU_NOTA_COMP{i} DECIMAL(10,1)' for i in range(1,6))
                    + ',TP_PRESENCA_LC TINYINT, TP_PRESENCA_CH TINYINT)')
        if linhas:
            con.executemany('INSERT INTO base VALUES (?,?,?,?,?,?,?,?,?)',linhas)
        return con

    def test_zeros_status_nulos_e_recorte_comum(self):
        con=self.base([
            (1,0,0,0,0,0,0,1,1),
            (1,500,100,100,100,100,100,0,0), # Não filtra redação pela presença LC.
            (4,0,0,0,0,0,0,1,1),
            (None,None,None,None,None,None,None,0,0),
            (1,400,100,None,100,100,100,1,1),
            (None,100,20,20,20,20,20,1,1),
            (2,None,None,None,None,None,None,2,2)])
        r,c=calcular_redacao(con)
        final=r['final'][0]
        self.assertEqual((final['n'],final['sem_nota'],final['zeros']),(5,2,2))
        self.assertEqual((final['media'],final['mediana'],final['q1'],final['q3']),(200,100,0,400))
        self.assertTrue(all(x['n']==2 and x['media']==50 for x in r['competencias']))
        self.assertEqual((c['incompletas_sem_problemas'],c['nota_sem_status'],c['status_sem_nota']),(1,1,1))
        self.assertTrue(all(c['reconciliacoes'].values()))

    def test_soma_divergente_reportada_sem_corrigir(self):
        con=self.base([(1,501,100,100,100,100,100,1,1),(2,20,0,0,0,0,0,1,1)])
        r,c=calcular_redacao(con)
        self.assertEqual(c['soma_divergente'],2)
        self.assertEqual(c['soma_divergente_recorte'],1)
        self.assertEqual(c['positivas_status_problematico'],1)
        self.assertEqual(r['final'][0]['maximo_observado'],501)

    def test_sem_notas_e_sem_denominador(self):
        for linhas in ([],[(None,None,None,None,None,None,None,0,0)]):
            with self.subTest(linhas=linhas):
                r,c=calcular_redacao(self.base(linhas))
                self.assertEqual(r['final'][0]['n'],0)
                self.assertIsNone(r['final'][0]['media'])
                self.assertTrue(all(x['n']==0 and x['mediana'] is None for x in r['competencias']))
                self.assertTrue(all(c['reconciliacoes'].values()))

    def test_status_invalido_bloqueia(self):
        with self.assertRaisesRegex(ValueError,'Situação'):
            calcular_redacao(self.base([(5,0,0,0,0,0,0,1,1)]))

    def test_fora_escala_e_quartil_interpolado(self):
        r,c=calcular_redacao(self.base([(1,0,0,0,0,0,0,1,1),(1,1001,201,200,200,200,200,1,1)]))
        self.assertEqual(r['final'][0]['q1'],250.25)
        self.assertEqual((c['final_fora_escala'],c['competencias_fora_escala']),(1,1))
