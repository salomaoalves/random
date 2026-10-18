"""Course content, read from sibling folders: one folder per language being learned.

    courses/
      es/                  Spanish
        course.json        {"name": {...}, "areas": ["basics", "food", "grammar"]}
        basics.json        {"name": {...}, "icon": "waving_hand", "stations": [...]}
        food.json
        grammar.json
      en/                  English
        ...

To add a course, add a folder with the same files; no code change is needed.
Texts in the learner's language are {"en": ..., "pt": ...} (missing languages fall back
to English); texts in the language being learned are plain strings.
A station is {"title": ..., "questions": [{"prompt": ..., "options": [...], "answer": <index>}]}.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from core.i18n import Localized

COURSES_DIR = Path(__file__).resolve().parent / "courses"
DEFAULT_COURSE = "es"


@dataclass(frozen=True)
class Question:
    prompt: Localized
    options: tuple[Localized, ...]
    answer: int  # index in `options`


@dataclass(frozen=True)
class Station:
    title: Localized
    questions: tuple[Question, ...]


@dataclass(frozen=True)
class Area:
    id: str
    name: Localized
    icon: str
    stations: tuple[Station, ...]


@dataclass(frozen=True)
class CourseInfo:
    """What the course menu needs, without reading every question."""

    id: str
    name: Localized


@dataclass(frozen=True)
class Course:
    id: str
    name: Localized
    areas: tuple[Area, ...]

    def area(self, id_: str) -> Area:
        return next((a for a in self.areas if a.id == id_), self.areas[0])


def _read(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e:
        raise ValueError(f"Invalid course file {path}: {e}") from e


def _question(data: dict, where: str) -> Question:
    options = tuple(data["options"])
    if not 0 <= data["answer"] < len(options):
        raise ValueError(f"{where}: answer {data['answer']} is outside the {len(options)} options")
    return Question(data["prompt"], options, data["answer"])


def _area(folder: Path, id_: str) -> Area:
    data = _read(folder / f"{id_}.json")
    stations = tuple(
        Station(s["title"], tuple(_question(q, f"{folder.name}/{id_}.json station {i + 1} question {j + 1}")
                                  for j, q in enumerate(s["questions"])))
        for i, s in enumerate(data["stations"])
    )
    return Area(id_, data["name"], data.get("icon", "school"), stations)


def available_courses(root: Path = COURSES_DIR) -> tuple[CourseInfo, ...]:
    """Every folder with a course.json, default course first."""
    infos = [CourseInfo(f.name, _read(f / "course.json")["name"])
             for f in sorted(root.iterdir()) if (f / "course.json").is_file()]
    return tuple(sorted(infos, key=lambda c: c.id != DEFAULT_COURSE))


@lru_cache(maxsize=None)
def load_course(id_: str, root: Path = COURSES_DIR) -> Course:
    """Reads one course folder; unknown ids fall back to the default course."""
    folder = root / id_
    if not (folder / "course.json").is_file():
        folder = root / available_courses(root)[0].id
    meta = _read(folder / "course.json")
    return Course(folder.name, meta["name"], tuple(_area(folder, a) for a in meta["areas"]))
