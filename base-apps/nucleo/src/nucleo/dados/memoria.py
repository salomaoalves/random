"""Implementação em memória, para desenvolver enquanto o banco não é definido."""

from __future__ import annotations

import copy
import uuid
from datetime import datetime, timezone
from typing import Any

from .base import ErroDados, Registro, Repositorio


class RepositorioMemoria(Repositorio):
    def __init__(self, namespace: str = "padrao") -> None:
        self.namespace = namespace
        self._colecoes: dict[str, dict[str, Registro]] = {}

    def _colecao(self, nome: str) -> dict[str, Registro]:
        return self._colecoes.setdefault(nome, {})

    def listar(self, colecao: str, filtros: dict[str, Any] | None = None) -> list[Registro]:
        itens = self._colecao(colecao).values()
        if filtros:
            itens = [i for i in itens if all(i.get(k) == v for k, v in filtros.items())]
        return sorted((copy.deepcopy(i) for i in itens), key=lambda i: i["criado_em"])

    def obter(self, colecao: str, id_: str) -> Registro | None:
        item = self._colecao(colecao).get(id_)
        return copy.deepcopy(item) if item else None

    def criar(self, colecao: str, dados: Registro) -> Registro:
        id_ = str(uuid.uuid4())
        item = {**copy.deepcopy(dados), "id": id_, "criado_em": datetime.now(timezone.utc).isoformat()}
        self._colecao(colecao)[id_] = item
        return copy.deepcopy(item)

    def atualizar(self, colecao: str, id_: str, dados: Registro) -> Registro:
        atual = self._colecao(colecao).get(id_)
        if atual is None:
            raise ErroDados(f"Registro {id_} não encontrado em {colecao}")
        atual.update({k: v for k, v in copy.deepcopy(dados).items() if k not in ("id", "criado_em")})
        return copy.deepcopy(atual)

    def remover(self, colecao: str, id_: str) -> None:
        if self._colecao(colecao).pop(id_, None) is None:
            raise ErroDados(f"Registro {id_} não encontrado em {colecao}")
