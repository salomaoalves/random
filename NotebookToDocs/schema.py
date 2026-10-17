"""Structure Claude returns for each photo: a list of formatted blocks."""
from typing import Literal, Optional

from pydantic import BaseModel, Field


class Run(BaseModel):
    """A piece of text with a single formatting."""
    text: str
    bold: bool = False
    italic: bool = False
    underline: bool = False
    strike: bool = False
    highlight: bool = Field(False, description="Highlighter, circled text or text inside a box")
    color: Optional[str] = Field(None, description="Hex (#RRGGBB) only when the pen is not black/dark blue")


class Box(BaseModel):
    """Rectangle in the photo, as fractions from 0 to 1 (0,0 = top-left corner)."""
    x0: float
    y0: float
    x1: float
    y1: float


class Diagram(BaseModel):
    description: str = Field(description="What the drawing shows: elements, arrows, links, hierarchy")
    texts: list[str] = Field(description="Every text written inside the drawing")
    box: Box


class Block(BaseModel):
    type: Literal["heading", "paragraph", "bullet_list", "numbered_list",
                  "quote", "table", "diagram", "separator"]
    level: int = Field(0, description="heading: 1 to 3. Lists/paragraphs: indentation from 0 to 3")
    alignment: Literal["left", "center", "right"] = "left"
    marker: str = Field("", description="How the item was marked in the notebook: '1.', 'a)', 'i.', '•', '☐', '☑', '→'")
    runs: list[Run] = Field(default_factory=list)
    table: Optional[list[list[str]]] = Field(None, description="Table rows; the first one is the header")
    diagram: Optional[Diagram] = None


class Page(BaseModel):
    blocks: list[Block]
    notes: str = Field("", description="Illegible parts, reading doubts; empty if none")
