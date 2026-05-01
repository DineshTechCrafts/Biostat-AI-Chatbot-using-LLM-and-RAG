import chromadb

from rag.config import CHROMA_COLLECTION, CHROMA_DIR, OLLAMA_HOST
from rag.ollama_client import Ollama
from rag.qa import answer_question
from rag.vectorstore import VectorStore


def main() -> None:
    collection = chromadb.PersistentClient(path=CHROMA_DIR).get_or_create_collection(
        CHROMA_COLLECTION
    )
    print(f"chunks_in_vector_db={collection.count()}")

    q = "What is biostatistics and why is it important in health research?"
    ans, ctx = answer_question(
        question=q,
        ollama=Ollama(host=OLLAMA_HOST),
        vectorstore=VectorStore(persist_dir=CHROMA_DIR, collection_name=CHROMA_COLLECTION),
    )
    print("\nanswer_preview:")
    print(ans[:700])
    print("\ntop_sources:")
    for c in ctx[:3]:
        m = c["metadata"]
        print(f"- {m.get('source')} (page {m.get('page')})")


if __name__ == "__main__":
    main()

