from rag.config import CHROMA_COLLECTION, CHROMA_DIR, CHAT_MODEL, EMBED_MODEL, OLLAMA_HOST
from rag.ollama_client import Ollama
from rag.qa import answer_question, simple_sources
from rag.vectorstore import VectorStore


def main() -> None:
    ollama = Ollama(host=OLLAMA_HOST)
    vs = VectorStore(persist_dir=CHROMA_DIR, collection_name=CHROMA_COLLECTION)

    print("BIO stat AI ready. Type 'exit' to quit.\n")
    print(f"Chat model: {CHAT_MODEL}")
    print(f"Embedding model: {EMBED_MODEL}\n")

    while True:
        q = input("You: ").strip()
        if q.lower() in {"exit", "quit"}:
            print("Bye.")
            break
        if not q:
            continue

        ans, ctxs = answer_question(question=q, ollama=ollama, vectorstore=vs)
        sources = simple_sources(ctxs, limit=3)
        print(f"\nAssistant: {ans}\n")
        if sources:
            print("📚 Source:")
            for src in sources:
                print(f"- {src}")
            print()


if __name__ == "__main__":
    main()

