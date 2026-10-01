"""Riscos novos: entrada mínima estrita e comparação de denominadores distintos."""
import tempfile
import unittest
from pathlib import Path
import duckdb
from src.participacao_entrada import preparar_participacao
from src.participacao import agregar_combinacoes
from src.participacao_comparacao import comparar_participacao
from src.trusted_resultados import sha256


class Participacao2024Test(unittest.TestCase):
    def test_entrada_preserva_nulos_invalidos_e_bloqueia_conversao(self):
        with tempfile.TemporaryDirectory() as temp:
            raiz = Path(temp)
            (raiz/'src').mkdir(); (raiz/'src/trusted_resultados.py').touch()
            raw = raiz/'raw/microdados_enem_2024/microdados_enem_2024/DADOS/RESULTADOS_2024.csv'
            raw.parent.mkdir(parents=True)
            cabecalho = 'NU_SEQUENCIAL;NU_ANO;TP_PRESENCA_CN;TP_PRESENCA_CH;TP_PRESENCA_LC;TP_PRESENCA_MT\n'
            raw.write_text(cabecalho+'001;2024;1;1;1;1\n002;2024;0;1;;9\n', encoding='latin-1')
            controle = preparar_participacao(raiz)
            self.assertEqual(controle['total_saida'], 2)
            self.assertEqual(controle['nulos']['TP_PRESENCA_LC'], 1)
            self.assertEqual(controle['codigos_invalidos']['TP_PRESENCA_MT'], 1)
            parquet = raiz/controle['parquet']; antes = sha256(parquet)
            with duckdb.connect() as con:
                self.assertEqual(con.read_parquet(str(parquet)).filter("NU_SEQUENCIAL='001'").count('*').fetchone()[0], 1)
            raw.write_text(cabecalho+'003;2024;1.5;1;1;1\n', encoding='latin-1')
            with self.assertRaisesRegex(ValueError, 'conversão'):
                preparar_participacao(raiz)
            self.assertEqual(sha256(parquet), antes)
            raw.write_text(cabecalho+'001;2024;1;1;1;1\n001;2024;1;1;1;1\n', encoding='latin-1')
            with self.assertRaisesRegex(ValueError, 'chave'):
                preparar_participacao(raiz)
            self.assertEqual(sha256(parquet), antes)

    def test_comparacao_usa_taxas_anuais_e_retencao_propria(self):
        a = agregar_combinacoes([(1,1,1,1,50),(1,1,0,0,30),(0,0,0,0,20)])
        b = agregar_combinacoes([(1,1,1,1,90),(1,1,0,0,10),(0,0,0,0,100)])
        linhas = comparar_participacao({2024:a, 2025:b})['comparacao']
        dia1 = next(x for x in linhas if x['indicador']=='presenca_dia1')
        ret = next(x for x in linhas if x['indicador']=='retencao')
        self.assertEqual(dia1['diferenca_pp_2025_menos_2024'], -30)
        self.assertEqual(ret['diferenca_pp_2025_menos_2024'], 27.5)
        self.assertEqual(ret['denominador_2024'], 80)
