"""Extração e divisão de manuais Markdown em chunks por seção."""

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
        match = re.match(r"^(#{1,2})\s+(.+)$", line.strip())
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
    """Divide um documento Markdown em chunks, um por seção (H1/H2).

    Sub-títulos (H3+) permanecem dentro do chunk da seção pai, para que
    a explicação completa de uma tela/modal fique em um único chunk.
    """
    return [
        Chunk(title=title, content=content)
        for title, content in _split_headings(text)
        if content.strip()
    ]
