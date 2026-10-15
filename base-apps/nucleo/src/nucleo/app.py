"""Ponto de entrada comum. Decide entre login e app a partir do estado de auth."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

import flet as ft

from .auth import ServicoAuth, Usuario, criar_auth
from .config import AppConfig
from .dados import Repositorio, criar_repositorio
from .ui import tela_login_padrao


@dataclass
class Contexto:
    """Tudo que uma tela precisa: página, config, auth e dados."""

    page: Any
    config: AppConfig
    auth: ServicoAuth
    dados: Repositorio

    @property
    def usuario(self) -> Usuario | None:
        return self.auth.usuario_atual

    def sair(self, _=None) -> None:
        self.auth.sair()


MontarApp = Callable[[Contexto], None]
MontarLogin = Callable[[Contexto], ft.Control]


def _aplicar_tema(page: Any, config: AppConfig) -> None:
    tema = config.tema
    page.title = config.nome
    page.bgcolor = tema.cor_fundo
    page.theme_mode = ft.ThemeMode.DARK if tema.escuro else ft.ThemeMode.LIGHT
    page.theme = ft.Theme(color_scheme_seed=tema.cor_primaria)
    page.dark_theme = ft.Theme(color_scheme_seed=tema.cor_primaria)
    page.padding = 24


def _limpar(page: Any) -> None:
    page.controls.clear()
    page.appbar = None
    page.navigation_bar = None
    page.drawer = None
    page.floating_action_button = None


def criar_main(config: AppConfig, montar_app: MontarApp,
               montar_login: MontarLogin = tela_login_padrao) -> Callable[[Any], None]:
    """Retorna o `main(page)` do Flet. Separado de `iniciar_app` para facilitar testes."""

    def main(page: Any) -> None:
        _aplicar_tema(page, config)
        ctx = Contexto(page=page, config=config, auth=criar_auth(config), dados=criar_repositorio(config))

        def renderizar(usuario: Usuario | None) -> None:
            _limpar(page)
            if usuario is None:
                page.add(montar_login(ctx))
            else:
                montar_app(ctx)
            page.update()

        ctx.auth.ao_mudar(renderizar)
        renderizar(ctx.usuario)

    return main


def iniciar_app(config: AppConfig, montar_app: MontarApp,
                montar_login: MontarLogin = tela_login_padrao) -> None:
    ft.run(criar_main(config, montar_app, montar_login))
