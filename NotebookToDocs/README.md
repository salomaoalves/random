# NotebookToDocs

Transforma fotos de anotações (caderno, folhas, quadro) num documento `.docx` que abre direto no Google Docs, mantendo o layout: títulos e subtítulos, parágrafos e recuos, listas e sublistas, **negrito**, <u>sublinhado</u>, ~~riscado~~, marca-texto, cores de caneta, tabelas e diagramas.

A leitura das fotos é feita pelo Claude (API da Anthropic), que devolve cada página como uma lista de blocos com formatação; o script monta o `.docx` a partir disso.

```
NotebookToDocs/
├── images/           coloque as fotos aqui (não vão para o git)
├── transcribe.py     script principal
├── schema.py         estrutura de cada página (blocos, trechos, diagramas)
├── docx_builder.py   monta o .docx
└── output/           documento gerado (notes.docx)
```

## Como usar

```
pip install -r requirements.txt
export ANTHROPIC_API_KEY=sk-ant-...
python transcribe.py
```

As fotos são lidas em ordem natural do nome (`pag2.jpg` antes de `pag10.jpg`), então nomeie na ordem das páginas. Aceita `.jpg`, `.png`, `.webp`, `.heic` (com `pip install pillow-heif`) e outros; a rotação das fotos de celular é corrigida sozinha.

Para levar ao Google Docs: envie `output/notes.docx` ao Google Drive → botão direito → **Abrir com → Documentos Google**.

### Opções

```
python transcribe.py --folder fotos/aula3 --output output/aula3.docx --title "Aula 3"
python transcribe.py --diagrams description    # desenhos viram só texto (sem recorte da foto)
python transcribe.py --page-break              # cada foto começa numa página nova
python transcribe.py --show-source             # anota o nome da foto antes de cada trecho
python transcribe.py --no-cache                # refaz todas as transcrições
```

| Opção | Padrão | O que faz |
|---|---|---|
| `--folder` | `images/` | pasta com as fotos |
| `--output` | `output/notes.docx` | arquivo gerado |
| `--title` | — | título no topo do documento |
| `--diagrams` | `both` | `image` (recorte da foto), `description` (texto) ou `both` |
| `--page-break` | não | uma página do documento por foto |
| `--show-source` | não | nome da foto antes do conteúdo dela |
| `--workers` | 4 | fotos enviadas ao mesmo tempo |
| `--no-cache` | não | ignora transcrições salvas em `.cache/` |

## Como o layout é mantido

| No caderno | No documento |
|---|---|
| Título / subtítulo | Título 1, 2, 3 |
| Parágrafo recuado | Parágrafo com recuo (até 3 níveis) |
| Lista com bolinha/traço | Lista com marcadores (com subníveis) |
| Lista `1.`, `a)`, `i.`, `→`, caixinhas `☐`/`☑` | Item com o marcador do jeito que foi escrito |
| Negrito, sublinhado, riscado, inclinado | Mesma formatação |
| Marca-texto, texto circulado ou num quadro | Realce amarelo |
| Caneta colorida | Texto na mesma cor |
| Tabela | Tabela (1ª linha em negrito) |
| Desenho, esquema, mapa mental | Recorte do desenho da foto + descrição em texto |
| Linha separando assuntos | Separador `⁂` |
| Palavra ilegível | `[ilegível]` + observação em cinza no fim da página |

## Observações

- Cada foto transcrita fica salva em `.cache/`; rodar de novo só envia as fotos novas ou alteradas.
- Fotos com erro são puladas e listadas no final; o documento é gerado com as demais.
- Fotos nítidas, de frente e bem iluminadas dão transcrições melhores. Uma página muito longa pode ser dividida em duas fotos.
