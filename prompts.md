# Uso de IA no projeto Rota Seca

**Ferramenta:** Claude Code (app desktop), modelo Claude Opus 5.5
**Data:** 19/11/2026
**Integrantes:** Felipe Bernardes de Almeida (RM564360) e Guilherme Romero Nogueira de Lima (RM564431)

A IA foi usada no fim do projeto, para **revisar** as entregas de todas as disciplinas antes do envio. O código, os scripts, os documentos e os vídeos já estavam prontos; a IA leu os arquivos, executou o que era possível e apontou problemas. As correções foram decididas e feitas pela equipe.

---

## Prompt 1: revisão geral das entregas

> Revisa para mim tudo que a gente fez, cada parte que a gente fez, e veja se o trabalho está correto com tudo que a gente precisa entregar.

**O que a IA fez:** dividiu a revisão em quatro frentes e analisou cada pasta do repositório:

| Disciplina | O que foi verificado |
|---|---|
| DDD Java (`ddd-java/`) | Camadas model/BO/DAO/controller, CRUD, tratamento de erros, credenciais no repositório, consistência entre `schema.sql` e DAOs, README e documentação, deploy no Render |
| Database Design | DDL/DML/DQL, ordem de execução, constraints, resultados das consultas, comparação com o schema da API, conteúdo do PDF |
| Data Science | Números do texto conferidos contra as saídas do notebook e contra o CSV, metodologia, citação da fonte |
| Dynamic Programming | Execução dos 17 testes e do `main.py --demo`, conferência dos números do README, correção da memoização, do Floyd-Warshall e da mochila 0/1 |
| Network | Contas de VLSM, máscaras, wildcards da ACL, DHCP, testes de conectividade |
| AR/VR e Agile | Links dos vídeos, conteúdo dos PDFs, somas de Story Points, coerência com o pitch |

**Principais apontamentos:**

- **Database Design:** os comentários tinham sido removidos dos scripts `.sql`, mas o PDF ainda dizia que havia DROP comentado no DDL e consultas comentadas; havia também uma pasta `.git` dentro da pasta de entrega.
- **Agile:** soma errada de Story Points na pág. 12 (Should e Could somam 21 SP cada, não 26 e 29).
- **Coerência entre documentos:** o ponto de apoio e o slogan mudam entre o Agile/pitch e o AR/VR.
- **Network:** texto do PDF sem acentuação e tabela de endereçamento quebrando as máscaras.
- **DDD Java:** alertas de exemplo já vencidos (a consulta de alertas ativos volta vazia na demo) e duas explicações erradas no README.
- **Data Science:** sugestão de incluir teste de hipótese formal e uma tabela de estatística descritiva.
- **Dynamic Programming:** todos os testes passaram e os números do README conferem com a saída do programa.

---

## Prompt 2: decisão sobre os comentários dos scripts SQL

> Foi de propósito.

(Resposta à pergunta da IA sobre restaurar os comentários removidos dos scripts de Database Design.)

**O que a IA fez:** localizou no PDF os trechos que citavam os comentários e indicou o texto a ajustar na seção 4 ("Scripts SQL entregues"):

- remover "(há comandos DROP comentados no início do DDL para recriar)";
- trocar "As três consultas pedidas, comentadas." por "As três consultas pedidas.".

Também observou que os `COMMENT ON` (comentários de tabela e coluna no banco) continuam no DDL, então essa parte do PDF segue correta.

---

## Prompt 3: este arquivo

> Agora você gera um prompts.md, por favor.

**O que a IA fez:** gerou este registro com as interações da sessão de revisão.
