"""In-memory auth for development. Do not use in production."""

from __future__ import annotations

import hashlib
import os
import uuid
from typing import Any

from .base import AuthError, AuthService, User


class MemoryAuth(AuthService):
    def __init__(self) -> None:
        super().__init__()
        self._accounts: dict[str, tuple[bytes, bytes, User]] = {}
        self.sent_password_resets: list[str] = []  # stands in for the outgoing email box

    @staticmethod
    def _hash(password: str, salt: bytes) -> bytes:
        return hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 100_000)

    def sign_up_email(self, email: str, password: str) -> User:
        email, password = self.validate(email, password)
        if email in self._accounts:
            raise AuthError("auth.email_taken")
        salt = os.urandom(16)
        user = User(id=str(uuid.uuid4()), email=email)
        self._accounts[email] = (salt, self._hash(password, salt), user)
        self._set_user(user)
        return user

    def sign_in_email(self, email: str, password: str) -> User:
        email, password = self.validate(email, password)
        account = self._accounts.get(email)
        if account is None or self._hash(password, account[0]) != account[1]:
            raise AuthError("auth.wrong_credentials")
        self._set_user(account[2])
        return account[2]

    def send_password_reset(self, email: str) -> None:
        email = self.validate_email(email)
        if email in self._accounts:
            self.sent_password_resets.append(email)

    def sign_in_google(self, page: Any) -> User | None:
        user = User(id="google-dev", email="dev@gmail.com", name="Google user (dev)", provider="google")
        self._set_user(user)
        return user
