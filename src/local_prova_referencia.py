"""Referência IBGE congelada e cobertura territorial, sem corrigir a fonte."""
import json
from pathlib import Path

ARQUIVO_REFERENCIA = Path(__file__).resolve().parents[1]/'docs/uf_regiao_ibge.json'
REFERENCIA = json.loads(ARQUIVO_REFERENCIA.read_text(encoding='utf-8'))
UFS = REFERENCIA['ufs']
REGIOES = ('Norte', 'Nordeste', 'Sudeste', 'Sul', 'Centro-Oeste')
SEM_LOCAL = 'Não classificada'
CAMPOS_LOCAL = ('CO_MUNICIPIO_PROVA', 'NO_MUNICIPIO_PROVA', 'CO_UF_PROVA', 'SG_UF_PROVA')


def preparar_local(con, origem='base'):
    if origem not in ('base','padronizados','releitura'):
        raise ValueError('Origem territorial não reconhecida.')
    if (len(UFS)!=27 or len({x['codigo'] for x in UFS})!=27 or
        len({x['sigla'] for x in UFS})!=27 or {x['regiao'] for x in UFS}!=set(REGIOES)):
        raise ValueError('Referência IBGE incompleta ou duplicada.')
    con.execute('CREATE OR REPLACE TEMP TABLE mapa_uf(codigo VARCHAR, sigla VARCHAR, nome VARCHAR, regiao VARCHAR)')
    con.executemany('INSERT INTO mapa_uf VALUES (?,?,?,?)',
                    [(x['codigo'],x['sigla'],x['nome'],x['regiao']) for x in UFS])
    con.execute(f'''CREATE OR REPLACE TEMP VIEW territorio AS
        SELECT b.*,
          CASE WHEN b.CO_UF_PROVA IS NULL OR b.SG_UF_PROVA IS NULL THEN 'dados_ausentes'
               WHEN c.codigo IS NULL OR s.sigla IS NULL THEN 'desconhecida'
               WHEN c.sigla<>b.SG_UF_PROVA THEN 'discordante' ELSE 'valida' END status_uf,
          CASE WHEN c.sigla=b.SG_UF_PROVA THEN c.sigla ELSE 'Não classificada' END local_uf,
          CASE WHEN c.sigla=b.SG_UF_PROVA THEN c.regiao ELSE 'Não classificada' END local_regiao
        FROM {origem} b LEFT JOIN mapa_uf c ON b.CO_UF_PROVA=c.codigo
        LEFT JOIN mapa_uf s ON b.SG_UF_PROVA=s.sigla''')


def auditar_local(con):
    total = con.execute('SELECT count(*) FROM territorio').fetchone()[0]
    status = dict(con.execute('SELECT status_uf,count(*) FROM territorio GROUP BY 1 ORDER BY 1').fetchall())
    condicoes = {
        'municipio_codigo_nulo':'CO_MUNICIPIO_PROVA IS NULL',
        'municipio_nome_nulo':'NO_MUNICIPIO_PROVA IS NULL',
        'municipio_codigo_formato_invalido': "CO_MUNICIPIO_PROVA IS NOT NULL AND NOT regexp_full_match(CO_MUNICIPIO_PROVA,'[0-9]{7}')",
        'municipio_prefixo_uf_discordante': "regexp_full_match(CO_MUNICIPIO_PROVA,'[0-9]{7}') AND CO_UF_PROVA IS NOT NULL AND left(CO_MUNICIPIO_PROVA,2)<>CO_UF_PROVA",
        'uf_codigo_nulo':'CO_UF_PROVA IS NULL',
        'uf_sigla_nula':'SG_UF_PROVA IS NULL',
        'uf_codigo_desconhecido':'CO_UF_PROVA IS NOT NULL AND CO_UF_PROVA NOT IN (SELECT codigo FROM mapa_uf)',
        'uf_sigla_desconhecida':'SG_UF_PROVA IS NOT NULL AND SG_UF_PROVA NOT IN (SELECT sigla FROM mapa_uf)',
    }
    contagens = dict(zip(condicoes,con.execute('SELECT '+','.join(
        f'count(*) FILTER(WHERE {c})' for c in condicoes.values())+' FROM territorio').fetchone()))
    contagens['codigos_municipio_com_nomes_divergentes'] = con.execute('''SELECT count(*) FROM
        (SELECT CO_MUNICIPIO_PROVA FROM territorio WHERE CO_MUNICIPIO_PROVA IS NOT NULL
         GROUP BY 1 HAVING count(DISTINCT NO_MUNICIPIO_PROVA)>1)''').fetchone()[0]
    pares_uf=[dict(zip(('codigo','sigla','status','quantidade'),r)) for r in con.execute(
        'SELECT CO_UF_PROVA,SG_UF_PROVA,status_uf,count(*) FROM territorio GROUP BY ALL ORDER BY 1,2,3').fetchall()]
    return dict(total=total, status_uf=status, pares_uf_observados=pares_uf, achados=contagens,
                municipios_distintos=con.execute('SELECT count(DISTINCT CO_MUNICIPIO_PROVA) FROM territorio').fetchone()[0],
                registros_uf_regiao_valida=status.get('valida',0),
                registros_nao_classificados=total-status.get('valida',0))
