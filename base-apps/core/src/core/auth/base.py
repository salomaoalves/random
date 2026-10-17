"""Authentication interface. Navigation reacts to `on_change`, never to a button's
return value, so a failed or cancelled login never leads to the home screen."""

from __future__ import annotations

import re
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Callable

_EMAIL = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


@dataclass(frozen=True)
class User:
    id: str
    email: str
    name: str = ""
    provider: str = "email"


class AuthError(Exception):
    """`key` is an i18n key (see core.i18n), translated by the screen that shows it."""

    def __init__(self, key: str) -> None:
        super().__init__(key)
        self.key = key


Observer = Callable[[User | None], None]


class AuthService(ABC):
    def __init__(self) -> None:
        self._user: User | None = None
        self._observers: list[Observer] = []

    @property
    def current_user(self) -> User | None:
        return self._user

    def on_change(self, observer: Observer) -> None:
        self._observers.append(observer)

    def _set_user(self, user: User | None) -> None:
        self._user = user
        for observer in list(self._observers):
            observer(user)

    @staticmethod
    def validate_email(email: str) -> str:
        email = (email or "").strip().lower()
        if not _EMAIL.match(email):
            raise AuthError("auth.invalid_email")
        return email

    @classmethod
    def validate(cls, email: str, password: str) -> tuple[str, str]:
        email = cls.validate_email(email)
        if len(password or "") < 6:
            raise AuthError("auth.short_password")
        return email, password

    @abstractmethod
    def sign_in_email(self, email: str, password: str) -> User: ...

    @abstractmethod
    def sign_up_email(self, email: str, password: str) -> User: ...

    @abstractmethod
    def sign_in_google(self, page: Any) -> User | None:
        """Returns None if the user cancels. `page` allows using Flet's `page.login()`."""

    @abstractmethod
    def send_password_reset(self, email: str) -> None:
        """Sends the reset link. Must not reveal whether the account exists."""

    def sign_out(self) -> None:
        self._set_user(None)
