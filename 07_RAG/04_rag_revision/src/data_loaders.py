from pathlib import Path
from typing import List, Any

from langchain_community.document_loaders import (
    PyPDFLoader,
    TextLoader,
    CSVLoader,
    Docx2txtLoader,
    JSONLoader,
)
from langchain_community.document_loaders.excel import (
    UnstructuredExcelLoader
)


def load_all_documents(data_dir: str) -> List[Any]:
    """
    Load all supported files from the data directory.

    Supported:
    - PDF
    - TXT
    - CSV
    - Excel
    - Word
    - JSON

    Returns:
        List of LangChain Document objects.
    """

    data_path = Path(data_dir).resolve()

    print(f"[DEBUG] Data path: {data_path}")

    if not data_path.exists():
        raise FileNotFoundError(
            f"Data directory does not exist: {data_path}"
        )

    documents = []

    # --------------------------------------------------
    # PDF
    # --------------------------------------------------

    pdf_files = list(data_path.glob("**/*.pdf"))

    print(
        f"[DEBUG] Found {len(pdf_files)} PDF files"
    )

    for pdf_file in pdf_files:

        print(f"[DEBUG] Loading PDF: {pdf_file}")

        try:
            loader = PyPDFLoader(
                str(pdf_file)
            )

            loaded = loader.load()

            print(
                f"[DEBUG] Loaded {len(loaded)} PDF documents"
            )

            documents.extend(loaded)

        except Exception as e:
            print(
                f"[ERROR] Failed to load PDF "
                f"{pdf_file}: {e}"
            )

    # --------------------------------------------------
    # TXT
    # --------------------------------------------------

    txt_files = list(data_path.glob("**/*.txt"))

    print(
        f"[DEBUG] Found {len(txt_files)} TXT files"
    )

    for txt_file in txt_files:

        print(f"[DEBUG] Loading TXT: {txt_file}")

        try:
            loader = TextLoader(
                str(txt_file),
                encoding="utf-8"
            )

            loaded = loader.load()

            print(
                f"[DEBUG] Loaded {len(loaded)} TXT documents"
            )

            documents.extend(loaded)

        except Exception as e:
            print(
                f"[ERROR] Failed to load TXT "
                f"{txt_file}: {e}"
            )

    # --------------------------------------------------
    # CSV
    # --------------------------------------------------

    csv_files = list(data_path.glob("**/*.csv"))

    print(
        f"[DEBUG] Found {len(csv_files)} CSV files"
    )

    for csv_file in csv_files:

        print(f"[DEBUG] Loading CSV: {csv_file}")

        try:
            loader = CSVLoader(
                str(csv_file)
            )

            loaded = loader.load()

            print(
                f"[DEBUG] Loaded {len(loaded)} CSV documents"
            )

            documents.extend(loaded)

        except Exception as e:
            print(
                f"[ERROR] Failed to load CSV "
                f"{csv_file}: {e}"
            )

    # --------------------------------------------------
    # Excel
    # --------------------------------------------------

    xlsx_files = list(
        data_path.glob("**/*.xlsx")
    )

    print(
        f"[DEBUG] Found {len(xlsx_files)} Excel files"
    )

    for xlsx_file in xlsx_files:

        print(f"[DEBUG] Loading Excel: {xlsx_file}")

        try:
            loader = UnstructuredExcelLoader(
                str(xlsx_file)
            )

            loaded = loader.load()

            print(
                f"[DEBUG] Loaded {len(loaded)} Excel documents"
            )

            documents.extend(loaded)

        except Exception as e:
            print(
                f"[ERROR] Failed to load Excel "
                f"{xlsx_file}: {e}"
            )

    # --------------------------------------------------
    # Word
    # --------------------------------------------------

    docx_files = list(
        data_path.glob("**/*.docx")
    )

    print(
        f"[DEBUG] Found {len(docx_files)} Word files"
    )

    for docx_file in docx_files:

        print(f"[DEBUG] Loading Word: {docx_file}")

        try:
            loader = Docx2txtLoader(
                str(docx_file)
            )

            loaded = loader.load()

            print(
                f"[DEBUG] Loaded {len(loaded)} Word documents"
            )

            documents.extend(loaded)

        except Exception as e:
            print(
                f"[ERROR] Failed to load Word "
                f"{docx_file}: {e}"
            )

    # --------------------------------------------------
    # JSON
    # --------------------------------------------------

    json_files = list(
        data_path.glob("**/*.json")
    )

    print(
        f"[DEBUG] Found {len(json_files)} JSON files"
    )

    for json_file in json_files:

        print(f"[DEBUG] Loading JSON: {json_file}")

        try:
            loader = JSONLoader(
                file_path=str(json_file),
                jq_schema=".",
                text_content=False
            )

            loaded = loader.load()

            print(
                f"[DEBUG] Loaded {len(loaded)} JSON documents"
            )

            documents.extend(loaded)

        except Exception as e:
            print(
                f"[ERROR] Failed to load JSON "
                f"{json_file}: {e}"
            )

    print(
        f"[DEBUG] Total loaded documents: "
        f"{len(documents)}"
    )

    return documents


# --------------------------------------------------
# Example usage
# --------------------------------------------------

if __name__ == "__main__":

    BASE_DIR = Path(__file__).resolve().parent

    DATA_DIR = BASE_DIR / "data"

    docs = load_all_documents(
        str(DATA_DIR)
    )

    print(
        f"Loaded {len(docs)} documents."
    )

    print(
        "Example document:",
        docs[0] if docs else None
    )