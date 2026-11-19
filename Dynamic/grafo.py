from dataclasses import dataclass

NIVEIS = ["BAIXO", "MODERADO", "ALTO", "MUITO_ALTO"]
LIMITE_GERAL_CM = 30
LIMITE_PRIORITARIO_CM = 10
VELOCIDADE_GERAL_M_MIN = 80
VELOCIDADE_PRIORITARIO_M_MIN = 40
CHUVA_REFERENCIA_MM_H = 50


def nivel_chuva(mm_h):
    if mm_h >= 50:
        return "MUITO_ALTO"
    if mm_h >= 25:
        return "ALTO"
    if mm_h >= 10:
        return "MODERADO"
    return "BAIXO"


@dataclass(frozen=True)
class Trecho:
    origem: str
    destino: str
    metros: float
    ponto_risco: object
    lamina_cm: float
    custo: float
    bloqueado: bool


class Grafo:
    def __init__(self, locais, trechos, pontos_risco, chuva_mm_h, prioritario):
        self.locais = locais
        self.chuva_mm_h = chuva_mm_h
        self.prioritario = prioritario
        self.limite_cm = LIMITE_PRIORITARIO_CM if prioritario else LIMITE_GERAL_CM
        self.velocidade = VELOCIDADE_PRIORITARIO_M_MIN if prioritario else VELOCIDADE_GERAL_M_MIN
        self.adjacencia = {local: [] for local in locais}
        self.todos_trechos = []
        for origem, destino, metros, ponto_id in trechos:
            ponto = pontos_risco.get(ponto_id) if ponto_id else None
            lamina = self.lamina_estimada(ponto)
            bloqueado = lamina > self.limite_cm
            custo = metros * (1 + lamina / 10)
            for a, b in ((origem, destino), (destino, origem)):
                trecho = Trecho(a, b, metros, ponto, lamina, custo, bloqueado)
                self.todos_trechos.append(trecho)
                if not bloqueado:
                    self.adjacencia[a].append(trecho)

    def lamina_estimada(self, ponto):
        if ponto is None:
            return 0.0
        fator = min(1.0, max(0.0, self.chuva_mm_h) / CHUVA_REFERENCIA_MM_H)
        return round(ponto.lamina_max_cm * fator, 1)

    def vertices(self):
        return list(self.locais)

    def vizinhos(self, local):
        return self.adjacencia[local]

    def trecho(self, origem, destino):
        for trecho in self.adjacencia[origem]:
            if trecho.destino == destino:
                return trecho
        return None

    def trechos_unicos(self):
        vistos = set()
        unicos = []
        for trecho in self.todos_trechos:
            chave = frozenset((trecho.origem, trecho.destino))
            if chave not in vistos:
                vistos.add(chave)
                unicos.append(trecho)
        return unicos

    def trechos_bloqueados(self):
        return [t for t in self.trechos_unicos() if t.bloqueado]

    def trechos_alagados_transitaveis(self):
        return [t for t in self.trechos_unicos() if not t.bloqueado and t.lamina_cm > 0]

    def tempo_minutos(self, metros):
        return metros / self.velocidade

    def numero_trechos(self):
        return sum(len(v) for v in self.adjacencia.values())
