from config_app import CONFIG
from telas import montar_app

from nucleo import iniciar_app

# Idiomas usa a tela de login padrão do núcleo.
iniciar_app(CONFIG, montar_app)
