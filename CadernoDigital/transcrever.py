"""Lê as fotos de anotações em imagens/ e gera um .docx (para o Google Docs)
mantendo títulos, parágrafos, listas, negrito, sublinhado, destaques e diagramas.

    python transcrever.py
    python transcrever.py --pasta fotos/aula3 --saida saida/aula3.docx --titulo "Aula 3"
"""
import argparse
import base64
import hashlib
import io
import re
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import anthropic
from PIL import Image, ImageOps

import gerar_docx
from modelo import Pagina

try:  # fotos .heic do iPhone (opcional: pip install pillow-heif)
    from pillow_heif import register_heif_opener
    register_heif_opener()
except ImportError:
    pass

MODELO = "claude-opus-5-5"
EXTENSOES = {".jpg", ".jpeg", ".png", ".webp", ".gif", ".bmp", ".tif", ".tiff", ".heic", ".heif"}
LADO_MAX = 2576           # px do maior lado enviado ao Claude
TAMANHO_MAX = 4_500_000   # bytes (limite da API é 5 MB por imagem)
PASTA_CACHE = Path(__file__).parent / ".cache"

PROMPT = """Esta é a foto de uma página de caderno/anotações (escrita à mão ou impressa, \
podendo ter desenhos e diagramas). Transcreva TUDO o que estiver nela para a estrutura pedida, \
reproduzindo o layout do caderno o mais fielmente possível.

Regras:
- Transcreva fielmente, no idioma original. Não traduza, não resuma, não reescreva. \
Corrija só o que for claramente um erro de leitura seu, não do autor.
- Siga a ordem de leitura da página (de cima para baixo; colunas da esquerda para a direita; \
notas na margem logo depois do trecho a que se referem).
- Um bloco por título, parágrafo, item de lista, tabela ou desenho. Uma quebra de linha que é só \
fim da largura da folha NÃO cria bloco novo; um parágrafo novo, sim.
- titulo: textos maiores, sublinhados sozinhos na linha ou que claramente abrem uma seção. \
nivel 1 = título principal, 2 = subtítulo, 3 = sub-subtítulo.
- Listas: use nivel para o recuo (0 = sem recuo, 1 = subitem, ...) e copie o marcador como \
foi escrito em `marcador` ("1.", "a)", "•", "-", "→", "☐" para caixinha vazia, "☑" para marcada). \
Parágrafos recuados também usam nivel.
- Formatação por trecho: negrito para letras reforçadas/mais grossas ou em caixa-alta de ênfase, \
sublinhado para o que foi sublinhado, riscado para o que foi riscado, destaque para marca-texto, \
texto circulado ou dentro de um quadro, italico só se for claramente inclinado de propósito. \
Use `cor` (hex) apenas para canetas coloridas diferentes da tinta principal.
- tabela: preencha `tabela` com as linhas (a primeira é o cabeçalho).
- diagrama: para desenhos, esquemas, fluxogramas, mapas mentais, gráficos e figuras. \
Descreva em `descricao` o que é e como os elementos se ligam (setas, hierarquia), liste em `textos` \
tudo o que está escrito dentro dele e marque em `caixa` o retângulo que envolve o desenho inteiro, \
em frações da largura/altura da foto (0 a 1). Texto corrido ao redor do desenho NÃO faz parte dele.
- separador: linhas horizontais traçadas para separar assuntos.
- Palavras que não der para ler: escreva [ilegível] no lugar e comente em `observacoes`.
- Ignore o que não é conteúdo: pauta, espiral, margem impressa, sombras, dedos, a mesa."""


def chave_natural(caminho: Path):
    """pagina2 vem antes de pagina10."""
    return [int(p) if p.isdigit() else p.lower() for p in re.split(r"(\d+)", caminho.name)]


def abrir_imagem(caminho: Path) -> Image.Image:
    imagem = Image.open(caminho)
    # Fotos de celular vêm deitadas com a rotação só no EXIF.
    return ImageOps.exif_transpose(imagem).convert("RGB")


def preparar_para_envio(imagem: Image.Image) -> str:
    copia = imagem.copy()
    copia.thumbnail((LADO_MAX, LADO_MAX))
    for qualidade in (90, 80, 70, 60):
        buffer = io.BytesIO()
        copia.save(buffer, "JPEG", quality=qualidade)
        if buffer.tell() <= TAMANHO_MAX:
            break
    return base64.standard_b64encode(buffer.getvalue()).decode("utf-8")


def transcrever(client: anthropic.Anthropic, caminho: Path, imagem: Image.Image, usar_cache: bool) -> Pagina:
    chave = hashlib.sha256(caminho.read_bytes() + MODELO.encode() + PROMPT.encode()).hexdigest()[:32]
    arquivo_cache = PASTA_CACHE / f"{chave}.json"
    if usar_cache and arquivo_cache.exists():
        return Pagina.model_validate_json(arquivo_cache.read_text(encoding="utf-8"))

    resposta = client.beta.messages.parse(
        model=MODELO,
        max_tokens=20000,
        output_config={"effort": "high"},
        betas=["server-side-fallback-2026-07-01"],
        fallbacks="default",
        output_format=Pagina,
        messages=[{
            "role": "user",
            "content": [
                {"type": "image", "source": {"type": "base64", "media_type": "image/jpeg",
                                             "data": preparar_para_envio(imagem)}},
                {"type": "text", "text": PROMPT},
            ],
        }],
    )
    if resposta.stop_reason == "refusal":
        raise RuntimeError("o modelo recusou a imagem")
    if resposta.stop_reason == "max_tokens":
        raise RuntimeError("resposta cortada (página longa demais); tente dividir a foto")
    pagina = resposta.parsed_output
    if pagina is None:
        raise RuntimeError("resposta sem conteúdo estruturado")

    PASTA_CACHE.mkdir(exist_ok=True)
    arquivo_cache.write_text(pagina.model_dump_json(indent=2), encoding="utf-8")
    return pagina


def main():
    base = Path(__file__).parent
    parser = argparse.ArgumentParser(description="Transcreve fotos de anotações para um .docx (Google Docs).")
    parser.add_argument("--pasta", type=Path, default=base / "imagens", help="pasta com as fotos (padrão: imagens/)")
    parser.add_argument("--saida", type=Path, default=base / "saida" / "anotacoes.docx", help="arquivo .docx gerado")
    parser.add_argument("--titulo", help="título no topo do documento")
    parser.add_argument("--diagramas", choices=["ambos", "imagem", "descricao"], default="ambos",
                        help="desenhos: recorte da foto, descrição em texto ou os dois (padrão)")
    parser.add_argument("--quebra-de-pagina", action="store_true", help="cada foto começa numa página nova")
    parser.add_argument("--mostrar-origem", action="store_true", help="anota o nome da foto antes de cada trecho")
    parser.add_argument("--paralelo", type=int, default=4, help="fotos processadas ao mesmo tempo (padrão: 4)")
    parser.add_argument("--sem-cache", action="store_true", help="ignora transcrições já salvas e refaz tudo")
    args = parser.parse_args()

    fotos = sorted((p for p in args.pasta.iterdir() if p.suffix.lower() in EXTENSOES), key=chave_natural) \
        if args.pasta.is_dir() else []
    if not fotos:
        sys.exit(f"Nenhuma imagem encontrada em {args.pasta}")
    print(f"{len(fotos)} foto(s) em {args.pasta}")

    client = anthropic.Anthropic()
    imagens = {}

    def processar(caminho):
        imagem = abrir_imagem(caminho)
        imagens[caminho] = imagem
        pagina = transcrever(client, caminho, imagem, usar_cache=not args.sem_cache)
        print(f"  ok  {caminho.name} ({len(pagina.blocos)} blocos)")
        return pagina

    def seguro(caminho):
        try:
            return processar(caminho)
        except (anthropic.APIError, RuntimeError, OSError) as erro:
            print(f"  ERRO {caminho.name}: {erro}")
            return None

    with ThreadPoolExecutor(max_workers=max(1, args.paralelo)) as pool:
        paginas = list(pool.map(seguro, fotos))
    if not any(paginas):
        sys.exit("Nenhuma foto foi transcrita; documento não gerado.")

    doc = gerar_docx.novo_documento(args.titulo)
    primeira = True
    falhas = []
    for caminho, pagina in zip(fotos, paginas):
        if pagina is None:
            falhas.append(caminho.name)
            continue
        if args.quebra_de_pagina and not primeira:
            gerar_docx.quebra_de_pagina(doc)
        primeira = False
        if args.mostrar_origem:
            gerar_docx.nota(doc, f"— {caminho.name} —")
        gerar_docx.adicionar_pagina(doc, pagina, imagens.get(caminho), args.diagramas)
        if pagina.observacoes:
            gerar_docx.nota(doc, f"Obs. ({caminho.name}): {pagina.observacoes}")

    args.saida.parent.mkdir(parents=True, exist_ok=True)
    doc.save(args.saida)
    print(f"\nDocumento salvo em {args.saida}")
    if falhas:
        print(f"Fotos com erro (fora do documento): {', '.join(falhas)}")
    print("Para abrir no Google Docs: envie o .docx ao Google Drive > botão direito > Abrir com > Documentos Google.")


if __name__ == "__main__":
    main()
