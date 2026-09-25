"""Territórios, populações distintas, pesos, ausências e proteção da migração."""
import csv
from pathlib import Path
import tempfile
import unittest

import duckdb
from src.trusted_resultados import TIPOS, TIPOS_V2, CAMPOS, FONTE, executar, ErroContrato, sha256
from src.local_prova import calcular_local_prova, top3_ufs
from src.local_prova_referencia import UFS, preparar_local, auditar_local
from src.local_prova_execucao import executar_local_prova


def linha(chave,uf='SP',codigo='35',nota=100,presenca=1,**alteracoes):
    r=dict.fromkeys(TIPOS)
    r.update(NU_SEQUENCIAL=str(chave),NU_ANO=2025,CO_UF_PROVA=codigo,SG_UF_PROVA=uf,
             CO_MUNICIPIO_PROVA=codigo+'00001' if codigo else None,NO_MUNICIPIO_PROVA='Município de teste')
    for a in ('CN','CH','LC','MT'):
        r[f'TP_PRESENCA_{a}']=presenca;r[f'NU_NOTA_{a}']=nota
    r.update(alteracoes)
    return r


class LocalTest(unittest.TestCase):
    def base(self,registros):
        con=duckdb.connect()
        self.addCleanup(con.close)
        con.execute('CREATE TABLE base('+','.join(f'{c} {t}' for c,t in TIPOS.items())+')')
        if registros:
            con.executemany('INSERT INTO base VALUES ('+','.join('?' for c in TIPOS)+')',
                            [[r[c] for c in TIPOS] for r in registros])
        return con

    def test_mapa_completo_27_ufs(self):
        con=self.base([linha(i,x['sigla'],x['codigo']) for i,x in enumerate(UFS)])
        preparar_local(con);a=auditar_local(con)
        self.assertEqual(a['registros_uf_regiao_valida'],27)
        self.assertEqual(dict(con.execute('SELECT local_regiao,count(*) FROM territorio GROUP BY 1').fetchall()),
                         {'Norte':7,'Nordeste':9,'Sudeste':4,'Sul':3,'Centro-Oeste':4})

    def test_nulos_desconhecidos_discordancias_sem_correcao(self):
        con=self.base([linha(1,uf=None),linha(2,uf='ZZ'),linha(3,uf='RJ',codigo='35'),
                       linha(4,uf='SP',CO_MUNICIPIO_PROVA='3304557'),
                       linha(5,uf='sp',NO_MUNICIPIO_PROVA=None),linha(6,CO_MUNICIPIO_PROVA='abc')])
        r,c=calcular_local_prova(con)
        self.assertEqual(c['cobertura']['status_uf'],{'dados_ausentes':1,'desconhecida':2,'discordante':1,'valida':2})
        self.assertEqual(c['cobertura']['achados']['municipio_prefixo_uf_discordante'],1)
        self.assertEqual(c['cobertura']['achados']['municipio_codigo_formato_invalido'],1)
        self.assertEqual(next(x for x in r['participacao'] if x['nivel']=='Região' and x['local']=='Não classificada')['total_base'],4)
        self.assertEqual(con.execute("SELECT SG_UF_PROVA FROM base WHERE NU_SEQUENCIAL='5'").fetchone()[0],'sp')
        self.assertTrue(all(c['reconciliacoes'].values()))

    def test_media_regional_ponderada_e_quantis_diretos_zeros(self):
        con=self.base([linha(1,nota=0),linha(2,nota=100),linha(3,nota=200,NU_NOTA_CH=None),
                       linha(4,uf='MG',codigo='31',nota=1000),linha(5,uf='AC',codigo='12',nota=900,presenca=0)])
        r,c=calcular_local_prova(con)
        sudeste=next(x for x in r['desempenho'] if x['nivel']=='Região' and x['local']=='Sudeste' and x['area']=='CN')
        self.assertEqual((sudeste['elegiveis'],sudeste['media'],sudeste['mediana'],sudeste['q1'],sudeste['q3']),(4,325,150,75,400))
        self.assertEqual(sudeste['zeros_elegiveis'],1)
        ch=next(x for x in r['desempenho'] if x['nivel']=='Região' and x['local']=='Sudeste' and x['area']=='CH')
        self.assertEqual((ch['elegiveis'],ch['presentes_sem_nota']),(3,1))
        norte=next(x for x in r['desempenho'] if x['nivel']=='Região' and x['local']=='Norte' and x['area']=='CN')
        self.assertEqual(norte['elegiveis'],0);self.assertIsNone(norte['mediana'])
        self.assertEqual(norte['notas_fora_presentes'],1)
        self.assertTrue(all(c['reconciliacoes'].values()))

    def test_reutiliza_status_mistos_nulos_invalidos_e_retencao(self):
        con=self.base([linha(1),linha(2,TP_PRESENCA_CN=0,TP_PRESENCA_MT=0),
                       linha(3,TP_PRESENCA_CN=2),linha(4,TP_PRESENCA_CN=None),linha(5,TP_PRESENCA_CN=9)])
        r,c=calcular_local_prova(con)
        n=next(x for x in r['participacao'] if x['nivel']=='Brasil')
        self.assertEqual((n['presentes_dia1'],n['presentes_dia2'],n['retencao_percentual']),(5,1,20))
        self.assertEqual([n[f'{s}_dia2'] for s in ('misto','dados_ausentes','codigo_invalido')],[1,1,1])
        self.assertTrue(all(c['reconciliacoes'].values()))

    def test_empates_taxa_exata_e_denominador_zero(self):
        rows=[dict(nivel='UF',local=uf,presentes_dia2=n,total_base=d,taxa_presenca_dia2=100*n/d if d else None)
              for uf,n,d in [('SP',1,2),('MG',2,4),('RJ',0,0),('AC',3,4),('AM',1,4),('Não classificada',100,100)]]
        top=top3_ufs(rows)
        self.assertEqual([x['uf'] for x in top[:3]],['AC','MG','SP'])
        self.assertEqual([x['uf'] for x in top[3:]],['AM','MG','SP'])
        r,c=calcular_local_prova(self.base([]))
        self.assertIsNone(r['participacao'][0]['taxa_presenca_dia2'])
        self.assertIsNone(r['participacao'][0]['retencao_percentual'])
        self.assertEqual(r['top3_ufs'],[])

    def test_migracao_preserva_dezessete_campos_e_publicacao(self):
        with tempfile.TemporaryDirectory() as temp:
            raiz=Path(temp);(raiz/'src').mkdir();(raiz/'src/trusted_resultados.py').touch();(raiz/'trusted').mkdir()
            p=raiz/'trusted/resultados_2025_base.parquet'
            registro=linha('001',TP_STATUS_REDACAO=1,NU_NOTA_REDACAO=500,
                           **{f'NU_NOTA_COMP{i}':100 for i in range(1,6)})
            with duckdb.connect() as con:
                con.execute('CREATE TABLE t('+','.join(f'{c} {t}' for c,t in TIPOS_V2.items())+')')
                con.executemany('INSERT INTO t VALUES ('+','.join('?' for c in TIPOS_V2)+')',[[registro[c] for c in TIPOS_V2]])
                con.execute('COPY t TO ? (FORMAT PARQUET)',[str(p)])
            anterior=sha256(p)
            raw=raiz/FONTE;raw.parent.mkdir(parents=True)
            def gravar():
                with raw.open('w',encoding='latin-1',newline='') as f:
                    w=csv.DictWriter(f,fieldnames=CAMPOS,delimiter=';');w.writeheader();w.writerow(registro)
            gravar();audit=executar(raiz)
            self.assertEqual(len(audit['regressao_legado']['campos']),17)
            self.assertEqual(sha256(raiz/audit['rollback_parquet']),anterior)
            atual=sha256(p);res,report=executar_local_prova(raiz)
            self.assertEqual(sha256(p),atual)
            self.assertTrue(all(sha256(raiz/'analitica'/n)==h for n,h in report['hashes_csv'].items()))
            registro['NU_NOTA_COMP5']=80;gravar()
            with self.assertRaisesRegex(ErroContrato,'campos legados'):executar(raiz)
            self.assertEqual(sha256(p),atual)
