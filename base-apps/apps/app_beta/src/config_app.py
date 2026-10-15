import os

from nucleo import AppConfig, ConfigAuth, ConfigDados, LinkRodape, Logo, Rodape, Tema

CONFIG = AppConfig(
    nome="App Beta",
    tema=Tema(cor_fundo="#111827", cor_primaria="#22C55E", cor_texto="#F9FAFB", cor_superficie="#1F2937"),
    logo=Logo(icone="dashboard", largura=90, altura=90),
    rodape=Rodape(
        texto="© 2026 App Beta",
        links=(LinkRodape("Privacidade", "https://exemplo.com/beta/privacidade"),
               LinkRodape("Suporte", "https://exemplo.com/beta/suporte")),
    ),
    dados=ConfigDados(provedor="memoria", projeto="app-beta", url=os.getenv("BETA_DB_URL", ""),
                      chave=os.getenv("BETA_DB_CHAVE", "")),
    auth=ConfigAuth(provedor="memoria", google_client_id=os.getenv("BETA_GOOGLE_CLIENT_ID", "")),
)
