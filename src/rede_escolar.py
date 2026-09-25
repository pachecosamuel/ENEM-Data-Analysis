"""Cobertura escolar e desempenho; a conexão fornece a view base."""
from src.desempenho import calcular_desempenho, percentual

REDES = {1: 'Federal', 2: 'Estadual', 3: 'Municipal', 4: 'Privada'}
CAMPO = 'TP_DEPENDENCIA_ADM_ESC'


def calcular_rede_escolar(con):
    contagens = dict(con.execute(f'SELECT {CAMPO}, count(*) FROM base GROUP BY 1').fetchall())
    invalidos = {k: v for k, v in contagens.items() if k is not None and k not in REDES}
    if invalidos:
        raise ValueError(f'Códigos de rede inválidos: {invalidos}')
    total = sum(contagens.values())
    validos = sum(contagens.get(k, 0) for k in REDES)
    cobertura = [dict(codigo=k, rede=nome, registros=contagens.get(k, 0),
                      pct_base=percentual(contagens.get(k, 0), total))
                 for k, nome in [*REDES.items(), (None, 'Sem informação')]]
    # Reusa o cálculo nacional sobre cada recorte, sem média de médias.
    desempenho, controles = [], []
    try:
        for codigo, nome in REDES.items():
            con.execute(f'CREATE OR REPLACE TEMP VIEW recorte_rede AS SELECT * FROM base WHERE {CAMPO}={codigo}')
            linhas, checks = calcular_desempenho(con, tabela='recorte_rede')
            desempenho.extend(dict(codigo=codigo, rede=nome, **r) for r in linhas)
            controles.extend(dict(codigo=codigo, **r) for r in checks)
    finally:
        con.execute('DROP VIEW IF EXISTS recorte_rede')
    return {'cobertura': cobertura, 'desempenho': desempenho}, {
        'total_base': total, 'rede_valida': validos, 'rede_nula': contagens.get(None, 0),
        'rede_invalida': 0, 'pct_rede_valida': percentual(validos, total),
        'reconciliacao_total': validos + contagens.get(None, 0) == total,
        'por_area_rede': controles}
