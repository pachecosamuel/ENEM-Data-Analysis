"""Categorias de PARTICIPANTES 2025 e agregação do perfil econômico."""
from src.desempenho import percentual

# Dicionário 2025, aba PARTICIPANTES_2025, linhas 184–202.
RENDA_PROPRIA = {'A': 'Não', 'B': 'Sim'}
RENDA_FAMILIAR = dict(zip('ABCDEFGHIJKLMNOPQ', [
    'Nenhuma renda', 'Até R$ 1.518,00',
    'De R$ 1.518,01 até R$ 2.277,00', 'De R$ 2.277,01 até R$ 3.036,00',
    'De R$ 3.036,01 até R$ 3.795,00', 'De R$ 3.795,01 até R$ 4.554,00',
    'De R$ 4.554,01 até R$ 6.072,00', 'De R$ 6.072,01 até R$ 7.590,00',
    'De R$ 7.590,01 até R$ 9.108,00', 'De R$ 9.108,01 até R$ 10.626,00',
    'De R$ 10.626,01 até R$ 12.144,00', 'De R$ 12.144,01 até R$ 13.662,00',
    'De R$ 13.662,01 até R$ 15.180,00', 'De R$ 15.180,01 até R$ 18.216,00',
    'De R$ 18.216,01 até R$ 22.770,00', 'De R$ 22.770,01 até R$ 30.360,00',
    'Acima de R$ 30.360,00']))
CATEGORIAS = {'Q006': RENDA_PROPRIA, 'Q007': RENDA_FAMILIAR}


def calcular_perfil_economico(con):
    """A view participantes contém Q006/Q007; somente contagens saem do SQL."""
    total = con.execute('SELECT count(*) FROM participantes').fetchone()[0]
    linhas = []
    for pergunta, categorias in CATEGORIAS.items():
        contagens = dict(con.execute(f'SELECT {pergunta}, count(*) FROM participantes GROUP BY 1').fetchall())
        invalidos = {k: v for k, v in contagens.items() if k is not None and k not in categorias}
        if invalidos:
            raise ValueError(f'Categorias inesperadas em {pergunta}: {invalidos}')
        ausentes = contagens.get(None, 0)
        validas = total - ausentes
        for codigo, categoria in [*categorias.items(), ('', 'Sem resposta')]:
            n = contagens.get(codigo or None, 0)
            linhas.append(dict(pergunta=pergunta, codigo=codigo, categoria=categoria,
                               quantidade=n, total_base=total, respostas_validas=validas,
                               sem_resposta=ausentes, percentual_base=percentual(n, total),
                               percentual_respostas=percentual(n, validas) if codigo else None))
    return linhas
