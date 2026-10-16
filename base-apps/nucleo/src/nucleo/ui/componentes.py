"""Blocos de UI. Os filhos montam o próprio layout combinando estas peças."""

from __future__ import annotations

from typing import Any, Callable

import flet as ft

from ..config import Logo, Rodape, Tema

Acao = Callable[[Any], Any]


def logo(cfg: Logo, tema: Tema) -> ft.Control:
    if cfg.src:
        return ft.Image(src=cfg.src, width=cfg.largura, height=cfg.altura, fit=ft.BoxFit.CONTAIN)
    return ft.Container(
        content=ft.Icon(cfg.icone, size=cfg.largura * 0.5, color=tema.cor_texto),
        width=cfg.largura,
        height=cfg.altura,
        bgcolor=tema.cor_primaria,
        border_radius=ft.BorderRadius.all(cfg.largura / 2),
        alignment=ft.Alignment.CENTER,
    )


def titulo(texto: str, tema: Tema, tamanho: int = 22) -> ft.Text:
    return ft.Text(texto, size=tamanho, weight=ft.FontWeight.BOLD, color=tema.cor_texto, text_align=ft.TextAlign.CENTER)


def campo(rotulo: str, tema: Tema, senha: bool = False, email: bool = False) -> ft.TextField:
    return ft.TextField(
        label=rotulo,
        password=senha,
        can_reveal_password=senha,
        keyboard_type=ft.KeyboardType.EMAIL if email else ft.KeyboardType.TEXT,
        filled=True,
        bgcolor=tema.cor_superficie,
        color=tema.cor_texto,
        border_radius=ft.BorderRadius.all(10),
    )


def botao_primario(rotulo: str, ao_clicar: Acao, tema: Tema) -> ft.Button:
    return ft.Button(
        content=rotulo,
        on_click=ao_clicar,
        bgcolor=tema.cor_primaria,
        color="#FFFFFF",
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10), padding=ft.Padding.symmetric(vertical=16)),
    )


def botao_google(ao_clicar: Acao) -> ft.Button:
    return ft.Button(
        content="Continuar com Google",
        icon=ft.Icons.LOGIN,
        on_click=ao_clicar,
        bgcolor="#FFFFFF",
        color="#111111",
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10), padding=ft.Padding.symmetric(vertical=16)),
    )


def mensagem_erro() -> ft.Text:
    return ft.Text("", color="#EF4444", text_align=ft.TextAlign.CENTER, visible=False)


def mensagem_aviso(tema: Tema) -> ft.Text:
    return ft.Text("", color=tema.cor_primaria, text_align=ft.TextAlign.CENTER, visible=False)


def rodape(cfg: Rodape, tema: Tema) -> ft.Column:
    links = [
        ft.Text(spans=[ft.TextSpan(link.rotulo, url=link.url, style=ft.TextStyle(decoration=ft.TextDecoration.UNDERLINE))],
                size=12, color=tema.cor_texto)
        for link in cfg.links
    ]
    return ft.Column(
        [ft.Text(cfg.texto, size=12, color=tema.cor_texto, opacity=0.7), *links],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=4,
    )


def cartao(titulo_: str, subtitulo: str, tema: Tema, ao_clicar: Acao | None = None) -> ft.Container:
    return ft.Container(
        content=ft.Column(
            [ft.Text(titulo_, weight=ft.FontWeight.BOLD, color=tema.cor_texto),
             ft.Text(subtitulo, size=12, color=tema.cor_texto, opacity=0.7)],
            spacing=4,
        ),
        padding=ft.Padding.all(16),
        bgcolor=tema.cor_superficie,
        border_radius=ft.BorderRadius.all(12),
        on_click=ao_clicar,
    )
