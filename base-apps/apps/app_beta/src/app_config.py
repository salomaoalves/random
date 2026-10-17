import os

from core import AppConfig, AuthConfig, DataConfig, Footer, FooterLink, Logo, Theme
from strings import STRINGS

CONFIG = AppConfig(
    name="App Beta",
    theme=Theme(background_color="#111827", primary_color="#22C55E", text_color="#F9FAFB", surface_color="#1F2937"),
    logo=Logo(icon="dashboard", width=90, height=90),
    footer=Footer(
        text="© 2026 App Beta",
        links=(FooterLink("footer.privacy", "https://example.com/beta/privacy"),
               FooterLink("footer.support", "https://example.com/beta/support")),
    ),
    data=DataConfig(provider="memory", project="app-beta", url=os.getenv("BETA_DB_URL", ""),
                    key=os.getenv("BETA_DB_KEY", "")),
    auth=AuthConfig(provider="memory", google_client_id=os.getenv("BETA_GOOGLE_CLIENT_ID", "")),
    strings=STRINGS,
)
