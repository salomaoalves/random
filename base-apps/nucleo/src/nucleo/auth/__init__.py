"""Autenticação. Para o provedor real, crie `auth/<provedor>.py` com uma
subclasse de `ServicoAuth` e registre-a em `_PROVEDORES`."""

from __future__ import annotations

from typing import Callable

from ..config import AppConfig
from .base import ErroAuth, ServicoAuth, Usuario
from .memoria import AuthMemoria

_PROVEDORES: dict[str, Callable[[AppConfig], ServicoAuth]] = {
    "memoria": lambda cfg: AuthMemoria(),
}


def registrar_provedor(nome: str, fabrica: Callable[[AppConfig], ServicoAuth]) -> None:
    _PROVEDORES[nome] = fabrica


def criar_auth(config: AppConfig) -> ServicoAuth:
    try:
        return _PROVEDORES[config.auth.provedor](config)
    except KeyError:
        raise ErroAuth(f"Provedor de auth desconhecido: {config.auth.provedor!r}") from None


__all__ = ["AuthMemoria", "ErroAuth", "ServicoAuth", "Usuario", "criar_auth", "registrar_provedor"]
