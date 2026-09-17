"""Definições, cálculo SQL e reconciliação do desempenho por área (sem arquivos/gráficos)."""
import math

AREAS = {'CN': 'Ciências da Natureza', 'CH': 'Ciências Humanas',
         'LC': 'Linguagens e Códigos', 'MT': 'Matemática'}
FILTRO = 'TP_PRESENCA_{area} = 1 AND NU_NOTA_{area} IS NOT NULL'
METODO_QUANTIL = 'quantile_cont sobre DOUBLE; tipo 7, h=(n-1)*p e interpolação linear'


def percentual(numerador, denominador):
    return 100 * numerador / denominador if denominador else None


def calcular_area(conexao, area):
    """A conexão fornece a view base; somente uma linha agregada sai do DuckDB."""
    if area not in AREAS:
        raise ValueError('Área desconhecida.')
    presenca, nota = f'TP_PRESENCA_{area}', f'NU_NOTA_{area}'
    elegivel = FILTRO.format(area=area)
    sql = f'''SELECT count(*) total_base,
        count(*) FILTER (WHERE {presenca}=1) presentes,
        count(*) FILTER (WHERE {presenca}=0) ausentes,
        count(*) FILTER (WHERE {presenca}=2) eliminados,
        count(*) FILTER (WHERE {presenca} IS NULL) presenca_nula,
        count(*) FILTER (WHERE {presenca} NOT IN (0,1,2)) presenca_invalida,
        count({nota}) notas_disponiveis,
        count(*) FILTER (WHERE {nota} IS NULL) notas_nulas,
        count(*) FILTER (WHERE {presenca}=1 AND {nota} IS NULL) presentes_sem_nota,
        count(*) FILTER (WHERE {presenca} IS DISTINCT FROM 1 AND {nota} IS NOT NULL) notas_fora_presentes,
        count(*) FILTER (WHERE {elegivel}) elegiveis,
        count(*) FILTER (WHERE {elegivel} AND {nota}=0) zeros_elegiveis,
        avg(CAST({nota} AS DOUBLE)) FILTER (WHERE {elegivel}) media,
        quantile_cont(CAST({nota} AS DOUBLE), [0.25,0.5,0.75]) FILTER (WHERE {elegivel}) quantis
        FROM base'''
    cursor = conexao.execute(sql)
    resultado = dict(zip([d[0] for d in cursor.description], cursor.fetchone()))
    quantis = resultado.pop('quantis') or [None, None, None]
    resultado.update(area=area, nome_area=AREAS[area], q1=quantis[0], mediana=quantis[1], q3=quantis[2])
    for categoria in ('presentes', 'ausentes', 'eliminados', 'presenca_nula', 'presenca_invalida', 'elegiveis'):
        resultado[f'pct_{categoria}_base'] = percentual(resultado[categoria], resultado['total_base'])
    resultado['pct_completude_base'] = percentual(resultado['notas_disponiveis'], resultado['total_base'])
    resultado['pct_completude_presentes'] = percentual(resultado['elegiveis'], resultado['presentes'])
    return resultado


def validar_indicadores(conexao, resultados):
    """Confere identidades e reconta elegíveis em consulta separada por área."""
    if [r['area'] for r in resultados] != list(AREAS):
        raise ValueError('Esperadas exatamente CN, CH, LC e MT.')
    controles = []
    for r in resultados:
        if r['presenca_invalida']:
            raise ValueError(f"Categoria de presença inválida em {r['area']}.")
        soma = sum(r[c] for c in ('presentes', 'ausentes', 'eliminados', 'presenca_nula', 'presenca_invalida'))
        contagem = conexao.execute('SELECT count(*) FROM base WHERE ' + FILTRO.format(area=r['area'])).fetchone()[0]
        verificacoes = {
            'categorias_total': soma == r['total_base'],
            'notas_total': r['notas_disponiveis'] + r['notas_nulas'] == r['total_base'],
            'presentes_completude': r['elegiveis'] + r['presentes_sem_nota'] == r['presentes'],
            'notas_reconciliadas': r['elegiveis'] + r['notas_fora_presentes'] == r['notas_disponiveis'],
            'elegiveis_recontados': contagem == r['elegiveis'],
            'zeros_preservados': 0 <= r['zeros_elegiveis'] <= r['elegiveis'],
        }
        medidas = [r[c] for c in ('media', 'q1', 'mediana', 'q3')]
        verificacoes['medidas_validas'] = (all(x is None for x in medidas) if not r['elegiveis'] else
            all(x is not None and math.isfinite(x) for x in medidas) and r['q1'] <= r['mediana'] <= r['q3'])
        if not all(verificacoes.values()):
            raise ValueError(f"Reconciliação falhou em {r['area']}: {verificacoes}")
        controles.append({'area': r['area'], 'elegiveis_recontados': contagem, 'verificacoes': verificacoes})
    if len({r['total_base'] for r in resultados}) != 1:
        raise ValueError('As áreas devem partir da mesma base, antes dos filtros.')
    return controles


def calcular_desempenho(conexao):
    resultados = [calcular_area(conexao, area) for area in AREAS]
    return resultados, validar_indicadores(conexao, resultados)
