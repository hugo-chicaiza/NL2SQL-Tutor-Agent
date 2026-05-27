# =========================================================
# app/context/retriever.py
# =========================================================

import logging

from typing import Dict, Any, List, Set

from app.models.context_models import (
    LLMContext
)

logger = logging.getLogger(__name__)


class ContextRetriever:

    """
    Intelligent context reduction layer.

    Responsibilities:
    - detect relevant tables
    - detect relevant columns
    - expand graph joins
    - reduce prompt size
    - keep only useful schema context
    """

    # =====================================================
    # MAIN RETRIEVAL
    # =====================================================

    @staticmethod
    def retrieve(
        question: str,
        plan: Dict[str, Any],
        llm_context: LLMContext,
    ) -> Dict[str, Any]:

        logger.info(
            "Starting intelligent context retrieval"
        )

        question_lower = question.lower()

        # =================================================
        # 1. DETECT RELEVANT TABLES
        # =================================================

        relevant_tables = (
            ContextRetriever
            ._detect_relevant_tables(
                question=question_lower,
                context=llm_context
            )
        )

        logger.info(
            f"Relevant tables detected: "
            f"{relevant_tables}"
        )

        # =================================================
        # FALLBACK
        # =================================================

        if not relevant_tables:

            logger.warning(
                "No relevant tables detected. "
                "Using fallback tables."
            )

            relevant_tables = set(
                list(
                    llm_context.schema.tables.keys()
                )[:2]
            )

        # =================================================
        # 2. GRAPH EXPANSION
        # =================================================

        expanded_tables = (
            ContextRetriever
            ._expand_related_tables(
                tables=relevant_tables,
                context=llm_context
            )
        )

        logger.info(
            f"Expanded tables: "
            f"{expanded_tables}"
        )

        # =================================================
        # 3. FILTER SCHEMA
        # =================================================

        filtered_schema = (
            ContextRetriever
            ._filter_schema(
                tables=expanded_tables,
                context=llm_context,
                question=question_lower
            )
        )

        # =================================================
        # 4. FILTER RELATIONSHIPS
        # =================================================

        filtered_relationships = (
            ContextRetriever
            ._filter_relationships(
                tables=expanded_tables,
                context=llm_context
            )
        )

        # =================================================
        # 5. FILTER JOINS
        # =================================================

        filtered_joins = (
            ContextRetriever
            ._filter_joins(
                tables=expanded_tables,
                context=llm_context
            )
        )

        # =================================================
        # 6. FILTER SEMANTICS
        # =================================================

        filtered_semantic_tables = (
            ContextRetriever
            ._filter_semantic_tables(
                tables=expanded_tables,
                context=llm_context
            )
        )

        filtered_semantic_columns = (
            ContextRetriever
            ._filter_semantic_columns(
                tables=expanded_tables,
                context=llm_context
            )
        )

        logger.info(
            "Context retrieval completed"
        )

        # =================================================
        # FINAL REDUCED CONTEXT
        # =================================================

        return {

            "schema":
                filtered_schema,

            "relationships":
                filtered_relationships,

            "semantic_tables":
                filtered_semantic_tables,

            "semantic_columns":
                filtered_semantic_columns,

            "joins":
                filtered_joins,
        }

    # =====================================================
    # TABLE DETECTION
    # =====================================================

    @staticmethod
    def _detect_relevant_tables(
        question: str,
        context: LLMContext,
    ) -> Set[str]:

        relevant = set()

        # -------------------------------------------------
        # TABLE NAME MATCHING
        # -------------------------------------------------

        for table_name in (
            context.schema.tables.keys()
        ):

            normalized = (
                table_name
                .split(".")[-1]
                .lower()
            )

            singular = (
                normalized[:-1]
                if normalized.endswith("s")
                else normalized
            )

            if (
                normalized in question
                or singular in question
            ):

                relevant.add(table_name)

        # -------------------------------------------------
        # COLUMN MATCHING
        # -------------------------------------------------

        for table_name, table_data in (
            context.schema.tables.items()
        ):

            for col in table_data["columns"]:

                col_name = (
                    col["name"]
                    .lower()
                )

                if col_name in question:

                    relevant.add(table_name)

        # -------------------------------------------------
        # SEMANTIC MATCHING
        # -------------------------------------------------

        for table_name, semantic in (
            context.semantics.tables.items()
        ):

            description = (
                semantic
                .get("description", "")
                .lower()
            )

            domain_tags = semantic.get(
                "domain_tags",
                []
            )

            if any(
                tag.lower() in question
                for tag in domain_tags
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

        adjacency = (
            context.graph.adjacency
        )

        for table in tables:

            table_short = (
                table.split(".")[-1]
            )

            neighbors = adjacency.get(
                table_short,
                []
            )

            for neighbor in neighbors:

                # normalize full name
                full_neighbor = None

                for schema_table in (
                    context.schema.tables.keys()
                ):

                    if (
                        schema_table.endswith(
                            f".{neighbor}"
                        )
                    ):

                        full_neighbor = (
                            schema_table
                        )

                        break

                if full_neighbor:

                    expanded.add(
                        full_neighbor
                    )

        return expanded

    # =====================================================
    # FILTER SCHEMA
    # =====================================================

    @staticmethod
    def _filter_schema(
        tables: Set[str],
        context: LLMContext,
        question: str,
    ) -> Dict[str, Any]:

        filtered = {}

        wants_all_columns = any(

            phrase in question

            for phrase in [

                "all information",
                "all columns",
                "select *",
                "everything",
                "full table",
            ]
        )

        for table in tables:

            if table not in (
                context.schema.tables
            ):
                continue

            table_data = (
                context
                .schema
                .tables[table]
            )

            filtered_columns = []

            for col in (
                table_data["columns"]
            ):

                col_name = (
                    col["name"]
                    .lower()
                )

                important = (

                    wants_all_columns

                    or

                    col.get(
                        "primary_key"
                    )

                    or

                    col.get(
                        "foreign_key"
                    )

                    or

                    "name" in col_name

                    or

                    "id" in col_name

                    or

                    col_name in question
                )

                if important:

                    filtered_columns.append(
                        {
                            "name": col["name"],
                            "type": col["type"],
                            "primary_key": col.get(
                                "primary_key",
                                False
                            ),
                            "foreign_key": col.get(
                                "foreign_key",
                                False
                            )
                        }
                    )

            filtered[table] = {

                "columns":
                    filtered_columns
            }

        return filtered

    # =====================================================
    # FILTER RELATIONSHIPS
    # =====================================================

    @staticmethod
    def _filter_relationships(
        tables: Set[str],
        context: LLMContext,
    ) -> List[dict]:

        filtered = []

        normalized_tables = {

            table.split(".")[-1]
            for table in tables
        }

        for edge in (
            context.graph.edges
        ):

            src = edge["source_table"]
            tgt = edge["target_table"]

            if (
                src in normalized_tables
                and tgt in normalized_tables
            ):

                filtered.append({

                    "source":
                        src,

                    "target":
                        tgt,

                    "on":
                        (
                            f"{src}."
                            f"{edge['source_column']} = "
                            f"{tgt}."
                            f"{edge['target_column']}"
                        )
                })

        return filtered

    # =====================================================
    # FILTER JOINS
    # =====================================================

    @staticmethod
    def _filter_joins(
        tables: Set[str],
        context: LLMContext,
    ) -> List[str]:

        joins = []

        normalized_tables = {

            table.split(".")[-1]
            for table in tables
        }

        for join in context.joins:

            if any(
                table in join
                for table in normalized_tables
            ):

                joins.append(join)

        return joins

    # =====================================================
    # FILTER TABLE SEMANTICS
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
    # FILTER COLUMN SEMANTICS
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