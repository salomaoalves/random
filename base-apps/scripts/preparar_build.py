"""Copia o nucleo para dentro de apps/<app>/src antes do `flet build`.

Uso:
    python scripts/preparar_build.py app_alfa
    cd apps/app_alfa && flet build apk     # ou: flet build ipa
"""

import shutil
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent


def main() -> None:
    if len(sys.argv) != 2:
        sys.exit("Uso: python scripts/preparar_build.py <nome_do_app>")
    destino = RAIZ / "apps" / sys.argv[1] / "src" / "nucleo"
    if not destino.parent.is_dir():
        sys.exit(f"App não encontrado: {destino.parent.parent}")
    if destino.exists():
        shutil.rmtree(destino)
    shutil.copytree(RAIZ / "nucleo" / "src" / "nucleo", destino,
                    ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    print(f"nucleo copiado para {destino.relative_to(RAIZ)}")


if __name__ == "__main__":
    main()
