"""Testes do app Idiomas sem abrir janela: trilha, estações, língua, áreas e sugestão.

Rodar da raiz:  python -m unittest discover tests
"""

import asyncio
import importlib
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace

import flet as ft

RAIZ = Path(__file__).resolve().parent.parent
SRC = RAIZ / "apps" / "app_idiomas" / "src"
sys.path.insert(0, str(RAIZ / "nucleo" / "src"))

from nucleo import criar_main  # noqa: E402


class PaginaFalsa(SimpleNamespace):
    def __init__(self):
        super().__init__(controls=[], appbar=None, navigation_bar=None, drawer=None,
                         floating_action_button=None, dialogos=[])

    def add(self, *controles):
        self.controls.extend(controles)

    def update(self):
        pass

    def show_dialog(self, dialogo):
        self.dialogos.append(dialogo)

    def pop_dialog(self):
        return self.dialogos.pop()

    async def show_drawer(self):
        pass

    async def close_drawer(self):
        pass


def carregar():
    for m in ("config_app", "telas", "conteudo"):
        sys.modules.pop(m, None)
    sys.path.insert(0, str(SRC))
    try:
        return importlib.import_module("config_app").CONFIG, importlib.import_module("telas"), \
            importlib.import_module("conteudo")
    finally:
        sys.path.remove(str(SRC))


def achar_todos(ctrl, criterio):
    achados = [ctrl] if criterio(ctrl) else []
    filhos = list(getattr(ctrl, "controls", None) or [])
    for attr in ("content", "leading", "label"):
        filho = getattr(ctrl, attr, None)
        if filho is not None and not isinstance(filho, str):
            filhos.append(filho)
    for f in filhos:
        achados += achar_todos(f, criterio)
    return achados


def textos(ctrl):
    return [t.value for t in achar_todos(ctrl, lambda c: isinstance(c, ft.Text) and c.value)]


class TestAppIdiomas(unittest.TestCase):
    def setUp(self):
        self.config, self.telas, self.conteudo = carregar()
        self.page, capturado = PaginaFalsa(), {}

        def login(ctx):  # captura o contexto para logar sem clicar
            capturado["ctx"] = ctx
            return ft.Text("login")

        criar_main(self.config, self.telas.montar_app, montar_login=login)(self.page)
        self.ctx = capturado["ctx"]
        self.ctx.auth.cadastrar_email("ana@exemplo.com", "123456")

    def tela(self):
        return self.page.controls[0]

    def estacoes(self):
        return achar_todos(self.tela(), lambda c: isinstance(c, ft.Container) and c.width == 76)

    def responder_estacao(self, certas=True):
        while True:
            enunciados = [p for e in self.conteudo.ESPANHOL.area("basico").estacoes for p in e.perguntas]
            botoes = achar_todos(self.tela(), lambda c: isinstance(c, ft.Button) and not c.disabled
                                 and c.content not in ("Próxima", "Ver resultado", "Voltar à trilha"))
            if not botoes:
                return
            visiveis = set(textos(self.tela()))
            pergunta = next(p for p in enunciados if p.enunciado in visiveis)
            escolha = pergunta.correta if certas else (pergunta.correta + 1) % len(pergunta.opcoes)
            botoes[escolha].on_click(None)
            seguinte = achar_todos(self.tela(), lambda c: isinstance(c, ft.Button) and c.visible
                                   and c.content in ("Próxima", "Ver resultado"))
            seguinte[0].on_click(None)

    def test_layout_apos_login(self):
        self.assertIsNotNone(self.page.appbar)
        self.assertIsNotNone(self.page.drawer)                        # menu de configurações/conta
        self.assertEqual(len(self.page.appbar.actions), 1)            # menu de línguas
        self.assertIsNotNone(self.page.floating_action_button)        # sugestão
        nomes = [ch.label.value for ch in achar_todos(self.tela(), lambda c: isinstance(c, ft.Chip))]
        self.assertEqual(nomes, ["Básico", "Comida", "Gramática"])
        self.assertIn("Espanhol · Básico", textos(self.tela()))

    def test_estacoes_liberam_em_sequencia(self):
        primeira, segunda = self.estacoes()
        self.assertIsNotNone(primeira.on_click)
        self.assertIsNone(segunda.on_click)                           # bloqueada

        primeira.on_click(None)
        self.assertFalse(self.page.floating_action_button.visible)    # sem sugestão durante as perguntas
        self.responder_estacao(certas=True)
        self.assertIn("3 de 3 acertos", textos(self.tela()))
        progresso = self.ctx.dados.listar("progresso", {"dono": self.ctx.usuario.id})
        self.assertEqual([(p["estacao"], p["acertos"]) for p in progresso], [(0, 3)])

        voltar = achar_todos(self.tela(), lambda c: getattr(c, "content", None) == "Voltar à trilha")[0]
        voltar.on_click(None)
        self.assertIsNotNone(self.estacoes()[1].on_click)             # segunda liberada
        self.assertIn("1 de 2 estações concluídas", textos(self.tela()))

    def test_erro_mostra_resposta_certa(self):
        self.estacoes()[0].on_click(None)
        pergunta = self.conteudo.ESPANHOL.area("basico").estacoes[0].perguntas[0]
        botoes = achar_todos(self.tela(), lambda c: isinstance(c, ft.Button) and c.content in pergunta.opcoes)
        botoes[(pergunta.correta + 1) % 3].on_click(None)
        self.assertIn(f"Resposta certa: {pergunta.opcoes[pergunta.correta]}", textos(self.tela()))
        self.assertTrue(all(b.disabled for b in botoes))

    def test_trocar_area_e_lingua(self):
        comida = next(ch for ch in achar_todos(self.tela(), lambda c: isinstance(c, ft.Chip))
                      if ch.label.value == "Comida")
        comida.on_select(None)
        self.assertIn("Espanhol · Comida", textos(self.tela()))

        ingles = next(i for i in self.page.appbar.actions[0].items if i.content == "Inglês")
        ingles.on_click(None)
        self.assertIn("Inglês · Comida", textos(self.tela()))         # mantém a área
        self.assertTrue(next(i for i in self.page.appbar.actions[0].items if i.content == "Inglês").checked)
        prefs = self.ctx.dados.listar("preferencias", {"dono": self.ctx.usuario.id})
        self.assertEqual([p["lingua"] for p in prefs], ["en"])        # lembrada no próximo login

    def test_menu_configuracoes_e_conta(self):
        evento = SimpleNamespace(control=SimpleNamespace(selected_index=2))
        asyncio.run(self.page.drawer.on_change(evento))
        self.assertIn("ana@exemplo.com", textos(self.tela()))
        sair = achar_todos(self.tela(), lambda c: getattr(c, "content", None) == "Sair")[0]
        sair.on_click(None)
        self.assertIsNone(self.ctx.usuario)
        self.assertIsNone(self.page.appbar)                           # voltou ao login

    def test_sugestao(self):
        self.page.floating_action_button.on_click(None)
        dialogo = self.page.dialogos[-1]
        campo = achar_todos(dialogo.content, lambda c: isinstance(c, ft.TextField))[0]
        enviar = dialogo.actions[1]

        enviar.on_click(None)                                          # vazio: não envia
        self.assertEqual(self.ctx.dados.listar("feedback"), [])
        self.assertIs(self.page.dialogos[-1], dialogo)

        campo.value = "Mais áreas, por favor"
        enviar.on_click(None)
        feedback = self.ctx.dados.listar("feedback")
        self.assertEqual([(f["texto"], f["lingua"], f["area"]) for f in feedback],
                         [("Mais áreas, por favor", "es", "basico")])
        self.assertIsInstance(self.page.dialogos[-1], ft.SnackBar)


class TestComponentes(unittest.TestCase):
    def test_icone_por_nome(self):
        from nucleo import componentes as c
        self.assertEqual(c.icone("translate"), ft.Icons.TRANSLATE)    # Flet 1.0 não aceita o nome direto
        self.assertEqual(c.icone(ft.Icons.APPS), ft.Icons.APPS)
        logo = c.logo(self.carregar_config().logo, self.carregar_config().tema)
        self.assertEqual(logo.content.content.icon, ft.Icons.TRANSLATE)

    @staticmethod
    def carregar_config():
        return carregar()[0]


class TestConteudo(unittest.TestCase):
    def test_respostas_validas(self):
        _, _, conteudo = carregar()
        for lingua in conteudo.LINGUAS:
            for area in lingua.areas:
                self.assertTrue(area.estacoes, f"{lingua.nome}/{area.nome} sem estações")
                for estacao in area.estacoes:
                    for p in estacao.perguntas:
                        self.assertEqual(len(set(p.opcoes)), len(p.opcoes), p.enunciado)
                        self.assertLess(p.correta, len(p.opcoes))


if __name__ == "__main__":
    unittest.main()
