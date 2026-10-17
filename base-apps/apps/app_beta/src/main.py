from app_config import CONFIG
from screens import build_app, login_screen

from core import run_app

# App Beta replaces the default login screen with its own.
run_app(CONFIG, build_app, build_login=login_screen)
