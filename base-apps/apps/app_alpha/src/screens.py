"""App Alpha layout: bottom tab bar with Home (list) and Profile."""

import flet as ft

from core import Context, components as c

COLLECTION = "items"


def _home_screen(ctx: Context) -> ft.Control:
    theme, t = ctx.config.theme, ctx.t
    items_list = ft.ListView(expand=True, spacing=8)
    new_item = c.field(t("home.new_item"), theme)

    def reload() -> None:
        items = ctx.data.list(COLLECTION, {"owner": ctx.user.id})
        items_list.controls = [
            ft.ListTile(
                title=ft.Text(i["title"], color=theme.text_color),
                trailing=ft.IconButton(icon=ft.Icons.DELETE_OUTLINE, on_click=lambda _, id_=i["id"]: remove(id_)),
            )
            for i in items
        ] or [ft.Text(t("home.empty"), color=theme.text_color, opacity=0.6)]

    def add(_=None) -> None:
        if (new_item.value or "").strip():
            ctx.data.create(COLLECTION, {"title": new_item.value.strip(), "owner": ctx.user.id})
            new_item.value = ""
            reload()
            ctx.page.update()

    def remove(id_: str) -> None:
        ctx.data.delete(COLLECTION, id_)
        reload()
        ctx.page.update()

    new_item.on_submit = add
    reload()
    return ft.Column(
        [c.title(t("home.title"), theme), ft.Row([ft.Container(new_item, expand=True),
                                                  ft.IconButton(icon=ft.Icons.ADD, on_click=add)]), items_list],
        expand=True,
    )


def _profile_screen(ctx: Context) -> ft.Control:
    theme = ctx.config.theme
    return ft.Column(
        [c.logo(ctx.config.logo, theme), c.title(ctx.user.name or ctx.user.email, theme, 18),
         ft.Text(ctx.user.email, color=theme.text_color, opacity=0.7),
         c.primary_button(ctx.t("account.sign_out"), ctx.sign_out, theme)],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=16,
    )


def build_app(ctx: Context) -> None:
    page = ctx.page
    screens = [_home_screen, _profile_screen]
    area = ft.SafeArea(content=screens[0](ctx), expand=True)

    def switch(e) -> None:
        area.content = screens[e.control.selected_index](ctx)
        page.update()

    page.navigation_bar = ft.NavigationBar(
        selected_index=0,
        on_change=switch,
        destinations=[
            ft.NavigationBarDestination(icon=ft.Icons.HOME_OUTLINED, label=ctx.t("home.tab")),
            ft.NavigationBarDestination(icon=ft.Icons.PERSON_OUTLINE, label=ctx.t("profile.tab")),
        ],
    )
    page.add(area)
