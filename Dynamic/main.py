import sys

from dados import LEITURAS_CHUVA, LOCAIS, MORADORES, PONTOS_APOIO, PONTOS_RISCO, TAREFAS_MUTIRAO, TRECHOS
from eficiencia import comparar_consultas, comparar_memoizacao, comparar_mochila
from grafo import LIMITE_GERAL_CM, LIMITE_PRIORITARIO_CM, Grafo, nivel_chuva
from mutirao import pontuacao, planejar_mutirao
from rotas import RotaMemoizada, TabelaFloydWarshall

CHUVA_PADRAO = 62.4
HORAS_PADRAO = 40
LINHA = "-" * 78


def configurar_saida():
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass


def destinos_ativos():
    return [p.local for p in PONTOS_APOIO if p.ativo]


def apoio_por_local(local):
    return next((p for p in PONTOS_APOIO if p.local == local), None)


def montar_grafo(chuva, prioritario):
    return Grafo(LOCAIS, TRECHOS, PONTOS_RISCO, chuva, prioritario)


def titulo(texto):
    print()
    print(LINHA)
    print(texto.upper())
    print(LINHA)


def formatar_caminho(caminho):
    return "\n".join(f"   {i}. {LOCAIS[local]}" for i, local in enumerate(caminho, 1))


def imprimir_rota(rota):
    apoio = apoio_por_local(rota.destino)
    print(f"Destino: {apoio.nome} - {apoio.endereco} - {apoio.capacidade} vagas")
    print(f"Distância: {rota.metros:.0f} m | Tempo estimado a pé: {rota.minutos:.0f} min")
    print(f"Trechos com água no caminho: {rota.trechos_alagados}")
    print("Caminho:")
    print(formatar_caminho(rota.caminho))


def mostrar_cenario(chuva):
    titulo(f"Cenário de chuva: {chuva:.1f} mm/h ({nivel_chuva(chuva)})")
    print("Leituras registradas no banco da Rota Seca:")
    for bairro, quando, mm in LEITURAS_CHUVA:
        print(f"   {quando}  {bairro:<16} {mm:>5.1f} mm/h  {nivel_chuva(mm)}")
    for prioritario, rotulo in ((False, f"público geral (limite {LIMITE_GERAL_CM} cm)"),
                               (True, f"público prioritário (limite {LIMITE_PRIORITARIO_CM} cm)")):
        grafo = montar_grafo(chuva, prioritario)
        print()
        print(f"Trechos bloqueados para o {rotulo}:")
        bloqueados = grafo.trechos_bloqueados()
        if not bloqueados:
            print("   nenhum")
        for t in bloqueados:
            print(f"   {LOCAIS[t.origem]} <-> {LOCAIS[t.destino]}  (lâmina estimada {t.lamina_cm:.0f} cm)")
    print()
    print("Pontos de apoio ativos:")
    for p in PONTOS_APOIO:
        situacao = "ativo" if p.ativo else "INATIVO (não é usado nas rotas)"
        print(f"   {p.nome:<32} {p.tipo:<7} {p.capacidade:>4} vagas  {situacao}")


def escolher_morador():
    print()
    for m in MORADORES:
        perfil = "prioritário" if m.prioritario() else "geral"
        print(f"   {m.id}. {m.nome:<18} {m.bairro:<16} {m.idade()} anos  perfil {perfil}")
    escolha = ler_inteiro("Número do morador: ", 1, len(MORADORES))
    return MORADORES[escolha - 1]


def rota_segura(chuva, morador):
    grafo = montar_grafo(chuva, morador.prioritario())
    calculadora = RotaMemoizada(grafo, destinos_ativos())
    rota = calculadora.melhor_rota(morador.local)
    perfil = "prioritário (idoso ou mobilidade reduzida)" if morador.prioritario() else "geral"
    titulo(f"Rota segura de {morador.nome} - memoização")
    print(f"Chuva: {chuva:.1f} mm/h ({nivel_chuva(chuva)}) | Perfil: {perfil}")
    if rota is None:
        print("Não existe rota segura agora. Permaneça em local alto e acione a Defesa Civil (199).")
    else:
        imprimir_rota(rota)
        seco = RotaMemoizada(montar_grafo(0, morador.prioritario()), destinos_ativos()).melhor_rota(morador.local)
        if seco and seco.caminho != rota.caminho:
            print(f"Sem chuva, o caminho seria de {seco.metros:.0f} m. O desvio acrescenta {rota.metros - seco.metros:.0f} m.")
    print(f"Estados calculados (local, k) na memória: {len(calculadora.memo)} | chamadas: {calculadora.chamadas}")


def matriz_tempos(chuva):
    titulo("Tempo a pé de cada morador até cada ponto de apoio - tabulação (Floyd-Warshall)")
    print(f"Chuva: {chuva:.1f} mm/h ({nivel_chuva(chuva)}) | '--' = sem caminho seguro")
    ativos = [p for p in PONTOS_APOIO if p.ativo]
    print()
    print("Morador".ljust(20) + "".join(f"{('Apoio ' + str(p.id)):>12}" for p in ativos) + "   Melhor opção")
    tabelas = {}
    for m in MORADORES:
        prioritario = m.prioritario()
        if prioritario not in tabelas:
            tabelas[prioritario] = TabelaFloydWarshall(montar_grafo(chuva, prioritario))
        tabela = tabelas[prioritario]
        celulas = []
        for p in ativos:
            rota = tabela.rota(m.local, p.local)
            celulas.append(f"{rota.minutos:>9.0f} min" if rota else f"{'--':>12}")
        melhor = tabela.melhor_destino(m.local, [p.local for p in ativos])
        nome_melhor = apoio_por_local(melhor.destino).nome if melhor else "sem rota segura"
        print(m.nome.ljust(20) + "".join(f"{c:>12}" for c in celulas) + "   " + nome_melhor)
    print()
    for p in ativos:
        print(f"   Apoio {p.id}: {p.nome}")
    total = sum(t.operacoes for t in tabelas.values())
    print(f"Tabelas construídas: {len(tabelas)} (uma por perfil) | operações do laço triplo: {total}")


def rota_entre_locais(chuva):
    titulo("Rota entre dois locais - tabulação (Floyd-Warshall)")
    codigos = list(LOCAIS)
    for i, codigo in enumerate(codigos, 1):
        print(f"   {i:>2}. {LOCAIS[codigo]}")
    origem = codigos[ler_inteiro("Origem: ", 1, len(codigos)) - 1]
    destino = codigos[ler_inteiro("Destino: ", 1, len(codigos)) - 1]
    prioritario = ler_sim_nao("A pessoa é idosa ou tem mobilidade reduzida? (s/n): ")
    tabela = TabelaFloydWarshall(montar_grafo(chuva, prioritario))
    rota = tabela.rota(origem, destino)
    print()
    if rota is None:
        print("Não há caminho seguro entre esses locais com a chuva atual.")
        return
    print(f"Distância: {rota.metros:.0f} m | Tempo: {rota.minutos:.0f} min | Trechos com água: {rota.trechos_alagados}")
    print(formatar_caminho(rota.caminho))


def plano_mutirao(horas):
    plano = planejar_mutirao(TAREFAS_MUTIRAO, horas, PONTOS_RISCO)
    titulo(f"Plano de mutirão de prevenção - tabulação (mochila 0/1) com {horas} horas de equipe")
    print("Tarefas candidatas:")
    for t in TAREFAS_MUTIRAO:
        ponto = PONTOS_RISCO[t.ponto_risco_id]
        print(f"   {t.id}. {t.descricao:<50} {t.horas:>3} h  {t.pessoas:>4} pessoas  {ponto.nivel:<10} pontos {pontuacao(t, PONTOS_RISCO)}")
    print()
    print("Tarefas escolhidas:")
    for t in plano.tarefas:
        print(f"   {t.id}. {t.descricao} ({t.horas} h)")
    print(f"Horas usadas: {plano.horas_usadas} de {plano.horas_disponiveis}")
    print(f"Pessoas beneficiadas: {plano.pessoas} | Pontuação (pessoas x peso do nível de risco): {plano.pontuacao}")
    print(f"Células da tabela calculadas: {plano.celulas_calculadas}")


def comparar_eficiencia(chuva):
    titulo("Eficiência: com e sem programação dinâmica")
    maria = MORADORES[0]
    grafo = montar_grafo(chuva, maria.prioritario())
    print(f"1) Rota da {maria.nome}: recursão ingênua x memoização")
    print(f"{'k (máx. trechos)':>17} {'chamadas sem memo':>18} {'tempo (ms)':>11} {'chamadas com memo':>18} {'tempo (ms)':>11} {'mesmo custo':>12}")
    for k, c1, t1, c2, t2, igual in comparar_memoizacao(grafo, destinos_ativos(), maria.local, [2, 4, 6, 8, 10]):
        print(f"{k:>17} {c1:>18} {t1:>11.2f} {c2:>18} {t2:>11.2f} {('sim' if igual else 'NÃO'):>12}")
    print()
    print("2) Rotas de todos os moradores: memoização por origem x uma tabela Floyd-Warshall")
    origens = [m.local for m in MORADORES]
    tempo_memo, tempo_floyd, operacoes = comparar_consultas(grafo, destinos_ativos(), origens)
    print(f"   Memoização (uma busca por morador): {tempo_memo:.2f} ms")
    vertices = len(grafo.vertices())
    print(f"   Floyd-Warshall (tabela única, {operacoes} operações; limite V³ = {vertices ** 3}): {tempo_floyd:.2f} ms")
    print()
    print(f"3) Mutirão: tabela da mochila x força bruta ({len(TAREFAS_MUTIRAO)} tarefas, {HORAS_PADRAO} horas)")
    celulas, t_tabela, combinacoes, t_bruta, igual = comparar_mochila(TAREFAS_MUTIRAO, HORAS_PADRAO, PONTOS_RISCO)
    print(f"   Tabela: {celulas} células em {t_tabela:.2f} ms")
    print(f"   Força bruta: {combinacoes} combinações em {t_bruta:.2f} ms")
    print(f"   Mesmo resultado: {'sim' if igual else 'NÃO'}")


def ler_inteiro(mensagem, minimo, maximo):
    while True:
        texto = input(mensagem).strip()
        if texto.isdigit() and minimo <= int(texto) <= maximo:
            return int(texto)
        print(f"Digite um número de {minimo} a {maximo}.")


def ler_decimal(mensagem, minimo, maximo):
    while True:
        texto = input(mensagem).strip().replace(",", ".")
        try:
            valor = float(texto)
        except ValueError:
            valor = None
        if valor is not None and minimo <= valor <= maximo:
            return valor
        print(f"Digite um valor de {minimo} a {maximo}.")


def ler_sim_nao(mensagem):
    while True:
        texto = input(mensagem).strip().lower()
        if texto in ("s", "sim"):
            return True
        if texto in ("n", "nao", "não"):
            return False
        print("Responda s ou n.")


def demonstracao():
    mostrar_cenario(CHUVA_PADRAO)
    for morador in MORADORES:
        rota_segura(CHUVA_PADRAO, morador)
    matriz_tempos(CHUVA_PADRAO)
    matriz_tempos(0)
    plano_mutirao(HORAS_PADRAO)
    comparar_eficiencia(CHUVA_PADRAO)


def menu():
    chuva = CHUVA_PADRAO
    opcoes = {
        "1": "Ver cenário de chuva e trechos bloqueados",
        "2": "Rota segura de um morador até o ponto de apoio (memoização)",
        "3": "Tempo de cada morador até cada ponto de apoio (Floyd-Warshall)",
        "4": "Rota entre dois locais quaisquer (Floyd-Warshall)",
        "5": "Plano de mutirão de prevenção (mochila 0/1)",
        "6": "Comparar eficiência com e sem programação dinâmica",
        "7": "Alterar a chuva (mm/h)",
        "0": "Sair",
    }
    while True:
        titulo(f"Rota Seca - chuva atual: {chuva:.1f} mm/h ({nivel_chuva(chuva)})")
        for chave, texto in opcoes.items():
            print(f"   {chave}. {texto}")
        escolha = input("Opção: ").strip()
        if escolha == "1":
            mostrar_cenario(chuva)
        elif escolha == "2":
            rota_segura(chuva, escolher_morador())
        elif escolha == "3":
            matriz_tempos(chuva)
        elif escolha == "4":
            rota_entre_locais(chuva)
        elif escolha == "5":
            plano_mutirao(ler_inteiro("Horas de equipe disponíveis (1 a 200): ", 1, 200))
        elif escolha == "6":
            comparar_eficiencia(chuva)
        elif escolha == "7":
            chuva = ler_decimal("Chuva em mm/h (0 a 200): ", 0, 200)
        elif escolha == "0":
            print("Até logo.")
            return
        else:
            print("Opção inválida.")
        if escolha in opcoes:
            input("\nPressione Enter para continuar...")


if __name__ == "__main__":
    configurar_saida()
    if "--demo" in sys.argv:
        demonstracao()
    else:
        try:
            menu()
        except (KeyboardInterrupt, EOFError):
            print("\nAté logo.")
