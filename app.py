from flask import Flask, jsonify, request
from flask_cors import CORS

from rag.config import CHROMA_COLLECTION, CHROMA_DIR, OLLAMA_HOST
from rag.ollama_client import Ollama
from rag.qa import answer_question, simple_sources
from rag.vectorstore import VectorStore

app = Flask(__name__)
CORS(app)

# Initialise once at startup
ollama = Ollama(host=OLLAMA_HOST)
vectorstore = VectorStore(persist_dir=CHROMA_DIR, collection_name=CHROMA_COLLECTION)


@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.get_json(force=True)
    question = (data.get("question") or "").strip()
    if not question:
        return jsonify({"error": "question is required"}), 400

    try:
        answer, contexts = answer_question(
            question=question,
            ollama=ollama,
            vectorstore=vectorstore,
        )
        sources = simple_sources(contexts, limit=3)
        return jsonify({"answer": answer, "sources": sources})
    except Exception as exc:  # noqa: BLE001
        return jsonify({"error": str(exc)}), 500


@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
