from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class Chunk:
    id: str
    text: str
    source: str
    page: int
    chunk_index: int


_whitespace_re = re.compile(r"\s+")


def normalize_text(text: str) -> str:
    text = text.replace("\x00", " ")
    text = _whitespace_re.sub(" ", text)
    return text.strip()


def chunk_text(
    *,
    text: str,
    source: str,
    page: int,
    chunk_size: int,
    chunk_overlap: int,
) -> list[Chunk]:
    t = normalize_text(text)
    if not t:
        return []

    if chunk_overlap >= chunk_size:
        raise ValueError("chunk_overlap must be < chunk_size")

    chunks: list[Chunk] = []
    start = 0
    chunk_index = 0
    while start < len(t):
        end = min(len(t), start + chunk_size)
        chunk = t[start:end].strip()

        if chunk:
            chunk_id = f"{source}::p{page:04d}::c{chunk_index:04d}"
            chunks.append(
                Chunk(
                    id=chunk_id,
                    text=chunk,
                    source=source,
                    page=page,
                    chunk_index=chunk_index,
                )
            )
            chunk_index += 1

        if end >= len(t):
            break
        start = max(0, end - chunk_overlap)

    return chunks

