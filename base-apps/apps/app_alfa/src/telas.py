"""Layout do App Alfa: barra de abas inferior com Início (lista) e Perfil."""

import flet as ft

from nucleo import Contexto, componentes as c

COLECAO = "itens"


def _tela_inicio(ctx: Contexto) -> ft.Control:
    tema = ctx.config.tema
    lista = ft.ListView(expand=True, spacing=8)
    novo = c.campo("Novo item", tema)

    def recarregar() -> None:
        itens = ctx.dados.listar(COLECAO, {"dono": ctx.usuario.id})
        lista.controls = [
            ft.ListTile(
                title=ft.Text(i["titulo"], color=tema.cor_texto),
                trailing=ft.IconButton(icon=ft.Icons.DELETE_OUTLINE, on_click=lambda _, id_=i["id"]: remover(id_)),
            )
            for i in itens
        ] or [ft.Text("Nenhum item ainda.", color=tema.cor_texto, opacity=0.6)]

    def adicionar(_=None) -> None:
        if (novo.value or "").strip():
            ctx.dados.criar(COLECAO, {"titulo": novo.value.strip(), "dono": ctx.usuario.id})
            novo.value = ""
            recarregar()
            ctx.page.update()

    def remover(id_: str) -> None:
        ctx.dados.remover(COLECAO, id_)
        recarregar()
        ctx.page.update()

    novo.on_submit = adicionar
    recarregar()
    return ft.Column(
        [c.titulo("Meus itens", tema), ft.Row([ft.Container(novo, expand=True),
                                               ft.IconButton(icon=ft.Icons.ADD, on_click=adicionar)]), lista],
        expand=True,
    )


def _tela_perfil(ctx: Contexto) -> ft.Control:
    tema = ctx.config.tema
    return ft.Column(
        [c.logo(ctx.config.logo, tema), c.titulo(ctx.usuario.nome or ctx.usuario.email, tema, 18),
         ft.Text(ctx.usuario.email, color=tema.cor_texto, opacity=0.7),
         c.botao_primario("Sair", ctx.sair, tema)],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=16,
    )


def montar_app(ctx: Contexto) -> None:
    page = ctx.page
    telas = [_tela_inicio, _tela_perfil]
    area = ft.SafeArea(content=telas[0](ctx), expand=True)

    def trocar(e) -> None:
        area.content = telas[e.control.selected_index](ctx)
        page.update()

    page.navigation_bar = ft.NavigationBar(
        selected_index=0,
        on_change=trocar,
        destinations=[
            ft.NavigationBarDestination(icon=ft.Icons.HOME_OUTLINED, label="Início"),
            ft.NavigationBarDestination(icon=ft.Icons.PERSON_OUTLINE, label="Perfil"),
        ],
    )
    page.add(area)
