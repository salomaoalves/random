"""Conteúdo do app: línguas → áreas → estações → perguntas.

Fica no código enquanto não há banco; depois pode vir de `ctx.dados` sem mudar as telas,
desde que mantenha estes mesmos tipos.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Pergunta:
    enunciado: str
    opcoes: tuple[str, ...]
    correta: int  # índice em `opcoes`


@dataclass(frozen=True)
class Estacao:
    titulo: str
    perguntas: tuple[Pergunta, ...]


@dataclass(frozen=True)
class Area:
    id: str
    nome: str
    icone: str
    estacoes: tuple[Estacao, ...]


@dataclass(frozen=True)
class Lingua:
    id: str
    nome: str
    areas: tuple[Area, ...]

    def area(self, id_: str) -> Area:
        return next((a for a in self.areas if a.id == id_), self.areas[0])


def _p(enunciado: str, correta: str, *erradas: str) -> Pergunta:
    """Atalho: a resposta certa vem primeiro e é embaralhada de forma fixa pelo tamanho do enunciado."""
    opcoes = [correta, *erradas]
    pos = len(enunciado) % len(opcoes)
    opcoes.insert(pos, opcoes.pop(0))
    return Pergunta(enunciado, tuple(opcoes), pos)


ESPANHOL = Lingua("es", "Espanhol", (
    Area("basico", "Básico", "waving_hand", (
        Estacao("Saudações", (
            _p("Como se diz \"bom dia\"?", "Buenos días", "Buenas noches", "Hasta luego"),
            _p("\"¿Cómo estás?\" significa…", "Como você está?", "Onde você está?", "Quem é você?"),
            _p("Resposta educada para \"gracias\":", "De nada", "Lo siento", "Perdón"),
        )),
        Estacao("Apresentação", (
            _p("\"Me llamo Ana\" significa…", "Meu nome é Ana", "Eu chamo a Ana", "Eu gosto da Ana"),
            _p("Como perguntar a idade?", "¿Cuántos años tienes?", "¿Cómo te llamas?", "¿De dónde eres?"),
            _p("\"Soy de Brasil\" significa…", "Sou do Brasil", "Estou no Brasil", "Vou ao Brasil"),
        )),
    )),
    Area("comida", "Comida", "restaurant", (
        Estacao("No mercado", (
            _p("\"Manzana\" é…", "Maçã", "Manteiga", "Laranja"),
            _p("Como se diz \"pão\"?", "Pan", "Pon", "Pane"),
            _p("\"Leche\" é…", "Leite", "Alface", "Linguiça"),
        )),
        Estacao("No restaurante", (
            _p("Para pedir a conta:", "La cuenta, por favor", "El menú, por favor", "Una mesa, por favor"),
            _p("\"Tengo hambre\" significa…", "Estou com fome", "Estou com sede", "Estou com pressa"),
            _p("\"Cubiertos\" são…", "Talheres", "Copos", "Guardanapos"),
        )),
    )),
    Area("gramatica", "Gramática", "menu_book", (
        Estacao("Ordem SVO", (
            _p("Qual frase está na ordem sujeito-verbo-objeto?", "Yo como pan", "Pan como yo", "Como pan yo"),
            _p("Em \"Ella lee un libro\", o verbo é…", "lee", "Ella", "libro"),
            _p("Em \"Nosotros vemos la película\", o objeto é…", "la película", "Nosotros", "vemos"),
        )),
        Estacao("Ser e estar", (
            _p("\"Yo ___ brasileño.\"", "soy", "estoy", "es"),
            _p("\"Ella ___ cansada hoy.\"", "está", "es", "soy"),
            _p("Para lugar usamos…", "estar", "ser", "tener"),
        )),
    )),
))

INGLES = Lingua("en", "Inglês", (
    Area("basico", "Básico", "waving_hand", (
        Estacao("Greetings", (
            _p("Como se diz \"boa noite\" ao se despedir?", "Good night", "Good morning", "Good afternoon"),
            _p("\"How are you?\" significa…", "Como você está?", "Quem é você?", "Quantos anos você tem?"),
            _p("Resposta para \"Thank you\":", "You're welcome", "Excuse me", "I'm sorry"),
        )),
    )),
    Area("comida", "Comida", "restaurant", (
        Estacao("Groceries", (
            _p("\"Apple\" é…", "Maçã", "Abacaxi", "Uva"),
            _p("Como se diz \"queijo\"?", "Cheese", "Chips", "Chicken"),
            _p("\"Water\" é…", "Água", "Vinho", "Suco"),
        )),
    )),
    Area("gramatica", "Gramática", "menu_book", (
        Estacao("Word order", (
            _p("Qual frase está na ordem sujeito-verbo-objeto?", "She reads books", "Books reads she", "Reads she books"),
            _p("Em \"They play football\", o sujeito é…", "They", "play", "football"),
            _p("\"I ___ a student.\"", "am", "is", "are"),
        )),
    )),
))

LINGUAS: tuple[Lingua, ...] = (ESPANHOL, INGLES)


def lingua(id_: str) -> Lingua:
    return next((x for x in LINGUAS if x.id == id_), LINGUAS[0])
