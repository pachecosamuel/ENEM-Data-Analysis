"""Dois gráficos a partir dos agregados, sem leitura de registros individuais."""
from pathlib import Path
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
from src.participacao_graficos import numero


def decimal(valor):
    return f'{valor:.2f}'.replace('.', ',')


def gerar_graficos_redacao(resultado, pasta):
    pasta = Path(pasta)
    pasta.mkdir(parents=True, exist_ok=True)
    final = resultado['final'][0]
    caminhos = []
    with plt.rc_context({'font.family':'DejaVu Sans', 'font.size':11,
                         'axes.spines.top':False, 'axes.spines.right':False}):
        fig,ax = plt.subplots(figsize=(12,6.5))
        faixas = [0]*10
        for r in resultado['distribuicao']:
            if not 0 <= r['nota'] <= 1000:
                raise ValueError('Nota fora da escala; gráfico não deve omitir observações.')
            faixas[min(int(r['nota']//100),9)] += r['quantidade']
        if sum(faixas) != final['n']:
            raise ValueError('Faixas não reconciliam com notas registradas.')
        ax.bar([50+100*i for i in range(10)], faixas, width=92, color='#527B86')
        for i,n in enumerate(faixas):
            ax.text(50+100*i,n,numero(n),ha='center',va='bottom',fontsize=9)
        ax.axvline(final['mediana'],color='#197C80',lw=2,label=f"Mediana {final['mediana']:g}") if final['n'] else None
        ax.set(xlim=(0,1000), xlabel='Nota final da redação', ylabel='Notas registradas')
        ax.set_xticks(range(0,1001,100))
        ax.yaxis.set_major_formatter(FuncFormatter(lambda v,p:numero(int(v))))
        ax.grid(axis='y',alpha=.13)
        ax.set_axisbelow(True)
        ax.margins(y=.16)
        ax.legend(frameon=False,loc='upper left')
        fig.text(.08,.94,'Como se distribuem as notas de redação?',fontsize=19,weight='bold',color='#202D3B')
        fig.text(.08,.885,f"{numero(final['n'])} notas registradas · média {decimal(final['media'])} · mediana {final['mediana']:g}" if final['n'] else 'Sem notas registradas',fontsize=12)
        fig.text(.08,.065,f"Inclui {numero(final['zeros'])} notas zero. {numero(final['sem_nota'])} registros sem nota ficam fora desta distribuição.\n"
                 'Faixas de 100 pontos: limite inferior incluído; última faixa inclui 1000. Fonte: RESULTADOS 2025.',
                 fontsize=10,color='#52616E')
        fig.subplots_adjust(left=.10,right=.96,top=.80,bottom=.22)
        caminho=pasta/'redacao_distribuicao_2025.png'
        fig.savefig(caminho,dpi=150); plt.close(fig); caminhos.append(caminho)

        comp=resultado['competencias']
        fig,ax=plt.subplots(figsize=(12,6.5))
        for i,r in enumerate(comp):
            if r['n']:
                ax.plot([r['media'],r['mediana']],[i,i],color='#B8C6CC',lw=3,zorder=1)
                ax.scatter(r['media'],i,s=65,color='#197C80',label='Média' if i==0 else None,zorder=3)
                ax.scatter(r['mediana'],i,s=75,color='#202D3B',marker='|',label='Mediana' if i==0 else None,zorder=4)
                ax.text(205,i,f"{decimal(r['media'])}  |  {r['mediana']:g}",va='center',fontsize=11)
        ax.set_yticks(range(5),[f'C{i+1} · {r["competencia"]}' for i,r in enumerate(comp)])
        ax.set(xlim=(0,200),ylim=(4.6,-.8),xlabel='Pontos por competência (escala de 0 a 200)')
        ax.set_xticks(range(0,201,40))
        ax.grid(axis='x',alpha=.15); ax.set_axisbelow(True)
        ax.legend(frameon=False,loc='upper left',bbox_to_anchor=(0,-.14),ncol=2)
        ax.text(205,-.7,'Média | Mediana',fontsize=10,color='#52616E')
        fig.text(.07,.94,'As cinco competências, no mesmo recorte',fontsize=19,weight='bold',color='#202D3B')
        fig.text(.07,.885,f"{numero(comp[0]['n'])} redações sem problemas e com as seis notas completas · zeros mantidos",fontsize=12)
        fig.text(.07,.06,'Notas publicadas pelo Inep; não recalculadas por avaliador. Diferenças não explicam suas causas.\n'
                 'Este recorte exclui situações problemáticas e registros incompletos. Fonte: RESULTADOS 2025.',
                 fontsize=10,color='#52616E')
        fig.subplots_adjust(left=.36,right=.81,top=.80,bottom=.25)
        caminho=pasta/'redacao_competencias_2025.png'
        fig.savefig(caminho,dpi=150); plt.close(fig); caminhos.append(caminho)
    return caminhos
