"""Distribuição regional de notas; lê somente agregados já calculados."""
from pathlib import Path
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from src.local_prova_referencia import REGIOES
from src.desempenho import AREAS


def gerar_grafico_local_prova(resultado,pasta):
    pasta=Path(pasta);pasta.mkdir(parents=True,exist_ok=True)
    dados=resultado['desempenho']
    regioes=[reg for reg in REGIOES if any(r['nivel']=='Região' and r['local']==reg for r in dados)]
    with plt.rc_context({'font.family':'DejaVu Sans','font.size':11,
                         'axes.spines.top':False,'axes.spines.right':False}):
        fig,axes=plt.subplots(2,2,figsize=(14,10))
        for ax,area in zip(axes.flat,AREAS):
            rows={r['local']:r for r in dados if r['nivel']=='Região' and r['area']==area}
            nacional=next(r for r in dados if r['nivel']=='Brasil' and r['area']==area)
            for i,reg in enumerate(regioes):
                r=rows[reg]
                if r['elegiveis']:
                    ax.plot([r['q1'],r['q3']],[i,i],color='#197C80',lw=8,solid_capstyle='butt',zorder=2)
                    ax.scatter(r['mediana'],i,color='#202D3B',s=38,zorder=3)
                    ax.annotate(f"{r['mediana']:.1f}".replace('.',','),(r['mediana'],i),
                                xytext=(0,10),textcoords='offset points',ha='center',fontsize=10)
            if nacional['mediana'] is not None:
                ax.axvline(nacional['mediana'],ls=':',lw=1.3,color='#81949C',zorder=1)
            valores=[r[c] for r in rows.values() for c in ('q1','q3') if r[c] is not None]
            if valores:ax.set_xlim(min(valores)-35,max(valores)+35)
            ax.set_yticks(range(len(regioes)),regioes)
            ax.set_ylim(len(regioes)-.45,-1)
            ax.set_title(AREAS[area],loc='left',fontweight='bold',pad=16)
            ax.set_xlabel('Nota da área');ax.grid(axis='x',alpha=.10);ax.set_axisbelow(True)
        fig.text(.06,.955,'Onde ficam o centro e a dispersão das notas?',fontsize=20,weight='bold',color='#202D3B')
        fig.text(.06,.905,'Comparações dentro de cada área · 50% centrais (Q1–Q3) e mediana por região',fontsize=12)
        legenda=[Line2D([0],[0],color='#197C80',lw=7,label='Q1–Q3'),
                 Line2D([0],[0],color='#202D3B',marker='o',ls='',label='Mediana regional'),
                 Line2D([0],[0],color='#81949C',ls=':',label='Mediana nacional da área')]
        fig.legend(handles=legenda,loc='lower center',bbox_to_anchor=(.5,.066),ncol=3,frameon=False)
        fig.text(.06,.025,'Presentes com nota na própria área, incluindo zero. Cada painel tem escala própria; não comparar dificuldade entre áreas.\n'
                 'Quartis calculados dos registros, não dos quartis das UFs. Fonte: RESULTADOS 2025 / regiões IBGE.',fontsize=10,color='#52616E')
        fig.subplots_adjust(left=.12,right=.87,top=.82,bottom=.17,hspace=.57,wspace=.80)
        p=pasta/'local_prova_notas_regioes_2025.png'
        fig.savefig(p,dpi=150);plt.close(fig)
    return p
