"""nucleo — pacote pai compartilhado pelos apps filhos."""

from .app import Contexto, criar_main, iniciar_app
from .auth import ErroAuth, ServicoAuth, Usuario
from .config import AppConfig, ConfigAuth, ConfigDados, LinkRodape, Logo, Rodape, Tema
from .dados import Registro, Repositorio
from .ui import FormularioLogin, componentes, tela_login_padrao

__all__ = [
    "AppConfig", "ConfigAuth", "ConfigDados", "Contexto", "ErroAuth", "FormularioLogin", "LinkRodape",
    "Logo", "Registro", "Repositorio", "Rodape", "ServicoAuth", "Tema", "Usuario", "componentes",
    "criar_main", "iniciar_app", "tela_login_padrao",
]
