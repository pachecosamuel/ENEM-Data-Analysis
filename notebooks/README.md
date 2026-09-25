# Processamento

- `01_resultados_trusted.ipynb`: carga raw → trusted; reexecute somente para reconstruir a base.
- `02_desempenho_por_area.ipynb`: cálculo e auditoria de desempenho sobre a trusted.
- `03_participacao_entre_dias.ipynb`: pares de presença, matriz de transições e retenção sobre a trusted.

- `04_redacao.ipynb`: contagem independente de inscritos, nota final, status e perfil de competências; gera dois PNGs.

- `05_local_prova.ipynb`: regiões/UFs, presença e permanência, desempenho por área; um PNG de notas regionais e tabela de top 3 UFs pela taxa do dia 2.

- `06_rede_escolar.ipynb`: cobertura e distribuições das quatro áreas por dependência administrativa; um PNG, sem join com PARTICIPANTES.

- `07_perfil_economico.ipynb`: Q007 renda familiar e Q006 declaração de possuir renda em PARTICIPANTES; um CSV e dois PNGs, sem join, nova trusted, testes ou reports. Regras nas células de abertura.

As regras estão em `src/`, não duplicadas nas células. Use o kernel ENEM 2025 (.venv). Para leitura dos resultados, prefira [a apresentação](../apresentacao/visao_geral_2025.ipynb).
