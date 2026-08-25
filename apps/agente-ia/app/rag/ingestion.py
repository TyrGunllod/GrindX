"""Extração e divisão de documentos em chunks (Markdown e CSV)."""

import csv
import io
import re
from dataclasses import dataclass


@dataclass
class Chunk:
    """Trecho de documento (seção) com título e conteúdo."""

    title: str
    content: str


def _split_headings(text: str) -> list[tuple[str, str]]:
    lines = text.splitlines()
    sections: list[tuple[str, str]] = []
    current_title: str | None = None
    current_lines: list[str] = []

    for line in lines:
        match = re.match(r"^(#{1,6})\s+(.+)$", line.strip())
        if match:
            if current_title is not None:
                sections.append((current_title, "\n".join(current_lines).strip()))
            current_title = match.group(2).strip()
            current_lines = []
        else:
            if current_title is None:
                current_title = ""
            current_lines.append(line)

    if current_title is not None:
        sections.append((current_title, "\n".join(current_lines).strip()))

    return sections


def chunk_markdown(text: str) -> list[Chunk]:
    """Divide um documento Markdown em chunks por seção (H1 a H6).

    Cada título vira um chunk, incluindo sub-seções (ex.: `### Botões ...`),
    o que torna cada funcionalidade/botão diretamente recuperável.
    """
    return [
        Chunk(title=title, content=content)
        for title, content in _split_headings(text)
        if content.strip()
    ]


def chunk_csv(text: str) -> list[Chunk]:
    """Converte um CSV em chunks legíveis (uma linha por chunk).

    A primeira linha é tratada como cabeçalho. Cada linha vira um trecho
    no formato "Coluna1: valor1; Coluna2: valor2", o que permite ao agente
    responder sobre o conteúdo de planilhas.
    """
    reader = csv.reader(io.StringIO(text))
    rows = list(reader)
    if not rows:
        return []

    header = rows[0]
    chunks: list[Chunk] = []
    for index, row in enumerate(rows[1:], start=2):
        if not any(cell.strip() for cell in row):
            continue
        fields = []
        for j, cell in enumerate(row):
            column = header[j] if j < len(header) else f"Coluna {j + 1}"
            if cell.strip():
                fields.append(f"{column}: {cell.strip()}")
        if fields:
            chunks.append(Chunk(title=f"Linha {index}", content="; ".join(fields)))
    return chunks
