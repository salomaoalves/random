import os

from core import AppConfig, AuthConfig, DataConfig, Footer, FooterLink, Logo, Theme
from strings import STRINGS

# Black/neon green palette. For the white/blue alternative:
#   Theme(background_color="#FFFFFF", primary_color="#2563EB", text_color="#0F172A",
#         surface_color="#EFF6FF", dark=False)
CONFIG = AppConfig(
    name="Bheh",
    theme=Theme(background_color="#050505", primary_color="#39FF14", text_color="#F5F5F5",
                surface_color="#141414", on_primary_color="#000000"),
    # With the file in src/assets/logotipo.png, use Logo(src="logotipo.png", ...).
    logo=Logo(icon="translate", width=110, height=110),
    footer=Footer(
        text="footer.text",
        links=(FooterLink("footer.terms", "https://example.com/bheh/terms"),),
    ),
    data=DataConfig(provider="memory", project="app-bheh", url=os.getenv("BHEH_DB_URL", ""),
                    key=os.getenv("BHEH_DB_KEY", "")),
    auth=AuthConfig(provider="memory", google_client_id=os.getenv("BHEH_GOOGLE_CLIENT_ID", "")),
    strings=STRINGS,
)
