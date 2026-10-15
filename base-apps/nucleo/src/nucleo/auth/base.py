"""Interface de autenticação. A navegação reage a `ao_mudar`, nunca ao retorno
de um botão, então login com erro ou cancelado não leva para a home."""

from __future__ import annotations

import re
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Callable

_EMAIL = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


@dataclass(frozen=True)
class Usuario:
    id: str
    email: str
    nome: str = ""
    provedor: str = "email"


class ErroAuth(Exception):
    pass


Observador = Callable[[Usuario | None], None]


class ServicoAuth(ABC):
    def __init__(self) -> None:
        self._usuario: Usuario | None = None
        self._observadores: list[Observador] = []

    @property
    def usuario_atual(self) -> Usuario | None:
        return self._usuario

    def ao_mudar(self, observador: Observador) -> None:
        self._observadores.append(observador)

    def _definir_usuario(self, usuario: Usuario | None) -> None:
        self._usuario = usuario
        for observador in list(self._observadores):
            observador(usuario)

    @staticmethod
    def validar(email: str, senha: str) -> tuple[str, str]:
        email = (email or "").strip().lower()
        if not _EMAIL.match(email):
            raise ErroAuth("Email inválido.")
        if len(senha or "") < 6:
            raise ErroAuth("A senha precisa ter pelo menos 6 caracteres.")
        return email, senha

    @abstractmethod
    def entrar_email(self, email: str, senha: str) -> Usuario: ...

    @abstractmethod
    def cadastrar_email(self, email: str, senha: str) -> Usuario: ...

    @abstractmethod
    def entrar_google(self, page: Any) -> Usuario | None:
        """Retorna None se o usuário cancelar. `page` permite usar `page.login()` do Flet."""

    def sair(self) -> None:
        self._definir_usuario(None)
