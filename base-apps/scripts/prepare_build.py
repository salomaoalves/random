"""Copies the core package into apps/<app>/src before `flet build`.

Usage:
    python scripts/prepare_build.py app_alpha
    cd apps/app_alpha && flet build apk     # or: flet build ipa
"""

import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def main() -> None:
    if len(sys.argv) != 2:
        sys.exit("Usage: python scripts/prepare_build.py <app_name>")
    target = ROOT / "apps" / sys.argv[1] / "src" / "core"
    if not target.parent.is_dir():
        sys.exit(f"App not found: {target.parent.parent}")
    if target.exists():
        shutil.rmtree(target)
    shutil.copytree(ROOT / "core" / "src" / "core", target,
                    ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    print(f"core copied to {target.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
