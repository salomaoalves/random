"""Data layer. When the database is chosen, create `data/<provider>.py`
with a `Repository` subclass and register it in `_PROVIDERS`."""

from __future__ import annotations

from typing import Callable

from ..config import AppConfig
from .base import DataError, Record, Repository
from .memory import MemoryRepository

_PROVIDERS: dict[str, Callable[[AppConfig], Repository]] = {
    "memory": lambda cfg: MemoryRepository(namespace=cfg.data.project or cfg.name),
}


def register_provider(name: str, factory: Callable[[AppConfig], Repository]) -> None:
    _PROVIDERS[name] = factory


def create_repository(config: AppConfig) -> Repository:
    try:
        return _PROVIDERS[config.data.provider](config)
    except KeyError:
        raise DataError(f"Unknown data provider: {config.data.provider!r}") from None


__all__ = ["DataError", "MemoryRepository", "Record", "Repository", "create_repository", "register_provider"]
