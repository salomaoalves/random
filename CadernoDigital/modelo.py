"""Estrutura que o Claude devolve para cada foto: uma lista de blocos com formatação."""
from typing import Literal, Optional

from pydantic import BaseModel, Field


class Trecho(BaseModel):
    """Pedaço de texto com a mesma formatação."""
    texto: str
    negrito: bool = False
    italico: bool = False
    sublinhado: bool = False
    riscado: bool = False
    destaque: bool = Field(False, description="Marca-texto, texto circulado ou dentro de um quadro")
    cor: Optional[str] = Field(None, description="Hex (#RRGGBB) só quando a caneta não é preta/azul escura")


class Caixa(BaseModel):
    """Retângulo na foto, em frações de 0 a 1 (0,0 = canto superior esquerdo)."""
    x0: float
    y0: float
    x1: float
    y1: float


class Diagrama(BaseModel):
    descricao: str = Field(description="O que o desenho mostra: elementos, setas, ligações, hierarquia")
    textos: list[str] = Field(description="Todos os textos escritos dentro do desenho")
    caixa: Caixa


class Bloco(BaseModel):
    tipo: Literal["titulo", "paragrafo", "lista_marcadores", "lista_numerada",
                  "citacao", "tabela", "diagrama", "separador"]
    nivel: int = Field(0, description="titulo: 1 a 3. Listas/parágrafos: recuo de 0 a 3")
    alinhamento: Literal["esquerda", "centro", "direita"] = "esquerda"
    marcador: str = Field("", description="Como o item foi marcado no caderno: '1.', 'a)', 'i.', '•', '☐', '☑', '→'")
    trechos: list[Trecho] = Field(default_factory=list)
    tabela: Optional[list[list[str]]] = Field(None, description="Linhas da tabela; a primeira é o cabeçalho")
    diagrama: Optional[Diagrama] = None


class Pagina(BaseModel):
    blocos: list[Bloco]
    observacoes: str = Field("", description="Trechos ilegíveis, dúvidas de leitura; vazio se não houver")
