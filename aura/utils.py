from __future__ import annotations

from datetime import datetime


def timestamp() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def make_source_chunks(documents: list, chunk_fn):
    chunks = []
    for doc in documents:
        if not doc.text.strip():
            continue
        for chunk in chunk_fn(doc.text):
            chunks.append((chunk, doc.name))
    return chunks
