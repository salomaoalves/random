"""Default login screen. A child app can use it or build its own from the blocks."""

from __future__ import annotations

from typing import TYPE_CHECKING

import flet as ft

from ..auth import AuthError
from . import components as c

if TYPE_CHECKING:
    from ..app import Context


class LoginForm:
    """Login fields + actions, reusable in any layout."""

    def __init__(self, ctx: "Context") -> None:
        self.ctx = ctx
        theme, t = ctx.config.theme, ctx.t
        self.email = c.field(t("login.email"), theme, email=True)
        self.password = c.field(t("login.password"), theme, password=True)
        self.error = c.error_message()
        self.info = c.info_message(theme)
        self.sign_in_button = c.primary_button(t("login.sign_in"), self.sign_in, theme)
        self.sign_up_button = ft.TextButton(content=t("login.sign_up"), on_click=self.sign_up)
        self.google_button = c.google_button(t("login.google"), self.sign_in_google)
        self.forgot_password_button = ft.TextButton(content=t("login.forgot_password"), on_click=self.forgot_password)

    def _run(self, action, success_key: str = "") -> None:
        self.error.visible = self.info.visible = False
        buttons = (self.sign_in_button, self.sign_up_button, self.google_button, self.forgot_password_button)
        for b in buttons:
            b.disabled = True
        self.ctx.page.update()
        try:
            action()
            if success_key:
                self.info.value, self.info.visible = self.ctx.t(success_key), True
        except AuthError as e:
            self.error.value, self.error.visible = self.ctx.t(e.key), True
        except Exception:
            self.error.value, self.error.visible = self.ctx.t("error.generic"), True
        finally:
            for b in buttons:
                b.disabled = False
            self.ctx.page.update()

    def sign_in(self, _=None) -> None:
        self._run(lambda: self.ctx.auth.sign_in_email(self.email.value, self.password.value))

    def sign_up(self, _=None) -> None:
        self._run(lambda: self.ctx.auth.sign_up_email(self.email.value, self.password.value))

    def sign_in_google(self, _=None) -> None:
        self._run(lambda: self.ctx.auth.sign_in_google(self.ctx.page))

    def forgot_password(self, _=None) -> None:
        self._run(lambda: self.ctx.auth.send_password_reset(self.email.value), success_key="login.reset_sent")


def default_login_screen(ctx: "Context") -> ft.Control:
    cfg, theme = ctx.config, ctx.config.theme
    form = LoginForm(ctx)
    return ft.SafeArea(
        expand=True,
        content=ft.Column(
            [
                c.logo(cfg.logo, theme),
                c.title(cfg.name, theme),
                form.email,
                form.password,
                form.error,
                form.info,
                form.sign_in_button,
                form.google_button,
                ft.Row([form.sign_up_button, form.forgot_password_button], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                c.footer(cfg.footer, theme, ctx.t),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
            spacing=12,
            scroll=ft.ScrollMode.AUTO,
            expand=True,
        ),
    )
