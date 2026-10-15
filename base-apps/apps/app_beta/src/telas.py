"""Layout do App Beta: menu lateral, painel em grade e login próprio."""

import flet as ft

from nucleo import Contexto, FormularioLogin, componentes as c

COLECAO = "registros"


def tela_login(ctx: Contexto) -> ft.Control:
    """Login próprio: Google em destaque, email/senha num cartão abaixo."""
    cfg, tema = ctx.config, ctx.config.tema
    form = FormularioLogin(ctx)
    cartao_email = ft.Container(
        content=ft.Column([form.email, form.senha, form.erro, form.botao_entrar, form.botao_cadastrar],
                          horizontal_alignment=ft.CrossAxisAlignment.STRETCH, spacing=12),
        padding=ft.Padding.all(20),
        bgcolor=tema.cor_superficie,
        border_radius=ft.BorderRadius.all(16),
    )
    return ft.SafeArea(
        expand=True,
        content=ft.Column(
            [ft.Row([c.logo(cfg.logo, tema), c.titulo(cfg.nome, tema, 26)],
                    alignment=ft.MainAxisAlignment.CENTER, spacing=16),
             form.botao_google,
             ft.Text("ou entre com email", color=tema.cor_texto, opacity=0.6, text_align=ft.TextAlign.CENTER),
             cartao_email,
             c.rodape(cfg.rodape, tema)],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
            spacing=16,
            scroll=ft.ScrollMode.AUTO,
            expand=True,
        ),
    )


def _tela_painel(ctx: Contexto) -> ft.Control:
    tema = ctx.config.tema
    registros = ctx.dados.listar(COLECAO, {"dono": ctx.usuario.id})
    grade = ft.GridView(
        expand=True, max_extent=180, child_aspect_ratio=1.4, spacing=12, run_spacing=12,
        controls=[c.cartao(r["titulo"], r["criado_em"][:10], tema) for r in registros],
    )
    vazio = ft.Text("Toque em + para criar um registro.", color=tema.cor_texto, opacity=0.6)
    return ft.Column([c.titulo("Painel", tema), grade if registros else vazio], expand=True)


def _tela_ajustes(ctx: Contexto) -> ft.Control:
    tema = ctx.config.tema
    return ft.Column(
        [c.titulo("Ajustes", tema),
         c.cartao("Conta", ctx.usuario.email, tema),
         c.botao_primario("Sair", ctx.sair, tema)],
        horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
        spacing=16,
    )


def montar_app(ctx: Contexto) -> None:
    page, tema = ctx.page, ctx.config.tema
    telas = [_tela_painel, _tela_ajustes]
    area = ft.SafeArea(content=telas[0](ctx), expand=True)
    atual = {"indice": 0}

    def mostrar(indice: int) -> None:
        atual["indice"] = indice
        area.content = telas[indice](ctx)
        page.floating_action_button.visible = indice == 0
        page.update()

    def ao_escolher(e) -> None:
        page.drawer.open = False
        mostrar(e.control.selected_index)

    def novo_registro(_=None) -> None:
        total = len(ctx.dados.listar(COLECAO, {"dono": ctx.usuario.id}))
        ctx.dados.criar(COLECAO, {"titulo": f"Registro {total + 1}", "dono": ctx.usuario.id})
        mostrar(0)

    async def abrir_menu(_=None) -> None:
        await page.show_drawer()

    page.drawer = ft.NavigationDrawer(
        selected_index=0,
        on_change=ao_escolher,
        controls=[
            ft.Container(c.titulo(ctx.config.nome, tema, 18), padding=ft.Padding.all(20)),
            ft.NavigationDrawerDestination(icon=ft.Icons.DASHBOARD_OUTLINED, label="Painel"),
            ft.NavigationDrawerDestination(icon=ft.Icons.SETTINGS_OUTLINED, label="Ajustes"),
        ],
    )
    page.appbar = ft.AppBar(
        leading=ft.IconButton(icon=ft.Icons.MENU, on_click=abrir_menu),
        title=ft.Text(ctx.config.nome),
        bgcolor=tema.cor_superficie,
    )
    page.floating_action_button = ft.FloatingActionButton(icon=ft.Icons.ADD, on_click=novo_registro,
                                                          bgcolor=tema.cor_primaria)
    page.add(area)
