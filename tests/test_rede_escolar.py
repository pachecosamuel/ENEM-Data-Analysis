"""Três verificações essenciais: recortes, domínio e proteção da v3."""
from pathlib import Path
import tempfile
import unittest
import duckdb
from src.rede_escolar import calcular_rede_escolar
from src.trusted_resultados import (TIPOS, TIPOS_V3, CAMPOS, padronizar,
                                    conferir_legado, ErroContrato)


class RedeEscolarTest(unittest.TestCase):
    def criar(self, con, nome='base'):
        con.execute(f'CREATE TABLE {nome} (' + ','.join(f'{k} {v}' for k, v in TIPOS.items()) + ')')

    def inserir(self, con, codigo, rede, nota, presenca=1, tabela='base'):
        linha = dict.fromkeys(TIPOS)
        linha.update(NU_SEQUENCIAL=str(codigo), NU_ANO=2025, TP_DEPENDENCIA_ADM_ESC=rede)
        for area in ('CN', 'CH', 'LC', 'MT'):
            linha[f'TP_PRESENCA_{area}'] = presenca
            linha[f'NU_NOTA_{area}'] = nota
        con.execute(f'INSERT INTO {tabela} VALUES (' + ','.join('?' for _ in TIPOS) + ')', list(linha.values()))

    def test_cobertura_nulos_zeros_ausentes_e_quartis(self):
        with duckdb.connect() as con:
            self.criar(con)
            for i, (rede, nota, presenca) in enumerate([
                (1, 0, 1), (1, 100, 1), (1, 200, 1), (1, 300, 1),
                (1, 900, 0), (1, None, 1), (2, 500, 1), (4, 600, 1), (None, 1000, 1)]):
                self.inserir(con, i, rede, nota, presenca)
            r, c = calcular_rede_escolar(con)
            self.assertEqual((c['total_base'], c['rede_valida'], c['rede_nula']), (9, 8, 1))
            federal = r['desempenho'][0]
            self.assertEqual((federal['elegiveis'], federal['zeros_elegiveis']), (4, 1))
            self.assertEqual([federal[k] for k in ('q1', 'mediana', 'q3')], [75, 150, 225])
            municipal = next(x for x in r['desempenho'] if x['codigo'] == 3)
            self.assertEqual(municipal['elegiveis'], 0)
            self.assertIsNone(municipal['mediana'])
            self.assertEqual(con.execute('SELECT count(*) FROM base').fetchone()[0], 9)

    def test_codigo_invalido_bloqueia_trusted_e_analise(self):
        with duckdb.connect() as con:
            self.criar(con)
            self.inserir(con, 1, 5, 500)
            with self.assertRaisesRegex(ValueError, 'inválidos'):
                calcular_rede_escolar(con)
            con.execute('CREATE TABLE entrada AS SELECT ' + ','.join(f'CAST({k} AS VARCHAR) {k}' for k in CAMPOS) + ' FROM base')
            with self.assertRaises(ErroContrato) as erro:
                padronizar(con)
            self.assertEqual(erro.exception.relatorio['categorias_inesperadas']['TP_DEPENDENCIA_ADM_ESC'],
                             [{'valor': '5', 'quantidade': 1}])

    def test_migracao_protege_os_21_campos_v3(self):
        with tempfile.TemporaryDirectory() as temp, duckdb.connect() as con:
            self.criar(con, 'padronizados')
            self.inserir(con, 1, 2, 500, tabela='padronizados')
            arquivo = Path(temp) / 'v3.parquet'
            con.execute('COPY (SELECT ' + ','.join(TIPOS_V3) + ' FROM padronizados) TO ? (FORMAT PARQUET)', [str(arquivo)])
            check = conferir_legado(con, arquivo, {})
            self.assertEqual(len(check['campos']), 21)
            self.assertEqual(check['divergencias'], 0)
            con.execute('DROP VIEW anterior')
            con.execute("UPDATE padronizados SET SG_UF_PROVA='SP'")
            with self.assertRaisesRegex(ErroContrato, 'campos legados'):
                conferir_legado(con, arquivo, {})
