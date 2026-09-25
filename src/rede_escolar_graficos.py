"""Um gráfico de quartis e medianas, somente a partir de agregados."""
from pathlib import Path
import matplotlib.pyplot as plt
from src.desempenho import AREAS


def gerar_grafico_rede_escolar(resultado, pasta):
    pasta = Path(pasta)
    pasta.mkdir(parents=True, exist_ok=True)
    total = sum(r['registros'] for r in resultado['cobertura'])
    validos = sum(r['registros'] for r in resultado['cobertura'] if r['codigo'] is not None)
    cobertura = f'{100 * validos / total:.2f}%'.replace('.', ',') if total else 'sem base'
    with plt.rc_context({'font.family': 'DejaVu Sans', 'font.size': 11,
                         'axes.spines.top': False, 'axes.spines.right': False}):
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        for ax, area in zip(axes.flat, AREAS):
            linhas = [r for r in resultado['desempenho'] if r['area'] == area]
            for i, r in enumerate(linhas):
                if r['elegiveis']:
                    ax.plot([r['q1'], r['q3']], [i, i], lw=8, color='#197C80', solid_capstyle='butt')
                    ax.scatter(r['mediana'], i, color='#202D3B', s=40, zorder=3)
                    ax.text(r['mediana'], i-.19, f"{r['mediana']:.1f}".replace('.', ','),
                            ha='center', fontsize=10, color='#202D3B')
            ax.set_yticks(range(4), [r['rede'] for r in linhas])
            ax.set(xlim=(250, 850), ylim=(3.6, -.6), xlabel='Nota na área', title=AREAS[area])
            ax.grid(axis='x', alpha=.15)
            ax.set_axisbelow(True)
        fig.text(.055, .965, 'Como as notas variam entre as redes informadas?',
                 fontsize=20, weight='bold', color='#202D3B')
        fig.text(.055, .925, 'Faixa: Q1–Q3 (50% centrais)  •  Ponto: mediana', fontsize=12)
        fig.text(.055, .055, f'Rede disponível em {cobertura} da base. Recorte escolar selecionado; não representa todos os participantes.\n'
                 'Zeros incluídos. A rede municipal tem base menor. Diferenças descritivas, sem interpretação causal ou de qualidade.\n'
                 'Fonte: microdados ENEM 2025 / RESULTADOS. Quartis contínuos (tipo 7); a faixa não mostra mínimos e máximos.',
                 fontsize=10, color='#52616E')
        fig.subplots_adjust(left=.12, right=.97, top=.86, bottom=.16, hspace=.43, wspace=.33)
        caminho = pasta / 'rede_escolar_notas_2025.png'
        fig.savefig(caminho, dpi=150)
        plt.close(fig)
    return caminho
