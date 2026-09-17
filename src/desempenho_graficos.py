"""Apresentação dos quatro agregados: nenhum acesso à base individual."""
from pathlib import Path
import math
import matplotlib.pyplot as plt


def gerar_graficos(resultados, pasta):
    pasta = Path(pasta)
    pasta.mkdir(parents=True, exist_ok=True)
    areas = [r['area'] for r in resultados]
    arquivos = []
    with plt.rc_context({'font.family': 'DejaVu Sans', 'font.size': 11,
                         'axes.spines.top': False, 'axes.spines.right': False}):
        fig, ax = plt.subplots(figsize=(10, 5.8))
        esquerda = [0.] * len(areas)
        for categoria, rotulo, cor in [('presentes','Presente','#197C80'), ('ausentes','Ausente','#BEC9D1'),
                                      ('eliminados','Eliminado','#DC842C'), ('presenca_nula','Não informado','#8063A1')]:
            valores = [r[f'pct_{categoria}_base'] or 0 for r in resultados]
            ax.barh(areas, valores, left=esquerda, color=cor, label=rotulo, height=.55)
            if categoria == 'presentes':
                for i, valor in enumerate(valores):
                    ax.text(valor/2, i, f'{valor:.2f}%'.replace('.',','), ha='center', va='center', color='white', weight='bold')
            esquerda = [a+b for a,b in zip(esquerda,valores)]
        ax.invert_yaxis()
        ax.set(xlim=(0,100), xlabel='Percentual de todos os registros da base (%)',
               title='ENEM 2025 | Situação de participação por área')
        ax.legend(loc='upper center', bbox_to_anchor=(.5,-.15), ncol=4, frameon=False)
        total = f"{resultados[0]['total_base']:,}".replace(',','.')
        eliminados = ' · '.join(f"{r['area']} {r['pct_eliminados_base']:.2f}%".replace('.',',') for r in resultados)
        fig.text(.08,.03,f'Base por área: {total} registros. Eliminados: {eliminados}\nFonte: RESULTADOS 2025, trusted local. Categorias pequenas podem ser pouco visíveis.',fontsize=9)
        fig.subplots_adjust(bottom=.29, top=.88, left=.09, right=.97)
        arquivo=pasta/'participacao_por_area_2025.png'
        fig.savefig(arquivo,dpi=150); plt.close(fig); arquivos.append(arquivo)

        fig, ax = plt.subplots(figsize=(10,5.8))
        for i,r in enumerate(resultados):
            if r['elegiveis']:
                ax.plot([r['q1'],r['q3']],[i,i],color='#197C80',linewidth=10,solid_capstyle='butt')
                ax.scatter(r['mediana'],i,color='#202D3B',s=65,zorder=3)
                ax.annotate(f"{r['q1']:.1f} / {r['mediana']:.1f} / {r['q3']:.1f}".replace('.',','),
                            (r['mediana'],i),xytext=(0,14),textcoords='offset points',ha='center',fontsize=10)
        ax.set_yticks(range(len(areas)), [f"{r['area']}   n={r['elegiveis']:,}".replace(',','.') for r in resultados])
        ax.set_ylim(len(areas)-.4,-.65)
        valores = [r[c] for r in resultados for c in ('q1','q3') if r[c] is not None]
        if valores:
            minimo = math.floor(min(valores)/50)*50
            maximo = math.ceil(max(valores)/50)*50
            marcas = list(range(minimo, maximo+1, 50))
            ax.set_xticks(marcas, [str(v) for v in marcas])
            ax.set_xlim(minimo-15, maximo+15)
        ax.set(xlabel='Nota da área (escala original)',title='ENEM 2025 | Intervalo interquartil e mediana')
        ax.grid(axis='x',alpha=.18)
        fig.text(.08,.045,'Traço: Q1–Q3 (50% centrais). Ponto: mediana. Rótulos: Q1 / mediana / Q3.\nSomente presentes com nota na própria área; zeros incluídos. Não é um boxplot completo.\nPopulações diferem; estas escalas não constituem um ranking de dificuldade entre áreas.',fontsize=9)
        fig.subplots_adjust(bottom=.23,top=.87,left=.24,right=.97)
        arquivo=pasta/'quartis_por_area_2025.png'
        fig.savefig(arquivo,dpi=150); plt.close(fig); arquivos.append(arquivo)
    return arquivos
