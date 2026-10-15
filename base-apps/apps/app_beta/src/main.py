from config_app import CONFIG
from telas import montar_app, tela_login

from nucleo import iniciar_app

# App Beta substitui a tela de login padrão pela própria.
iniciar_app(CONFIG, montar_app, montar_login=tela_login)
