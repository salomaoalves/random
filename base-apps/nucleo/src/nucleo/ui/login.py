"""Tela de login padrão. Um filho pode usá-la ou montar a sua com os blocos."""

from __future__ import annotations

from typing import TYPE_CHECKING

import flet as ft

from ..auth import ErroAuth
from . import componentes as c

if TYPE_CHECKING:
    from ..app import Contexto

AVISO_REDEFINICAO = "Se existir uma conta com esse email, enviamos um link para redefinir a senha."


class FormularioLogin:
    """Campos + ações de login, reaproveitáveis em qualquer layout."""

    def __init__(self, ctx: "Contexto") -> None:
        self.ctx = ctx
        tema = ctx.config.tema
        self.email = c.campo("Email", tema, email=True)
        self.senha = c.campo("Senha", tema, senha=True)
        self.erro = c.mensagem_erro()
        self.aviso = c.mensagem_aviso(tema)
        self.botao_entrar = c.botao_primario("Entrar", self.entrar, tema)
        self.botao_cadastrar = ft.TextButton(content="Criar conta", on_click=self.cadastrar)
        self.botao_google = c.botao_google(self.entrar_google)
        self.botao_esqueci = ft.TextButton(content="Esqueci a senha", on_click=self.esqueci_senha)

    def _executar(self, acao, sucesso: str = "") -> None:
        self.erro.visible = self.aviso.visible = False
        botoes = (self.botao_entrar, self.botao_cadastrar, self.botao_google, self.botao_esqueci)
        for b in botoes:
            b.disabled = True
        self.ctx.page.update()
        try:
            acao()
            if sucesso:
                self.aviso.value, self.aviso.visible = sucesso, True
        except ErroAuth as e:
            self.erro.value, self.erro.visible = str(e), True
        except Exception:
            self.erro.value, self.erro.visible = "Não foi possível concluir. Tente de novo.", True
        finally:
            for b in botoes:
                b.disabled = False
            self.ctx.page.update()

    def entrar(self, _=None) -> None:
        self._executar(lambda: self.ctx.auth.entrar_email(self.email.value, self.senha.value))

    def cadastrar(self, _=None) -> None:
        self._executar(lambda: self.ctx.auth.cadastrar_email(self.email.value, self.senha.value))

    def entrar_google(self, _=None) -> None:
        self._executar(lambda: self.ctx.auth.entrar_google(self.ctx.page))

    def esqueci_senha(self, _=None) -> None:
        self._executar(lambda: self.ctx.auth.enviar_redefinicao_senha(self.email.value), AVISO_REDEFINICAO)


def tela_login_padrao(ctx: "Contexto") -> ft.Control:
    cfg, tema = ctx.config, ctx.config.tema
    form = FormularioLogin(ctx)
    return ft.SafeArea(
        expand=True,
        content=ft.Column(
            [
                c.logo(cfg.logo, tema),
                c.titulo(cfg.nome, tema),
                form.email,
                form.senha,
                form.erro,
                form.aviso,
                form.botao_entrar,
                form.botao_google,
                ft.Row([form.botao_cadastrar, form.botao_esqueci], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                c.rodape(cfg.rodape, tema),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
            spacing=12,
            scroll=ft.ScrollMode.AUTO,
            expand=True,
        ),
    )
