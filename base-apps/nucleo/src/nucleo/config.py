"""Contrato que cada app filho preenche. Tudo que varia entre apps vem daqui."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Tema:
    cor_fundo: str = "#0F172A"
    cor_primaria: str = "#3B82F6"
    cor_texto: str = "#FFFFFF"
    cor_superficie: str = "#1E293B"
    escuro: bool = True


@dataclass(frozen=True)
class Logo:
    """Use `src` (URL ou arquivo em src/assets) ou, sem imagem, um ícone do Flet."""

    src: str = ""
    icone: str = "apps"
    largura: int = 120
    altura: int = 120


@dataclass(frozen=True)
class LinkRodape:
    rotulo: str
    url: str


@dataclass(frozen=True)
class Rodape:
    texto: str
    links: tuple[LinkRodape, ...] = ()


@dataclass(frozen=True)
class ConfigDados:
    """Mesmo banco em todos os apps; muda só a instância/credencial.

    `provedor` escolhe a implementação registrada em `nucleo.dados`.
    Enquanto o banco não é definido, use "memoria".
    """

    provedor: str = "memoria"
    projeto: str = ""
    url: str = ""
    chave: str = ""
    extras: dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class ConfigAuth:
    provedor: str = "memoria"
    google_client_id: str = ""
    google_client_secret: str = ""
    extras: dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class AppConfig:
    nome: str
    tema: Tema
    logo: Logo
    rodape: Rodape
    dados: ConfigDados = field(default_factory=ConfigDados)
    auth: ConfigAuth = field(default_factory=ConfigAuth)
