import asyncio
from collections import defaultdict

from sqlalchemy import text

from app.db.database import AsyncSessionLocal

from app.services.schema_service import SchemaService

from app.graph.schema_graph import SchemaGraphBuilder
from app.graph.inner_graph import ColumnGraphBuilder

from app.context.context_builder import ContextBuilderLLM


# =========================================================
# CONNECTION TEST
# =========================================================

async def test_connection():
    async with AsyncSessionLocal() as session:
        result = await session.execute(text("SELECT NOW();"))

        print("\nDATABASE CONNECTION SUCCESS:\n")
        for row in result:
            print(row)


# =========================================================
# HELPERS
# =========================================================

def group_columns_by_table(columns):
    grouped = defaultdict(list)

    for c in columns:
        grouped[c.table_name].append(c)

    return dict(grouped)


# =========================================================
# SEMANTIC LOADER (FIXED DICT STRUCTURE)
# =========================================================

async def load_semantic_context(session):

    semantic_tables = {}
    semantic_columns = {}

    # TABLES
    res = await session.execute(
        text("""
            SELECT table_name, description
            FROM context.semantic_tables
        """)
    )

    for row in res.fetchall():
        semantic_tables[row.table_name] = {
            "label": row.table_name,
            "description": row.description
        }

    # COLUMNS (IMPORTANT FIX → DICT NOT LIST)
    res = await session.execute(
        text("""
            SELECT table_name, column_name, description
            FROM context.semantic_columns
        """)
    )

    for row in res.fetchall():

        if row.table_name not in semantic_columns:
            semantic_columns[row.table_name] = {}

        semantic_columns[row.table_name][row.column_name] = row.description

    return type("SemanticContext", (), {
        "tables": semantic_tables,
        "columns": semantic_columns
    })()


# =========================================================
# FULL PIPELINE TEST
# =========================================================

async def test_full_context_pipeline():

    async with AsyncSessionLocal() as session:

        # -----------------------------
        # 1. SCHEMA
        # -----------------------------
        tables = await SchemaService.get_tables(session)

        columns_flat = []
        for t in tables:
            cols = await SchemaService.get_columns(session, t.table_name)
            columns_flat.extend(cols)

        print("\nTABLES:", len(tables))
        print("COLUMNS:", len(columns_flat))

        # -----------------------------
        # 2. RELATIONSHIPS / GRAPHS
        # -----------------------------
        relationships = await SchemaService.get_relationships(session)

        schema_graph = SchemaGraphBuilder.build(relationships)
        column_graph = ColumnGraphBuilder.build(relationships)

        print("\nRELATIONSHIPS:", len(relationships))

        print("\nTABLE GRAPH (ADJACENCY):")
        print(schema_graph.adjacency)

        print("\nSHORTEST PATH TEST (members → facilities):")
        print(schema_graph.shortest_path("members", "facilities"))

        print("\nCOLUMN JOIN CLAUSES:")
        for j in column_graph.join_clauses:
            print(j)

        # -----------------------------
        # 3. SEMANTIC CONTEXT (FROM DB CACHE)
        # -----------------------------
        semantic_context = await load_semantic_context(session)

        print("\nSEMANTIC TABLES:")
        print(semantic_context.tables)

        # -----------------------------
        # 4. GROUP COLUMNS (IMPORTANT FIX)
        # -----------------------------
        grouped_columns = group_columns_by_table(columns_flat)

        # -----------------------------
        # 5. BUILD CONTEXT
        # -----------------------------
        context = ContextBuilderLLM.build(
            tables=tables,
            columns=grouped_columns,
            schema_graph=schema_graph,
            column_graph=column_graph,
            semantic_context=semantic_context,
        )

        # -----------------------------
        # 6. OUTPUT FINAL CONTEXT
        # -----------------------------
        print("\n================ CONTEXT BUILDER OUTPUT ================\n")

        print("SCHEMA BLOCK:")
        print(context.schema.tables)

        print("\nGRAPH BLOCK (ADJACENCY):")
        print(context.graph.adjacency)

        print("\nSEMANTIC BLOCK:")
        print(context.semantics.tables)

        print("\nJOINS:")
        for j in context.joins:
            print(j)

        print("\n================ VALIDATION =================\n")

        print("Tables:", len(context.schema.tables))
        print("Joins:", len(context.joins))
        print("Semantic tables:", len(context.semantics.tables))


# =========================================================
# MAIN
# =========================================================

async def main():
    await test_connection()
    await test_full_context_pipeline()


if __name__ == "__main__":
    asyncio.run(main())