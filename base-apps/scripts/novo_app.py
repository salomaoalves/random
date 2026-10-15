"""Cria um novo app filho copiando um existente.

Uso:
    python scripts/novo_app.py app_gama "App Gama"
    python scripts/novo_app.py app_gama "App Gama" --base app_beta
"""

import argparse
import re
import shutil
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("pasta", help="nome da pasta, ex.: app_gama")
    p.add_argument("nome", help='nome exibido, ex.: "App Gama"')
    p.add_argument("--base", default="app_alfa", help="app a copiar (padrão: app_alfa)")
    a = p.parse_args()

    if not re.fullmatch(r"[a-z][a-z0-9_]*", a.pasta):
        raise SystemExit("Use só letras minúsculas, números e _ no nome da pasta.")
    origem, destino = RAIZ / "apps" / a.base, RAIZ / "apps" / a.pasta
    if destino.exists():
        raise SystemExit(f"{destino} já existe.")
    shutil.copytree(origem, destino, ignore=shutil.ignore_patterns("__pycache__", "build", "nucleo"))

    nome_base = re.search(r'nome="([^"]+)"', (origem / "src" / "config_app.py").read_text()).group(1)
    prefixo_base, prefixo = a.base.removeprefix("app_").upper(), a.pasta.removeprefix("app_").upper()
    slug_base, slug = a.base.replace("_", "-"), a.pasta.replace("_", "-")

    for arquivo in (destino / "pyproject.toml", destino / "src" / "config_app.py", destino / "src" / "main.py"):
        texto = arquivo.read_text()
        texto = texto.replace(nome_base, a.nome).replace(slug_base, slug).replace(f"{prefixo_base}_", f"{prefixo}_")
        arquivo.write_text(texto)

    print(f"Criado {destino.relative_to(RAIZ)}. Edite src/config_app.py (tema, logo, rodapé, credenciais)"
          " e src/telas.py (layout).")


if __name__ == "__main__":
    main()
