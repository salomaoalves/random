"""Reads the photos of notes in images/ and builds a .docx (for Google Docs)
keeping headings, paragraphs, lists, bold, underline, highlights and diagrams.

    python transcribe.py
    python transcribe.py --folder photos/class3 --output output/class3.docx --title "Class 3"
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

import docx_builder
from schema import Page

try:  # iPhone .heic photos (optional: pip install pillow-heif)
    from pillow_heif import register_heif_opener
    register_heif_opener()
except ImportError:
    pass

MODEL = "claude-opus-5-5"
EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".gif", ".bmp", ".tif", ".tiff", ".heic", ".heif"}
MAX_SIDE = 2576          # px of the longest side sent to Claude
MAX_BYTES = 4_500_000    # the API limit is 5 MB per image
CACHE_DIR = Path(__file__).parent / ".cache"

PROMPT = """This is a photo of a notebook/notes page (handwritten or printed, possibly with \
drawings and diagrams). Transcribe EVERYTHING on it into the requested structure, reproducing \
the notebook layout as faithfully as possible.

Rules:
- Transcribe faithfully, in the original language. Do not translate, summarize or rewrite. \
Only fix what is clearly your own reading mistake, not the author's.
- Follow the page reading order (top to bottom; columns left to right; margin notes right \
after the passage they refer to).
- One block per heading, paragraph, list item, table or drawing. A line break that is only the \
end of the sheet width does NOT create a new block; a new paragraph does.
- heading: larger text, text underlined alone on its line, or text that clearly opens a section. \
level 1 = main title, 2 = subtitle, 3 = sub-subtitle.
- Lists: use level for the indentation (0 = no indent, 1 = sub-item, ...) and copy the marker \
as written into `marker` ("1.", "a)", "•", "-", "→", "☐" for an empty checkbox, "☑" for a \
checked one). Indented paragraphs also use level.
- Formatting per run: bold for reinforced/thicker letters or emphasis in capitals, underline \
for underlined text, strike for crossed-out text, highlight for highlighter, circled text or \
text inside a box, italic only if clearly slanted on purpose. Use `color` (hex) only for \
colored pens different from the main ink.
- table: fill `table` with the rows (the first one is the header).
- diagram: for drawings, sketches, flowcharts, mind maps, charts and figures. Describe in \
`description` what it is and how the elements connect (arrows, hierarchy), list in `texts` \
everything written inside it and mark in `box` the rectangle around the whole drawing, as \
fractions of the photo width/height (0 to 1). Running text around the drawing is NOT part of it.
- separator: horizontal lines drawn to separate subjects.
- Words that cannot be read: write [ilegível] in their place and mention them in `notes`.
- Ignore what is not content: ruling, spiral, printed margin, shadows, fingers, the table."""


def natural_key(path: Path):
    """page2 comes before page10."""
    return [int(p) if p.isdigit() else p.lower() for p in re.split(r"(\d+)", path.name)]


def open_image(path: Path) -> Image.Image:
    image = Image.open(path)
    # Phone photos come sideways with the rotation only in EXIF.
    return ImageOps.exif_transpose(image).convert("RGB")


def encode_for_upload(image: Image.Image) -> str:
    copy = image.copy()
    copy.thumbnail((MAX_SIDE, MAX_SIDE))
    for quality in (90, 80, 70, 60):
        buffer = io.BytesIO()
        copy.save(buffer, "JPEG", quality=quality)
        if buffer.tell() <= MAX_BYTES:
            break
    return base64.standard_b64encode(buffer.getvalue()).decode("utf-8")


def transcribe(client: anthropic.Anthropic, path: Path, image: Image.Image, use_cache: bool) -> Page:
    key = hashlib.sha256(path.read_bytes() + MODEL.encode() + PROMPT.encode()).hexdigest()[:32]
    cache_file = CACHE_DIR / f"{key}.json"
    if use_cache and cache_file.exists():
        return Page.model_validate_json(cache_file.read_text(encoding="utf-8"))

    response = client.beta.messages.parse(
        model=MODEL,
        max_tokens=20000,
        output_config={"effort": "high"},
        betas=["server-side-fallback-2026-07-01"],
        fallbacks="default",
        output_format=Page,
        messages=[{
            "role": "user",
            "content": [
                {"type": "image", "source": {"type": "base64", "media_type": "image/jpeg",
                                             "data": encode_for_upload(image)}},
                {"type": "text", "text": PROMPT},
            ],
        }],
    )
    if response.stop_reason == "refusal":
        raise RuntimeError("the model refused the image")
    if response.stop_reason == "max_tokens":
        raise RuntimeError("response truncated (page too long); try splitting the photo")
    page = response.parsed_output
    if page is None:
        raise RuntimeError("response without structured content")

    CACHE_DIR.mkdir(exist_ok=True)
    cache_file.write_text(page.model_dump_json(indent=2), encoding="utf-8")
    return page


def main():
    base = Path(__file__).parent
    parser = argparse.ArgumentParser(description="Transcribes photos of notes into a .docx (Google Docs).")
    parser.add_argument("--folder", type=Path, default=base / "images", help="folder with the photos (default: images/)")
    parser.add_argument("--output", type=Path, default=base / "output" / "notes.docx", help="generated .docx file")
    parser.add_argument("--title", help="title at the top of the document")
    parser.add_argument("--diagrams", choices=["both", "image", "description"], default="both",
                        help="drawings: crop of the photo, text description or both (default)")
    parser.add_argument("--page-break", action="store_true", help="each photo starts on a new page")
    parser.add_argument("--show-source", action="store_true", help="writes the photo name before its content")
    parser.add_argument("--workers", type=int, default=4, help="photos processed at the same time (default: 4)")
    parser.add_argument("--no-cache", action="store_true", help="ignores saved transcriptions and redoes everything")
    args = parser.parse_args()

    photos = sorted((p for p in args.folder.iterdir() if p.suffix.lower() in EXTENSIONS), key=natural_key) \
        if args.folder.is_dir() else []
    if not photos:
        sys.exit(f"No images found in {args.folder}")
    print(f"{len(photos)} photo(s) in {args.folder}")

    client = anthropic.Anthropic()
    images = {}

    def process(path):
        image = open_image(path)
        images[path] = image
        page = transcribe(client, path, image, use_cache=not args.no_cache)
        print(f"  ok    {path.name} ({len(page.blocks)} blocks)")
        return page

    def safe_process(path):
        try:
            return process(path)
        except (anthropic.APIError, RuntimeError, OSError) as error:
            print(f"  ERROR {path.name}: {error}")
            return None

    with ThreadPoolExecutor(max_workers=max(1, args.workers)) as pool:
        pages = list(pool.map(safe_process, photos))
    if not any(pages):
        sys.exit("No photo was transcribed; document not generated.")

    doc = docx_builder.new_document(args.title)
    first = True
    failures = []
    for path, page in zip(photos, pages):
        if page is None:
            failures.append(path.name)
            continue
        if args.page_break and not first:
            docx_builder.page_break(doc)
        first = False
        if args.show_source:
            docx_builder.note(doc, f"— {path.name} —")
        docx_builder.add_page(doc, page, images.get(path), args.diagrams)
        if page.notes:
            docx_builder.note(doc, f"Notes ({path.name}): {page.notes}")

    args.output.parent.mkdir(parents=True, exist_ok=True)
    doc.save(args.output)
    print(f"\nDocument saved to {args.output}")
    if failures:
        print(f"Photos with errors (left out of the document): {', '.join(failures)}")
    print("To open in Google Docs: upload the .docx to Google Drive > right click > Open with > Google Docs.")


if __name__ == "__main__":
    main()
