"""Apresentação dos quatro agregados: nenhum acesso à base individual."""
from pathlib import Path
import math
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from src.desempenho import AREAS


def gerar_graficos(resultados, pasta):
    pasta = Path(pasta)
    pasta.mkdir(parents=True, exist_ok=True)
    areas = [AREAS[r['area']] for r in resultados]
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
        ax.set(xlim=(0,100), xlabel='Registros da base (%)',
               title='Quem participou de cada área?')
        ax.legend(loc='upper center', bbox_to_anchor=(.5,-.15), ncol=4, frameon=False)
        total = f"{resultados[0]['total_base']:,}".replace(',','.')
        eliminados = ' · '.join(f"{r['area']} {r['pct_eliminados_base']:.2f}%".replace('.',',') for r in resultados)
        fig.text(.08,.03,f'Base por área: {total} registros. Eliminados: {eliminados}\nFonte: RESULTADOS 2025, trusted local. Categorias pequenas podem ser pouco visíveis.',fontsize=9)
        fig.subplots_adjust(bottom=.29, top=.88, left=.26, right=.97)
        arquivo=pasta/'participacao_por_area_2025.png'
        fig.savefig(arquivo,dpi=150); plt.close(fig); arquivos.append(arquivo)

        fig, ax = plt.subplots(figsize=(11,6))
        for i,r in enumerate(resultados):
            if not r['elegiveis']:
                continue
            minimo, maximo = r['minimo_observado'], r['maximo_observado']
            ax.plot([minimo,maximo],[i,i],color='#A5B2BD',linewidth=2,zorder=1)
            ax.scatter([minimo,maximo],[i,i],marker='|',color='#71818E',s=80,zorder=2)
            ax.plot([r['q1'],r['q3']],[i,i],color='#197C80',linewidth=11,solid_capstyle='butt',zorder=3)
            ax.scatter(r['mediana'],i,color='#202D3B',s=55,zorder=4)
            ax.annotate(f"{r['mediana']:.1f}".replace('.',','), (r['mediana'],i),
                        xytext=(0,14),textcoords='offset points',ha='center',fontsize=11,weight='bold')
            for valor in (minimo,maximo):
                ax.annotate(f'{valor:.1f}'.replace('.',','),(valor,i),xytext=(0,-19),
                            textcoords='offset points',ha='center',fontsize=9,color='#52616E')
        ax.set_yticks(range(len(areas)), areas)
        ax.set_ylim(len(areas)-.4,-.7)
        valores=[r[c] for r in resultados for c in ('minimo_observado','maximo_observado') if r[c] is not None]
        if valores:
            baixo,alto=min(valores),max(valores)
            margem=max((alto-baixo)*.045,1)
            ax.set_xlim(baixo-margem,alto+margem)
            passo=max(100,math.ceil((alto-baixo)/600)*100)
            marcas=list(range(math.ceil(baixo/passo)*passo,math.floor(alto/passo)*passo+1,passo))
            ax.set_xticks(marcas,[str(v) for v in marcas])
        ax.set(xlabel='Nota',title='Onde se concentram as notas?')
        ax.grid(axis='x',alpha=.12)
        legenda=[Line2D([0],[0],color='#A5B2BD',lw=2,label='Mínimo–máximo observado'),
                 Line2D([0],[0],color='#197C80',lw=8,label='50% centrais'),
                 Line2D([0],[0],color='#202D3B',marker='o',linestyle='',label='Mediana')]
        ax.legend(handles=legenda,loc='upper center',bbox_to_anchor=(.5,-.17),ncol=3,frameon=False,fontsize=10)
        fig.text(.06,.035,'ENEM 2025 · Presentes com nota em cada área, incluindo zero.\nExtremos desta base; não são limites teóricos da TRI. Áreas não formam um ranking de dificuldade.',fontsize=9,color='#52616E')
        fig.subplots_adjust(bottom=.29,top=.88,left=.26,right=.97)
        arquivo=pasta/'quartis_por_area_2025.png'
        fig.savefig(arquivo,dpi=150); plt.close(fig); arquivos.append(arquivo)
    return arquivos
