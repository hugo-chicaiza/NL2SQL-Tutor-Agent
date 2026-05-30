# =========================================================
# app/context/semantic_retriever.py
# =========================================================

import logging

from typing import (
    Dict,
    Any,
    List,
    Set
)

from app.context.embeddings import (
    EmbeddingManager
)

logger = logging.getLogger(__name__)


class SemanticRetriever:

    """
    Enterprise Semantic Retrieval Layer.

    Responsibilities:
    - query normalization
    - lightweight query expansion
    - semantic table retrieval
    - score filtering
    - ranked debugging output
    """

    DEFAULT_TOP_K = 8

    DEFAULT_MIN_SCORE = 0.35

    def __init__(
        self,
        embedding_manager: EmbeddingManager,
        top_k: int = DEFAULT_TOP_K,
        min_score: float = DEFAULT_MIN_SCORE
    ):

        self.embedding_manager = (
            embedding_manager
        )

        self.top_k = top_k

        self.min_score = min_score

    # =====================================================
    # MAIN RETRIEVAL
    # =====================================================

    def retrieve(
        self,
        question: str
    ) -> Set[str]:

        logger.info(
            "Running semantic retrieval"
        )

        expanded_query = (
            self._expand_query(
                question
            )
        )

        results = (
            self.embedding_manager.search(
                query=expanded_query,
                top_k=self.top_k
            )
        )

        candidates = set()

        for result in results:

            score = result.get(
                "score",
                0.0
            )

            if score < self.min_score:
                continue

            candidates.add(
                result["table"]
            )

        logger.info(

            f"Semantic retrieval returned "
            f"{len(candidates)} candidates"
        )

        return candidates

    # =====================================================
    # RANKED OUTPUT
    # =====================================================

    def retrieve_ranked(
        self,
        question: str
    ) -> List[Dict[str, Any]]:

        expanded_query = (
            self._expand_query(
                question
            )
        )

        results = (
            self.embedding_manager.search(
                query=expanded_query,
                top_k=self.top_k
            )
        )

        filtered = []

        for result in results:

            score = result.get(
                "score",
                0.0
            )

            if score < self.min_score:
                continue

            filtered.append({

                "table":
                    result["table"],

                "score":
                    score,

                "type":
                    result.get(
                        "type",
                        "table"
                    )
            })

        filtered.sort(

            key=lambda x:
                x["score"],

            reverse=True
        )

        return filtered

    # =====================================================
    # QUERY EXPANSION
    # =====================================================

    def _expand_query(
        self,
        query: str
    ) -> str:

        query = (
            query
            .lower()
            .strip()
        )

        expansions = []

        # ---------------------------------------------
        # CUSTOMER DOMAIN
        # ---------------------------------------------

        if any(

            term in query

            for term in [

                "customer",
                "client",
                "buyer"
            ]
        ):

            expansions.extend([

                "customers",
                "users",
                "accounts",
                "buyers"
            ])

        # ---------------------------------------------
        # SALES DOMAIN
        # ---------------------------------------------

        if any(

            term in query

            for term in [

                "revenue",
                "income",
                "sales"
            ]
        ):

            expansions.extend([

                "billing",
                "payments",
                "earnings",
                "financial"
            ])

        # ---------------------------------------------
        # ORDER DOMAIN
        # ---------------------------------------------

        if any(

            term in query

            for term in [

                "order",
                "purchase",
                "transaction"
            ]
        ):

            expansions.extend([

                "orders",
                "transactions",
                "purchases",
                "invoices"
            ])

        # ---------------------------------------------
        # PAYMENT DOMAIN
        # ---------------------------------------------

        if any(

            term in query

            for term in [

                "payment",
                "invoice"
            ]
        ):

            expansions.extend([

                "billing",
                "transactions",
                "money"
            ])

        # ---------------------------------------------
        # NETWORK DOMAIN
        # ---------------------------------------------

        if any(

            term in query

            for term in [

                "network",
                "router",
                "switch",
                "device"
            ]
        ):

            expansions.extend([

                "telecom",
                "infrastructure",
                "equipment",
                "nodes"
            ])

        # ---------------------------------------------
        # INCIDENT DOMAIN
        # ---------------------------------------------

        if any(

            term in query

            for term in [

                "incident",
                "alarm",
                "fault",
                "failure"
            ]
        ):

            expansions.extend([

                "events",
                "alerts",
                "outages",
                "tickets"
            ])

        if not expansions:
            return query

        return (

            f"{query} "
            f"{' '.join(expansions)}"
        )
    
    def is_ready(self) -> bool:
        return (
            self.embedding_manager is not None
            and self.embedding_manager.is_ready()
    )