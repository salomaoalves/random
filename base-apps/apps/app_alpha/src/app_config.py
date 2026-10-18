import os

from core import AppConfig, AuthConfig, DataConfig, Footer, FooterLink, Logo, Theme
from strings import STRINGS

CONFIG = AppConfig(
    name="App Alpha",
    theme=Theme(background_color="#0F172A", primary_color="#3B82F6", text_color="#FFFFFF", surface_color="#1E293B"),
    logo=Logo(icon="apps", width=110, height=110),
    footer=Footer(
        text="footer.text",
        links=(FooterLink("footer.terms", "https://example.com/alpha/terms"),),
    ),
    data=DataConfig(provider="memory", project="app-alpha", url=os.getenv("ALPHA_DB_URL", ""),
                    key=os.getenv("ALPHA_DB_KEY", "")),
    auth=AuthConfig(provider="memory", google_client_id=os.getenv("ALPHA_GOOGLE_CLIENT_ID", "")),
    strings=STRINGS,
)
