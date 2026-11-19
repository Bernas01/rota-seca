import heapq
from dataclasses import dataclass

INF = float("inf")


@dataclass
class Rota:
    origem: str
    destino: str
    caminho: list
    custo: float
    metros: float
    minutos: float
    trechos_alagados: int


def montar_rota(grafo, caminho, custo):
    if not caminho or custo == INF:
        return None
    metros = 0.0
    alagados = 0
    for a, b in zip(caminho, caminho[1:]):
        trecho = grafo.trecho(a, b)
        metros += trecho.metros
        if trecho.lamina_cm > 0:
            alagados += 1
    return Rota(caminho[0], caminho[-1], caminho, custo, metros, grafo.tempo_minutos(metros), alagados)


class RotaMemoizada:
    def __init__(self, grafo, destinos):
        self.grafo = grafo
        self.destinos = set(destinos)
        self.memo = {}
        self.chamadas = 0
        self.limite_trechos = max(len(grafo.vertices()) - 1, 0)

    def custo(self, local, k):
        self.chamadas += 1
        chave = (local, k)
        if chave in self.memo:
            return self.memo[chave][0]
        if local in self.destinos:
            resultado = (0.0, None)
        elif k == 0:
            resultado = (INF, None)
        else:
            melhor_custo = self.custo(local, k - 1)
            melhor_proximo = None
            for trecho in self.grafo.vizinhos(local):
                total = trecho.custo + self.custo(trecho.destino, k - 1)
                if total < melhor_custo:
                    melhor_custo = total
                    melhor_proximo = trecho.destino
            resultado = (melhor_custo, melhor_proximo)
        self.memo[chave] = resultado
        return resultado[0]

    def caminho(self, origem, k):
        if self.custo(origem, k) == INF:
            return []
        caminho = [origem]
        atual = origem
        while atual not in self.destinos:
            _, proximo = self.memo[(atual, k)]
            if proximo is None:
                k -= 1
                continue
            caminho.append(proximo)
            atual = proximo
            k -= 1
        return caminho

    def melhor_rota(self, origem):
        k = self.limite_trechos
        custo = self.custo(origem, k)
        return montar_rota(self.grafo, self.caminho(origem, k), custo)


class TabelaFloydWarshall:
    def __init__(self, grafo):
        self.grafo = grafo
        self.locais = grafo.vertices()
        self.indice = {local: i for i, local in enumerate(self.locais)}
        n = len(self.locais)
        self.dist = [[INF] * n for _ in range(n)]
        self.proximo = [[None] * n for _ in range(n)]
        for i in range(n):
            self.dist[i][i] = 0.0
            self.proximo[i][i] = i
        for local in self.locais:
            i = self.indice[local]
            for trecho in grafo.vizinhos(local):
                j = self.indice[trecho.destino]
                if trecho.custo < self.dist[i][j]:
                    self.dist[i][j] = trecho.custo
                    self.proximo[i][j] = j
        self.operacoes = 0
        for k in range(n):
            linha_k = self.dist[k]
            for i in range(n):
                dik = self.dist[i][k]
                if dik == INF:
                    continue
                linha_i = self.dist[i]
                prox_i = self.proximo[i]
                for j in range(n):
                    self.operacoes += 1
                    novo = dik + linha_k[j]
                    if novo < linha_i[j]:
                        linha_i[j] = novo
                        prox_i[j] = prox_i[k]

    def custo(self, origem, destino):
        return self.dist[self.indice[origem]][self.indice[destino]]

    def caminho(self, origem, destino):
        i, j = self.indice[origem], self.indice[destino]
        if self.proximo[i][j] is None:
            return []
        caminho = [origem]
        while i != j:
            i = self.proximo[i][j]
            caminho.append(self.locais[i])
        return caminho

    def rota(self, origem, destino):
        return montar_rota(self.grafo, self.caminho(origem, destino), self.custo(origem, destino))

    def melhor_destino(self, origem, destinos):
        candidatos = [(self.custo(origem, d), d) for d in destinos]
        custo, destino = min(candidatos)
        if custo == INF:
            return None
        return self.rota(origem, destino)


def dijkstra(grafo, origem):
    dist = {local: INF for local in grafo.vertices()}
    dist[origem] = 0.0
    fila = [(0.0, origem)]
    while fila:
        d, local = heapq.heappop(fila)
        if d > dist[local]:
            continue
        for trecho in grafo.vizinhos(local):
            novo = d + trecho.custo
            if novo < dist[trecho.destino]:
                dist[trecho.destino] = novo
                heapq.heappush(fila, (novo, trecho.destino))
    return dist
