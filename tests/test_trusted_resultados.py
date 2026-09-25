"""Casos de borda do contrato; não usam os microdados reais."""
import csv
from decimal import Decimal
from pathlib import Path
import tempfile
import unittest

import duckdb

from src.trusted_resultados import (CAMPOS, ErroContrato, ler_selecionados,
                                    padronizar, validar, reconciliar, executar, FONTE, sha256)


class ContratoTest(unittest.TestCase):
    def carregar(self, linhas):
        con = duckdb.connect()
        self.addCleanup(con.close)
        con.execute('CREATE TABLE entrada (' + ','.join(f'{c} VARCHAR' for c in CAMPOS) + ')')
        con.executemany('INSERT INTO entrada VALUES (' + ','.join('?' for _ in CAMPOS) + ')', linhas)
        return con

    def linha(self, identificador='0001', ano='2025', presenca='1', nota='0.0'):
        return [identificador, ano, *([presenca] * 4), *([nota] * 4), '1', *(['0'] * 6), '3550308', 'São Paulo', '35', 'SP', '2']

    def test_nulos_zero_texto_e_coerencia_sem_exclusao(self):
        con = self.carregar([self.linha(), self.linha('0002', presenca='0', nota=''),
                             self.linha('0003', presenca='1', nota=None),
                             self.linha('0004', presenca='2', nota='500.5')])
        padronizar(con)
        self.assertEqual(con.execute('SELECT NU_SEQUENCIAL, NU_NOTA_CN FROM padronizados '
                                    'ORDER BY NU_SEQUENCIAL LIMIT 1').fetchone(), ('0001', Decimal('0.0')))
        r = validar(con)
        self.assertEqual(r['registros'], 4)
        self.assertEqual(r['nulos']['NU_NOTA_CN'], 2)
        self.assertEqual(r['por_area']['CN']['presente_sem_nota'], 1)
        self.assertEqual(r['por_area']['CN']['eliminado_com_nota'], 1)

    def test_falhas_nao_viram_nulos_silenciosos(self):
        for campo, valor in [('NU_ANO', '2025.5'), ('NU_NOTA_CN', 'abc'),
                              ('NU_NOTA_CN', '12.34'), ('TP_PRESENCA_CN', '9')]:
            with self.subTest(campo=campo, valor=valor):
                linha = self.linha()
                linha[CAMPOS.index(campo)] = valor
                con = self.carregar([linha])
                with self.assertRaises(ErroContrato) as erro:
                    padronizar(con)
                r = erro.exception.relatorio
                self.assertTrue(any(r['falhas_conversao'].values()) or any(r['categorias_inesperadas'].values()))

    def test_chave_nula_duplicada_e_ano_reportados(self):
        con = self.carregar([self.linha(), self.linha(), self.linha(None, ano='2024')])
        padronizar(con)
        r = validar(con)
        self.assertEqual(r['nulos']['NU_SEQUENCIAL'], 1)
        self.assertEqual(r['chaves_duplicadas'], 1)
        self.assertEqual(r['linhas_excedentes_chave'], 1)
        self.assertEqual(r['anos'][0]['ano'], 2024)

    def test_reconciliacao_detecta_valor_alterado(self):
        con = self.carregar([self.linha('1', nota='400.0'), self.linha('2', nota='500.0')])
        padronizar(con)
        esperado = validar(con)
        con.execute('CREATE TABLE releitura AS SELECT * FROM padronizados')
        reconciliar(con, esperado, {})
        # Troca mantém os agregados iguais: só a comparação por chave a detecta.
        con.execute('UPDATE releitura SET NU_NOTA_CN=900.0-NU_NOTA_CN')
        with self.assertRaises(ErroContrato):
            reconciliar(con, esperado, {})

    def test_csv_latin1_coluna_extra_e_erro_estrutural(self):
        with tempfile.TemporaryDirectory() as pasta:
            arquivo = Path(pasta) / 'teste.csv'
            with arquivo.open('w', encoding='latin-1', newline='') as f:
                w = csv.writer(f, delimiter=';')
                w.writerow([*CAMPOS, 'LOCAL'])
                w.writerow([*self.linha(), 'São Luís'])
                w.writerow([*self.linha('0002', nota=''), 'Açúcar'])
            con = duckdb.connect()
            self.addCleanup(con.close)
            self.assertEqual(ler_selecionados(con, arquivo), 2)
            padronizar(con)
            self.assertEqual(validar(con)['nulos']['NU_NOTA_CN'], 1)
            self.assertEqual(con.execute("SELECT LOCAL FROM read_csv(?, delim=';', encoding='latin-1') LIMIT 1",
                                         [str(arquivo)]).fetchone()[0], 'São Luís')
            arquivo.write_text(';'.join(CAMPOS) + '\n1;2025\n', encoding='latin-1')
            with duckdb.connect() as outro:
                with self.assertRaises(duckdb.Error):
                    ler_selecionados(outro, arquivo)

    def test_publicacao_reexecucao_e_falha_preservam_saida_anterior(self):
        with tempfile.TemporaryDirectory() as pasta:
            raiz = Path(pasta)
            (raiz / 'src').mkdir()
            (raiz / 'src/trusted_resultados.py').touch()
            fonte = raiz / FONTE
            fonte.parent.mkdir(parents=True)
            def gravar(linhas):
                with fonte.open('w', encoding='latin-1', newline='') as f:
                    w = csv.writer(f, delimiter=';')
                    w.writerow(CAMPOS)
                    w.writerows(linhas)
            gravar([self.linha('1'), self.linha('2', presenca='0', nota='')])
            original = sha256(fonte)
            primeiro = executar(raiz)
            self.assertTrue(primeiro['publicado'])
            self.assertEqual(primeiro['releitura']['registros'], 2)
            self.assertEqual(sha256(fonte), original)
            executar(raiz)
            destino = raiz / 'trusted/resultados_2025_base.parquet'
            anterior = sha256(destino)
            gravar([self.linha('1', presenca='9')])
            with self.assertRaises(ErroContrato):
                executar(raiz)
            self.assertEqual(sha256(destino), anterior)
            self.assertEqual(list((raiz / 'work').iterdir()), [])


if __name__ == '__main__':
    unittest.main()
