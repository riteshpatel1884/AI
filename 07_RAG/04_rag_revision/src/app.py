from pathlib import Path

from src.data_loaders import load_all_documents
from src.vectorstore import FaissVectorStore
from src.search import RAGSearch


# --------------------------------------------------
# Project paths
# --------------------------------------------------

BASE_DIR = Path(
    __file__
).resolve().parent

DATA_DIR = BASE_DIR / "data"
FAISS_DIR = BASE_DIR / "faiss_store"


# --------------------------------------------------
# Main
# --------------------------------------------------

if __name__ == "__main__":

    print("=" * 60)
    print("STARTING RAG APPLICATION")
    print("=" * 60)

    print(
        f"Data directory  : {DATA_DIR}"
    )

    print(
        f"FAISS directory : {FAISS_DIR}"
    )

    # --------------------------------------------------
    # Check whether vector store exists
    # --------------------------------------------------

    faiss_path = (
        FAISS_DIR / "faiss.index"
    )

    meta_path = (
        FAISS_DIR / "metadata.pkl"
    )

    # --------------------------------------------------
    # Build vector store if needed
    # --------------------------------------------------

    if not (
        faiss_path.exists()
        and meta_path.exists()
    ):

        print(
            "\n[INFO] Vector store not found."
        )

        print(
            "[INFO] Loading documents..."
        )

        docs = load_all_documents(
            str(DATA_DIR)
        )

        if not docs:

            raise ValueError(
                "No documents found "
                f"in {DATA_DIR}"
            )

        print(
            f"[INFO] Loaded {len(docs)} documents."
        )

        store = FaissVectorStore(
            persist_dir=str(FAISS_DIR)
        )

        store.build_from_documents(
            docs
        )

    else:

        print(
            "\n[INFO] Existing vector store found."
        )

    # --------------------------------------------------
    # Initialize RAG
    # --------------------------------------------------

    rag_search = RAGSearch(
        persist_dir=str(FAISS_DIR)
    )

    # --------------------------------------------------
    # Query
    # --------------------------------------------------

    query = (
        "What are the skills of Ritesh?"
    )

    summary = (
        rag_search.search_and_summarize(
            query,
            top_k=3
        )
    )

    # --------------------------------------------------
    # Output
    # --------------------------------------------------

    print("\n" + "=" * 60)
    print("QUERY")
    print("=" * 60)

    print(query)

    print("\n" + "=" * 60)
    print("ANSWER")
    print("=" * 60)

    print(summary)



# run :python -m src.app