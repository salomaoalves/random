"""Contract each child app fills in. Everything that varies between apps comes from here."""

from __future__ import annotations

from dataclasses import dataclass, field

from .i18n import Catalog


@dataclass(frozen=True)
class Theme:
    background_color: str = "#0F172A"
    primary_color: str = "#3B82F6"
    text_color: str = "#FFFFFF"
    surface_color: str = "#1E293B"
    dark: bool = True


@dataclass(frozen=True)
class Logo:
    """Use `src` (URL or file in src/assets) or, without an image, a Flet icon name."""

    src: str = ""
    icon: str = "apps"
    width: int = 120
    height: int = 120


@dataclass(frozen=True)
class FooterLink:
    label: str  # text or i18n key
    url: str


@dataclass(frozen=True)
class Footer:
    text: str  # text or i18n key
    links: tuple[FooterLink, ...] = ()


@dataclass(frozen=True)
class DataConfig:
    """Same database for every app; only the instance/credential changes.

    `provider` picks the implementation registered in `core.data`.
    Until the database is chosen, use "memory".
    """

    provider: str = "memory"
    project: str = ""
    url: str = ""
    key: str = ""
    extras: dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class AuthConfig:
    provider: str = "memory"
    google_client_id: str = ""
    google_client_secret: str = ""
    extras: dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class AppConfig:
    name: str
    theme: Theme
    logo: Logo
    footer: Footer
    data: DataConfig = field(default_factory=DataConfig)
    auth: AuthConfig = field(default_factory=AuthConfig)
    strings: Catalog = field(default_factory=dict)  # the app's own texts, merged over the core ones
