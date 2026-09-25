"""Leitura estrita de PARTICIPANTES e publicação de um CSV agregado, sem reports."""
import csv
import os
from pathlib import Path
import tempfile
import duckdb
from src.trusted_resultados import raiz_projeto, literal, sha256
from src.perfil_economico import calcular_perfil_economico

FONTE = Path('raw/microdados_enem_2025/microdados_enem_2025/DADOS/PARTICIPANTES_2025.csv')
SAIDA = Path('analitica/perfil_economico_2025.csv')


def executar_perfil_economico(raiz=None):
    raiz = raiz_projeto(raiz)
    fonte = raiz / FONTE
    antes = sha256(fonte)
    with fonte.open(encoding='latin-1', newline='') as f:
        nomes = next(csv.reader(f, delimiter=';'))
    campos = ('NU_INSCRICAO', 'NU_ANO', 'Q006', 'Q007')
    if len(nomes) != len(set(nomes)) or not set(campos).issubset(nomes):
        raise ValueError('Cabeçalho inválido de PARTICIPANTES 2025.')
    esquema = '{' + ','.join(f"{literal(n)}:'VARCHAR'" for n in nomes) + '}'
    (raiz / 'work').mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='perfil_economico_', dir=raiz / 'work') as temp:
        with duckdb.connect(str(Path(temp) / 'leitura.duckdb'), config={
            'memory_limit': '256MB', 'threads': '1', 'temp_directory': str(Path(temp) / 'spill'),
            'max_temp_directory_size': '2GB'}) as con:
            projecao = ','.join(f"NULLIF(trim({c}), '') {c}" for c in campos)
            con.execute(f'''CREATE TABLE participantes AS SELECT {projecao}
                FROM read_csv({literal(fonte.as_posix())}, columns={esquema}, auto_detect=false,
                header=true, delim=';', encoding='latin-1', quote='"', escape='"', nullstr='',
                strict_mode=true, ignore_errors=false, null_padding=false, parallel=false)''')
            total, nulos, duplicadas, anos = con.execute('''SELECT count(*),
                count(*) FILTER(WHERE NU_INSCRICAO IS NULL),
                count(NU_INSCRICAO)-count(DISTINCT NU_INSCRICAO),
                count(*) FILTER(WHERE NU_ANO IS DISTINCT FROM '2025') FROM participantes''').fetchone()
            if nulos or duplicadas or anos or not total:
                raise ValueError('Base vazia ou chave/ano inválidos em PARTICIPANTES.')
            linhas = calcular_perfil_economico(con)
        if sha256(fonte) != antes:
            raise ValueError('Fonte alterada durante a leitura.')
        for pergunta in ('Q006', 'Q007'):
            if sum(r['quantidade'] for r in linhas if r['pergunta'] == pergunta) != total:
                raise ValueError(f'Contagem não reconciliada: {pergunta}')
        for r in linhas:
            r['sha256_fonte'] = antes
        temporario = Path(temp) / SAIDA.name
        with temporario.open('w', encoding='utf-8', newline='') as f:
            w = csv.DictWriter(f, fieldnames=list(linhas[0]))
            w.writeheader()
            w.writerows(linhas)
        (raiz / SAIDA).parent.mkdir(exist_ok=True)
        os.replace(temporario, raiz / SAIDA)
    return linhas


if __name__ == '__main__':
    for linha in executar_perfil_economico():
        print(linha['pergunta'], linha['codigo'] or 'Sem resposta', linha['quantidade'], linha['percentual_base'])
