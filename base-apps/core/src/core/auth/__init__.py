"""Authentication. For the real provider, create `auth/<provider>.py` with an
`AuthService` subclass and register it in `_PROVIDERS`."""

from __future__ import annotations

from typing import Callable

from ..config import AppConfig
from .base import AuthError, AuthService, User
from .memory import MemoryAuth

_PROVIDERS: dict[str, Callable[[AppConfig], AuthService]] = {
    "memory": lambda cfg: MemoryAuth(),
}


def register_provider(name: str, factory: Callable[[AppConfig], AuthService]) -> None:
    _PROVIDERS[name] = factory


def create_auth(config: AppConfig) -> AuthService:
    try:
        return _PROVIDERS[config.auth.provider](config)
    except KeyError:
        raise ValueError(f"Unknown auth provider: {config.auth.provider!r}") from None


__all__ = ["AuthError", "AuthService", "MemoryAuth", "User", "create_auth", "register_provider"]
