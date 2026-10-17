"""Common entry point. Picks the UI language and switches between login and app from the auth state."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Iterable

import flet as ft

from .auth import AuthService, User, create_auth
from .config import AppConfig
from .data import Repository, create_repository
from .i18n import CORE_STRINGS, Translator, merge
from .ui import default_login_screen


@dataclass
class Context:
    """Everything a screen needs: page, config, auth, data and translations."""

    page: Any
    config: AppConfig
    auth: AuthService
    data: Repository
    i18n: Translator

    @property
    def user(self) -> User | None:
        return self.auth.current_user

    def t(self, key: str, **values: object) -> str:
        return self.i18n.t(key, **values)

    def sign_out(self, _=None) -> None:
        self.auth.sign_out()


BuildApp = Callable[[Context], None]
BuildLogin = Callable[[Context], ft.Control]


def _apply_theme(page: Any, config: AppConfig) -> None:
    theme = config.theme
    page.title = config.name
    page.bgcolor = theme.background_color
    page.theme_mode = ft.ThemeMode.DARK if theme.dark else ft.ThemeMode.LIGHT
    page.theme = ft.Theme(color_scheme_seed=theme.primary_color)
    page.dark_theme = ft.Theme(color_scheme_seed=theme.primary_color)
    page.padding = 24


def _apply_locale(page: Any, i18n: Translator) -> None:
    """Also localizes Flutter's built-in widgets (text selection menu, date picker…)."""
    page.locale_configuration = ft.LocaleConfiguration(
        supported_locales=[ft.Locale(language_code=lang) for lang in i18n.languages],
        current_locale=ft.Locale(language_code=i18n.language),
    )


def _languages(locales: Iterable[Any] | None) -> list[str]:
    return [loc.language_code for loc in locales or []]


async def _device_languages(page: Any) -> list[str]:
    try:
        info = await page.get_device_info()
    except Exception:  # not available on every host; fall back to the default language
        return []
    return _languages(info.locales if info else None)


def _clear(page: Any) -> None:
    page.controls.clear()
    page.appbar = None
    page.navigation_bar = None
    page.drawer = None
    page.floating_action_button = None


def create_main(config: AppConfig, build_app: BuildApp,
                build_login: BuildLogin = default_login_screen) -> Callable[[Any], Any]:
    """Returns Flet's `main(page)`. Kept apart from `run_app` to make testing easier."""

    async def main(page: Any) -> None:
        _apply_theme(page, config)
        i18n = Translator(merge(CORE_STRINGS, config.strings))
        i18n.pick(await _device_languages(page))
        _apply_locale(page, i18n)
        ctx = Context(page=page, config=config, auth=create_auth(config), data=create_repository(config), i18n=i18n)

        def render(user: User | None) -> None:
            _clear(page)
            if user is None:
                page.add(build_login(ctx))
            else:
                build_app(ctx)
            page.update()

        def on_locale_change(e: Any) -> None:
            if i18n.pick(_languages(e.locales)):
                _apply_locale(page, i18n)
                render(ctx.user)

        page.on_locale_change = on_locale_change
        ctx.auth.on_change(render)
        render(ctx.user)

    return main


def run_app(config: AppConfig, build_app: BuildApp,
            build_login: BuildLogin = default_login_screen) -> None:
    ft.run(create_main(config, build_app, build_login))
