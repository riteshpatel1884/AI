import os
from pathlib import Path

from dotenv import load_dotenv
from langchain_groq import ChatGroq

from src.vectorstore import FaissVectorStore


load_dotenv()


class RAGSearch:

    def __init__(
        self,
        persist_dir=None,
        embedding_model="all-MiniLM-L6-v2",
        llm_model="openai/gpt-oss-20b"
    ):

        # --------------------------------------------------
        # Project paths
        # --------------------------------------------------

        BASE_DIR = Path(
            __file__
        ).resolve().parent

        if persist_dir is None:

            persist_dir = (
                BASE_DIR / "faiss_store"
            )

        else:

            persist_dir = Path(
                persist_dir
            )

        # --------------------------------------------------
        # Vector store
        # --------------------------------------------------

        self.vectorstore = FaissVectorStore(
            persist_dir=str(persist_dir),
            embedding_model=embedding_model
        )

        # --------------------------------------------------
        # Load existing vector store
        # --------------------------------------------------

        faiss_path = (
            persist_dir / "faiss.index"
        )

        meta_path = (
            persist_dir / "metadata.pkl"
        )

        if not (
            faiss_path.exists()
            and meta_path.exists()
        ):

            raise FileNotFoundError(
                "FAISS vector store not found.\n"
                f"Expected:\n"
                f"{faiss_path}\n"
                f"{meta_path}\n"
                "\n"
                "Build the vector store first."
            )

        self.vectorstore.load()

        # --------------------------------------------------
        # Groq
        # --------------------------------------------------

        groq_api_key = os.getenv(
            "GROQ_API_KEY"
        )

        if not groq_api_key:

            raise ValueError(
                "GROQ_API_KEY not found "
                "in .env file."
            )

        self.llm = ChatGroq(
            groq_api_key=groq_api_key,
            model_name=llm_model,
            temperature=0.1
        )

        print(
            f"[INFO] Groq LLM initialized: "
            f"{llm_model}"
        )

    # --------------------------------------------------
    # Search + summarize
    # --------------------------------------------------

    def search_and_summarize(
        self,
        query: str,
        top_k: int = 5
    ) -> str:

        results = self.vectorstore.query(
            query,
            top_k=top_k
        )

        if not results:

            return (
                "No relevant documents found."
            )

        # --------------------------------------------------
        # Extract retrieved text
        # --------------------------------------------------

        texts = []

        for result in results:

            metadata = result.get(
                "metadata"
            )

            if not metadata:
                continue

            text = metadata.get(
                "text",
                ""
            )

            if text:
                texts.append(
                    text
                )

        context = "\n\n".join(
            texts
        )

        if not context:

            return (
                "No relevant documents found."
            )

        # --------------------------------------------------
        # Prompt
        # --------------------------------------------------

        prompt = f"""
You are a helpful RAG assistant.

Answer the question using ONLY the
provided context.

If the answer is not available in the
context, say:

"I don't have enough information
in the provided documents."

Question:
{query}

Context:
{context}

Answer:
"""

        # --------------------------------------------------
        # LLM
        # --------------------------------------------------

        response = self.llm.invoke(
            prompt
        )

        return response.content