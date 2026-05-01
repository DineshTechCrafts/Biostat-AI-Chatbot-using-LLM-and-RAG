from __future__ import annotations

from pathlib import Path

from tqdm import tqdm

from rag.chunking import chunk_text
from rag.config import (
    CHROMA_COLLECTION,
    CHROMA_DIR,
    CHUNK_OVERLAP,
    CHUNK_SIZE,
    EMBED_MODEL,
    OLLAMA_HOST,
    PDF_DIR,
)
from rag.ollama_client import Ollama
from rag.pdf_extract import extract_pdf_pages
from rag.vectorstore import VectorStore


def iter_pdfs(pdf_dir: str) -> list[Path]:
    d = Path(pdf_dir)
    if not d.exists():
        raise FileNotFoundError(f"PDF folder not found: {d.resolve()}")
    return sorted([p for p in d.rglob("*.pdf") if p.is_file()])


def ingest_all(
    *,
    pdf_dir: str = PDF_DIR,
    chroma_dir: str = CHROMA_DIR,
    collection_name: str = CHROMA_COLLECTION,
    embed_model: str = EMBED_MODEL,
    chunk_size: int = CHUNK_SIZE,
    chunk_overlap: int = CHUNK_OVERLAP,
    batch_size: int = 64,
) -> None:
    pdfs = iter_pdfs(pdf_dir)
    if not pdfs:
        raise RuntimeError(f"No PDFs found under: {Path(pdf_dir).resolve()}")

    ollama = Ollama(host=OLLAMA_HOST)
    vs = VectorStore(persist_dir=chroma_dir, collection_name=collection_name)

    for pdf_path in pdfs:
        source = pdf_path.name
        pages = extract_pdf_pages(pdf_path)

        pending_ids: list[str] = []
        pending_docs: list[str] = []
        pending_texts: list[str] = []
        pending_meta: list[dict] = []

        for pt in tqdm(pages, desc=f"Ingesting {source}", unit="page"):
            chunks = chunk_text(
                text=pt.text,
                source=source,
                page=pt.page_number,
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap,
            )
            for ch in chunks:
                pending_ids.append(ch.id)
                pending_docs.append(ch.text)
                pending_texts.append(ch.text)
                pending_meta.append(
                    {
                        "source": ch.source,
                        "page": ch.page,
                        "chunk_index": ch.chunk_index,
                    }
                )

                if len(pending_ids) >= batch_size:
                    pending_embs = ollama.embed_many(model=embed_model, inputs=pending_texts)
                    vs.upsert(
                        ids=pending_ids,
                        documents=pending_docs,
                        embeddings=pending_embs,
                        metadatas=pending_meta,
                    )
                    pending_ids, pending_docs, pending_texts, pending_meta = [], [], [], []

        if pending_ids:
            pending_embs = ollama.embed_many(model=embed_model, inputs=pending_texts)
            vs.upsert(
                ids=pending_ids,
                documents=pending_docs,
                embeddings=pending_embs,
                metadatas=pending_meta,
            )


if __name__ == "__main__":
    ingest_all()

