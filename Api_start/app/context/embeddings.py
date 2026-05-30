# =========================================================
# app/context/embeddings.py
# =========================================================

import logging
import pickle

from typing import (
    Dict,
    List,
    Any,
    Optional,
    Protocol
)

import numpy as np

try:
    import faiss
except ImportError:
    faiss = None


logger = logging.getLogger(__name__)


# =========================================================
# EMBEDDING PROVIDER INTERFACE
# =========================================================

class EmbeddingProvider(Protocol):
    """
    Interface for any embedding backend.
    You can plug OpenAI, OpenRouter, HF API, etc.
    """

    def embed(self, texts: List[str]) -> np.ndarray:
        ...


# =========================================================
# EMBEDDING MANAGER
# =========================================================

class EmbeddingManager:

    """
    Enterprise Semantic Embedding Layer (PLUGGABLE).

    Responsibilities:
    - schema document creation
    - semantic document creation
    - embedding generation (external provider)
    - vector search (FAISS)
    - persistence
    """

    MIN_SCORE_THRESHOLD = 0.20

    def __init__(
        self,
        embedder: EmbeddingProvider
    ):

        if embedder is None:
            raise ValueError(
                "EmbeddingProvider is required. "
                "Provide a valid embedder (OpenAI, OpenRouter, etc)."
            )

        self.embedder = embedder

        self.index = None
        self.metadata: List[Dict[str, Any]] = []

    # =====================================================
    # DOCUMENT GENERATION
    # =====================================================

    def build_documents(
        self,
        schema: Dict[str, Any],
        semantics: Dict[str, Any],
        adjacency: Optional[Dict[str, List[str]]] = None,
    ) -> List[Dict[str, Any]]:

        documents = []

        for table_name, table_data in schema.items():

            semantic = semantics.get(table_name, {})
            columns = table_data.get("columns", [])

            column_names = [
                col["name"]
                for col in columns
            ]

            related_tables = []

            if adjacency:
                related_tables = adjacency.get(table_name, [])

            text = self._build_table_document(
                table_name=table_name,
                semantic=semantic,
                column_names=column_names,
                related_tables=related_tables
            )

            documents.append({
                "type": "table",
                "table": table_name,
                "text": text
            })

        logger.info(
            f"Generated {len(documents)} semantic documents"
        )

        return documents

    def _build_table_document(
        self,
        table_name: str,
        semantic: Dict[str, Any],
        column_names: List[str],
        related_tables: List[str]
    ) -> str:

        description = semantic.get("description", "")
        tags = semantic.get("domain_tags", [])

        return f"""
TABLE:
{table_name}

BUSINESS_DESCRIPTION:
{description}

DOMAIN_TAGS:
{", ".join(tags)}

COLUMNS:
{", ".join(column_names)}

RELATED_TABLES:
{", ".join(related_tables)}

ENTITY_TYPE:
Business database table
""".strip()

    # =====================================================
    # EMBEDDINGS
    # =====================================================

    def encode(
        self,
        texts: List[str]
    ) -> np.ndarray:

        embeddings = self.embedder.embed(texts)

        embeddings = np.asarray(embeddings, dtype="float32")

        return embeddings

    # =====================================================
    # BUILD VECTOR INDEX
    # =====================================================

    def build_index(
        self,
        documents: List[Dict[str, Any]]
    ):

        if faiss is None:
            raise ImportError("faiss-cpu is required")

        if not documents:
            raise ValueError("No documents supplied")

        texts = [
            doc["text"]
            for doc in documents
        ]

        embeddings = self.encode(texts)

        dimension = embeddings.shape[1]

        index = faiss.IndexFlatIP(dimension)
        index.add(embeddings)

        self.index = index
        self.metadata = documents

        logger.info(
            f"Built semantic index with {len(documents)} documents"
        )

    # =====================================================
    # SEARCH
    # =====================================================

    def search(
        self,
        query: str,
        top_k: int = 10
    ) -> List[Dict[str, Any]]:

        if self.index is None:
            raise RuntimeError("Index not initialized")

        query_embedding = self.encode([query])

        scores, indices = self.index.search(
            query_embedding,
            top_k
        )

        results = []

        for idx, score in zip(indices[0], scores[0]):

            if idx < 0:
                continue

            if score < self.MIN_SCORE_THRESHOLD:
                continue

            metadata = self.metadata[idx]

            results.append({
                "table": metadata["table"],
                "score": round(float(score), 4),
                "type": metadata["type"],
                "text": metadata["text"]
            })

        return results

    # =====================================================
    # PERSISTENCE
    # =====================================================

    def save(self, index_path: str, metadata_path: str):

        if self.index is None:
            raise RuntimeError("Index not built")

        faiss.write_index(self.index, index_path)

        with open(metadata_path, "wb") as f:
            pickle.dump(self.metadata, f)

        logger.info("Embedding index saved")

    def load(self, index_path: str, metadata_path: str):

        if faiss is None:
            raise ImportError("faiss-cpu is required")

        self.index = faiss.read_index(index_path)

        with open(metadata_path, "rb") as f:
            self.metadata = pickle.load(f)

        logger.info("Embedding index loaded")

    # =====================================================
    # UTILITIES
    # =====================================================

    def is_ready(self) -> bool:

        return (
            self.index is not None
            and len(self.metadata) > 0
        )

    def total_documents(self) -> int:

        return len(self.metadata)