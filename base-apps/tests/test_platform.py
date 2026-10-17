"""Tests without opening a window: data, auth, i18n and screen building with a fake page.

Run from the root:  python -m unittest discover tests
"""

import asyncio
import importlib
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "core" / "src"))

from core import AuthError, Translator, create_main  # noqa: E402
from core.auth import MemoryAuth  # noqa: E402
from core.data import MemoryRepository  # noqa: E402
from core.i18n import CORE_STRINGS  # noqa: E402


class FakePage(SimpleNamespace):
    def __init__(self, languages=()):
        super().__init__(controls=[], appbar=None, navigation_bar=None, drawer=None,
                         floating_action_button=None, updates=0, languages=list(languages))

    def add(self, *controls):
        self.controls.extend(controls)

    def update(self):
        self.updates += 1

    async def get_device_info(self):
        return SimpleNamespace(locales=[SimpleNamespace(language_code=lang) for lang in self.languages])


def load_app(folder):
    src = str(ROOT / "apps" / folder / "src")
    for m in ("app_config", "screens", "strings"):
        sys.modules.pop(m, None)
    sys.path.insert(0, src)
    try:
        return importlib.import_module("app_config").CONFIG, importlib.import_module("screens")
    finally:
        sys.path.remove(src)


def start(main, page):
    asyncio.run(main(page))
    return page


def find(ctrl, predicate):
    if predicate(ctrl):
        return ctrl
    children = list(getattr(ctrl, "controls", None) or [])
    if getattr(ctrl, "content", None) is not None and not isinstance(ctrl.content, str):
        children.append(ctrl.content)
    for child in children:
        found = find(child, predicate)
        if found:
            return found
    return None


def forgot_password(page):
    find(page.controls[0], lambda c: getattr(c, "label", None) == "Email").value = "ana@example.com"
    click(page, "Forgot password")
    info = find(page.controls[0], lambda c: getattr(c, "value", None) == CORE_STRINGS["en"]["login.reset_sent"])
    assert info is not None and info.visible, "reset message did not show up"


def click(page, label):
    button = find(page.controls[0], lambda c: getattr(c, "content", None) == label)
    assert button is not None, f"button {label!r} not found"
    button.on_click(None)


class TestData(unittest.TestCase):
    def test_crud(self):
        repo = MemoryRepository()
        item = repo.create("items", {"title": "a", "owner": "u1"})
        repo.create("items", {"title": "b", "owner": "u2"})
        self.assertEqual([i["title"] for i in repo.list("items", {"owner": "u1"})], ["a"])
        self.assertEqual(repo.update("items", item["id"], {"title": "a2"})["title"], "a2")
        repo.delete("items", item["id"])
        self.assertIsNone(repo.get("items", item["id"]))


class TestAuth(unittest.TestCase):
    def test_flow(self):
        auth, events = MemoryAuth(), []
        auth.on_change(events.append)
        auth.sign_up_email("Ana@Example.com", "123456")
        auth.sign_out()
        with self.assertRaises(AuthError):
            auth.sign_in_email("ana@example.com", "wrong1")
        self.assertIsNone(auth.current_user)  # an error does not sign in
        auth.sign_in_email("ana@example.com", "123456")
        self.assertEqual([e.email if e else None for e in events],
                         ["ana@example.com", None, "ana@example.com"])

    def test_password_reset(self):
        auth = MemoryAuth()
        auth.sign_up_email("ana@example.com", "123456")
        auth.sign_out()
        auth.send_password_reset(" Ana@Example.com ")
        auth.send_password_reset("nobody@example.com")   # no account: neither fails nor sends
        self.assertEqual(auth.sent_password_resets, ["ana@example.com"])
        self.assertIsNone(auth.current_user)             # asking for a reset does not sign in
        with self.assertRaises(AuthError):
            auth.send_password_reset("invalid")

    def test_validation(self):
        with self.assertRaises(AuthError) as invalid:
            MemoryAuth().sign_up_email("invalid", "123456")
        self.assertEqual(invalid.exception.key, "auth.invalid_email")
        with self.assertRaises(AuthError):
            MemoryAuth().sign_up_email("a@b.com", "123")


class TestI18n(unittest.TestCase):
    def test_translator(self):
        t = Translator({"en": {"hi": "Hi {name}", "only_en": "x"}, "pt": {"hi": "Oi {name}"}})
        self.assertEqual(t.t("hi", name="Ana"), "Hi Ana")             # English by default
        self.assertTrue(t.pick(["ja", "pt-BR", "en"]))               # first supported one wins
        self.assertEqual(t.t("hi", name="Ana"), "Oi Ana")
        self.assertEqual(t.t("only_en"), "x")                        # missing key falls back to English
        self.assertEqual(t.t("plain text"), "plain text")            # unknown key is shown as is
        self.assertEqual(t.localize({"en": "Apple", "pt": "Maçã"}), "Maçã")
        t.pick(["ja"])
        self.assertEqual(t.language, "en")                           # unsupported device language

    def test_core_catalog_complete(self):
        for language, texts in CORE_STRINGS.items():
            self.assertEqual(set(texts), set(CORE_STRINGS["en"]), language)

    def test_app_catalogs_complete(self):
        for folder in ("app_alpha", "app_beta"):
            strings = load_app(folder)[0].strings
            for language, texts in strings.items():
                self.assertEqual(set(texts), set(strings["en"]), f"{folder}/{language}")

    def test_device_language(self):
        config, screens = load_app("app_alpha")
        english = start(create_main(config, screens.build_app), FakePage())
        self.assertIsNotNone(find(english.controls[0], lambda c: getattr(c, "content", None) == "Sign in"))

        page = start(create_main(config, screens.build_app), FakePage(["pt"]))
        self.assertIsNotNone(find(page.controls[0], lambda c: getattr(c, "content", None) == "Entrar"))
        self.assertEqual(page.locale_configuration.current_locale.language_code, "pt")

        page.on_locale_change(SimpleNamespace(locales=[SimpleNamespace(language_code="es")]))
        self.assertIsNotNone(find(page.controls[0], lambda c: getattr(c, "content", None) == "Continuar con Google"))


class TestComponents(unittest.TestCase):
    def test_icon_by_name(self):
        import flet as ft
        from core import Logo, Theme, components as c
        self.assertEqual(c.icon("translate"), ft.Icons.TRANSLATE)   # Flet 1.0 rejects the plain name
        self.assertEqual(c.icon(ft.Icons.APPS), ft.Icons.APPS)
        self.assertEqual(c.logo(Logo(icon="apps"), Theme()).content.content.icon, ft.Icons.APPS)


class TestApps(unittest.TestCase):
    def test_alpha(self):
        config, screens = load_app("app_alpha")
        page = start(create_main(config, screens.build_app), FakePage())
        self.assertEqual(len(page.controls), 1)          # login screen
        self.assertIsNone(page.navigation_bar)
        forgot_password(page)
        self.assertIsNone(page.navigation_bar)           # still on the login screen
        click(page, "Continue with Google")
        self.assertIsNotNone(page.navigation_bar)        # tab layout

    def test_beta(self):
        config, screens = load_app("app_beta")
        page = start(create_main(config, screens.build_app, build_login=screens.login_screen), FakePage())
        self.assertIsNone(page.drawer)
        forgot_password(page)
        click(page, "Continue with Google")
        self.assertIsNotNone(page.drawer)                # side menu layout
        page.floating_action_button.on_click(None)       # creates a record
        self.assertEqual(len(page.controls), 1)


if __name__ == "__main__":
    unittest.main()
