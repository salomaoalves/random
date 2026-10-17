from app_config import CONFIG
from screens import build_app

from core import run_app

# App Alpha uses the core's default login screen.
run_app(CONFIG, build_app)
