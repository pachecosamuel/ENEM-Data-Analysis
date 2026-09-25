"""Duas distribuições independentes, somente a partir do CSV agregado."""
from pathlib import Path
import matplotlib.pyplot as plt
from src.participacao_graficos import numero, porcentagem


def gerar_graficos_perfil_economico(linhas, pasta):
    pasta = Path(pasta)
    pasta.mkdir(parents=True, exist_ok=True)
    caminhos = []
    with plt.rc_context({'font.family': 'DejaVu Sans', 'font.size': 11, 'text.parse_math': False,
                         'axes.spines.top': False, 'axes.spines.right': False}):
        familiar = [r for r in linhas if r['pergunta'] == 'Q007']
        ate_3036 = 100 * sum(r['quantidade'] for r in familiar if r['codigo'] in ('A', 'B', 'C', 'D')) / familiar[0]['total_base']
        fig, ax = plt.subplots(figsize=(14, 10))
        for i, r in enumerate(familiar):
            valor = r['percentual_base']
            ax.barh(i, valor, color='#197C80' if r['codigo'] in ('A', 'B', 'C', 'D') else '#A6BBC3', height=.65)
            ax.text(valor+.4, i, porcentagem(valor), va='center', fontsize=10)
        ax.set_yticks(range(len(familiar)), [r['categoria'] for r in familiar])
        ax.invert_yaxis()
        ax.set(xlim=(0, max(r['percentual_base'] for r in familiar)+7),
               xlabel='Percentual de todos os registros de PARTICIPANTES (%)')
        ax.grid(axis='x', alpha=.12)
        ax.set_axisbelow(True)
        fig.text(.04, .95, f'{porcentagem(ate_3036)} dos inscritos declararam renda familiar de até R$ 3.036',
                 fontsize=18, weight='bold', color='#202D3B')
        fig.text(.04, .91, 'Renda mensal familiar declarada (Q007) · Acumulado A–D, incluindo nenhuma renda · Não é renda per capita', fontsize=11)
        fig.text(.04, .045, f"Base: {numero(familiar[0]['total_base'])} registros divulgados · Categorias na ordem do dicionário 2025.\n"
                 'Valores declarados em faixas; não são renda por pessoa. Fonte: ENEM 2025 / PARTICIPANTES.', fontsize=10, color='#52616E')
        fig.subplots_adjust(left=.36, right=.96, top=.86, bottom=.13)
        caminho = pasta / 'perfil_economico_renda_familiar_2025.png'
        fig.savefig(caminho, dpi=150)
        plt.close(fig)
        caminhos.append(caminho)

        propria = [r for r in linhas if r['pergunta'] == 'Q006']
        nao = next(r for r in propria if r['codigo'] == 'A')
        fig, ax = plt.subplots(figsize=(12, 5.5))
        for i, r in enumerate(propria):
            ax.barh(i, r['percentual_base'], color='#197C80' if r['codigo'] == 'A' else '#A6BBC3', height=.48)
            ax.text(r['percentual_base']+1, i,
                    f"{porcentagem(r['percentual_base'])} · {numero(r['quantidade'])}", va='center', fontsize=11)
        ax.set_yticks(range(len(propria)), [r['categoria'] for r in propria])
        ax.invert_yaxis()
        ax.set(xlim=(0, 100), xlabel='Percentual de todos os registros de PARTICIPANTES (%)')
        ax.grid(axis='x', alpha=.12)
        ax.set_axisbelow(True)
        fig.text(.05, .93, f"{porcentagem(nao['percentual_base'])} declararam não possuir renda própria",
                 fontsize=19, weight='bold', color='#202D3B')
        fig.text(.05, .85, '“Você possui renda?” (Q006) — declaração de possuir renda, sem informar seu valor', fontsize=12)
        fig.text(.05, .055, f"Base: {numero(nao['total_base'])} registros divulgados · Fonte: ENEM 2025 / PARTICIPANTES.\n"
                 'Não possuir renda própria não significa que a família não tenha renda, nem identifica situação de emprego.',
                 fontsize=10, color='#52616E')
        fig.subplots_adjust(left=.17, right=.96, top=.76, bottom=.24)
        caminho = pasta / 'perfil_economico_renda_propria_2025.png'
        fig.savefig(caminho, dpi=150)
        plt.close(fig)
        caminhos.append(caminho)
    return caminhos
