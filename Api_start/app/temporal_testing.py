# app/temporal_testing.py

import asyncio
from datetime import datetime

from app.db.database import (
    AsyncSessionLocal
)

from app.core.sql_generator import (
    SQLGenerator
)

from app.context.context_builder import (
    ContextBuilderLLM
)

from app.context.retriever import (
    ContextRetriever
)

from app.context.prompt_modulator import (
    PromptModulator
)

from app.services.schema_service import (
    SchemaService
)

from app.graph.schema_graph import (
    SchemaGraphBuilder
)

from app.graph.inner_graph import (
    ColumnGraphBuilder
)

from app.models.semantic_models import (
    SchemaSemanticMap,
    TableSemanticInfo,
    ColumnSemanticInfo,
)


# =========================================================
# SEMANTIC CONTEXT BUILDER
# =========================================================

def build_semantic_context(
    tables,
    columns
) -> SchemaSemanticMap:

    table_semantics = []

    column_semantics = []

    # -----------------------------------------------------
    # TABLE SEMANTICS
    # -----------------------------------------------------

    for table in tables:

        table_semantics.append(

            TableSemanticInfo(

                table_name=table.table_name,

                business_meaning=(
                    f"Business table containing "
                    f"{table.table_name} information"
                ),

                domain_tags=[
                    "database",
                    "business"
                ],

                importance_score=0.5,

                sample_queries=[],

                approved=True,

                confidence_score=0.8,

                generated_by="temporal_testing",

                review_notes="Auto-generated",

                last_updated=datetime.now()
            )
        )

    # -----------------------------------------------------
    # COLUMN SEMANTICS
    # -----------------------------------------------------

    for table_name, cols in columns.items():

        for col in cols:

            column_semantics.append(

                ColumnSemanticInfo(

                    table_name=table_name,

                    column_name=col.column_name,

                    semantic_type=col.data_type,

                    business_meaning=(
                        f"{col.column_name} field "
                        f"from {table_name}"
                    ),

                    synonyms=[],

                    example_values=[],

                    approved=True,

                    confidence_score=0.7,

                    generated_by="temporal_testing",

                    review_notes="Auto-generated",

                    last_updated=datetime.now()
                )
            )

    return SchemaSemanticMap(

        tables=table_semantics,

        columns=column_semantics
    )


# =========================================================
# MAIN TEST PIPELINE
# =========================================================

async def main():

    try:

        # =================================================
        # CREATE DATABASE SESSION
        # =================================================

        async with AsyncSessionLocal() as session:

            print(
                "\n[1] Async PostgreSQL session created"
            )

            # =============================================
            # EXTRACT TABLES
            # =============================================

            tables = await (
                SchemaService.get_tables(
                    db=session
                )
            )

            print(
                f"[2] Extracted "
                #f"{len(tables)} tables"
            )

            # =============================================
            # EXTRACT COLUMNS
            # =============================================

            columns = {}

            for table in tables:

                table_columns = await (
                    SchemaService.get_columns(
                        db=session,
                        table_name=table.table_name
                    )
                )

                columns[
                    table.table_name
                ] = table_columns

            print(
                "[3] Columns extracted"
            )

            # =============================================
            # EXTRACT RELATIONSHIPS
            # =============================================

            relationships = await (
                SchemaService.get_relationships(
                    db=session
                )
            )

            print(
                f"[4] Extracted "
                #f"{len(relationships)} relationships"
            )

            # =============================================
            # BUILD SCHEMA GRAPH
            # =============================================

            schema_graph = (
                SchemaGraphBuilder.build(
                    relationships=relationships
                )
            )

            print(
                "[5] Schema graph built"
            )

            # =============================================
            # BUILD COLUMN GRAPH
            # =============================================

            column_graph = (
                ColumnGraphBuilder.build(
                    relationships=relationships
                )
            )

            print(
                "[6] Column graph built"
            )

            # =============================================
            # BUILD SEMANTIC CONTEXT
            # =============================================

            semantic_context = (
                build_semantic_context(
                    tables=tables,
                    columns=columns
                )
            )

            print(
                "[7] Semantic context built"
            )

            # =============================================
            # BUILD LLM CONTEXT
            # =============================================

            llm_context = (
                ContextBuilderLLM.build(
                    tables=tables,
                    columns=columns,
                    schema_graph=schema_graph,
                    column_graph=column_graph,
                    semantic_context=semantic_context
                )
            )

            print(
                "[8] LLM context built"
            )

            # =============================================
            # INITIALIZE SQL GENERATOR
            # =============================================

            generator = SQLGenerator(
                db_session=session,
                context=llm_context
            )

            print(
                "[9] SQL Generator initialized"
            )

            # =============================================
            # TEST QUESTION
            # =============================================

            question = """
            How can you produce a list of all members
            who have used a tennis court?

            Include in your output the name
            of the court, and the name
            of the member formatted
            as a single column.

            Ensure no duplicate data,
            and order by the member name
            followed by the facility name.
            """

            print(
                "\n===================================="
            )

            print("QUESTION")

            print(
                "===================================="
            )

            print(question)

            # =============================================
            # CONTEXT RETRIEVAL TEST
            # =============================================

            retrieved_context = (
                ContextRetriever.retrieve(
                    question=question,
                    plan={},
                    llm_context=llm_context
                )
            )

            print(
                "\n===================================="
            )

            print("RETRIEVED CONTEXT")

            print(
                "===================================="
            )

            print(retrieved_context)

            # =============================================
            # PROMPT MODULATION TEST
            # =============================================

            modulated_context = (
                PromptModulator.build_context_text(
                    retrieved_context
                )
            )

            print(
                "\n===================================="
            )

            print("MODULATED CONTEXT")

            print(
                "===================================="
            )

            print(modulated_context)

            # =============================================
            # CONTEXT METRICS
            # =============================================

            raw_size = len(
                str(retrieved_context)
            )

            modulated_size = len(
                modulated_context
            )

            reduction = round(

                (
                    1 - (
                        modulated_size
                        / raw_size
                    )
                ) * 100,

                2
            )

            print(
                "\n===================================="
            )

            print("CONTEXT METRICS")

            print(
                "===================================="
            )

            print(
                f"Raw Context Size: "
                f"{raw_size} chars"
            )

            print(
                f"Modulated Context Size: "
                f"{modulated_size} chars"
            )

            print(
                f"Reduction: "
                f"{reduction}%"
            )

            # =============================================
            # GENERATE SQL
            # =============================================

            response = await (
                generator.generate(
                    question=question
                )
            )

            # =============================================
            # GENERATED SQL
            # =============================================

            print(
                "\n===================================="
            )

            print("GENERATED SQL")

            print(
                "===================================="
            )

            print(response.sql)

            # =============================================
            # EXPLANATION
            # =============================================

            print(
                "\n===================================="
            )

            print("EXPLANATION")

            print(
                "===================================="
            )

            print(
                response.explanation
            )

            # =============================================
            # RESULTS
            # =============================================

            print(
                "\n===================================="
            )

            print("RESULTS")

            print(
                "===================================="
            )

            if not response.rows:

                print(
                    "No rows returned"
                )

            else:

                for row in (
                    response.rows[:20]
                ):

                    print(row)

            # =============================================
            # METRICS
            # =============================================

            print(
                "\n===================================="
            )

            print("PIPELINE METRICS")

            print(
                "===================================="
            )

            print(
                f"Execution Time: "
                f"{response.execution_time}s"
            )

            print(
                f"LLM Time: "
                f"{response.llm_time}s"
            )

            print(
                "\n===================================="
            )

            print("PIPELINE SUCCESS")

            print(
                "===================================="
            )

    except Exception as e:

        print(
            "\n===================================="
        )

        print("PIPELINE FAILED")

        print(
            "===================================="
        )

        print(str(e))


# =========================================================
# ENTRYPOINT
# =========================================================

if __name__ == "__main__":

    asyncio.run(main())