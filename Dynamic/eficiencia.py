import time

from mutirao import planejar_forca_bruta, planejar_mutirao
from rotas import INF, RotaMemoizada, TabelaFloydWarshall


class RecursaoIngenua:
    def __init__(self, grafo, destinos):
        self.grafo = grafo
        self.destinos = set(destinos)
        self.chamadas = 0

    def custo(self, local, k):
        self.chamadas += 1
        if local in self.destinos:
            return 0.0
        if k == 0:
            return INF
        melhor = self.custo(local, k - 1)
        for trecho in self.grafo.vizinhos(local):
            melhor = min(melhor, trecho.custo + self.custo(trecho.destino, k - 1))
        return melhor


def medir(funcao):
    inicio = time.perf_counter()
    resultado = funcao()
    return resultado, (time.perf_counter() - inicio) * 1000


def comparar_memoizacao(grafo, destinos, origem, limites):
    linhas = []
    for k in limites:
        ingenua = RecursaoIngenua(grafo, destinos)
        custo_ingenuo, tempo_ingenuo = medir(lambda: ingenua.custo(origem, k))
        memo = RotaMemoizada(grafo, destinos)
        custo_memo, tempo_memo = medir(lambda: memo.custo(origem, k))
        linhas.append((k, ingenua.chamadas, tempo_ingenuo, memo.chamadas, tempo_memo, custo_ingenuo == custo_memo))
    return linhas


def comparar_consultas(grafo, destinos, origens):
    def com_memo():
        return [RotaMemoizada(grafo, destinos).melhor_rota(o) for o in origens]

    def com_floyd():
        tabela = TabelaFloydWarshall(grafo)
        return [tabela.melhor_destino(o, destinos) for o in origens], tabela.operacoes

    _, tempo_memo = medir(com_memo)
    (_, operacoes), tempo_floyd = medir(com_floyd)
    return tempo_memo, tempo_floyd, operacoes


def comparar_mochila(tarefas, horas, pontos_risco):
    plano, tempo_tabela = medir(lambda: planejar_mutirao(tarefas, horas, pontos_risco))
    (melhor, combinacoes), tempo_bruta = medir(lambda: planejar_forca_bruta(tarefas, horas, pontos_risco))
    return plano.celulas_calculadas, tempo_tabela, combinacoes, tempo_bruta, plano.pontuacao == melhor
