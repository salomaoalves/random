"""UI blocks. The child apps build their own layout by combining these pieces.

Blocks receive texts already translated; screens translate with `ctx.t(...)`.
"""

from __future__ import annotations

from typing import Any, Callable

import flet as ft

from ..config import Footer, Logo, Theme

Action = Callable[[Any], Any]
Translate = Callable[[str], str]


def icon(name: str | ft.IconData) -> ft.IconData:
    """Accepts the icon name ("apps", "translate"); in Flet 1.0 Icon only accepts `ft.Icons.*`."""
    return getattr(ft.Icons, name.upper()) if isinstance(name, str) else name


def logo(cfg: Logo, theme: Theme) -> ft.Control:
    if cfg.src:
        image = ft.Image(src=cfg.src, width=cfg.width, height=cfg.height, fit=ft.BoxFit.CONTAIN)
    else:
        image = ft.Container(
            content=ft.Icon(icon(cfg.icon), size=cfg.width * 0.5, color=theme.text_color),
            width=cfg.width,
            height=cfg.height,
            bgcolor=theme.primary_color,
            border_radius=ft.BorderRadius.all(cfg.width / 2),
            alignment=ft.Alignment.CENTER,
        )
    # Centers without stretching when the parent uses CrossAxisAlignment.STRETCH (login screen).
    return ft.Container(content=image, alignment=ft.Alignment.CENTER)


def title(text: str, theme: Theme, size: int = 22) -> ft.Text:
    return ft.Text(text, size=size, weight=ft.FontWeight.BOLD, color=theme.text_color, text_align=ft.TextAlign.CENTER)


def field(label: str, theme: Theme, password: bool = False, email: bool = False) -> ft.TextField:
    return ft.TextField(
        label=label,
        password=password,
        can_reveal_password=password,
        keyboard_type=ft.KeyboardType.EMAIL if email else ft.KeyboardType.TEXT,
        filled=True,
        bgcolor=theme.surface_color,
        color=theme.text_color,
        border_radius=ft.BorderRadius.all(10),
    )


def primary_button(label: str, on_click: Action, theme: Theme) -> ft.Button:
    return ft.Button(
        content=label,
        on_click=on_click,
        bgcolor=theme.primary_color,
        color="#FFFFFF",
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10), padding=ft.Padding.symmetric(vertical=16)),
    )


def google_button(label: str, on_click: Action) -> ft.Button:
    return ft.Button(
        content=label,
        icon=ft.Icons.LOGIN,
        on_click=on_click,
        bgcolor="#FFFFFF",
        color="#111111",
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10), padding=ft.Padding.symmetric(vertical=16)),
    )


def error_message() -> ft.Text:
    return ft.Text("", color="#EF4444", text_align=ft.TextAlign.CENTER, visible=False)


def footer(cfg: Footer, theme: Theme, t: Translate = str) -> ft.Column:
    links = [
        ft.Text(spans=[ft.TextSpan(t(link.label), url=link.url, style=ft.TextStyle(decoration=ft.TextDecoration.UNDERLINE))],
                size=12, color=theme.text_color)
        for link in cfg.links
    ]
    return ft.Column(
        [ft.Text(t(cfg.text), size=12, color=theme.text_color, opacity=0.7), *links],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=4,
    )


def card(title_: str, subtitle: str, theme: Theme, on_click: Action | None = None) -> ft.Container:
    return ft.Container(
        content=ft.Column(
            [ft.Text(title_, weight=ft.FontWeight.BOLD, color=theme.text_color),
             ft.Text(subtitle, size=12, color=theme.text_color, opacity=0.7)],
            spacing=4,
        ),
        padding=ft.Padding.all(16),
        bgcolor=theme.surface_color,
        border_radius=ft.BorderRadius.all(12),
        on_click=on_click,
    )
