"""Agregações de redação: nota registrada, situação e competências sem imputação."""
from src.desempenho import percentual

STATUS = {1: 'Sem problemas', 2: 'Anulada', 3: 'Cópia Texto Motivador',
          4: 'Em Branco', 6: 'Fuga ao tema', 7: 'Não atendimento ao tipo textual',
          8: 'Texto insuficiente', 9: 'Parte desconectada'}
COMPETENCIAS = {f'NU_NOTA_COMP{i}': nome for i, nome in enumerate((
    'Domínio da escrita formal', 'Tema e tipo textual', 'Defesa de um ponto de vista',
    'Mecanismos da argumentação', 'Proposta de intervenção'), 1)}
COMPLETAS = ' AND '.join(f'{c} IS NOT NULL' for c in COMPETENCIAS)
FILTRO_FINAL = 'NU_NOTA_REDACAO IS NOT NULL'
FILTRO_COMP = f'TP_STATUS_REDACAO=1 AND {FILTRO_FINAL} AND {COMPLETAS}'


def registros(con, sql):
    cursor = con.execute(sql)
    return [dict(zip([d[0] for d in cursor.description], row)) for row in cursor.fetchall()]


def estatisticas(con, campo, filtro):
    r = registros(con, f'''SELECT count(*) n, count(*) FILTER(WHERE {campo}=0) zeros,
        avg({campo})::DOUBLE media, min({campo})::DOUBLE minimo_observado,
        max({campo})::DOUBLE maximo_observado,
        quantile_cont({campo}::DOUBLE, [0.25,0.5,0.75]) quantis
        FROM base WHERE {filtro}''')[0]
    q = r.pop('quantis') or [None]*3
    r.update(q1=q[0], mediana=q[1], q3=q[2])
    return r


def calcular_redacao(con):
    total = con.execute('SELECT count(*) FROM base').fetchone()[0]
    invalidos = con.execute('SELECT count(*) FROM base WHERE TP_STATUS_REDACAO NOT IN ('
                           + ','.join(map(str, STATUS)) + ')').fetchone()[0]
    if invalidos:
        raise ValueError('Situação de redação não prevista no dicionário.')
    final = estatisticas(con, 'NU_NOTA_REDACAO', FILTRO_FINAL)
    final.update(total_base=total, sem_nota=total-final['n'], pct_com_nota_base=percentual(final['n'],total))
    status = registros(con, '''SELECT TP_STATUS_REDACAO codigo, count(*) quantidade,
        count(NU_NOTA_REDACAO) com_nota,
        count(*) FILTER(WHERE NU_NOTA_REDACAO IS NULL) sem_nota,
        count(*) FILTER(WHERE NU_NOTA_REDACAO=0) zeros,
        count(*) FILTER(WHERE NU_NOTA_REDACAO>0) positivas
        FROM base GROUP BY 1 ORDER BY 1 NULLS LAST''')
    for r in status:
        r.update(situacao=STATUS.get(r['codigo'], 'Sem status registrado'),
                 percentual_base=percentual(r['quantidade'],total))
    competencias = [dict(campo=c, competencia=nome, **estatisticas(con,c,FILTRO_COMP))
                    for c,nome in COMPETENCIAS.items()]
    soma = '+'.join(COMPETENCIAS)
    controles = registros(con, f'''SELECT
        count(*) FILTER(WHERE TP_STATUS_REDACAO=1) sem_problemas,
        count(*) FILTER(WHERE TP_STATUS_REDACAO=1 AND NOT ({FILTRO_FINAL} AND {COMPLETAS})) incompletas_sem_problemas,
        count(*) FILTER(WHERE {FILTRO_COMP}) recorte_competencias,
        count(*) FILTER(WHERE {FILTRO_FINAL} AND {COMPLETAS}) soma_comparavel,
        count(*) FILTER(WHERE {FILTRO_FINAL} AND {COMPLETAS} AND NU_NOTA_REDACAO<>({soma})) soma_divergente,
        count(*) FILTER(WHERE {FILTRO_COMP} AND NU_NOTA_REDACAO<>({soma})) soma_divergente_recorte,
        count(*) FILTER(WHERE TP_STATUS_REDACAO IS NULL AND {FILTRO_FINAL}) nota_sem_status,
        count(*) FILTER(WHERE TP_STATUS_REDACAO IS NOT NULL AND NU_NOTA_REDACAO IS NULL) status_sem_nota,
        count(*) FILTER(WHERE TP_STATUS_REDACAO<>1 AND NU_NOTA_REDACAO>0) positivas_status_problematico,
        count(*) FILTER(WHERE NU_NOTA_REDACAO<0 OR NU_NOTA_REDACAO>1000) final_fora_escala,
        count(*) FILTER(WHERE {' OR '.join(f'{c}<0 OR {c}>200' for c in COMPETENCIAS)}) competencias_fora_escala
        FROM base''')[0]
    controles['nulos_campos'] = registros(con, 'SELECT ' + ','.join(
        f'count(*) FILTER(WHERE {c} IS NULL) {c}' for c in ['TP_STATUS_REDACAO','NU_NOTA_REDACAO',*COMPETENCIAS])+' FROM base')[0]
    # Cruzamento apenas dentro de RESULTADOS: auditoria de coerência, nunca filtro de presença da redação.
    presencas = registros(con, '''SELECT TP_PRESENCA_LC presenca_lc, TP_PRESENCA_CH presenca_ch,
        count(*) quantidade, count(NU_NOTA_REDACAO) com_nota,
        count(TP_STATUS_REDACAO) com_status FROM base GROUP BY 1,2 ORDER BY 1,2''')
    distribuicao = registros(con, '''SELECT NU_NOTA_REDACAO::DOUBLE nota, count(*) quantidade
        FROM base WHERE NU_NOTA_REDACAO IS NOT NULL GROUP BY 1 ORDER BY 1''')
    reconciliacoes = {
        'status_total': sum(r['quantidade'] for r in status)==total,
        'status_notas': sum(r['com_nota'] for r in status)==final['n'],
        'status_zeros': sum(r['zeros'] for r in status)==final['zeros'],
        'distribuicao_notas': sum(r['quantidade'] for r in distribuicao)==final['n'],
        'distribuicao_zeros': sum(r['quantidade'] for r in distribuicao if r['nota']==0)==final['zeros'],
        'competencias_denominador': all(r['n']==controles['recorte_competencias'] for r in competencias),
        'competencias_exclusoes': controles['recorte_competencias']+controles['incompletas_sem_problemas']==controles['sem_problemas'],
        'presencas_total': sum(r['quantidade'] for r in presencas)==total,
    }
    if not all(reconciliacoes.values()):
        raise ValueError(f'Reconciliação da redação falhou: {reconciliacoes}')
    controles['reconciliacoes'] = reconciliacoes
    return dict(final=[final], status=status, competencias=competencias,
                distribuicao=distribuicao, presencas=presencas), controles
