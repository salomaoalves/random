"""Bheh layout.

Top bar: settings/account menu (left), logo (center), language being learned (right).
Below it, the areas (Basics, Food, Grammar…). In the middle, the path of stations,
each with n questions. At the bottom, the suggestion button to send feedback.
"""

from __future__ import annotations

import flet as ft

import content as ct
from core import Context, Record, components as c

PROGRESS, PREFERENCES, FEEDBACK = "progress", "preferences", "feedback"
RIGHT_COLOR, WRONG_COLOR = "#16A34A", "#DC2626"


class BhehApp:
    def __init__(self, ctx: Context) -> None:
        self.ctx, self.page, self.theme, self.t = ctx, ctx.page, ctx.config.theme, ctx.t
        self.course = ct.course(self._saved_course())
        self.area = self.course.areas[0]
        self.body = ft.SafeArea(content=ft.Container(), expand=True)

    def text(self, value) -> str:
        return self.ctx.i18n.localize(value)

    # ---- data ----------------------------------------------------------------

    @property
    def _owner(self) -> dict[str, str]:
        return {"owner": self.ctx.user.id}

    def _saved_course(self) -> str:
        prefs = self.ctx.data.list(PREFERENCES, self._owner)
        return prefs[0]["course"] if prefs else ct.COURSES[0].id

    def _save_course(self) -> None:
        prefs = self.ctx.data.list(PREFERENCES, self._owner)
        if prefs:
            self.ctx.data.update(PREFERENCES, prefs[0]["id"], {"course": self.course.id})
        else:
            self.ctx.data.create(PREFERENCES, {**self._owner, "course": self.course.id})

    def _completed(self) -> dict[int, Record]:
        filters = {**self._owner, "course": self.course.id, "area": self.area.id}
        return {r["station"]: r for r in self.ctx.data.list(PROGRESS, filters)}

    def _save_progress(self, index: int, correct: int, total: int) -> None:
        previous = self._completed().get(index)
        if previous is None:
            self.ctx.data.create(PROGRESS, {**self._owner, "course": self.course.id, "area": self.area.id,
                                            "station": index, "correct": correct, "total": total})
        elif correct > previous["correct"]:
            self.ctx.data.update(PROGRESS, previous["id"], {"correct": correct})

    # ---- structure -----------------------------------------------------------

    def build(self) -> None:
        page, theme, t = self.page, self.theme, self.t
        page.appbar = ft.AppBar(
            leading=ft.IconButton(icon=ft.Icons.MENU, tooltip=t("menu.tooltip"), on_click=self._open_menu),
            title=self._bar_logo(),
            center_title=True,
            bgcolor=theme.surface_color,
            actions=[self._course_menu()],
        )
        page.drawer = ft.NavigationDrawer(
            selected_index=0,
            on_change=self._on_menu_select,
            controls=[
                ft.Container(c.title(self.ctx.config.name, theme, 18), padding=ft.Padding.all(20)),
                ft.NavigationDrawerDestination(icon=ft.Icons.ROUTE_OUTLINED, label=t("menu.path")),
                ft.NavigationDrawerDestination(icon=ft.Icons.SETTINGS_OUTLINED, label=t("menu.settings")),
                ft.NavigationDrawerDestination(icon=ft.Icons.PERSON_OUTLINE, label=t("menu.account")),
            ],
        )
        page.floating_action_button = ft.FloatingActionButton(
            icon=ft.Icons.FEEDBACK_OUTLINED, tooltip=t("feedback.tooltip"), on_click=self.open_feedback,
            bgcolor=theme.primary_color, foreground_color=theme.on_primary_color,
        )
        page.floating_action_button_location = ft.FloatingActionButtonLocation.START_FLOAT
        page.add(self.body)
        self.show_path(refresh=False)

    def _bar_logo(self) -> ft.Control:
        logo = self.ctx.config.logo
        if logo.src:
            return ft.Image(src=logo.src, height=32, fit=ft.BoxFit.CONTAIN)
        return ft.Row([ft.Icon(c.icon(logo.icon), color=self.theme.primary_color),
                       ft.Text(self.ctx.config.name, weight=ft.FontWeight.BOLD, color=self.theme.text_color)],
                      tight=True, spacing=8)

    def _course_menu(self) -> ft.PopupMenuButton:
        return ft.PopupMenuButton(
            icon=ft.Icons.TRANSLATE,
            icon_color=self.theme.primary_color,
            tooltip=self.t("course.tooltip"),
            items=[ft.PopupMenuItem(content=self.t(x.name_key), checked=x.id == self.course.id,
                                    on_click=lambda _, id_=x.id: self.switch_course(id_))
                   for x in ct.COURSES],
        )

    def _show(self, control: ft.Control, with_feedback: bool, refresh: bool = True) -> None:
        self.body.content = control
        self.page.floating_action_button.visible = with_feedback
        if refresh:
            self.page.update()

    async def _open_menu(self, _=None) -> None:
        await self.page.show_drawer()

    async def _on_menu_select(self, e) -> None:
        await self.page.close_drawer()
        [self.show_path, self.show_settings, self.show_account][e.control.selected_index]()

    # ---- actions -------------------------------------------------------------

    def switch_course(self, id_: str) -> None:
        self.course = ct.course(id_)
        self.area = self.course.area(self.area.id)
        self._save_course()
        self.page.appbar.actions = [self._course_menu()]
        self.show_path()

    def switch_area(self, id_: str) -> None:
        self.area = self.course.area(id_)
        self.show_path()

    # ---- path ----------------------------------------------------------------

    def show_path(self, _=None, refresh: bool = True) -> None:
        self._show(ft.Column([self._area_picker(), self._path()], expand=True, spacing=16),
                   with_feedback=True, refresh=refresh)

    def _area_picker(self) -> ft.Row:
        theme = self.theme
        chips = []
        for a in self.course.areas:
            active = a.id == self.area.id
            chips.append(ft.Chip(
                label=ft.Text(self.t(a.name_key), color=theme.on_primary_color if active else theme.text_color),
                leading=ft.Icon(c.icon(a.icon), color=theme.on_primary_color if active else theme.primary_color),
                selected=active, show_checkmark=False,
                selected_color=theme.primary_color, bgcolor=theme.surface_color,
                on_select=lambda _, id_=a.id: self.switch_area(id_),
            ))
        return ft.Row(chips, scroll=ft.ScrollMode.AUTO, spacing=8)

    def _path(self) -> ft.ListView:
        theme, stations = self.theme, self.area.stations
        done = self._completed()
        items: list[ft.Control] = [
            c.title(f"{self.t(self.course.name_key)} · {self.t(self.area.name_key)}", theme, 20),
            ft.Text(self.t("path.progress", done=len(done), total=len(stations)), color=theme.text_color,
                    opacity=0.7, text_align=ft.TextAlign.CENTER),
            ft.Container(height=12),
        ]
        for i, station in enumerate(stations):
            unlocked = i == 0 or (i - 1) in done
            if i:
                items.append(ft.Container(width=4, height=32, border_radius=ft.BorderRadius.all(2),
                                          bgcolor=theme.primary_color if unlocked else theme.surface_color))
            items.append(self._station(i, station, done.get(i), unlocked))
        return ft.ListView(
            [ft.Column(items, horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=0)],
            expand=True, padding=ft.Padding.only(bottom=96),
        )

    def _station(self, index: int, station: ct.Station, done: Record | None, unlocked: bool) -> ft.Control:
        theme, t = self.theme, self.t
        if done:
            icon, fill, color, border = ft.Icons.CHECK, theme.primary_color, theme.on_primary_color, theme.primary_color
            detail = t("station.score", correct=done["correct"], total=done["total"])
        elif unlocked:
            icon, fill, color, border = ft.Icons.PLAY_ARROW, theme.surface_color, theme.primary_color, theme.primary_color
            detail = t("station.questions", count=len(station.questions))
        else:
            icon, fill, color, border = ft.Icons.LOCK_OUTLINE, theme.surface_color, theme.text_color, theme.surface_color
            detail = t("station.locked")
        node = ft.Container(
            content=ft.Icon(icon, color=color, size=32), width=76, height=76, bgcolor=fill,
            border=ft.Border.all(3, border), border_radius=ft.BorderRadius.all(38), alignment=ft.Alignment.CENTER,
            on_click=(lambda _: self.open_station(index)) if unlocked else None,
            opacity=1 if unlocked else 0.5, tooltip=self.text(station.title),
        )
        return ft.Column(
            [node, ft.Text(f"{index + 1}. {self.text(station.title)}", weight=ft.FontWeight.BOLD,
                           color=theme.text_color),
             ft.Text(detail, size=12, color=theme.text_color, opacity=0.7)],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=6,
        )

    # ---- station (questions) -------------------------------------------------

    def open_station(self, index: int) -> None:
        theme, t, station = self.theme, self.t, self.area.stations[index]
        questions, state = station.questions, {"current": 0, "correct": 0}
        body = ft.Column(expand=True, spacing=16, scroll=ft.ScrollMode.AUTO,
                         horizontal_alignment=ft.CrossAxisAlignment.STRETCH)

        def advance(_=None) -> None:
            state["current"] += 1
            render()
            self.page.update()

        def render() -> None:
            n, i = len(questions), state["current"]
            if i == n:
                self._save_progress(index, state["correct"], n)
                body.controls = [
                    ft.Icon(ft.Icons.EMOJI_EVENTS_OUTLINED, size=72, color=theme.primary_color),
                    c.title(t("quiz.done"), theme),
                    ft.Text(t("quiz.done_score", correct=state["correct"], total=n), color=theme.text_color,
                            text_align=ft.TextAlign.CENTER),
                    c.primary_button(t("quiz.back"), self.show_path, theme),
                ]
                return
            question = questions[i]
            result = ft.Text("", visible=False, text_align=ft.TextAlign.CENTER, weight=ft.FontWeight.BOLD)
            next_button = c.primary_button(t("quiz.next") if i + 1 < n else t("quiz.see_result"), advance, theme)
            next_button.visible = False
            options: list[ft.Button] = []

            def answer(choice: int) -> None:
                right = choice == question.answer
                state["correct"] += right
                for j, button in enumerate(options):
                    button.disabled = True
                    if j == question.answer:
                        button.bgcolor = RIGHT_COLOR
                    elif j == choice:
                        button.bgcolor = WRONG_COLOR
                result.value = (t("quiz.correct") if right
                                else t("quiz.answer_was", answer=self.text(question.options[question.answer])))
                result.color = RIGHT_COLOR if right else WRONG_COLOR
                result.visible = next_button.visible = True
                self.page.update()

            options.extend(
                ft.Button(content=self.text(option), on_click=lambda _, j=j: answer(j), bgcolor=theme.surface_color,
                          color=theme.text_color, style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10),
                                                                       padding=ft.Padding.symmetric(vertical=16)))
                for j, option in enumerate(question.options)
            )
            body.controls = [
                ft.Row([ft.IconButton(icon=ft.Icons.CLOSE, tooltip=t("quiz.exit"), on_click=self.show_path),
                        ft.Text(f"{self.text(station.title)} · {i + 1}/{n}", color=theme.text_color, expand=True)]),
                ft.ProgressBar(value=i / n, color=theme.primary_color, bgcolor=theme.surface_color),
                ft.Text(self.text(question.prompt), size=20, weight=ft.FontWeight.BOLD, color=theme.text_color),
                *options,
                result,
                next_button,
            ]

        render()
        self._show(body, with_feedback=False)

    # ---- settings and account ------------------------------------------------

    def show_settings(self) -> None:
        theme, t = self.theme, self.t
        group = ft.RadioGroup(
            value=self.course.id,
            on_change=lambda e: self.switch_course(e.control.value),
            content=ft.Column([ft.Radio(value=x.id, label=t(x.name_key), active_color=theme.primary_color)
                               for x in ct.COURSES]),
        )
        self._show(ft.Column([c.title(t("menu.settings"), theme),
                              ft.Text(t("settings.course"), color=theme.text_color, opacity=0.7), group],
                             spacing=16), with_feedback=True)

    def show_account(self) -> None:
        theme, t, user = self.theme, self.t, self.ctx.user
        self._show(ft.Column([c.title(t("menu.account"), theme),
                              c.card(user.name or t("account.no_name"), user.email, theme),
                              c.primary_button(t("account.sign_out"), self.ctx.sign_out, theme)],
                             horizontal_alignment=ft.CrossAxisAlignment.STRETCH, spacing=16),
                   with_feedback=True)

    # ---- feedback ------------------------------------------------------------

    def open_feedback(self, _=None) -> None:
        theme, t, page = self.theme, self.t, self.page
        field = c.field(t("feedback.field"), theme)
        field.multiline, field.min_lines, field.max_lines = True, 3, 6
        error = c.error_message()

        def send(_=None) -> None:
            text = (field.value or "").strip()
            if not text:
                error.value, error.visible = t("feedback.empty"), True
                page.update()
                return
            self.ctx.data.create(FEEDBACK, {**self._owner, "text": text, "course": self.course.id,
                                            "area": self.area.id, "ui_language": self.ctx.i18n.language})
            page.pop_dialog()
            page.show_dialog(ft.SnackBar(ft.Text(t("feedback.thanks"))))

        page.show_dialog(ft.AlertDialog(
            title=ft.Text(t("feedback.title")),
            content=ft.Column([field, error], tight=True, spacing=8),
            actions=[ft.TextButton(content=t("feedback.cancel"), on_click=lambda _: page.pop_dialog()),
                     c.primary_button(t("feedback.send"), send, theme)],
        ))


def build_app(ctx: Context) -> None:
    BhehApp(ctx).build()
