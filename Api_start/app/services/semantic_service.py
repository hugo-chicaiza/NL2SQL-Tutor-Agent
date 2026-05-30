# =========================================================
# app/services/semantic_service.py
# =========================================================

import logging
from pathlib import Path

from app.context.embeddings import (
    EmbeddingManager
)

from app.context.semantic_retriever import (
    SemanticRetriever
)

from app.models.context_models import (
    LLMContext
)

logger = logging.getLogger(__name__)


class SemanticService:

    """
    Enterprise Semantic Layer Bootstrapper.

    Responsibilities
    ----------------
    - Build semantic documents
    - Build FAISS index
    - Load persisted index
    - Save persisted index
    - Create SemanticRetriever

    Does NOT perform retrieval.
    """

    INDEX_FILE = "semantic_index.faiss"

    MAPPING_FILE = "semantic_mapping.pkl"

    def __init__(
        self,
        llm_context: LLMContext,
        artifacts_dir: str = "artifacts/semantic"
    ):

        self.llm_context = llm_context

        self.artifacts_dir = Path(
            artifacts_dir
        )

        self.artifacts_dir.mkdir(
            parents=True,
            exist_ok=True
        )

        self.index_path = (
            self.artifacts_dir
            / self.INDEX_FILE
        )

        self.mapping_path = (
            self.artifacts_dir
            / self.MAPPING_FILE
        )

        self.embedding_manager = (
            EmbeddingManager()
        )

        self.semantic_retriever = None

    # =====================================================
    # PUBLIC INITIALIZATION
    # =====================================================

    def initialize(
        self,
        rebuild: bool = False
    ) -> SemanticRetriever:

        """
        Initializes semantic layer.

        rebuild=True
            Force FAISS rebuild.

        rebuild=False
            Load existing index if available.
        """

        if (
            not rebuild
            and self._artifacts_exist()
        ):

            logger.info(
                "Loading semantic index from disk"
            )

            self._load_index()

        else:

            logger.info(
                "Building semantic index"
            )

            self._build_index()

        self.semantic_retriever = (
            SemanticRetriever(
                embedding_manager=(
                    self.embedding_manager
                )
            )
        )

        logger.info(
            "Semantic retriever initialized"
        )

        return self.semantic_retriever

    # =====================================================
    # BUILD INDEX
    # =====================================================

    def _build_index(self):

        documents = (
            self.embedding_manager
            .build_documents(
                schema=(
                    self.llm_context
                    .schema
                    .tables
                ),

                semantics=(
                    self.llm_context
                    .semantics
                    .tables
                ),

                graph=(
                    self.llm_context
                    .graph
                    .adjacency
                )
            )
        )

        logger.info(
            f"Generated "
            f"{len(documents)} "
            f"semantic documents"
        )

        self.embedding_manager.build_index(
            documents
        )

        self.embedding_manager.save(
            str(self.index_path),
            str(self.mapping_path)
        )

        logger.info(
            "Semantic index persisted"
        )

    # =====================================================
    # LOAD INDEX
    # =====================================================

    def _load_index(self):

        self.embedding_manager.load(
            str(self.index_path),
            str(self.mapping_path)
        )

        logger.info(
            "Semantic index loaded"
        )

    # =====================================================
    # HELPERS
    # =====================================================

    def _artifacts_exist(
        self
    ) -> bool:

        return (

            self.index_path.exists()

            and

            self.mapping_path.exists()
        )

    # =====================================================
    # ACCESSORS
    # =====================================================

    def get_retriever(
        self
    ) -> SemanticRetriever:

        if self.semantic_retriever is None:

            raise RuntimeError(

                "Semantic layer not initialized. "
                "Call initialize() first."
            )

        return self.semantic_retriever

    def get_embedding_manager(
        self
    ) -> EmbeddingManager:

        return self.embedding_manager