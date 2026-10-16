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
from nucleo.ui.login import AVISO_REDEFINICAO  # noqa: E402


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

    def test_redefinicao_senha(self):
        auth = AuthMemoria()
        auth.cadastrar_email("ana@exemplo.com", "123456")
        auth.sair()
        auth.enviar_redefinicao_senha(" Ana@Exemplo.com ")
        auth.enviar_redefinicao_senha("ninguem@exemplo.com")   # sem conta: não falha nem envia
        self.assertEqual(auth.redefinicoes_enviadas, ["ana@exemplo.com"])
        self.assertIsNone(auth.usuario_atual)                  # pedir redefinição não autentica
        with self.assertRaises(ErroAuth):
            auth.enviar_redefinicao_senha("invalido")

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
        self._esqueci_senha(page)
        self.assertIsNone(page.navigation_bar)           # continua no login
        self._entrar_google(page)
        self.assertIsNotNone(page.navigation_bar)        # layout de abas

    def test_beta(self):
        config, telas = carregar_app("app_beta")
        page = PaginaFalsa()
        criar_main(config, telas.montar_app, montar_login=telas.tela_login)(page)
        self.assertIsNone(page.drawer)
        self._esqueci_senha(page)
        self._entrar_google(page)
        self.assertIsNotNone(page.drawer)                # layout com menu lateral
        page.floating_action_button.on_click(None)       # cria registro
        self.assertEqual(len(page.controls), 1)

    @classmethod
    def _entrar_google(cls, page):
        cls._clicar(page, "Continuar com Google")

    @classmethod
    def _esqueci_senha(cls, page):
        cls._achar(page.controls[0], lambda c: getattr(c, "label", None) == "Email").value = "ana@exemplo.com"
        cls._clicar(page, "Esqueci a senha")
        aviso = cls._achar(page.controls[0], lambda c: getattr(c, "value", None) == AVISO_REDEFINICAO)
        assert aviso is not None and aviso.visible, "aviso de redefinição não apareceu"

    @classmethod
    def _clicar(cls, page, rotulo):
        botao = cls._achar(page.controls[0], lambda c: getattr(c, "content", None) == rotulo)
        assert botao is not None, f"botão {rotulo!r} não encontrado"
        botao.on_click(None)

    @classmethod
    def _achar(cls, ctrl, criterio):
        if criterio(ctrl):
            return ctrl
        filhos = list(getattr(ctrl, "controls", None) or [])
        if getattr(ctrl, "content", None) is not None and not isinstance(ctrl.content, str):
            filhos.append(ctrl.content)
        for f in filhos:
            achado = cls._achar(f, criterio)
            if achado:
                return achado
        return None


if __name__ == "__main__":
    unittest.main()
