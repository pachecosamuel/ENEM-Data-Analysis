"""Consolidação de indicadores anuais; nunca vincula registros individuais."""
import csv
import json
import os
from pathlib import Path
import tempfile

from src.desempenho import percentual
from src.desempenho_execucao import hash_arquivo, raiz_projeto
from src.participacao import validar_participacao


def comparar_participacao(resultados):
    if set(resultados) != {2024, 2025}:
        raise ValueError('Comparação esperada: 2024 e 2025.')
    for resultado in resultados.values():
        validar_participacao(resultado)
    consolidado = {nome: [] for nome in ('dias', 'transicoes', 'resumo')}
    medidas = {}
    for ano, resultado in sorted(resultados.items()):
        resumo = resultado['resumo']
        for nome in consolidado:
            linhas = [resumo] if nome == 'resumo' else resultado[nome]
            consolidado[nome].extend({'edicao': ano, **linha} for linha in linhas)
        medidas[ano] = {
            'presenca_dia1': (resumo['presentes_dia1'], resumo['total_base']),
            'presenca_dia2': (resumo['presentes_dia2'], resumo['total_base']),
            'presenca_ambos': (resumo['presentes_ambos'], resumo['total_base']),
            'retencao': (resumo['presentes_ambos'], resumo['presentes_dia1'])}
    comparacao = []
    for indicador in medidas[2024]:
        n24, d24 = medidas[2024][indicador]
        n25, d25 = medidas[2025][indicador]
        p24, p25 = percentual(n24, d24), percentual(n25, d25)
        comparacao.append({'indicador': indicador, 'contagem_2024': n24, 'denominador_2024': d24,
                          'taxa_2024': p24, 'contagem_2025': n25, 'denominador_2025': d25,
                          'taxa_2025': p25, 'diferenca_contagem_2025_menos_2024': n25-n24,
                          'diferenca_pp_2025_menos_2024': None if p24 is None or p25 is None else p25-p24})
    consolidado['comparacao'] = comparacao
    return consolidado


def executar_comparacao(raiz=None):
    raiz = raiz_projeto(raiz)
    resultados = {}
    for ano in (2024, 2025):
        report = json.loads((raiz/f'reports/validacao_participacao_{ano}.json').read_text(encoding='utf-8'))
        for nome, esperado in report['hashes_csv'].items():
            if hash_arquivo(raiz/'analitica'/nome) != esperado:
                raise ValueError(f'Agregado alterado desde a validação: {nome}')
        if hash_arquivo(raiz/report['fonte']) != report['sha256_depois']:
            raise ValueError(f'Fonte {ano} diverge da validação.')
        resultados[ano] = report['resultado']
    consolidado = comparar_participacao(resultados)
    with tempfile.TemporaryDirectory(prefix='comparacao_', dir=raiz/'work') as temp:
        arquivos = []
        for nome, linhas in consolidado.items():
            p = Path(temp)/f'participacao_2024_2025_{nome}.csv'
            with p.open('w', encoding='utf-8', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=list(linhas[0]))
                writer.writeheader(); writer.writerows(linhas)
            arquivos.append(p)
        for p in arquivos:
            os.replace(p, raiz/'analitica'/p.name)
    return consolidado
