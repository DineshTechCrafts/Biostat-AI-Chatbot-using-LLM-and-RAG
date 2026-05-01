import os


def env(name: str, default: str) -> str:
    val = os.getenv(name)
    return val if val not in (None, "") else default


PDF_DIR = env("PDF_DIR", "PDF Dataset")
CHROMA_DIR = env("CHROMA_DIR", "chroma_db")
CHROMA_COLLECTION = env("CHROMA_COLLECTION", "pdf_chunks")

OLLAMA_HOST = env("OLLAMA_HOST", "http://localhost:11434")
CHAT_MODEL = env("CHAT_MODEL", "llama3.2:latest")
EMBED_MODEL = env("EMBED_MODEL", "nomic-embed-text")

# Chunking
CHUNK_SIZE = int(env("CHUNK_SIZE", "1100"))  # characters
CHUNK_OVERLAP = int(env("CHUNK_OVERLAP", "150"))
