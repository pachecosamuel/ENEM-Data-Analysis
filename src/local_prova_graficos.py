"""Duas visões regionais; lê somente agregados já calculados."""
from pathlib import Path
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from src.local_prova_referencia import REGIOES
from src.desempenho import AREAS
from src.participacao_graficos import numero


def gerar_graficos_local_prova(resultado,pasta):
    pasta=Path(pasta);pasta.mkdir(parents=True,exist_ok=True)
    presenca={r['local']:r for r in resultado['participacao'] if r['nivel']=='Região'}
    regioes=[r for r in REGIOES if r in presenca]
    caminhos=[]
    with plt.rc_context({'font.family':'DejaVu Sans','font.size':11,
                         'axes.spines.top':False,'axes.spines.right':False}):
        fig,ax=plt.subplots(figsize=(12,7))
        for dia,deslocamento,cor in [(1,-.17,'#9CAFB7'),(2,.17,'#197C80')]:
            for i,reg in enumerate(regioes):
                taxa=presenca[reg][f'taxa_presenca_dia{dia}']
                if taxa is not None:
                    ax.barh(i+deslocamento,taxa,height=.29,color=cor,label=f'{dia}º dia' if i==0 else None)
                    ax.text(taxa+1,i+deslocamento,f'{taxa:.2f}%'.replace('.',','),va='center',fontsize=11)
        ax.set_yticks(range(len(regioes)),[f'{r}\nBase: {numero(presenca[r]["total_base"])}' for r in regioes])
        ax.invert_yaxis();ax.set(xlim=(0,100),xlabel='Presença completa / registros da própria região (%)')
        ax.grid(axis='x',alpha=.12);ax.set_axisbelow(True)
        ax.legend(frameon=False,ncol=2,loc='upper left',bbox_to_anchor=(0,-.13))
        fig.text(.07,.94,'Como a presença varia por região de aplicação?',fontsize=19,weight='bold',color='#202D3B')
        fig.text(.07,.885,'Mesma regra nos dois dias: presença nas duas áreas do dia',fontsize=12)
        fig.text(.07,.045,'ENEM 2025 · Local de prova, não residência. Base inclui ausentes e eliminados.\n'
                 'Contagens e permanência entre dias estão nas tabelas de apoio. Fonte: RESULTADOS / regiões IBGE.',fontsize=10,color='#52616E')
        fig.subplots_adjust(left=.23,right=.95,top=.81,bottom=.23)
        p=pasta/'local_prova_presenca_regioes_2025.png'
        fig.savefig(p,dpi=150);plt.close(fig);caminhos.append(p)

        fig,axes=plt.subplots(2,2,figsize=(14,10))
        dados=resultado['desempenho']
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
                ax.text(1.02,i,numero(r['elegiveis']),transform=ax.get_yaxis_transform(),va='center',fontsize=9,color='#52616E')
            if nacional['mediana'] is not None:
                ax.axvline(nacional['mediana'],ls=':',lw=1.3,color='#81949C',zorder=1)
            ax.text(1.02,-.82,'Notas elegíveis',transform=ax.get_yaxis_transform(),fontsize=9,color='#52616E')
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
        fig.savefig(p,dpi=150);plt.close(fig);caminhos.append(p)
    return caminhos
