# app/context/nl2sql_service.py

from datetime import datetime

from app.services.schema_service import SchemaService
from app.graph.schema_graph import SchemaGraphBuilder
from app.graph.inner_graph import ColumnGraphBuilder

from app.context.context_builder import ContextBuilderLLM
from app.context.retriever import ContextRetriever
from app.context.prompt_modulator import PromptModulator

from app.models.semantic_models import (
    SchemaSemanticMap,
    TableSemanticInfo,
    ColumnSemanticInfo,
)

from app.core.sql_generator import SQLGenerator


class NL2SQLService:

    def __init__(self, db_session):

        self.db = db_session

    # =====================================================
    # SEMANTIC CONTEXT BUILDER
    # =====================================================

    def _build_semantic_context(self, tables, columns) -> SchemaSemanticMap:

        table_semantics = []
        column_semantics = []

        for table in tables:

            table_semantics.append(
                TableSemanticInfo(
                    table_name=table.table_name,
                    business_meaning=f"Business table containing {table.table_name} information",
                    domain_tags=["database", "business"],
                    importance_score=0.5,
                    sample_queries=[],
                    approved=True,
                    confidence_score=0.8,
                    generated_by="nl2sql_service",
                    review_notes="Auto-generated",
                    last_updated=datetime.now()
                )
            )

        for table_name, cols in columns.items():

            for col in cols:

                column_semantics.append(
                    ColumnSemanticInfo(
                        table_name=table_name,
                        column_name=col.column_name,
                        semantic_type=col.data_type,
                        business_meaning=f"{col.column_name} field from {table_name}",
                        synonyms=[],
                        example_values=[],
                        approved=True,
                        confidence_score=0.7,
                        generated_by="nl2sql_service",
                        review_notes="Auto-generated",
                        last_updated=datetime.now()
                    )
                )

        return SchemaSemanticMap(
            tables=table_semantics,
            columns=column_semantics
        )

    # =====================================================
    # MAIN PIPELINE
    # =====================================================

    async def run(self, question: str):

        # -----------------------------
        # SCHEMA
        # -----------------------------

        tables = await SchemaService.get_tables(db=self.db)

        columns = {}

        for table in tables:
            columns[table.table_name] = await SchemaService.get_columns(
                db=self.db,
                table_name=table.table_name
            )

        relationships = await SchemaService.get_relationships(db=self.db)

        # -----------------------------
        # GRAPH
        # -----------------------------

        schema_graph = SchemaGraphBuilder.build(relationships)
        column_graph = ColumnGraphBuilder.build(relationships)

        # -----------------------------
        # SEMANTIC
        # -----------------------------

        semantic_context = self._build_semantic_context(tables, columns)

        # -----------------------------
        # LLM CONTEXT
        # -----------------------------

        llm_context = ContextBuilderLLM.build(
            tables=tables,
            columns=columns,
            schema_graph=schema_graph,
            column_graph=column_graph,
            semantic_context=semantic_context
        )

        # -----------------------------
        # RETRIEVAL
        # -----------------------------

        retrieved_context = ContextRetriever.retrieve(
            question=question,
            plan={},
            llm_context=llm_context
        )

        modulated_context = PromptModulator.build_context_text(
            retrieved_context
        )

        # -----------------------------
        # SQL GENERATOR
        # -----------------------------

        generator = SQLGenerator(
            db_session=self.db,
            context=llm_context
        )

        return await generator.generate(question)