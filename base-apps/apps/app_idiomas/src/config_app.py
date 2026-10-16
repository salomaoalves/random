import os

from nucleo import AppConfig, ConfigAuth, ConfigDados, LinkRodape, Logo, Rodape, Tema

# Paleta preto/verde neon. Para a alternativa branco/azul:
#   Tema(cor_fundo="#FFFFFF", cor_primaria="#2563EB", cor_texto="#0F172A", cor_superficie="#EFF6FF", escuro=False)
CONFIG = AppConfig(
    nome="Idiomas",
    tema=Tema(cor_fundo="#050505", cor_primaria="#39FF14", cor_texto="#F5F5F5", cor_superficie="#141414",
              cor_sobre_primaria="#000000"),
    # Com o arquivo em src/assets/logotipo.png, troque por Logo(src="logotipo.png", ...).
    logo=Logo(icone="translate", largura=110, altura=110),
    rodape=Rodape(
        texto="© 2026 Idiomas. Todos os direitos reservados.",
        links=(LinkRodape("Termos de uso", "https://exemplo.com/idiomas/termos"),),
    ),
    dados=ConfigDados(provedor="memoria", projeto="app-idiomas", url=os.getenv("IDIOMAS_DB_URL", ""),
                      chave=os.getenv("IDIOMAS_DB_CHAVE", "")),
    auth=ConfigAuth(provedor="memoria", google_client_id=os.getenv("IDIOMAS_GOOGLE_CLIENT_ID", "")),
)
