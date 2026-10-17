"""In-memory implementation, for development while the database is not chosen."""

from __future__ import annotations

import copy
import uuid
from datetime import datetime, timezone
from typing import Any

from .base import DataError, Record, Repository


class MemoryRepository(Repository):
    def __init__(self, namespace: str = "default") -> None:
        self.namespace = namespace
        self._collections: dict[str, dict[str, Record]] = {}

    def _collection(self, name: str) -> dict[str, Record]:
        return self._collections.setdefault(name, {})

    def list(self, collection: str, filters: dict[str, Any] | None = None) -> list[Record]:
        items = self._collection(collection).values()
        if filters:
            items = [i for i in items if all(i.get(k) == v for k, v in filters.items())]
        return sorted((copy.deepcopy(i) for i in items), key=lambda i: i["created_at"])

    def get(self, collection: str, id_: str) -> Record | None:
        item = self._collection(collection).get(id_)
        return copy.deepcopy(item) if item else None

    def create(self, collection: str, data: Record) -> Record:
        id_ = str(uuid.uuid4())
        item = {**copy.deepcopy(data), "id": id_, "created_at": datetime.now(timezone.utc).isoformat()}
        self._collection(collection)[id_] = item
        return copy.deepcopy(item)

    def update(self, collection: str, id_: str, data: Record) -> Record:
        current = self._collection(collection).get(id_)
        if current is None:
            raise DataError(f"Record {id_} not found in {collection}")
        current.update({k: v for k, v in copy.deepcopy(data).items() if k not in ("id", "created_at")})
        return copy.deepcopy(current)

    def delete(self, collection: str, id_: str) -> None:
        if self._collection(collection).pop(id_, None) is None:
            raise DataError(f"Record {id_} not found in {collection}")
