"""App Beta layout: side menu, grid dashboard and its own login screen."""

import flet as ft

from core import Context, LoginForm, components as c

COLLECTION = "records"


def login_screen(ctx: Context) -> ft.Control:
    """Own login: Google first, email/password in a card below."""
    cfg, theme = ctx.config, ctx.config.theme
    form = LoginForm(ctx)
    email_card = ft.Container(
        content=ft.Column([form.email, form.password, form.error, form.sign_in_button, form.sign_up_button],
                          horizontal_alignment=ft.CrossAxisAlignment.STRETCH, spacing=12),
        padding=ft.Padding.all(20),
        bgcolor=theme.surface_color,
        border_radius=ft.BorderRadius.all(16),
    )
    return ft.SafeArea(
        expand=True,
        content=ft.Column(
            [ft.Row([c.logo(cfg.logo, theme), c.title(cfg.name, theme, 26)],
                    alignment=ft.MainAxisAlignment.CENTER, spacing=16),
             form.google_button,
             ft.Text(ctx.t("login.or_email"), color=theme.text_color, opacity=0.6, text_align=ft.TextAlign.CENTER),
             email_card,
             c.footer(cfg.footer, theme, ctx.t)],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
            spacing=16,
            scroll=ft.ScrollMode.AUTO,
            expand=True,
        ),
    )


def _dashboard_screen(ctx: Context) -> ft.Control:
    theme = ctx.config.theme
    records = ctx.data.list(COLLECTION, {"owner": ctx.user.id})
    grid = ft.GridView(
        expand=True, max_extent=180, child_aspect_ratio=1.4, spacing=12, run_spacing=12,
        controls=[c.card(r["title"], r["created_at"][:10], theme) for r in records],
    )
    empty = ft.Text(ctx.t("dashboard.empty"), color=theme.text_color, opacity=0.6)
    return ft.Column([c.title(ctx.t("dashboard.title"), theme), grid if records else empty], expand=True)


def _settings_screen(ctx: Context) -> ft.Control:
    theme = ctx.config.theme
    return ft.Column(
        [c.title(ctx.t("settings.title"), theme),
         c.card(ctx.t("settings.account"), ctx.user.email, theme),
         c.primary_button(ctx.t("account.sign_out"), ctx.sign_out, theme)],
        horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
        spacing=16,
    )


def build_app(ctx: Context) -> None:
    page, theme = ctx.page, ctx.config.theme
    screens = [_dashboard_screen, _settings_screen]
    area = ft.SafeArea(content=screens[0](ctx), expand=True)

    def show(index: int) -> None:
        area.content = screens[index](ctx)
        page.floating_action_button.visible = index == 0
        page.update()

    def on_select(e) -> None:
        page.drawer.open = False
        show(e.control.selected_index)

    def new_record(_=None) -> None:
        total = len(ctx.data.list(COLLECTION, {"owner": ctx.user.id}))
        ctx.data.create(COLLECTION, {"title": ctx.t("dashboard.record", number=total + 1), "owner": ctx.user.id})
        show(0)

    async def open_menu(_=None) -> None:
        await page.show_drawer()

    page.drawer = ft.NavigationDrawer(
        selected_index=0,
        on_change=on_select,
        controls=[
            ft.Container(c.title(ctx.config.name, theme, 18), padding=ft.Padding.all(20)),
            ft.NavigationDrawerDestination(icon=ft.Icons.DASHBOARD_OUTLINED, label=ctx.t("dashboard.title")),
            ft.NavigationDrawerDestination(icon=ft.Icons.SETTINGS_OUTLINED, label=ctx.t("settings.title")),
        ],
    )
    page.appbar = ft.AppBar(
        leading=ft.IconButton(icon=ft.Icons.MENU, on_click=open_menu),
        title=ft.Text(ctx.config.name),
        bgcolor=theme.surface_color,
    )
    page.floating_action_button = ft.FloatingActionButton(icon=ft.Icons.ADD, on_click=new_record,
                                                          bgcolor=theme.primary_color)
    page.add(area)
