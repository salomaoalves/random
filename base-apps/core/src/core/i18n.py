"""UI texts by language. English is the default; the device language is used when supported.

Catalogs map a language code to {key: text}. The core ships its own texts (`CORE_STRINGS`)
and each app adds its own through `AppConfig.strings`. A missing key falls back to English,
then to the key itself, so plain text can be passed wherever a key is expected.
"""

from __future__ import annotations

from typing import Iterable, Mapping, Union

Catalog = Mapping[str, Mapping[str, str]]
Localized = Union[str, Mapping[str, str]]  # plain text, or {"en": ..., "pt": ...}

DEFAULT_LANGUAGE = "en"

CORE_STRINGS: Catalog = {
    "en": {
        "login.email": "Email",
        "login.password": "Password",
        "login.sign_in": "Sign in",
        "login.sign_up": "Create account",
        "login.google": "Continue with Google",
        "login.or_email": "or sign in with email",
        "login.forgot_password": "Forgot password",
        "login.reset_sent": "If an account exists for this email, we sent a link to reset the password.",
        "auth.invalid_email": "Invalid email.",
        "auth.short_password": "The password must have at least 6 characters.",
        "auth.email_taken": "An account with this email already exists.",
        "auth.wrong_credentials": "Wrong email or password.",
        "error.generic": "Something went wrong. Please try again.",
        "account.sign_out": "Sign out",
    },
    "pt": {
        "login.email": "Email",
        "login.password": "Senha",
        "login.sign_in": "Entrar",
        "login.sign_up": "Criar conta",
        "login.google": "Continuar com Google",
        "login.or_email": "ou entre com email",
        "login.forgot_password": "Esqueci a senha",
        "login.reset_sent": "Se existir uma conta com esse email, enviamos um link para redefinir a senha.",
        "auth.invalid_email": "Email inválido.",
        "auth.short_password": "A senha precisa ter pelo menos 6 caracteres.",
        "auth.email_taken": "Já existe uma conta com esse email.",
        "auth.wrong_credentials": "Email ou senha incorretos.",
        "error.generic": "Não foi possível concluir. Tente de novo.",
        "account.sign_out": "Sair",
    },
    "es": {
        "login.email": "Correo",
        "login.password": "Contraseña",
        "login.sign_in": "Entrar",
        "login.sign_up": "Crear cuenta",
        "login.google": "Continuar con Google",
        "login.or_email": "o entra con tu correo",
        "login.forgot_password": "Olvidé la contraseña",
        "login.reset_sent": "Si existe una cuenta con ese correo, enviamos un enlace para restablecer la contraseña.",
        "auth.invalid_email": "Correo inválido.",
        "auth.short_password": "La contraseña debe tener al menos 6 caracteres.",
        "auth.email_taken": "Ya existe una cuenta con ese correo.",
        "auth.wrong_credentials": "Correo o contraseña incorrectos.",
        "error.generic": "No se pudo completar. Inténtalo de nuevo.",
        "account.sign_out": "Salir",
    },
}


def _normalize(language: str) -> str:
    """"pt-BR" / "pt_BR" / "PT" -> "pt"."""
    return (language or "").replace("_", "-").split("-")[0].lower()


def merge(*catalogs: Catalog) -> dict[str, dict[str, str]]:
    merged: dict[str, dict[str, str]] = {}
    for catalog in catalogs:
        for language, texts in catalog.items():
            merged.setdefault(language, {}).update(texts)
    return merged


class Translator:
    def __init__(self, catalog: Catalog, language: str = DEFAULT_LANGUAGE) -> None:
        self.catalog = catalog
        self.language = DEFAULT_LANGUAGE
        self.set_language(language)

    @property
    def languages(self) -> tuple[str, ...]:
        return tuple(self.catalog)

    def set_language(self, language: str) -> bool:
        """Switches language if supported. Returns True when it changed."""
        language = _normalize(language)
        new = language if language in self.catalog else DEFAULT_LANGUAGE
        changed, self.language = new != self.language, new
        return changed

    def pick(self, preferred: Iterable[str]) -> bool:
        """Uses the first supported language in priority order (e.g. the device locales)."""
        for language in preferred:
            if _normalize(language) in self.catalog:
                return self.set_language(language)
        return self.set_language(DEFAULT_LANGUAGE)

    def t(self, key: str, **values: object) -> str:
        text = self.catalog.get(self.language, {}).get(key) or self.catalog.get(DEFAULT_LANGUAGE, {}).get(key) or key
        return text.format(**values) if values else text

    def localize(self, value: Localized) -> str:
        """Resolves content that carries its own translations, e.g. {"en": "Apple", "pt": "Maçã"}."""
        if isinstance(value, str):
            return value
        return value.get(self.language) or value.get(DEFAULT_LANGUAGE) or next(iter(value.values()), "")
