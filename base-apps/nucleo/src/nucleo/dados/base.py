"""Interface única de dados. As telas dos filhos só conhecem esta classe."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

Registro = dict[str, Any]


class ErroDados(Exception):
    pass


class Repositorio(ABC):
    """CRUD genérico por coleção (tabela no SQL, coleção no Firestore etc.)."""

    @abstractmethod
    def listar(self, colecao: str, filtros: dict[str, Any] | None = None) -> list[Registro]: ...

    @abstractmethod
    def obter(self, colecao: str, id_: str) -> Registro | None: ...

    @abstractmethod
    def criar(self, colecao: str, dados: Registro) -> Registro: ...

    @abstractmethod
    def atualizar(self, colecao: str, id_: str, dados: Registro) -> Registro: ...

    @abstractmethod
    def remover(self, colecao: str, id_: str) -> None: ...
