from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class PontoRisco:
    id: int
    bairro: str
    local: str
    nivel: str
    lamina_max_cm: float


@dataclass(frozen=True)
class PontoApoio:
    id: int
    local: str
    nome: str
    tipo: str
    endereco: str
    capacidade: int
    ativo: bool


@dataclass(frozen=True)
class Morador:
    id: int
    nome: str
    local: str
    bairro: str
    nascimento: date
    mobilidade_reduzida: bool

    def idade(self, hoje=None):
        hoje = hoje or date.today()
        anos = hoje.year - self.nascimento.year
        if (hoje.month, hoje.day) < (self.nascimento.month, self.nascimento.day):
            anos -= 1
        return anos

    def prioritario(self, hoje=None):
        return self.mobilidade_reduzida or self.idade(hoje) >= 60


@dataclass(frozen=True)
class Tarefa:
    id: int
    descricao: str
    ponto_risco_id: int
    horas: int
    pessoas: int


LOCAIS = {
    "CASA_MARIA": "Casa da Maria Aparecida (Jardim Pantanal)",
    "CASA_JOSE": "Casa do José Carlos (Jardim Pantanal)",
    "CASA_ANA": "Casa da Ana Beatriz (Jardim Romano)",
    "CASA_ANTONIO": "Casa do Antônio Ferreira (Vila Itaim)",
    "CASA_LUCAS": "Casa do Lucas Souza (Jardim Helena)",
    "RUA_A_1": "Rua A x Rua 1",
    "RUA_A_2": "Rua A x Rua 2",
    "RUA_B_1": "Rua B x Rua 1",
    "RUA_B_2": "Rua B x Rua 2",
    "CORREGO": "Rua do córrego, trecho baixo",
    "TRAVESSA": "Travessa de acesso à escola",
    "AVENIDA_C": "Avenida principal x Rua C",
    "PONTO_ONIBUS": "Ponto de ônibus da avenida principal",
    "VIELA": "Viela junto à várzea",
    "RUA_D_5": "Rua D x Rua 5",
    "PONTE": "Cruzamento sob a ponte",
    "ABRIGO_PANTANAL": "Abrigo Comunitário Pantanal",
    "ESCOLA_BAIRRO": "Escola Municipal do Bairro",
    "UBS_ROMANO": "UBS Jardim Romano",
    "CENTRO_ITAIM": "Centro Comunitário Vila Itaim",
    "ESCOLA_HELENA": "Escola Estadual Jardim Helena",
}

PONTOS_RISCO = {
    1: PontoRisco(1, "Jardim Pantanal", "Rua próxima ao córrego, trecho baixo", "MUITO_ALTO", 80.0),
    2: PontoRisco(2, "Jardim Pantanal", "Travessa de acesso à escola", "ALTO", 45.0),
    3: PontoRisco(3, "Jardim Romano", "Avenida principal, ponto de ônibus", "ALTO", 50.0),
    4: PontoRisco(4, "Vila Itaim", "Viela junto à várzea", "MODERADO", 25.0),
    5: PontoRisco(5, "Jardim Helena", "Cruzamento sob a ponte", "BAIXO", 10.0),
}

PONTOS_APOIO = [
    PontoApoio(1, "ABRIGO_PANTANAL", "Abrigo Comunitário Pantanal", "ABRIGO", "Rua A, 100 (endereço simulado)", 120, True),
    PontoApoio(2, "ESCOLA_BAIRRO", "Escola Municipal do Bairro", "ESCOLA", "Rua B, 250 (endereço simulado)", 300, True),
    PontoApoio(3, "UBS_ROMANO", "UBS Jardim Romano", "UBS", "Rua C, 30 (endereço simulado)", 60, True),
    PontoApoio(4, "CENTRO_ITAIM", "Centro Comunitário Vila Itaim", "OUTRO", "Rua D, 75 (endereço simulado)", 80, True),
    PontoApoio(5, "ESCOLA_HELENA", "Escola Estadual Jardim Helena", "ESCOLA", "Rua E, 410 (endereço simulado)", 250, False),
]

MORADORES = [
    Morador(1, "Maria Aparecida", "CASA_MARIA", "Jardim Pantanal", date(1958, 3, 14), True),
    Morador(2, "José Carlos", "CASA_JOSE", "Jardim Pantanal", date(1985, 7, 2), False),
    Morador(3, "Ana Beatriz", "CASA_ANA", "Jardim Romano", date(1999, 11, 21), False),
    Morador(4, "Antônio Ferreira", "CASA_ANTONIO", "Vila Itaim", date(1949, 1, 30), True),
    Morador(5, "Lucas Souza", "CASA_LUCAS", "Jardim Helena", date(2004, 5, 9), False),
]

TRECHOS = [
    ("CASA_MARIA", "CORREGO", 60, 1),
    ("CASA_MARIA", "RUA_B_1", 150, None),
    ("CORREGO", "RUA_A_1", 120, 1),
    ("CORREGO", "TRAVESSA", 90, 2),
    ("TRAVESSA", "ESCOLA_BAIRRO", 80, 2),
    ("RUA_A_1", "ABRIGO_PANTANAL", 100, None),
    ("RUA_A_1", "RUA_A_2", 150, None),
    ("RUA_B_1", "RUA_A_1", 130, None),
    ("RUA_B_1", "RUA_B_2", 140, None),
    ("RUA_B_2", "ESCOLA_BAIRRO", 110, None),
    ("RUA_A_2", "RUA_B_2", 120, None),
    ("CASA_JOSE", "RUA_A_2", 70, None),
    ("CASA_JOSE", "TRAVESSA", 60, 2),
    ("RUA_A_2", "AVENIDA_C", 400, None),
    ("AVENIDA_C", "PONTO_ONIBUS", 90, 3),
    ("PONTO_ONIBUS", "UBS_ROMANO", 70, 3),
    ("AVENIDA_C", "UBS_ROMANO", 200, None),
    ("CASA_ANA", "PONTO_ONIBUS", 50, 3),
    ("CASA_ANA", "AVENIDA_C", 160, None),
    ("AVENIDA_C", "RUA_D_5", 450, None),
    ("RUA_D_5", "CENTRO_ITAIM", 90, None),
    ("RUA_D_5", "VIELA", 100, 4),
    ("CASA_ANTONIO", "VIELA", 40, 4),
    ("CASA_ANTONIO", "RUA_D_5", 260, None),
    ("VIELA", "CENTRO_ITAIM", 120, 4),
    ("RUA_D_5", "PONTE", 500, None),
    ("PONTE", "ESCOLA_HELENA", 80, 5),
    ("CASA_LUCAS", "PONTE", 60, 5),
]

TAREFAS_MUTIRAO = [
    Tarefa(1, "Desentupir os bueiros da rua do córrego", 1, 12, 450),
    Tarefa(2, "Remover entulho da margem do córrego", 1, 16, 380),
    Tarefa(3, "Limpar a boca de lobo da travessa da escola", 2, 6, 300),
    Tarefa(4, "Sinalizar o desvio na travessa da escola", 2, 3, 120),
    Tarefa(5, "Desobstruir a galeria da avenida principal", 3, 14, 420),
    Tarefa(6, "Instalar placa de rota segura no ponto de ônibus", 3, 2, 90),
    Tarefa(7, "Roçar e limpar a viela da várzea", 4, 8, 200),
    Tarefa(8, "Limpar o canal sob a ponte", 5, 5, 80),
]

LEITURAS_CHUVA = [
    ("Jardim Pantanal", "10/11/2026 17:00", 62.4),
    ("Jardim Romano", "10/11/2026 17:00", 31.8),
    ("Vila Itaim", "11/11/2026 15:00", 14.2),
    ("Jardim Helena", "12/11/2026 09:00", 2.6),
    ("Jardim Pantanal", "13/11/2026 18:00", 27.5),
]
