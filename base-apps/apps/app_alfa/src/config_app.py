import os

from nucleo import AppConfig, ConfigAuth, ConfigDados, LinkRodape, Logo, Rodape, Tema

CONFIG = AppConfig(
    nome="App Alfa",
    tema=Tema(cor_fundo="#0F172A", cor_primaria="#3B82F6", cor_texto="#FFFFFF", cor_superficie="#1E293B"),
    logo=Logo(icone="apps", largura=110, altura=110),
    rodape=Rodape(
        texto="© 2026 App Alfa. Todos os direitos reservados.",
        links=(LinkRodape("Termos de uso", "https://exemplo.com/alfa/termos"),),
    ),
    dados=ConfigDados(provedor="memoria", projeto="app-alfa", url=os.getenv("ALFA_DB_URL", ""),
                      chave=os.getenv("ALFA_DB_CHAVE", "")),
    auth=ConfigAuth(provedor="memoria", google_client_id=os.getenv("ALFA_GOOGLE_CLIENT_ID", "")),
)
