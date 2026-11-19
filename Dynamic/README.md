# Rota Seca · Dynamic Programming

**FIAP · Global Solution 2026.2 · CitizenTech · Engenharia de Software, 2º ano**

| Integrante | RM |
|---|---|
| Felipe Bernardes de Almeida | RM564360 |
| Guilherme Romero Nogueira de Lima | RM564431 |

Repositório do projeto: https://github.com/0Romero/rota-seca

---

## 1. O problema

A **Rota Seca** avisa moradores de áreas que alagam, na várzea do Rio Tietê (Zona Leste de São Paulo), quando a chuva fica forte e indica **para onde ir e por qual caminho**. Este módulo resolve três necessidades da solução com programação dinâmica:

1. **Rota segura do morador até o ponto de apoio mais próximo**, desviando dos trechos alagados (memoização sobre grafo).
2. **Tabela de tempos de todos os locais para todos os locais**, para a Defesa Civil saber em quanto tempo cada morador chega a cada ponto de apoio (tabulação com Floyd-Warshall).
3. **Plano de mutirão de prevenção**: com poucas horas de equipe, escolher quais limpezas fazer antes da chuva para proteger o maior número de pessoas (tabulação com a mochila 0/1).

Os bairros, pontos de risco, pontos de apoio, moradores e leituras de chuva são os **mesmos dados do banco Oracle e da API Java** do projeto (tabelas `RS_BAIRRO`, `RS_PONTO_RISCO`, `RS_PONTO_APOIO`, `RS_MORADOR` e `RS_LEITURA_CHUVA`). Todos os dados são simulados; os nomes de pessoas são fictícios.

## 2. Como executar

Requisito: **Python 3.10 ou superior**. Não usa bibliotecas externas.

```bash
python main.py            # menu interativo
python main.py --demo     # executa todas as funcionalidades de uma vez
python -m unittest discover -s testes -v   # 17 testes automatizados
```

No Windows, use `py` no lugar de `python`, se necessário.

## 3. Estrutura do projeto

| Arquivo | Conteúdo |
|---|---|
| `main.py` | Menu interativo, modo demonstração e apresentação dos resultados |
| `dados.py` | Locais, trechos de rua, pontos de risco, pontos de apoio, moradores, tarefas do mutirão e leituras de chuva |
| `grafo.py` | Grafo ponderado das ruas, cálculo da lâmina d'água, bloqueios e escala de chuva do CGE |
| `rotas.py` | Rota segura com **memoização**, tabela **Floyd-Warshall** e Dijkstra (usado para validar) |
| `mutirao.py` | Plano de mutirão com a **mochila 0/1 tabulada** e a versão por força bruta (para comparar) |
| `eficiencia.py` | Comparações de chamadas, operações e tempo com e sem programação dinâmica |
| `testes/test_rota_seca.py` | Testes automatizados que comparam os algoritmos entre si e com soluções de referência |

## 4. Modelagem: o bairro como grafo

- **Vértices (21):** casas dos moradores, esquinas, pontos de risco e pontos de apoio.
- **Arestas (28 trechos de rua, nos dois sentidos):** cada uma tem o comprimento em metros e, se passa por um ponto de risco, a referência a ele.
- **Lâmina d'água estimada** em um trecho com ponto de risco:
  `lâmina = lâmina máxima registrada no ponto × min(1, chuva em mm/h ÷ 50)`
- **Bloqueio:** o trecho sai do grafo se a lâmina passar do limite do perfil:
  - público geral: **30 cm**;
  - público prioritário (60 anos ou mais, ou mobilidade reduzida, mesma regra da API Java): **10 cm**.
- **Custo de um trecho transitável:** `metros × (1 + lâmina ÷ 10)`. Um trecho seco custa o próprio comprimento; um trecho com água fica mais "caro", então o algoritmo só passa por ele se valer a pena.
- **Velocidade a pé:** 80 m/min para o público geral e 40 m/min para o prioritário.
- **Escala de chuva (CGE-SP):** abaixo de 10 mm/h BAIXO; a partir de 10 MODERADO; a partir de 25 ALTO; a partir de 50 MUITO_ALTO.
- Pontos de apoio **inativos** nunca são usados como destino.

## 5. Algoritmos

### 5.1 Memoização: rota segura até o ponto de apoio mais próximo (`rotas.py`, classe `RotaMemoizada`)

Subproblema: `custo(v, k)` = menor custo para sair do local `v` e chegar a **qualquer** ponto de apoio ativo usando no máximo `k` trechos.

```
custo(v, k) = 0                                   se v é ponto de apoio ativo
custo(v, 0) = infinito                            se v não é ponto de apoio
custo(v, k) = min( custo(v, k-1),
                   min sobre os vizinhos u de v: custo do trecho (v,u) + custo(u, k-1) )
```

Com `k = V − 1`, o resultado é a rota de menor custo, porque um caminho mínimo nunca repete vértices. Cada par `(v, k)` é calculado **uma única vez** e guardado em um dicionário. A escolha que gerou o mínimo também é guardada, o que permite **reconstruir o caminho** completo.

- **Sem memoização:** o número de chamadas cresce exponencialmente com `k` (a mesma subrota é recalculada várias vezes).
- **Com memoização:** no máximo `V × V` estados, cada um percorrendo os vizinhos uma vez: **O(V · E)** de tempo e **O(V²)** de memória.

### 5.2 Tabulação com grafos: Floyd-Warshall (`rotas.py`, classe `TabelaFloydWarshall`)

Preenche uma tabela `dist[i][j]` com o menor custo entre **todos os pares** de locais, permitindo, a cada rodada, usar o local `k` como intermediário:

```
dist[i][j] = min( dist[i][j], dist[i][k] + dist[k][j] )      para k = 1..V
```

Uma segunda tabela, `proximo[i][j]`, guarda o próximo passo e permite reconstruir qualquer rota.

- Complexidade: **O(V³)** de tempo e **O(V²)** de memória.
- Vantagem: depois de pronta, a tabela responde qualquer consulta "de A para B" sem recalcular nada. É usada para a matriz morador × ponto de apoio e para rotas entre dois locais quaisquer.

### 5.3 Tabulação: mochila 0/1 para o mutirão (`mutirao.py`)

Cada tarefa de prevenção (desentupir bueiros, remover entulho, sinalizar desvio…) consome **horas de equipe** e protege um número de **pessoas**. O valor de cada tarefa é `pessoas × peso do nível de risco do ponto` (BAIXO 1, MODERADO 2, ALTO 3, MUITO_ALTO 4).

```
tabela[i][h] = max( tabela[i-1][h],
                    tabela[i-1][h - horas_i] + valor_i )      se horas_i <= h
```

A tabela é percorrida de trás para frente para descobrir quais tarefas foram escolhidas.

- Complexidade: **O(n · H)** contra **O(2ⁿ)** da força bruta (n = tarefas, H = horas disponíveis).

### 5.4 Validação

O algoritmo de **Dijkstra** é usado nos testes como referência independente: a memoização e o Floyd-Warshall precisam dar exatamente o mesmo custo que ele em todos os cenários de chuva e para os dois perfis. A mochila é comparada com a força bruta para orçamentos de 0 a 69 horas.

## 6. Funcionalidades (menu)

| Opção | Funcionalidade | Técnica |
|---|---|---|
| 1 | Ver o cenário de chuva, as leituras do banco e os trechos bloqueados por perfil | Grafo |
| 2 | Rota segura de um morador até o ponto de apoio mais próximo, com distância, tempo e o desvio em relação ao dia seco | Memoização + grafo |
| 3 | Tempo de cada morador até cada ponto de apoio e a melhor opção de cada um | Tabulação (Floyd-Warshall) |
| 4 | Rota entre dois locais quaisquer | Tabulação (Floyd-Warshall) |
| 5 | Plano de mutirão com as horas de equipe informadas | Tabulação (mochila 0/1) |
| 6 | Comparação de eficiência com e sem programação dinâmica | Todas |
| 7 | Alterar a chuva (mm/h) e recalcular tudo | — |

Todas as entradas são validadas; valores inválidos pedem uma nova digitação.

## 7. Resultados com a chuva de 62,4 mm/h (MUITO_ALTO)

É a leitura registrada no Jardim Pantanal em 10/11/2026 às 17h.

| Morador | Perfil | Destino | Distância | Tempo | Desvio em relação ao dia seco |
|---|---|---|---|---|---|
| Maria Aparecida | prioritário | Abrigo Comunitário Pantanal | 380 m | 10 min | +150 m (evita a rua do córrego) |
| José Carlos | geral | Escola Municipal do Bairro | 300 m | 4 min | +160 m (evita a travessa da escola) |
| Ana Beatriz | geral | UBS Jardim Romano | 360 m | 4 min | +240 m (evita o ponto de ônibus) |
| Antônio Ferreira | prioritário | Centro Comunitário Vila Itaim | 350 m | 9 min | +190 m (evita a viela da várzea) |
| Lucas Souza | geral | Centro Comunitário Vila Itaim | 650 m | 8 min | atravessa a ponte com 10 cm de água, dentro do limite do público geral |

**Mutirão com 40 horas:** o plano escolhe 5 tarefas (39 horas), que beneficiam 1.340 pessoas. A prioridade fica com o córrego e a travessa da escola.

## 8. Eficiência (medida pelo próprio programa, opção 6)

| k (máx. de trechos) | Chamadas sem memoização | Chamadas com memoização |
|---|---|---|
| 4 | 95 | 42 |
| 6 | 1.099 | 101 |
| 8 | 13.225 | 183 |
| 10 | 161.069 | 269 |

- Sem memoização, as chamadas crescem cerca de **12 vezes a cada 2 trechos** a mais (crescimento exponencial). Com memoização, crescem de forma aproximadamente linear.
- O Floyd-Warshall monta, em uma única passada, a tabela usada para todos os moradores. Por isso é a melhor escolha quando há muitas consultas.
- Mochila: a tabela de 8 tarefas × 40 horas tem 369 células. A força bruta precisa testar 2⁸ = 256 combinações, número que dobra a cada nova tarefa: com 30 tarefas seriam mais de 1 bilhão, enquanto a tabela teria só 1.271 células.

## 9. Limitações

- O grafo é uma simplificação das ruas do piloto, com distâncias aproximadas.
- A lâmina d'água é estimada de forma proporcional à chuva. Na prática, ela depende também de drenagem, lixo e duração da chuva.
- A chuva é considerada igual em toda a região do grafo.
