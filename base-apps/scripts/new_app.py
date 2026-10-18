"""Creates a new child app by copying an existing one.

Usage:
    python scripts/new_app.py app_gamma "App Gamma"
    python scripts/new_app.py app_gamma "App Gamma" --base app_beta
"""

import argparse
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("folder", help="folder name, e.g. app_gamma")
    p.add_argument("name", help='display name, e.g. "App Gamma"')
    p.add_argument("--base", default="app_alpha", help="app to copy (default: app_alpha)")
    a = p.parse_args()

    if not re.fullmatch(r"[a-z][a-z0-9_]*", a.folder):
        raise SystemExit("Use only lowercase letters, digits and _ in the folder name.")
    source, target = ROOT / "apps" / a.base, ROOT / "apps" / a.folder
    if target.exists():
        raise SystemExit(f"{target} already exists.")
    shutil.copytree(source, target, ignore=shutil.ignore_patterns("__pycache__", "build", "core"))

    base_name = re.search(r'name="([^"]+)"', (source / "src" / "app_config.py").read_text()).group(1)
    base_prefix, prefix = a.base.removeprefix("app_").upper(), a.folder.removeprefix("app_").upper()
    base_slug, slug = a.base.replace("_", "-"), a.folder.replace("_", "-")
    base_path, path = a.base.removeprefix("app_"), a.folder.removeprefix("app_")

    src = target / "src"
    for file in (target / "pyproject.toml", src / "app_config.py", src / "main.py", src / "strings.py"):
        if not file.exists():
            continue
        text = file.read_text()
        text = (text.replace(base_name, a.name).replace(base_slug, slug).replace(f"{base_prefix}_", f"{prefix}_")
                .replace(f"/{base_path}/", f"/{path}/"))
        file.write_text(text)

    print(f"Created {target.relative_to(ROOT)}. Edit src/app_config.py (theme, logo, footer, credentials),"
          " src/strings.py (texts) and src/screens.py (layout).")


if __name__ == "__main__":
    main()
