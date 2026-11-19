import os
import sys
import unittest
from datetime import date

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dados import LOCAIS, MORADORES, PONTOS_APOIO, PONTOS_RISCO, TAREFAS_MUTIRAO, TRECHOS
from eficiencia import RecursaoIngenua
from grafo import Grafo, nivel_chuva
from mutirao import planejar_forca_bruta, planejar_mutirao
from rotas import RotaMemoizada, TabelaFloydWarshall, dijkstra

CENARIOS = [0, 9.9, 10, 14.2, 25, 31.8, 50, 62.4, 120]
DESTINOS = [p.local for p in PONTOS_APOIO if p.ativo]


def grafo(chuva, prioritario):
    return Grafo(LOCAIS, TRECHOS, PONTOS_RISCO, chuva, prioritario)


def menor_ate_destinos(g, origem):
    dist = dijkstra(g, origem)
    return min(dist[d] for d in DESTINOS)


class TestNivelChuva(unittest.TestCase):
    def test_escala_cge(self):
        self.assertEqual(nivel_chuva(0), "BAIXO")
        self.assertEqual(nivel_chuva(9.99), "BAIXO")
        self.assertEqual(nivel_chuva(10), "MODERADO")
        self.assertEqual(nivel_chuva(25), "ALTO")
        self.assertEqual(nivel_chuva(50), "MUITO_ALTO")


class TestGrafo(unittest.TestCase):
    def test_sem_chuva_nada_bloqueado(self):
        self.assertEqual(grafo(0, True).trechos_bloqueados(), [])

    def test_lamina_proporcional_e_limitada(self):
        g = grafo(25, False)
        self.assertEqual(g.lamina_estimada(PONTOS_RISCO[1]), 40.0)
        self.assertEqual(grafo(500, False).lamina_estimada(PONTOS_RISCO[1]), 80.0)

    def test_prioritario_tem_mais_bloqueios(self):
        for chuva in CENARIOS:
            self.assertGreaterEqual(len(grafo(chuva, True).trechos_bloqueados()),
                                    len(grafo(chuva, False).trechos_bloqueados()))

    def test_trecho_bloqueado_fora_da_adjacencia(self):
        g = grafo(62.4, False)
        self.assertIsNone(g.trecho("CASA_MARIA", "CORREGO"))


class TestMemoizacao(unittest.TestCase):
    def test_igual_ao_dijkstra_em_todos_os_cenarios(self):
        for chuva in CENARIOS:
            for prioritario in (False, True):
                g = grafo(chuva, prioritario)
                calc = RotaMemoizada(g, DESTINOS)
                for origem in g.vertices():
                    esperado = menor_ate_destinos(g, origem)
                    obtido = calc.custo(origem, calc.limite_trechos)
                    self.assertAlmostEqual(obtido, esperado, places=6)

    def test_caminho_valido_e_coerente_com_custo(self):
        g = grafo(62.4, True)
        rota = RotaMemoizada(g, DESTINOS).melhor_rota("CASA_MARIA")
        self.assertEqual(rota.caminho[0], "CASA_MARIA")
        self.assertIn(rota.destino, DESTINOS)
        custo = sum(g.trecho(a, b).custo for a, b in zip(rota.caminho, rota.caminho[1:]))
        self.assertAlmostEqual(custo, rota.custo)
        self.assertNotIn("CORREGO", rota.caminho)

    def test_nao_usa_ponto_de_apoio_inativo(self):
        for chuva in CENARIOS:
            rota = RotaMemoizada(grafo(chuva, False), DESTINOS).melhor_rota("CASA_LUCAS")
            if rota:
                self.assertNotEqual(rota.destino, "ESCOLA_HELENA")

    def test_igual_a_recursao_ingenua(self):
        g = grafo(31.8, False)
        for k in range(0, 8):
            self.assertEqual(RotaMemoizada(g, DESTINOS).custo("CASA_JOSE", k),
                             RecursaoIngenua(g, DESTINOS).custo("CASA_JOSE", k))

    def test_memoizacao_reduz_chamadas(self):
        g = grafo(62.4, True)
        ingenua = RecursaoIngenua(g, DESTINOS)
        ingenua.custo("CASA_MARIA", 9)
        memo = RotaMemoizada(g, DESTINOS)
        memo.custo("CASA_MARIA", 9)
        self.assertLess(memo.chamadas * 50, ingenua.chamadas)

    def test_sem_rota_retorna_none(self):
        trechos = [("CASA_MARIA", "CORREGO", 60, 1), ("CORREGO", "ABRIGO_PANTANAL", 50, 1)]
        g = Grafo(LOCAIS, trechos, PONTOS_RISCO, 62.4, True)
        self.assertIsNone(RotaMemoizada(g, ["ABRIGO_PANTANAL"]).melhor_rota("CASA_MARIA"))


class TestFloydWarshall(unittest.TestCase):
    def test_igual_ao_dijkstra_para_todos_os_pares(self):
        for chuva in (0, 31.8, 62.4):
            for prioritario in (False, True):
                g = grafo(chuva, prioritario)
                tabela = TabelaFloydWarshall(g)
                for origem in g.vertices():
                    dist = dijkstra(g, origem)
                    for destino in g.vertices():
                        self.assertAlmostEqual(tabela.custo(origem, destino), dist[destino], places=6)

    def test_caminho_reconstruido(self):
        g = grafo(62.4, False)
        tabela = TabelaFloydWarshall(g)
        caminho = tabela.caminho("CASA_ANA", "UBS_ROMANO")
        self.assertEqual(caminho, ["CASA_ANA", "AVENIDA_C", "UBS_ROMANO"])

    def test_concorda_com_memoizacao_no_melhor_destino(self):
        for chuva in CENARIOS:
            for m in MORADORES:
                g = grafo(chuva, m.prioritario())
                a = TabelaFloydWarshall(g).melhor_destino(m.local, DESTINOS)
                b = RotaMemoizada(g, DESTINOS).melhor_rota(m.local)
                self.assertAlmostEqual(a.custo, b.custo)


class TestMutirao(unittest.TestCase):
    def test_igual_a_forca_bruta(self):
        for horas in range(0, 70, 3):
            plano = planejar_mutirao(TAREFAS_MUTIRAO, horas, PONTOS_RISCO)
            melhor, _ = planejar_forca_bruta(TAREFAS_MUTIRAO, horas, PONTOS_RISCO)
            self.assertEqual(plano.pontuacao, melhor)
            self.assertLessEqual(plano.horas_usadas, horas)

    def test_orcamento_zero(self):
        plano = planejar_mutirao(TAREFAS_MUTIRAO, 0, PONTOS_RISCO)
        self.assertEqual(plano.tarefas, [])


class TestMorador(unittest.TestCase):
    def test_prioritario(self):
        hoje = date(2026, 11, 16)
        self.assertTrue(MORADORES[0].prioritario(hoje))
        self.assertFalse(MORADORES[1].prioritario(hoje))
        self.assertTrue(MORADORES[3].prioritario(hoje))


if __name__ == "__main__":
    unittest.main()
