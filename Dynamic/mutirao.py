from dataclasses import dataclass
from itertools import combinations

PESO_NIVEL = {"BAIXO": 1, "MODERADO": 2, "ALTO": 3, "MUITO_ALTO": 4}


@dataclass
class PlanoMutirao:
    tarefas: list
    horas_disponiveis: int
    horas_usadas: int
    pontuacao: int
    pessoas: int
    celulas_calculadas: int


def pontuacao(tarefa, pontos_risco):
    return tarefa.pessoas * PESO_NIVEL[pontos_risco[tarefa.ponto_risco_id].nivel]


def planejar_mutirao(tarefas, horas_disponiveis, pontos_risco):
    n = len(tarefas)
    tabela = [[0] * (horas_disponiveis + 1) for _ in range(n + 1)]
    for i in range(1, n + 1):
        tarefa = tarefas[i - 1]
        valor = pontuacao(tarefa, pontos_risco)
        for h in range(horas_disponiveis + 1):
            tabela[i][h] = tabela[i - 1][h]
            if tarefa.horas <= h:
                com_tarefa = tabela[i - 1][h - tarefa.horas] + valor
                if com_tarefa > tabela[i][h]:
                    tabela[i][h] = com_tarefa
    escolhidas = []
    h = horas_disponiveis
    for i in range(n, 0, -1):
        if tabela[i][h] != tabela[i - 1][h]:
            tarefa = tarefas[i - 1]
            escolhidas.append(tarefa)
            h -= tarefa.horas
    escolhidas.reverse()
    return PlanoMutirao(
        escolhidas,
        horas_disponiveis,
        sum(t.horas for t in escolhidas),
        tabela[n][horas_disponiveis],
        sum(t.pessoas for t in escolhidas),
        (n + 1) * (horas_disponiveis + 1),
    )


def planejar_forca_bruta(tarefas, horas_disponiveis, pontos_risco):
    melhor = 0
    combinacoes = 0
    for tamanho in range(len(tarefas) + 1):
        for grupo in combinations(tarefas, tamanho):
            combinacoes += 1
            if sum(t.horas for t in grupo) <= horas_disponiveis:
                melhor = max(melhor, sum(pontuacao(t, pontos_risco) for t in grupo))
    return melhor, combinacoes
