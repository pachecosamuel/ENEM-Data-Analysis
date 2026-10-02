"""Visuais de participação: lê somente indicadores já publicados."""
from pathlib import Path
import matplotlib.pyplot as plt
from src.participacao_graficos import numero, porcentagem


def gerar_comparacao(dias, comparacao, pasta):
    pasta = Path(pasta)
    pasta.mkdir(parents=True, exist_ok=True)
    cores = {2024: '#537687', 2025: '#178778'}
    with plt.rc_context({'font.family': 'DejaVu Sans', 'font.size': 11,
                         'axes.spines.top': False, 'axes.spines.right': False}):
        fig, axes = plt.subplots(1, 3, figsize=(14, 6))
        for ax, indicador, titulo in zip(axes, ('presenca_dia1', 'presenca_dia2', 'retencao'),
                                         ('Presença · 1º dia', 'Presença · 2º dia', 'Permanência entre dias')):
            linha = comparacao.loc[comparacao.indicador == indicador].iloc[0]
            for i, ano in enumerate((2024, 2025)):
                valor = linha[f'taxa_{ano}']
                ax.bar(i, valor, width=.55, color=cores[ano])
                ax.text(i, valor+2, porcentagem(valor), ha='center', weight='bold', fontsize=14)
                ax.text(i, 4, numero(int(linha[f'contagem_{ano}'])), ha='center', color='white', fontsize=11)
            ax.set_ylim(0, 108); ax.set_xticks([0, 1], ['2024', '2025'])
            ax.set_yticks([0, 25, 50, 75, 100]); ax.set_title(titulo, pad=16)
            ax.set_axisbelow(True); ax.grid(axis='y', alpha=.15)
        axes[0].set_ylabel('Percentual (%)')
        fig.suptitle('ENEM: mais presenças em 2025, mas taxas menores', fontsize=17, y=.97)
        primeiro = comparacao.iloc[0]; ret = comparacao.loc[comparacao.indicador == 'retencao'].iloc[0]
        fig.text(.055, .075, 'Presenças: base publicada de cada edição — '
                 f"2024: {numero(int(primeiro.denominador_2024))}; 2025: {numero(int(primeiro.denominador_2025))}.\n"
                 'Permanência: presentes nos dois dias / presentes no primeiro — '
                 f"2024: {numero(int(ret.denominador_2024))}; 2025: {numero(int(ret.denominador_2025))}.\n"
                 'Números nas barras = contagens. Comparação descritiva, sem vínculo entre pessoas.', fontsize=10)
        fig.subplots_adjust(left=.06, right=.98, bottom=.27, top=.78, wspace=.27)
        p1 = pasta/'participacao_comparacao_2024_2025.png'
        fig.savefig(p1, dpi=180); plt.close(fig)

        dados = dias.loc[dias.edicao == 2024]
        nomes = {'presente': 'Presença completa', 'ausente': 'Ausência completa', 'eliminado': 'Eliminação completa',
                 'misto': 'Situação mista', 'dados_ausentes': 'Dados ausentes', 'codigo_invalido': 'Código inválido'}
        estados = [s for s in nomes if dados.loc[dados.status == s, 'quantidade'].sum() > 0]
        fig, axes = plt.subplots(1, 2, figsize=(13, 5.5), sharex=True)
        for ax, dia in zip(axes, (1, 2)):
            linhas = [dados.loc[(dados.dia == dia) & (dados.status == s)].iloc[0] for s in estados]
            ax.barh(range(len(estados)), [x.percentual_base for x in linhas], color=cores[2024], height=.5)
            for i, linha in enumerate(linhas):
                dentro = linha.percentual_base >= 50
                ax.text(2 if dentro else linha.percentual_base+1, i,
                        f'{porcentagem(linha.percentual_base)} · {numero(int(linha.quantidade))}',
                        va='center', fontsize=11, color='white' if dentro else '#222222')
            ax.set_yticks(range(len(estados)), [nomes[s] for s in estados]); ax.invert_yaxis()
            ax.set_xlim(0, 105); ax.set_title(f'{dia}º dia · ' + ('LC + CH' if dia == 1 else 'CN + MT'))
        fig.suptitle('ENEM 2024: presença, ausência e eliminação permanecem distintas', fontsize=16, y=.97)
        vazios = [nomes[s] for s in nomes if s not in estados]
        fig.text(.03, .06, f'Base: {numero(int(primeiro.denominador_2024))} registros. Presença completa exige código 1 nas duas áreas.\n'
                 + ('Contagem zero nos dois dias: '+', '.join(vazios)+'.' if vazios else 'Todas as situações observadas estão representadas.'), fontsize=10)
        fig.subplots_adjust(left=.16, right=.98, bottom=.23, top=.83, wspace=.75)
        p2 = pasta/'participacao_situacoes_2024.png'
        fig.savefig(p2, dpi=180); plt.close(fig)
    return [p1, p2]
