from __future__ import annotations

import re
from typing import Any

from rag.config import CHAT_MODEL, EMBED_MODEL
from rag.ollama_client import Ollama
from rag.vectorstore import VectorStore


def _build_prompt(question: str, contexts: list[dict[str, Any]]) -> str:
    context_lines: list[str] = []
    for i, ctx in enumerate(contexts, start=1):
        meta = ctx["metadata"]
        src = meta.get("source", "unknown")
        page = meta.get("page", "?")
        text = ctx["text"]
        context_lines.append(f"[{i}] Source: {src}, page: {page}\n{text}")

    context_block = "\n\n".join(context_lines) if context_lines else "No context found."
    return (
        "You are a highly skilled teacher explaining concepts to a beginner.\n\n"
        "Use ONLY the provided context to answer.\n\n"
        "Only use information explicitly present in the context.\n"
        "Do not add interpretations or general knowledge.\n\n"
        "Think step-by-step before answering, but only output the final structured answer.\n\n"
        "Follow this format strictly:\n\n"
        "🔹 Concept:\n"
        "(1–2 line definition)\n\n"
        "🔹 Explanation:\n"
        "(Explain step-by-step in simple terms)\n\n"
        "🔹 Key Points:\n"
        "- Point 1\n"
        "- Point 2\n"
        "- Point 3\n\n"
        "🔹 Example:\n"
        "(Give a real-world or simple example)\n\n"
        "🔹 Final Summary:\n"
        "(2–3 line recap)\n\n"
        "If the answer is not found in the context, say exactly:\n"
        "\"Sorry, this is not available in the provided material.\"\n\n"
        f"Context:\n{context_block}\n\n"
        f"Question:\n{question}\n\n"
        "Answer:"
    )


def retrieve(
    *,
    question: str,
    ollama: Ollama,
    vectorstore: VectorStore,
    embed_model: str = EMBED_MODEL,
    top_k: int = 3,
) -> list[dict[str, Any]]:
    q_emb = ollama.embeddings(model=embed_model, prompt=question)
    res = vectorstore.query(query_embedding=q_emb, n_results=top_k)

    docs = (res.get("documents") or [[]])[0]
    metas = (res.get("metadatas") or [[]])[0]
    dists = (res.get("distances") or [[]])[0]

    out: list[dict[str, Any]] = []
    for doc, meta, dist in zip(docs, metas, dists):
        out.append({"text": doc, "metadata": meta or {}, "distance": dist})
    return out


def answer_question(
    *,
    question: str,
    ollama: Ollama,
    vectorstore: VectorStore,
    chat_model: str = CHAT_MODEL,
    embed_model: str = EMBED_MODEL,
    top_k: int = 3,
) -> tuple[str, list[dict[str, Any]]]:
    contexts = retrieve(
        question=question,
        ollama=ollama,
        vectorstore=vectorstore,
        embed_model=embed_model,
        top_k=top_k,
    )
    prompt = _build_prompt(question, contexts)
    answer = ollama.generate(model=chat_model, prompt=prompt)
    return answer, contexts


def simple_sources(contexts: list[dict[str, Any]], limit: int = 3) -> list[str]:
    """Return a concise source line with mandatory page number."""
    del limit  # keep signature stable for callers
    if not contexts:
        return []

    first = contexts[0]
    meta = first.get("metadata", {})
    source = _clean_source_title(str(meta.get("source", "Provided material")))
    page = str(meta.get("page", "?"))
    chapter = _detect_chapter_from_contexts(contexts)

    if chapter:
        return [f"{source}, {chapter}, page {page}"]
    return [f"{source}, page {page}"]


def _clean_source_title(raw: str) -> str:
    title = raw.replace(".pdf", "").replace("_", " ").strip()
    title = re.sub(r"\s+", " ", title)
    # Remove trailing scanner/version noise like "-1" or "--UnitedVRG-".
    title = re.sub(r"\s*-\s*\d+$", "", title)
    title = re.sub(r"\s*--.*$", "", title)
    return title


def _detect_chapter_from_contexts(contexts: list[dict[str, Any]]) -> str | None:
    patterns = [
        re.compile(r"\bchapter\s+(\d+)\b", re.IGNORECASE),
        re.compile(r"\bch\.\s*(\d+)\b", re.IGNORECASE),
    ]
    for c in contexts:
        text = str(c.get("text", ""))
        for p in patterns:
            m = p.search(text)
            if m:
                return f"Chapter {m.group(1)}"
    return None

