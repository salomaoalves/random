"""Camada de dados. Quando o banco for definido, crie `dados/<provedor>.py`
com uma subclasse de `Repositorio` e registre-a em `_PROVEDORES`."""

from __future__ import annotations

from typing import Callable

from ..config import AppConfig
from .base import ErroDados, Registro, Repositorio
from .memoria import RepositorioMemoria

_PROVEDORES: dict[str, Callable[[AppConfig], Repositorio]] = {
    "memoria": lambda cfg: RepositorioMemoria(namespace=cfg.dados.projeto or cfg.nome),
}


def registrar_provedor(nome: str, fabrica: Callable[[AppConfig], Repositorio]) -> None:
    _PROVEDORES[nome] = fabrica


def criar_repositorio(config: AppConfig) -> Repositorio:
    try:
        return _PROVEDORES[config.dados.provedor](config)
    except KeyError:
        raise ErroDados(f"Provedor de dados desconhecido: {config.dados.provedor!r}") from None


__all__ = ["ErroDados", "Registro", "Repositorio", "RepositorioMemoria", "criar_repositorio", "registrar_provedor"]
