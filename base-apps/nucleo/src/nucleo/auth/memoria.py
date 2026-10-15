"""Auth em memória para desenvolvimento. Não usar em produção."""

from __future__ import annotations

import hashlib
import os
import uuid
from typing import Any

from .base import ErroAuth, ServicoAuth, Usuario


class AuthMemoria(ServicoAuth):
    def __init__(self) -> None:
        super().__init__()
        self._contas: dict[str, tuple[bytes, bytes, Usuario]] = {}

    @staticmethod
    def _hash(senha: str, sal: bytes) -> bytes:
        return hashlib.pbkdf2_hmac("sha256", senha.encode(), sal, 100_000)

    def cadastrar_email(self, email: str, senha: str) -> Usuario:
        email, senha = self.validar(email, senha)
        if email in self._contas:
            raise ErroAuth("Já existe uma conta com esse email.")
        sal = os.urandom(16)
        usuario = Usuario(id=str(uuid.uuid4()), email=email)
        self._contas[email] = (sal, self._hash(senha, sal), usuario)
        self._definir_usuario(usuario)
        return usuario

    def entrar_email(self, email: str, senha: str) -> Usuario:
        email, senha = self.validar(email, senha)
        conta = self._contas.get(email)
        if conta is None or self._hash(senha, conta[0]) != conta[1]:
            raise ErroAuth("Email ou senha incorretos.")
        self._definir_usuario(conta[2])
        return conta[2]

    def entrar_google(self, page: Any) -> Usuario | None:
        usuario = Usuario(id="google-dev", email="dev@gmail.com", nome="Usuário Google (dev)", provedor="google")
        self._definir_usuario(usuario)
        return usuario
