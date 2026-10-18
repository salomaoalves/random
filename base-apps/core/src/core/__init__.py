"""core — parent package shared by the child apps."""

from .app import Context, create_main, run_app
from .auth import AuthError, AuthService, User
from .config import AppConfig, AuthConfig, DataConfig, Footer, FooterLink, Logo, Theme
from .data import Record, Repository
from .i18n import Translator
from .ui import LoginForm, components, default_login_screen

__all__ = [
    "AppConfig", "AuthConfig", "AuthError", "AuthService", "Context", "DataConfig", "Footer", "FooterLink",
    "LoginForm", "Logo", "Record", "Repository", "Theme", "Translator", "User", "components", "create_main",
    "default_login_screen", "run_app",
]
