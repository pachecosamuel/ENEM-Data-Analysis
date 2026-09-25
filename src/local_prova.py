"""Indicadores por local de aplicação; regras nacionais reutilizadas, sem arquivos."""
from collections import defaultdict
from fractions import Fraction
import math

from src.participacao import agregar_combinacoes, validar_participacao, STATUS
from src.desempenho import AREAS, FILTRO, percentual
from src.local_prova_referencia import preparar_local, auditar_local, SEM_LOCAL, UFS


def linhas(con, sql):
    c=con.execute(sql)
    return [dict(zip([d[0] for d in c.description],row)) for row in c.fetchall()]


def participacao_local(con):
    grupos=defaultdict(list)
    for uf,regiao,lc,ch,cn,mt,n in con.execute('''SELECT local_uf,local_regiao,
        TP_PRESENCA_LC,TP_PRESENCA_CH,TP_PRESENCA_CN,TP_PRESENCA_MT,count(*)
        FROM territorio GROUP BY ALL ORDER BY 1,2,3,4,5,6''').fetchall():
        for chave in [('Brasil','Brasil'),('Região',regiao),('UF',uf)]:
            grupos[chave].append((lc,ch,cn,mt,n))
    # A base vazia ainda tem um total nacional e taxas indisponíveis.
    grupos.setdefault(('Brasil','Brasil'),[])
    resumo,transicoes=[],[]
    for (nivel,local),combinacoes in sorted(grupos.items()):
        r=agregar_combinacoes(combinacoes)
        validar_participacao(r)
        registro=dict(nivel=nivel,local=local,**r['resumo'])
        for dia in (1,2):
            registro[f'taxa_presenca_dia{dia}']=percentual(registro[f'presentes_dia{dia}'],registro['total_base'])
            for status in STATUS:
                registro[f'{status}_dia{dia}']=next(x['quantidade'] for x in r['dias'] if x['dia']==dia and x['status']==status)
        resumo.append(registro)
        transicoes.extend(dict(nivel=nivel,local=local,**x) for x in r['transicoes'])
    return resumo,transicoes


def desempenho_local(con):
    saida=[]
    for nivel,expressao in [('Brasil',"'Brasil'"),('Região','local_regiao'),('UF','local_uf')]:
        for area in AREAS:
            nota=f'NU_NOTA_{area}'
            filtro=FILTRO.format(area=area)
            sql=f'''SELECT {expressao} AS "local", count(*) total_base,
                count(*) FILTER(WHERE {filtro}) elegiveis,
                count(*) FILTER(WHERE {filtro} AND {nota}=0) zeros_elegiveis,
                count(*) FILTER(WHERE TP_PRESENCA_{area}=1 AND {nota} IS NULL) presentes_sem_nota,
                count(*) FILTER(WHERE TP_PRESENCA_{area} IS DISTINCT FROM 1 AND {nota} IS NOT NULL) notas_fora_presentes,
                coalesce(sum({nota}) FILTER(WHERE {filtro}),0)::DOUBLE soma_notas,
                avg({nota}::DOUBLE) FILTER(WHERE {filtro}) media,
                (min({nota}) FILTER(WHERE {filtro}))::DOUBLE minimo_observado,
                (max({nota}) FILTER(WHERE {filtro}))::DOUBLE maximo_observado,
                quantile_cont({nota}::DOUBLE,[0.25,0.5,0.75]) FILTER(WHERE {filtro}) quantis
                FROM territorio {'GROUP BY 1' if nivel!='Brasil' else ''} ORDER BY 1'''
            for r in linhas(con,sql):
                q=r.pop('quantis') or [None]*3
                r.update(nivel=nivel,area=area,q1=q[0],mediana=q[1],q3=q[2],
                         pct_elegiveis_base=percentual(r['elegiveis'],r['total_base']))
                saida.append(r)
    return saida


def top3_ufs(participacao):
    """Taxa exata; empate por sigla crescente, sem arredondar antes de ordenar."""
    validas={x['sigla'] for x in UFS}
    candidatas=[r for r in participacao if r['nivel']=='UF' and r['local'] in validas and r['total_base']>0]
    resultado=[]
    for grupo,sinal in [('Maiores taxas',-1),('Menores taxas',1)]:
        ordenadas=sorted(candidatas,key=lambda r:(sinal*Fraction(r['presentes_dia2'],r['total_base']),r['local']))
        for pos,r in enumerate(ordenadas[:3],1):
            resultado.append(dict(grupo=grupo,posicao=pos,uf=r['local'],presentes_dia2=r['presentes_dia2'],
                total_base=r['total_base'],taxa_presenca_dia2=r['taxa_presenca_dia2']))
    return resultado


def validar_local(con, participacao, desempenho, transicoes):
    nacional=next(r for r in participacao if r['nivel']=='Brasil')
    controles={}
    contagens=['total_base','presentes_dia1','presentes_dia2','presentes_ambos','ausentes_ambos',
        'somente_primeiro_ausente_segundo','somente_segundo_ausente_primeiro','demais_situacoes',
        *[f'{s}_dia{d}' for d in (1,2) for s in STATUS]]
    mapa={x['sigla']:x['regiao'] for x in UFS}
    for nivel in ('Região','UF'):
        grupos=[r for r in participacao if r['nivel']==nivel]
        controles[f'{nivel}_participacao_nacional']=all(sum(r[c] for r in grupos)==nacional[c] for c in contagens)
        controles[f'{nivel}_transicoes_nacional']=all(sum(r['quantidade'] for r in transicoes if r['nivel']==nivel and r['dia1']==n['dia1'] and r['dia2']==n['dia2'])==n['quantidade'] for n in transicoes if n['nivel']=='Brasil')
    for reg in (r for r in participacao if r['nivel']=='Região'):
        ufs=[r for r in participacao if r['nivel']=='UF' and mapa.get(r['local'],SEM_LOCAL)==reg['local']]
        controles[f"{reg['local']}_ufs_participacao"]=all(sum(r[c] for r in ufs)==reg[c] for c in contagens)
    for area in AREAS:
        rows=[r for r in desempenho if r['area']==area]
        n=next(r for r in rows if r['nivel']=='Brasil')
        for nivel in ('Região','UF'):
            sub=[r for r in rows if r['nivel']==nivel]
            controles[f'{nivel}_{area}_nacional']=all(sum(r[c] for r in sub)==n[c] for c in
                ('total_base','elegiveis','zeros_elegiveis','presentes_sem_nota','notas_fora_presentes')) and math.isclose(sum(r['soma_notas'] for r in sub),n['soma_notas'],abs_tol=1e-6,rel_tol=1e-12)
        for reg in (r for r in rows if r['nivel']=='Região'):
            sub=[r for r in rows if r['nivel']=='UF' and mapa.get(r['local'],SEM_LOCAL)==reg['local']]
            controles[f"{reg['local']}_{area}_ufs"]=sum(r['elegiveis'] for r in sub)==reg['elegiveis'] and math.isclose(sum(r['soma_notas'] for r in sub),reg['soma_notas'],abs_tol=1e-6,rel_tol=1e-12)
        for r in rows:
            medidas=[r[k] for k in ('media','q1','mediana','q3','minimo_observado','maximo_observado')]
            ok=(all(x is None for x in medidas) if not r['elegiveis'] else
                all(x is not None and math.isfinite(x) for x in medidas) and
                r['minimo_observado']<=r['q1']<=r['mediana']<=r['q3']<=r['maximo_observado'] and
                math.isclose(r['media'],r['soma_notas']/r['elegiveis'],abs_tol=1e-8))
            controles[f"{r['nivel']}_{r['local']}_{area}_medidas"]=ok
    controles['contagem_independente']=nacional['total_base']==con.execute('SELECT count(*) FROM base').fetchone()[0]
    if not all(controles.values()):
        raise ValueError(f'Reconciliação territorial falhou: {[k for k,v in controles.items() if not v]}')
    return controles


def calcular_local_prova(con):
    preparar_local(con)
    cobertura=auditar_local(con)
    participacao,transicoes=participacao_local(con)
    desempenho=desempenho_local(con)
    controles=validar_local(con,participacao,desempenho,transicoes)
    return dict(participacao=participacao,desempenho=desempenho,transicoes=transicoes,
                top3_ufs=top3_ufs(participacao)),dict(cobertura=cobertura,reconciliacoes=controles)
