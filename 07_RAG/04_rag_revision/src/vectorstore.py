import os
import pickle

import faiss
import numpy as np

from typing import List, Any

from sentence_transformers import (
    SentenceTransformer
)

from src.embedding import EmbeddingPipeline


class FaissVectorStore:

    def __init__(
        self,
        persist_dir: str = "faiss_store",
        embedding_model: str = "all-MiniLM-L6-v2",
        chunk_size: int = 1000,
        chunk_overlap: int = 200
    ):

        self.persist_dir = persist_dir

        os.makedirs(
            self.persist_dir,
            exist_ok=True
        )

        self.index = None
        self.metadata = []

        self.embedding_model = embedding_model

        self.model = SentenceTransformer(
            embedding_model
        )

        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

        print(
            f"[INFO] Loaded embedding model: "
            f"{embedding_model}"
        )

    # --------------------------------------------------
    # Build vector store
    # --------------------------------------------------

    def build_from_documents(
        self,
        documents: List[Any]
    ):

        print(
            f"[INFO] Building vector store from "
            f"{len(documents)} raw documents..."
        )

        embedding_pipeline = EmbeddingPipeline(
            model_name=self.embedding_model,
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap
        )

        # Chunk documents
        chunks = embedding_pipeline.chunk_documents(
            documents
        )

        # Generate embeddings
        embeddings = embedding_pipeline.embed_chunks(
            chunks
        )

        # Store original text + metadata
        metadatas = []

        for chunk in chunks:

            metadata = dict(
                chunk.metadata
            )

            metadata["text"] = (
                chunk.page_content
            )

            metadatas.append(
                metadata
            )

        # Add embeddings
        self.add_embeddings(
            embeddings,
            metadatas
        )

        # Save
        self.save()

        print(
            f"[INFO] Vector store built and saved "
            f"to {self.persist_dir}"
        )

    # --------------------------------------------------
    # Add embeddings
    # --------------------------------------------------

    def add_embeddings(
        self,
        embeddings: np.ndarray,
        metadatas: List[Any] = None
    ):

        embeddings = np.asarray(
            embeddings,
            dtype="float32"
        )

        dimension = embeddings.shape[1]

        if self.index is None:

            self.index = faiss.IndexFlatL2(
                dimension
            )

        self.index.add(
            embeddings
        )

        if metadatas:

            self.metadata.extend(
                metadatas
            )

        print(
            f"[INFO] Added "
            f"{embeddings.shape[0]} vectors "
            f"to FAISS index."
        )

    # --------------------------------------------------
    # Save
    # --------------------------------------------------

    def save(self):

        faiss_path = os.path.join(
            self.persist_dir,
            "faiss.index"
        )

        meta_path = os.path.join(
            self.persist_dir,
            "metadata.pkl"
        )

        faiss.write_index(
            self.index,
            faiss_path
        )

        with open(
            meta_path,
            "wb"
        ) as f:

            pickle.dump(
                self.metadata,
                f
            )

        print(
            f"[INFO] Saved FAISS index and "
            f"metadata to {self.persist_dir}"
        )

    # --------------------------------------------------
    # Load
    # --------------------------------------------------

    def load(self):

        faiss_path = os.path.join(
            self.persist_dir,
            "faiss.index"
        )

        meta_path = os.path.join(
            self.persist_dir,
            "metadata.pkl"
        )

        if not os.path.exists(
            faiss_path
        ):

            raise FileNotFoundError(
                f"FAISS index not found: "
                f"{faiss_path}"
            )

        if not os.path.exists(
            meta_path
        ):

            raise FileNotFoundError(
                f"Metadata file not found: "
                f"{meta_path}"
            )

        self.index = faiss.read_index(
            faiss_path
        )

        with open(
            meta_path,
            "rb"
        ) as f:

            self.metadata = pickle.load(
                f
            )

        print(
            f"[INFO] Loaded FAISS index and "
            f"metadata from {self.persist_dir}"
        )

        print(
            f"[INFO] Total vectors: "
            f"{self.index.ntotal}"
        )

    # --------------------------------------------------
    # Search
    # --------------------------------------------------

    def search(
        self,
        query_embedding: np.ndarray,
        top_k: int = 5
    ):

        if self.index is None:

            raise ValueError(
                "FAISS index is not loaded."
            )

        query_embedding = np.asarray(
            query_embedding,
            dtype="float32"
        )

        top_k = min(
            top_k,
            self.index.ntotal
        )

        distances, indices = (
            self.index.search(
                query_embedding,
                top_k
            )
        )

        results = []

        for idx, distance in zip(
            indices[0],
            distances[0]
        ):

            if idx < 0:
                continue

            metadata = (
                self.metadata[idx]
                if idx < len(self.metadata)
                else None
            )

            results.append(
                {
                    "index": int(idx),
                    "distance": float(distance),
                    "metadata": metadata
                }
            )

        return results

    # --------------------------------------------------
    # Query
    # --------------------------------------------------

    def query(
        self,
        query_text: str,
        top_k: int = 5
    ):

        print(
            f"[INFO] Querying vector store for: "
            f"'{query_text}'"
        )

        query_embedding = self.model.encode(
            [query_text]
        )

        query_embedding = np.asarray(
            query_embedding,
            dtype="float32"
        )

        return self.search(
            query_embedding,
            top_k=top_k
        )