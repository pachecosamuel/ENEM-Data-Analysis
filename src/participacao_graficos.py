"""Gráficos de contagens agregadas; nenhuma leitura de registros individuais."""
from pathlib import Path
import matplotlib.pyplot as plt
from matplotlib.path import Path as Caminho
from matplotlib.patches import PathPatch, Rectangle
from src.participacao import STATUS

NOMES = {'presente':'Presença completa', 'ausente':'Ausência completa', 'eliminado':'Eliminação completa',
         'misto':'Situação mista', 'dados_ausentes':'Dados ausentes', 'codigo_invalido':'Código inválido'}


def numero(valor):
    return f'{valor:,}'.replace(',','.')


def porcentagem(valor):
    if valor is None:
        return 'não se aplica'
    if valor == 0:
        return '0%'
    if 0 < valor < .01:
        return '<0,01%'
    return f'{valor:.2f}%'.replace('.',',')


def gerar_graficos_participacao(resultado, pasta):
    """Apresenta agregados existentes; não modifica percentuais ou arquivos de negócio."""
    pasta = Path(pasta)
    pasta.mkdir(parents=True, exist_ok=True)
    dias, transicoes, resumo = (resultado[k] for k in ('dias', 'transicoes', 'resumo'))
    estados = [s for s in STATUS if any(x['status'] == s and x['quantidade'] for x in dias)]
    arquivos = []
    with plt.rc_context({'font.family': 'DejaVu Sans', 'font.size': 11,
                         'axes.spines.top': False, 'axes.spines.right': False}):
        fig, ax = plt.subplots(figsize=(12, 4.8))
        presencas = [next(x for x in dias if x['dia'] == d and x['status'] == 'presente') for d in (1, 2)]
        valores = [x['percentual_base'] or 0 for x in presencas]
        ax.barh([0, 1], valores, color='#466674', height=.45)
        for i, x in enumerate(presencas):
            ax.text(2, i, f"{numero(x['quantidade'])}  |  {porcentagem(x['percentual_base'])}",
                    color='white', va='center', fontsize=13, weight='bold')
        ax.set_yticks([0, 1], ['1º dia · LC + CH', '2º dia · CN + MT'])
        ax.set_xlim(0, 100)
        ax.invert_yaxis()
        ax.set_xlabel('Presenças completas (% da base total)')
        fig.suptitle('O 2º dia teve 197.219 presenças completas a menos que o 1º.', fontsize=15, y=.95)
        fig.text(.06, .04, f"Base: {numero(resumo['total_base'])} registros divulgados de RESULTADOS 2025.\nPresença completa = presença nas duas áreas do dia. Percentuais arredondados.", fontsize=10)
        fig.subplots_adjust(left=.19, right=.96, top=.82, bottom=.24)
        destino = pasta/'participacao_por_dia_2025.png'
        fig.savefig(destino, dpi=150)
        plt.close(fig)
        arquivos.append(destino)

        fig, ax = plt.subplots(figsize=(12, 7.5))
        total = resumo['total_base']
        if total <= 0:
            raise ValueError('O fluxo exige pelo menos um registro.')
        lookup = {(x['dia1'], x['dia2']): x['quantidade'] for x in transicoes}
        marginais = [{s: sum(lookup[s, t] for t in estados) for s in estados},
                     {s: sum(lookup[t, s] for t in estados) for s in estados}]
        # Uma única escala para todas as faixas, sem largura mínima para residuais.
        escala, intervalo = .78 / total, .055
        inicios = []
        for contagens in marginais:
            posicao, lado = .06, {}
            for status in estados:
                lado[status] = posicao
                posicao += contagens[status] * escala + intervalo
            inicios.append(lado)
        offsets = [dict(x) for x in inicios]
        faixas = []
        for origem in estados:
            for destino_status in estados:
                n = lookup[origem, destino_status]
                y0, y1 = offsets[0][origem], offsets[1][destino_status]
                altura = n * escala
                offsets[0][origem] += altura
                offsets[1][destino_status] += altura
                if not n:
                    continue
                destaque = origem == 'presente' and destino_status == 'ausente'
                vertices = [(.24,y0),(.43,y0),(.57,y1),(.76,y1),
                            (.76,y1+altura),(.57,y1+altura),(.43,y0+altura),(.24,y0+altura),(.24,y0)]
                comandos = [Caminho.MOVETO, Caminho.CURVE4, Caminho.CURVE4, Caminho.CURVE4,
                            Caminho.LINETO, Caminho.CURVE4, Caminho.CURVE4, Caminho.CURVE4,Caminho.CLOSEPOLY]
                faixas.append((destaque, vertices, comandos, n, (y0+y1+altura)/2, origem, destino_status))
        for destaque, vertices, comandos, n, meio, origem, destino_status in sorted(faixas, key=lambda x:x[0]):
            ax.add_patch(PathPatch(Caminho(vertices, comandos), facecolor='#D57832' if destaque else '#C6CED3',
                                   edgecolor='none', alpha=1 if destaque else .65))
            if destaque:
                ax.text(.5, meio, numero(n), ha='center', va='center', color='#24180F', fontsize=11, weight='bold')
            elif origem == destino_status == 'presente':
                ax.text(.5, meio, numero(n), ha='center', va='center', color='#34454E', fontsize=13)
        for lado, x in enumerate((.225, .76)):
            for status in estados:
                y = inicios[lado][status]
                altura = marginais[lado][status] * escala
                ax.add_patch(Rectangle((x, y), .015, altura, facecolor='#687C87', edgecolor='none'))
                ax.text(.205 if lado == 0 else .795, y+altura/2,
                        f"{NOMES[status].replace(' ', chr(10), 1)}\n{numero(marginais[lado][status])}",
                        ha='right' if lado == 0 else 'left', va='center', fontsize=10, color='#34454E')
        ax.text(.23, .015, '1º dia', ha='center', weight='bold', fontsize=12)
        ax.text(.77, .015, '2º dia', ha='center', weight='bold', fontsize=12)
        ax.set_xlim(0, 1)
        ax.set_ylim(1.02, 0)
        ax.axis('off')
        fig.suptitle('211.292 passaram de presença completa para ausência completa', fontsize=15, y=.96)
        fig.text(.06,.05,'Laranja: presença → ausência. Demais fluxos em cinza; larguras proporcionais às contagens.\nFluxos residuais podem ser quase invisíveis: a matriz de apoio traz todos os valores, sem arredondar contagens.',fontsize=10)
        fig.subplots_adjust(left=.03,right=.97,top=.89,bottom=.15)
        destino = pasta/'transicoes_entre_dias_2025.png'
        fig.savefig(destino,dpi=150)
        plt.close(fig)
        arquivos.append(destino)
    return arquivos
