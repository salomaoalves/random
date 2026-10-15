"""Testes sem abrir janela: dados, auth e montagem das telas com uma página falsa.

Rodar da raiz:  python -m unittest discover tests
"""

import importlib
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "nucleo" / "src"))

from nucleo import ErroAuth, criar_main  # noqa: E402
from nucleo.auth import AuthMemoria  # noqa: E402
from nucleo.dados import RepositorioMemoria  # noqa: E402


class PaginaFalsa(SimpleNamespace):
    def __init__(self):
        super().__init__(controls=[], appbar=None, navigation_bar=None, drawer=None,
                         floating_action_button=None, atualizacoes=0)

    def add(self, *controles):
        self.controls.extend(controles)

    def update(self):
        self.atualizacoes += 1


def carregar_app(pasta):
    src = str(RAIZ / "apps" / pasta / "src")
    for m in ("config_app", "telas"):
        sys.modules.pop(m, None)
    sys.path.insert(0, src)
    try:
        return importlib.import_module("config_app").CONFIG, importlib.import_module("telas")
    finally:
        sys.path.remove(src)


class TestDados(unittest.TestCase):
    def test_crud(self):
        repo = RepositorioMemoria()
        item = repo.criar("itens", {"titulo": "a", "dono": "u1"})
        repo.criar("itens", {"titulo": "b", "dono": "u2"})
        self.assertEqual([i["titulo"] for i in repo.listar("itens", {"dono": "u1"})], ["a"])
        self.assertEqual(repo.atualizar("itens", item["id"], {"titulo": "a2"})["titulo"], "a2")
        repo.remover("itens", item["id"])
        self.assertIsNone(repo.obter("itens", item["id"]))


class TestAuth(unittest.TestCase):
    def test_fluxo(self):
        auth, eventos = AuthMemoria(), []
        auth.ao_mudar(eventos.append)
        auth.cadastrar_email("Ana@Exemplo.com", "123456")
        auth.sair()
        with self.assertRaises(ErroAuth):
            auth.entrar_email("ana@exemplo.com", "errada1")
        self.assertIsNone(auth.usuario_atual)  # erro não autentica
        auth.entrar_email("ana@exemplo.com", "123456")
        self.assertEqual([e.email if e else None for e in eventos],
                         ["ana@exemplo.com", None, "ana@exemplo.com"])

    def test_validacao(self):
        with self.assertRaises(ErroAuth):
            AuthMemoria().cadastrar_email("invalido", "123456")
        with self.assertRaises(ErroAuth):
            AuthMemoria().cadastrar_email("a@b.com", "123")


class TestApps(unittest.TestCase):
    def test_alfa(self):
        config, telas = carregar_app("app_alfa")
        page = PaginaFalsa()
        main = criar_main(config, telas.montar_app)
        main(page)
        self.assertEqual(len(page.controls), 1)          # tela de login
        self.assertIsNone(page.navigation_bar)
        self._entrar_google(page)
        self.assertIsNotNone(page.navigation_bar)        # layout de abas

    def test_beta(self):
        config, telas = carregar_app("app_beta")
        page = PaginaFalsa()
        criar_main(config, telas.montar_app, montar_login=telas.tela_login)(page)
        self.assertIsNone(page.drawer)
        self._entrar_google(page)
        self.assertIsNotNone(page.drawer)                # layout com menu lateral
        page.floating_action_button.on_click(None)       # cria registro
        self.assertEqual(len(page.controls), 1)

    @staticmethod
    def _entrar_google(page):
        def achar(ctrl):
            if getattr(ctrl, "content", None) == "Continuar com Google":
                return ctrl
            filhos = list(getattr(ctrl, "controls", None) or [])
            if getattr(ctrl, "content", None) is not None and not isinstance(ctrl.content, str):
                filhos.append(ctrl.content)
            for f in filhos:
                achado = achar(f)
                if achado:
                    return achado
            return None

        botao = achar(page.controls[0])
        assert botao is not None, "botão Google não encontrado"
        botao.on_click(None)


if __name__ == "__main__":
    unittest.main()
