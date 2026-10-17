"""Bheh tests without opening a window: path, stations, course, areas, feedback and languages.

Run from the root:  python -m unittest discover tests
"""

import asyncio
import importlib
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace

import flet as ft

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "apps" / "app_bheh" / "src"
sys.path.insert(0, str(ROOT / "core" / "src"))

from core import Translator, create_main  # noqa: E402


class FakePage(SimpleNamespace):
    def __init__(self, languages=()):
        super().__init__(controls=[], appbar=None, navigation_bar=None, drawer=None,
                         floating_action_button=None, dialogs=[], languages=list(languages))

    def add(self, *controls):
        self.controls.extend(controls)

    def update(self):
        pass

    def show_dialog(self, dialog):
        self.dialogs.append(dialog)

    def pop_dialog(self):
        return self.dialogs.pop()

    async def show_drawer(self):
        pass

    async def close_drawer(self):
        pass

    async def get_device_info(self):
        return SimpleNamespace(locales=[SimpleNamespace(language_code=lang) for lang in self.languages])


def load():
    for m in ("app_config", "screens", "content", "strings"):
        sys.modules.pop(m, None)
    sys.path.insert(0, str(SRC))
    try:
        return (importlib.import_module("app_config").CONFIG, importlib.import_module("screens"),
                importlib.import_module("content"))
    finally:
        sys.path.remove(str(SRC))


def find_all(ctrl, predicate):
    found = [ctrl] if predicate(ctrl) else []
    children = list(getattr(ctrl, "controls", None) or [])
    for attr in ("content", "leading", "label"):
        child = getattr(ctrl, attr, None)
        if child is not None and not isinstance(child, str):
            children.append(child)
    for child in children:
        found += find_all(child, predicate)
    return found


def texts(ctrl):
    return [t.value for t in find_all(ctrl, lambda c: isinstance(c, ft.Text) and c.value)]


class BhehTestCase(unittest.TestCase):
    languages = ()

    def setUp(self):
        self.config, self.screens, self.content = load()
        self.page, captured = FakePage(self.languages), {}

        def login(ctx):  # captures the context to sign in without clicking
            captured["ctx"] = ctx
            return ft.Text("login")

        asyncio.run(create_main(self.config, self.screens.build_app, build_login=login)(self.page))
        self.ctx = captured["ctx"]
        self.ctx.auth.sign_up_email("ana@example.com", "123456")

    def screen(self):
        return self.page.controls[0]

    def stations(self):
        return find_all(self.screen(), lambda c: isinstance(c, ft.Container) and c.width == 76)


class TestBheh(BhehTestCase):
    def answer_station(self):
        prompts = {self.ctx.i18n.localize(q.prompt): q
                   for s in self.content.SPANISH.area("basics").stations for q in s.questions}
        controls = ("Next", "See result", "Back to the path")
        while True:
            buttons = find_all(self.screen(), lambda c: isinstance(c, ft.Button) and not c.disabled
                               and c.content not in controls)
            if not buttons:
                return
            question = next(prompts[t] for t in texts(self.screen()) if t in prompts)
            buttons[question.answer].on_click(None)
            find_all(self.screen(), lambda c: isinstance(c, ft.Button) and c.visible
                     and c.content in ("Next", "See result"))[0].on_click(None)

    def test_layout_after_login(self):
        self.assertIsNotNone(self.page.appbar)
        self.assertIsNotNone(self.page.drawer)                        # settings/account menu
        self.assertEqual(len(self.page.appbar.actions), 1)            # course menu
        self.assertIsNotNone(self.page.floating_action_button)        # feedback
        names = [ch.label.value for ch in find_all(self.screen(), lambda c: isinstance(c, ft.Chip))]
        self.assertEqual(names, ["Basics", "Food", "Grammar"])        # English by default
        self.assertIn("Spanish · Basics", texts(self.screen()))

    def test_stations_unlock_in_order(self):
        first, second = self.stations()
        self.assertIsNotNone(first.on_click)
        self.assertIsNone(second.on_click)                            # locked

        first.on_click(None)
        self.assertFalse(self.page.floating_action_button.visible)    # no feedback during questions
        self.answer_station()
        self.assertIn("3 of 3 correct", texts(self.screen()))
        progress = self.ctx.data.list("progress", {"owner": self.ctx.user.id})
        self.assertEqual([(p["station"], p["correct"]) for p in progress], [(0, 3)])

        back = find_all(self.screen(), lambda c: getattr(c, "content", None) == "Back to the path")[0]
        back.on_click(None)
        self.assertIsNotNone(self.stations()[1].on_click)             # second one unlocked
        self.assertIn("1 of 2 stations completed", texts(self.screen()))

    def test_wrong_answer_shows_right_one(self):
        self.stations()[0].on_click(None)
        question = self.content.SPANISH.area("basics").stations[0].questions[0]
        options = [self.ctx.i18n.localize(o) for o in question.options]
        buttons = find_all(self.screen(), lambda c: isinstance(c, ft.Button) and c.content in options)
        buttons[(question.answer + 1) % 3].on_click(None)
        self.assertIn(f"Correct answer: {options[question.answer]}", texts(self.screen()))
        self.assertTrue(all(b.disabled for b in buttons))

    def test_switch_area_and_course(self):
        food = next(ch for ch in find_all(self.screen(), lambda c: isinstance(c, ft.Chip))
                    if ch.label.value == "Food")
        food.on_select(None)
        self.assertIn("Spanish · Food", texts(self.screen()))

        english = next(i for i in self.page.appbar.actions[0].items if i.content == "English")
        english.on_click(None)
        self.assertIn("English · Food", texts(self.screen()))         # keeps the area
        self.assertTrue(next(i for i in self.page.appbar.actions[0].items if i.content == "English").checked)
        prefs = self.ctx.data.list("preferences", {"owner": self.ctx.user.id})
        self.assertEqual([p["course"] for p in prefs], ["en"])        # remembered on the next login

    def test_settings_and_account_menu(self):
        event = SimpleNamespace(control=SimpleNamespace(selected_index=2))
        asyncio.run(self.page.drawer.on_change(event))
        self.assertIn("ana@example.com", texts(self.screen()))
        sign_out = find_all(self.screen(), lambda c: getattr(c, "content", None) == "Sign out")[0]
        sign_out.on_click(None)
        self.assertIsNone(self.ctx.user)
        self.assertIsNone(self.page.appbar)                           # back to login

    def test_feedback(self):
        self.page.floating_action_button.on_click(None)
        dialog = self.page.dialogs[-1]
        field = find_all(dialog.content, lambda c: isinstance(c, ft.TextField))[0]
        send = dialog.actions[1]

        send.on_click(None)                                           # empty: not sent
        self.assertEqual(self.ctx.data.list("feedback"), [])
        self.assertIs(self.page.dialogs[-1], dialog)

        field.value = "More areas, please"
        send.on_click(None)
        feedback = self.ctx.data.list("feedback")
        self.assertEqual([(f["text"], f["course"], f["area"], f["ui_language"]) for f in feedback],
                         [("More areas, please", "es", "basics", "en")])
        self.assertIsInstance(self.page.dialogs[-1], ft.SnackBar)


class TestBhehInPortuguese(BhehTestCase):
    languages = ("pt",)

    def test_ui_and_content_follow_device_language(self):
        self.assertIn("Espanhol · Básico", texts(self.screen()))
        self.assertIn("1. Saudações", texts(self.screen()))
        self.stations()[0].on_click(None)
        self.assertIn('Como se diz "bom dia"?', texts(self.screen()))


class TestCatalogs(unittest.TestCase):
    def test_strings_complete(self):
        strings = load()[0].strings
        for language, values in strings.items():
            self.assertEqual(set(values), set(strings["en"]), language)

    def test_content_valid(self):
        _, _, content = load()
        for language in ("en", "pt"):
            t = Translator({"en": {}, "pt": {}}, language)
            for course in content.COURSES:
                for area in course.areas:
                    self.assertTrue(area.stations, f"{course.id}/{area.id} has no stations")
                    for station in area.stations:
                        for q in station.questions:
                            options = [t.localize(o) for o in q.options]
                            self.assertEqual(len(set(options)), len(options), t.localize(q.prompt))
                            self.assertLess(q.answer, len(options))


if __name__ == "__main__":
    unittest.main()
