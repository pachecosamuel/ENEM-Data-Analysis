"""Classificação e agregados de participação; sem arquivos ou apresentação."""
from collections import Counter
from itertools import product
import math

from src.desempenho import percentual

DIAS = {1: ('LC', 'CH'), 2: ('CN', 'MT')}
STATUS = ('presente', 'ausente', 'eliminado', 'misto', 'dados_ausentes', 'codigo_invalido')
ROTULOS = {'presente': 'Presença nas duas áreas', 'ausente': 'Ausência nas duas áreas',
           'eliminado': 'Eliminação nas duas áreas', 'misto': 'Situação mista',
           'dados_ausentes': 'Dados ausentes', 'codigo_invalido': 'Código inválido'}


def classificar_par(primeiro, segundo):
    """Inválido prevalece sobre nulo; os códigos originais ficam no detalhamento."""
    if any(c is not None and c not in (0, 1, 2) for c in (primeiro, segundo)):
        return 'codigo_invalido'
    if primeiro is None or segundo is None:
        return 'dados_ausentes'
    if primeiro == segundo:
        return {0: 'ausente', 1: 'presente', 2: 'eliminado'}[primeiro]
    return 'misto'


def agregar_combinacoes(combinacoes):
    """Recebe apenas grupos (LC,CH,CN,MT,quantidade), nunca milhões de linhas."""
    pares = {dia: Counter({p: 0 for p in product((0, 1, 2), repeat=2)}) for dia in DIAS}
    matriz = Counter({p: 0 for p in product(STATUS, repeat=2)})
    total = 0
    for lc, ch, cn, mt, quantidade in combinacoes:
        total += quantidade
        pares[1][lc, ch] += quantidade
        pares[2][cn, mt] += quantidade
        matriz[classificar_par(lc, ch), classificar_par(cn, mt)] += quantidade
    detalhes, dias, transicoes = [], [], []
    for dia in DIAS:
        contagens = Counter({s: 0 for s in STATUS})
        for (a, b), n in sorted(pares[dia].items(), key=lambda item: tuple((v is not None, v or 0) for v in item[0])):
            status = classificar_par(a, b)
            contagens[status] += n
            detalhes.append({'dia': dia, 'area_a': DIAS[dia][0], 'area_b': DIAS[dia][1],
                             'codigo_a': a, 'codigo_b': b, 'status': status, 'quantidade': n,
                             'percentual_base': percentual(n, total)})
        for s in STATUS:
            dias.append({'dia': dia, 'status': s, 'quantidade': contagens[s],
                         'percentual_base': percentual(contagens[s], total)})
    for a, b in product(STATUS, repeat=2):
        n = matriz[a, b]
        origem = sum(matriz[a, s] for s in STATUS)
        transicoes.append({'dia1': a, 'dia2': b, 'quantidade': n,
                           'percentual_base': percentual(n, total),
                           'denominador_origem': origem, 'percentual_origem': percentual(n, origem)})
    presentes1 = sum(matriz['presente', s] for s in STATUS)
    presentes2 = sum(matriz[s, 'presente'] for s in STATUS)
    ambos = matriz['presente', 'presente']
    primeiro = matriz['presente', 'ausente']
    segundo = matriz['ausente', 'presente']
    ausentes = matriz['ausente', 'ausente']
    resumo = {'total_base': total, 'presentes_dia1': presentes1, 'presentes_dia2': presentes2,
              'presentes_ambos': ambos, 'somente_primeiro_ausente_segundo': primeiro,
              'somente_segundo_ausente_primeiro': segundo, 'ausentes_ambos': ausentes,
              'demais_situacoes': total - ambos - primeiro - segundo - ausentes,
              'retencao_percentual': percentual(ambos, presentes1),
              'retencao_denominador': presentes1,
              'diferenca_liquida_dia2_menos_dia1': presentes2 - presentes1,
              'presente_dia1_sem_presenca_completa_dia2': presentes1 - ambos,
              'presente_dia2_sem_presenca_completa_dia1': presentes2 - ambos}
    for grupo in ('presentes_ambos','somente_primeiro_ausente_segundo','somente_segundo_ausente_primeiro',
                  'ausentes_ambos','demais_situacoes'):
        resumo[f'pct_{grupo}_base'] = percentual(resumo[grupo], total)
    return {'dias': dias, 'pares': detalhes, 'transicoes': transicoes, 'resumo': resumo}


def validar_participacao(resultado):
    dias, pares, matriz, r = (resultado[k] for k in ('dias', 'pares', 'transicoes', 'resumo'))
    total = r['total_base']
    controles = {'matriz_total': sum(x['quantidade'] for x in matriz) == total,
                 'grupos_total': sum(r[k] for k in ('presentes_ambos', 'somente_primeiro_ausente_segundo',
                    'somente_segundo_ausente_primeiro', 'ausentes_ambos', 'demais_situacoes')) == total,
                 'diferenca_liquida': r['diferenca_liquida_dia2_menos_dia1'] ==
                    r['presente_dia2_sem_presenca_completa_dia1'] - r['presente_dia1_sem_presenca_completa_dia2']}
    for dia in DIAS:
        controles[f'total_dia{dia}'] = sum(x['quantidade'] for x in dias if x['dia'] == dia) == total
        controles[f'pares_dia{dia}'] = sum(x['quantidade'] for x in pares if x['dia'] == dia) == total
        for status in STATUS:
            marginal = next(x['quantidade'] for x in dias if x['dia'] == dia and x['status'] == status)
            controles[f'marginal_{dia}_{status}'] = marginal == sum(x['quantidade'] for x in matriz if x[f'dia{dia}'] == status)
        percentuais = [x['percentual_base'] for x in dias if x['dia'] == dia]
        controles[f'percentuais_dia{dia}'] = (all(x is None for x in percentuais) if not total else math.isclose(sum(percentuais), 100))
    controles['retencao'] = r['retencao_percentual'] == percentual(r['presentes_ambos'], r['presentes_dia1'])
    controles['percentuais_intervalo'] = all(x[k] is None or 0 <= x[k] <= 100 for x in [*dias, *pares, *matriz]
        for k in x if k.startswith('percentual_'))
    controles['percentuais_denominador_base'] = all(x['percentual_base'] == percentual(x['quantidade'], total)
        for x in [*dias,*pares,*matriz])
    for status in STATUS:
        linhas = [x for x in matriz if x['dia1'] == status]
        controles[f'percentuais_origem_{status}'] = (all(x['percentual_origem'] is None for x in linhas)
            if not linhas[0]['denominador_origem'] else math.isclose(sum(x['percentual_origem'] for x in linhas), 100))
    if not all(controles.values()):
        raise ValueError(f'Reconciliação de participação falhou: {controles}')
    return controles


def calcular_participacao(conexao):
    grupos = conexao.execute('''SELECT TP_PRESENCA_LC, TP_PRESENCA_CH, TP_PRESENCA_CN,
        TP_PRESENCA_MT, count(*) FROM base GROUP BY ALL ORDER BY 1,2,3,4''').fetchall()
    resultado = agregar_combinacoes(grupos)
    controles = validar_participacao(resultado)
    # Reconta cada par diretamente para conferir a agregação conjunta.
    for dia, (a, b) in DIAS.items():
        direto = dict(((x,y), n) for x,y,n in conexao.execute(
            f'SELECT TP_PRESENCA_{a}, TP_PRESENCA_{b}, count(*) FROM base GROUP BY ALL').fetchall())
        agregado = {(x['codigo_a'], x['codigo_b']): x['quantidade'] for x in resultado['pares'] if x['dia'] == dia and x['quantidade']}
        controles[f'pares_recontados_dia{dia}'] = direto == agregado
    if not all(controles.values()):
        raise ValueError('Contagem independente dos pares diverge.')
    resultado['combinacoes_conjuntas'] = [dict(zip(('LC','CH','CN','MT','quantidade'), linha)) for linha in grupos]
    return resultado, controles
