import streamlit as st

from rag.config import CHROMA_COLLECTION, CHROMA_DIR, OLLAMA_HOST
from rag.ollama_client import Ollama
from rag.qa import answer_question, simple_sources
from rag.vectorstore import VectorStore


st.set_page_config(page_title="Biostat AI", page_icon="💬", layout="wide")

st.markdown(
    """
    <style>
    .main { max-width: 900px; margin: auto; }
    .stChatMessage { border-radius: 14px; padding: 6px 10px; }
    .source-box {
        background: #f7f7f8;
        border: 1px solid #e7e7e8;
        border-radius: 12px;
        padding: 10px 12px;
        margin-top: 10px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("Biostat AI")
st.caption("Ask questions from your PDF dataset")

if "messages" not in st.session_state:
    st.session_state.messages = []

if "backend" not in st.session_state:
    st.session_state.backend = {
        "ollama": Ollama(host=OLLAMA_HOST),
        "vectorstore": VectorStore(persist_dir=CHROMA_DIR, collection_name=CHROMA_COLLECTION),
    }

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg["role"] == "assistant" and msg.get("sources"):
            st.markdown("📚 **Source:**")
            for src in msg["sources"]:
                st.markdown(f"- {src}")

question = st.chat_input("Ask your question...")
if question:
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            answer, contexts = answer_question(
                question=question,
                ollama=st.session_state.backend["ollama"],
                vectorstore=st.session_state.backend["vectorstore"],
            )
            sources = simple_sources(contexts, limit=3)

        st.markdown(answer)
        if sources:
            st.markdown("📚 **Source:**")
            for src in sources:
                st.markdown(f"- {src}")

    st.session_state.messages.append(
        {"role": "assistant", "content": answer, "sources": sources}
    )