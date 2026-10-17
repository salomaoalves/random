"""Single data interface. The child apps' screens only know this class."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

Record = dict[str, Any]


class DataError(Exception):
    pass


class Repository(ABC):
    """Generic CRUD per collection (a table in SQL, a collection in Firestore, etc.)."""

    @abstractmethod
    def list(self, collection: str, filters: dict[str, Any] | None = None) -> list[Record]: ...

    @abstractmethod
    def get(self, collection: str, id_: str) -> Record | None: ...

    @abstractmethod
    def create(self, collection: str, data: Record) -> Record: ...

    @abstractmethod
    def update(self, collection: str, id_: str, data: Record) -> Record: ...

    @abstractmethod
    def delete(self, collection: str, id_: str) -> None: ...
