"""Course content: course (language being learned) → areas → stations → questions.

It lives in code while there is no database; later it can come from `ctx.data` without
changing the screens, as long as it keeps these same types.

Texts shown in the learner's language are `Localized` ({"en": ..., "pt": ...}); texts in the
language being learned are plain strings. Missing languages fall back to English.
"""

from __future__ import annotations

from dataclasses import dataclass

from core.i18n import Localized


@dataclass(frozen=True)
class Question:
    prompt: Localized
    options: tuple[Localized, ...]
    answer: int  # index in `options`


@dataclass(frozen=True)
class Station:
    title: Localized
    questions: tuple[Question, ...]


@dataclass(frozen=True)
class Area:
    id: str
    name_key: str  # i18n key in strings.py
    icon: str
    stations: tuple[Station, ...]


@dataclass(frozen=True)
class Course:
    id: str
    name_key: str
    areas: tuple[Area, ...]

    def area(self, id_: str) -> Area:
        return next((a for a in self.areas if a.id == id_), self.areas[0])


def _q(prompt: Localized, correct: Localized, *wrong: Localized) -> Question:
    """Shortcut: the right answer comes first and is moved to a fixed spot based on the prompt."""
    options = [correct, *wrong]
    key = prompt if isinstance(prompt, str) else prompt["en"]
    position = len(key) % len(options)
    options.insert(position, options.pop(0))
    return Question(prompt, tuple(options), position)


def _t(en: str, pt: str) -> dict[str, str]:
    return {"en": en, "pt": pt}


SPANISH = Course("es", "course.es", (
    Area("basics", "area.basics", "waving_hand", (
        Station(_t("Greetings", "Saudações"), (
            _q(_t('How do you say "good morning"?', 'Como se diz "bom dia"?'),
               "Buenos días", "Buenas noches", "Hasta luego"),
            _q(_t('"¿Cómo estás?" means…', '"¿Cómo estás?" significa…'),
               _t("How are you?", "Como você está?"), _t("Where are you?", "Onde você está?"),
               _t("Who are you?", "Quem é você?")),
            _q(_t('Polite reply to "gracias":', 'Resposta educada para "gracias":'),
               "De nada", "Lo siento", "Perdón"),
        )),
        Station(_t("Introductions", "Apresentação"), (
            _q(_t('"Me llamo Ana" means…', '"Me llamo Ana" significa…'),
               _t("My name is Ana", "Meu nome é Ana"), _t("I call Ana", "Eu chamo a Ana"),
               _t("I like Ana", "Eu gosto da Ana")),
            _q(_t("How do you ask someone's age?", "Como perguntar a idade?"),
               "¿Cuántos años tienes?", "¿Cómo te llamas?", "¿De dónde eres?"),
            _q(_t('"Soy de Brasil" means…', '"Soy de Brasil" significa…'),
               _t("I am from Brazil", "Sou do Brasil"), _t("I am in Brazil", "Estou no Brasil"),
               _t("I am going to Brazil", "Vou ao Brasil")),
        )),
    )),
    Area("food", "area.food", "restaurant", (
        Station(_t("At the market", "No mercado"), (
            _q(_t('"Manzana" is…', '"Manzana" é…'),
               _t("Apple", "Maçã"), _t("Butter", "Manteiga"), _t("Orange", "Laranja")),
            _q(_t('How do you say "bread"?', 'Como se diz "pão"?'), "Pan", "Pon", "Pane"),
            _q(_t('"Leche" is…', '"Leche" é…'),
               _t("Milk", "Leite"), _t("Lettuce", "Alface"), _t("Sausage", "Linguiça")),
        )),
        Station(_t("At the restaurant", "No restaurante"), (
            _q(_t("To ask for the bill:", "Para pedir a conta:"),
               "La cuenta, por favor", "El menú, por favor", "Una mesa, por favor"),
            _q(_t('"Tengo hambre" means…', '"Tengo hambre" significa…'),
               _t("I'm hungry", "Estou com fome"), _t("I'm thirsty", "Estou com sede"),
               _t("I'm in a hurry", "Estou com pressa")),
            _q(_t('"Cubiertos" are…', '"Cubiertos" são…'),
               _t("Cutlery", "Talheres"), _t("Glasses", "Copos"), _t("Napkins", "Guardanapos")),
        )),
    )),
    Area("grammar", "area.grammar", "menu_book", (
        Station(_t("Word order (SVO)", "Ordem SVO"), (
            _q(_t("Which sentence is subject-verb-object?", "Qual frase está na ordem sujeito-verbo-objeto?"),
               "Yo como pan", "Pan como yo", "Como pan yo"),
            _q(_t('In "Ella lee un libro", the verb is…', 'Em "Ella lee un libro", o verbo é…'),
               "lee", "Ella", "libro"),
            _q(_t('In "Nosotros vemos la película", the object is…',
                  'Em "Nosotros vemos la película", o objeto é…'),
               "la película", "Nosotros", "vemos"),
        )),
        Station(_t("Ser and estar", "Ser e estar"), (
            _q('"Yo ___ brasileño."', "soy", "estoy", "es"),
            _q('"Ella ___ cansada hoy."', "está", "es", "soy"),
            _q(_t("For a location we use…", "Para lugar usamos…"), "estar", "ser", "tener"),
        )),
    )),
))

ENGLISH = Course("en", "course.en", (
    Area("basics", "area.basics", "waving_hand", (
        Station(_t("Greetings", "Cumprimentos"), (
            _q(_t("Say goodbye at night:", 'Como se diz "boa noite" ao se despedir?'),
               "Good night", "Good morning", "Good afternoon"),
            _q(_t("Which one asks how someone is?", 'Como se pergunta "como você está?"'),
               "How are you?", "Who are you?", "How old are you?"),
            _q(_t('Reply to "Thank you":', 'Resposta para "Thank you":'),
               "You're welcome", "Excuse me", "I'm sorry"),
        )),
    )),
    Area("food", "area.food", "restaurant", (
        Station(_t("Groceries", "Mercado"), (
            _q(_t("Which one is a fruit?", 'Como se diz "maçã"?'), "Apple", "Chicken", "Bread"),
            _q(_t("Which one is made from milk?", 'Como se diz "queijo"?'), "Cheese", "Chips", "Chicken"),
            _q(_t("What do you drink when you are thirsty?", 'Como se diz "água"?'), "Water", "Bread", "Rice"),
        )),
    )),
    Area("grammar", "area.grammar", "menu_book", (
        Station(_t("Word order", "Ordem das palavras"), (
            _q(_t("Which sentence is subject-verb-object?", "Qual frase está na ordem sujeito-verbo-objeto?"),
               "She reads books", "Books reads she", "Reads she books"),
            _q(_t('In "They play football", the subject is…', 'Em "They play football", o sujeito é…'),
               "They", "play", "football"),
            _q('"I ___ a student."', "am", "is", "are"),
        )),
    )),
))

COURSES: tuple[Course, ...] = (SPANISH, ENGLISH)


def course(id_: str) -> Course:
    return next((c for c in COURSES if c.id == id_), COURSES[0])
