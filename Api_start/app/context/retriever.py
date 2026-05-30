# =========================================================
# app/context/retriever.py
# =========================================================

import logging

from typing import Dict, Any, List, Set, Optional

from app.models.context_models import (
    LLMContext
)

logger = logging.getLogger(__name__)


class ContextRetriever:

    """
    Enterprise Context Retrieval Layer.

    Responsibilities:
    - deterministic retrieval
    - semantic retrieval integration
    - graph expansion
    - schema reduction
    - relationship filtering
    - semantic filtering
    """

    MAX_GRAPH_NEIGHBORS = 3

    DEFAULT_FALLBACK_TABLES = 3

    # =====================================================
    # MAIN ENTRYPOINT
    # =====================================================

    @staticmethod
    def retrieve(
        question: str,
        plan: Dict[str, Any],
        llm_context: LLMContext,
        semantic_candidates: Optional[Set[str]] = None,
    ) -> Dict[str, Any]:

        logger.info(
            "Starting context retrieval"
        )

        question_lower = question.lower()

        # -------------------------------------------------
        # 1. TABLE SELECTION
        # -------------------------------------------------

        if semantic_candidates:

            selected_tables = {

                t
                for t in semantic_candidates
                if t in llm_context.schema.tables
            }

            selection_source = "semantic"

        else:

            selected_tables = (
                ContextRetriever
                ._detect_relevant_tables(
                    question_lower,
                    llm_context
                )
            )

            selection_source = "deterministic"

        # -------------------------------------------------
        # FALLBACK
        # -------------------------------------------------

        if not selected_tables:

            selected_tables = (
                ContextRetriever
                ._fallback_tables(
                    llm_context
                )
            )

            selection_source = "fallback"

        # -------------------------------------------------
        # 2. GRAPH EXPANSION
        # -------------------------------------------------

        expanded_tables = (
            ContextRetriever
            ._expand_related_tables(
                selected_tables,
                llm_context
            )
        )

        # -------------------------------------------------
        # 3. FILTER CONTEXT
        # -------------------------------------------------

        filtered_schema = (
            ContextRetriever
            ._filter_schema(
                expanded_tables,
                llm_context,
                question_lower
            )
        )

        filtered_relationships = (
            ContextRetriever
            ._filter_relationships(
                expanded_tables,
                llm_context
            )
        )

        filtered_joins = (
            ContextRetriever
            ._filter_joins(
                expanded_tables,
                llm_context
            )
        )

        filtered_semantic_tables = (
            ContextRetriever
            ._filter_semantic_tables(
                expanded_tables,
                llm_context
            )
        )

        filtered_semantic_columns = (
            ContextRetriever
            ._filter_semantic_columns(
                expanded_tables,
                llm_context
            )
        )

        logger.info(
            f"Context retrieval completed. "
            f"{len(expanded_tables)} tables selected."
        )

        return {

            "schema":
                filtered_schema,

            "relationships":
                filtered_relationships,

            "joins":
                filtered_joins,

            "semantic_tables":
                filtered_semantic_tables,

            "semantic_columns":
                filtered_semantic_columns,

            "retrieval_metadata": {

                "selection_source":
                    selection_source,

                "tables_selected":
                    sorted(expanded_tables),

                "table_count":
                    len(expanded_tables)
            }
        }

    # =====================================================
    # FALLBACK
    # =====================================================

    @staticmethod
    def _fallback_tables(
        context: LLMContext
    ) -> Set[str]:

        semantic_tables = (
            context.semantics.tables
        )

        if semantic_tables:

            ordered = sorted(

                semantic_tables.items(),

                key=lambda x:
                    x[1].get(
                        "importance_score",
                        0
                    ),

                reverse=True
            )

            return {

                table

                for table, _ in ordered[
                    :ContextRetriever
                    .DEFAULT_FALLBACK_TABLES
                ]
            }

        return set(
            list(
                context.schema.tables.keys()
            )[
                :ContextRetriever
                .DEFAULT_FALLBACK_TABLES
            ]
        )

    # =====================================================
    # DETERMINISTIC TABLE DETECTION
    # =====================================================

    @staticmethod
    def _detect_relevant_tables(
        question: str,
        context: LLMContext,
    ) -> Set[str]:

        relevant = set()

        # ---------------------------------------------
        # TABLE NAME MATCH
        # ---------------------------------------------

        for table_name in context.schema.tables:

            short_name = (
                table_name
                .split(".")[-1]
                .lower()
            )

            singular = (
                short_name[:-1]
                if short_name.endswith("s")
                else short_name
            )

            if (
                short_name in question
                or singular in question
            ):
                relevant.add(table_name)

        # ---------------------------------------------
        # COLUMN MATCH
        # ---------------------------------------------

        for table_name, table_data in (
            context.schema.tables.items()
        ):

            for column in (
                table_data["columns"]
            ):

                col_name = (
                    column["name"]
                    .lower()
                )

                if col_name in question:

                    relevant.add(
                        table_name
                    )

        # ---------------------------------------------
        # SEMANTIC TABLE MATCH
        # ---------------------------------------------

        for table_name, semantic in (
            context.semantics.tables.items()
        ):

            tags = semantic.get(
                "domain_tags",
                []
            )

            description = semantic.get(
                "description",
                ""
            ).lower()

            if any(
                tag.lower() in question
                for tag in tags
            ):
                relevant.add(table_name)

            if any(
                word in description
                for word in question.split()
            ):
                relevant.add(table_name)

        return relevant

    # =====================================================
    # GRAPH EXPANSION
    # =====================================================

    @staticmethod
    def _expand_related_tables(
        tables: Set[str],
        context: LLMContext,
    ) -> Set[str]:

        expanded = set(tables)

        for table in tables:

            neighbors = (
                context.graph.adjacency.get(
                    table,
                    []
                )[
                    :ContextRetriever
                    .MAX_GRAPH_NEIGHBORS
                ]
            )

            expanded.update(
                neighbors
            )

        return expanded

    # =====================================================
    # SCHEMA FILTERING
    # =====================================================

    @staticmethod
    def _filter_schema(
        tables: Set[str],
        context: LLMContext,
        question: str,
    ) -> Dict[str, Any]:

        result = {}

        for table in tables:

            if table not in (
                context.schema.tables
            ):
                continue

            table_data = (
                context.schema.tables[
                    table
                ]
            )

            semantic_columns = (
                context.semantics.columns.get(
                    table,
                    []
                )
            )

            semantic_terms = set()

            for col in semantic_columns:

                semantic_terms.update(

                    synonym.lower()

                    for synonym in col.get(
                        "synonyms",
                        []
                    )
                )

            selected_columns = []

            for column in (
                table_data["columns"]
            ):

                col_name = (
                    column["name"]
                    .lower()
                )

                important = (

                    column.get(
                        "primary_key",
                        False
                    )

                    or

                    column.get(
                        "foreign_key",
                        False
                    )

                    or

                    col_name in question

                    or

                    any(
                        term in question
                        for term in semantic_terms
                    )
                )

                if important:

                    selected_columns.append(
                        column
                    )

            if not selected_columns:

                selected_columns = (
                    table_data["columns"][:10]
                )

            result[table] = {

                **table_data,

                "columns":
                    selected_columns
            }

        return result

    # =====================================================
    # RELATIONSHIPS
    # =====================================================

    @staticmethod
    def _filter_relationships(
        tables: Set[str],
        context: LLMContext,
    ) -> List[Dict[str, Any]]:

        relationships = []

        for edge in (
            context.graph.edges
        ):

            src = edge[
                "source_table"
            ]

            tgt = edge[
                "target_table"
            ]

            if (
                src in tables
                and tgt in tables
            ):

                relationships.append(
                    edge
                )

        return relationships

    # =====================================================
    # JOINS
    # =====================================================

    @staticmethod
    def _filter_joins(
        tables: Set[str],
        context: LLMContext,
    ) -> List[str]:

        joins = []

        for join in context.joins:

            if any(
                table in join
                for table in tables
            ):
                joins.append(join)

        return joins

    # =====================================================
    # TABLE SEMANTICS
    # =====================================================

    @staticmethod
    def _filter_semantic_tables(
        tables: Set[str],
        context: LLMContext,
    ) -> Dict[str, Any]:

        return {

            table: semantic

            for table, semantic in (
                context
                .semantics
                .tables
                .items()
            )

            if table in tables
        }

    # =====================================================
    # COLUMN SEMANTICS
    # =====================================================

    @staticmethod
    def _filter_semantic_columns(
        tables: Set[str],
        context: LLMContext,
    ) -> Dict[str, Any]:

        return {

            table: columns

            for table, columns in (
                context
                .semantics
                .columns
                .items()
            )

            if table in tables
        }